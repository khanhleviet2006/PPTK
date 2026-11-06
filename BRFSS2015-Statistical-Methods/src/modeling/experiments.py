import io
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import train_test_split
from src.modeling.models import build_pipeline, ensemble, available
from src.modeling.splits import folds
from src.evaluation.metrics import metrics
from src.utils.io import write_json, atomic_bytes, read_json, canonical_hash, digest
from src.data.ingest import ScientificValidationError

ENSEMBLES = ["feature_ensemble", "soft_voting", "stacking"]


def plan(profile, config):
    # Fixed, finite ablations, not an unconstrained Cartesian search.
    exps = [
        dict(model=n, selector="original", k=10, imbalance="none", budget=1)
        for n in config["models"]
    ]
    if profile == "quick":
        exps += [
            dict(model="logistic", selector=s, k=10, imbalance="none", budget=1)
            for s in ["mutual_info", "l1", "tree"]
        ]
        exps += [
            dict(model="logistic", selector="original", k=10, imbalance=i, budget=1)
            for i in ["class_weight", "random_under", "smote"]
        ]
    if profile != "quick":
        for method in config["selectors"]:
            if method == "original":
                continue
            ks = (
                config["top_k"]
                if method in ["mutual_info", "l1", "tree", "permutation", "rfe"]
                else [10]
            )
            for k in ks:
                exps.append(
                    dict(model="logistic", selector=method, k=k, imbalance="none", budget=1)
                )
        for strategy in ["class_weight", "random_under", "smote"]:
            for n in ["logistic", "random_forest"]:
                exps.append(dict(model=n, selector="original", k=10, imbalance=strategy, budget=1))
    if profile == "extended":
        for n in ["logistic", "random_forest", "decision_tree"]:
            exps.append(dict(model=n, selector="original", k=10, imbalance="none", budget=2))
    return exps


def develop(X, y, specs, out, config, profile="quick", seed=2015):
    settings = config["profiles"][profile]
    y = np.asarray(y, int)
    cv = folds(y, settings["folds"], seed)
    write_json(
        out / "cv_splits.json", [{"train": a.tolist(), "validation": b.tolist()} for a, b in cv]
    )
    history = []
    best = None
    best_score = -np.inf
    for exp in plan(profile, config):
        eid = canonical_hash(exp)[:16]
        if not available(exp["model"]):
            history.append(
                {**exp, "experiment_id": eid, "status": "SKIPPED_DEPENDENCY_UNAVAILABLE"}
            )
            continue
        pipe = (
            ensemble(X.columns, specs, exp["model"], seed)
            if exp["model"] in ENSEMBLES
            else build_pipeline(
                X.columns,
                specs,
                name=exp["model"],
                selector=exp["selector"],
                k=exp["k"],
                imbalance=exp["imbalance"],
                budget=exp["budget"],
                seed=seed,
            )
        )
        cache = out / "experiments" / (eid + ".joblib")
        metadata = out / "experiments" / (eid + ".json")
        start = time.time()
        if (
            cache.exists()
            and metadata.exists()
            and read_json(metadata).get("prediction_hash") == digest(cache)
        ):
            oof = joblib.load(cache)
        else:
            oof = np.full((len(y), len(np.unique(y))), np.nan)
            for train, val in cv:
                m = clone(pipe).fit(X.iloc[train], y[train])
                oof[val] = m.predict_proba(X.iloc[val])
            buf = io.BytesIO()
            joblib.dump(oof, buf)
            atomic_bytes(cache, buf.getvalue())
            write_json(metadata, {"prediction_hash": digest(cache), "experiment": exp})
        # Threshold selection is part of development, on OOF predictions only.
        thresholds = config["threshold_grid"] if oof.shape[1] == 2 else [0.5]
        summaries = []
        for t in thresholds:
            scores = [metrics(y[b], oof[b], t)["balanced_accuracy"] for _, b in cv]
            summaries.append((float(np.mean(scores)), t, scores))
        score, t, scores = max(summaries, key=lambda r: (r[0], -abs(r[1] - 0.5)))
        row = {
            **exp,
            "experiment_id": eid,
            "status": "SUCCESS",
            "cv_mean": score,
            "cv_fold_scores": scores,
            "threshold": t,
            "oof_metrics": metrics(y, oof, t),
            "seconds": time.time() - start,
        }
        history.append(row)
        write_json(out / "development.json", history)
        if score > best_score or (score == best_score and (best is None or eid < best[0])):
            best_score = score
            best = (eid, pipe, t, exp, oof)
    if best is None:
        raise ScientificValidationError("No model successfully completed development")
    eid, pipe, threshold, exp, oof = best
    # Interpretation uses a fresh training-internal split, never final test respondents.
    from sklearn.inspection import permutation_importance
    from src.utils.io import write_csv

    ia, ib = train_test_split(np.arange(len(y)), test_size=0.25, stratify=y, random_state=seed + 1)
    explain_model = clone(pipe).fit(X.iloc[ia], y[ia])
    importance = permutation_importance(
        explain_model,
        X.iloc[ib],
        y[ib],
        scoring="balanced_accuracy",
        n_repeats=settings["permutations"],
        random_state=seed,
        n_jobs=1,
    )
    write_csv(
        out / "feature_importance.csv",
        pd.DataFrame(
            {
                "variable": list(X),
                "importance_mean": importance.importances_mean,
                "importance_sd": importance.importances_std,
            }
        ),
    )
    final = clone(pipe).fit(X, y)
    buf = io.BytesIO()
    joblib.dump(final, buf)
    atomic_bytes(out / "frozen_model.joblib", buf.getvalue())
    write_json(
        out / "frozen.json",
        {
            "experiment_id": eid,
            "experiment": exp,
            "threshold": threshold,
            "model_sha256": digest(out / "frozen_model.joblib"),
            "cv_mean": best_score,
            "warning": "OOF score used for selection and threshold tuning; not an unbiased final performance estimate",
        },
    )
    # Freeze a same-cohort logistic comparator now, before test access.
    baseline = build_pipeline(X.columns, specs, seed=seed).fit(X, y)
    buf = io.BytesIO()
    joblib.dump(baseline, buf)
    atomic_bytes(out / "baseline_model.joblib", buf.getvalue())
    write_json(
        out / "baseline_frozen.json",
        {
            "model_sha256": digest(out / "baseline_model.joblib"),
            "type": "prespecified same-cohort logistic comparator; not a Chang reproduction",
        },
    )
    return history


def subsample_training(X, y, limit, seed):
    if limit and len(y) > limit:
        a, _ = train_test_split(np.arange(len(y)), train_size=limit, stratify=y, random_state=seed)
        return X.iloc[a].reset_index(drop=True), np.asarray(y)[a], a
    return X.reset_index(drop=True), np.asarray(y), np.arange(len(y))
