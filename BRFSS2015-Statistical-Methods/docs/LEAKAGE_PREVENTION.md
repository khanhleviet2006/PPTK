# Leakage prevention and test access policy

1. Validate source identifiers and construct deterministic code mappings.
2. Save the untouched final test partition before learned preprocessing or feature selection.
3. Use training folds for imputation, scaling, one-hot encoding, supervised feature selection, resampling and fitting. The permutation selector uses an additional inner training/validation split. Stacking includes full pipelines as base estimators.
4. Use OOF predictions for threshold and candidate selection; interpret selected development scores as optimistic. No held-out test labels enter these decisions.
5. Hash fitted model and fixed logistic comparator before final access. One batch writes predictions, all metrics, calibration and subgroups. Interruption after access marks the test as accessed; automatic retry is blocked.
6. Checkpoints verify hashes and include code/config/source/package signatures. Changing a signature requires another output directory, not overwriting historical test evidence. This is an engineering safeguard, not permission to treat reused respondents as a new independent test after outcome-directed software/model changes.
7. Record exploratory full-cohort statistical inference separately. Because it can inform future prediction choices, planned prediction features and experiment grids are fixed here in advance. Any data-driven protocol amendment after viewing whole-cohort associations must be disclosed.

Duplicate respondents are rejected using state+SEQNO; identical predictor patterns in different respondents are counted, not automatically deleted. Processed datasets may lack respondent IDs, so their overlap and de-duplication limitations must be disclosed. No medical treatment/diabetes diagnosis fields are predictive inputs.
