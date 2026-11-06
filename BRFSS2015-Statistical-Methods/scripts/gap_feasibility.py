"""Source/cohort/biomarker audits plus an isolated synthetic leakage diagnostic."""

from pathlib import Path
import json
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from src.utils.io import write_json, write_csv, digest, read_json


def run(source_root):
    source_root = Path(source_root)
    out = Path("reports/evidence/gap_extension")
    out.mkdir(parents=True, exist_ok=True)
    p = source_root / "processed/uci_891.csv"
    d = pd.read_csv(p)
    meta = json.loads((source_root / "processed/uci_metadata.json").read_text())
    write_json(
        out / "processed_source_audit.json",
        {
            "source_url": "https://archive.ics.uci.edu/static/public/891/data.csv",
            "metadata_url": "https://archive.ics.uci.edu/api/dataset?id=891",
            "sha256": digest(p),
            "records": len(d),
            "columns": list(d),
            "counts": d.Diabetes_binary.value_counts().to_dict(),
            "missing": int(d.isna().sum().sum()),
            "duplicate_predictor_outcome_rows": int(d.drop(columns=["ID"]).duplicated().sum()),
            "metadata_inconsistencies": "Abstract says35 features/lab tests while schema has21 predictors. year_of_dataset_creation=2017 does not certify source BRFSS year. Same Kaggle feature names/cohort size are evidence of similarity, not byte-identical provenance.",
            "exact_reproduction": "NOT_POSSIBLE_FROM_AVAILABLE_EVIDENCE",
            "predictive_execution": "BLOCKED_UNKNOWN_LINKAGE_TO_OLD_2015_TEST_RESPONDENTS",
            "reason": "Sequential UCI ID cannot map to CDC state+SEQNO; old final-test overlap cannot be excluded. No new model scored on these potentially overlapping respondents.",
            "paper_params_verified": {
                "DT": {"max_depth": 50, "criterion": "entropy"},
                "RF": {
                    "random_state": 42,
                    "criterion": "entropy",
                    "depth_trees_phrase": "ambiguous",
                },
                "KNN": {"n_neighbors": 3},
                "LR": {"random_state": 0},
            },
            "metadata": meta,
        },
    )
    text = (source_root / "codebook.txt").read_text()
    matches = []
    for term in ["PDIABTST", "BLDSUGAR", "DIABETE3", "INSULIN", "HbA1c", "genetic"]:
        ix = text.lower().find(term.lower())
        matches.append(
            {
                "term": term,
                "found": ix >= 0,
                "context": text[max(0, ix - 200) : ix + 1000] if ix >= 0 else None,
            }
        )
    write_json(
        out / "clinical_genetic_availability.json",
        {
            "source": "CDC2015 codebook",
            "codebook_sha256": digest(source_root / "codebook15_llcp.pdf"),
            "matches": matches,
            "conclusion": "DIABETE3 is self-reported diagnosis; testing/monitoring questions and medication are not measured blood glucose, HbA1c or genetic biomarkers. External clinical/genetic data required; clinical verification not implemented.",
        },
    )
    X, y = make_classification(
        n_samples=500, n_features=6, n_informative=3, weights=[0.9, 0.1], random_state=917
    )
    cv = StratifiedKFold(3, shuffle=True, random_state=917)
    valid = cross_val_score(
        Pipeline(
            [("sample", SMOTE(random_state=917, k_neighbors=3)), ("model", LogisticRegression())]
        ),
        X,
        y,
        cv=cv,
        scoring="balanced_accuracy",
    )
    XX, yy = SMOTE(random_state=917, k_neighbors=3).fit_resample(X, y)
    invalid = cross_val_score(LogisticRegression(), XX, yy, cv=cv, scoring="balanced_accuracy")
    write_json(
        out / "isolated_leakage_diagnostic.json",
        {
            "synthetic": True,
            "valid_fold_local_BA": valid.tolist(),
            "deliberately_invalid_global_resampling_BA": invalid.tolist(),
            "warning": "EDUCATIONAL_ONLY_NOT_ELIGIBLE_FOR_SELECTION. Validation populations differ after global SMOTE; difference is not a causal leakage effect and is not evidence about Chang.",
        },
    )
    cohort = read_json("runs/real_final_quick/cohort.json")
    write_csv(
        out / "cohort_flow.csv",
        pd.DataFrame(
            [
                {"stage": "Original CDC", "n": cohort["total"]},
                {"stage": "Binary eligible", "n": cohort["eligible"]},
                {"stage": "Complete-case inference", "n": cohort["complete_case"]},
                {"stage": "Original development pool", "n": 338046},
                {"stage": "Extension development budget", "n": 2000},
                {"stage": "Protected legacy test NOT REUSED", "n": 84512},
            ]
        ),
    )


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument(
        "--source-root",
        required=True,
        help="Folder containing processed/ UCI files and original CDC codebook files",
    )
    run(p.parse_args().source_root)
