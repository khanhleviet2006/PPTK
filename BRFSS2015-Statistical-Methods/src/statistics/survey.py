"""With-replacement ultimate-cluster Taylor linearization, stratified PSUs.

No finite population correction. Domains contribute zero influence outside domain.
Weights are fixed calibrated survey weights; calibration variance gains are not modeled.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import expit, softmax
from scipy.optimize import minimize
from src.data.ingest import ScientificValidationError


class Design:
    def __init__(self, frame):
        self.frame = frame.reset_index(drop=True)
        self.w = self.frame["_LLCPWT"].to_numpy(float)
        if not np.isfinite(self.w).all() or np.any(self.w <= 0):
            raise ScientificValidationError("Invalid design weights")
        pairs = pd.MultiIndex.from_frame(self.frame[["_STSTR", "_PSU"]])
        self.cluster_codes, cluster_keys = pd.factorize(pairs, sort=True)
        self.stratum_codes, strata = pd.factorize(cluster_keys.get_level_values(0), sort=True)
        self.nclusters = len(cluster_keys)
        self.nstrata = len(strata)
        self.counts = np.bincount(self.stratum_codes)
        if np.any(self.counts < 2):
            raise ScientificValidationError("Singleton stratum; variance policy is fail-closed")
        self.df = int(np.sum(self.counts - 1))

    def meat(self, influence):
        u = np.asarray(influence)
        if u.ndim == 1:
            u = u[:, None]
        if len(u) != len(self.w):
            raise ValueError("Influence must include full design with zero values outside domain")
        totals = np.column_stack(
            [
                np.bincount(self.cluster_codes, weights=u[:, j], minlength=self.nclusters)
                for j in range(u.shape[1])
            ]
        )
        stratum_totals = np.column_stack(
            [
                np.bincount(self.stratum_codes, weights=totals[:, j], minlength=self.nstrata)
                for j in range(u.shape[1])
            ]
        )
        centered = (
            totals - stratum_totals[self.stratum_codes] / self.counts[self.stratum_codes, None]
        )
        centered *= np.sqrt((self.counts / (self.counts - 1))[self.stratum_codes])[:, None]
        return centered.T @ centered

    def mean(self, values, domain=None, proportion=False):
        x = np.asarray(values, dtype=float)
        keep = np.isfinite(x)
        if domain is not None:
            keep &= np.asarray(domain, bool)
        if keep.sum() == 0:
            return dict(estimate=np.nan, se=np.nan, lower=np.nan, upper=np.nan, n=0, df=self.df)
        denom = self.w[keep].sum()
        est = np.dot(self.w[keep], x[keep]) / denom
        influence = np.zeros(len(x))
        influence[keep] = self.w[keep] * (x[keep] - est) / denom
        se = np.sqrt(max(self.meat(influence)[0, 0], 0))
        t = stats.t.ppf(0.975, self.df)
        if proportion and 0 < est < 1:
            a = stats.logistic.cdf(
                stats.logistic.ppf(est) + np.array([-1, 1]) * t * se / (est * (1 - est))
            )
        else:
            a = est + np.array([-1, 1]) * t * se
            if proportion:
                a = np.clip(a, 0, 1)
        return dict(estimate=est, se=se, lower=a[0], upper=a[1], n=int(keep.sum()), df=self.df)


def wald(beta, covariance, df):
    beta = np.asarray(beta)
    rank = np.linalg.matrix_rank(covariance)
    if rank == 0:
        return {"F": np.nan, "df_num": 0, "df_den": df, "p": np.nan}
    f = float(beta @ np.linalg.pinv(covariance) @ beta / rank)
    return {"F": f, "df_num": rank, "df_den": df, "p": stats.f.sf(f, rank, df)}


def logistic(design, X, y, domain=None):
    import statsmodels.api as sm

    X, y = np.asarray(X, float), np.asarray(y, float)
    keep = np.isfinite(y) & np.isfinite(X).all(axis=1)
    if domain is not None:
        keep &= np.asarray(domain, bool)
    if len(np.unique(y[keep])) != 2:
        raise ScientificValidationError("Logistic regression requires two observed outcome classes")
    x, z = X[keep], y[keep]
    if np.linalg.matrix_rank(x) < x.shape[1]:
        raise ScientificValidationError("Rank-deficient inference model")
    w = design.w[keep] / design.w[keep].mean()
    model = sm.GLM(z, x, family=sm.families.Binomial(), freq_weights=w).fit(maxiter=100)
    if not model.converged:
        raise ScientificValidationError("GLM did not converge")
    b = np.asarray(model.params)
    p = expit(x @ b)
    bread = np.linalg.inv(x.T @ ((w * p * (1 - p))[:, None] * x))
    scores = np.zeros_like(X)
    scores[keep] = x * (w * (z - p))[:, None]
    cov = bread @ design.meat(scores) @ bread
    # Conservative residual survey df, matching degf(design)-rank+1 convention.
    df = design.df - X.shape[1] + 1
    if df <= 0:
        raise ScientificValidationError("Insufficient design degrees of freedom")
    return (
        b,
        cov,
        df,
        {
            "n": int(keep.sum()),
            "converged": model.converged,
            "condition_number": float(np.linalg.cond(x)),
            "max_abs_coefficient": float(np.abs(b).max()),
        },
    )


def multinomial(design, X, y, domain=None):
    """Baseline category 0, pseudo-MLE with design-based cluster score covariance."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    keep = np.isfinite(y) & np.isfinite(X).all(axis=1)
    if domain is not None:
        keep &= np.asarray(domain, bool)
    x, z = X[keep], y[keep].astype(int)
    classes = np.unique(z)
    if not np.array_equal(classes, np.arange(len(classes))) or len(classes) < 3:
        raise ScientificValidationError("Multinomial outcome must have contiguous 0..K-1 classes")
    k, q = len(classes) - 1, x.shape[1]
    if np.linalg.matrix_rank(x) < q:
        raise ScientificValidationError("Rank-deficient multinomial design")
    w = design.w[keep] / design.w[keep].mean()
    Y = np.eye(k + 1)[z][:, 1:]

    def objective(b):
        logits = np.column_stack([np.zeros(len(x)), x @ b.reshape(k, q).T])
        p = softmax(logits, axis=1)
        loss = -np.sum(w * np.log(np.maximum(p[np.arange(len(z)), z], 1e-300)))
        g = ((p[:, 1:] - Y) * w[:, None]).T @ x
        return loss, g.ravel()

    fit = minimize(
        objective, np.zeros(k * q), jac=True, method="BFGS", options={"gtol": 1e-6, "maxiter": 500}
    )
    grad = np.linalg.norm(fit.jac, ord=np.inf) / len(z)
    if not fit.success and grad > 1e-6:
        raise ScientificValidationError(f"Multinomial convergence failure: {fit.message}")
    p = softmax(np.column_stack([np.zeros(len(x)), x @ fit.x.reshape(k, q).T]), axis=1)[:, 1:]
    h = np.zeros((k * q, k * q))
    for a in range(k):
        for b in range(k):
            h[a * q : (a + 1) * q, b * q : (b + 1) * q] = x.T @ (
                (w * p[:, a] * ((a == b) - p[:, b]))[:, None] * x
            )
    scores = np.zeros((len(X), k * q))
    scores[keep] = ((Y - p)[:, :, None] * x[:, None, :] * w[:, None, None]).reshape(len(x), -1)
    bread = np.linalg.inv(h)
    cov = bread @ design.meat(scores) @ bread
    df = design.df - k * q + 1
    if df <= 0:
        raise ScientificValidationError("Insufficient multinomial design degrees of freedom")
    return fit.x, cov, df, {"n": int(keep.sum()), "gradient_per_record": grad, "reference_class": 0}


def coefficient_table(beta, cov, df, names, effect="OR"):
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    t = stats.t.ppf(0.975, df)
    return pd.DataFrame(
        {
            "term": names,
            "beta": beta,
            "se_design": se,
            effect: np.exp(beta),
            "lower": np.exp(beta - t * se),
            "upper": np.exp(beta + t * se),
            "p": 2
            * stats.t.sf(
                np.abs(np.divide(beta, se, out=np.full_like(beta, np.nan), where=se > 0)), df
            ),
            "df": df,
        }
    )
