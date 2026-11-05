# Software validation

Executed in the cloud workspace with Python 3.12 and the pinned requirements installed in `/workspace/brfss-venv`.

Command: `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 /workspace/brfss-venv/bin/python tests/smoke.py --full`

Outcome: PASS, exit 0. Uses 240 synthetic records plus 10 duplicated profiles, generated only inside a temporary directory. Tests exercise grouped holdout separation; all five selectors; B0–B3 transforms; interactions and explicit composites; six model families; 3-fold synthetic CV; Optuna one trial for each of two selected boosting families; pipeline serialization; paired group-bootstrap final evaluation; repeat-final refusal; synthetic smoke-final refusal; target inclusion rejection. Temporary model/prediction artifacts are deleted when the test ends. CatBoost filesystem logging is disabled.

The real study defaults remain 5 folds and 12 tuning trials per selected family. Those runs were not executed on BRFSS. Software validation does not establish clinical accuracy, sensitivity, external validity, codebook correctness, literature comparability, or full-dataset resource feasibility.

No original source/data/results existed in this checkout at implementation time. New research files remain local/uncommitted. No GitHub push or publication was performed. Environment configuration draft saved `install_script` and `start_skill`; publishing the environment is a separate user action.

## ZIP/schema/lock update — 2026-11-05

- `python -m unittest discover -s tests -p 'test_*.py'`: **9 tests passed**, exit 0. Real pandas SAS V5 parsing of a five-row synthetic XPT, equality of direct and zipped input, system missing, bounded sample/header inspection, whole-file raw-code frequency audit, CRC corruption rejection, member/path/link/size/ratio rejection, temporary-handle cleanup, review gate, raw-domain checks before recoding, BMI bin boundaries, default final lock, and refusal to overwrite reports.
- `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python tests/smoke.py --full`: **PASS**, exit 0. Six model families, all selectors/preprocessing paths, synthetic Optuna, serialization and paired group bootstrap remain functional with the new input module. Final scoring occurs only on temporary synthetic data in this integration test, with an explicit test-only unlock; the real BRFSS Final Test was not accessed.
- All notebook code cells parsed with Python AST; no executable `final` invocation remains. Actual Google Colab execution/Drive access was not available in this cloud environment.
- The tests found and corrected the former right-closed BMI bins: exact 18.5/25/30 now enter the configured normal/overweight/obese categories. No Test outcomes were used for this fix.
- CDC PDF retrieval failed at the proxy with CONNECT 403. Official source/page/scale/missing-code validation and actual Drive ZIP/raw-domain inspection remain **unverified**, irrespective of software test success. `schema.reviewed.json` remains false/pending and cannot train as shipped.
- No original dataset, checkpoint or previous research output was changed. ZIP source is never modified; automatic temporary spooling is cleaned up. Source updates are versioned separately from prior frozen runs; the latter must use their original source version for final evaluation.

## Audit-only recheck after Colab report — 2026-11-05

`python -m unittest discover -s tests -p 'test_*.py'`: **16 tests PASS**, exit 0. No smoke training, fitted model, CV experiment or Final Test was run in this phase. Synthetic nontraining checks exercise parsing/CRC/ZIP bounds, raw recoding, backup-preserving/idempotent/header-dependent schema migration, conservative revocation of inherited citations, raw-count evidence/provenance mismatch handling, no fabricated page citations from a blank PDF, finite survey diagnostics, early audit-only training denial, and AST checks that notebook code contains no model fitting or Train/Final invocation. Original `research.load` split utility is exercised only on synthetic data by the pre-existing nontraining tests; no CV or model is fitted.

Actual Google Drive evidence (raw CSV/metadata/preflight/PDF) is not present in the workspace. Official CDC download retry returned 403; runtime custom allowed_hosts remained empty. User-reported 441456 rows and absent HIGHBP3 are recorded as reports, not independent file verification. BPHIGH4 remains a pending candidate. Unit success does not complete codebook, source authenticity, clinical timing, survey design or prior Test-use review. All unresolved requirements and codebook_reviewed=false remain in force.

## Preflight subprocess diagnostics — 2026-11-06

20 nontraining unit/integration tests PASS with Python 3.12.14. New tests execute the real audit CLI on the synthetic five-row XPT, repeat preflight with distinct report names, verify preservation of existing reports and visible FileExistsError, verify JSONDecodeError is present in the notebook-facing error and full log, and block sklearn/scipy/joblib/boosting imports in a subprocess to prove audit dependency isolation. No Train/CV, model fitting, Final Test or real BRFSS analysis ran.

The user's Colab traceback reports Python 3.13 and only CalledProcessError exit 1. The child stderr was not provided, so its actual cause is not established. The notebook now logs and exposes it; this does not establish that the actual Drive ZIP/schema succeeds in Colab. Codebook, raw-data, split-history and timing approvals remain unchanged/pending.

## Current schema verification — 2026-11-06

Schema was backed up before edits under `/workspace/brfss_schema_backups/`, content hash `1452e7a4551f495935f0a595f948df95a3cdf0d348a72fb507613ac7cbf8245a`. All pre-existing unresolved requirements were preserved. No VERIFIED/safe approvals were granted. Timing remains pending for every active variable. Survey weight/strata/PSU now require individual definition/page checks instead of relying on a blanket design status. Train/Test history remains UNKNOWN.

20 nontraining tests passed. `00_Audit/current_schema_verification.json` records the current schema-only audit and missing evidence. Actual raw-code counts, codebook PDF and page-evidence artifacts are absent in this workspace, so no real-data raw audit or codebook comparison was rerun. No Train/CV or Final Test ran; original data were not modified.
