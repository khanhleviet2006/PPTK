import os
import shutil
import subprocess
import numpy as np
import pandas as pd
import pytest
from scipy.special import expit
from src.statistics.survey import Design, logistic


def test_against_r_survey(tmp_path):
    r = os.environ.get("BRFSS_RSCRIPT") or shutil.which("Rscript")
    if not r:
        pytest.skip("R_REFERENCE_NOT_VERIFIED: set BRFSS_RSCRIPT to run numerical comparison")
    rng = np.random.default_rng(817)
    n = 800
    x = rng.normal(size=n)
    y = rng.binomial(1, expit(-0.5 + 0.7 * x))
    d = pd.DataFrame(
        {
            "weight": rng.uniform(0.5, 5, n),
            "stratum": np.arange(n) // 16,
            "psu": np.arange(n) // 4,
            "x": x,
            "y": y,
            "domain": (x > 0).astype(int),
        }
    )
    path = tmp_path / "data.csv"
    d.to_csv(path, index=False)
    prefix = tmp_path / "reference"
    subprocess.run([r, "scripts/reference_survey.R", str(path), str(prefix)], check=True)
    design = Design(d.rename(columns={"weight": "_LLCPWT", "stratum": "_STSTR", "psu": "_PSU"}))
    m = design.mean(y)
    ref = pd.read_csv(str(prefix) + "_mean.csv")
    assert np.isclose(m["estimate"], ref.estimate.iloc[0], rtol=1e-9)
    assert np.isclose(m["se"] ** 2, ref.variance.iloc[0], rtol=1e-8)
    b, cov, _, _ = logistic(design, np.c_[np.ones(n), x], y)
    ref = pd.read_csv(str(prefix) + "_logistic.csv")
    assert np.allclose(b, ref.beta, rtol=1e-7, atol=1e-8)
    assert np.allclose(cov, pd.read_csv(str(prefix) + "_cov.csv"), rtol=1e-6, atol=1e-9)
    md = design.mean(y, d.domain.eq(1))
    ref = pd.read_csv(str(prefix) + "_domain.csv")
    assert np.isclose(md["se"] ** 2, ref.variance.iloc[0], rtol=1e-8)


def test_multinomial_against_r(tmp_path):
    from scipy.special import softmax
    from src.statistics.survey import multinomial

    r = os.environ.get("BRFSS_RSCRIPT") or shutil.which("Rscript")
    if not r:
        pytest.skip("R_REFERENCE_NOT_VERIFIED")
    rng = np.random.default_rng(617)
    n = 800
    x = rng.normal(size=n)
    prob = softmax(np.c_[np.zeros(n), -0.5 + 0.6 * x, -0.8 - 0.4 * x], axis=1)
    y = np.array([rng.choice(3, p=row) for row in prob])
    d = pd.DataFrame(
        {
            "weight": rng.uniform(0.5, 5, n),
            "stratum": np.arange(n) // 16,
            "psu": np.arange(n) // 4,
            "x": x,
            "y": (y == 2).astype(int),
            "domain": (x > 0).astype(int),
            "ymulti": y,
        }
    )
    path = tmp_path / "data.csv"
    d.to_csv(path, index=False)
    prefix = tmp_path / "reference"
    subprocess.run([r, "scripts/reference_survey.R", str(path), str(prefix)], check=True)
    design = Design(d.rename(columns={"weight": "_LLCPWT", "stratum": "_STSTR", "psu": "_PSU"}))
    b, cov, _, _ = multinomial(design, np.c_[np.ones(n), x], y)
    assert np.allclose(b, pd.read_csv(str(prefix) + "_multi_beta.csv").beta, rtol=1e-5, atol=1e-6)
    assert np.allclose(cov, pd.read_csv(str(prefix) + "_multi_cov.csv"), rtol=1e-5, atol=1e-7)
