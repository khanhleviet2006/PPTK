import importlib.util
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline as SKPipeline
from imblearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    VotingClassifier,
    StackingClassifier,
)
from imblearn.over_sampling import SMOTENC, SMOTE, BorderlineSMOTE
from imblearn.under_sampling import RandomUnderSampler
from src.features.engineering import RankingSelector, DomainFeatures

OPTIONAL = {"xgboost": "xgboost", "lightgbm": "lightgbm", "catboost": "catboost"}


def model(name, seed=2015, weighted=False, budget=1):
    cw = "balanced" if weighted else None
    if name == "logistic":
        return LogisticRegression(C=budget, max_iter=1000, class_weight=cw, random_state=seed)
    if name == "decision_tree":
        return DecisionTreeClassifier(
            max_depth=6 if budget == 1 else 10,
            min_samples_leaf=10,
            class_weight=cw,
            random_state=seed,
        )
    if name in ["random_forest", "extra_trees"]:
        cls = RandomForestClassifier if name == "random_forest" else ExtraTreesClassifier
        return cls(
            n_estimators=80 if budget == 1 else 160,
            min_samples_leaf=5,
            max_features="sqrt",
            class_weight=cw,
            random_state=seed,
            n_jobs=1,
        )
    if name == "gradient_boosting":
        return HistGradientBoostingClassifier(
            max_iter=80, max_leaf_nodes=15, class_weight=cw, random_state=seed
        )
    if name == "xgboost":
        from xgboost import XGBClassifier

        if weighted:
            raise ValueError(
                "Use explicit sampler for boosters without automatic multiclass weights"
            )
        return XGBClassifier(
            n_estimators=80,
            max_depth=3,
            learning_rate=0.07,
            tree_method="hist",
            n_jobs=1,
            random_state=seed,
        )
    if name == "lightgbm":
        from lightgbm import LGBMClassifier

        return LGBMClassifier(
            n_estimators=80,
            num_leaves=15,
            learning_rate=0.07,
            verbosity=-1,
            n_jobs=1,
            class_weight=cw,
            random_state=seed,
        )
    if name == "catboost":
        from catboost import CatBoostClassifier

        return CatBoostClassifier(
            iterations=80,
            depth=4,
            learning_rate=0.07,
            verbose=False,
            allow_writing_files=False,
            thread_count=1,
            random_seed=seed,
            auto_class_weights="Balanced" if weighted else None,
        )
    raise ValueError(name)


def preprocess(columns, specs, ordinal=False):
    cats = [c for c in columns if specs.get(c, {}).get("kind") == "categorical"]
    nums = [c for c in columns if c not in cats]
    numeric = SKPipeline(
        [
            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scale", StandardScaler()),
        ]
    )
    categorical = SKPipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    if ordinal:
        # SMOTENC works on imputed categorical codes, before one-hot encoding.
        categorical = SimpleImputer(strategy="most_frequent", keep_empty_features=True)
    return (
        ColumnTransformer([("num", numeric, nums), ("cat", categorical, cats)], remainder="drop"),
        len(nums),
        len(cats),
    )


def build_pipeline(
    columns,
    specs,
    name="logistic",
    selector="original",
    k=10,
    imbalance="none",
    seed=2015,
    budget=1,
):
    columns = list(columns)
    steps = []
    if selector == "clinical":
        columns = [
            c
            for c in columns
            if specs[c]["group"] in ["demographic", "biomedical", "socioeconomic", "lifestyle"]
        ]
        selector = "original"
    if selector == "interactions":
        steps.append(("domain", DomainFeatures()))
        columns += ["BMI_sq", "BMI_age", "health_days"]
        selector = "original"
    if imbalance in ["smote", "borderline_smote"]:
        pre, nnum, ncat = preprocess(columns, specs, ordinal=True)
        steps.append(("pre", pre))
        if imbalance == "borderline_smote" and ncat:
            raise ValueError("BorderlineSMOTE invalid for mixed categorical data; use SMOTENC")
        sampler = (
            SMOTENC(
                categorical_features=list(range(nnum, nnum + ncat)),
                random_state=seed,
                k_neighbors=3,
            )
            if ncat
            else (
                BorderlineSMOTE(random_state=seed, k_neighbors=3)
                if imbalance == "borderline_smote"
                else SMOTE(random_state=seed, k_neighbors=3)
            )
        )
        steps.append(("resample", sampler))
        # Sampler returns numeric then categorical; scale already fit on original training rows.
        encoder = ColumnTransformer(
            [
                ("numeric", "passthrough", list(range(nnum))),
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    list(range(nnum, nnum + ncat)),
                ),
            ]
        )
        steps.append(("encode", encoder))
    else:
        pre, _, _ = preprocess(columns, specs)
        steps.append(("pre", pre))
        if imbalance == "random_under":
            steps.append(("resample", RandomUnderSampler(random_state=seed)))
    steps.append(("select", RankingSelector(selector, k, seed)))
    steps.append(("model", model(name, seed, imbalance == "class_weight", budget)))
    return Pipeline(steps)


def ensemble(columns, specs, name, seed):
    if name == "feature_ensemble":
        estimators = [
            ("clinical", build_pipeline(columns, specs, "logistic", "clinical", seed=seed)),
            ("mi", build_pipeline(columns, specs, "extra_trees", "mutual_info", 10, seed=seed)),
            ("all", build_pipeline(columns, specs, "gradient_boosting", seed=seed)),
        ]
    else:
        estimators = [
            (n, build_pipeline(columns, specs, n, seed=seed))
            for n in ["logistic", "extra_trees", "gradient_boosting"]
        ]
    if name == "stacking":
        # Complete pipelines inside inner CV prevent preprocessing leakage into meta-features.
        return StackingClassifier(
            estimators=estimators, final_estimator=LogisticRegression(max_iter=1000), cv=3, n_jobs=1
        )
    return VotingClassifier(estimators=estimators, voting="soft", n_jobs=1)


def available(name):
    return name not in OPTIONAL or importlib.util.find_spec(OPTIONAL[name]) is not None
