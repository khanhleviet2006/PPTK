"""Create a source + verified-report archive, excluding raw data and historical runs."""

from pathlib import Path
import argparse
import zipfile
from src.utils.io import digest


def package(destination):
    root = Path.cwd()
    destination = Path(destination)
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            relative = p.relative_to(root)
            if any(
                part in ["__pycache__", ".pytest_cache", ".ruff_cache", ".git", ".venv", "runs"]
                or part.endswith(".egg-info")
                for part in relative.parts
            ):
                continue
            if relative.parts[0] == "data":
                continue
            if p.suffix.lower() in [".xpt", ".zip", ".joblib"] or p.name == ".env":
                continue
            if (
                relative.parts[0] == "reports"
                and len(relative.parts) > 1
                and relative.parts[1].startswith("notebook_execution")
                and relative.parts[1] != "notebook_execution_verified"
            ):
                continue
            archive.write(p, Path(root.name) / relative)
    print(destination, destination.stat().st_size, digest(destination))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("destination")
    package(p.parse_args().destination)
