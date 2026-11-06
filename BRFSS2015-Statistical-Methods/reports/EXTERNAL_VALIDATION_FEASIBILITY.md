# Temporal validation: executed with scope limits

2015→2017 CDC BRFSS. A separate14-variable LR candidate track was frozen using only2015 development CV before reading2017 row outcomes. Nutrition/alcohol and changed cholesterol screening omitted. Same DIABETE3 yes/no coding; SEX refused9 maps missing. Codebook variable pages and excerpts: runs/temporal_2017/compatibility.json.

2017 original source450016 records, eligible 431963; prespecified simple random eligible sample n=5000, seed20261106. External ledger evaluation_count=1. Source hash 09bbdc4bcef8b801cd8c4383b861658ddc89179fadfcd661eef33118aeab2bc9.

| accuracy | balanced_accuracy | precision | sensitivity | f1 | macro_f1 | log_loss | class_0_sensitivity | class_0_specificity | class_1_sensitivity | class_1_specificity | roc_auc | pr_auc | brier | specificity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.5634 | 0.69765 | 0.23349 | 0.88643 | 0.36962 | 0.51784 | 0.55141 | 0.50888 | 0.88643 | 0.88643 | 0.50888 | 0.79042 | 0.37989 | 0.18782 | 0.50888 |

Conditional respondent bootstrap200 repeats (not survey prediction CI):

{
  "accuracy": {
    "lower": 0.547995,
    "upper": 0.5776,
    "valid_replicates": 200
  },
  "balanced_accuracy": {
    "lower": 0.6844107738907571,
    "upper": 0.7119209605090647,
    "valid_replicates": 200
  },
  "precision": {
    "lower": 0.21541225945372977,
    "upper": 0.24826359489549865,
    "valid_replicates": 200
  },
  "sensitivity": {
    "lower": 0.8648925530990749,
    "upper": 0.9105654017563324,
    "valid_replicates": 200
  },
  "f1": {
    "lower": 0.3457654357609784,
    "upper": 0.3888817081245453,
    "valid_replicates": 200
  },
  "macro_f1": {
    "lower": 0.501979746297197,
    "upper": 0.5321244855927142,
    "valid_replicates": 200
  },
  "log_loss": {
    "lower": 0.5363489940413998,
    "upper": 0.5671661307965246,
    "valid_replicates": 200
  },
  "class_0_sensitivity": {
    "lower": 0.49411209790064003,
    "upper": 0.5231064376060787,
    "valid_replicates": 200
  },
  "class_0_specificity": {
    "lower": 0.8648925530990749,
    "upper": 0.9105654017563324,
    "valid_replicates": 200
  },
  "class_1_sensitivity": {
    "lower": 0.8648925530990749,
    "upper": 0.9105654017563324,
    "valid_replicates": 200
  },
  "class_1_specificity": {
    "lower": 0.49411209790064003,
    "upper": 0.5231064376060787,
    "valid_replicates": 200
  },
  "roc_auc": {
    "lower": 0.7739971286609659,
    "upper": 0.8058242716575235,
    "valid_replicates": 200
  },
  "pr_auc": {
    "lower": 0.34139071963824125,
    "upper": 0.41636896654067457,
    "valid_replicates": 200
  },
  "brier": {
    "lower": 0.1820406817502265,
    "upper": 0.19366097795722229,
    "valid_replicates": 200
  },
  "specificity": {
    "lower": 0.49411209790064003,
    "upper": 0.5231064376060787,
    "valid_replicates": 200
  }
}

This is temporal transportability in the same survey system, not clinical validation, proof of person-level independence across years, or a comparison with Chang. Unlinked repeat respondents cannot be excluded. Full-year population prediction uncertainty was not estimated. No post-external tuning occurred.
