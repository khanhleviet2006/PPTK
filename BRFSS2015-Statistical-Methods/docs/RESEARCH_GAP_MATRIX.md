> Historical pre-extension audit. Evidence classifications remain applicable; implementation statuses below describe that earlier snapshot. Current execution/scientific status: reports/RESEARCH_GAP_EXECUTION_MATRIX.md and research_gap_execution_matrix.csv.

# Research gap evidence matrix — audited update

Audited 2026-11-06 (Asia/Bangkok). Authoritative detailed source: [RESEARCH_GAP_AUDIT.md](../reports/RESEARCH_GAP_AUDIT.md) and [research_gap_evidence.csv](../reports/research_gap_evidence.csv). The initial extraction had no PDF page validation; the current update uses the preserved original 14-page PDF. DOI for every Chang row: https://doi.org/10.1016/j.health.2022.100118.

Classification describes the gap claim, not merely whether a quote exists. VERIFIED author future work does not prove its benefit; UNVERIFIED/CONTRADICTED rows are rejected claims and must not count as solved gaps. Implementation status is separate. No test-based model choice was made.

| ID | Claim / research direction | Gap classification | Section / printed = PDF pages | Implementation |
|---|---|---|---|---|
| C01 | Cohort, cỡ mẫu và provenance chưa nhất quán | VERIFIED; SUPPORTED_REPORTING_AMBIGUITY | 3.1; Data availability; p.4,13 | PARTIALLY_ADDRESSED |
| C02 | Định nghĩa nhãn diabetes/prediabetes chưa thống nhất | VERIFIED; SUPPORTED_REPORTING_AMBIGUITY | 3.1; Appendix Table A.1; p.4,13 | PARTIALLY_ADDRESSED |
| C03 | Tính hợp lý và tác động của quy trình missing-data/preprocessing | PARTIALLY_VERIFIED; PROCEDURE_VERIFIED_HARM_UNTESTED | 3.3; 3.3.1; p.4,5 | PARTIALLY_ADDRESSED |
| C04 | Nghi vấn leakage do preprocessing/SMOTE trước split | HYPOTHESIS; EXECUTION_ORDER_NOT_ESTABLISHED | 3.3; 4.3; Table 3; p.4,6,10 | PARTIALLY_ADDRESSED |
| C05 | Đánh giá chiến lược mất cân bằng và phân bố test | PARTIALLY_VERIFIED; SMOTE_EXISTS_COMPARATIVE_GAP_NARROWED | 3.3; 3.3.1–3.3.2; 4.3; p.4,5,10 | PARTIALLY_ADDRESSED |
| C06 | Khẳng định Chang chỉ dùng accuracy | UNVERIFIED; CONTRADICTED_BY_VERIFIED_EVIDENCE | 4.3; Table 4; Fig.19; p.10,11,12,13 | NOT_A_VALIDATED_GAP |
| C07 | Khẳng định Chang không có train/test holdout | UNVERIFIED; CONTRADICTED_BY_VERIFIED_EVIDENCE | 3.3; 4.3; p.4,10 | NOT_A_VALIDATED_GAP |
| C08 | CV phát triển và truy vết selection trước final test | VERIFIED; AUTHOR_IDENTIFIED_EXTENSION | 5.2; 3.3; Table 2; p.12,4,6 | ADDRESSED_WITHIN_SCOPE |
| C09 | Thiếu uncertainty/paired comparison trong bảng kết quả báo cáo | VERIFIED; NARROW_REPORTING_GAP | 4.3, Table 4; p.10,11,12 | ADDRESSED_WITHIN_SCOPE |
| C10 | Minority detection, threshold và cost tradeoff | PARTIALLY_VERIFIED; SENSITIVITY_ALREADY_REPORTED_EXTENSION_IS_TRADEOFF | 4.3, Table 4; p.11,12 | PARTIALLY_ADDRESSED |
| C11 | Calibration chưa được báo cáo trong evaluation đã đọc | VERIFIED; NARROW_REPORTING_GAP | 3.4; 4.3; Table 4; Fig.19; p.5,10,11,12,13 | PARTIALLY_ADDRESSED |
| C12 | Thiết kế survey và adjusted population inference | PARTIALLY_VERIFIED; OBJECTIVE_EXTENSION_NO_DESIGN_PROCEDURE_REPORTED | 3.1; 3.4; Table A.1; p.4,5,13 | ADDRESSED_WITHIN_SCOPE |
| C13 | Robustness: missingness, outcome và demographic subgroups | PARTIALLY_VERIFIED; LIMITED_REPORTING_EVIDENCE | 3.3; 4.3; Table 4; p.4,10,11,12 | PARTIALLY_ADDRESSED |
| C14 | Interpretability và hướng mở rộng SHAP | VERIFIED; AUTHOR_IDENTIFIED_EXTENSION | 5.2; 3.2; 3.3.3; p.12,4,5 | PARTIALLY_ADDRESSED |
| C15 | Đa dạng feature selection và top-k ablation | PARTIALLY_VERIFIED; PCA_EXISTS_DIVERSITY_EXTENSION | 3.2; 3.3.3; Table 3; p.4,5,6 | PARTIALLY_ADDRESSED |
| C16 | Mở rộng ensembles/boosters và kiểm tra lợi ích | VERIFIED; AUTHOR_EXTENSION_BENEFIT_IS_HYPOTHESIS | 5.2; 5.2.3; 3.4; p.12,13,5 | PARTIALLY_ADDRESSED |
| C17 | External/temporal validity và clinical generalizability | PARTIALLY_VERIFIED; SINGLE_COHORT_LIMITATION_EXTENSION | 3.1; 5.2; p.4,12 | NOT_TESTED |
| C18 | ADASYN-based ensemble được đề xuất trong bài | VERIFIED; AUTHOR_IDENTIFIED_EXTENSION | 5.2.2–5.2.3; p.12,13 | NOT_IMPLEMENTED |
| C19 | Genetic/clinical variables và disease ascertainment | VERIFIED; AUTHOR_IDENTIFIED_EXTENSION | 5.2; p.12 | OUT_OF_SCOPE_NOT_IMPLEMENTED |
| C20 | Federated learning/privacy-preserving workflow | VERIFIED; AUTHOR_IDENTIFIED_EXTENSION | 5.2.1; p.12 | OUT_OF_SCOPE_NOT_IMPLEMENTED |
| C21 | Seeds, hyperparameters và khả năng reproduction chính xác | PARTIALLY_VERIFIED; SOME_PARAMETERS_VERIFIED_REPRODUCTION_UNRESOLVED | Table 2; Table 3; 3.3; Data availability; p.6,4,13 | PARTIALLY_ADDRESSED |

Table 2 p.6 does specify several seeds/settings: RF 42, LR 0, KNN k=3, DT max_depth=50/entropy. Missing split/resampling details do not justify marking every parameter unverified. Section 3.3 p.4 is preprocessing; section 3.2 is EDA. The paper has an 80:20 split, SMOTE, PCA, several metrics and RF; claims to the contrary are rejected or narrowed.

Only C08/C09/C12 are addressed within a narrowly stated project scope. This is not a direct replication or three proofs of superiority over Chang. Other rows are partial, untested, unimplemented, out of scope, or rejected as gaps.

## Other papers retained from the initial review

| Paper / DOI | Verified scope | Status / limitations |
|---|---|---|
| An investigation of machine learning algorithms and data augmentation techniques for diabetes diagnosis using class imbalanced BRFSS dataset (2024), https://doi.org/10.1016/j.health.2023.100297 | Publisher/index identity and title | PARTIALLY_VERIFIED; cohort/methods not inspected, no deficiency asserted |
| Ullah et al. (2022), Detecting High-Risk Factors and Early Diagnosis of Diabetes Using Machine Learning Methods, https://doi.org/10.1155/2022/2557795 | Full Europe PMC JATS: §§3.1–3.3,4.1,5,6; processed BRFSS2015, 253680 source records; SMOTE-ENN; initial 70/30 split; KNN 98.363% reported accuracy | VERIFIED for those descriptions; executable ordering and independent tuning remain unresolved; no proven leakage asserted |
