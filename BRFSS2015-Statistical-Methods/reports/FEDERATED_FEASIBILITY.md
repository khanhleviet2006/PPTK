# Federated feasibility: simulated optimization only

Four artificial public-data clients,20 FedAvg rounds, centralized preprocessing on training only, simulated held-out development validation. No real institutions, secure aggregation, privacy attack resistance or differential privacy claim. Train/test contamination prevention differs from privacy protection.

| method | accuracy | balanced_accuracy | precision | sensitivity | f1 | macro_f1 | log_loss | class_0_sensitivity | class_0_specificity | class_1_sensitivity | class_1_specificity | roc_auc | pr_auc | brier | specificity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fedavg | 0.866 | 0.49885 | 0.0 | 0.0 | 0.0 | 0.46409 | 0.35662 | 0.9977 | 0.0 | 0.0 | 0.9977 | 0.73485 | 0.33685 | 0.10534 | 0.9977 |
| central | 0.866 | 0.49885 | 0.0 | 0.0 | 0.0 | 0.46409 | 0.35661 | 0.9977 | 0.0 | 0.0 | 0.9977 | 0.73485 | 0.3369 | 0.10534 | 0.9977 |

Feasible as a proof of concept; C20 remains PARTIALLY_ADDRESSED. Clinical/privacy effectiveness is not tested.
