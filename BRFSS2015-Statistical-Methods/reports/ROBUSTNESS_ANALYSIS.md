# Development robustness

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| seed_run | accuracy | balanced_accuracy | precision | sensitivity | f1 | macro_f1 | log_loss | class_0_sensitivity | class_0_specificity | class_1_sensitivity | class_1_specificity | roc_auc | pr_auc | brier | specificity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.6885 | 0.73573 | 0.2711 | 0.8 | 0.40497 | 0.597 | 0.32677 | 0.67147 | 0.8 | 0.8 | 0.67147 | 0.80174 | 0.37789 | 0.09888 | 0.67147 |
| 1 | 0.7245 | 0.71972 | 0.28464 | 0.71321 | 0.40689 | 0.61373 | 0.32535 | 0.72622 | 0.71321 | 0.71321 | 0.72622 | 0.79812 | 0.39853 | 0.09798 | 0.72622 |

Additional RepeatedStratifiedKFold and held-out-state results: runs/gap_real_quick_v4/repeated_cv_* and group_cv. Sex/age/race/BMI/education/income descriptive development groups: tables/gap_extension/development_subgroups.csv. Cohorts differ for complete-case analysis. Overlapping folds are dependent; variability is descriptive, with no IID significance claim. Subgroup sample thresholds30 and presence of all classes are required. No model-selection uncertainty correction or confirmatory fairness claims.
