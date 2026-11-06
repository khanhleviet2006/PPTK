import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
from src.statistics.survey import Design, logistic, multinomial, coefficient_table, wald


def model_matrix(X, specs, median_impute=False, imputation_domain=None):
    x = X.copy()
    if median_impute:
        # Explicitly a deterministic inference sensitivity, not proper multiple imputation.
        fit = x if imputation_domain is None else x.loc[np.asarray(imputation_domain, bool)]
        for c in x:
            if fit[c].notna().sum() == 0:
                raise ValueError(f"Cannot infer imputation value for entirely missing {c}")
            value = fit[c].median() if specs[c]["kind"] == "continuous" else fit[c].mode().iloc[0]
            x[c] = x[c].fillna(value)
    mats = [pd.DataFrame({"Intercept": np.ones(len(x))}, index=x.index)]
    for c in x:
        if specs[c]["kind"] == "categorical":
            categories = specs[c]["valid"]
            part = pd.get_dummies(
                pd.Categorical(x[c], categories=categories), prefix=c, drop_first=True, dtype=float
            )
            part.index = x.index
            part.loc[x[c].isna(), :] = np.nan
            # Exclude absent levels to avoid structural zero columns in small synthetic runs.
            part = part.loc[:, part.fillna(0).any()]
            mats.append(part)
        else:
            # Scaling aids numerics, explicitly reported in coefficient labels.
            scale = 10 if c in ["_BMI5", "PHYSHLTH", "MENTHLTH"] else 1
            mats.append(x[[c]].rename(columns={c: c + f"_per_{scale}"}) / scale)
    return pd.concat(mats, axis=1)


def table_one(frame, X, y, specs, domain):
    design = Design(frame)
    rows = []
    for group in ["all"] + sorted(y[domain].dropna().unique().tolist()):
        dom = np.asarray(domain) & (
            np.ones(len(y), bool) if group == "all" else y.eq(group).to_numpy()
        )
        for c in X:
            missing = design.mean(X[c].isna().astype(float), dom, proportion=True)
            levels = specs[c].get("valid", [None])
            for level in levels:
                v = X[c].to_numpy(float).copy()
                if level is not None:
                    v = np.where(np.isnan(v), np.nan, (v == level).astype(float))
                r = design.mean(v, dom, proportion=level is not None)
                rows.append(
                    {
                        "group": group,
                        "variable": c,
                        "level": level,
                        **r,
                        "missing_n": int(X.loc[dom, c].isna().sum()),
                        "missing_weighted": missing["estimate"],
                    }
                )
    return pd.DataFrame(rows)


def inference(frame, X, y, specs, domain, multiclass=False, impute=False):
    design = Design(frame)
    mat = model_matrix(X, specs, median_impute=impute, imputation_domain=domain)
    func = multinomial if multiclass else logistic
    b, cov, df, diag = func(design, mat, y, domain)
    names = list(mat)
    if multiclass:
        names = [f"class_{k}_vs_0:{t}" for k in range(1, int(y.max()) + 1) for t in names]
    tab = coefficient_table(b, cov, df, names, "RRR" if multiclass else "OR")
    tab["p_BH_exploratory"] = multipletests(tab.p.fillna(1), method="fdr_bh")[1]
    grouped = {}
    for c in X:
        ix = [
            i
            for i, term in enumerate(names)
            if (term.split(":")[-1].startswith(c + "_") or term.split(":")[-1] == c)
        ]
        if ix:
            grouped[c] = wald(b[ix], cov[np.ix_(ix, ix)], df)
    return tab, {
        **diag,
        "variance": "stratified PSU Taylor score linearization",
        "df": df,
        "imputation": "median/mode sensitivity" if impute else "complete case",
        "grouped_wald": grouped,
        "joint_wald": wald(
            b[[i for i, t in enumerate(names) if not t.endswith("Intercept")]],
            cov[
                np.ix_(
                    [i for i, t in enumerate(names) if not t.endswith("Intercept")],
                    [i for i, t in enumerate(names) if not t.endswith("Intercept")],
                )
            ],
            df,
        ),
    }


def univariate(frame, X, y, specs, domain):
    results = []
    for col in X:
        tab, diag = inference(frame, X[[col]], y, {col: specs[col]}, domain)
        tab["variable"] = col
        results.append(tab)
    return pd.concat(results, ignore_index=True)
