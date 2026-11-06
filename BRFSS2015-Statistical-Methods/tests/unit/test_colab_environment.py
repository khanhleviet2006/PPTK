from pathlib import Path

from packaging.requirements import Requirement

from scripts.verify_environment import ROOT


def test_numpy_colab_and_original_versions():
    req = next(
        Requirement(line)
        for line in (ROOT / "requirements.txt").read_text().splitlines()
        if line.startswith("numpy")
    )
    assert "2.0.2" in req.specifier
    assert "2.2.6" in req.specifier
    assert "1.26.4" not in req.specifier
    assert "2.3.0" not in req.specifier


def test_requirements_path_independent_of_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert (ROOT / "requirements.txt").is_file()
    assert ROOT == Path(__file__).resolve().parents[2]


def test_dependency_closure_checks_transitive_versions(monkeypatch):
    from types import SimpleNamespace
    from scripts.verify_environment import dependency_conflicts
    import importlib.metadata

    dists = {"root": SimpleNamespace(requires=["child>=2"]), "child": SimpleNamespace(requires=[])}
    monkeypatch.setattr(importlib.metadata, "distribution", lambda name: dists[name])
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "1.0")
    assert "installed 1.0" in dependency_conflicts(["root"])[0]
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "2.0")
    assert dependency_conflicts(["root"]) == []
