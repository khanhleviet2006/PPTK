"""Standard-library-only bootstrap shared by every standalone notebook."""

import importlib
import json
import pkgutil
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def initialize(require_data=True):
    synthetic = os.environ.get("BRFSS_SYNTHETIC", "0") == "1"
    if not (3, 10) <= sys.version_info[:2] < (3, 14):
        raise RuntimeError(f"Python {sys.version.split()[0]} unsupported; use Python 3.10–3.13.")
    required = [
        "pyproject.toml",
        "src/pipeline.py",
        "src/data/ingest.py",
        "src/data/outcomes.py",
        "src/data/synthetic.py",
        "configs/project.yaml",
    ]
    layout = ROOT / "docs/required_source_files.json"
    if not layout.is_file():
        raise FileNotFoundError(f"Missing {layout}; update the complete checkout")
    required += json.loads(layout.read_text())
    missing = [n for n in required if not (ROOT / n).is_file()]
    if missing:
        raise FileNotFoundError(f"Incomplete checkout: {missing}. Update the entire repository.")
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    out = Path(
        os.environ.get(
            "BRFSS_OUT",
            str(ROOT / "runs" / ("colab_synthetic_v2" if synthetic else "colab_new_protocol_v2")),
        )
    ).resolve()
    if not synthetic:
        commands = [[sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")]]
        if os.environ.get("BRFSS_INSTALL_OPTIONAL", "1") == "1":
            commands += [
                [sys.executable, "-m", "pip", "install", "-r", str(ROOT / f)]
                for f in ["requirements-boosters.txt", "requirements-research-extensions.txt"]
            ]
        commands.append([sys.executable, "-m", "pip", "install", "-e", str(ROOT), "--no-deps"])
        for i, command in enumerate(commands):
            result = subprocess.run(command, capture_output=True, text=True)
            log = ROOT / "runs/bootstrap_logs" / f"install_{i}.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(result.stdout + result.stderr)
            print(
                f"Install step {i + 1}: {'PASS' if result.returncode == 0 else 'FAIL'}; log: {log}"
            )
            if result.returncode:
                raise RuntimeError(
                    f"Install failed using {sys.executable} Python {sys.version.split()[0]}. Log: {log}\n"
                    + (result.stdout + result.stderr)[-6000:]
                )
    importlib.invalidate_caches()
    from scripts.verify_environment import verify

    try:
        versions = verify()
    except (ImportError, ValueError) as exc:
        raise RuntimeError(
            "Binary/import incompatibility after installation. Restart the Colab session and Run all; if persistent, inspect bootstrap logs. "
            + str(exc)
        ) from exc
    for name in ["src", "src_extensions", "scripts"]:
        package = importlib.import_module(name)
        for module in pkgutil.walk_packages(package.__path__, name + "."):
            importlib.import_module(module.name)
    from scripts.colab_runtime import locate_data, locate_codebook

    data = None if synthetic or not require_data else str(locate_data(os.environ.get("BRFSS_DATA")))
    codebook = (
        None
        if synthetic or not require_data
        else str(locate_codebook(data, os.environ.get("BRFSS_CODEBOOK")))
    )
    return dict(
        SYNTHETIC=synthetic,
        REPO=ROOT,
        PROJECT=ROOT.parent,
        DATA=data,
        DATA_PATH=data,
        CODEBOOK_PATH=codebook,
        OUT=out,
        PROFILE=os.environ.get("BRFSS_PROFILE", "quick").lower(),
        MODE=os.environ.get("BRFSS_MODE", "binary"),
        PROTOCOL=os.environ.get("BRFSS_PROTOCOL", "NEW_PROTOCOL"),
        SEED=int(os.environ.get("BRFSS_SEED", "20261107")),
        ALLOW_FINAL=os.environ.get("BRFSS_FINAL_EVALUATION", "0") == "1",
        versions=versions,
    )
