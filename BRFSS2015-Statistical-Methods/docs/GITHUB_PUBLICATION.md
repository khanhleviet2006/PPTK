# GitHub publication scope

This project is published under `PPTK/BRFSS2015-Statistical-Methods/`, alongside the pre-existing `BRFSS2015_Improvement` project. The two projects and their evidence are separate.

Included: research source, tests, dependency constraints, notebooks, reports, CSV result tables, figures, original-paper evidence and verification logs. Scientific status remains **PARTIAL_COMPLETION**; actual Colab execution is **COLAB_RUNTIME_NOT_VERIFIED**. Uploading the files does not rerun experiments or change the recorded result status.

Excluded from Git: raw CDC/UCI data, `runs/` model/cached prediction files, ZIP exports, large recovery checkpoints and credentials. Consequently a source-only Git clone is not the complete executable frozen-artifact bundle. The post-audit runner deliberately requires the preserved legacy bundle to exclude old test IDs and verify immutable state. Do not bypass that guard or regenerate the old final test when a file is absent.

Use the complete research ZIP supplied with the project delivery to restore the frozen artifacts before continuing post-audit real-data experiments. Raw data must be provided separately. Repository evidence contains aggregated results and recorded checksums; no claim is made that excluded model files are available from Git.

For a clone, work from this subdirectory before installation. Configure `BRFSS_REPO`, `BRFSS_DATA` and output paths as described in POST_AUDIT_COLAB_RUNBOOK.md. Reports can be read without downloading raw data or restoring model binaries.

- Main report: ../reports/FINAL_RESEARCH_REPORT.md
- Gap execution matrix: ../reports/RESEARCH_GAP_EXECUTION_MATRIX.md
- Machine-readable matrix: ../reports/research_gap_execution_matrix.csv
- Verification: ../reports/VERIFICATION.md
- Remaining work: ../reports/UNFINISHED_WORK.md
