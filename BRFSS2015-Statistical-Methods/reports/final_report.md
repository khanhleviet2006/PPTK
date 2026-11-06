# BRFSS 2015 Statistical Methods: empirical report draft

## Abstract

This cross-sectional analysis investigates self-reported diabetes associations and fixed-protocol predictive classification. Estimates describe associations, not causal effects or future incident disease.

## Research questions and prespecified analysis

RQ1: adjusted associations using complex survey design. RQ2: training-only feature, imbalance and model comparisons. RQ3: balanced accuracy, sensitivity, calibration and discrimination versus a same-cohort logistic baseline. RQ4: subgroup and outcome/missingness sensitivity. Full estimands and hypotheses are in docs/RESEARCH_PROTOCOL.md.

## Data and cohort

Source records: 441,456. Eligible: 422,558. Complete cases: 243,529. Design strata: 1,306. Profile: quick. Source fingerprints and exact schema are in audit.json.

## Methods

CDC core DIABETE3=1 versus 3 is the primary contrast; pregnancy-only and borderline responses are excluded. Optional prediabetes ascertainment is not assumed complete. Survey point estimates use _LLCPWT and variance uses stratified _PSU score totals within _STSTR, without a finite population correction. Complete-case inference and median/mode sensitivity target different missing-data assumptions. Preprocessing and feature selection are fitted inside training folds. The final test set is accessed in one frozen-model batch.

## Weighted prevalence

| class | estimate | lower | upper | n |
| --- | --- | --- | --- | --- |
| 0.0 | 0.89295 | 0.89117 | 0.8947 | 422558 |
| 1.0 | 0.10705 | 0.1053 | 0.10883 | 422558 |

Weighted diabetes prevalence within this defined analysis domain was 10.71% (95% design CI 10.53% to 10.88%). This domain excludes unknown outcomes and may exclude borderline/pregnancy-only responses; it is not an unconditional whole-population estimate.

## Statistical associations

P-values below are rounded to five decimal places; entries shown as 0.0 indicate rounding, not an exactly zero probability. Full precision is retained in tables/adjusted_or.csv. See [the interpretation addendum](RESULTS_INTERPRETATION.md) for sensitivity findings and performance tradeoffs.

Adjusted OR, confidence limits, design-based p-values, and exploratory BH corrections: adjusted_or.csv. Multinomial RRR: multinomial_rrr.csv when completed. Univariate results: univariate.csv. Clinical interpretation must consider coding references, precision, multiplicity, selection, and reverse causation.

Prespecified illustrative contrasts are below; the complete coefficient table accompanies this report. OR/RRR compare coded levels with the first codebook category, holding included covariates fixed. BMI is per 10 kg/m²; no coefficient is a causal effect.

| term | OR | lower | upper | p |
| --- | --- | --- | --- | --- |
| _AGEG5YR_13 | 7.13345 | 4.82473 | 10.54691 | 0.0 |
| SEX_2 | 0.74509 | 0.70333 | 0.78933 | 0.0 |
| _BMI5_per_10 | 1.87543 | 1.79359 | 1.96101 | 0.0 |
| INCOME2_8 | 0.7176 | 0.62063 | 0.82974 | 1e-05 |
| BPHIGH4_3 | 0.48937 | 0.45932 | 0.5214 | 0.0 |
| TOLDHI2_2 | 0.53889 | 0.5092 | 0.57032 | 0.0 |
| GENHLTH_5 | 8.40663 | 7.02499 | 10.06002 | 0.0 |

## Model development

Development scores guided selection and threshold tuning; they are optimistic for the selected strategy. They are not final test performance. All candidates and skipped dependencies are in model_comparison.csv.

| model | selector | k | imbalance | cv_mean | threshold |
| --- | --- | --- | --- | --- | --- |
| logistic | original | 10 | class_weight | 0.75059 | 0.4 |
| logistic | original | 10 | random_under | 0.74284 | 0.5 |
| xgboost | original | 10 | none | 0.73136 | 0.2 |
| extra_trees | original | 10 | none | 0.72948 | 0.2 |
| random_forest | original | 10 | none | 0.72834 | 0.2 |
| logistic | original | 10 | smote | 0.72727 | 0.3 |
| catboost | original | 10 | none | 0.72503 | 0.2 |
| feature_ensemble | original | 10 | none | 0.72456 | 0.2 |
| soft_voting | original | 10 | none | 0.72314 | 0.2 |
| lightgbm | original | 10 | none | 0.72057 | 0.2 |
| logistic | original | 10 | none | 0.71974 | 0.2 |
| logistic | mutual_info | 10 | none | 0.71673 | 0.2 |
| gradient_boosting | original | 10 | none | 0.716 | 0.2 |
| logistic | tree | 10 | none | 0.71209 | 0.2 |
| stacking | original | 10 | none | 0.70311 | 0.2 |

## Predictive results

| metric | selected | baseline | CI_lower | CI_upper |
| --- | --- | --- | --- | --- |
| accuracy | 0.67466 | 0.87215 | 0.67138 | 0.6779 |
| balanced_accuracy | 0.7511 | 0.57858 | 0.74773 | 0.75505 |
| sensitivity | 0.85509 | 0.17922 | 0.84901 | 0.86078 |
| specificity | 0.64712 | 0.97793 | 0.64306 | 0.65061 |
| precision | 0.27003 | 0.55353 | 0.26632 | 0.27434 |
| f1 | 0.41045 | 0.27077 | 0.40593 | 0.41536 |
| roc_auc | 0.83068 | 0.82956 | 0.82778 | 0.83386 |
| pr_auc | 0.41289 | 0.41485 | 0.40481 | 0.42215 |
| brier | 0.17277 | 0.09363 | 0.17153 | 0.17404 |
| log_loss | 0.51427 | 0.30477 | 0.51079 | 0.51782 |

The frozen model was evaluated on 84,512 test respondents once. Balanced-accuracy difference versus the fixed same-cohort logistic comparator was 0.1725 (paired conditional bootstrap 95% interval 0.1684 to 0.1758). Intervals describe test respondents conditional on fixed fitted models; they do not include survey population or model-selection uncertainty. See final_metrics.json for all per-class errors, comparisons and weighted point estimates.

## Research gaps and interpretation

The [full research-gap audit](RESEARCH_GAP_AUDIT.md) links 21 claims/directions to the original Chang PDF, exact pages, implemented code and frozen empirical outputs. It confirms reporting ambiguities in cohort/label (p.4 and p.13), and author-proposed CV/SHAP/ADASYN-ensemble extensions (pp.12–13). It rejects claims that Chang used accuracy alone or had no 80:20 holdout. Chang already used SMOTE, PCA, sensitivity and RF. Train/test contamination remains a HYPOTHESIS because §3.3 p.4 instructs partitioning first while other descriptions omit or narrate the split differently.

Only project-scoped CV/selection traceability, conditional paired uncertainty, and original-data survey inference are addressed within stated limits. They do not establish that the paper's workflow was repaired, faithfully reproduced or outperformed. The frozen result compares a class-weighted LR policy at threshold 0.40 against an unweighted LR at 0.50, so the BA gain cannot be attributed separately to weighting, threshold optimization or a new classifier. ROC-AUC increased only about 0.001115; calibration and macro-F1 worsened. Ensembles did not win real-data training CV; unselected ensembles were not evaluated on final test. Full real-data top-k comparisons, SHAP, ADASYN ensembles and external validation remain unexecuted.

Chang et al. (2022), DOI 10.1016/j.health.2022.100118, reported RF accuracy 82.26%; cohort/outcome/protocol incompatibility prevents a direct superiority claim. Feature importance is not causal evidence. The audit is an editorial/evidence update: model/config/source, splits, predictions, frozen metrics and the evaluation ledger are unchanged, and no test-driven selection or re-evaluation occurred. See [the detailed evidence CSV](research_gap_evidence.csv).

## Sensitivity and generalizability

See sensitivity_or.csv, borderline_sensitivity_or.csv, multinomial_rrr.csv, and subgroups.csv. Missing outputs are unavailable rather than negative findings. Core-question borderline status is an imperfect three-category self-report; module analyses require geographic/version eligibility and appropriate weights. External or temporal validation has not been performed.

## Limitations

Self-reported cross-sectional data cannot distinguish all diabetes types, verify biological disease, or determine temporal direction. Complete-case inference may be selected. Deterministic imputation sensitivity is not multiple imputation. Calibrated weights are treated as fixed in the with-replacement linearization. Predictive bootstrap intervals are conditional respondent intervals, not full survey population intervals or uncertainty over model selection. Small demographic groups may be unstable. Quick mode caps training size and is a computational validation rather than a full experimental study.

## Reproducibility

Source hashes, code/config signature, package versions, split IDs/checksum, CV indices, experiment history, frozen model checksum, test-access ledger and atomic checkpoints accompany this report. See execution_status.json; actual Google Colab execution remains unverified.

## Conclusion

The paired balanced-accuracy interval excludes zero. The executed quick profile supports the reported same-cohort comparison under this protocol; it does not establish superiority to a different published cohort or clinical diagnostic utility. Associations remain cross-sectional and require interpretation alongside outcome coding, missingness and sensitivity tables.

## References

CDC BRFSS 2015 data and codebook: https://www.cdc.gov/brfss/annual_data/annual_2015.html

Chang V, Ganatra MA, Hall K, Golightly L, Xu Q (2022). An assessment of machine learning models and algorithms for early prediction and diagnosis of diabetes using health indicators. Healthcare Analytics 2:100118. https://doi.org/10.1016/j.health.2022.100118


## Post-audit extension

The historical results above remain unchanged. New development and temporal evidence is in [FINAL_RESEARCH_REPORT.md](FINAL_RESEARCH_REPORT.md), [RESEARCH_GAP_RESULTS.md](RESEARCH_GAP_RESULTS.md) and [UNFINISHED_WORK.md](UNFINISHED_WORK.md). These tracks do not re-evaluate the old2015 test or establish a faithful Chang comparison.
