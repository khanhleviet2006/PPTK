import numpy as np
import pandas as pd
from scipy.special import expit, softmax
from src.statistics.survey import Design, logistic, multinomial, coefficient_table
from src.data.ingest import ScientificValidationError
import pytest


def frame(n):
    return pd.DataFrame(
        {"_LLCPWT": np.ones(n), "_STSTR": np.arange(n) // 8, "_PSU": np.arange(n) // 2}
    )


def test_weighted_mean_hand_calculation():
    d = pd.DataFrame(
        {"_LLCPWT": [1.0, 2.0, 3.0, 4.0], "_STSTR": [1, 1, 2, 2], "_PSU": [1, 2, 3, 4]}
    )
    x = np.array([0, 1, 0, 1])
    s = Design(d)
    m = s.mean(x, proportion=True)
    assert m["estimate"] == 0.6
    u = d._LLCPWT.to_numpy() * (x - 0.6) / 10
    expected = (u[0] - u[1]) ** 2 + (u[2] - u[3]) ** 2
    assert np.isclose(m["se"] ** 2, expected)
    assert m["lower"] < 0.6 < m["upper"]


def test_domain_keeps_zero_psus():
    d = frame(16)
    s = Design(d)
    keep = np.arange(16) % 2 == 0
    r = s.mean(np.arange(16), keep)
    assert r["n"] == 8 and r["df"] == 6


def test_scale_invariance_and_cluster_variance():
    d = frame(160)
    x = (np.arange(160) // 2) % 2
    s = Design(d)
    a = s.mean(x)
    d._LLCPWT *= 100
    assert np.isclose(Design(d).mean(x)["se"], a["se"])
    iid = d.copy()
    iid._PSU = np.arange(160)
    assert a["se"] > Design(iid).mean(x)["se"]


def test_coefficient_recovery_and_odds():
    rng = np.random.default_rng(123)
    n = 10000
    X = np.column_stack([np.ones(n), rng.normal(size=n)])
    y = rng.binomial(1, expit(X @ np.array([-0.5, 0.8])))
    b, v, df, _ = logistic(Design(frame(n)), X, y)
    assert np.max(np.abs(b - [-0.5, 0.8])) < 0.08
    t = coefficient_table(b, v, df, ["intercept", "x"])
    assert np.allclose(t.OR, np.exp(b)) and (t.lower < t.OR).all()


def test_multinomial_recovery():
    rng = np.random.default_rng(5)
    n = 6000
    X = np.c_[np.ones(n), rng.normal(size=n)]
    true = np.array([[-0.4, 0.6], [-0.8, -0.5]])
    p = softmax(np.c_[np.zeros(n), X @ true.T], axis=1)
    y = np.array([rng.choice(3, p=row) for row in p])
    b, v, _, _ = multinomial(Design(frame(n)), X, y)
    assert np.max(np.abs(b - true.ravel())) < 0.12
    assert np.linalg.eigvalsh(v).min() > 0


def test_singleton():
    d = frame(16)
    d.loc[:7, "_PSU"] = 1
    with pytest.raises(ScientificValidationError):
        Design(d)
