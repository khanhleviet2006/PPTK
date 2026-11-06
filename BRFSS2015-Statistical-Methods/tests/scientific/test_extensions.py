import numpy as np
import pandas as pd
import pytest
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold
from src.data.synthetic import generate
from src.features.engineering import transform_raw, specifications
from src.data.outcomes import outcome
from src_extensions.experiments import Selector, make, evaluate, policy_metrics


@pytest.mark.parametrize("selector", ["pca", "selectkbest", "rfecv", "rf", "xgb", "shap"])
def test_new_selectors(selector):
    rng = np.random.default_rng(4)
    X = rng.normal(size=(160, 12))
    y = (X[:, 0] + rng.normal(size=160) > 0.3).astype(int)
    m = clone(Selector(selector, 5)).fit(X, y)
    assert m.transform(X).shape[0] == len(X)
    assert np.isfinite(m.transform(X)).all()


@pytest.mark.parametrize("calibration", ["sigmoid", "isotonic"])
def test_calibration_wraps_full_pipeline(calibration):
    d = generate(320)
    X = transform_raw(d, specifications())
    y = outcome(d).fillna(0).astype(int)
    m = make(X, specifications(), dict(model="logistic", calibration=calibration), 4)
    assert m.estimator.steps[0][0] == "pre"
    m.fit(X.iloc[:240], y.iloc[:240])
    assert m.predict_proba(X.iloc[240:]).shape == (80, 2)


def test_nominal_adasyn_rejected():
    with pytest.raises(ValueError, match="continuous-only"):
        make(
            pd.DataFrame(columns=specifications()),
            specifications(),
            dict(model="logistic", sampling="adasyn"),
            4,
        )


def test_outer_oof_and_serialized_cache(tmp_path):
    d = generate(320)
    X = transform_raw(d, specifications())
    y = outcome(d).fillna(0).to_numpy(int)
    cv = list(StratifiedKFold(2, shuffle=True, random_state=2).split(X, y))
    exp = dict(model="logistic", stage="fixture")
    r = evaluate(X, y, specifications(), tmp_path, exp, cv, 4)
    r2 = evaluate(X, y, specifications(), tmp_path, exp, cv, 4)
    assert r == r2
    oof = pd.read_csv(tmp_path / r["oof_file"])
    assert len(oof) == len(y) and oof.y.tolist() == y.tolist()
    assert len(r["thresholds_inner_training"]) == 2
    assert all(0.1 <= t <= 0.9 + 1e-9 for t in r["thresholds_inner_training"])


def test_policy_metrics_use_pred_not_half_threshold():
    y = np.array([0, 0, 1, 1])
    p = np.tile([0.7, 0.3], (4, 1))
    pred = np.array([0, 1, 0, 1])
    r = policy_metrics(y, p, pred)
    assert (
        r["balanced_accuracy"] == 0.5
        and r["accuracy"] == 0.5
        and r["confusion_matrix"] == [[1, 1], [1, 1]]
    )


def test_smotenc_encoded_feature_names(tmp_path):
    d = generate(320)
    X = transform_raw(d, specifications())
    y = outcome(d).fillna(0).to_numpy(int)
    cv = list(StratifiedKFold(2, shuffle=True, random_state=2).split(X, y))
    r = evaluate(
        X,
        y,
        specifications(),
        tmp_path,
        dict(model="logistic", sampling="smotenc", stage="regression"),
        cv,
        4,
    )
    assert r["status"] == "SUCCESS"
    assert len(r["selected_features_by_fold"][0]) > 19


def test_temporal_interruption_does_not_reaccess(tmp_path):
    from src.utils.io import write_json
    from src_extensions.temporal import run

    write_json(tmp_path / "external_access.json", {"state": "ACCESSED", "evaluation_count": 1})
    with pytest.raises(RuntimeError, match="already accessed"):
        run("nonexistent", "nonexistent", "nonexistent", tmp_path)


def test_inner_feature_selection_has_no_fitted_outer_preprocessor():
    from src_extensions.experiments import FixedCodebookEncoder

    d = generate(320)
    X = transform_raw(d, specifications())
    y = outcome(d).fillna(0).to_numpy(int)
    for method in ["rfecv", "permutation"]:
        m = make(X, specifications(), dict(model="logistic", selector=method, k=5), 4)
        assert isinstance(m.named_steps["pre"], FixedCodebookEncoder)
        expanded = m.named_steps["pre"].fit_transform(X)
        assert np.isnan(
            expanded
        ).any()  # deterministic expansion did not impute validation information
        m.fit(X.iloc[:240], y[:240])
        assert m.predict_proba(X.iloc[240:]).shape == (80, 2)


def test_new_directory_cannot_reset_temporal_test(tmp_path, monkeypatch):
    import src_extensions.temporal as temporal
    from src.utils.io import write_json

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(temporal, "snapshot", lambda: {})
    monkeypatch.setattr(temporal, "specifications", lambda: {})
    write_json(
        tmp_path / "runs/temporal_2017/external_access.json",
        {"state": "COMPLETE", "evaluation_count": 1},
    )
    with pytest.raises(RuntimeError, match="cannot reset"):
        temporal.run(None, None, None, tmp_path / "new_directory")
    assert not (tmp_path / "new_directory/external_access.json").exists()
