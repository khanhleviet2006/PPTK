# Feature-selection comparison

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| model | selector | k | sampling | representation | calibration | missing | search | balanced_accuracy | sensitivity | specificity | roc_auc | pr_auc | brier | log_loss | macro_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logistic | pca | 5.0 |  |  |  |  |  | 0.70183 | 0.78868 | 0.61499 | 0.78013 | 0.34473 | 0.10148 | 0.33903 | 0.55635 |
| logistic | pca | 10.0 |  |  |  |  |  | 0.74279 | 0.83774 | 0.64784 | 0.80163 | 0.37801 | 0.09783 | 0.32653 | 0.5895 |
| logistic | pca | 15.0 |  |  |  |  |  | 0.74525 | 0.84151 | 0.64899 | 0.80669 | 0.39009 | 0.09722 | 0.32302 | 0.59116 |
| logistic | pca | 20.0 |  |  |  |  |  | 0.74231 | 0.82642 | 0.65821 | 0.80559 | 0.39084 | 0.09737 | 0.32332 | 0.59404 |
| logistic | mutual_info | 5.0 |  |  |  |  |  | 0.71074 | 0.82264 | 0.59885 | 0.76538 | 0.31527 | 0.10242 | 0.34473 | 0.55321 |
| logistic | mutual_info | 10.0 |  |  |  |  |  | 0.72264 | 0.80377 | 0.6415 | 0.77705 | 0.35614 | 0.09994 | 0.33597 | 0.57743 |
| logistic | mutual_info | 15.0 |  |  |  |  |  | 0.72334 | 0.8 | 0.64669 | 0.78617 | 0.36085 | 0.09984 | 0.33178 | 0.58006 |
| logistic | mutual_info | 20.0 |  |  |  |  |  | 0.7181 | 0.78491 | 0.6513 | 0.78914 | 0.36637 | 0.10008 | 0.33166 | 0.57967 |
| logistic | selectkbest | 5.0 |  |  |  |  |  | 0.7256 | 0.82642 | 0.62478 | 0.77553 | 0.34429 | 0.1009 | 0.33429 | 0.57131 |
| logistic | selectkbest | 10.0 |  |  |  |  |  | 0.72827 | 0.80755 | 0.64899 | 0.7933 | 0.36651 | 0.09912 | 0.32642 | 0.58337 |
| logistic | selectkbest | 15.0 |  |  |  |  |  | 0.72725 | 0.80377 | 0.65072 | 0.80017 | 0.36609 | 0.099 | 0.32369 | 0.58367 |
| logistic | selectkbest | 20.0 |  |  |  |  |  | 0.73464 | 0.81509 | 0.65418 | 0.80598 | 0.37426 | 0.09847 | 0.32069 | 0.58865 |
| logistic | l1 | 5.0 |  |  |  |  |  | 0.67545 | 0.78491 | 0.56599 | 0.72328 | 0.24279 | 0.10679 | 0.35439 | 0.52366 |
| logistic | l1 | 10.0 |  |  |  |  |  | 0.72156 | 0.82642 | 0.61671 | 0.77859 | 0.32104 | 0.10267 | 0.33507 | 0.56591 |
| logistic | l1 | 15.0 |  |  |  |  |  | 0.73212 | 0.83774 | 0.62651 | 0.80087 | 0.35534 | 0.09976 | 0.32373 | 0.575 |
| logistic | l1 | 20.0 |  |  |  |  |  | 0.73584 | 0.83019 | 0.6415 | 0.80874 | 0.37612 | 0.09857 | 0.31942 | 0.58346 |
| logistic | rfe | 5.0 |  |  |  |  |  | 0.69669 | 0.76226 | 0.63112 | 0.73185 | 0.25959 | 0.10557 | 0.35033 | 0.56097 |
| logistic | rfe | 10.0 |  |  |  |  |  | 0.68261 | 0.65283 | 0.71239 | 0.74666 | 0.27864 | 0.10485 | 0.34528 | 0.58816 |
| logistic | rfe | 15.0 |  |  |  |  |  | 0.69193 | 0.75849 | 0.62536 | 0.76267 | 0.32186 | 0.10346 | 0.34058 | 0.55632 |
| logistic | rfe | 20.0 |  |  |  |  |  | 0.71842 | 0.79245 | 0.64438 | 0.79527 | 0.3664 | 0.09985 | 0.32678 | 0.57676 |
| logistic | rf | 5.0 |  |  |  |  |  | 0.68576 | 0.68679 | 0.68473 | 0.76481 | 0.31403 | 0.10343 | 0.34196 | 0.57831 |
| logistic | rf | 10.0 |  |  |  |  |  | 0.72948 | 0.82264 | 0.63631 | 0.78121 | 0.3522 | 0.10035 | 0.33598 | 0.57823 |
| logistic | rf | 15.0 |  |  |  |  |  | 0.73595 | 0.81887 | 0.65303 | 0.78653 | 0.36605 | 0.10048 | 0.33416 | 0.58873 |
| logistic | rf | 20.0 |  |  |  |  |  | 0.73521 | 0.81509 | 0.65533 | 0.79378 | 0.38148 | 0.0992 | 0.32978 | 0.58944 |
| logistic | xgb | 5.0 |  |  |  |  |  | 0.69997 | 0.75094 | 0.64899 | 0.74748 | 0.32914 | 0.10291 | 0.34314 | 0.57016 |
| logistic | xgb | 10.0 |  |  |  |  |  | 0.7196 | 0.8 | 0.63919 | 0.7809 | 0.35833 | 0.10056 | 0.33142 | 0.57501 |
| logistic | xgb | 15.0 |  |  |  |  |  | 0.72271 | 0.78491 | 0.66052 | 0.79086 | 0.36122 | 0.09988 | 0.3286 | 0.58592 |
| logistic | xgb | 20.0 |  |  |  |  |  | 0.73157 | 0.80377 | 0.65937 | 0.79594 | 0.37422 | 0.09965 | 0.32642 | 0.58956 |
| logistic | permutation | 5.0 |  |  |  |  |  | 0.67332 | 0.75472 | 0.59193 | 0.71968 | 0.26326 | 0.1069 | 0.35732 | 0.53379 |
| logistic | permutation | 10.0 |  |  |  |  |  | 0.69649 | 0.78491 | 0.60807 | 0.75376 | 0.29744 | 0.10448 | 0.34432 | 0.55096 |
| logistic | permutation | 15.0 |  |  |  |  |  | 0.72502 | 0.82642 | 0.62363 | 0.77778 | 0.34426 | 0.10119 | 0.33357 | 0.57054 |
| logistic | permutation | 20.0 |  |  |  |  |  | 0.73506 | 0.85283 | 0.61729 | 0.79188 | 0.34381 | 0.10077 | 0.32807 | 0.57212 |
| logistic | shap | 5.0 |  |  |  |  |  | 0.6958 | 0.75472 | 0.63689 | 0.74724 | 0.28777 | 0.10406 | 0.34523 | 0.56303 |
| logistic | shap | 10.0 |  |  |  |  |  | 0.72138 | 0.81509 | 0.62767 | 0.76945 | 0.31535 | 0.10308 | 0.33826 | 0.57071 |
| logistic | shap | 15.0 |  |  |  |  |  | 0.73451 | 0.81887 | 0.65014 | 0.79963 | 0.37894 | 0.09864 | 0.32316 | 0.58676 |
| logistic | shap | 20.0 |  |  |  |  |  | 0.73796 | 0.81887 | 0.65706 | 0.80241 | 0.38356 | 0.09838 | 0.32175 | 0.5915 |
| logistic | rfecv |  |  |  |  |  |  | 0.70871 | 0.6566 | 0.76081 | 0.80053 | 0.38532 | 0.0997 | 0.33318 | 0.62333 |

Full settings, fold metrics, inner thresholds and selected-feature lists: runs/gap_real_quick_v4/experiments/*.json. RFECV/permutation use deterministic codebook encoding and fit imputation/scaling inside internal training folds; outer validation stays excluded. No claim of full-standard execution, stable feature discovery, a new algorithm or superiority to Chang.
