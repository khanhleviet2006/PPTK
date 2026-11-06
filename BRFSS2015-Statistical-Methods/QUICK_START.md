# Quick start

Google Colab Python 3.13: follow [COLAB_QUICK_START.md](docs/COLAB_QUICK_START.md). Update the entire project and open the current master; every active notebook is standalone. Final Test is disabled during development by default.

For local Linux validation:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-boosters.txt -r requirements-research-extensions.txt
python -m pip install -e . --no-deps
python scripts/verify_environment.py
python -m pytest
python -m scripts.validate_notebooks --execute --repeat 2
```

Original data: use the exact CDC ZIP/XPT and codebook; see [the runbook](docs/COLAB_QUICK_START.md). Never silently substitute a processed dataset. CLI development example (requires a new output directory):

```bash
python -m scripts.run_pipeline --data /your/path/LLCP2015XPT.zip --codebook /your/path/codebook15_llcp.pdf --out runs/cli_new_study --profile quick --through develop
```

The low-level CLI requires `--final-evaluation` for `--through evaluate` or `--through report`. Prefer the master and NEW_PROTOCOL wrapper for an explicit protocol manifest and development report without test access. Synthetic fixtures are software validation, not empirical findings. Changed signatures require a new output directory. Keep all old test ledgers.
