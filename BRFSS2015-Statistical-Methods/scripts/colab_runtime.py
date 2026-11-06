"""Colab entry point with explicit, isolated historical and new protocols."""

import os
from pathlib import Path

from src.data.ingest import ScientificValidationError, discover
from src.utils.io import canonical_hash, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def locate_repo(explicit=None):
    if explicit:
        candidates = [Path(explicit).expanduser()]
    else:
        drive = Path("/content/drive/MyDrive")
        candidates = [
            Path.cwd(),
            Path.cwd().parent,
            ROOT,
            drive / "BRFSS2015-Statistical-Methods",
            drive / "BRFSS2015_Statistical_Methods_AZ/BRFSS2015-Statistical-Methods",
        ]
        if drive.is_dir():
            candidates += sorted(drive.glob("PPTK-main*/PPTK-main/BRFSS2015-Statistical-Methods"))
    for candidate in candidates:
        if (candidate / "pyproject.toml").is_file() and (candidate / "src/pipeline.py").is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "Set BRFSS_REPO to BRFSS2015-Statistical-Methods. Checked: " + str(candidates)
    )


def require_legacy():
    from scripts.audit_research_gaps import PROTECTED, RUN, snapshot

    missing = [str(RUN / n) for n in PROTECTED if not (RUN / n).is_file()]
    if missing:
        raise FileNotFoundError(
            "LEGACY_RESUME requires the complete preserved bundle; missing: "
            + ", ".join(missing)
            + ". Use NEW_PROTOCOL in a separate output directory; never reconstruct historical test IDs."
        )
    from scripts.audit_research_gaps import audit

    # Hashes, original code, frozen selection and one-time test ledger must all agree.
    audit(verify_only=True)
    return snapshot()


def execute(
    protocol="NEW_PROTOCOL",
    synthetic=False,
    data=None,
    codebook=None,
    out=None,
    profile="quick",
    mode="binary",
    seed=20261107,
    through="report",
):
    if protocol not in {"NEW_PROTOCOL", "LEGACY_RESUME"}:
        raise ValueError("Protocol must be NEW_PROTOCOL or LEGACY_RESUME")
    os.chdir(ROOT)
    out = Path(out or ROOT / "runs/new_protocol").resolve()
    if protocol == "LEGACY_RESUME":
        if synthetic:
            raise ValueError("Synthetic fixtures cannot impersonate a historical resume")
        require_legacy()
        from src_extensions.runner import run

        return run(data=data, out=out, profile=profile.upper(), mode=mode)
    # Never write new artifacts over any historical run, including when it was not restored.
    legacy = ROOT / "runs"
    if out == legacy or any(
        out == legacy / n or legacy / n in out.parents
        for n in [
            "real_final_quick",
            "gap_real_quick",
            "gap_real_quick_v2",
            "gap_real_quick_v3",
            "gap_real_quick_v4",
            "temporal_2017",
        ]
    ):
        raise ScientificValidationError("NEW_PROTOCOL must use a separate output directory")
    definition = dict(
        protocol=protocol,
        seed=seed,
        profile=profile.lower(),
        mode=mode,
        synthetic=synthetic,
        primary_metric="training CV balanced_accuracy",
        test_policy="one frozen selected model and prespecified baseline batch; no test-based selection",
        historical_test_overlap="UNKNOWN: historical split not used; not independent validation of previously published models",
        claim_scope="new within-run split only; cross-sectional internal validation",
    )
    path = out / "protocol.json"
    signature = canonical_hash(definition)
    if path.exists() and read_json(path)["signature"] != signature:
        raise ScientificValidationError("Protocol changed; choose a new output directory")
    if not path.exists():
        write_json(path, dict(signature=signature, **definition))
    from src.pipeline import run

    return run(
        out=out,
        data=data,
        codebook=codebook,
        synthetic=synthetic,
        profile=profile.lower(),
        mode=mode,
        seed=seed,
        through=through,
    )


def locate_data(explicit=None):
    import yaml

    cfg = yaml.safe_load((ROOT / "configs/project.yaml").read_text())
    return discover(explicit or cfg.get("data_path"), cfg["candidate_directories"])


def locate_codebook(data, explicit=None):
    """Use a local CDC codebook or fetch only the recorded CDC PDF with exact hash."""
    from src.utils.io import atomic_bytes, digest

    if explicit:
        return discover(explicit, filename="codebook15_llcp.pdf")
    parent = Path(data).parent
    local = parent / "codebook15_llcp.pdf"
    if local.is_file():
        return local
    source = next(
        x
        for x in read_json(ROOT / "docs/source_manifest.json")["files"]
        if x["filename"] == "codebook15_llcp.pdf"
    )
    target = (
        Path(
            os.environ.get(
                "BRFSS_DOCUMENT_CACHE",
                "/content/brfss_documents" if Path("/content").is_dir() else "/tmp/brfss_documents",
            )
        )
        / source["filename"]
    )
    if target.is_file() and digest(target) == source["sha256"]:
        return target
    import hashlib
    import requests

    try:
        response = requests.get(source["source"], timeout=90)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FileNotFoundError(
            "CDC codebook download failed. Set BRFSS_CODEBOOK to codebook15_llcp.pdf. URL: "
            + source["source"]
        ) from exc
    if hashlib.sha256(response.content).hexdigest() != source["sha256"]:
        raise ScientificValidationError(
            "CDC codebook hash differs from audited source. Review the source; do not bypass validation."
        )
    atomic_bytes(target, response.content)
    return target
