import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from src.utils.io import write_json, read_json, canonical_hash
from src.data.ingest import ScientificValidationError


def create_split(ids, y, seed=2015, test_fraction=0.2):
    ids = np.asarray(ids).astype(str)
    y = np.asarray(y)
    if len(set(ids)) != len(ids):
        raise ScientificValidationError("Respondent IDs must be unique before splitting")
    a, b = train_test_split(
        np.arange(len(y)), stratify=y, test_size=test_fraction, random_state=seed
    )
    manifest = {
        "seed": seed,
        "train_ids": ids[a].tolist(),
        "test_ids": ids[b].tolist(),
        "cohort_ids_hash": canonical_hash(ids.tolist()),
        "test_ids_hash": canonical_hash(ids[b].tolist()),
    }
    return a, b, manifest


def save_split(path, manifest):
    if path.exists():
        old = read_json(path)
        if old != manifest:
            raise ScientificValidationError(
                "Existing split differs; create a separate run directory"
            )
    else:
        write_json(path, manifest)


def folds(y, n_splits, seed):
    _, counts = np.unique(y, return_counts=True)
    if len(counts) < 2 or counts.min() < n_splits:
        raise ScientificValidationError("Insufficient minority observations for requested folds")
    return list(
        StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed).split(
            np.zeros(len(y)), y
        )
    )
