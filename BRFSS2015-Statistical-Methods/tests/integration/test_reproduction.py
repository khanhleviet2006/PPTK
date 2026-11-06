import numpy as np
import pandas as pd
import pytest
from scripts.reproduce_baseline import reproduce, FEATURES
from src.utils.io import write_json, read_json
from src.data.ingest import ScientificValidationError


def test_processed_approximate_reproduction(tmp_path):
    rng = np.random.default_rng(2)
    d = pd.DataFrame(rng.normal(size=(240, len(FEATURES))), columns=FEATURES)
    d["Diabetes_binary"] = np.tile([0, 0, 1], 80)
    path = tmp_path / "processed.csv"
    d.to_csv(path, index=False)
    provenance = tmp_path / "provenance.json"
    write_json(
        provenance,
        {
            "url": "synthetic fixture",
            "outcome_definition": "synthetic binary",
            "cohort_definition": "240 artificial rows",
        },
    )
    out = tmp_path / "run"
    results = reproduce(path, provenance, out)
    assert set(results) == {"LR", "DT", "RF", "KNN", "NB"}
    assert read_json(out / "results.json")["classification"] == "APPROXIMATE_REPRODUCTION"
    with pytest.raises(ScientificValidationError, match="already evaluated"):
        reproduce(path, provenance, out)
