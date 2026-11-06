"""Export code, frozen legacy state, executed research evidence and recovery snapshot; no raw data."""

from pathlib import Path
import zipfile
import argparse
from src.utils.io import digest

RUNS = {
    "real_final_quick",
    "gap_real_quick",
    "gap_real_quick_v2",
    "gap_real_quick_v3",
    "gap_real_quick_v4",
    "gap_real_three_v3",
    "temporal_2017",
}


def package(destination, checkpoint=None):
    root = Path.cwd()
    destination = Path(destination)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if any(
                x in [".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "data"]
                or x.endswith(".egg-info")
                for x in rel.parts
            ):
                continue
            if rel.parts[0] == "runs" and (len(rel.parts) < 2 or rel.parts[1] not in RUNS):
                continue
            if p.suffix.lower() in [".xpt", ".zip"] or p.name == ".env":
                continue
            if (
                rel.parts[0] == "reports"
                and len(rel.parts) > 1
                and rel.parts[1].startswith("notebook_execution")
                and rel.parts[1] != "notebook_execution_verified"
            ):
                continue
            z.write(p, Path(root.name) / rel)
        if checkpoint:
            z.write(checkpoint, Path(root.name) / "research_checkpoints/pre_extension.tar.gz")
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        assert any(n.endswith("runs/real_final_quick/split.json") for n in z.namelist())
        assert any(n.endswith("reports/FINAL_RESEARCH_REPORT.md") for n in z.namelist())
        assert not any(n.lower().endswith(".xpt") for n in z.namelist())
    print(destination, destination.stat().st_size, digest(destination))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("destination")
    p.add_argument("--checkpoint")
    package(**vars(p.parse_args()))
