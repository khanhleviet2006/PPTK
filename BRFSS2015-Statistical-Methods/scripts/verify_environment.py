import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from packaging.requirements import Requirement
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def dependency_conflicts(names):
    """Validate all active requirements in the transitive project dependency closure."""
    queue, visited, conflicts = list(names), set(), []
    while queue:
        name = queue.pop()
        key = name.lower().replace("_", "-")
        if key in visited:
            continue
        visited.add(key)
        try:
            dist = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            conflicts.append(f"Missing {name}")
            continue
        for line in dist.requires or []:
            req = Requirement(line)
            if req.marker and not req.marker.evaluate({"extra": ""}):
                continue
            try:
                version = importlib.metadata.version(req.name)
            except importlib.metadata.PackageNotFoundError:
                conflicts.append(f"{name} requires missing {req}")
                continue
            if version not in req.specifier:
                conflicts.append(f"{name} requires {req}; installed {version}")
            queue.append(req.name)
    return conflicts


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
    conflicts = dependency_conflicts(versions.keys() - {"python"})
    if conflicts:
        raise RuntimeError("Project dependency conflicts: " + "; ".join(conflicts))
    # Colab also contains unrelated preinstalled applications. Report their global
    # constraints without mistaking them for the dependency graph of this study.
    check = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
    if check.returncode:
        print("GLOBAL_ENVIRONMENT_CONFLICTS (project dependency closure passed):")
    print(check.stdout + check.stderr)
    if check.returncode not in (0, 1):
        raise RuntimeError("pip check could not complete")
    print(json.dumps(versions, indent=2))
    return versions


if __name__ == "__main__":
    verify()
