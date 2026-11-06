"""Freeze on 2015 development before a single 2017 temporal evaluation."""

from pathlib import Path
import os
import io
import re
import numpy as np
import pandas as pd
import pyreadstat
import joblib
from pypdf import PdfReader
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from src.features.engineering import specifications, transform_raw
from src.data.outcomes import eligible
from src.evaluation.metrics import metrics, bootstrap, calibration
from src.utils.io import write_json, read_json, write_csv, atomic_bytes, digest
from src_extensions.experiments import make, evaluate
from scripts.audit_research_gaps import snapshot

FEATURES = [
    "_AGEG5YR",
    "SEX",
    "_BMI5",
    "EDUCA",
    "INCOME2",
    "_RACE",
    "_SMOKER3",
    "EXERANY2",
    "GENHLTH",
    "PHYSHLTH",
    "MENTHLTH",
    "HLTHPLN1",
    "MEDCOST",
    "CHECKUP1",
]


def run(development, data, codebook, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    protected = snapshot()
    specs = {k: v for k, v in specifications().items() if k in FEATURES}
    ledger = out / "external_access.json"
    if ledger.exists():
        state = read_json(ledger)
        if state["state"] == "COMPLETE":
            return read_json(out / "external_metrics.json")
        raise RuntimeError(
            "External data already accessed/interrupted; manual scientific audit required"
        )
    canonical_ledger = Path("runs/temporal_2017/external_access.json")
    if canonical_ledger.exists() and canonical_ledger.resolve() != ledger.resolve():
        raise RuntimeError(
            "2017 has already been evaluated; a new output directory cannot reset its test ledger"
        )
    pages = [p.extract_text() or "" for p in PdfReader(codebook).pages]
    evidence = []
    for name in FEATURES + ["DIABETE3", "_LLCPWT", "_STSTR", "_PSU"]:
        matches = [
            (i + 1, t)
            for i, t in enumerate(pages)
            if re.search(r"SAS Variable Name:\s*" + re.escape(name) + r"\s", t)
        ]
        if not matches:
            raise ValueError(f"2017 codebook variable not found: {name}")
        i, t = matches[0]
        start = t.index("SAS Variable Name:")
        evidence.append({"variable": name, "pdf_page": i, "excerpt": t[start : start + 1700]})
    write_json(
        out / "compatibility.json",
        {
            "year": 2017,
            "codebook_sha256": digest(codebook),
            "variables": evidence,
            "review": "Core DIABETE3 1 yes/3 no; pregnancy2 and borderline4 excluded. Same selected coded factors/scales; SEX=9 newly refused maps missing. Nutrition, alcohol and cholesterol screening omitted to avoid rotated/changed modules. No biological diabetes/type inference.",
            "limitations": "2017 skip/nonresponse and population shifts remain; same survey system and possible unlinked repeat respondents; no clinical external population claim.",
        },
    )
    d = pd.read_csv(Path(development) / "development_features.csv")
    y = d.pop("outcome").to_numpy(int)
    X = d[FEATURES]
    seed = 20261106
    cv = list(StratifiedKFold(2, shuffle=True, random_state=seed).split(X, y))
    configs = [
        dict(model="logistic", stage="temporal_development"),
        dict(model="logistic", weighted=True, stage="temporal_development"),
        dict(model="logistic", calibration="sigmoid", stage="temporal_development"),
    ]
    records = [evaluate(X, y, specs, out, c, cv, seed) for c in configs]
    winner = sorted(records, key=lambda r: (-r["metrics"]["balanced_accuracy"], str(r["config"])))[
        0
    ]
    m = make(X, specs, winner["config"], seed)
    oof = cross_val_predict(m, X, y, cv=cv, method="predict_proba")[:, 1]
    from sklearn.metrics import balanced_accuracy_score

    threshold = float(
        max(
            np.arange(0.1, 0.91, 0.1),
            key=lambda t: (balanced_accuracy_score(y, oof >= t), -abs(t - 0.5)),
        )
    )
    m.fit(X, y)
    b = io.BytesIO()
    joblib.dump(m, b)
    atomic_bytes(out / "temporal_model.joblib", b.getvalue())
    write_json(
        out / "frozen_before_external.json",
        {
            "config": winner["config"],
            "threshold": threshold,
            "features": FEATURES,
            "model_sha256": digest(out / "temporal_model.joblib"),
            "development_manifest_sha256": digest(Path(development) / "manifest.json"),
            "external_sample_n": 5000,
            "external_sampling_seed": seed,
            "selection": "training 2015 outer CV only; threshold training OOF only; no 2017 row labels accessed before this freeze",
            "uncertainty": "conditional respondent bootstrap; not survey prediction CI",
        },
    )
    fd = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    write_json(ledger, {"state": "ACCESSED", "evaluation_count": 1})
    raw, meta = pyreadstat.read_xport(
        data, usecols=FEATURES + ["DIABETE3", "_STATE", "_LLCPWT", "_STSTR", "_PSU"]
    )
    if len(raw) != 450016:
        raise ValueError("Unexpected original CDC 2017 record count")
    if raw[["_LLCPWT", "_STSTR", "_PSU"]].isna().any().any() or (raw._LLCPWT <= 0).any():
        raise ValueError("Invalid external survey design")
    keep, yy = eligible(raw, "binary")
    raw = raw.loc[keep].reset_index(drop=True)
    yy = yy.loc[keep].to_numpy(int)
    ix = np.random.default_rng(seed).choice(len(raw), min(5000, len(raw)), replace=False)
    xx = transform_raw(raw.iloc[ix], specs)
    target = yy[ix]
    p = m.predict_proba(xx)
    result = {
        "year": 2017,
        "sample_n": len(ix),
        "eligible_n": len(raw),
        "outcome": "DIABETE3=1 vs3; 50 states/DC",
        "source_sha256": digest(data),
        "metrics": metrics(target, p, threshold),
        "ci_conditional": bootstrap(target, p, 200, seed, threshold),
        "weighted_point_estimates": metrics(
            target, p, threshold, weights=raw._LLCPWT.iloc[ix].to_numpy()
        ),
        "evaluation_count": 1,
        "scope": "TEMPORAL_UNWEIGHTED_RESPONDENT_SAMPLE_NOT_CLINICAL_EXTERNAL_VALIDATION",
    }
    shift = []
    for c in FEATURES:
        shift.append(
            {
                "variable": c,
                "train_missing": X[c].isna().mean(),
                "external_missing": xx[c].isna().mean(),
                "train_mean_code": X[c].mean(),
                "external_mean_code": xx[c].mean(),
            }
        )
    write_csv(out / "distribution_shift.csv", pd.DataFrame(shift))
    write_csv(out / "calibration.csv", pd.DataFrame(calibration(target, p)))
    write_csv(out / "predictions.csv", pd.DataFrame({"y": target, "p": p[:, 1]}))
    write_json(out / "external_metrics.json", result)
    write_json(
        ledger,
        {
            "state": "COMPLETE",
            "evaluation_count": 1,
            "result_sha256": digest(out / "external_metrics.json"),
        },
    )
    assert protected == snapshot()
    write_json(out / "integrity.json", {"legacy_2015_unchanged": True, "new_2015_evaluations": 0})
    return result
