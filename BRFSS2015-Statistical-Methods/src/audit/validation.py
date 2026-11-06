import re
import numpy as np
import pandas as pd
from src.data.ingest import ScientificValidationError

DESIGN = ["_LLCPWT", "_STSTR", "_PSU"]


def validate_source(df, meta, specs, synthetic=False):
    required = DESIGN + ["DIABETE3", "_STATE", "SEQNO"] + list(specs)
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ScientificValidationError(f"Required columns absent: {missing}")
    if not synthetic and (len(df) != 441456 or len(meta["source_columns"]) != 330):
        raise ScientificValidationError(
            "Expected CDC 2015 release: 441456 records, 330 columns; investigate source."
        )
    if df[["_STATE", "SEQNO"]].isna().any().any() or df[["_STATE", "SEQNO"]].duplicated().any():
        raise ScientificValidationError(
            "Missing/duplicate state+SEQNO: respondent integrity cannot be established"
        )
    if df[DESIGN].isna().any().any() or (~np.isfinite(df[DESIGN])).any().any():
        raise ScientificValidationError("Survey design contains missing/nonfinite values")
    if df["_LLCPWT"].le(0).any():
        raise ScientificValidationError("Nonpositive sampling weights")
    if not df["DIABETE3"].dropna().isin([1, 2, 3, 4, 7, 9]).all():
        raise ScientificValidationError("Unknown DIABETE3 code")
    npsu = df.groupby("_STSTR")["_PSU"].nunique()
    if npsu.lt(2).any():
        raise ScientificValidationError(
            "Singleton strata: explicit defensible variance policy required"
        )
    return {
        **meta,
        "records": len(df),
        "columns_loaded": len(df.columns),
        "strata": len(npsu),
        "psus_nested": int(npsu.sum()),
        "design_df": int((npsu - 1).sum()),
        "duplicate_ids": 0,
        "duplicate_predictor_rows": int(df[list(specs)].duplicated().sum()),
        "outcome_counts": df.DIABETE3.value_counts(dropna=False).to_dict(),
        "synthetic": synthetic,
    }


def verify_codebook(path, names):
    from pypdf import PdfReader

    text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    absent = [
        v
        for v in names
        if re.search(r"(?<![A-Z0-9_])" + re.escape(v) + r"(?![A-Z0-9_])", text) is None
    ]
    if absent:
        raise ScientificValidationError(f"Codebook lacks required variable names: {absent}")
    if "2015" not in text or "DIABETE3" not in text:
        raise ScientificValidationError("Incorrect codebook")
    from src.utils.io import digest

    return {
        "sha256": digest(path),
        "variables_found": names,
        "status": "VARIABLE_NAMES_VERIFIED",
        "coding_review": "See docs/DATA_DICTIONARY.md; name search alone does not verify semantics",
    }


def missingness(X, y):
    rows = []
    for group in ["all"] + sorted(y.dropna().unique().tolist()):
        x = X if group == "all" else X.loc[y.eq(group)]
        for col in X:
            rows.append(
                {
                    "outcome": group,
                    "variable": col,
                    "n": len(x),
                    "missing": int(x[col].isna().sum()),
                    "fraction": x[col].isna().mean(),
                }
            )
    return pd.DataFrame(rows)
