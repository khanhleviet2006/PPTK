import numpy as np
import pandas as pd
import pytest
from src.data.outcomes import outcome, eligible
from src.features.engineering import transform_raw, specifications
from src.audit.validation import validate_source
from src.data.ingest import ScientificValidationError, discover


def test_outcome():
    d = pd.DataFrame({"DIABETE3": [1, 2, 3, 4, 7, 9, np.nan], "PREDIAB1": [np.nan] * 7})
    assert outcome(d).dropna().tolist() == [1, 0]
    assert outcome(d, "core_three").dropna().tolist() == [2, 0, 1]
    assert np.isnan(outcome(d, "module_three").iloc[2])
    assert outcome(d, "module_three").dropna().tolist() == [2, 1]


def test_specific_missing_codes(synthetic):
    x = synthetic.copy()
    x.loc[:2, "PHYSHLTH"] = [88, 77, 9]
    x.loc[:2, "_DRNKWEK"] = [99900, 700, 0]
    X = transform_raw(x, specifications())
    assert X.PHYSHLTH.iloc[0] == 0 and np.isnan(X.PHYSHLTH.iloc[1]) and X.PHYSHLTH.iloc[2] == 9
    assert np.isnan(X._DRNKWEK.iloc[0]) and X._DRNKWEK.iloc[1] == 7


def test_duplicate_and_weight(synthetic):
    m = {"source_columns": synthetic.columns.tolist()}
    d = synthetic.copy()
    d.loc[1, ["_STATE", "SEQNO"]] = d.loc[0, ["_STATE", "SEQNO"]].values
    with pytest.raises(ScientificValidationError):
        validate_source(d, m, specifications(), True)
    d = synthetic.copy()
    d.loc[0, "_LLCPWT"] = 0
    with pytest.raises(ScientificValidationError):
        validate_source(d, m, specifications(), True)


def test_eligibility(synthetic):
    k, y = eligible(synthetic)
    assert not y[k].isna().any()
    assert synthetic.loc[k, "DIABETE3"].isin([1, 3]).all()


def test_discovery(tmp_path):
    with pytest.raises(FileNotFoundError, match="No substitute"):
        discover(directories=[tmp_path])
    (tmp_path / "LLCP2015.XPT").write_bytes(b"bad")
    assert discover(directories=[tmp_path]).name == "LLCP2015.XPT"
