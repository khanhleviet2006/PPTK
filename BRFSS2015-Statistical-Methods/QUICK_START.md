# Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e . --no-deps
pip install -r requirements-boosters.txt  # optional
python scripts/verify_environment.py
python -m pytest
python scripts/smoke_test.py
python scripts/validate_notebooks.py --execute
```

Original data: download the exact CDC LLCP2015XPT.zip and codebook15_llcp.pdf from https://www.cdc.gov/brfss/annual_data/annual_2015.html. Extract and normalize `LLCP2015.XPT ` to `LLCP2015.XPT`. The source audit expects 441456 records and 330 columns.

```bash
python scripts/run_pipeline.py --data /your/path/LLCP2015.XPT --codebook /your/path/codebook15_llcp.pdf --out runs/real_quick --profile quick
python scripts/verify_outputs.py runs/real_quick
# Primary full experiment, new output directory:
python scripts/run_pipeline.py --data /your/path/LLCP2015.XPT --codebook /your/path/codebook15_llcp.pdf --out runs/real_standard --profile standard
# Secondary three-category self-report, new directory:
python scripts/run_pipeline.py --data /your/path/LLCP2015.XPT --codebook /your/path/codebook15_llcp.pdf --out runs/real_three --mode core_three --profile quick
```

For Colab use notebooks/00_Run_All_Colab.ipynb and set persistent Drive paths. For synthetic validation add --synthetic; synthetic data never replace original data silently. Rerunning identical commands resumes checkpoints. Changed code/configuration/data requires a distinct run; preserve and disclose prior test access. Standard/extended modes can take hours on CPU; consult EXPERIMENT_PLAN before launching.


Post-audit extension: use [POST_AUDIT_COLAB_RUNBOOK.md](docs/POST_AUDIT_COLAB_RUNBOOK.md) and [FINAL_RESEARCH_REPORT.md](reports/FINAL_RESEARCH_REPORT.md). The master now performs development-only research; historical2015 real final-evaluation notebooks are blocked. Full research ZIP includes protected legacy state. Scientific status remains PARTIAL_COMPLETION.
