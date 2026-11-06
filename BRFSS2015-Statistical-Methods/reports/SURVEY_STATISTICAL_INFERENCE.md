# Survey statistical inference

Preserved original results and code: _LLCPWT/_STSTR/nested_PSU Taylor linearization, full-domain zero influences, design CIs, adjusted OR/RRR. Independent R survey/nnet covariance tests were rerun in the baseline and final test suite.

Original binary cohort422558; complete cases243529; weighted conditional-domain diabetes prevalence10.7052% (CI10.5303–10.8826%); BMI OR1.8754 (1.7936–1.9610). Core-three complete cases248053. Median/mode sensitivity is deterministic, not proper multiple imputation. These associations are not causal.

New development class weighting is not survey weighting. Temporal unweighted CI is not design-based population prediction uncertainty. Full multiple imputation, MNAR and confirmatory subgroup inference remain incomplete.

## New domain analysis

41 full2015 survey-domain prevalence estimates were executed for sex, age, race, BMI, education and income, with design-based95% CIs and minimum n50. See tables/gap_extension/survey_domains.csv and source-hash metadata. Full-population descriptive inference includes legacy-test respondents, explicitly separate from predictive selection; it did not change any fitted predictor or threshold.
