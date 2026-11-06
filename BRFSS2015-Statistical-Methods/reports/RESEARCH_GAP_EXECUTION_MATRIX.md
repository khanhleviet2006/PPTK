# Research-gap execution matrix

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

Full row-specific scientific test,data requirements,module,configuration,execution,result artifact,outcome and remaining limitations are in research_gap_execution_matrix.csv. C12/C17 RESOLVED refers only to the stated design-inference and one frozen temporal evaluation scope, not elimination of all external-validity limitations. No blanket paper-superiority claim.
