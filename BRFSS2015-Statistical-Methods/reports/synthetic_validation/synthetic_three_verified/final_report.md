# Synthetic validation report — not epidemiological evidence

## Abstract

This cross-sectional analysis investigates self-reported diabetes associations and fixed-protocol predictive classification. Estimates describe associations, not causal effects or future incident disease.

## Research questions and prespecified analysis

RQ1: adjusted associations using complex survey design. RQ2: training-only feature, imbalance and model comparisons. RQ3: balanced accuracy, sensitivity, calibration and discrimination versus a same-cohort logistic baseline. RQ4: subgroup and outcome/missingness sensitivity. Full estimands and hypotheses are in docs/RESEARCH_PROTOCOL.md.

## Data and cohort

Source records: 1,600. Eligible: 1,600. Complete cases: 1,172. Design strata: 200. Profile: quick. Source fingerprints and exact schema are in audit.json.

## Methods

CDC core DIABETE3=1 versus 3 is the primary contrast; pregnancy-only and borderline responses are excluded. Optional prediabetes ascertainment is not assumed complete. Survey point estimates use _LLCPWT and variance uses stratified _PSU score totals within _STSTR, without a finite population correction. Complete-case inference and median/mode sensitivity target different missing-data assumptions. Preprocessing and feature selection are fitted inside training folds. The final test set is accessed in one frozen-model batch.

## Weighted prevalence

| class | estimate | lower | upper | n |
| --- | --- | --- | --- | --- |
| 0.0 | 0.78247 | 0.75918 | 0.8041 | 1600 |
| 1.0 | 0.08202 | 0.0685 | 0.09794 | 1600 |
| 2.0 | 0.1355 | 0.11763 | 0.15561 | 1600 |

Weighted diabetes prevalence within this defined analysis domain was 13.55% (95% design CI 11.76% to 15.56%). This domain excludes unknown outcomes and may exclude borderline/pregnancy-only responses; it is not an unconditional whole-population estimate.

## Statistical associations

Adjusted OR, confidence limits, design-based p-values, and exploratory BH corrections: adjusted_or.csv. Multinomial RRR: multinomial_rrr.csv when completed. Univariate results: univariate.csv. Clinical interpretation must consider coding references, precision, multiplicity, selection, and reverse causation.

Prespecified illustrative contrasts are below; the complete coefficient table accompanies this report. OR/RRR compare coded levels with the first codebook category, holding included covariates fixed. BMI is per 10 kg/m²; no coefficient is a causal effect.

| term | RRR | lower | upper | p |
| --- | --- | --- | --- | --- |
| class_1_vs_0:_AGEG5YR_13 | 0.29318 | 0.06747 | 1.27392 | 0.10143 |
| class_1_vs_0:SEX_2 | 0.8887 | 0.56082 | 1.40829 | 0.61478 |
| class_1_vs_0:_BMI5_per_10 | 1.41451 | 0.83696 | 2.39061 | 0.19475 |
| class_1_vs_0:INCOME2_8 | 0.36539 | 0.1325 | 1.00758 | 0.05172 |
| class_1_vs_0:BPHIGH4_3 | 0.68441 | 0.35931 | 1.30364 | 0.24813 |
| class_1_vs_0:TOLDHI2_2 | 1.12059 | 0.70686 | 1.77648 | 0.62755 |
| class_1_vs_0:GENHLTH_5 | 1.52974 | 0.72185 | 3.2418 | 0.26662 |
| class_2_vs_0:_AGEG5YR_13 | 3.1697 | 1.15519 | 8.69722 | 0.02517 |
| class_2_vs_0:SEX_2 | 0.85611 | 0.56971 | 1.28648 | 0.45391 |
| class_2_vs_0:_BMI5_per_10 | 2.0705 | 1.38642 | 3.0921 | 0.0004 |
| class_2_vs_0:INCOME2_8 | 1.62255 | 0.70317 | 3.74398 | 0.25596 |
| class_2_vs_0:BPHIGH4_3 | 0.88296 | 0.5003 | 1.55831 | 0.667 |
| class_2_vs_0:TOLDHI2_2 | 1.19691 | 0.79516 | 1.80164 | 0.38825 |
| class_2_vs_0:GENHLTH_5 | 0.96242 | 0.53941 | 1.71715 | 0.89662 |

## Model development

Development scores guided selection and threshold tuning; they are optimistic for the selected strategy. They are not final test performance. All candidates and skipped dependencies are in model_comparison.csv.

| model | selector | k | imbalance | cv_mean | threshold |
| --- | --- | --- | --- | --- | --- |
| logistic | original | 10 | random_under | 0.37372 | 0.5 |
| logistic | original | 10 | class_weight | 0.37337 | 0.5 |
| logistic | original | 10 | smote | 0.36063 | 0.5 |
| xgboost | original | 10 | none | 0.33611 | 0.5 |
| gradient_boosting | original | 10 | none | 0.33359 | 0.5 |
| logistic | mutual_info | 10 | none | 0.33333 | 0.5 |
| feature_ensemble | original | 10 | none | 0.33333 | 0.5 |
| extra_trees | original | 10 | none | 0.33333 | 0.5 |
| random_forest | original | 10 | none | 0.33333 | 0.5 |
| logistic | tree | 10 | none | 0.33333 | 0.5 |
| logistic | l1 | 10 | none | 0.33333 | 0.5 |
| catboost | original | 10 | none | 0.33333 | 0.5 |
| stacking | original | 10 | none | 0.33333 | 0.5 |
| soft_voting | original | 10 | none | 0.33234 | 0.5 |
| lightgbm | original | 10 | none | 0.33213 | 0.5 |

## Predictive results

| metric | selected | baseline | CI_lower | CI_upper |
| --- | --- | --- | --- | --- |
| accuracy | 0.32188 | 0.78438 | 0.265 | 0.37203 |
| balanced_accuracy | 0.35798 | 0.33201 | 0.25996 | 0.43753 |
| sensitivity | 0.35798 | 0.33201 | 0.25996 | 0.43753 |
| specificity | 0.66495 | 0.66924 | 0.62309 | 0.69601 |
| precision | 0.33935 | 0.2631 | 0.29886 | 0.38029 |
| f1 | 0.26699 | 0.29357 | 0.21594 | 0.31255 |
| roc_auc | 0.50373 | 0.56063 | 0.4363 | 0.56042 |
| pr_auc | 0.33956 | 0.3658 | 0.31984 | 0.38448 |
| brier | 0.82976 | 0.37005 | 0.77981 | 0.89367 |
| log_loss | 1.40514 | 0.69302 | 1.3161 | 1.52772 |

The frozen model was evaluated on 320 test respondents once. Balanced-accuracy difference versus the fixed same-cohort logistic comparator was 0.0260 (paired conditional bootstrap 95% interval -0.0734 to 0.1055). Intervals describe test respondents conditional on fixed fitted models; they do not include survey population or model-selection uncertainty. See final_metrics.json for all per-class errors, comparisons and weighted point estimates.

## Research gaps and interpretation

The gap matrix distinguishes inspected evidence from hypotheses. Chang et al. (2022), DOI 10.1016/j.health.2022.100118, reported 82.26% accuracy; our cohort/outcome and evaluation may differ. A higher point estimate here does not establish improvement over that publication. The implemented comparison estimates improvement over a prespecified logistic model on identical test respondents. Feature importance measures predictive utility, not causal contribution. Prediction, methodological validity, interpretability, and epidemiological evidence are separate contributions.

## Sensitivity and generalizability

See sensitivity_or.csv, borderline_sensitivity_or.csv, multinomial_rrr.csv, and subgroups.csv. Missing outputs are unavailable rather than negative findings. Core-question borderline status is an imperfect three-category self-report; module analyses require geographic/version eligibility and appropriate weights. External or temporal validation has not been performed.

## Limitations

Self-reported cross-sectional data cannot distinguish all diabetes types, verify biological disease, or determine temporal direction. Complete-case inference may be selected. Deterministic imputation sensitivity is not multiple imputation. Calibrated weights are treated as fixed in the with-replacement linearization. Predictive bootstrap intervals are conditional respondent intervals, not full survey population intervals or uncertainty over model selection. Small demographic groups may be unstable. Quick mode caps training size and is a computational validation rather than a full experimental study.

## Reproducibility

Source hashes, code/config signature, package versions, split IDs/checksum, CV indices, experiment history, frozen model checksum, test-access ledger and atomic checkpoints accompany this report. See execution_status.json; actual Google Colab execution remains unverified.

## Conclusion

All numerical results in this report are synthetic software validation. They provide no evidence about diabetes prevalence, real-world associations, or predictive benefit.

## References

CDC BRFSS 2015 data and codebook: https://www.cdc.gov/brfss/annual_data/annual_2015.html

Chang V, Ganatra MA, Hall K, Golightly L, Xu Q (2022). An assessment of machine learning models and algorithms for early prediction and diagnosis of diabetes using health indicators. Healthcare Analytics 2:100118. https://doi.org/10.1016/j.health.2022.100118
