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
