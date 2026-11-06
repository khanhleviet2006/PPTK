"""Dataset B approximate reproduction, strictly separate from original inference."""

import argparse
from pathlib import Path
import numpy as np
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from src.data.ingest import load_processed, ScientificValidationError
from src.modeling.splits import create_split, save_split
from src.evaluation.metrics import metrics
from src.utils.io import digest, read_json, write_json

FEATURES = [
    "HighBP",
    "HighChol",
    "CholCheck",
    "BMI",
    "Smoker",
    "Stroke",
    "HeartDiseaseorAttack",
    "PhysActivity",
    "Fruits",
    "Veggies",
    "HvyAlcoholConsump",
    "AnyHealthcare",
    "NoDocbcCost",
    "GenHlth",
    "MentHlth",
    "PhysHlth",
    "DiffWalk",
    "Sex",
    "Age",
    "Education",
    "Income",
]


def reproduce(data, provenance, out, seed=2015):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "results.json").exists():
        raise ScientificValidationError(
            "Reproduction test was already evaluated; preserve prior results."
        )
    source = read_json(provenance)
    for field in ["url", "outcome_definition", "cohort_definition"]:
        if not source.get(field):
            raise ScientificValidationError(f"Provenance missing: {field}")
    d = load_processed(data)
    if set(FEATURES) - set(d):
        raise ScientificValidationError("Dataset B does not have required 21 predictors")
    if d.Diabetes_binary.isna().any() or not d.Diabetes_binary.isin([0, 1]).all():
        raise ScientificValidationError("Invalid processed binary outcome")
    ids = np.arange(len(d)).astype(str)
    y = d.Diabetes_binary.to_numpy(int)
    X = d[FEATURES]
    if X.select_dtypes("number").shape[1] != 21:
        raise ScientificValidationError("Non-numeric Dataset B predictors")
    a, b, manifest = create_split(ids, y, seed)
    save_split(out / "split.json", manifest)
    write_json(
        out / "provenance.json",
        {
            "classification": "APPROXIMATE_REPRODUCTION",
            "user_provenance": source,
            "source_sha256": digest(data),
            "n": len(d),
            "feature_list": FEATURES,
            "seed": seed,
            "differences": [
                "No induced 5% missingness; paper details unresolved",
                "Train-only imputation and scaling; no pre-split SMOTE",
                "Defaults fixed in code; original hyperparameters unverified",
                "Respondent identities unavailable; row IDs cannot establish independence of duplicate predictor patterns",
            ],
            "duplicate_full_rows": int(d.duplicated().sum()),
            "comparable_with_82_26": False,
        },
    )
    models = {
        "LR": LogisticRegression(max_iter=1000, random_state=seed),
        "DT": DecisionTreeClassifier(max_depth=6, min_samples_leaf=10, random_state=seed),
        "RF": RandomForestClassifier(
            n_estimators=100, min_samples_leaf=5, random_state=seed, n_jobs=1
        ),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "NB": GaussianNB(),
    }
    scores = {}
    fitted = {}
    cv = list(StratifiedKFold(3, shuffle=True, random_state=seed).split(X.iloc[a], y[a]))
    for name, model in models.items():
        pipe = Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", MinMaxScaler()),
                ("model", model),
            ]
        )
        ss = []
        for train, val in cv:
            m = clone(pipe).fit(X.iloc[a[train]], y[a[train]])
            ss.append(metrics(y[a[val]], m.predict_proba(X.iloc[a[val]]))["balanced_accuracy"])
        scores[name] = float(np.mean(ss))
        fitted[name] = pipe.fit(X.iloc[a], y[a])
    selected = sorted(scores, key=lambda k: (-scores[k], k))[0]
    write_json(out / "frozen_selection.json", {"selected": selected, "cv": scores})
    # A fixed single batch evaluates all prespecified baselines. No post-test selection.
    write_json(out / "test_access.json", {"state": "ACCESSED", "evaluations": 1})
    results = {name: metrics(y[b], m.predict_proba(X.iloc[b])) for name, m in fitted.items()}
    write_json(
        out / "results.json",
        {"classification": "APPROXIMATE_REPRODUCTION", "cv_selected": selected, "test": results},
    )
    write_json(out / "test_access.json", {"state": "COMPLETE", "evaluations": 1})
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--provenance", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=2015)
    reproduce(**vars(p.parse_args()))
