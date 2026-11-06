from pathlib import Path
import argparse
from src.utils.io import read_json, Checkpoints
from src.pipeline import STAGES


def verify(out):
    out = Path(out)
    m = read_json(out / "run_manifest.json")
    cp = Checkpoints(out, m["signature"])
    for stage in STAGES:
        if not cp.valid(stage):
            raise AssertionError(f"Invalid/missing checkpoint: {stage}")
    for f in [
        "audit.json",
        "cohort.json",
        "missingness.csv",
        "table1.csv",
        "prevalence.json",
        "inference_diagnostics.json",
        "development.json",
        "final_metrics.json",
        "final_report.md",
        "feature_importance.csv",
        "model_comparison.csv",
        "grouped_wald.csv",
    ]:
        assert (out / f).stat().st_size > 0, f
    assert read_json(out / "test_access.json")["evaluation_count"] == 1
    print("OUTPUTS_VERIFIED", out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("out")
    verify(p.parse_args().out)
