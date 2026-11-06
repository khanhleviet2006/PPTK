"""One-time final evaluation with pre-access ledger; interrupted access fails closed."""

import os
import joblib
import numpy as np
import pandas as pd
from src.utils.io import read_json, write_json, write_csv, digest
from src.evaluation.metrics import metrics, bootstrap, calibration, mcnemar
from src.data.ingest import ScientificValidationError


def final_evaluate(out, X, y, demographics, weights, repeats=100, seed=2015):
    result = out / "final_metrics.json"
    ledger = out / "test_access.json"
    if ledger.exists():
        try:
            record = read_json(ledger)
        except (ValueError, OSError) as exc:
            raise ScientificValidationError(
                "Unreadable test access ledger; treat test as accessed and audit interruption"
            ) from exc
        if record["state"] == "COMPLETE" and result.exists():
            return read_json(result)
        raise ScientificValidationError(
            "Test already accessed/interrupted; audit ledger before any reuse"
        )
    frozen = read_json(out / "frozen.json")
    if frozen["model_sha256"] != digest(out / "frozen_model.joblib"):
        raise ScientificValidationError("Frozen model changed")
    baseline = read_json(out / "baseline_frozen.json")
    if baseline["model_sha256"] != digest(out / "baseline_model.joblib"):
        raise ScientificValidationError("Frozen baseline changed")
    # O_EXCL prevents simultaneous evaluations from both entering test access.
    fd = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    write_json(
        ledger,
        {
            "state": "ACCESSED",
            "purpose": "one prespecified batch final evaluation",
            "test_reused": False,
            "frozen": frozen,
        },
    )
    model = joblib.load(out / "frozen_model.joblib")
    base = joblib.load(out / "baseline_model.joblib")
    p = model.predict_proba(X)
    b = base.predict_proba(X)
    t = frozen["threshold"]
    m = metrics(y, p, t)
    weighted = metrics(y, p, t, weights=weights)
    rows = []
    for c in ["SEX", "_AGEG5YR", "_RACE"]:
        if c not in demographics:
            continue
        for level in sorted(demographics[c].dropna().unique()):
            keep = demographics[c].eq(level).to_numpy()
            if keep.sum() < 30:
                rows.append(
                    {
                        "variable": c,
                        "level": level,
                        "n": int(keep.sum()),
                        "status": "SUPPRESSED_N_LT_30",
                    }
                )
                continue
            r = metrics(np.asarray(y)[keep], p[keep], t)
            ci = bootstrap(np.asarray(y)[keep], p[keep], repeats, seed, t)
            rows.append(
                {
                    "variable": c,
                    "level": level,
                    "n": int(keep.sum()),
                    "status": "DESCRIPTIVE_CONDITIONAL",
                    **{k: v for k, v in r.items() if np.isscalar(v)},
                    "balanced_accuracy_lower": ci["balanced_accuracy"]["lower"],
                    "balanced_accuracy_upper": ci["balanced_accuracy"]["upper"],
                }
            )
    write_csv(out / "subgroups.csv", pd.DataFrame(rows))
    write_csv(out / "calibration.csv", pd.DataFrame(calibration(y, p)))
    pred = (p[:, 1] >= t).astype(int) if p.shape[1] == 2 else p.argmax(axis=1)
    bp = (b[:, 1] >= 0.5).astype(int) if b.shape[1] == 2 else b.argmax(axis=1)
    prediction = pd.DataFrame({"y": y, "predicted": pred, "baseline_predicted": bp})
    for k in range(p.shape[1]):
        prediction[f"prob_{k}"] = p[:, k]
    write_csv(out / "test_predictions.csv", prediction)
    output = {
        "selected": m,
        "baseline": metrics(y, b),
        "weighted_point_estimates": weighted,
        "conditional_respondent_bootstrap_ci": bootstrap(y, p, repeats, seed, t),
        "paired_difference_ci": bootstrap(y, p, repeats, seed, t, other=b),
        "mcnemar": mcnemar(np.asarray(y), pred, bp) if p.shape[1] == 2 else None,
        "uncertainty_scope": "Conditional test-respondent performance for fixed models, not population survey-design intervals; training/model selection uncertainty excluded",
        "test_n": len(y),
        "evaluation_count": 1,
    }
    write_json(result, output)
    write_json(
        ledger,
        {
            "state": "COMPLETE",
            "test_reused": False,
            "evaluation_count": 1,
            "result_sha256": digest(result),
        },
    )
    return output
