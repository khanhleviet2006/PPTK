## Title

BRFSS2015 Statistical Methods: design-based inference and post-audit exploratory prediction with temporal validation

## Abstract

Original inference and protected2015 quick findings were preserved. An extension executed78 binary configurations and four three-class models on development-only data, plus a separately frozen14-variable temporal model evaluated on5000 BRFSS2017 respondents. Findings show operating-point and calibration tradeoffs; no faithful paper superiority claim.

## Introduction

Self-reported diabetes surveillance supports cross-sectional association and classification, not causal or incidence claims.

## Literature review

# Targeted literature review, 2026-11-06

This is a targeted evidence review, not a PRISMA systematic review. Searches used public web search/publisher records for 'Chang 2022 diabetes BRFSS 2015 82.26', exact DOI 10.1016/j.health.2022.100118, 'BRFSS2015 class imbalanced 100297', and 'Detecting High-Risk Factors 2015 253680'. A search result's absence is not evidence that a method was absent from a paper.

Chang V, Ganatra MA, Hall K, Golightly L, Xu QA. An assessment of machine learning models and algorithms for early prediction and diagnosis of diabetes using health indicators. Healthcare Analytics 2 (2022), 100118. DOI https://doi.org/10.1016/j.health.2022.100118. The original review used indexed publisher text. The subsequent full-PDF audit retrieved the author-posted 14-page typeset article, verified identity on page 1, and matched 22 short excerpts to their actual PDF/printed pages. The preserved source and its SHA256 are documented in [RESEARCH_GAP_AUDIT.md](../reports/RESEARCH_GAP_AUDIT.md). Page numbers below refer to that verified PDF, not inferred HTML pagination.

Section 3.1 (p.4) contains inconsistent cohort-size descriptions (70,692 and 253,680). Its target-label description (p.4) and Appendix Table A.1 (p.13) differ in the treatment/naming of prediabetes. These are verified reporting ambiguities; the executed cohort and label still cannot be reconstructed faithfully. Data availability on p.13 also states confidentiality despite the Kaggle link on p.4. Original-data inference in our project does not resolve these provenance questions for Chang.

The correct preprocessing section is **3.3**, not 3.2; section 3.2 is EDA. Section 3.3 (p.4) explicitly describes an 80:20 partition before model input, induced 5% null values, row deletion and scaling; SMOTE is discussed in sections 3.3.1–3.3.2 (p.5). Section 4.3 (p.10) narrates resampling before mentioning the split, and Table 3 (p.6) omits the split from its pseudocode. These incomplete/contrasting descriptions leave execution order unresolved. Pre-split contamination remains a **HYPOTHESIS**, not demonstrated leakage. The instruction to partition first in section 3.3 is material counterevidence and must not be omitted.

An accuracy-only criticism is contradicted by section 4.3 (pp.10–12), Table 4 (p.12) and Fig.19 (p.13). The paper already reports sensitivity, specificity, precision, F1 and ROC/PR curves; it uses SMOTE, PCA and RF. Extensions must therefore concern controlled ablations, uncertainty, calibration or evaluation traceability, not claims that imbalance handling, feature selection, minority detection or every ensemble were absent. Narrow reporting gaps: Table 4 supplies point estimates without confidence intervals; the inspected evaluation does not report probability calibration. This does not prove what was or was not computed in unpublished code.

Section 5.2 (p.12) explicitly proposes CV and SHAP, and sections 5.2.2–5.2.3 (pp.12–13) propose ADASYN-based ensembles. The paragraph also proposes genetic/clinical data, and section 5.2.1 (p.12) discusses federated learning/privacy. These are verified future directions, not proven performance gains and not all are in our project scope. Federated privacy leakage must not be conflated with train/test contamination.

**Parameter correction:** Table 2 (p.6) specifies RF random_state=42, LR random_state=0, KNN k=3, DT max_depth=50 with entropy. RF's wording about ten trees/depth remains ambiguous, and the full split/resampling/tuning configuration is still unresolved. The previous blanket description of seeds/hyperparameters as UNVERIFIED was too broad. Our seed 2015 and estimator defaults differ; no faithful paper replication was executed.

The frozen quick experiment demonstrates a sensitivity/BA operating-policy tradeoff against a same-cohort logistic comparator at fixed threshold 0.50. It does not isolate a class-weight effect, prove a new algorithm, improve calibration, or establish superiority to Chang. Multi-selector/top-k standard execution is synthetic; only MI/L1/tree k=10 and the finite model/imbalance comparisons ran on real training CV. SHAP, ADASYN-based ensembles, external validation and full real-data standard/extended experiments remain unexecuted. The exhaustive claim-to-source-to-artifact crosswalk is in [research_gap_evidence.csv](../reports/research_gap_evidence.csv).

The 2024 Healthcare Analytics article 'An investigation of machine learning algorithms and data augmentation techniques for diabetes diagnosis using class imbalanced BRFSS dataset', DOI https://doi.org/10.1016/j.health.2023.100297, was identified through publisher/index records. Its detailed methodology and cohort were not verified in this session; no ranking or deficiency is assigned. The 2022 article 'Detecting High-Risk Factors and Early Diagnosis of Diabetes Using Machine Learning Methods', DOI https://doi.org/10.1155/2022/2557795 (https://pmc.ncbi.nlm.nih.gov/articles/PMC9536939/) was identified. The full JATS article was subsequently retrieved through the public Europe PMC API (https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9536939/fullTextXML), resolving the blocked PMC page. Ullah et al. describe the 253,680-row processed dataset, all 21 predictors, SMOTE-ENN and normalization (§3), and an initial 70/30 split (§4.1). Section 5 reports KNN test accuracy 98.363%; this is a reported result, not a reproduced finding. The narrative does not establish the exact executable ordering or a pristine independent tuning validation. Section 6 proposes further clinic-dataset testing. A defensible extension is a reproducible test-population definition and independent validation, without asserting demonstrated leakage.

The proposed contribution is testable: preserve original CDC survey design for epidemiological inference while conducting fold-local prediction development and a frozen same-cohort final comparison. Whether prediction improves, which variables are stable, and whether interval precision supports useful subgroup conclusions must come from executed experiments. Better scientific traceability can be a contribution even when discrimination does not improve.

Search evidence classifications are not a blanket quality score. VERIFIED denotes an inspected specific claim, PARTIALLY_VERIFIED denotes unresolved metadata/method details, UNVERIFIED denotes an unavailable item, and HYPOTHESIS denotes a proposed explanation or gap requiring further inspection. The initial extraction named sections without invented pages; the full-PDF audit now supplies checked PDF/printed page numbers for Chang. No page numbers were assigned to papers without an inspected paginated source. No fabricated numerical findings appear in generated reports.


## Research Gap

| gap_id | question | evidence_status | scientific_status |
| --- | --- | --- | --- |
| C01 | Cohort, cỡ mẫu và provenance chưa nhất quán | VERIFIED | PARTIALLY_ADDRESSED |
| C02 | Định nghĩa nhãn diabetes/prediabetes chưa thống nhất | VERIFIED | PARTIALLY_ADDRESSED |
| C03 | Tính hợp lý và tác động của quy trình missing-data/preprocessing | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C04 | Nghi vấn leakage do preprocessing/SMOTE trước split | HYPOTHESIS | PARTIALLY_ADDRESSED |
| C05 | Đánh giá chiến lược mất cân bằng và phân bố test | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C06 | Khẳng định Chang chỉ dùng accuracy | UNVERIFIED | REFUTED_AS_GAP |
| C07 | Khẳng định Chang không có train/test holdout | UNVERIFIED | REFUTED_AS_GAP |
| C08 | CV phát triển và truy vết selection trước final test | VERIFIED | PARTIALLY_ADDRESSED |
| C09 | Thiếu uncertainty/paired comparison trong bảng kết quả báo cáo | VERIFIED | PARTIALLY_ADDRESSED |
| C10 | Minority detection, threshold và cost tradeoff | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C11 | Calibration chưa được báo cáo trong evaluation đã đọc | VERIFIED | PARTIALLY_ADDRESSED |
| C12 | Thiết kế survey và adjusted population inference | PARTIALLY_VERIFIED | RESOLVED |
| C13 | Robustness: missingness, outcome và demographic subgroups | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C14 | Interpretability và hướng mở rộng SHAP | VERIFIED | PARTIALLY_ADDRESSED |
| C15 | Đa dạng feature selection và top-k ablation | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C16 | Mở rộng ensembles/boosters và kiểm tra lợi ích | VERIFIED | PARTIALLY_ADDRESSED |
| C17 | External/temporal validity và clinical generalizability | PARTIALLY_VERIFIED | RESOLVED |
| C18 | ADASYN-based ensemble được đề xuất trong bài | VERIFIED | PARTIALLY_ADDRESSED |
| C19 | Genetic/clinical variables và disease ascertainment | VERIFIED | INFEASIBLE_WITH_AVAILABLE_DATA |
| C20 | Federated learning/privacy-preserving workflow | VERIFIED | PARTIALLY_ADDRESSED |
| C21 | Seeds, hyperparameters và khả năng reproduction chính xác | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |

## Research objectives

A: source-grounded reproduction feasibility. B: investigate C01–C21 with evidence. C: predictive comparisons under controlled development. D: preserve survey inference. These outcomes are distinct.

## Research questions

RQ1 adjusted associations; RQ2 feature/model/resampling effects; RQ3 threshold/calibration tradeoffs; RQ4 subgroup/seed/year stability.

## Hypotheses

Coefficient/group nulls: adjusted association=0. Predictive contrasts require matched cohorts/conditions; development rankings are exploratory, not confirmatory significance tests.

## Dataset

Original CDC2015 XPT441456×330; UCI processed source audited separately; original CDC2017 XPT450016 for temporal evaluation. See source hashes and codebook evidence.

## Cohort construction

Original binary422558, complete cases243529; all84512 legacy final-test IDs excluded from new development. QUICK draws2000 training-pool respondents. Core-three outcomes and cohorts remain separate.

## Variables

19 original predictors for development; encoded-column k differs from raw-variable count. Temporal model uses14 compatible variables, excludes rotated/changed nutrition/alcohol/cholesterol screening. No genes/lab disease confirmation.

## Statistical methods

# Survey statistical inference

Preserved original results and code: _LLCPWT/_STSTR/nested_PSU Taylor linearization, full-domain zero influences, design CIs, adjusted OR/RRR. Independent R survey/nnet covariance tests were rerun in the baseline and final test suite.

Original binary cohort422558; complete cases243529; weighted conditional-domain diabetes prevalence10.7052% (CI10.5303–10.8826%); BMI OR1.8754 (1.7936–1.9610). Core-three complete cases248053. Median/mode sensitivity is deterministic, not proper multiple imputation. These associations are not causal.

New development class weighting is not survey weighting. Temporal unweighted CI is not design-based population prediction uncertainty. Full multiple imputation, MNAR and confirmatory subgroup inference remain incomplete.


## Machine-learning methods

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

See feature/model/imbalance/ensemble reports and registry for executable settings; no new algorithm claimed.

## Experimental protocol

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

Model and threshold for temporal evaluation frozen before2017 label loading; no new2015 final evaluations.

## Results

| model | stage | balanced_accuracy | sensitivity | specificity | roc_auc | pr_auc | brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| logistic | screen | 0.73547 | 0.80755 | 0.6634 | 0.80735 | 0.395 | 0.0982 |
| decision_tree | screen | 0.7067 | 0.78113 | 0.63228 | 0.72403 | 0.27626 | 0.11351 |
| random_forest | screen | 0.71657 | 0.87925 | 0.55389 | 0.81125 | 0.4037 | 0.09686 |
| extra_trees | screen | 0.70109 | 0.70189 | 0.70029 | 0.79545 | 0.35653 | 0.09922 |
| knn | screen | 0.67684 | 0.61132 | 0.74236 | 0.68654 | 0.23766 | 0.12033 |
| naive_bayes | screen | 0.61018 | 0.94717 | 0.2732 | 0.70458 | 0.21967 | 0.64094 |
| gb | screen | 0.71715 | 0.72075 | 0.71354 | 0.80309 | 0.3733 | 0.09839 |
| gradient_boosting | screen | 0.70538 | 0.65283 | 0.75793 | 0.79329 | 0.37908 | 0.1028 |
| xgboost | screen | 0.74439 | 0.84151 | 0.64726 | 0.80173 | 0.37116 | 0.09856 |
| lightgbm | screen | 0.72695 | 0.72075 | 0.73314 | 0.79742 | 0.38799 | 0.09968 |
| catboost | screen | 0.74124 | 0.84906 | 0.63343 | 0.81252 | 0.39969 | 0.09641 |
| logistic | features | 0.70183 | 0.78868 | 0.61499 | 0.78013 | 0.34473 | 0.10148 |
| logistic | features | 0.74279 | 0.83774 | 0.64784 | 0.80163 | 0.37801 | 0.09783 |
| logistic | features | 0.74525 | 0.84151 | 0.64899 | 0.80669 | 0.39009 | 0.09722 |
| logistic | features | 0.74231 | 0.82642 | 0.65821 | 0.80559 | 0.39084 | 0.09737 |
| logistic | features | 0.71074 | 0.82264 | 0.59885 | 0.76538 | 0.31527 | 0.10242 |
| logistic | features | 0.72264 | 0.80377 | 0.6415 | 0.77705 | 0.35614 | 0.09994 |
| logistic | features | 0.72334 | 0.8 | 0.64669 | 0.78617 | 0.36085 | 0.09984 |
| logistic | features | 0.7181 | 0.78491 | 0.6513 | 0.78914 | 0.36637 | 0.10008 |
| logistic | features | 0.7256 | 0.82642 | 0.62478 | 0.77553 | 0.34429 | 0.1009 |
| logistic | features | 0.72827 | 0.80755 | 0.64899 | 0.7933 | 0.36651 | 0.09912 |
| logistic | features | 0.72725 | 0.80377 | 0.65072 | 0.80017 | 0.36609 | 0.099 |
| logistic | features | 0.73464 | 0.81509 | 0.65418 | 0.80598 | 0.37426 | 0.09847 |
| logistic | features | 0.67545 | 0.78491 | 0.56599 | 0.72328 | 0.24279 | 0.10679 |
| logistic | features | 0.72156 | 0.82642 | 0.61671 | 0.77859 | 0.32104 | 0.10267 |
| logistic | features | 0.73212 | 0.83774 | 0.62651 | 0.80087 | 0.35534 | 0.09976 |
| logistic | features | 0.73584 | 0.83019 | 0.6415 | 0.80874 | 0.37612 | 0.09857 |
| logistic | features | 0.69669 | 0.76226 | 0.63112 | 0.73185 | 0.25959 | 0.10557 |
| logistic | features | 0.68261 | 0.65283 | 0.71239 | 0.74666 | 0.27864 | 0.10485 |
| logistic | features | 0.69193 | 0.75849 | 0.62536 | 0.76267 | 0.32186 | 0.10346 |
| logistic | features | 0.71842 | 0.79245 | 0.64438 | 0.79527 | 0.3664 | 0.09985 |
| logistic | features | 0.68576 | 0.68679 | 0.68473 | 0.76481 | 0.31403 | 0.10343 |
| logistic | features | 0.72948 | 0.82264 | 0.63631 | 0.78121 | 0.3522 | 0.10035 |
| logistic | features | 0.73595 | 0.81887 | 0.65303 | 0.78653 | 0.36605 | 0.10048 |
| logistic | features | 0.73521 | 0.81509 | 0.65533 | 0.79378 | 0.38148 | 0.0992 |
| logistic | features | 0.69997 | 0.75094 | 0.64899 | 0.74748 | 0.32914 | 0.10291 |
| logistic | features | 0.7196 | 0.8 | 0.63919 | 0.7809 | 0.35833 | 0.10056 |
| logistic | features | 0.72271 | 0.78491 | 0.66052 | 0.79086 | 0.36122 | 0.09988 |
| logistic | features | 0.73157 | 0.80377 | 0.65937 | 0.79594 | 0.37422 | 0.09965 |
| logistic | features | 0.67332 | 0.75472 | 0.59193 | 0.71968 | 0.26326 | 0.1069 |
| logistic | features | 0.69649 | 0.78491 | 0.60807 | 0.75376 | 0.29744 | 0.10448 |
| logistic | features | 0.72502 | 0.82642 | 0.62363 | 0.77778 | 0.34426 | 0.10119 |
| logistic | features | 0.73506 | 0.85283 | 0.61729 | 0.79188 | 0.34381 | 0.10077 |
| logistic | features | 0.6958 | 0.75472 | 0.63689 | 0.74724 | 0.28777 | 0.10406 |
| logistic | features | 0.72138 | 0.81509 | 0.62767 | 0.76945 | 0.31535 | 0.10308 |
| logistic | features | 0.73451 | 0.81887 | 0.65014 | 0.79963 | 0.37894 | 0.09864 |
| logistic | features | 0.73796 | 0.81887 | 0.65706 | 0.80241 | 0.38356 | 0.09838 |
| logistic | features | 0.70871 | 0.6566 | 0.76081 | 0.80053 | 0.38532 | 0.0997 |
| logistic | imbalance | 0.71719 | 0.81132 | 0.62305 | 0.79692 | 0.37071 | 0.19412 |
| logistic | imbalance | 0.737 | 0.8717 | 0.60231 | 0.8046 | 0.3843 | 0.16931 |
| logistic | imbalance | 0.71845 | 0.84151 | 0.59539 | 0.78735 | 0.35924 | 0.15672 |
| logistic | imbalance | 0.72432 | 0.83019 | 0.61844 | 0.80666 | 0.38746 | 0.17165 |
| random_forest | imbalance | 0.64133 | 0.71321 | 0.56945 | 0.69588 | 0.28434 | 0.10738 |
| xgboost | imbalance | 0.6302 | 0.58491 | 0.6755 | 0.70805 | 0.2656 | 0.10838 |
| lightgbm | imbalance | 0.62827 | 0.60755 | 0.64899 | 0.68324 | 0.24099 | 0.11457 |
| random_forest | imbalance | 0.63068 | 0.63774 | 0.62363 | 0.66437 | 0.23389 | 0.15098 |
| xgboost | imbalance | 0.60361 | 0.72075 | 0.48646 | 0.68199 | 0.23646 | 0.17746 |
| lightgbm | imbalance | 0.59013 | 0.86038 | 0.31988 | 0.67351 | 0.23061 | 0.14922 |
| random_forest | imbalance | 0.63375 | 0.64906 | 0.61844 | 0.66255 | 0.23082 | 0.15249 |
| xgboost | imbalance | 0.61204 | 0.7434 | 0.48069 | 0.68959 | 0.24047 | 0.17989 |
| lightgbm | imbalance | 0.59808 | 0.74717 | 0.44899 | 0.66443 | 0.22164 | 0.152 |
| adasyn_soft_voting | ensemble | 0.63546 | 0.68302 | 0.5879 | 0.67965 | 0.23941 | 0.15609 |
| adasyn_stacking | ensemble | 0.59893 | 0.82264 | 0.37522 | 0.67628 | 0.24673 | 0.1098 |
| soft_voting | ensemble | 0.75335 | 0.84906 | 0.65764 | 0.81848 | 0.42276 | 0.09524 |
| hard_voting | ensemble | 0.55346 | 0.12075 | 0.98617 | 0.55346 | 0.1855 | 0.1285 |
| weighted_voting | ensemble | 0.74858 | 0.84528 | 0.65187 | 0.81873 | 0.4213 | 0.09529 |
| stacking | ensemble | 0.74095 | 0.84906 | 0.63285 | 0.81319 | 0.41767 | 0.09719 |
| feature_ensemble | ensemble | 0.73789 | 0.83774 | 0.63804 | 0.80903 | 0.40994 | 0.09616 |
| family_ensemble | ensemble | 0.73172 | 0.76604 | 0.69741 | 0.81703 | 0.41919 | 0.09565 |
| logistic | missing | 0.7414 | 0.81132 | 0.67147 | 0.81067 | 0.39659 | 0.09791 |
| logistic | missing | 0.73736 | 0.81132 | 0.6634 | 0.80728 | 0.3948 | 0.09828 |
| logistic | search | 0.73759 | 0.79623 | 0.67896 | 0.80259 | 0.38489 | 0.09986 |
| random_forest | search | 0.72702 | 0.90189 | 0.55216 | 0.80982 | 0.39994 | 0.0973 |
| xgboost | search | 0.70488 | 0.63396 | 0.77579 | 0.78516 | 0.35888 | 0.10461 |
| lightgbm | search | 0.72271 | 0.7434 | 0.70202 | 0.79883 | 0.38772 | 0.09942 |
| catboost | search | 0.73752 | 0.81509 | 0.65994 | 0.80299 | 0.37818 | 0.09799 |
| logistic | calibration | 0.72068 | 0.90189 | 0.53948 | 0.8044 | 0.40158 | 0.0979 |
| logistic | calibration | 0.72595 | 0.92453 | 0.52738 | 0.80405 | 0.39852 | 0.09672 |

Temporal:

| accuracy | balanced_accuracy | precision | sensitivity | f1 | macro_f1 | log_loss | class_0_sensitivity | class_0_specificity | class_1_sensitivity | class_1_specificity | roc_auc | pr_auc | brier | specificity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.5634 | 0.69765 | 0.23349 | 0.88643 | 0.36962 | 0.51784 | 0.55141 | 0.50888 | 0.88643 | 0.88643 | 0.50888 | 0.79042 | 0.37989 | 0.18782 | 0.50888 |

## Baseline comparison

# Chang 2022 reproduction track

Original DOI 10.1016/j.health.2022.100118; audited PDF pages4–6,12–13.

UCI public processed source downloaded and audited: 253680 rows, ID plus21 predictors and Diabetes_binary. Source SHA256 9f71fda9d4ae5f4878c99b9233b6a16accfa9a17c194116a6b78100540934964. Metadata itself is inconsistent (35 vs21 features, creation year2017). It is not established as the exact paper input.

Exact replication: NOT_POSSIBLE_FROM_AVAILABLE_EVIDENCE. Approximate processed predictive reproduction: NOT_EXECUTED because sequential UCI IDs cannot establish exclusion of the already-accessed 2015 final-test respondents. Repartitioning that potentially overlapping cohort would not create an independent test.

The prior approximate reproduction script remains tested synthetically; it is not executed on these real processed rows. No claim of82.26% reproduction. Known Table2 params: RF state42/entropy (tree/depth ambiguity), LR state0, KNN3, DT depth50/entropy. New development experiments on original-source training IDs are a separate track, not a faithful paper baseline.


## Research-gap evaluation

# Research-gap results: PARTIAL COMPLETION

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| gap_id | question | evidence_status | scientific_status |
| --- | --- | --- | --- |
| C01 | Cohort, cỡ mẫu và provenance chưa nhất quán | VERIFIED | PARTIALLY_ADDRESSED |
| C02 | Định nghĩa nhãn diabetes/prediabetes chưa thống nhất | VERIFIED | PARTIALLY_ADDRESSED |
| C03 | Tính hợp lý và tác động của quy trình missing-data/preprocessing | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C04 | Nghi vấn leakage do preprocessing/SMOTE trước split | HYPOTHESIS | PARTIALLY_ADDRESSED |
| C05 | Đánh giá chiến lược mất cân bằng và phân bố test | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C06 | Khẳng định Chang chỉ dùng accuracy | UNVERIFIED | REFUTED_AS_GAP |
| C07 | Khẳng định Chang không có train/test holdout | UNVERIFIED | REFUTED_AS_GAP |
| C08 | CV phát triển và truy vết selection trước final test | VERIFIED | PARTIALLY_ADDRESSED |
| C09 | Thiếu uncertainty/paired comparison trong bảng kết quả báo cáo | VERIFIED | PARTIALLY_ADDRESSED |
| C10 | Minority detection, threshold và cost tradeoff | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C11 | Calibration chưa được báo cáo trong evaluation đã đọc | VERIFIED | PARTIALLY_ADDRESSED |
| C12 | Thiết kế survey và adjusted population inference | PARTIALLY_VERIFIED | RESOLVED |
| C13 | Robustness: missingness, outcome và demographic subgroups | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C14 | Interpretability và hướng mở rộng SHAP | VERIFIED | PARTIALLY_ADDRESSED |
| C15 | Đa dạng feature selection và top-k ablation | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| C16 | Mở rộng ensembles/boosters và kiểm tra lợi ích | VERIFIED | PARTIALLY_ADDRESSED |
| C17 | External/temporal validity và clinical generalizability | PARTIALLY_VERIFIED | RESOLVED |
| C18 | ADASYN-based ensemble được đề xuất trong bài | VERIFIED | PARTIALLY_ADDRESSED |
| C19 | Genetic/clinical variables và disease ascertainment | VERIFIED | INFEASIBLE_WITH_AVAILABLE_DATA |
| C20 | Federated learning/privacy-preserving workflow | VERIFIED | PARTIALLY_ADDRESSED |
| C21 | Seeds, hyperparameters và khả năng reproduction chính xác | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |

78 of 78 binary experiments completed on real development data. Four three-class models executed separately. Best selected development score is not an unbiased final estimate. Temporal BA=0.6977, sensitivity=0.8864, specificity=0.5089. No comparison of these scores directly to82.26% is valid.


## Statistical inference

# Survey statistical inference

Preserved original results and code: _LLCPWT/_STSTR/nested_PSU Taylor linearization, full-domain zero influences, design CIs, adjusted OR/RRR. Independent R survey/nnet covariance tests were rerun in the baseline and final test suite.

Original binary cohort422558; complete cases243529; weighted conditional-domain diabetes prevalence10.7052% (CI10.5303–10.8826%); BMI OR1.8754 (1.7936–1.9610). Core-three complete cases248053. Median/mode sensitivity is deterministic, not proper multiple imputation. These associations are not causal.

New development class weighting is not survey weighting. Temporal unweighted CI is not design-based population prediction uncertainty. Full multiple imputation, MNAR and confirmatory subgroup inference remain incomplete.


## Model interpretation

SHAP and bootstrap stability executed on training data; predictive importance is not causal. Adjusted ORs answer a different conditional associational question.

## Robustness

# Development robustness

These are executed post-audit exploratory development results, not new 2015 final-test results. CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.

| seed_run | accuracy | balanced_accuracy | precision | sensitivity | f1 | macro_f1 | log_loss | class_0_sensitivity | class_0_specificity | class_1_sensitivity | class_1_specificity | roc_auc | pr_auc | brier | specificity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.6885 | 0.73573 | 0.2711 | 0.8 | 0.40497 | 0.597 | 0.32677 | 0.67147 | 0.8 | 0.8 | 0.67147 | 0.80174 | 0.37789 | 0.09888 | 0.67147 |
| 1 | 0.7245 | 0.71972 | 0.28464 | 0.71321 | 0.40689 | 0.61373 | 0.32535 | 0.72622 | 0.71321 | 0.71321 | 0.72622 | 0.79812 | 0.39853 | 0.09798 | 0.72622 |

Additional RepeatedStratifiedKFold and held-out-state results: runs/gap_real_quick_v4/repeated_cv_* and group_cv. Sex/age/race/BMI/education/income descriptive development groups: tables/gap_extension/development_subgroups.csv. Cohorts differ for complete-case analysis. Overlapping folds are dependent; variability is descriptive, with no IID significance claim. Subgroup sample thresholds30 and presence of all classes are required. No model-selection uncertainty correction or confirmatory fairness claims.


## Discussion

Soft voting led exploratory development BA, but the separate temporal clinical-feature track selected weighted LR. This is not an apples-to-apples architecture comparison across years. Broad benefits and clinical utility remain unproved.

## Limitations

# Unfinished work — PARTIAL COMPLETION

- Exact/faithful Chang reproduction: unresolved cohort, label, RF tree/depth and preprocessing order; processed UCI linkage to old test unknown. Real processed predictive reproduction deliberately not executed.
- STANDARD/EXTENDED full eligible development execution not run; QUICK budget2000 and shallow nested searches only. Full optimization/long repeated nested CV not claimed.
- Strict inner-preprocessing isolation for RFECV/permutation was corrected in v4; older v2 results remain archived and are superseded for those comparisons.
- Full mixed-feature ADASYN not used; continuous-only experiments cannot establish benefit for nominal-rich full representation. Matched continuous soft-voting/stacking controls remain incomplete.
- Calibration interventions tested on unweighted LR; no claim of repairing the legacy weighted model calibration. Clinical operating constraints/utilities not established.
- Full multiple-imputation survey inference, MNAR, functional-form sensitivity and confirmatory adjusted subgroup effects incomplete.
- SHAP is training-only/descriptive with64-row selector samples and128-row summary; bootstrap3 for stability is limited. No causal explanations or validated interpretability gains.
- Temporal validation limited to a separate14-variable model and5000 eligible2017 respondents; not a clinical external cohort, no survey-valid predictive CIs, possible unlinked repeat respondents across years.
- Genetics/lab biomarkers unavailable. Federation is public-data simulated clients with centralized preprocessing; no real institutions, secure aggregation, differential privacy or privacy guarantee.
- Actual Google Colab runtime not available: COLAB_RUNTIME_NOT_VERIFIED.
- Historical notebook tests retained; only modified notebooks must be reported with current execution counts. No guaranteed zero-error environment claim.


## Conclusions

PARTIAL COMPLETION. Feasible selected experiments executed and independent temporal evaluation added; unresolved reproduction, full-budget inference/ML and real privacy/clinical-data requirements remain explicit.

## References

Chang et al.2022, DOI10.1016/j.health.2022.100118; CDC2015 https://www.cdc.gov/brfss/annual_data/annual_2015.html ; CDC2017 https://www.cdc.gov/brfss/annual_data/annual_2017.html ; UCI DOI10.24432/C53919. No unverified methodological deficiency attributed to a paper.

## Reproducibility appendix

# Extension reproducibility

Recoverable pre-modification checkpoint: /workspace/research_checkpoints/brfss_before_gap_extension.tar.gz (local evidence; not a required execution path). Baseline39 tests passed before modification. Legacy src/config/model/split/evaluation evidence remained unchanged; audit snapshot checks in runner and temporal workflow.

Each experiment stores config, source-run signature, OOF rows checksum, fold metrics, feature lists and inner thresholds. Fixed outer splits/development IDs in run folder; seed20261106. Source/dependency versions in manifest. Model serialization uses trusted joblib artifacts. Completed experiment records resume by checksum; modified scientific engine requires new run directory, not deletion of evidence.

First attempt had a SMOTENC feature-name export error (77/78); v2 corrected it. V3 exposed a nested-pipeline wrapper failure in five selector configs; canonical v4 corrects the wrapper and isolates inner preprocessing for RFECV/permutation. Temporal evaluation used the earlier unchanged LR factory branch, was not repeated, and is not evidence for the new selector variants. Exact earlier engine sources were recovered with verified original hashes. Earlier attempt preserved. This was development debugging, not repeated final-test evaluation. 2017 evaluation ledger has one batch and no post-result optimization. Original2015 final ledger remains1.


## Additional domain results and final release qualification

41 survey domain estimates are in tables/gap_extension/survey_domains.csv. Current release verification is54 tests passed,78 corrected real binary development configurations,4 core-three configurations under the archived matching engine, and one frozen2017 evaluation. None of these establishes direct superiority to Chang. The original2015 final evaluation is unchanged. Full-budget standard/extended runs, faithful processed reproduction and genuine clinical/private-data validation remain incomplete.
