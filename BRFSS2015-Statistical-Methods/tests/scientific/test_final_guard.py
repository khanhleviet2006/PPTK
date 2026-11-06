import numpy as np
import pandas as pd
import pytest
from src.evaluation.final import final_evaluate
from src.data.ingest import ScientificValidationError
from src.utils.io import write_json


@pytest.mark.parametrize("state", ["accessed", "corrupt"])
def test_interrupted_test_fails_closed(tmp_path, state):
    ledger = tmp_path / "test_access.json"
    if state == "corrupt":
        ledger.write_bytes(b"")
    else:
        write_json(ledger, {"state": "ACCESSED", "purpose": "interruption fixture"})
    with pytest.raises(ScientificValidationError, match="accessed|Unreadable"):
        final_evaluate(
            tmp_path, pd.DataFrame({"x": [1]}), np.array([0]), pd.DataFrame(), np.ones(1)
        )


def test_model_tampering_before_access_fails_closed(tmp_path):
    write_json(tmp_path / "frozen.json", {"model_sha256": "invalid"})
    (tmp_path / "frozen_model.joblib").write_bytes(b"not-the-frozen-model")
    with pytest.raises(ScientificValidationError, match="Frozen model changed"):
        final_evaluate(
            tmp_path, pd.DataFrame({"x": [1]}), np.array([0]), pd.DataFrame(), np.ones(1)
        )
    assert not (tmp_path / "test_access.json").exists()
