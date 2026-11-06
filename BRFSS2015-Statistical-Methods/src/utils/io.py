"""Atomic artifacts, checksums and content-addressed stage checkpoints."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def atomic_bytes(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def clean_json(x):
    if isinstance(x, dict):
        return {str(k): clean_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [clean_json(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return float(x) if np.isfinite(x) else None
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def write_json(path, value):
    atomic_bytes(path, json.dumps(clean_json(value), indent=2, allow_nan=False).encode())


def write_csv(path, frame):
    atomic_bytes(path, frame.to_csv(index=False).encode())


def read_json(path):
    return json.loads(Path(path).read_text())


def frame_hash(df):
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()


class Checkpoints:
    def __init__(self, root, signature):
        self.root = Path(root)
        self.signature = signature

    def valid(self, stage):
        p = self.root / "checkpoints" / (stage + ".json")
        if not p.exists():
            return False
        meta = read_json(p)
        return meta["signature"] == self.signature and all(
            (self.root / f).is_file() and digest(self.root / f) == h
            for f, h in meta["outputs"].items()
        )

    def commit(self, stage, outputs):
        write_json(
            self.root / "checkpoints" / (stage + ".json"),
            {
                "signature": self.signature,
                "outputs": {str(Path(f).relative_to(self.root)): digest(f) for f in outputs},
            },
        )
