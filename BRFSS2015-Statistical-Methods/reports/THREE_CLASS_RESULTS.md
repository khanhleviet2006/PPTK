# Three-class development results

Real CDC2015, n2000, two outer folds; excluded all old binary final-test IDs. Core DIABETE3 3/4/1 mapped0/1/2: no diabetes reported / reported borderline-prediabetes / reported diabetes. Class0 does not establish absence of prediabetes. No optional-module missing value is called negative.

| model | accuracy | balanced_accuracy | precision | sensitivity | f1 | macro_f1 | log_loss | class_0_sensitivity | class_0_specificity | class_1_sensitivity | class_1_specificity | class_2_sensitivity | class_2_specificity | roc_auc | pr_auc | brier | specificity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logistic | 0.847 | 0.39791 | 0.51472 | 0.39791 | 0.41444 | 0.41444 | 0.42197 | 0.96584 | 0.19536 | 0.02326 | 0.99796 | 0.20463 | 0.96611 | 0.77316 | 0.45896 | 0.22955 | 0.71981 |
| decision_tree | 0.836 | 0.3784 | 0.41429 | 0.3784 | 0.38362 | 0.38362 | 1.24465 | 0.9576 | 0.16556 | 0.0 | 1.0 | 0.17761 | 0.95635 | 0.6544 | 0.40019 | 0.2681 | 0.7073 |
| random_forest | 0.8505 | 0.34156 | 0.49602 | 0.34156 | 0.32359 | 0.32359 | 0.41135 | 0.99764 | 0.02318 | 0.0 | 1.0 | 0.02703 | 0.9977 | 0.77121 | 0.45866 | 0.22692 | 0.67363 |
| extra_trees | 0.8505 | 0.34374 | 0.48413 | 0.34374 | 0.32817 | 0.32817 | 0.41366 | 0.99647 | 0.0298 | 0.0 | 1.0 | 0.03475 | 0.99655 | 0.7679 | 0.4481 | 0.22895 | 0.67545 |

Exploratory development CV only. No new three-class final test was opened. Full per-fold probabilities, confusion matrices and config in runs/gap_real_three.
