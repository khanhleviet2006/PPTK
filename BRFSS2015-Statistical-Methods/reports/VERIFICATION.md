# Executed verification — 2026-11-06

The opening table records the original release. Current post-audit release verification appears below:54 passing tests and the scoped extension executions.

| Check | Actual result |
|---|---|
| Fresh isolated Linux installation | PASS: Python 3.12.14, exact core requirements and optional boosters |
| Compilation, lint, formatting, imports, dependency conflicts | PASS: compileall, ruff, environment validator, pip check |
| Unit / scientific / integration / schema tests | **39 passed, no skips** in final R-enabled run |
| Independent R reference | PASS: R 4.2.2, survey 4.1-1, nnet 7.3-18 and numDeriv; means, domain variance, binary and multinomial coefficients/covariance |
| Actual notebook execution | **13 notebooks × 2 = 26**; a fresh kernel each time; same output/checkpoint directory for each repeat |
| Synthetic standard profile | PASS: 39 completed experiments, 5-fold development, feature/imbalance ablations and all available model families |
| Synthetic three-class profile | PASS: multinomial inference, 17 prediction experiments, class metrics and output checks |
| Original CDC source audit | PASS: original XPT, 441456 records / 330 columns; codebook verification; source SHA256 fingerprints |
| Original-data binary inference | PASS: weighted descriptions, adjusted/univariate ORs, group Wald tests, VIF, missingness and outcome sensitivities |
| Original-data multinomial inference | PASS: core-question three-category complete-case and deterministic-imputation fits; RRR tables |
| Original-data quick prediction | PASS: 4000 training respondents, 3-fold development, 17 successful experiments; 84512 held-out respondents evaluated once |
| Original-data resume | PASS: all 8 checkpoints resumed; evaluation_count remains 1; scientific source unchanged during canonical run |
| Actual Google Colab runtime | **COLAB_RUNTIME_NOT_VERIFIED** |
| Full real-data standard/extended experiments | **NOT_EXECUTED**; standard code exercised on synthetic data |
| Real Dataset B reproduction | **NOT_EXECUTED**; approximate reproduction tested on synthetic fixture; processed data/provenance not supplied |

Canonical commands:

```bash
python scripts/verify_environment.py
python -m compileall -q src scripts tests
ruff check .
ruff format --check .
BRFSS_RSCRIPT=/path/to/Rscript python -m pytest -q
python scripts/validate_notebooks.py --execute --repeat 2 --output reports/notebook_execution_verified
python scripts/run_pipeline.py --synthetic --n 960 --profile standard --out runs/synthetic_standard_verified
python scripts/run_pipeline.py --synthetic --n 1600 --mode core_three --out runs/synthetic_three_verified
python scripts/run_pipeline.py --data /path/to/LLCP2015.XPT --codebook /path/to/codebook15_llcp.pdf --out runs/real_final_quick
python scripts/run_pipeline.py --data /path/to/LLCP2015.XPT --codebook /path/to/codebook15_llcp.pdf --mode core_three --out runs/real_three_inference --through inference
python scripts/verify_outputs.py runs/real_final_quick
```

R was run from locally extracted Debian packages because system installation was unavailable. This is independent reference validation, not a Colab run. Notebook execution used nbclient with loopback socket access. Final pytest reported 17 warnings from upstream Matplotlib/pyparsing deprecations and LightGBM feature-name notices; no failed/skipped tests were hidden.

Synthetic debugging and source/formatting corrections preceded the canonical final real evaluation. An earlier real-data development run (`runs/real_quick`) never accessed its final test. Canonical scientific sources remained unchanged from run start through evaluation/resume. No real final-test result guided models, features or thresholds. Logs and result manifests are retained in reports/.

The quick model traded accuracy, specificity and calibration for sensitivity. Its 67.47% accuracy did not achieve the proposed 82.26% target. Conditional respondent-bootstrap intervals do not cover survey population prediction, model-selection uncertainty or external validation. No faithful Chang replication, full real three-class prediction or publication-ready multiple-imputation analysis is claimed.


## Post-audit extension verification

Baseline39 tests passed before modification; recoverable pre-change snapshot created (approximately12MB compressed). Current suite54 tests passed with independent R references enabled, no skips;17 upstream warnings. New tests cover selectors, calibration pipelines, categorical ADASYN rejection, OOF/cache integrity, threshold-policy metrics, SMOTENC encoded-name regression and temporal ledger interruption. Compilation, lint, formatting and pip check executed.

78/78 real binary development configs and4/4 real core-three configs completed. An earlier77/78 attempt exposed a feature-name export IndexError, corrected in a preserved v2 run. No legacy model/config/split/test artifacts changed. Legacy2015 evaluation_count=1; separate2017 temporal evaluation_count=1, n5000. Additional tuning/repeated/group CV, SHAP and simulated federation executed.

Original13 notebooks had prior26 clean-kernel executions. The3 modified notebooks were each rerun twice in new kernels on synthetic fixtures (6 current executions); unchanged notebooks retain prior evidence. Initial test harness passed uppercase SMOKE to legacy notebooks and failed; harness corrected to legacy quick, then all3 passed twice. This was synthetic-only debugging. Actual Colab remains COLAB_RUNTIME_NOT_VERIFIED. Full standard/extended real execution and faithful processed reproduction remain incomplete. Overall PARTIAL COMPLETION.

Final release: canonical v4 completed78/78 after correcting strict inner preprocessing and its wrapper. A new regression test verifies the inner-safe selector path, and a negative test prevents resetting2017 by changing output directory. Final suite54 passed, no skips;17 upstream warnings. Legacy source/config/model/split/evaluation hashes remain unchanged. Current master was tested twice in clean kernels against the final engine.
