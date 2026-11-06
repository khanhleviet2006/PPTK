from pathlib import Path
from src.utils.io import read_json, digest, write_json
from scripts.audit_research_gaps import snapshot


def verify():
    p = Path("runs/gap_real_quick_v4")
    m = read_json(p / "manifest.json")
    r = read_json(p / "registry.json")
    assert len(r) == 78 and all(x["status"] == "SUCCESS" for x in r)
    for x in r:
        assert digest(p / x["oof_file"]) == x["oof_sha256"]
    assert all(digest(k) == v for k, v in m["code"].items())
    ids = read_json(p / "development_ids.json")["ids"]
    old = read_json("runs/real_final_quick/split.json")
    assert not set(ids) & set(old["test_ids"]) and set(ids) <= set(old["train_ids"])
    assert read_json(p / "integrity.json")["unchanged"]
    protected = read_json(p / "integrity.json")["legacy_protected_hashes"]
    assert protected == snapshot()
    assert read_json("runs/real_final_quick/test_access.json")["evaluation_count"] == 1
    ledger = read_json("runs/temporal_2017/external_access.json")
    assert ledger["state"] == "COMPLETE" and ledger["evaluation_count"] == 1
    assert ledger["result_sha256"] == digest("runs/temporal_2017/external_metrics.json")
    frozen = read_json("runs/temporal_2017/frozen_before_external.json")
    assert frozen["model_sha256"] == digest("runs/temporal_2017/temporal_model.joblib")
    required = [
        "RESEARCH_GAP_EXECUTION_MATRIX",
        "RESEARCH_GAP_RESULTS",
        "CHANG_2022_REPRODUCTION",
        "FEATURE_SELECTION_COMPARISON",
        "ADVANCED_ML_COMPARISON",
        "ENSEMBLE_COMPARISON",
        "IMBALANCE_EXPERIMENTS",
        "CALIBRATION_ANALYSIS",
        "SURVEY_STATISTICAL_INFERENCE",
        "ROBUSTNESS_ANALYSIS",
        "EXTERNAL_VALIDATION_FEASIBILITY",
        "REPRODUCIBILITY",
        "FINAL_RESEARCH_REPORT",
        "UNFINISHED_WORK",
    ]
    assert all(Path("reports", x + ".md").stat().st_size > 100 for x in required)
    write_json(
        "reports/evidence/gap_extension/output_verification.json",
        {
            "status": "PASS",
            "binary_experiments": 78,
            "legacy_overlap": 0,
            "legacy_artifacts_unchanged": True,
            "legacy_evaluation_count": 1,
            "temporal_evaluation_count": 1,
        },
    )
    print(
        "Extension outputs verified; legacy source/test immutable;78 experiments; temporal evaluation_count=1."
    )


if __name__ == "__main__":
    verify()
