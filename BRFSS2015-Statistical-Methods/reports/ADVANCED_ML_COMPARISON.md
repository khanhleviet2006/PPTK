# Advanced-model and nested-search comparison

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| model | selector | k | sampling | representation | calibration | missing | search | balanced_accuracy | sensitivity | specificity | roc_auc | pr_auc | brier | log_loss | macro_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logistic |  |  |  |  |  |  |  | 0.73547 | 0.80755 | 0.6634 | 0.80735 | 0.395 | 0.0982 | 0.32279 | 0.59321 |
| decision_tree |  |  |  |  |  |  |  | 0.7067 | 0.78113 | 0.63228 | 0.72403 | 0.27626 | 0.11351 | 0.71127 | 0.56607 |
| random_forest |  |  |  |  |  |  |  | 0.71657 | 0.87925 | 0.55389 | 0.81125 | 0.4037 | 0.09686 | 0.31756 | 0.53545 |
| extra_trees |  |  |  |  |  |  |  | 0.70109 | 0.70189 | 0.70029 | 0.79545 | 0.35653 | 0.09922 | 0.32488 | 0.59268 |
| knn |  |  |  |  |  |  |  | 0.67684 | 0.61132 | 0.74236 | 0.68654 | 0.23766 | 0.12033 | 2.30487 | 0.59738 |
| naive_bayes |  |  |  |  |  |  |  | 0.61018 | 0.94717 | 0.2732 | 0.70458 | 0.21967 | 0.64094 | 18.00292 | 0.35447 |
| gb |  |  |  |  |  |  |  | 0.71715 | 0.72075 | 0.71354 | 0.80309 | 0.3733 | 0.09839 | 0.32372 | 0.60672 |
| gradient_boosting |  |  |  |  |  |  |  | 0.70538 | 0.65283 | 0.75793 | 0.79329 | 0.37908 | 0.1028 | 0.34776 | 0.62015 |
| xgboost |  |  |  |  |  |  |  | 0.74439 | 0.84151 | 0.64726 | 0.80173 | 0.37116 | 0.09856 | 0.32217 | 0.58997 |
| lightgbm |  |  |  |  |  |  |  | 0.72695 | 0.72075 | 0.73314 | 0.79742 | 0.38799 | 0.09968 | 0.33129 | 0.62069 |
| catboost |  |  |  |  |  |  |  | 0.74124 | 0.84906 | 0.63343 | 0.81252 | 0.39969 | 0.09641 | 0.31587 | 0.58222 |
| logistic |  |  |  |  |  |  | True | 0.73759 | 0.79623 | 0.67896 | 0.80259 | 0.38489 | 0.09986 | 0.33001 | 0.60129 |
| random_forest |  |  |  |  |  |  | True | 0.72702 | 0.90189 | 0.55216 | 0.80982 | 0.39994 | 0.0973 | 0.318 | 0.53891 |
| xgboost |  |  |  |  |  |  | True | 0.70488 | 0.63396 | 0.77579 | 0.78516 | 0.35888 | 0.10461 | 0.35295 | 0.62792 |
| lightgbm |  |  |  |  |  |  | True | 0.72271 | 0.7434 | 0.70202 | 0.79883 | 0.38772 | 0.09942 | 0.32643 | 0.6044 |
| catboost |  |  |  |  |  |  | True | 0.73752 | 0.81509 | 0.65994 | 0.80299 | 0.37818 | 0.09799 | 0.32103 | 0.5926 |

Full settings, fold metrics, inner thresholds and selected-feature lists: runs/gap_real_quick_v4/experiments/*.json. RFECV/permutation use deterministic codebook encoding and fit imputation/scaling inside internal training folds; outer validation stays excluded. No claim of full-standard execution, stable feature discovery, a new algorithm or superiority to Chang.
