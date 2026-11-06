"""Read original CDC XPT; no automatic substitute downloads."""

from pathlib import Path
import os
import shutil
import tempfile
import zipfile
from pathlib import PurePosixPath
import pandas as pd
import pyreadstat
from src.utils.io import digest


class ScientificValidationError(ValueError):
    pass


def discover(explicit=None, directories=(), filename="LLCP2015.XPT"):
    if explicit:
        p = Path(explicit).expanduser()
        if p.is_file():
            return p
        raise FileNotFoundError(f"Configured file does not exist: {p}")
    matches = []
    for folder in directories:
        p = Path(folder)
        if p.is_dir():
            matches.extend(
                f
                for f in p.iterdir()
                if f.is_file()
                and (
                    f.name.upper() == filename.upper()
                    or (filename == "LLCP2015.XPT" and f.name.upper() == "LLCP2015XPT.ZIP")
                )
            )
    matches = list(dict.fromkeys(matches))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ScientificValidationError(
            f"Multiple candidates: {matches}; set data_path explicitly."
        )
    raise FileNotFoundError(
        f"Missing {filename}. Mount Drive, extract CDC LLCP2015XPT.zip, and set data_path "
        f"or --data. Searched only: {list(directories)}. No substitute was downloaded."
    )


def load_xpt(path, columns=None):
    path = materialize_xpt(path)
    with path.open("rb") as f:
        if not f.read(80).startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"):
            raise ScientificValidationError("Not a SAS XPORT file (possibly an unextracted ZIP).")
    # Read metadata independently so projected loading cannot conceal source dimensions.
    _, meta = pyreadstat.read_xport(str(path), metadataonly=True)
    df, _ = pyreadstat.read_xport(str(path), usecols=columns)
    return df, {
        "source_sha256": digest(path),
        "source_columns": meta.column_names,
        "labels": dict(zip(meta.column_names, meta.column_labels)),
        "loaded_records": len(df),
        "file_bytes": path.stat().st_size,
    }


def load_processed(path):
    df = pd.read_csv(path)
    if "Diabetes_binary" not in df:
        raise ScientificValidationError(
            "Dataset B requires Diabetes_binary and separate provenance."
        )
    return df


def materialize_xpt(path, cache=None):
    """Extract only the exact CDC XPT member; validate archive paths and CRC, cache by hash."""
    path = Path(path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Raw data absent: {path}; set BRFSS_DATA to XPT or CDC ZIP.")
    if path.suffix.lower() != ".zip":
        return path
    archive_hash = digest(path)
    base = Path(
        cache
        or os.environ.get(
            "BRFSS_XPT_CACHE",
            "/content/brfss_xpt"
            if Path("/content").is_dir()
            else Path(tempfile.gettempdir()) / "brfss_xpt",
        )
    )
    folder = base / archive_hash
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "LLCP2015.XPT"
    from src.utils.io import read_json, write_json

    stamp = folder / "extraction.json"
    if target.is_file() and stamp.is_file():
        meta = read_json(stamp)
        if meta.get("archive_sha256") == archive_hash and meta.get("xpt_sha256") == digest(target):
            return target
    try:
        with zipfile.ZipFile(path) as archive:
            matches = []
            for info in archive.infolist():
                member = PurePosixPath(info.filename.replace("\\", "/"))
                if member.is_absolute() or ".." in member.parts or ":" in info.filename:
                    raise ScientificValidationError("Unsafe path in ZIP archive")
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ScientificValidationError("Symlink in ZIP archive")
                if member.name.strip().upper() == "LLCP2015.XPT" and not info.is_dir():
                    matches.append(info)
            if len(matches) != 1:
                raise ScientificValidationError("ZIP must contain exactly one LLCP2015.XPT member")
            info = matches[0]
            if info.file_size > 3_000_000_000:
                raise ScientificValidationError("XPT exceeds 3 GB extraction limit")
            fd, temporary = tempfile.mkstemp(dir=folder, prefix=".extract-")
            try:
                with os.fdopen(fd, "wb") as dst, archive.open(info) as src:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)
                with open(temporary, "rb") as src:
                    if not src.read(80).startswith(
                        b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"
                    ):
                        raise ScientificValidationError("ZIP member is not SAS XPORT")
                os.replace(temporary, target)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise ScientificValidationError(f"Cannot read CDC ZIP: {exc}") from exc
    write_json(
        stamp,
        {"archive_sha256": archive_hash, "xpt_sha256": digest(target), "member": info.filename},
    )
    return target
