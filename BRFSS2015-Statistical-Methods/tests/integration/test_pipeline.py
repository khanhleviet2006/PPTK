from src.pipeline import run
from scripts.verify_outputs import verify
from src.utils.io import read_json, digest
from src.data.ingest import ScientificValidationError
import pytest


def test_end_to_end_resume(tmp_path):
    run(tmp_path, synthetic=True, n=960)
    verify(tmp_path)
    h = digest(tmp_path / "final_metrics.json")
    run(tmp_path, synthetic=True, n=960)
    assert digest(tmp_path / "final_metrics.json") == h
    assert read_json(tmp_path / "test_access.json")["evaluation_count"] == 1
    with pytest.raises(ScientificValidationError, match="signature changed"):
        run(tmp_path, synthetic=True, n=960, seed=4)
