import numpy as np
import pytest
from src.utils.io import Checkpoints, atomic_bytes, write_json
from src.modeling.splits import create_split, folds, save_split
from src.data.ingest import ScientificValidationError


def test_atomic_checkpoint(tmp_path):
    f = tmp_path / "value.json"
    write_json(f, {"x": 1})
    c = Checkpoints(tmp_path, "a")
    c.commit("stage", [f])
    assert c.valid("stage")
    atomic_bytes(f, b"changed")
    assert not c.valid("stage")
    assert not Checkpoints(tmp_path, "b").valid("stage")


def test_split_preservation(tmp_path):
    y = np.tile([0, 0, 0, 1], 100)
    ids = np.arange(len(y))
    a, b, m = create_split(ids, y)
    assert not set(a) & set(b)
    assert sorted(np.r_[a, b]) == list(range(len(y)))
    _, _, m2 = create_split(ids, y)
    assert m == m2
    p = tmp_path / "split.json"
    save_split(p, m)
    save_split(p, m2)
    _, _, m3 = create_split(ids, y, seed=2)
    with pytest.raises(ScientificValidationError):
        save_split(p, m3)


def test_single_class():
    with pytest.raises(ScientificValidationError):
        folds(np.zeros(20), 3, 1)
