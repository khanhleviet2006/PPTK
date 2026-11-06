# Interpretation of frozen original-data outputs

These are interpretations of executed results, not a new model-selection step.

The primary domain includes 422,558 respondents from 50 states/DC with an explicit core diabetes yes/no answer. Weighted prevalence is 10.71% (95% design CI 10.53%–10.88%). This is conditional on the stated exclusions, not unconditional prevalence across every original record. The adjusted complete-case model uses 243,529 respondents, making missing-data selection a substantive limitation.

BMI was positively associated with reported diabetes: adjusted OR 1.875 per 10 kg/m² (95% design CI 1.794–1.961). Deterministic-imputation sensitivity gave OR 1.832 (1.772–1.893); including borderline diagnoses as non-diabetes gave OR 1.838 (1.760–1.920). These analyses agree in direction but do not establish MAR, eliminate confounding, or identify a causal effect. The core-three multinomial model gave BMI RRR 1.643 (1.519–1.778) for reported borderline/prediabetes versus no diabetes reported, and 1.889 (1.807–1.974) for diabetes versus no diabetes reported. These are relative category-probability ratios, not incidence risk ratios.

Training CV selected class-weighted logistic regression at threshold 0.40. Its test balanced accuracy was 75.11%, sensitivity 85.51%, specificity 64.71%, precision 27.00%, ROC-AUC 0.8307 and PR-AUC 0.4129. Accuracy was 67.47%. The fixed unweighted logistic comparator at threshold 0.50 had balanced accuracy 57.86%, sensitivity 17.92%, specificity 97.79%, accuracy 87.21% and ROC-AUC 0.8296.

The balanced-accuracy difference was 0.1725 (paired conditional bootstrap 95% interval 0.1684–0.1758). This is primarily an operating-point tradeoff, not a large gain in ranking discrimination. Calibration worsened: Brier score 0.1728 versus 0.0936 and log loss 0.5143 versus 0.3048. The selected model therefore does not provide better calibrated individual probabilities. The 82.26% accuracy target was not achieved. Recalibration or revised thresholds require training-based development in a separately documented future experiment, not choosing settings from this test result.

Recorded-sex subgroup balanced accuracy was 74.73% for male and 75.38% for female respondents. These descriptive values alone establish neither fairness nor equivalence. Race/age subgroup estimates and intervals are in tables/subgroups.csv. All predictive findings are conditional on the quick training budget and same-year sample distribution.

Prediction improved balanced accuracy and minority detection relative to the fixed same-cohort comparator, with substantial losses in other endpoints. Methodological validity comes from preserved survey design, fold-local preprocessing and a protected final test. Interpretability comes from association estimates and training-only permutation importance; importance is not causal. Epidemiological findings remain cross-sectional associations requiring missing-data and functional-form review before a publication-level novelty claim.

Full real standard/extended experiments, faithful processed-cohort reproduction, temporal/external validation and actual Colab runtime execution remain unexecuted. Synthetic experiments validate implementation only.

## Research-gap audit qualification

See [RESEARCH_GAP_AUDIT.md](RESEARCH_GAP_AUDIT.md). The observed gain compares two operating policies with different class weights and thresholds, rather than isolating a new model effect. A threshold-matched unweighted comparator has not been evaluated in the final batch. No such comparison or new threshold selection was added during this audit. Macro-F1 was 0.592895 versus 0.600351, despite improved positive-class F1. Added algorithms, generic permutation importance and synthetic top-k execution do not close the paper-specific SHAP, ADASYN, faithful reproduction or external-validation directions.
