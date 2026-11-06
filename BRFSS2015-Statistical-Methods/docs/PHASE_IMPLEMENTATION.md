# Phase-to-implementation map

| Phase | Working implementation / artifacts |
|---|---|
| 00 Environment | pyproject, exact requirements, tested Linux transitive lock, verify_environment.py, CI |
| 01 Protocol/literature | docs/RESEARCH_PROTOCOL, LITERATURE_REVIEW, RESEARCH_GAP_MATRIX, literature_evidence.csv |
| 02 Ingestion/audit | src/data/ingest.py; audit.json, CDC source_manifest.json, source/codebook fingerprints |
| 03 Outcomes | src/data/outcomes.py; cohort.json; binary/core-three and explicit module mapping |
| 04 Missingness | missingness.csv, missingness figures; fold-local predictive imputation; complete-case / deterministic sensitivity |
| 05 Descriptive | src/statistics/analysis.py; Table 1, weighted prevalence with design intervals |
| 06 Inference | Taylor linearization, survey logistic/multinomial, adjusted OR/RRR, group Wald, VIF, sensitivity tables |
| 07 Prediction split | src/modeling/splits.py; respondent IDs, split/test checksums and CV indices |
| 08 Features | src/features/engineering.py; fold-local original/clinical/MI/L1/tree/permutation/RFE/interactions |
| 09 Reproduction | scripts/reproduce_baseline.py; explicit Dataset B provenance; approximate status; synthetic test |
| 10 Experiments | src/modeling/experiments.py; finite CPU budgets; optional boosters and ensemble pipelines |
| 11 Selection | CV balanced accuracy, fixed threshold grid; frozen.json and model hash |
| 12 Final evaluation | src/evaluation/final.py; one-time ledger, test predictions, metrics, calibration, subgroups, CI |
| 13 Comparisons | paired respondent bootstrap, one prespecified McNemar comparison; no IID fold t-test |
| 14 Interpretation | training-only permutation importance; OR/RRR and sensitivity artifacts; contribution distinctions in report |
| 15 Reports | src/reporting/report.py; Markdown draft, CSV/JSON, figures, execution status |

All phase code is executable. Empirical execution scope is recorded separately in reports/VERIFICATION.md. A workflow implementation is not evidence that a full standard/extended real-data experiment or a faithful paper replication has completed. Dataset B is optional and is never substituted for original-data inference. No unverifiable literature detail is invented. Optional-module national inference remains blocked until a defensible geographic/version eligibility manifest and associated weights are supplied.
