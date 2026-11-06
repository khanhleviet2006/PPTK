# MASTER CODEX PROMPT — COMPLETE ALL RESEARCH GAPS
## BRFSS 2015 Statistical Methods | Chang et al. (2022)

### ROLE

You are an autonomous multidisciplinary scientific research and engineering team consisting of:

- Senior Biostatistician
- Epidemiologist
- Survey Statistics Specialist
- Senior Machine Learning Research Scientist
- Feature Engineering and Ensemble Learning Specialist
- Python Research Software Engineer
- Google Colab / MLOps Engineer
- Scientific Reproducibility Auditor
- Academic Research Methodologist

Your task is to **continue and complete the existing BRFSS2015-Statistical-Methods research project**, systematically address all 21 audited research-gap items, implement the missing experiments, execute the experiments wherever valid data and computational resources are available, and produce scientifically defensible research reports.

Do not stop at writing plans, pseudocode, placeholder notebooks, or unexecuted implementations.

Do not fabricate results, claim experimental completion without execution, or optimize against an already-accessed final test set.

---

# 1. EXISTING PROJECT

Repository:

`BRFSS2015-Statistical-Methods`

Existing important files:

- `reports/final_report.md`
- `reports/VERIFICATION.md`
- `reports/RESEARCH_GAP_AUDIT.md`
- `notebooks/00_Run_All_Colab.ipynb`

The project already contains a research pipeline, statistical analyses, tests, and real-data quick experiments.

Preserve all existing valid work.

Before changing anything:

1. Inspect the complete repository.
2. Read the existing research protocol.
3. Read every research-gap audit and evidence matrix.
4. Inspect all 13 notebooks.
5. Inspect the data-processing and statistical-analysis modules.
6. Inspect machine-learning pipelines and experiment configurations.
7. Inspect frozen model artifacts, existing split definitions, checksums, and evaluation logs.
8. Identify implemented, partially implemented, unimplemented, and unverified functionality.
9. Run existing tests and document the baseline state.
10. Create a recoverable checkpoint before modifications.

Never overwrite original experimental evidence.

Maintain backward compatibility with validated outputs whenever possible.

---

# 2. SCIENTIFIC REFERENCE

Primary baseline:

Chang, V., Ganatra, M. A., Hall, K., Golightly, L., & Xu, Q. A. (2022).

*An assessment of machine learning models and algorithms for early prediction and diagnosis of diabetes using health indicators.*

Healthcare Analytics, 2, 100118.

DOI: https://doi.org/10.1016/j.health.2022.100118

Use the full paper and original supporting evidence.

Prior research-gap audit:

- 21 research-gap and methodological items.
- 22 page-specific citations.
- Full 14-page paper reviewed.

Do not assume that every identified item is a verified weakness of Chang.

Preserve the distinction between:

- VERIFIED
- PARTIALLY_VERIFIED
- UNVERIFIED
- HYPOTHESIS
- REFUTED

Also distinguish evidence status from implementation status.

---

# 3. EXISTING EXPERIMENTAL RESULTS

Existing real-data quick comparison:

| Metric | Selected LR | Fixed LR Baseline |
|---|---:|---:|
| Accuracy | 0.6747 | 0.8721 |
| Balanced Accuracy | 0.7511 | 0.5786 |
| Sensitivity | 0.8551 | 0.1792 |
| Specificity | 0.6471 | 0.9779 |
| Precision | 0.2700 | 0.5535 |
| Positive F1 | 0.4104 | 0.2708 |
| Macro-F1 | 0.5929 | 0.6004 |
| ROC-AUC | 0.8307 | 0.8296 |
| PR-AUC | 0.4129 | 0.4148 |
| Brier Score | 0.1728 | 0.0936 |
| Log Loss | 0.5143 | 0.3048 |

Selected model:

- Logistic Regression
- Class weighting enabled
- Threshold = 0.40

Fixed comparator:

- Logistic Regression
- No class weighting
- Threshold = 0.50

These models were evaluated on the existing final test cohort of 84,512 observations.

Existing evaluation ledger:

`evaluation_count = 1`

IMPORTANT:

The final test has already been accessed.

It is no longer a completely untouched test set for any future model-development decisions informed by its results.

Do not repeatedly evaluate new candidates on this test set.

Do not tune feature selection, hyperparameters, class weighting, thresholds, calibration, or ensemble weights using this test set.

Preserve the existing evaluation ledger.

If new confirmatory evaluation is necessary, create an independently justified evaluation design using genuinely unseen data, a valid external or temporal dataset, or explicitly label results exploratory when independence cannot be established.

Never silently create a new "final test" by repeatedly repartitioning observations already used for experiment selection.

---

# 4. OVERALL RESEARCH OBJECTIVES

The project must address four objectives.

### Objective A — Faithful scientific baseline reproduction

Reconstruct Chang et al. (2022) as faithfully as the available evidence permits.

### Objective B — Research-gap experiments

Systematically investigate all 21 audited items using controlled experiments, statistical analyses, or documented feasibility assessments.

### Objective C — Predictive performance improvement

Investigate whether feature selection, gradient boosting, imbalance handling, threshold optimization, calibration, and ensemble learning improve model performance.

### Objective D — Statistical inference

Use appropriate BRFSS survey-design methods to estimate associations between demographic, biomedical, lifestyle variables and diabetes status.

All four objectives must be reported independently.

A higher predictive score must not be misrepresented as evidence of improved statistical inference.

---

# 5. RESEARCH GAP EXECUTION MATRIX

Use the existing audit IDs C01–C21.

Create a formal execution matrix containing:

- Gap ID
- Exact research question
- Evidence from Chang
- Evidence classification
- Proposed scientific test
- Data requirements
- Implementation module
- Experiment configuration
- Execution status
- Result artifact
- Outcome
- Remaining limitations

Implement the following work.

## GAP C01 — Cohort and Sample Reproducibility

Investigate the reported cohort-size inconsistencies.

Implement:

- Dataset source comparison
- Cohort eligibility reconstruction
- Inclusion/exclusion flowchart
- Sample-count reconciliation
- Dataset checksum validation
- Comparison of original CDC data and processed Kaggle data

Where exact reconstruction is impossible, explicitly record why.

Do not manufacture an exact match.

## GAP C02 — Diabetes Outcome Definition

Audit diabetes and prediabetes labels.

Implement separate, documented outcome definitions:

A. Binary diabetes classification.

B. Three-class diabetes status if supported by the source questionnaire and eligibility logic.

C. Sensitivity analyses under alternative scientifically defensible definitions.

Do not automatically classify unobserved prediabetes status as negative.

Compare class prevalence, sample sizes, and subgroup distributions.

Keep these outcomes in separate experiments.

## GAP C03 — Missing Data and Preprocessing

Compare:

- Complete-case analysis
- Median/mode imputation
- Missingness indicators
- Iterative imputation where justified
- Scientifically justified alternative preprocessing

Reproduce Chang's preprocessing only when its exact implementation can be established.

All preprocessing must be fitted inside training folds.

Document how missingness changes cohort composition and estimates.

## GAP C04 — Data Leakage

Perform a reproducibility audit.

Compare:

A. Scientifically valid split-first preprocessing.

B. SMOTE inside training folds.

C. Published-order reconstruction, only if sufficient evidence exists.

A deliberately leaky experiment may be used solely as a clearly isolated educational diagnostic on training/development data, never to select a production model or to claim improvement.

Do not declare Chang's results leaked without direct evidence.

## GAP C05 — Class Imbalance

Experiment with:

- No resampling
- Class weighting
- Random undersampling
- Random oversampling
- SMOTE
- SMOTENC
- ADASYN where technically appropriate

Respect categorical encoding and feature validity.

Apply all resampling within training folds only.

Compare performance using consistent validation populations.

## GAP C06 — Metric Coverage

Chang already reports multiple classification metrics.

Do not classify "accuracy-only evaluation" as a valid gap.

Instead investigate:

- Metric reporting completeness
- Whether uncertainty is reported
- Threshold-dependent tradeoffs
- Calibration quality
- Class-specific errors

## GAP C07 — Independent Evaluation

Chang already reports an 80:20 split.

Do not claim there was no holdout.

Audit:

- Preprocessing isolation
- Hyperparameter selection
- Resampling placement
- Evaluation independence
- Leakage prevention

Document uncertainty where source code is unavailable.

## GAP C08 — Cross-Validation

Implement:

- Stratified K-Fold
- Repeated Stratified K-Fold where computationally feasible
- Nested CV where justified
- Group-aware or survey-aware alternatives where appropriate

Use a consistent development protocol.

All hyperparameter and feature selection must occur within training folds.

Do not use nested CV as a substitute for a genuine independent final test when making confirmatory claims.

## GAP C09 — Statistical Uncertainty

Implement:

- Confidence intervals
- Paired bootstrap comparisons
- Out-of-fold performance summaries
- Variability across repeated CV
- Appropriate comparisons of correlated model predictions

Distinguish conditional test-set uncertainty, model-selection uncertainty, and survey-design uncertainty.

Do not overstate bootstrap confidence intervals.

## GAP C10 — Minority-Class Detection

Evaluate:

- Sensitivity
- Specificity
- Precision
- F1
- Balanced Accuracy
- PR-AUC
- Confusion matrices
- Threshold tradeoff curves

Select thresholds using development data only.

Explore whether higher minority-class recall can be obtained without unacceptable false-positive rates.

## GAP C11 — Probability Calibration

Implement:

- Brier Score
- Log Loss
- Calibration curves
- Calibration intercept/slope where appropriate
- Sigmoid calibration
- Isotonic calibration

Fit calibration using properly separated development folds.

Compare calibrated and uncalibrated models.

Report discrimination and calibration separately.

Do not assume higher sensitivity means better probabilities.

## GAP C12 — Complex Survey Design

Preserve and extend the existing survey analysis.

Use:

- `_LLCPWT`
- `_STSTR`
- `_PSU`

Where appropriate, estimate:

- Weighted prevalence
- Confidence intervals
- Adjusted Odds Ratios
- Relative Risk Ratios for multinomial outcomes
- Design-based standard errors
- Subgroup/domain estimates

Cross-check selected results with independent R survey implementations.

Distinguish statistical survey weighting from machine-learning class weighting.

## GAP C13 — Robustness and Subgroup Analysis

Implement:

- Age subgroup analysis
- Sex subgroup analysis
- BMI subgroup analysis
- Income/education analysis where supported
- Missing-data sensitivity
- Alternative eligible-cohort definitions
- Multiple random seeds
- Stability of model performance

Respect data availability and minimum subgroup sizes.

Report uncertainty and multiple-comparison limitations.

## GAP C14 — Interpretability and SHAP

Implement:

- Permutation importance
- SHAP for supported models
- Feature-importance stability
- Subgroup explanations where justified
- Comparison with adjusted logistic regression effects

Avoid interpreting SHAP values as causal effects.

Explain the distinction between predictive importance and statistical association.

## GAP C15 — Feature Selection

This is a major experimental workstream.

Implement and compare:

1. No feature selection
2. PCA baseline
3. Mutual Information
4. SelectKBest
5. L1 Logistic Regression
6. Recursive Feature Elimination
7. RFECV
8. Random Forest importance
9. XGBoost importance
10. Permutation-based selection
11. SHAP-based feature selection where feasible

Evaluate different feature counts, including:

- Top 5
- Top 10
- Top 15
- Top 20
- Full eligible feature set

Deduplicate selectors that are mathematically or operationally equivalent under a configuration.

Prevent unstable or ungrounded selection.

Perform all feature selection inside CV folds.

Save selected-feature lists, stability measures, runtime, and performance results.

Use the same development splits when comparing methods.

## GAP C16 — Advanced ML and Ensemble Learning

Implement and compare:

Baseline models:

- Logistic Regression
- Decision Tree
- Random Forest
- Extra Trees
- KNN
- Naive Bayes

Advanced models:

- Gradient Boosting
- HistGradientBoosting
- XGBoost
- LightGBM
- CatBoost

Ensemble methods:

- Soft Voting
- Hard Voting
- Weighted Voting
- Stacking
- Feature-based Ensemble
- Model-family Ensemble

Use out-of-fold predictions for stacking.

Do not construct a stacking meta-model using in-sample predictions.

Ensure ensemble weighting is selected using development data.

Compare against strong single-model baselines.

## GAP C17 — External and Temporal Validation

Investigate whether an independent BRFSS year or compatible dataset can be used.

Before using an external dataset:

- Verify questionnaire compatibility
- Verify outcome comparability
- Verify feature availability
- Verify sampling design
- Document distribution shift

If external validation is not feasible, report it as NOT_EXECUTED.

Never describe within-cohort subgroup analysis as external validation.

## GAP C18 — ADASYN-Based Ensemble

Chang proposes ADASYN-based ensemble extensions.

Implement where methodologically feasible:

- ADASYN + Random Forest
- ADASYN + XGBoost
- ADASYN + LightGBM
- ADASYN + Soft Voting
- ADASYN + Stacking

Do not apply vanilla ADASYN directly to arbitrarily integer-coded nominal predictors.

Use an encoding/sampling design appropriate to the features, or document infeasibility and compare categorical-safe alternatives.

Resampling must be strictly training-only.

## GAP C19 — Genetic and Clinical Variables

Audit availability of:

- Genetic markers
- Blood glucose
- HbA1c
- Clinical diagnoses
- Laboratory biomarkers

Do not invent unavailable BRFSS variables.

If unavailable, classify this gap as requiring external data.

Produce a feasibility report.

## GAP C20 — Federated Learning and Privacy

Investigate the feasibility of federated learning.

Distinguish:

- Data privacy
- Federated optimization
- Train/test contamination

Implement a small, explicitly simulated federated proof of concept only if justified and feasible.

Do not claim real multi-institutional federated validation from simulated data partitions.

## GAP C21 — Reproducibility

Audit and document:

- Seeds
- Hyperparameters
- Data versions
- Dataset hashes
- Python versions
- Library versions
- Split identifiers
- Experiment configurations
- Model artifacts
- Evaluation ledgers

Create a reproducibility manifest for every experiment.

---

# 6. CONTROLLED FEATURE-SELECTION EXPERIMENTS

Construct a factorial but computationally controlled experiment framework.

Factors:

- Outcome definition
- Feature-selection method
- Number of features
- Imbalance strategy
- Model family
- Calibration method
- Threshold policy

Do not execute an uncontrolled combinatorial explosion.

Use staged experimentation:

Stage 1 — Screening using training CV.

Stage 2 — Reduced candidate comparison.

Stage 3 — Hyperparameter optimization on shortlisted candidates.

Stage 4 — Robustness and calibration.

Stage 5 — Confirmatory evaluation only when a scientifically independent evaluation dataset is available.

Use paired development folds for fair comparisons.

Maintain a machine-readable experiment registry.

---

# 7. HYPERPARAMETER OPTIMIZATION

Support:

- RandomizedSearchCV
- Optuna, if compatible
- Scientifically justified search ranges
- Reproducible search seeds
- Resource budgets
- Early stopping implemented without leakage

Optimize:

- XGBoost
- LightGBM
- CatBoost
- Random Forest
- Logistic Regression
- Relevant ensemble configurations

Do not choose a model solely by highest Accuracy.

Predefine a primary selection criterion based on the research question.

Recommended primary metric:

Balanced Accuracy.

Secondary metrics:

- Sensitivity
- Specificity
- PR-AUC
- F1
- Accuracy
- Calibration

For selected clinical screening scenarios, evaluate sensitivity at a predefined minimum specificity, when scientifically justified.

If no justified operating constraint exists, report a threshold tradeoff curve instead of manufacturing one.

---

# 8. BASELINE REPRODUCTION — CHANG 2022

Create a separate reproduction track.

Reconstruct where supported:

- Original processed dataset
- Outcome coding
- 21-feature or other documented feature set
- Preprocessing
- PCA
- SMOTE
- 80:20 split
- Random Forest
- Other published comparator models

Verify exact details before implementing.

Separate:

A. Faithful reproduction.

B. Approximate reproduction.

C. Corrected leakage-free reproduction.

D. New experimental methods.

For each, document:

- Dataset
- Sample size
- Outcome prevalence
- Class balance
- Train/test split
- Feature set
- Preprocessing order
- Hyperparameters
- Accuracy
- Balanced Accuracy
- Sensitivity
- Specificity
- F1
- ROC-AUC
- PR-AUC

The published Accuracy 82.26% is a reference point, not an independently verified benchmark on the project's current cohort.

Never claim direct improvement unless the comparison conditions genuinely match.

---

# 9. GOOGLE COLAB EXECUTION

The final project must work on Google Colab.

Default Drive root:

`/content/drive/MyDrive/BRFSS2015_Statistical_Methods_AZ`

The actual dataset might be stored in another Drive directory.

Implement configurable dataset discovery and explicit failure messages.

Create or update:

`notebooks/00_Run_All_Colab.ipynb`

The master notebook must:

1. Verify Python version.
2. Install validated compatible dependencies.
3. Mount Google Drive.
4. Locate raw data.
5. Validate file schema and integrity.
6. Run cohort engineering.
7. Run descriptive analyses.
8. Run statistical inference.
9. Run baseline reproduction.
10. Run feature-selection experiments.
11. Run advanced machine-learning experiments.
12. Run imbalance experiments.
13. Run ensemble experiments.
14. Run calibration and interpretation.
15. Run robustness analyses.
16. Export complete reports.

Create execution profiles:

- `SMOKE`
- `QUICK`
- `STANDARD`
- `EXTENDED`

SMOKE must use a minimal scientifically coherent fixture or a clearly marked subset and verify that the pipeline works.

QUICK may use a predefined restricted training budget.

STANDARD should use the intended full eligible development dataset.

EXTENDED should add nested/repeated CV, advanced optimization, robustness, and relevant extended experiments.

No profile may mislabel synthetic results as actual BRFSS findings.

Support CPU execution as the default.

Use GPU only when optional acceleration is available.

Add checkpointing and resumable execution.

Protect against:

- Colab runtime restarts
- Out-of-memory failures
- Missing dependencies
- Incompatible package versions
- Missing Drive files
- Partial output files
- Accidental re-evaluation of the final test

If Colab execution is not available in the current environment, test the notebook under the closest compatible local environment and explicitly report actual Colab execution as UNVERIFIED.

---

# 10. TESTING AND SCIENTIFIC VALIDATION

Implement comprehensive tests covering:

- Cohort construction
- Outcome coding
- Codebook transformations
- Missing-value handling
- Survey weights
- Strata and PSU processing
- Feature selection
- SMOTE and ADASYN placement
- Cross-validation
- Stacking OOF integrity
- Threshold selection
- Calibration
- Reproducibility
- Model serialization
- Evaluation ledger protection
- Report generation

Add leakage-specific negative tests.

Ensure:

- No preprocessing leakage
- No feature-selection leakage
- No resampling leakage
- No threshold leakage
- No stacking leakage
- No test-driven model selection

Use synthetic fixtures for automated unit tests.

Use actual BRFSS data for scientific results whenever available.

Keep these evidence types separate.

Every model result must include dataset provenance and experiment configuration.

---

# 11. SCIENTIFIC OUTPUTS

Generate:

`reports/RESEARCH_GAP_EXECUTION_MATRIX.md`

`reports/RESEARCH_GAP_RESULTS.md`

`reports/CHANG_2022_REPRODUCTION.md`

`reports/FEATURE_SELECTION_COMPARISON.md`

`reports/ADVANCED_ML_COMPARISON.md`

`reports/ENSEMBLE_COMPARISON.md`

`reports/IMBALANCE_EXPERIMENTS.md`

`reports/CALIBRATION_ANALYSIS.md`

`reports/SURVEY_STATISTICAL_INFERENCE.md`

`reports/ROBUSTNESS_ANALYSIS.md`

`reports/EXTERNAL_VALIDATION_FEASIBILITY.md`

`reports/REPRODUCIBILITY.md`

`reports/VERIFICATION.md`

`reports/FINAL_RESEARCH_REPORT.md`

`reports/UNFINISHED_WORK.md`

Produce machine-readable CSV/Parquet tables as appropriate.

Generate publication-quality figures:

- Cohort flowchart
- Missingness charts
- Class distributions
- Feature-selection comparison
- Model comparison
- ROC curves
- Precision–Recall curves
- Confusion matrices
- Calibration curves
- SHAP summary plots
- Subgroup performance
- Confidence interval plots

Figures must come from actual recorded experiment results.

---

# 12. FINAL RESEARCH REPORT

Produce a complete academic report suitable for a Statistical Methods course.

Include:

1. Title
2. Abstract
3. Introduction
4. Literature review
5. Research Gap
6. Research objectives
7. Research questions
8. Hypotheses
9. Dataset
10. Cohort construction
11. Variables
12. Statistical methods
13. Machine-learning methods
14. Experimental protocol
15. Results
16. Baseline comparison
17. Research-gap evaluation
18. Statistical inference
19. Model interpretation
20. Robustness
21. Discussion
22. Limitations
23. Conclusions
24. References
25. Reproducibility appendix

For every research gap, state whether the project:

- RESOLVED
- PARTIALLY_ADDRESSED
- INVESTIGATED_NOT_IMPROVED
- NOT_TESTED
- INFEASIBLE_WITH_AVAILABLE_DATA
- REFUTED_AS_GAP

Do not confuse successful code execution with scientific gap resolution.

---

# 13. SCIENTIFIC INTEGRITY REQUIREMENTS

Mandatory:

- No fabricated data.
- No fabricated experiments.
- No fabricated references.
- No invented page citations.
- No fabricated Google Colab verification.
- No leakage.
- No repeated use of final test for model selection.
- No unsupported performance claims.
- No causal claims from cross-sectional associations.
- No claim of a new algorithm merely for combining existing algorithms.
- No claim that using XGBoost automatically resolves a research gap.
- No claim that Accuracy above 82.26% proves superiority without comparable experimental conditions.

Distinguish:

- Engineering completion
- Experimental execution
- Reproducibility verification
- Statistical validity
- Scientific contribution

When evidence is insufficient, record the limitation.

---

# 14. AUTONOMOUS EXECUTION

Work autonomously in the existing repository.

Do not stop after auditing.

Proceed through:

1. Repository inspection
2. Baseline tests
3. Research-gap matrix
4. Missing implementation
5. Scientific validation
6. Actual experiment execution
7. Result verification
8. Report generation
9. Notebook integration
10. Final audit

Prioritize the most valuable and feasible experiments first:

1. Chang baseline reproduction
2. Feature selection
3. XGBoost / LightGBM / CatBoost
4. Class imbalance
5. Ensemble methods
6. Calibration
7. Robustness
8. SHAP
9. Remaining gap feasibility studies

If a genuine dataset is unavailable, complete testable engineering work and clearly mark real-data experiments as pending.

If computational resources are insufficient, preserve checkpoints, reduce experimental scope using a documented predefined budget, and report incomplete experiments without fabricated results.

Do not turn pending experiments into claims of success.

---

# 15. DEFINITION OF DONE

The project is complete only when:

- Existing code and artifacts have been audited.
- All 21 research-gap items have an evidence-backed status.
- Every feasible selected experiment is implemented.
- Required tests pass.
- Real-data experiments available in the environment have actually executed.
- Model comparisons use controlled protocols.
- Scientific results are traceable to files and configurations.
- Existing final-test protections are preserved.
- Colab notebooks are executable and validated to the extent available.
- Reports accurately distinguish completed and pending work.
- Scientific limitations are explicitly documented.

Where any criterion cannot be satisfied, report PARTIAL COMPLETION rather than claiming full success.

Do not promise a zero-error run under an environment you have not actually tested.

---

# 16. FINAL RESPONSE FORMAT

When finished, provide the following summary in Vietnamese:

**A. Repository changes**

Files created, modified, and preserved.

**B. Research Gap completion**

A table of all C01–C21 items and their scientific status.

**C. Algorithms executed**

Separate implemented algorithms, synthetically tested algorithms, CV-tested algorithms, and independently evaluated algorithms.

**D. Actual results**

Report metrics from real BRFSS experiments only, with dataset, sample size, outcome, validation protocol, and uncertainty.

**E. Comparison with Chang et al. (2022)**

State exactly whether comparison is direct, approximate, or not comparable.

**F. Verification**

Number of tests, notebook executions, environment, R cross-checks, and unresolved failures.

**G. Google Colab**

Exact instructions for running the project from a clean runtime.

**H. Remaining limitations**

Explicitly identify every incomplete experiment and scientific gap.

**I. Final deliverables**

Provide accessible repository artifacts, reports, notebook files, and ZIP export if supported by the environment.

Do not merely list internal workspace paths as downloadable artifacts unless they are actually accessible.

**EXECUTE THE WORK. DO NOT STOP AT A PROPOSAL.**