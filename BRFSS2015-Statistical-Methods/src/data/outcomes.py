"""Self-reported diagnosis categories, never inferred biochemical disease."""

import numpy as np
import pandas as pd
from src.data.ingest import ScientificValidationError


def outcome(df, mode="binary"):
    d = df["DIABETE3"]
    if mode == "binary":
        # Primary contrast: affirmative diabetes vs explicit no; borderline and pregnancy excluded.
        return d.map({1: 1.0, 3: 0.0})
    if mode == "core_three":
        # No claim that DIABETE3=3 proves absence of prediabetes.
        return d.map({3: 0.0, 4: 1.0, 1: 2.0})
    if mode == "binary_borderline_negative":
        return d.map({1: 1.0, 3: 0.0, 4: 0.0})
    if mode == "module_three":
        if "PREDIAB1" not in df:
            raise ScientificValidationError("PREDIAB1 missing; no module outcome can be inferred.")
        p = df["PREDIAB1"]
        y = pd.Series(np.nan, index=df.index)
        y.loc[d.eq(3) & p.eq(3)] = 0
        y.loc[d.eq(4) | (d.eq(3) & p.eq(1))] = 1
        y.loc[d.eq(1)] = 2
        # Geographic module eligibility must separately restrict the analysis design.
        return y
    raise ValueError(f"Unknown outcome: {mode}")


def eligible(df, mode="binary", exclude_territories=True):
    y = outcome(df, mode)
    keep = y.notna()
    if exclude_territories:
        keep &= df["_STATE"].le(56)
    return keep, y
