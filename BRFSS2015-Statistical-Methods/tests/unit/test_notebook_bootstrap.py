import pytest
from scripts.colab_runtime import execute
from src.data.ingest import ScientificValidationError, discover


def test_development_cannot_access_final(tmp_path):
    with pytest.raises(ScientificValidationError, match="explicit allow_final"):
        execute(out=tmp_path / "not_created", synthetic=True, through="report")
    assert not (tmp_path / "not_created").exists()


def test_missing_dataset_is_actionable(tmp_path):
    with pytest.raises(FileNotFoundError, match="No substitute"):
        discover(directories=[tmp_path])


def test_setup_is_independent_and_initializes_variables(monkeypatch):
    import scripts.verify_environment as environment
    import scripts.notebook_bootstrap as bootstrap

    monkeypatch.setenv("BRFSS_SYNTHETIC", "1")
    monkeypatch.delenv("BRFSS_DATA", raising=False)
    monkeypatch.setattr(environment, "verify", lambda: {"python": "fixture"})
    variables = bootstrap.initialize(require_data=False)
    assert {"SYNTHETIC", "REPO", "PROJECT", "DATA", "OUT", "PROFILE"} <= variables.keys()
    assert variables["DATA"] is None and variables["SYNTHETIC"] is True
    assert variables["ALLOW_FINAL"] is False


def test_cli_final_requires_explicit_opt_in():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "scripts.run_pipeline", "--through", "report"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "requires --final-evaluation" in result.stderr
