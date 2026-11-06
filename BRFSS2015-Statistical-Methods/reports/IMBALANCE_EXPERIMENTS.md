# Imbalance comparison

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| model | selector | k | sampling | representation | calibration | missing | search | balanced_accuracy | sensitivity | specificity | roc_auc | pr_auc | brier | log_loss | macro_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logistic |  |  | random_under |  |  |  |  | 0.71719 | 0.81132 | 0.62305 | 0.79692 | 0.37071 | 0.19412 | 0.58693 | 0.56678 |
| logistic |  |  | random_over |  |  |  |  | 0.737 | 0.8717 | 0.60231 | 0.8046 | 0.3843 | 0.16931 | 0.51298 | 0.56613 |
| logistic |  |  | smotenc |  |  |  |  | 0.71845 | 0.84151 | 0.59539 | 0.78735 | 0.35924 | 0.15672 | 0.48187 | 0.55501 |
| logistic |  |  |  |  |  |  |  | 0.72432 | 0.83019 | 0.61844 | 0.80666 | 0.38746 | 0.17165 | 0.51735 | 0.5679 |
| random_forest |  |  | none | continuous |  |  |  | 0.64133 | 0.71321 | 0.56945 | 0.69588 | 0.28434 | 0.10738 | 0.36587 | 0.51035 |
| xgboost |  |  | none | continuous |  |  |  | 0.6302 | 0.58491 | 0.6755 | 0.70805 | 0.2656 | 0.10838 | 0.36317 | 0.54615 |
| lightgbm |  |  | none | continuous |  |  |  | 0.62827 | 0.60755 | 0.64899 | 0.68324 | 0.24099 | 0.11457 | 0.3918 | 0.53532 |
| random_forest |  |  | smote | continuous |  |  |  | 0.63068 | 0.63774 | 0.62363 | 0.66437 | 0.23389 | 0.15098 | 0.46564 | 0.52691 |
| xgboost |  |  | smote | continuous |  |  |  | 0.60361 | 0.72075 | 0.48646 | 0.68199 | 0.23646 | 0.17746 | 0.52638 | 0.45993 |
| lightgbm |  |  | smote | continuous |  |  |  | 0.59013 | 0.86038 | 0.31988 | 0.67351 | 0.23061 | 0.14922 | 0.46109 | 0.37479 |
| random_forest |  |  | adasyn | continuous |  |  |  | 0.63375 | 0.64906 | 0.61844 | 0.66255 | 0.23082 | 0.15249 | 0.46943 | 0.52638 |
| xgboost |  |  | adasyn | continuous |  |  |  | 0.61204 | 0.7434 | 0.48069 | 0.68959 | 0.24047 | 0.17989 | 0.5299 | 0.4608 |
| lightgbm |  |  | adasyn | continuous |  |  |  | 0.59808 | 0.74717 | 0.44899 | 0.66443 | 0.22164 | 0.152 | 0.46911 | 0.44136 |

Full settings, fold metrics, inner thresholds and selected-feature lists: runs/gap_real_quick_v4/experiments/*.json. RFECV/permutation use deterministic codebook encoding and fit imputation/scaling inside internal training folds; outer validation stays excluded. No claim of full-standard execution, stable feature discovery, a new algorithm or superiority to Chang.
