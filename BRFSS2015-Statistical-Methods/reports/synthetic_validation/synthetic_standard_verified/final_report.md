# Synthetic validation report — not epidemiological evidence

## Abstract

This cross-sectional analysis investigates self-reported diabetes associations and fixed-protocol predictive classification. Estimates describe associations, not causal effects or future incident disease.

## Research questions and prespecified analysis

RQ1: adjusted associations using complex survey design. RQ2: training-only feature, imbalance and model comparisons. RQ3: balanced accuracy, sensitivity, calibration and discrimination versus a same-cohort logistic baseline. RQ4: subgroup and outcome/missingness sensitivity. Full estimands and hypotheses are in docs/RESEARCH_PROTOCOL.md.

## Data and cohort

Source records: 960. Eligible: 873. Complete cases: 659. Design strata: 120. Profile: standard. Source fingerprints and exact schema are in audit.json.

## Methods

CDC core DIABETE3=1 versus 3 is the primary contrast; pregnancy-only and borderline responses are excluded. Optional prediabetes ascertainment is not assumed complete. Survey point estimates use _LLCPWT and variance uses stratified _PSU score totals within _STSTR, without a finite population correction. Complete-case inference and median/mode sensitivity target different missing-data assumptions. Preprocessing and feature selection are fitted inside training folds. The final test set is accessed in one frozen-model batch.

## Weighted prevalence

| class | estimate | lower | upper | n |
| --- | --- | --- | --- | --- |
| 0.0 | 0.84011 | 0.8131 | 0.86387 | 873 |
| 1.0 | 0.15989 | 0.13613 | 0.1869 | 873 |

Weighted diabetes prevalence within this defined analysis domain was 15.99% (95% design CI 13.61% to 18.69%). This domain excludes unknown outcomes and may exclude borderline/pregnancy-only responses; it is not an unconditional whole-population estimate.

## Statistical associations

Adjusted OR, confidence limits, design-based p-values, and exploratory BH corrections: adjusted_or.csv. Multinomial RRR: multinomial_rrr.csv when completed. Univariate results: univariate.csv. Clinical interpretation must consider coding references, precision, multiplicity, selection, and reverse causation.

Prespecified illustrative contrasts are below; the complete coefficient table accompanies this report. OR/RRR compare coded levels with the first codebook category, holding included covariates fixed. BMI is per 10 kg/m²; no coefficient is a causal effect.

| term | OR | lower | upper | p |
| --- | --- | --- | --- | --- |
| _AGEG5YR_13 | 5.0211 | 1.47976 | 17.03747 | 0.00981 |
| SEX_2 | 0.80503 | 0.48523 | 1.3356 | 0.3999 |
| _BMI5_per_10 | 2.66503 | 1.58451 | 4.48236 | 0.00025 |
| INCOME2_8 | 0.50399 | 0.21964 | 1.15647 | 0.10554 |
| BPHIGH4_3 | 0.69367 | 0.33894 | 1.41962 | 0.31569 |
| TOLDHI2_2 | 0.84405 | 0.51614 | 1.38028 | 0.49808 |
| GENHLTH_5 | 0.64245 | 0.29513 | 1.39849 | 0.26388 |

## Model development

Development scores guided selection and threshold tuning; they are optimistic for the selected strategy. They are not final test performance. All candidates and skipped dependencies are in model_comparison.csv.

| model | selector | k | imbalance | cv_mean | threshold |
| --- | --- | --- | --- | --- | --- |
| decision_tree | original | 10 | none | 0.61037 | 0.2 |
| random_forest | original | 10 | none | 0.57063 | 0.2 |
| logistic | permutation | 10 | none | 0.56618 | 0.2 |
| logistic | tree | 20 | none | 0.54885 | 0.2 |
| logistic | permutation | 5 | none | 0.54783 | 0.2 |
| random_forest | original | 10 | random_under | 0.54584 | 0.5 |
| logistic | rfe | 20 | none | 0.54564 | 0.2 |
| logistic | rfe | 15 | none | 0.54282 | 0.2 |
| catboost | original | 10 | none | 0.54234 | 0.2 |
| logistic | permutation | 15 | none | 0.53931 | 0.2 |
| xgboost | original | 10 | none | 0.53813 | 0.3 |
| logistic | l1 | 10 | none | 0.53786 | 0.2 |
| random_forest | original | 10 | class_weight | 0.5361 | 0.4 |
| logistic | mutual_info | 20 | none | 0.53577 | 0.2 |
| gradient_boosting | original | 10 | none | 0.53536 | 0.2 |

## Predictive results

| metric | selected | baseline | CI_lower | CI_upper |
| --- | --- | --- | --- | --- |
| accuracy | 0.68571 | 0.84 | 0.61714 | 0.75429 |
| balanced_accuracy | 0.54913 | 0.51724 | 0.46 | 0.65334 |
| sensitivity | 0.34483 | 0.03448 | 0.18174 | 0.52193 |
| specificity | 0.75342 | 1.0 | 0.68387 | 0.82553 |
| precision | 0.21739 | 1.0 | 0.10635 | 0.34783 |
| f1 | 0.26667 | 0.06667 | 0.13558 | 0.39487 |
| roc_auc | 0.59152 | 0.55291 | 0.47804 | 0.70243 |
| pr_auc | 0.25781 | 0.29012 | 0.15885 | 0.40489 |
| brier | 0.15788 | 0.1395 | 0.1166 | 0.20137 |
| log_loss | 0.71014 | 0.47175 | 0.41848 | 1.21253 |

The frozen model was evaluated on 175 test respondents once. Balanced-accuracy difference versus the fixed same-cohort logistic comparator was 0.0319 (paired conditional bootstrap 95% interval -0.0548 to 0.1260). Intervals describe test respondents conditional on fixed fitted models; they do not include survey population or model-selection uncertainty. See final_metrics.json for all per-class errors, comparisons and weighted point estimates.

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
