"""Development-only robustness, tuning and simulated federation diagnostics."""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.model_selection import (
    train_test_split,
    StratifiedGroupKFold,
    RepeatedStratifiedKFold,
    cross_val_score,
)
from src.features.engineering import specifications
from src.utils.io import write_json, write_csv, read_json, digest
from src_extensions.experiments import make, evaluate, preprocessing
from src.evaluation.metrics import metrics


def run(out):
    out = Path(out)
    d = pd.read_csv(out / "development_features.csv")
    y = d.pop("outcome").to_numpy(int)
    X = d
    specs = specifications()
    seed = 20261106
    import optuna

    def objective(trial):
        m = make(X, specs, {"model": "logistic"}, seed)
        m.set_params(model__C=trial.suggest_float("C", 0.01, 10, log=True))
        return cross_val_score(m, X, y, cv=2, scoring="balanced_accuracy", n_jobs=1).mean()

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=2)
    write_csv(out / "optuna_trials.csv", study.trials_dataframe())
    write_json(
        out / "optuna_manifest.json",
        {
            "budget": 2,
            "scope": "development-only diagnostic",
            "source_manifest_sha256": digest(out / "manifest.json"),
            "objective": "2-fold BA at default threshold .5; no independent HPO performance claim",
        },
    )
    ids = read_json(out / "development_ids.json")["ids"]
    groups = [s.split(":")[0] for s in ids]
    if len(set(groups)) >= 4:
        cv = list(StratifiedGroupKFold(2, shuffle=True, random_state=seed).split(X, y, groups))
        for a, b in cv:
            assert not set(np.asarray(groups)[a]) & set(np.asarray(groups)[b])
        dest = out / "group_cv"
        dest.mkdir(exist_ok=True)
        evaluate(X, y, specs, dest, dict(model="logistic", stage="held_out_state"), cv, seed)
        write_json(
            dest / "splits.json", [dict(train=a.tolist(), validation=b.tolist()) for a, b in cv]
        )
    rk = list(RepeatedStratifiedKFold(n_splits=2, n_repeats=2, random_state=seed).split(X, y))
    for i in range(2):
        dest = out / f"repeated_cv_{i}"
        dest.mkdir(exist_ok=True)
        evaluate(
            X,
            y,
            specs,
            dest,
            dict(model="logistic", stage="repeated_stratified_cv"),
            rk[2 * i : 2 * i + 2],
            seed + i,
        )
    # Public-data optimization simulation: no multi-institutional/private-data claim.
    a, b = train_test_split(np.arange(len(y)), test_size=0.25, stratify=y, random_state=seed)
    pre = preprocessing(list(X), specs)
    z = pre.fit_transform(X.iloc[a])
    v = pre.transform(X.iloc[b])
    z = np.c_[np.ones(len(z)), z]
    v = np.c_[np.ones(len(v)), v]
    clients = np.array_split(np.random.default_rng(seed).permutation(len(a)), 4)
    w = np.zeros(z.shape[1])
    central = w.copy()
    history = []
    for epoch in range(20):
        local = []
        for ix in clients:
            q = w.copy()
            for _ in range(3):
                q -= 0.05 * (z[ix].T @ (expit(z[ix] @ q) - y[a][ix]) / len(ix))
            local.append(q)
        w = np.average(local, axis=0, weights=[len(ix) for ix in clients])
        for _ in range(3):
            central -= 0.05 * (z.T @ (expit(z @ central) - y[a]) / len(a))
        history.append(
            {"round": epoch + 1, "coefficient_distance": float(np.linalg.norm(w - central))}
        )
    p = expit(v @ w)
    q = expit(v @ central)
    write_json(
        out / "federated_simulation.json",
        {
            "scope": "SIMULATED_PUBLIC_DATA_CLIENTS_CENTRAL_PREPROCESSOR_NO_PRIVACY_GUARANTEE",
            "clients": 4,
            "rounds": 20,
            "validation_n": len(b),
            "fedavg": metrics(y[b], np.c_[1 - p, p]),
            "central": metrics(y[b], np.c_[1 - q, q]),
            "history": history,
        },
    )
