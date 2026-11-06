# BRFSS 2015 Statistical Methods

A reproducible research system combining complex-survey associations with leakage-safe classification. It uses the original CDC XPT for inference, separate protected prediction runs, and a distinct approximate processed-data reproduction. No causal or clinical diagnostic claims are supported by this cross-sectional survey.

Start with [QUICK_START.md](QUICK_START.md) or [the Colab master notebook](notebooks/00_Run_All_Colab.ipynb). Python 3.10–3.12, Linux/Colab CPU. Exact core dependencies are pinned; optional boosters are in requirements-boosters.txt. Full literature evidence, outcome definitions, estimands, missing-data assumptions and experiment budgets are in docs/.

The primary binary contrast is self-reported diabetes versus explicit no diabetes, excluding pregnancy-only/borderline answers. Three-category core-question status is available as a secondary analysis and never claims complete prediabetes ascertainment. Missing optional-module answers are not confirmed negatives. Survey inference uses _LLCPWT, _STSTR and nested _PSU with a design-based Taylor covariance, not ordinary IID weighted-regression errors.

Output directories contain audit/cohort records, weighted Table 1 and prevalence, adjusted OR/RRR, sensitivities, experiment history, split hashes, frozen models, one-time test-access ledger, calibration/subgroup diagnostics, paired uncertainty and a generated academic report draft. Numerical output is never manufactured when a stage is unavailable. Synthetic reports are explicitly labelled.

See [reports/VERIFICATION.md](reports/VERIFICATION.md) for actual checks and limitations. Actual Google Colab runtime execution is separately classified as COLAB_RUNTIME_NOT_VERIFIED unless independently run there. Quick execution is a practical validation, not the full standard/extended study. Chang's 82.26% is a literature target, not a guaranteed outcome or comparable benchmark for a different cohort.

Repository layout follows the requested src/data, audit, features, statistics, modeling, evaluation, reporting, utils structure. No large data or credentials belong in Git. Model joblib files are trusted local artifacts; do not load unknown pickle/joblib files.


Post-audit extension: use [POST_AUDIT_COLAB_RUNBOOK.md](docs/POST_AUDIT_COLAB_RUNBOOK.md) and [FINAL_RESEARCH_REPORT.md](reports/FINAL_RESEARCH_REPORT.md). The master now performs development-only research; historical2015 real final-evaluation notebooks are blocked. Full research ZIP includes protected legacy state. Scientific status remains PARTIAL_COMPLETION.


Colab repair: see [end-to-end runbook](docs/COLAB_END_TO_END.md). The master now defaults to NEW_PROTOCOL, which works from a source-only checkout; LEGACY_RESUME still requires the original complete frozen bundle. See [verification](reports/COLAB_REPAIR_AUDIT.md).
