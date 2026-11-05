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

## ZIP/codebook preparation update

The user supplied the Drive ZIP path `Diabetes_Statistics_2015/01_Raw_Data/LLCP2015XPT.zip`. It is not mounted in the cloud workspace. Notebook now reads XPT-in-ZIP via CRC-checked temporary spooling, performs metadata preflight and an independent full raw-code count, and keeps Final Test locked. The Train/CV protocol is unchanged.

`schema.reviewed.json` is a **partial, unverified draft**, with 8 active original candidates, an inactive ordinal-age alternative and explicit leakage exclusions. CDC access was blocked by proxy CONNECT 403; no official variable page was reviewed. All proposed codes/units still require authoritative checking. See `00_Audit/codebook_review.md`. No BRFSS baseline, CV result, final score, CI or literature-improvement claim is available. Both default unit tests and the full synthetic integration workflow passed; these establish software behavior only.
