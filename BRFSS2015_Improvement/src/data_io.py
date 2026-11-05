"""Bounded, CRC-checked XPT-in-ZIP input; never extracts archive paths."""
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import hashlib
import stat
import tempfile
import zipfile

import pandas as pd

MAX_XPT_BYTES = 4 * 1024**3
MAX_RATIO = 200
MAX_MEMBERS = 10000


def zip_member(archive):
    """Accept exactly one unencrypted regular XPT with conservative size limits."""
    entries = archive.infolist()
    if len(entries) > MAX_MEMBERS:
        raise ValueError('Too many ZIP members.')
    names = set()
    for entry in entries:
        name = entry.filename
        path = PurePosixPath(name)
        if (name in names or '\\' in name or path.is_absolute()
                or '..' in path.parts or ':' in name or '\x00' in name):
            raise ValueError('Unsafe or duplicate ZIP member name.')
        names.add(name)
        if stat.S_ISLNK(entry.external_attr >> 16):
            raise ValueError('ZIP symbolic links are not accepted.')
    candidates = [e for e in entries if not e.is_dir()
                  and PurePosixPath(e.filename).suffix.lower() == '.xpt']
    if len(candidates) != 1:
        raise ValueError('ZIP must contain exactly one XPT; ambiguous archives are refused.')
    entry = candidates[0]
    mode = stat.S_IFMT(entry.external_attr >> 16)
    if mode not in (0, stat.S_IFREG):
        raise ValueError('XPT member is not a regular file.')
    if entry.flag_bits & 1:
        raise ValueError('Encrypted XPT is unsupported.')
    if entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise ValueError('Only stored/deflated XPT members are supported.')
    if not 0 < entry.file_size <= MAX_XPT_BYTES:
        raise ValueError('XPT exceeds the 4 GiB bound or is empty.')
    if entry.file_size / max(entry.compress_size, 1) > MAX_RATIO:
        raise ValueError('ZIP compression ratio exceeds the safety bound.')
    return entry


@contextmanager
def xpt_source(path):
    """Yield seekable input and provenance; temporary content is always removed."""
    path = Path(path)
    if path.suffix.lower() == '.xpt':
        with path.open('rb') as stream:
            yield stream, {'format': 'xpt', 'container': str(path)}
        return
    if path.suffix.lower() != '.zip':
        raise ValueError('Expected .xpt or an XPT .zip.')
    with zipfile.ZipFile(path) as archive:
        entry = zip_member(archive)
        # Disk-backed temporary file avoids loading ~1+ GiB of decompressed bytes
        # into RAM and avoids repeated ZipExtFile decompression during SAS seeks.
        with tempfile.TemporaryFile(prefix='brfss_xpt_') as tmp:
            sha = hashlib.sha256()
            total = 0
            with archive.open(entry) as source:
                while True:
                    block = source.read(1024**2)
                    if not block:
                        break
                    total += len(block)
                    if total > MAX_XPT_BYTES or total > entry.file_size:
                        raise ValueError('XPT stream exceeds declared/safe size.')
                    sha.update(block)
                    tmp.write(block)
            # Reading to EOF above also validates zipfile's CRC check.
            if total != entry.file_size:
                raise ValueError('Truncated XPT member.')
            tmp.seek(0)
            yield tmp, {'format': 'xpt-in-zip', 'container': str(path),
                        'member': entry.filename, 'member_bytes': total,
                        'member_sha256': sha.hexdigest(),
                        'member_crc32': f'{entry.CRC:08x}', 'crc_checked': True}


def read_xpt(path, sample_rows=None):
    with xpt_source(path) as (stream, info):
        with pd.read_sas(stream, format='xport', encoding='utf8', iterator=True) as reader:
            frame = reader.read(nrows=sample_rows)
            frame.attrs['input_provenance'] = info
            return frame


def inspect_xpt(path, sample_rows=1000):
    """Metadata and a bounded sample only: no fitting, splitting or test scoring."""
    if sample_rows < 1:
        raise ValueError('sample_rows must be positive.')
    with xpt_source(path) as (stream, info):
        with pd.read_sas(stream, format='xport', encoding='utf8', iterator=True) as reader:
            sample = reader.read(nrows=sample_rows)
            info.update(columns=list(sample.columns), sample_rows=len(sample),
                        xpt_reported_rows=int(reader.nobs),
                        sample_only=True, raw_domain_audit_complete=False)
            return sample, info
