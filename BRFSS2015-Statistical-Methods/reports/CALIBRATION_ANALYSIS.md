# Calibration and missing-data comparison

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| model | selector | k | sampling | representation | calibration | missing | search | balanced_accuracy | sensitivity | specificity | roc_auc | pr_auc | brier | log_loss | macro_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logistic |  |  |  |  |  |  |  | 0.73547 | 0.80755 | 0.6634 | 0.80735 | 0.395 | 0.0982 | 0.32279 | 0.59321 |
| logistic |  |  |  |  |  | indicators |  | 0.7414 | 0.81132 | 0.67147 | 0.81067 | 0.39659 | 0.09791 | 0.3219 | 0.59968 |
| logistic |  |  |  |  |  | iterative |  | 0.73736 | 0.81132 | 0.6634 | 0.80728 | 0.3948 | 0.09828 | 0.32351 | 0.5941 |
| logistic |  |  |  |  | sigmoid |  |  | 0.72068 | 0.90189 | 0.53948 | 0.8044 | 0.40158 | 0.0979 | 0.32385 | 0.53048 |
| logistic |  |  |  |  | isotonic |  |  | 0.72595 | 0.92453 | 0.52738 | 0.80405 | 0.39852 | 0.09672 | 0.35094 | 0.52691 |

Full settings, fold metrics, inner thresholds and selected-feature lists: runs/gap_real_quick_v4/experiments/*.json. RFECV/permutation use deterministic codebook encoding and fit imputation/scaling inside internal training folds; outer validation stays excluded. No claim of full-standard execution, stable feature discovery, a new algorithm or superiority to Chang.
