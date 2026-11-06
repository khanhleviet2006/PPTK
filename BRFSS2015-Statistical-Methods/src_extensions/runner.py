"""Resumable post-audit research; old final-test IDs are excluded before feature engineering."""

from pathlib import Path
import io
import logging
import importlib.metadata
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold
from src.data.ingest import load_xpt
from src.data.synthetic import generate
from src.data.outcomes import eligible
from src.features.engineering import specifications, transform_raw
from src.utils.io import (
    digest,
    canonical_hash,
    write_json,
    write_csv,
    read_json,
    atomic_bytes,
    frame_hash,
)
from scripts.audit_research_gaps import snapshot
from src_extensions.experiments import plan, evaluate, make, policy_metrics

PROFILES = {
    "SMOKE": {"n": 480, "folds": 2},
    "QUICK": {"n": 2000, "folds": 2},
    "STANDARD": {"n": None, "folds": 5},
    "EXTENDED": {"n": None, "folds": 5},
}


def run(
    data=None,
    out="runs/gap_development",
    profile="QUICK",
    synthetic=False,
    mode="binary",
    max_experiments=None,
):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    seed = 20261106
    specs = specifications()
    if synthetic:
        protected = {str(p): digest(p) for p in Path("src").rglob("*.py")}
    else:
        from scripts.colab_runtime import require_legacy

        require_legacy()
        protected = snapshot()
    if synthetic:
        raw = generate(640, seed)
        source = frame_hash(raw)
        old_test = set()
        old_train = None
    else:
        if not data or not Path(data).is_file():
            raise FileNotFoundError(
                "Provide --data LLCP2015.XPT; old final test is never a development fallback."
            )
        legacy = read_json("runs/real_final_quick/split.json")
        old_test = set(legacy["test_ids"])
        old_train = set(legacy["train_ids"])
        raw, meta = load_xpt(
            data, columns=list(specs) + ["_STATE", "SEQNO", "DIABETE3", "_LLCPWT", "_STSTR", "_PSU"]
        )
        source = meta["source_sha256"]
    ids = raw["_STATE"].astype(int).astype(str) + ":" + raw["SEQNO"].astype(str)
    mask, y = eligible(raw, mode)
    available = mask & ~ids.isin(old_test)
    if mode == "binary" and old_train is not None:
        available &= ids.isin(old_train)
    raw = raw.loc[available].copy()
    ids = ids.loc[available].reset_index(drop=True)
    y = y.loc[available].to_numpy(int)
    X = transform_raw(raw, specs).reset_index(drop=True)
    raw = raw.reset_index(drop=True)
    limit = PROFILES[profile]["n"]
    if limit and len(y) > limit:
        ix, _ = train_test_split(np.arange(len(y)), train_size=limit, stratify=y, random_state=seed)
        X = X.iloc[ix].reset_index(drop=True)
        y = y[ix]
        ids = ids.iloc[ix].reset_index(drop=True)
        raw = raw.iloc[ix].reset_index(drop=True)
    write_csv(out / "development_features.csv", X.assign(outcome=y))
    assert not set(ids) & old_test
    code = {
        str(p): digest(p)
        for p in [Path("src_extensions/runner.py"), Path("src_extensions/experiments.py")]
    }
    conf = {
        "profile": profile,
        "synthetic": synthetic,
        "mode": mode,
        "seed": seed,
        "source": source,
        "n": len(y),
        "code": code,
        "exclusion": "all legacy final-test IDs excluded; binary restricted to old training IDs",
        "scope": "EXPLORATORY_POST_AUDIT_DEVELOPMENT_CV",
        "primary_metric": "outer-CV balanced_accuracy with inner-training thresholds",
        "versions": {
            p: importlib.metadata.version(p)
            for p in ["scikit-learn", "numpy", "pandas", "shap", "optuna"]
        },
    }
    signature = canonical_hash(conf)
    if (out / "manifest.json").exists() and read_json(out / "manifest.json")[
        "signature"
    ] != signature:
        raise ValueError(
            "Run signature changed; use a separate output directory; no old evidence overwritten."
        )
    write_json(out / "manifest.json", dict(signature=signature, **conf))
    write_json(
        out / "development_ids.json",
        {"ids": ids.tolist(), "legacy_test_overlap": 0, "ids_hash": canonical_hash(ids.tolist())},
    )
    cv = list(
        StratifiedKFold(PROFILES[profile]["folds"], shuffle=True, random_state=seed).split(X, y)
    )
    write_json(
        out / "outer_splits.json", [dict(train=a.tolist(), validation=b.tolist()) for a, b in cv]
    )
    exps = plan(mode)
    if profile == "SMOKE":
        exps = [
            dict(model="logistic", stage="screen"),
            dict(model="logistic", selector="pca", k=5, stage="features"),
            dict(model="logistic", calibration="sigmoid", stage="calibration"),
        ]
    if max_experiments:
        exps = exps[:max_experiments]
    write_json(out / "planned_experiments.json", exps)
    registry = []
    for exp in exps:
        logging.info("Experiment %s", exp)
        try:
            r = evaluate(X, y, specs, out, exp, cv, seed)
        except Exception as e:
            logging.exception("Experiment failed")
            r = {"config": exp, "status": "FAILED", "exception": type(e).__name__, "reason": str(e)}
        registry.append(r)
        write_json(out / "registry.json", registry)
    if mode == "binary":
        # Complete-case sensitivity targets a different observed-case cohort, explicitly separate.
        cc = X.notna().all(axis=1).to_numpy()
        if cc.sum() > 100 and np.bincount(y[cc]).min() >= 4:
            ccv = list(StratifiedKFold(2, shuffle=True, random_state=seed).split(X.loc[cc], y[cc]))
            dd = out / "complete_case"
            dd.mkdir(exist_ok=True)
            evaluate(
                X.loc[cc].reset_index(drop=True),
                y[cc],
                specs,
                dd,
                dict(model="logistic", stage="complete_case"),
                ccv,
                seed,
            )
        # Repeated-seed stability, kept separate from primary paired outer folds.
        repeats = []
        for s in [seed + 1, seed + 2]:
            dd = out / f"seed_{s}"
            dd.mkdir(exist_ok=True)
            cv2 = list(StratifiedKFold(2, shuffle=True, random_state=s).split(X, y))
            repeats.append(
                evaluate(X, y, specs, dd, dict(model="logistic", stage="repeated_seed"), cv2, s)
            )
        write_json(out / "repeat_seed_results.json", repeats)
    good = [r for r in registry if r["status"] == "SUCCESS"]
    if not good:
        raise RuntimeError("No experiment completed")
    winner = sorted(
        good, key=lambda r: (-r["metrics"]["balanced_accuracy"], canonical_hash(r["config"]))
    )[0]
    # Development winner only. No endpoint evaluates it against the legacy final test.
    write_json(
        out / "development_selection.json",
        {
            "experiment": winner["config"],
            "criterion": "outer development BA; optimistic after candidate selection",
            "confirmatory_evaluation": "NOT_EXECUTED",
        },
    )
    final = make(X, specs, winner["config"], seed).fit(X, y)
    b = io.BytesIO()
    joblib.dump(final, b)
    atomic_bytes(out / "development_model.joblib", b.getvalue())
    explain(X, y, specs, raw, out, seed, good)
    current = {str(p): digest(p) for p in Path("src").rglob("*.py")} if synthetic else snapshot()
    assert protected == current, "Legacy source/config/models/test artifacts changed"
    write_json(
        out / "integrity.json",
        {
            "legacy_protected_hashes": protected,
            "unchanged": True,
            "legacy_test_overlap": 0,
            "new_final_test_evaluations": 0,
        },
    )
    return out


def explain(X, y, specs, raw, out, seed, good):
    import shap
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LogisticRegression
    from scipy.special import logit
    from src_extensions.experiments import preprocessing

    pre = preprocessing(list(X), specs)
    z = pre.fit_transform(X)
    names = pre.get_feature_names_out()
    from sklearn.ensemble import ExtraTreesClassifier

    tree = ExtraTreesClassifier(
        n_estimators=40, min_samples_leaf=5, n_jobs=1, random_state=seed
    ).fit(z, y)
    values = np.asarray(shap.TreeExplainer(tree).shap_values(z[: min(128, len(z))]))
    if values.ndim == 3:
        values = values[:, :, 1]
    write_csv(
        out / "shap_importance.csv",
        pd.DataFrame({"feature": names, "mean_abs_shap": np.abs(values).mean(axis=0)}),
    )
    shap.summary_plot(values, z[: len(values)], feature_names=names, show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(out / "shap_summary.png", dpi=180)
    plt.close()
    stability = []
    for s in [seed, seed + 1, seed + 2]:
        ix = np.random.default_rng(s).choice(len(y), len(y), replace=True)
        tree.fit(z[ix], y[ix])
        v = np.asarray(shap.TreeExplainer(tree).shap_values(z[:64]))
        if v.ndim == 3:
            v = v[:, :, 1]
        stability.append(np.abs(v).mean(axis=0))
    write_csv(
        out / "shap_stability.csv",
        pd.DataFrame(
            {"feature": names, "mean": np.mean(stability, axis=0), "sd": np.std(stability, axis=0)}
        ),
    )
    # Subgroup and calibration diagnostics use development OOF predictions only.
    base = next(
        r
        for r in good
        if r["config"].get("model") == "logistic" and r["config"].get("stage") == "screen"
    )
    oof = pd.read_csv(out / base["oof_file"])
    p = oof[[c for c in oof if c.startswith("p") and c != "pred"]].to_numpy()
    if p.shape[1] == 2:
        lm = LogisticRegression(C=1e6).fit(logit(np.clip(p[:, 1], 1e-6, 1 - 1e-6))[:, None], y)
        write_json(
            out / "calibration_intercept_slope.json",
            {
                "intercept": lm.intercept_[0],
                "slope": lm.coef_[0, 0],
                "scope": "descriptive OOF diagnostic, not recalibration fit",
            },
        )
    groups = []
    for c in ["SEX", "_AGEG5YR", "_RACE", "EDUCA", "INCOME2"]:
        for level in sorted(X[c].dropna().unique()):
            mask = X[c].eq(level).to_numpy()
            if mask.sum() >= 30 and len(np.unique(y[mask])) == p.shape[1]:
                groups.append(
                    {
                        "variable": c,
                        "level": level,
                        "n": int(mask.sum()),
                        **policy_metrics(y[mask], p[mask], oof.pred.to_numpy()[mask]),
                    }
                )
    bmi = pd.cut(X["_BMI5"], [0, 18.5, 25, 30, 100], right=False)
    for level in bmi.cat.categories:
        mask = bmi.eq(level).to_numpy()
        if mask.sum() >= 30 and len(np.unique(y[mask])) == p.shape[1]:
            groups.append(
                {
                    "variable": "BMI",
                    "level": str(level),
                    "n": int(mask.sum()),
                    **policy_metrics(y[mask], p[mask], oof.pred.to_numpy()[mask]),
                }
            )
    write_csv(
        out / "development_subgroups.csv",
        pd.DataFrame([{k: v for k, v in r.items() if k != "confusion_matrix"} for r in groups]),
    )
