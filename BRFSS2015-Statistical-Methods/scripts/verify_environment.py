import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from packaging.requirements import Requirement
from pathlib import Path


def verify():
    if not (3, 10) <= sys.version_info[:2] < (3, 13):
        raise RuntimeError(
            "Supported Python: 3.10–3.12. Revalidate constraints for other versions."
        )
    versions = {"python": platform.python_version()}
    for line in Path("requirements.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        req = Requirement(line)
        v = importlib.metadata.version(req.name)
        if v not in req.specifier:
            raise RuntimeError(f"Version mismatch: {req.name} {v}, expected {req.specifier}")
        versions[req.name] = v
    for mod in ["numpy", "pandas", "scipy", "sklearn", "statsmodels", "imblearn", "src.pipeline"]:
        importlib.import_module(mod)
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    print(json.dumps(versions, indent=2))
    return versions


if __name__ == "__main__":
    verify()
