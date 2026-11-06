import numpy as np
from sklearn.base import clone
from src.features.engineering import specifications, transform_raw
from src.modeling.models import build_pipeline, ensemble
from src.data.outcomes import outcome
import pytest


@pytest.mark.parametrize(
    "selector",
    ["original", "mutual_info", "l1", "tree", "rfe", "permutation", "clinical", "interactions"],
)
def test_fold_local_fit_and_unseen_categories(synthetic, selector):
    X = transform_raw(synthetic, specifications())
    y = outcome(synthetic).fillna(0).astype(int)
    pipe = build_pipeline(X.columns, specifications(), selector=selector, k=5)
    train = X.iloc[:700].copy()
    test = X.iloc[700:].copy()
    m = clone(pipe).fit(train, y.iloc[:700])
    before = m.predict_proba(test)
    test.loc[:, "_BMI5"] = 1e8
    test.loc[:, "EDUCA"] = 999
    assert np.isfinite(m.predict_proba(test)).all()
    assert before.shape == (260, 2)
    # Test values never affect fitted imputer statistics.
    numeric = m.named_steps["pre"].named_transformers_["num"].named_steps["impute"]
    assert numeric.statistics_[0] < 100


@pytest.mark.parametrize("strategy", ["class_weight", "random_under", "smote"])
def test_resampling_inside_pipeline(synthetic, strategy):
    X = transform_raw(synthetic, specifications())
    y = outcome(synthetic).fillna(0).astype(int)
    m = build_pipeline(X.columns, specifications(), imbalance=strategy).fit(
        X.iloc[:700], y.iloc[:700]
    )
    assert m.predict_proba(X.iloc[700:]).shape == (260, 2)


def test_constant_feature(synthetic):
    X = transform_raw(synthetic, specifications())
    X["_BMI5"] = 1
    y = outcome(synthetic).fillna(0).astype(int)
    m = build_pipeline(X.columns, specifications()).fit(X, y)
    assert np.isfinite(m.predict_proba(X)).all()


def test_smote_variant_rejects_categorical(synthetic):
    with pytest.raises(ValueError, match="mixed categorical"):
        build_pipeline(specifications(), specifications(), imbalance="borderline_smote")


def test_stacking_full_pipelines(synthetic):
    X = transform_raw(synthetic, specifications())
    y = outcome(synthetic).fillna(0).astype(int)
    m = ensemble(X.columns, specifications(), "stacking", 2015).fit(X.iloc[:700], y.iloc[:700])
    assert m.predict_proba(X.iloc[700:]).shape == (260, 2)
