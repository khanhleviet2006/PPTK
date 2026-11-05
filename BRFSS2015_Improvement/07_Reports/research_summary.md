# Research status — NOT EXECUTED ON BRFSS

Research question: Do fold-fitted feature selection, explicit interactions/composites and boosting improve binary diabetes prediction over an internal LR baseline while retaining sensitivity?

Research gap: A controlled internal comparison is needed; comparability with Chang et al. (2022) is unverified.

Dataset/cohort: No BRFSS 2015 dataset or previous split found in this workspace. Proposed DIABETE3 cohort requires official codebook review. No Google Drive mount is available here.

Preprocessing, feature selection, model comparison, ablation and statistical methodology are implemented in src/research.py and documented in README.md. All real-data analyses remain UNRUN. Synthetic integration tests validate software only. Survey population inference is explicitly unsupported; no weighted population claim is made.

Limitations: Data/codebook unavailable; no clinical performance evidence; no validated literature protocol match. Three-day runtime feasibility has not been measured on full BRFSS.

Conclusion: Cannot determine improvement over internal baseline or whether Accuracy exceeds 82.26% until data and codebook are supplied and the protocol is executed.

|Experiment|Features|Model|CV Accuracy|CV Sensitivity|CV Balanced Accuracy|
|---|---|---|---|---|---|
|Baseline (unrun)|Reviewed originals|LR|N/A|N/A|N/A|
|Preprocessing (unrun)|B0–B3|LR / native CAT|N/A|N/A|N/A|
|Selection (unrun)|Top 5/10/15/20/all|LR|N/A|N/A|N/A|
|Ablation (unrun)|D0–D4|LR / CAT / LGBM|N/A|N/A|N/A|
|Model comparison (unrun)|Reviewed originals|LR/RF/ET/XGB/LGBM/CAT|N/A|N/A|N/A|

Final Test: unrun. No scores or CI available. It will be reported separately after configuration freezing.
