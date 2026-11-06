"""Synthetic BRFSS-shaped records; no epidemiological estimates may be inferred."""

import numpy as np
import pandas as pd
from scipy.special import expit
from src.features.engineering import specifications


def generate(n=960, seed=2015):
    rng = np.random.default_rng(seed)
    n = max(240, n)
    n = n // 4 * 4
    d = pd.DataFrame(
        {
            "SEQNO": np.arange(n) + 2015000000,
            "_STATE": rng.choice([1, 6, 12, 36], n),
            "_PSU": np.arange(n) // 2,
            "_STSTR": np.arange(n) // 8,
            "_LLCPWT": rng.uniform(0.5, 3, n),
        }
    )
    for c, spec in specifications().items():
        if "valid" in spec:
            d[c] = rng.choice(spec["valid"], n)
        else:
            d[c] = rng.uniform(0, 10, n)
    d["_BMI5"] = np.clip(rng.normal(2800, 500, n), 1400, 5000)
    d["_AGEG5YR"] = rng.integers(1, 14, n)
    d["_FRUTSUM"] = rng.integers(0, 500, n)
    d["_VEGESUM"] = rng.integers(0, 600, n)
    d["_DRNKWEK"] = rng.integers(0, 1400, n)
    for c in ["PHYSHLTH", "MENTHLTH"]:
        d[c] = rng.choice([88, 1, 5, 15, 30, 77, 99], n, p=[0.4, 0.1, 0.15, 0.1, 0.15, 0.05, 0.05])
    p = expit(-2 + 0.08 * (d._AGEG5YR - 6) + 0.0005 * (d._BMI5 - 2800))
    d["DIABETE3"] = np.where(rng.random(n) < p, 1, 3)
    border = (d.DIABETE3 == 3) & (rng.random(n) < 0.1)
    d.loc[border, "DIABETE3"] = 4
    d["PREDIAB1"] = np.where(d.DIABETE3.eq(4), 1, np.where(d.DIABETE3.eq(3), 3, np.nan))
    for c in ["INCOME2", "_BMI5", "TOLDHI2"]:
        d.loc[rng.random(n) < 0.03, c] = np.nan
    return d
