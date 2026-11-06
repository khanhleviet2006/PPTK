import numpy as np
import pandas as pd
import yaml
from sklearn.base import BaseEstimator, TransformerMixin


def specifications(path="configs/variables.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)["variables"]


def transform_raw(df, specs):
    out = pd.DataFrame(index=df.index)
    for name, spec in specs.items():
        if name not in df:
            raise ValueError(
                f"Required predictor {name} missing; do not silently alter the feature set"
            )
        x = pd.to_numeric(df[name], errors="coerce").replace(spec.get("zero_codes", []), 0)
        if "valid" in spec:
            x = x.where(x.isin(spec["valid"]))
        else:
            lo, hi = spec["range"]
            x = x.where(x.between(lo, hi)) * spec.get("scale", 1)
        out[name] = x
    return out


class DomainFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        x = X.copy()
        x["BMI_sq"] = x["_BMI5"] ** 2
        x["BMI_age"] = x["_BMI5"] * x["_AGEG5YR"]
        x["health_days"] = x["PHYSHLTH"] + x["MENTHLTH"]
        return x


class RankingSelector(BaseEstimator, TransformerMixin):
    """All rankings are learned inside training folds; permutation has an inner split."""

    def __init__(self, method="original", k=10, seed=2015):
        self.method, self.k, self.seed = method, k, seed

    def fit(self, X, y):
        from sklearn.feature_selection import mutual_info_classif, RFE
        from sklearn.ensemble import ExtraTreesClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.inspection import permutation_importance
        from sklearn.model_selection import train_test_split

        n = X.shape[1]
        k = min(self.k, n)
        if self.method == "original":
            self.indices_ = np.arange(n)
            return self
        if self.method == "mutual_info":
            scores = mutual_info_classif(X, y, random_state=self.seed)
        elif self.method == "l1":
            m = LogisticRegression(
                penalty="l1", solver="liblinear", max_iter=1000, random_state=self.seed
            ).fit(X, y)
            scores = np.abs(m.coef_).max(axis=0)
        elif self.method == "rfe":
            m = RFE(LogisticRegression(max_iter=1000), n_features_to_select=k, step=0.2).fit(X, y)
            scores = -m.ranking_
        elif self.method in ["tree", "permutation"]:
            m = ExtraTreesClassifier(
                n_estimators=60, min_samples_leaf=5, random_state=self.seed, n_jobs=1
            )
            if self.method == "permutation":
                a, b, c, d = train_test_split(
                    X, y, test_size=0.25, stratify=y, random_state=self.seed
                )
                m.fit(a, c)
                scores = permutation_importance(
                    m, b, d, scoring="balanced_accuracy", n_repeats=2, random_state=self.seed
                ).importances_mean
            else:
                scores = m.fit(X, y).feature_importances_
        else:
            raise ValueError(self.method)
        self.indices_ = np.sort(np.argsort(-scores, kind="stable")[:k])
        return self

    def transform(self, X):
        return np.asarray(X)[:, self.indices_]

    def get_support(self, indices=False):
        if indices:
            return self.indices_
        raise ValueError("Request indices=True")
