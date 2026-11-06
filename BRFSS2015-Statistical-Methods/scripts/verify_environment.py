import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from packaging.requirements import Requirement
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def verify():
    if not (3, 10) <= sys.version_info[:2] < (3, 13):
        raise RuntimeError(
            "Supported Python: 3.10–3.12. Revalidate constraints for other versions."
        )
    versions = {"python": platform.python_version()}
    for line in (ROOT / "requirements.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        req = Requirement(line)
        if req.marker and not req.marker.evaluate():
            continue
        v = importlib.metadata.version(req.name)
        if v not in req.specifier:
            raise RuntimeError(f"Version mismatch: {req.name} {v}, expected {req.specifier}")
        versions[req.name] = v
    for mod in ["numpy", "pandas", "scipy", "sklearn", "statsmodels", "imblearn", "src.pipeline"]:
        loaded = importlib.import_module(mod)
        if mod in {"numpy", "pandas", "scipy", "sklearn", "statsmodels", "imblearn"}:
            package = {"sklearn": "scikit-learn", "imblearn": "imbalanced-learn"}.get(mod, mod)
            if loaded.__version__ != versions[package]:
                raise RuntimeError(
                    f"{mod} loaded {loaded.__version__}, installed {versions[package]}. "
                    "Restart the Colab session after installation, then rerun setup."
                )
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    print(json.dumps(versions, indent=2))
    return versions


if __name__ == "__main__":
    verify()
