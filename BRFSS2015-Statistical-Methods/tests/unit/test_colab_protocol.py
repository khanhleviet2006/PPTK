import zipfile
import pandas as pd
import pyreadstat
import pytest
from src.data.ingest import load_xpt, materialize_xpt, ScientificValidationError
from scripts.colab_runtime import execute, locate_repo
from scripts.package_project import package


def test_xpt_and_zip_roundtrip(tmp_path):
    original = tmp_path / "LLCP2015.XPT"
    pyreadstat.write_xport(
        pd.DataFrame({"VALUE": [1.0, 2.0, float("nan")]}), str(original), file_format_version=5
    )
    archive = tmp_path / "LLCP2015XPT.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.write(original, "LLCP2015.XPT ")
    frame, meta = load_xpt(original, ["VALUE"])
    assert frame.VALUE.iloc[:2].tolist() == [1.0, 2.0]
    assert pd.isna(frame.VALUE.iloc[2])
    extracted = materialize_xpt(archive, tmp_path / "cache")
    other, metadata = load_xpt(extracted)
    pd.testing.assert_frame_equal(frame, other)
    assert meta["source_sha256"] == metadata["source_sha256"]
    assert extracted == materialize_xpt(archive, tmp_path / "cache")
    extracted.write_bytes(b"corrupt")
    assert materialize_xpt(archive, tmp_path / "cache").read_bytes() == original.read_bytes()


def test_unsafe_and_invalid_archives(tmp_path):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("../LLCP2015.XPT", b"bad")
    with pytest.raises(ScientificValidationError, match="Unsafe"):
        materialize_xpt(archive, tmp_path / "cache")
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("unrelated.csv", b"bad")
    with pytest.raises(ScientificValidationError, match="exactly one"):
        materialize_xpt(archive, tmp_path / "cache")
    bad = tmp_path / "bad.xpt"
    bad.write_bytes(b"bad")
    with pytest.raises(ScientificValidationError, match="Not a SAS"):
        load_xpt(bad)


def test_repo_path_with_spaces(tmp_path):
    r = tmp_path / "PPTK-main (1)/PPTK-main/BRFSS2015-Statistical-Methods"
    (r / "src").mkdir(parents=True)
    (r / "pyproject.toml").touch()
    (r / "src/pipeline.py").touch()
    assert locate_repo(r) == r


def test_legacy_missing_fails_closed(tmp_path, monkeypatch):
    import scripts.audit_research_gaps as audit

    monkeypatch.setattr(audit, "RUN", tmp_path / "missing")
    with pytest.raises(FileNotFoundError, match="LEGACY_RESUME"):
        execute(protocol="LEGACY_RESUME", out=tmp_path / "out")
    assert not (tmp_path / "out/split.json").exists()


def test_new_protocol_forbids_legacy_output():
    from scripts.colab_runtime import ROOT

    with pytest.raises(ScientificValidationError, match="separate"):
        execute(out=ROOT / "runs/real_final_quick", synthetic=True)


def test_source_archive_includes_data_modules(tmp_path, monkeypatch):
    from scripts.colab_runtime import ROOT

    monkeypatch.chdir(ROOT)
    destination = tmp_path / "source.zip"
    package(destination)
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        assert all(
            any(n.endswith("src/data/" + p) for n in names)
            for p in ["ingest.py", "outcomes.py", "synthetic.py"]
        )
        assert not any("/runs/" in n for n in names)


def test_codebook_download_hash_validation(tmp_path, monkeypatch):
    import hashlib
    import requests
    import scripts.colab_runtime as runtime

    payload = b"%PDF-fixture-only"
    monkeypatch.setenv("BRFSS_DOCUMENT_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(
        runtime,
        "read_json",
        lambda p: {
            "files": [
                dict(
                    filename="codebook15_llcp.pdf",
                    source="https://www.cdc.gov/fixture",
                    sha256=hashlib.sha256(payload).hexdigest(),
                )
            ]
        },
    )

    class Response:
        content = payload

        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda *a, **kw: Response())
    target = runtime.locate_codebook(tmp_path / "raw/LLCP2015XPT.zip")
    assert target.read_bytes() == payload
    target.unlink()
    Response.content = b"wrong"
    with pytest.raises(ScientificValidationError, match="hash differs"):
        runtime.locate_codebook(tmp_path / "raw/LLCP2015XPT.zip")
