# Colab execution repair audit

Date: 2026-11-06. Repository before repair: `7fcd764b33a4f6a15216d253cd22553c394db637`.

The failure was reproducible from the published tree: all four `src/data` files were absent. Root causes were the unanchored `data/` ignore rule and archive publication filters excluding any path component named data. The fix tracks the recovered source package, anchors raw-data exclusions to the project root, and tests that a source archive contains the ingestion/outcome/synthetic modules while excluding runs.

## Recovery and history

GitHub path histories for `src/data/{__init__,ingest,outcomes,synthetic}.py` and `runs/real_final_quick/split.json` contained no commits. Both project-introducing commits and the current tree were inspected. Original module bytes and the historical split were recovered locally from `brfss_before_gap_extension.tar.gz`; their original digests are in `colab_repair_validation/history_recovery.json`. Outcome semantics and synthetic generation were retained, with formatting and validated ZIP ingestion added. The recovered split is not published alone or represented as a restored full historical study. Legacy models, frozen selection, original source/config hashes and test ledger are also necessary; the strict audit remains mandatory.

## Changes

- Restored `src/data/__init__.py`, `ingest.py`, `outcomes.py`, `synthetic.py`.
- Ingestion handles XPT or a CDC ZIP with one exact member, safe paths, CRC validation, a size cap, XPORT header checks and checksummed cached extraction.
- Added `scripts/colab_runtime.py`: bounded path discovery, explicit NEW_PROTOCOL/LEGACY_RESUME dispatch, immutable protocol metadata and protected output-directory rules. Local codebook discovery or the recorded official CDC PDF with exact SHA256 is supported. An unavailable/changed PDF fails; names and coding are not fabricated.
- Replaced the master with ordered executable cells for Drive, repository preflight, dependencies, imports, protocol execution, status and current-run report display. It supports the supplied Drive folder containing spaces and the supplied raw ZIP directory. Python outside the tested range fails with an actionable explanation.
- Added the user data directory to `configs/project.yaml`, fixed `.gitignore` and both packaging scripts.
- Extension runner uses the shared ZIP loader. Its real-data path requires full legacy integrity; synthetic fixtures protect existing source without pretending that historical artifacts exist.
- Dependency verifier checks the transitive active project dependency graph and hard-fails missing/incompatible packages. Full global `pip check` output is still displayed; conflicts of unrelated preinstalled Colab applications are reported separately rather than falsely treated as study dependency failures.
- Added `tests/unit/test_colab_protocol.py`, the end-to-end runbook, README/navigation updates and verification artifacts.

## Scientific review

NEW_PROTOCOL uses the core prespecified statistical and prediction pipeline. Deterministic, codebook-only recoding precedes learned prediction preprocessing; imputation, encoding/scaling, feature selection and resampling live inside cloned fold pipelines. Mixed-variable SMOTE uses SMOTENC before categorical one-hot encoding; incompatible BorderlineSMOTE is rejected. Full-pipeline stacking uses internal CV. Training OOF predictions select candidates and binary thresholds; selection CV scores are optimistic and are not confirmatory performance. Models and thresholds are frozen before the single test batch. The existing final access ledger uses exclusive creation and rejects interrupted reuse. Atomic checkpoints record hashes and resume completed work.

`protocol.json`, source/code/version manifest and `split.json` identify each new study. No historical test result is used to choose models. The new study has unknown overlap with historical BRFSS 2015 test respondents; it is not independent confirmation of old models or replication of Chang's cohort/results. Prediction splits are respondent-stratified, not PSU-held-out or external validation; clustered dependence can limit generalization. Survey inferential procedures remain separate from conditional prediction bootstrap uncertainty. Prespecified descriptive/inference analyses use the eligible survey cohort and do not feed learned feature selection. The new mode implements the core grid, not a claim that all 21 research gaps have been resolved.

LEGACY_RESUME refuses missing files, invalid frozen artifacts, changed original code/config hashes or invalid test ledgers. No checkpoint is synthesized. A complete historical bundle may need its original separate checkout; this repair deliberately does not relax that audit.

## Executed verification

| Check | Result |
|---|---|
| Ruff lint, formatting and Python compilation of source/scripts/tests | PASS |
| Installed dependency check | PASS (`pip check`) |
| Unit/scientific/integration pytest suite | 62 PASS, 2 SKIPPED (R reference configuration absent) |
| Notebook JSON/schema validation | All 13 PASS |
| Master notebook, source-only checkout without legacy runs | PASS, two fresh kernels, second execution resumed, final synthetic test batch count remained 1 |
| Every notebook actual synthetic execution | PASS: all 13 notebooks executed twice in fresh kernels; see `colab_repair_validation/all_notebooks/results.json` |
| Real original CDC ZIP | PASS: 441,456 records / 330 columns; source/codebook audit, cohort/missingness, survey descriptive statistics, adjusted inference/sensitivities, split, training CV development |
| New real-data final test | NOT_EXECUTED; no new real test access ledger created |
| Actual Google Colab hosted runtime | COLAB_RUNTIME_NOT_VERIFIED |

The real-data evidence is recorded in `colab_repair_validation/real_data_results.json`. No empirical final-test benefit is claimed by this repair. Existing historical research reports were not relabelled as new execution results. Executed synthetic notebooks are software evidence only.

## Running

Update the entire repository, then follow [the Colab runbook](../docs/COLAB_END_TO_END.md). Do not run an old exported notebook against an incomplete folder. Use NEW_PROTOCOL by default. Configure a local codebook if CDC network access is unavailable. After installation changes an imported binary package, restart once and Run all. Keep the same seed, configuration and output path to resume; a signature change requires a separate run. Never remove a test ledger to force another evaluation.
