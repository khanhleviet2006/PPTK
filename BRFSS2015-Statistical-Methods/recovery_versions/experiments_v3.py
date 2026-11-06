import time
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline as SKPipeline
from sklearn.feature_selection import SelectKBest, f_classif, RFECV
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
    StackingClassifier,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
    RandomizedSearchCV,
)
from sklearn.metrics import (
    confusion_matrix,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import RandomOverSampler, ADASYN, SMOTE
from imblearn.under_sampling import RandomUnderSampler
from src.features.engineering import RankingSelector
from src.modeling.models import model, build_pipeline, ensemble
from src.evaluation.metrics import metrics
from src.utils.io import write_json, write_csv, read_json, canonical_hash, digest


class Selector(BaseEstimator, TransformerMixin):
    def __init__(self, method="original", k=10, seed=20261106):
        self.method, self.k, self.seed = method, k, seed

    def fit(self, X, y):
        n = X.shape[1]
        k = min(self.k, n)
        self.indices_ = np.arange(n)
        if self.method == "pca":
            self.reducer_ = PCA(n_components=k, random_state=self.seed).fit(X)
        elif self.method == "selectkbest":
            self.indices_ = SelectKBest(f_classif, k=k).fit(X, y).get_support(indices=True)
        elif self.method == "rfecv":
            r = RFECV(
                LogisticRegression(max_iter=500),
                step=0.25,
                min_features_to_select=5,
                cv=StratifiedKFold(2, shuffle=True, random_state=self.seed),
                scoring="balanced_accuracy",
                n_jobs=1,
            ).fit(X, y)
            self.indices_ = np.flatnonzero(r.support_)
        elif self.method in ["rf", "xgb", "shap"]:
            est = (
                RandomForestClassifier(
                    n_estimators=40, min_samples_leaf=5, n_jobs=1, random_state=self.seed
                )
                if self.method == "rf"
                else model("xgboost", self.seed)
                if self.method == "xgb"
                else ExtraTreesClassifier(
                    n_estimators=40, min_samples_leaf=5, random_state=self.seed, n_jobs=1
                )
            )
            est.fit(X, y)
            if self.method == "shap":
                import shap

                values = np.asarray(shap.TreeExplainer(est).shap_values(np.asarray(X)[:64]))
                scores = np.abs(values).mean(axis=0)
                if scores.ndim > 1:
                    scores = scores.mean(axis=-1)
            else:
                scores = est.feature_importances_
            self.indices_ = np.sort(np.argsort(-scores, kind="stable")[:k])
        elif self.method != "original":
            self.indices_ = RankingSelector(self.method, k, self.seed).fit(X, y).indices_
        return self

    def transform(self, X):
        return (
            self.reducer_.transform(X) if self.method == "pca" else np.asarray(X)[:, self.indices_]
        )


def preprocessing(columns, specs, missing="median"):
    cats = [c for c in columns if specs[c]["kind"] == "categorical"]
    nums = [c for c in columns if c not in cats]
    impute = (
        IterativeImputer(max_iter=5, random_state=20261106, skip_complete=True)
        if missing == "iterative"
        else SimpleImputer(
            strategy="median", add_indicator=missing == "indicators", keep_empty_features=True
        )
    )
    num = SKPipeline([("impute", impute), ("scale", StandardScaler())])
    cat = SKPipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer([("numeric", num, nums), ("categorical", cat, cats)])


def make(X, specs, exp, seed):
    name = exp["model"]
    method = exp.get("selector", "original")
    sampling = exp.get("sampling", "none")
    if exp.get("representation") == "continuous":
        cols = [c for c in X if specs[c]["kind"] == "continuous"]
    else:
        cols = list(X)
    if method in ["rfecv", "permutation"]:
        # Expansion uses only codebook categories; inner validation fits its own preprocessing.
        return Pipeline(
            [
                ("pre", FixedCodebookEncoder({c: specs[c] for c in cols})),
                ("select", InnerSafeSelector(method, exp.get("k", 10), seed)),
                (
                    "post",
                    SKPipeline(
                        [
                            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
                            ("scale", StandardScaler()),
                        ]
                    ),
                ),
                ("model", model(name, seed)),
            ]
        )
    if name in ["soft_voting", "stacking", "feature_ensemble"]:
        return ensemble(cols, specs, name, seed)
    if name in ["hard_voting", "weighted_voting", "family_ensemble"]:
        names = (
            ["logistic", "random_forest", "extra_trees"]
            if name == "family_ensemble"
            else ["logistic", "extra_trees", "gradient_boosting"]
        )
        bases = [(n, build_pipeline(cols, specs, n, seed=seed)) for n in names]
        return VotingClassifier(
            bases,
            voting="hard" if name == "hard_voting" else "soft",
            weights=[2, 1, 1] if name == "weighted_voting" else None,
            n_jobs=1,
        )
    if name.startswith("adasyn_"):
        base = name.removeprefix("adasyn_")
        if base in ["soft_voting", "stacking"]:
            bases = [
                (
                    n,
                    make(
                        X,
                        specs,
                        dict(model=n, sampling="adasyn", representation="continuous"),
                        seed,
                    ),
                )
                for n in ["random_forest", "xgboost", "lightgbm"]
            ]
            return (
                VotingClassifier(bases, voting="soft")
                if base == "soft_voting"
                else StackingClassifier(
                    bases, final_estimator=LogisticRegression(max_iter=500), cv=2, n_jobs=1
                )
            )
        return make(
            X, specs, dict(model=base, sampling="adasyn", representation="continuous"), seed
        )
    if sampling == "smotenc":
        return build_pipeline(cols, specs, name, imbalance="smote", seed=seed)
    if name == "knn":
        est = KNeighborsClassifier(n_neighbors=3)
    elif name == "naive_bayes":
        est = GaussianNB()
    elif name == "gb":
        est = GradientBoostingClassifier(n_estimators=40, max_depth=2, random_state=seed)
    else:
        est = model(name, seed, weighted=exp.get("weighted", False))
    steps = [("pre", preprocessing(cols, specs, exp.get("missing", "median")))]
    samplers = {
        "random_over": RandomOverSampler(random_state=seed),
        "random_under": RandomUnderSampler(random_state=seed),
        "smote": SMOTE(k_neighbors=3, random_state=seed),
        "adasyn": ADASYN(n_neighbors=3, random_state=seed),
    }
    if sampling in ["adasyn", "smote"] and exp.get("representation") != "continuous":
        raise ValueError("Vanilla synthetic sampling requires continuous-only representation")
    if sampling in samplers:
        steps.append(("sample", samplers[sampling]))
    steps += [("select", Selector(method, exp.get("k", 10), seed)), ("model", est)]
    pipe = Pipeline(steps)
    if exp.get("calibration") in ["sigmoid", "isotonic"]:
        return CalibratedClassifierCV(pipe, method=exp["calibration"], cv=2, n_jobs=1)
    if exp.get("search"):
        params = (
            {"model__C": [0.1, 1, 10]} if name == "logistic" else {"model__max_depth": [3, 6, 10]}
        )
        if name == "lightgbm":
            params = {"model__num_leaves": [7, 15, 31]}
        if name == "catboost":
            params = {"model__depth": [3, 4, 6]}
        return RandomizedSearchCV(
            pipe,
            params,
            n_iter=2,
            cv=2,
            scoring="balanced_accuracy",
            random_state=seed,
            n_jobs=1,
            refit=True,
        )
    return pipe


def probability(m, X, k):
    if hasattr(m, "predict_proba"):
        try:
            p = m.predict_proba(X)
        except AttributeError:
            p = np.eye(k)[m.predict(X).astype(int)]
    else:
        p = np.eye(k)[m.predict(X).astype(int)]
    return np.asarray(p, float)


def policy_metrics(y, p, pred):
    r = metrics(y, p)
    k = p.shape[1]
    cm = confusion_matrix(y, pred, labels=np.arange(k))
    avg = "binary" if k == 2 else "macro"
    r.update(
        accuracy=float(np.mean(np.asarray(y) == pred)),
        balanced_accuracy=balanced_accuracy_score(y, pred),
        precision=precision_score(y, pred, average=avg, zero_division=0),
        sensitivity=recall_score(y, pred, average=avg, zero_division=0),
        f1=f1_score(y, pred, average=avg, zero_division=0),
        macro_f1=f1_score(y, pred, average="macro", zero_division=0),
        confusion_matrix=cm.tolist(),
    )
    specs = []
    for c in range(k):
        tp = cm[c, c]
        fn = cm[c].sum() - tp
        fp = cm[:, c].sum() - tp
        tn = cm.sum() - tp - fn - fp
        r[f"class_{c}_sensitivity"] = tp / (tp + fn) if tp + fn else float("nan")
        r[f"class_{c}_specificity"] = tn / (tn + fp) if tn + fp else float("nan")
        specs.append(r[f"class_{c}_specificity"])
    r["specificity"] = specs[1] if k == 2 else float(np.mean(specs))
    return r


def plan(mode="binary"):
    bases = [
        "logistic",
        "decision_tree",
        "random_forest",
        "extra_trees",
        "knn",
        "naive_bayes",
        "gb",
        "gradient_boosting",
        "xgboost",
        "lightgbm",
        "catboost",
    ]
    exps = [dict(model=n, stage="screen") for n in bases]
    if mode != "binary":
        return exps[:4]
    for method in [
        "pca",
        "mutual_info",
        "selectkbest",
        "l1",
        "rfe",
        "rf",
        "xgb",
        "permutation",
        "shap",
    ]:
        for k in [5, 10, 15, 20]:
            exps.append(dict(model="logistic", selector=method, k=k, stage="features"))
    exps.append(dict(model="logistic", selector="rfecv", stage="features"))
    for s in ["random_under", "random_over", "smotenc"]:
        exps.append(dict(model="logistic", sampling=s, stage="imbalance"))
    exps.append(dict(model="logistic", weighted=True, stage="imbalance"))
    for s in ["none", "smote", "adasyn"]:
        for n in ["random_forest", "xgboost", "lightgbm"]:
            exps.append(dict(model=n, sampling=s, representation="continuous", stage="imbalance"))
    for n in [
        "adasyn_soft_voting",
        "adasyn_stacking",
        "soft_voting",
        "hard_voting",
        "weighted_voting",
        "stacking",
        "feature_ensemble",
        "family_ensemble",
    ]:
        exps.append(dict(model=n, stage="ensemble"))
    for missing in ["indicators", "iterative"]:
        exps.append(dict(model="logistic", missing=missing, stage="missing"))
    for n in ["logistic", "random_forest", "xgboost", "lightgbm", "catboost"]:
        exps.append(dict(model=n, search=True, stage="search"))
    for cal in ["sigmoid", "isotonic"]:
        exps.append(dict(model="logistic", calibration=cal, stage="calibration"))
    return exps


def evaluate(X, y, specs, out, exp, cv, seed):
    eid = canonical_hash(exp)[:16]
    meta = out / "experiments" / f"{eid}.json"
    if meta.exists():
        record = read_json(meta)
        if (
            record.get("status") == "SUCCESS"
            and digest(out / record["oof_file"]) == record["oof_sha256"]
        ):
            return record
    start = time.time()
    y = np.asarray(y, int)
    k = len(np.unique(y))
    p = np.zeros((len(y), k))
    pred = np.zeros(len(y), int)
    fold_records = []
    features = []
    thresholds = []
    for f, (train, val) in enumerate(cv):
        m = make(X, specs, exp, seed + f)
        # Threshold choice is inside outer training: no outer-validation labels used.
        t = 0.5
        if k == 2 and exp["model"] != "hard_voting":
            inner = StratifiedKFold(2, shuffle=True, random_state=seed + f)
            probs = cross_val_predict(
                clone(m), X.iloc[train], y[train], cv=inner, method="predict_proba", n_jobs=1
            )[:, 1]
            grid = np.arange(0.1, 0.91, 0.1)
            t = float(
                max(
                    grid,
                    key=lambda v: (balanced_accuracy_score(y[train], probs >= v), -abs(v - 0.5)),
                )
            )
        m.fit(X.iloc[train], y[train])
        p[val] = probability(m, X.iloc[val], k)
        pred[val] = (p[val, 1] >= t).astype(int) if k == 2 else p[val].argmax(axis=1)
        thresholds.append(t)
        fold_records.append(policy_metrics(y[val], p[val], pred[val]))
        inner_m = m.best_estimator_ if hasattr(m, "best_estimator_") else m
        if hasattr(inner_m, "named_steps") and "select" in inner_m.named_steps:
            sel = inner_m.named_steps["select"]
            if sel.method != "pca":
                try:
                    names = inner_m.named_steps["pre"].get_feature_names_out()
                    if "encode" in inner_m.named_steps:
                        names = inner_m.named_steps["encode"].get_feature_names_out(names)
                    features.append(names[sel.indices_].tolist())
                except (ValueError, AttributeError):
                    features.append([str(i) for i in sel.indices_])
    data = pd.DataFrame({"y": y, "pred": pred})
    for c in range(k):
        data[f"p{c}"] = p[:, c]
    rel = f"experiments/{eid}.csv"
    write_csv(out / rel, data)
    record = {
        "experiment_id": eid,
        "config": exp,
        "status": "SUCCESS",
        "scope": "EXPLORATORY_OUTER_CV_NOT_FINAL_TEST",
        "n": len(y),
        "metrics": policy_metrics(y, p, pred),
        "fold_metrics": fold_records,
        "thresholds_inner_training": thresholds,
        "selected_features_by_fold": features,
        "seconds": time.time() - start,
        "oof_file": rel,
        "oof_sha256": digest(out / rel),
    }
    if len(features) == 2:
        a, b = map(set, features)
        record["feature_jaccard"] = len(a & b) / len(a | b) if a | b else 1
    write_json(meta, record)
    return record


class FixedCodebookEncoder(BaseEstimator, TransformerMixin):
    """Data-independent expansion so inner selector CV can fit its own imputer/scaler."""

    def __init__(self, specs):
        self.specs = specs

    def fit(self, X, y=None):
        self.names_ = []
        for c in X:
            if self.specs[c]["kind"] == "categorical":
                self.names_ += [f"{c}={v}" for v in self.specs[c]["valid"]]
            else:
                self.names_.append(c)
        return self

    def transform(self, X):
        parts = []
        for c in X:
            v = X[c].to_numpy(float)
            if self.specs[c]["kind"] == "categorical":
                a = np.column_stack(
                    [(v == level).astype(float) for level in self.specs[c]["valid"]]
                )
                a[np.isnan(v), :] = np.nan
                parts.append(a)
            else:
                parts.append(v[:, None])
        return np.column_stack(parts)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.names_, object)


class InnerSafeSelector(BaseEstimator, TransformerMixin):
    def __init__(self, method="rfecv", k=10, seed=20261106):
        self.method, self.k, self.seed = method, k, seed

    def fit(self, X, y):
        from sklearn.model_selection import train_test_split
        from sklearn.inspection import permutation_importance

        prep = [
            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scale", StandardScaler()),
        ]
        if self.method == "rfecv":
            est = SKPipeline(prep + [("lr", LogisticRegression(max_iter=500))])
            sel = RFECV(
                est,
                step=0.25,
                min_features_to_select=5,
                cv=StratifiedKFold(2, shuffle=True, random_state=self.seed),
                scoring="balanced_accuracy",
                importance_getter="named_steps.lr.coef_",
                n_jobs=1,
            ).fit(X, y)
            self.indices_ = np.flatnonzero(sel.support_)
        else:
            a, b = train_test_split(
                np.arange(len(y)), test_size=0.25, stratify=y, random_state=self.seed
            )
            est = SKPipeline(
                prep
                + [
                    (
                        "tree",
                        ExtraTreesClassifier(
                            n_estimators=40, min_samples_leaf=5, random_state=self.seed, n_jobs=1
                        ),
                    )
                ]
            ).fit(X[a], np.asarray(y)[a])
            scores = permutation_importance(
                est,
                X[b],
                np.asarray(y)[b],
                scoring="balanced_accuracy",
                n_repeats=2,
                random_state=self.seed,
            ).importances_mean
            self.indices_ = np.sort(np.argsort(-scores, kind="stable")[: min(self.k, X.shape[1])])
        return self

    def transform(self, X):
        return np.asarray(X)[:, self.indices_]
