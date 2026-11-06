"""Ordered, restartable research stages. Final access guarded independently of checkpoints."""

from pathlib import Path
import importlib.metadata
import logging
import platform
import numpy as np
import pandas as pd
import yaml
from src.utils.io import (
    write_json,
    write_csv,
    read_json,
    canonical_hash,
    digest,
    frame_hash,
    Checkpoints,
)
from src.data.ingest import load_xpt, discover, ScientificValidationError
from src.data.synthetic import generate
from src.data.outcomes import eligible
from src.features.engineering import specifications, transform_raw
from src.audit.validation import validate_source, verify_codebook, missingness, DESIGN
from src.statistics.survey import Design
from src.statistics.analysis import table_one, inference, univariate
from src.modeling.splits import create_split, save_split
from src.modeling.experiments import develop, subsample_training
from src.evaluation.final import final_evaluate
from src.reporting.report import generate as report

STAGES = ["audit", "cohort", "descriptive", "inference", "split", "develop", "evaluate", "report"]


def run(
    out="runs/synthetic",
    data=None,
    codebook=None,
    synthetic=False,
    n=960,
    profile="quick",
    through="report",
    mode="binary",
    seed=2015,
):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    specs = specifications()
    cfg = yaml.safe_load(Path("configs/project.yaml").read_text())
    ecfg = yaml.safe_load(Path("configs/experiments.yaml").read_text())
    np.random.seed(seed)
    raw_path = None
    if synthetic:
        raw = generate(n, seed)
        meta = {"source_columns": raw.columns.tolist(), "source_sha256": frame_hash(raw)}
    else:
        raw_path = discover(data or cfg["data_path"], cfg["candidate_directories"])
        columns = list(
            dict.fromkeys(DESIGN + ["DIABETE3", "PREDIAB1", "_STATE", "SEQNO"] + list(specs))
        )
        raw, meta = load_xpt(raw_path, columns)
    versions = {
        p: importlib.metadata.version(p)
        for p in ["numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "imbalanced-learn"]
    }
    versions["python"] = platform.python_version()
    code = {str(p): digest(p) for p in sorted(Path("src").rglob("*.py"))}
    signature = canonical_hash(
        {
            "source": meta["source_sha256"],
            "specs": specs,
            "cfg": cfg,
            "experiments": ecfg,
            "profile": profile,
            "mode": mode,
            "seed": seed,
            "code": code,
            "versions": versions,
        }
    )
    existing = out / "run_manifest.json"
    if existing.exists() and read_json(existing)["signature"] != signature:
        raise ScientificValidationError(
            "Run signature changed. Use a NEW output directory; protected test artifacts will not be overwritten."
        )
    if not existing.exists():
        write_json(
            existing,
            {
                "signature": signature,
                "versions": versions,
                "source_path": str(raw_path),
                "synthetic": synthetic,
                "profile": profile,
                "mode": mode,
                "seed": seed,
                "code": code,
            },
        )
    cp = Checkpoints(out, signature)
    keep, y = eligible(raw, mode, cfg["exclude_territories"])
    X = transform_raw(raw, specs)
    end = STAGES.index(through)

    def execute(stage, fn, outputs):
        if STAGES.index(stage) > end:
            return
        if cp.valid(stage):
            logging.info("RESUME %s", stage)
            return
        logging.info("RUN %s", stage)
        fn()
        cp.commit(stage, [out / p for p in outputs])

    def audit():
        a = validate_source(raw, meta, specs, synthetic)
        if not synthetic:
            c = discover(
                codebook or cfg["codebook_path"],
                [raw_path.parent] + [Path(x) for x in cfg["candidate_directories"]],
                "codebook15_llcp.pdf",
            )
            a["codebook"] = verify_codebook(c, list(specs) + DESIGN + ["DIABETE3", "PREDIAB1"])
        else:
            a["codebook"] = "SYNTHETIC_FIXTURE_NO_CDC_CODING_VERIFICATION"
        write_json(out / "audit.json", a)

    execute("audit", audit, ["audit.json"])

    def cohort():
        write_json(
            out / "cohort.json",
            {
                "mode": mode,
                "total": len(raw),
                "eligible": int(keep.sum()),
                "excluded": int((~keep).sum()),
                "complete_case": int((keep & X.notna().all(axis=1)).sum()),
                "labels": y[keep].value_counts().to_dict(),
                "outcome_semantics": "self-reported diagnosis; not incident risk",
            },
        )
        write_csv(out / "missingness.csv", missingness(X.loc[keep], y.loc[keep]))

    execute("cohort", cohort, ["cohort.json", "missingness.csv"])

    def descriptive():
        design = Design(raw)
        prevalence = {
            str(c): design.mean((y == c).astype(float), keep, proportion=True)
            for c in sorted(y[keep].unique())
        }
        write_json(out / "prevalence.json", prevalence)
        write_csv(out / "table1.csv", table_one(raw, X, y, specs, keep))

    execute("descriptive", descriptive, ["prevalence.json", "table1.csv"])

    def stats():
        multi = mode in ["core_three", "module_three"]
        tab, diag = inference(raw, X, y, specs, keep, multiclass=multi)
        write_csv(out / ("multinomial_rrr.csv" if multi else "adjusted_or.csv"), tab)
        write_json(out / "inference_diagnostics.json", diag)
        write_csv(
            out / "grouped_wald.csv",
            pd.DataFrame([{"variable": k, **v} for k, v in diag["grouped_wald"].items()]),
        )
        tab, _ = inference(raw, X, y, specs, keep, multiclass=multi, impute=True)
        write_csv(out / "sensitivity_or.csv", tab)
        if not multi:
            write_csv(out / "univariate.csv", univariate(raw, X, y, specs, keep))
            keep2, y2 = eligible(raw, "binary_borderline_negative", cfg["exclude_territories"])
            tab, _ = inference(raw, X, y2, specs, keep2)
            write_csv(out / "borderline_sensitivity_or.csv", tab)
        # VIF is a model-matrix diagnostic; not survey causal identification.
        from src.statistics.analysis import model_matrix

        mat = model_matrix(X.loc[keep], specs).dropna()
        correlation = mat.iloc[:, 1:].corr().fillna(0).to_numpy()
        vif = np.diag(np.linalg.pinv(correlation))
        write_csv(out / "vif.csv", pd.DataFrame({"term": mat.columns[1:], "vif": vif}))

    statoutputs = [
        "multinomial_rrr.csv" if mode in ["core_three", "module_three"] else "adjusted_or.csv",
        "sensitivity_or.csv",
        "inference_diagnostics.json",
        "grouped_wald.csv",
        "vif.csv",
    ]
    if mode == "binary":
        statoutputs += ["univariate.csv", "borderline_sensitivity_or.csv"]
    execute("inference", stats, statoutputs)
    if end >= STAGES.index("split"):
        XX = X.loc[keep].reset_index(drop=True)
        yy = y[keep].to_numpy(int)
        ids = (
            raw.loc[keep, "_STATE"].astype(int).astype(str)
            + ":"
            + raw.loc[keep, "SEQNO"].astype(str)
        ).to_numpy()
        a, b, manifest = create_split(ids, yy, seed, cfg["test_fraction"])
        execute("split", lambda: save_split(out / "split.json", manifest), ["split.json"])
        trainX, trainy, ix = subsample_training(
            XX.iloc[a], yy[a], ecfg["profiles"][profile]["max_train"], seed
        )
        write_json(
            out / "training_subset.json", {"indices_within_train": ix.tolist(), "n": len(ix)}
        )

        def development():
            develop(trainX, trainy, specs, out, ecfg, profile, seed)

        execute(
            "develop",
            development,
            [
                "development.json",
                "frozen_model.joblib",
                "frozen.json",
                "baseline_model.joblib",
                "baseline_frozen.json",
                "feature_importance.csv",
            ],
        )

        def evaluate():
            final_evaluate(
                out,
                XX.iloc[b],
                yy[b],
                raw.loc[keep].iloc[b],
                raw.loc[keep, "_LLCPWT"].iloc[b].to_numpy(),
                ecfg["profiles"][profile]["bootstrap"],
                seed,
            )

        execute(
            "evaluate",
            evaluate,
            [
                "final_metrics.json",
                "test_access.json",
                "calibration.csv",
                "subgroups.csv",
                "test_predictions.csv",
            ],
        )
    execute(
        "report",
        lambda: report(out, synthetic),
        [
            "final_report.md",
            "execution_status.json",
            "execution_status.md",
            "model_comparison.csv",
            "figures/missingness.png",
            "figures/missingness_by_outcome.png",
            "figures/confusion_matrix.png",
            "figures/calibration.png",
        ],
    )
    return out
