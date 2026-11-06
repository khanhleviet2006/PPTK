# Ensemble comparison

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| model | selector | k | sampling | representation | calibration | missing | search | balanced_accuracy | sensitivity | specificity | roc_auc | pr_auc | brier | log_loss | macro_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adasyn_soft_voting |  |  |  |  |  |  |  | 0.63546 | 0.68302 | 0.5879 | 0.67965 | 0.23941 | 0.15609 | 0.47624 | 0.51518 |
| adasyn_stacking |  |  |  |  |  |  |  | 0.59893 | 0.82264 | 0.37522 | 0.67628 | 0.24673 | 0.1098 | 0.37017 | 0.40669 |
| soft_voting |  |  |  |  |  |  |  | 0.75335 | 0.84906 | 0.65764 | 0.81848 | 0.42276 | 0.09524 | 0.31016 | 0.59885 |
| hard_voting |  |  |  |  |  |  |  | 0.55346 | 0.12075 | 0.98617 | 0.55346 | 0.1855 | 0.1285 | 4.63161 | 0.56476 |
| weighted_voting |  |  |  |  |  |  |  | 0.74858 | 0.84528 | 0.65187 | 0.81873 | 0.4213 | 0.09529 | 0.30982 | 0.594 |
| stacking |  |  |  |  |  |  |  | 0.74095 | 0.84906 | 0.63285 | 0.81319 | 0.41767 | 0.09719 | 0.32574 | 0.58182 |
| feature_ensemble |  |  |  |  |  |  |  | 0.73789 | 0.83774 | 0.63804 | 0.80903 | 0.40994 | 0.09616 | 0.31513 | 0.58281 |
| family_ensemble |  |  |  |  |  |  |  | 0.73172 | 0.76604 | 0.69741 | 0.81703 | 0.41919 | 0.09565 | 0.31236 | 0.60683 |

Full settings, fold metrics, inner thresholds and selected-feature lists: runs/gap_real_quick_v4/experiments/*.json. RFECV/permutation use deterministic codebook encoding and fit imputation/scaling inside internal training folds; outer validation stays excluded. No claim of full-standard execution, stable feature discovery, a new algorithm or superiority to Chang.
