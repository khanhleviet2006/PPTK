# Software validation

Executed in the cloud workspace with Python 3.12 and the pinned requirements installed in `/workspace/brfss-venv`.

Command: `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 /workspace/brfss-venv/bin/python tests/smoke.py --full`

Outcome: PASS, exit 0. Uses 240 synthetic records plus 10 duplicated profiles, generated only inside a temporary directory. Tests exercise grouped holdout separation; all five selectors; B0–B3 transforms; interactions and explicit composites; six model families; 3-fold synthetic CV; Optuna one trial for each of two selected boosting families; pipeline serialization; paired group-bootstrap final evaluation; repeat-final refusal; synthetic smoke-final refusal; target inclusion rejection. Temporary model/prediction artifacts are deleted when the test ends. CatBoost filesystem logging is disabled.

The real study defaults remain 5 folds and 12 tuning trials per selected family. Those runs were not executed on BRFSS. Software validation does not establish clinical accuracy, sensitivity, external validity, codebook correctness, literature comparability, or full-dataset resource feasibility.

No original source/data/results existed in this checkout at implementation time. New research files remain local/uncommitted. No GitHub push or publication was performed. Environment configuration draft saved `install_script` and `start_skill`; publishing the environment is a separate user action.
