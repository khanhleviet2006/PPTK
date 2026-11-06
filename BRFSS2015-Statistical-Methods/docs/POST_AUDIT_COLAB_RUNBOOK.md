# Post-audit Colab runbook

1. Extract **BRFSS2015-Complete-Research.zip** to `/content/drive/MyDrive/BRFSS2015_Statistical_Methods_AZ/`. Keep its protected `runs/real_final_quick` bundle; the earlier source-only ZIP omits this required state.
2. Store original CDC `LLCP2015.XPT` in one of the bounded discovery folders or set `BRFSS_DATA` explicitly. The raw file is not in the ZIP. CDC source: https://www.cdc.gov/brfss/annual_data/2015/files/LLCP2015XPT.zip . Normalize the archive member's trailing space.
3. Open `notebooks/00_Run_All_Colab.ipynb`. Check REPO and OUT in its first code cell. Default Drive root is the path above. The master mounts Drive, validates Python, installs core/boosters/extensions and runs development-only research. CPU defaults, one estimator worker.
4. Default real profile is QUICK (2000 development respondents,2 outer folds). SMOKE uses a small explicit fixture/subset. STANDARD uses the complete eligible development pool,5 folds. EXTENDED currently shares the main five-fold grid; longer repeat/nested search budgets remain unfinished and are not claimed as executed. Full profiles may exceed a Colab session.
5. Exact packages: requirements.txt, requirements-boosters.txt, requirements-research-extensions.txt. Tested Linux Python3.12.14; Python3.10–3.12 declared. If pip replaces imported packages, restart then rerun setup before research imports.
6. Resume with the same output folder, source and code. Per-experiment prediction checksums preserve completed work. Source changes require a separate documented exploratory run, never a fresh independent test claim.
7. View shipped `reports/FINAL_RESEARCH_REPORT.md`, detailed comparison tables and unfinished work. The notebook explicitly identifies the shipped report; it does not relabel old manuscript results as a new run's outcomes. To render a new compatible binary QUICK run, use `scripts.report_gap_results.report(run_path=OUT)` only after its ancillary outputs and supporting evidence are available; inspect scope labels.
8. Historical notebooks10/11 reject real-data evaluation; their synthetic execution remains supported. The2015 final test is closed to new model development. The2017 temporal model has also been evaluated once and must not become a tuning target. New confirmatory work requires new independent data/design.
9. Local equivalents:

```bash
pip install -r requirements.txt -r requirements-boosters.txt -r requirements-research-extensions.txt
pip install -e . --no-deps
python scripts/run_gap_experiments.py --data /path/LLCP2015.XPT --out runs/new_development --profile QUICK
python scripts/verify_gap_outputs.py  # shipped canonical outputs
```

The immutable legacy bundle is necessary for exclusion and integrity checks. Do not delete ledgers, fabricate them or silently regenerate a2015 final test if it is missing. No actual Google Colab runtime was accessible here: **COLAB_RUNTIME_NOT_VERIFIED**. Only the documented Linux notebook executions are verified.
