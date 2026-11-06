from pathlib import Path
import nbformat


def test_notebook_schemas():
    paths = list(Path("notebooks").glob("*.ipynb"))
    assert len(paths) == 13
    for p in paths:
        nb = nbformat.read(p, as_version=4)
        nbformat.validate(nb)
        assert nb.metadata.kernelspec.name == "python3"
