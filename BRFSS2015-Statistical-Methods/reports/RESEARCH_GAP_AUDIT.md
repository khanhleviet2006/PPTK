> Historical pre-extension audit. Evidence classifications remain applicable; implementation statuses below describe that earlier snapshot. Current execution/scientific status: reports/RESEARCH_GAP_EXECUTION_MATRIX.md and research_gap_execution_matrix.csv.

# Kiểm toán Research Gap — BRFSS2015-Statistical-Methods

Ngày kiểm toán: 06/11/2026, múi giờ Asia/Bangkok. Báo cáo này đối chiếu bằng chứng bài gốc, mã đã có và kết quả đã đóng băng; không chạy lại nghiên cứu.

## Kết luận chính

Không có bằng chứng rằng dự án đã giải quyết toàn bộ các gap của Chang hoặc vượt Chang trên một benchmark tương thích. Có ba hạng mục được xử lý **trong phạm vi dự án**: quy trình CV/selection trước test (C08), CI và paired comparison có giới hạn (C09), và original-data survey inference (C12). Chúng không tương đương ba chứng minh ưu thế so với bài báo.

Hai nhận định phải bác bỏ: Chang chỉ dùng accuracy (C06) và Chang không có train/test holdout (C07). Bài đã có SMOTE, PCA, sensitivity và RF; vì vậy cũng không được nói bài không xử lý imbalance, không feature selection, không xét minority detection hoặc hoàn toàn không có ensemble. Leakage thực thi vẫn chỉ là HYPOTHESIS (C04).

Thêm thuật toán là mở rộng thực nghiệm, không tự tạo novelty. Trong quick real-data CV, các ensemble không thắng mô hình LR được chọn. Calibration, macro-F1, precision và accuracy của selected policy kém comparator mặc dù sensitivity/balanced accuracy tăng. Chưa có faithful Chang reproduction, external/temporal validation, full real standard/extended run, SHAP, ADASYN ensemble hay clinical/privacy experiment.

## 1. Phạm vi, nguồn và quy tắc phân loại

Bài được đối chiếu: Chang V, Ganatra MA, Hall K, Golightly L, Xu QA (2022). An assessment of machine learning models and algorithms for early prediction and diagnosis of diabetes using health indicators. Healthcare Analytics 2:100118. DOI: [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118). Đã đọc bản typeset 14 trang, do tác giả đăng qua ResearchGate; DOI, tiêu đề, tác giả và journal khớp trang 1. Đây là bản PDF bài gốc được lưu lại, không phải PDF do dự án tái tạo. Không khẳng định đã so byte-for-byte với publisher download vì truy cập trực tiếp publisher bị chặn.

Nguồn tải: [author-posted PDF](https://www.researchgate.net/profile/Victor-Chang-14/publication/365201083_An_assessment_of_machine_learning_models_and_algorithms_for_early_prediction_and_diagnosis_of_diabetes_using_health_indicators/links/636eab022f4bca7fd050ab55/An-assessment-of-machine-learning-models-and-algorithms-for-early-prediction-and-diagnosis-of-diabetes-using-health-indicators.pdf). Bản lưu: [Chang_2022_100118.pdf](evidence/literature/Chang_2022_100118.pdf). SHA256: `861f7ea4f8c109e0d5941d878e9bada41c3a074675559033079c402cfbfe791c`. Trang PDF 1–14 trùng số trang in. Không dùng số trang suy từ HTML/search snippets.

Nguồn nội bộ rà soát: reports/final_report.md, reports/RESULTS_INTERPRETATION.md, docs/LITERATURE_REVIEW.md, docs/RESEARCH_GAP_MATRIX.md, docs/literature_evidence.csv, RESEARCH_PROTOCOL, EXPERIMENT_PLAN, SCIENTIFIC_AUDIT, configs và src tương ứng. Hướng tương lai chỉ tìm thấy khi đọc đầy đủ bài được gắn origin riêng C18–C20; không coi đó là cam kết cũ của dự án.

**VERIFIED**: phát biểu hẹp được nội dung bài xác nhận, gồm cả bất nhất báo cáo hoặc hướng future work. **PARTIALLY_VERIFIED**: một phần có bằng chứng nhưng chưa đủ kết luận hạn chế toàn bộ quy trình. **UNVERIFIED**: gap chưa có căn cứ; nếu có phản chứng thì ghi rõ CONTRADICTED. **HYPOTHESIS**: cơ chế/giải thích cần kiểm chứng. `evidence_classification=VERIFIED_PDF_CONTENT` chỉ xác nhận đã đọc đúng trích đoạn, không biến nghi vấn gap thành VERIFIED.

Trạng thái triển khai độc lập với độ tin cậy gap: ADDRESSED_WITHIN_SCOPE = có code và empirical outputs cho mục tiêu được giới hạn; PARTIALLY_ADDRESSED = thiếu bước hoặc chưa chứng minh tác dụng; NOT_TESTED = chưa có empirical validation tương ứng; NOT_IMPLEMENTED/OUT_OF_SCOPE = chưa có phương pháp; NOT_A_VALIDATED_GAP = gap bị bác bỏ, không được tính là đã giải quyết. Kiểm thử synthetic chỉ chứng minh vận hành, không chứng minh lợi ích thực tế.

## 2. Toàn bộ danh mục và trạng thái

| ID | Gap/phát biểu được audit | Phân loại gap | Trạng thái dự án |
|---|---|---|---|
| [C01](#c01) | Cohort, cỡ mẫu và provenance chưa nhất quán | VERIFIED | PARTIALLY_ADDRESSED |
| [C02](#c02) | Định nghĩa nhãn diabetes/prediabetes chưa thống nhất | VERIFIED | PARTIALLY_ADDRESSED |
| [C03](#c03) | Tính hợp lý và tác động của quy trình missing-data/preprocessing | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| [C04](#c04) | Nghi vấn leakage do preprocessing/SMOTE trước split | HYPOTHESIS | PARTIALLY_ADDRESSED |
| [C05](#c05) | Đánh giá chiến lược mất cân bằng và phân bố test | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| [C06](#c06) | Khẳng định Chang chỉ dùng accuracy | UNVERIFIED | NOT_A_VALIDATED_GAP |
| [C07](#c07) | Khẳng định Chang không có train/test holdout | UNVERIFIED | NOT_A_VALIDATED_GAP |
| [C08](#c08) | CV phát triển và truy vết selection trước final test | VERIFIED | ADDRESSED_WITHIN_SCOPE |
| [C09](#c09) | Thiếu uncertainty/paired comparison trong bảng kết quả báo cáo | VERIFIED | ADDRESSED_WITHIN_SCOPE |
| [C10](#c10) | Minority detection, threshold và cost tradeoff | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| [C11](#c11) | Calibration chưa được báo cáo trong evaluation đã đọc | VERIFIED | PARTIALLY_ADDRESSED |
| [C12](#c12) | Thiết kế survey và adjusted population inference | PARTIALLY_VERIFIED | ADDRESSED_WITHIN_SCOPE |
| [C13](#c13) | Robustness: missingness, outcome và demographic subgroups | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| [C14](#c14) | Interpretability và hướng mở rộng SHAP | VERIFIED | PARTIALLY_ADDRESSED |
| [C15](#c15) | Đa dạng feature selection và top-k ablation | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |
| [C16](#c16) | Mở rộng ensembles/boosters và kiểm tra lợi ích | VERIFIED | PARTIALLY_ADDRESSED |
| [C17](#c17) | External/temporal validity và clinical generalizability | PARTIALLY_VERIFIED | NOT_TESTED |
| [C18](#c18) | ADASYN-based ensemble được đề xuất trong bài | VERIFIED | NOT_IMPLEMENTED |
| [C19](#c19) | Genetic/clinical variables và disease ascertainment | VERIFIED | OUT_OF_SCOPE_NOT_IMPLEMENTED |
| [C20](#c20) | Federated learning/privacy-preserving workflow | VERIFIED | OUT_OF_SCOPE_NOT_IMPLEMENTED |
| [C21](#c21) | Seeds, hyperparameters và khả năng reproduction chính xác | PARTIALLY_VERIFIED | PARTIALLY_ADDRESSED |

Phân bố phân loại: VERIFIED: 10, PARTIALLY_VERIFIED: 8, HYPOTHESIS: 1, UNVERIFIED: 2. Phân bố triển khai: PARTIALLY_ADDRESSED: 12, NOT_A_VALIDATED_GAP: 2, ADDRESSED_WITHIN_SCOPE: 3, NOT_TESTED: 1, NOT_IMPLEMENTED: 1, OUT_OF_SCOPE_NOT_IMPLEMENTED: 2.

### Các hạng mục đã xử lý với giới hạn

C08: quy trình quick CV/selection/holdout có bằng chứng và trace. C09: paired CI cho selected và comparator đã đóng băng; bootstrap chỉ conditional respondents. C12: inference weighted/design-based trên cohort gốc, với numerical R reference. Không mục nào chứng minh rằng toàn bộ quy trình Chang đã được sửa hoặc paper benchmark bị vượt.

### Các hạng mục chưa hoàn tất hoặc chưa thử nghiệm

C01–C05, C10–C11, C13–C16 và C21 mới xử lý một phần. C17 chưa external/temporal validation. C18 chưa ADASYN ensemble. C19 và C20 chưa có dữ liệu/phương pháp clinical/genetic hoặc federated/privacy và ngoài phạm vi hiện tại. C06–C07 bị phản chứng, không thuộc danh sách thành tích.

## 3. Ngân hàng bằng chứng trực tiếp từ bài gốc

Các trích ngắn dưới đây là bằng chứng dùng chung cho các gap; mỗi chi tiết gap ở mục 4 nêu DOI, section, trang và mã E tương ứng. Với phát biểu về thứ không được báo cáo, phạm vi rà soát được chỉ rõ, không dùng sự vắng một từ khóa làm bằng chứng duy nhất.

| Mã | Mục/bảng | Trang in = PDF | Trích nguyên văn ngắn |
|---|---|---|---|
| E01 | 3.1 | 4 | “It is a clean dataset of 70,692” |
| E02 | 3.1 | 4 | “This dataset has 253,680 records” |
| E03 | 3.1 | 4 | “they have prediabetes or diabetes” |
| E04 | Appendix, Table A.1 | 13 | “0 = no diabetes, 1 = diabetes” |
| E05 | 3.3 | 4 | “Before feeding the data to the model, it must be partitioned into train and test sets.” |
| E06 | 3.3 | 4 | “5% of null values were added by using sample functions” |
| E07 | 4.3 | 10 | “The dataset is split in an 80:20 ratio” |
| E08 | 4.3 | 11 | “Precision, Recall, and Specificity are used alongside accuracy” |
| E09 | 4.3, Table 4 | 12 | “RF 82.26% 83.47% 80.45% 84.07% 82.26% 17.74%” |
| E10 | 5.2 | 12 | “cross-validation techniques should be used” |
| E11 | 5.2 | 12 | “include SHAP values” |
| E12 | 3.2 | 4 | “PCA is used as the feature selection tool” |
| E13 | 5.2.3 | 13 | “ADASYN-based ensemble classifiers can be developed” |
| E14 | 5.2 | 12 | “gene and clinical variables” |
| E15 | 5.2.1 | 12 | “FML should be employed” |
| E16 | Table 2 | 6 | “a random state of 42” |
| E17 | Table 2 | 6 | “a random state of 0” |
| E18 | Table 2 | 6 | “A k-value of 3” |
| E19 | Data availability | 13 | “The data that has been used is confidential.” |
| E20 | 3.3 | 4 | “80:20 ratio for training and testing” |
| E21 | 3.3.1 | 5 | “SMOTE [31] is a statistical sampling technique” |
| E22 | 4.3, Table 4 | 12 | “Classifier Accuracy Precision Sensitivity Specificity F1-Score Hamming loss” |

**Sửa nguồn dẫn cũ:** §3.2 là EDA, còn §3.3 mới là Data pre-processing (trang 4). Table 2 (trang 6) đã nêu RF random_state=42, LR random_state=0, KNN k=3, DT max_depth=50/entropy. Chưa đủ settings để exact reproduction nhưng không còn hợp lệ khi đánh dấu toàn bộ seeds/hyperparameters UNVERIFIED. Table 3 thiếu split trong pseudocode, song §3.3 nói partition trước model; phải giữ cả hai khi bàn leakage.

**Phạm vi negative evidence:** Table 4 (trang 12) chỉ có point metrics và không có CI/paired tests; §3.4, §4.3, Table 4/Fig.19 không trình bày calibration; §3.1/§3.4/Table A.1 không mô tả survey-design variance. Không suy thành tác giả chắc chắn chưa làm bất kỳ thủ tục đó trong code không công khai. Nhận định “không kiểm soát survey” là mở rộng mục tiêu inference, không tự động là lỗi của một bài prediction.

## 4. Đối chiếu chi tiết từng gap với code và thực nghiệm

<a id="c01"></a>

### C01 — Cohort, cỡ mẫu và provenance chưa nhất quán

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.1; Data availability; trang 4, 13. Bằng chứng: E01: tr. 4, §/bảng 3.1; E02: tr. 4, §/bảng 3.1; E19: tr. 13, §/bảng Data availability; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** SUPPORTED_REPORTING_AMBIGUITY. §3.1 nêu cả 70.692 lẫn 253.680 và mô tả cân bằng/không cân bằng; đường dẫn Kaggle công khai ở chú thích trang 4 cùng tuyên bố dữ liệu confidential ở trang 13. Đây là bất nhất báo cáo đã xác minh; không xác định được cohort thực thi chỉ từ bài.

**Đã triển khai:** Audit CDC XPT, mã định danh bang+SEQNO, cohort và checksum; reproduction Dataset B tách riêng.

**Artifacts:** `src/data/ingest.py`; `src/audit/validation.py`; `runs/real_final_quick/audit.json`; `runs/real_final_quick/cohort.json`; `scripts/reproduce_baseline.py`.

**Kết quả thực tế:** Nguồn dự án: 441.456 × 330; cohort binary 422.558; complete case 243.529. Không có kết quả reproduction Dataset B thật.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Cần file nguồn/cohort/mã xử lý của Chang và chạy reproduction có provenance. Làm rõ cohort dự án không đồng nghĩa giải được cohort của Chang.

<a id="c02"></a>

### C02 — Định nghĩa nhãn diabetes/prediabetes chưa thống nhất

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.1; Appendix Table A.1; trang 4, 13. Bằng chứng: E03: tr. 4, §/bảng 3.1; E04: tr. 13, §/bảng Appendix, Table A.1; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** SUPPORTED_REPORTING_AMBIGUITY. §3.1 gộp prediabetes/diabetes ở nhãn 1, trong khi Appendix ghi nhãn 1 là diabetes. Không có cơ sở chọn một cách diễn giải làm nhãn chính xác của dữ liệu đã chạy.

**Đã triển khai:** Binary DIABETE3 1 vs 3; loại borderline/pregnancy; sensitivity và core-three riêng, không coi thiếu PREDIAB1 là âm tính.

**Artifacts:** `src/data/outcomes.py`; `runs/real_final_quick/cohort.json`; `runs/real_final_quick/borderline_sensitivity_or.csv`; `runs/real_three_inference/multinomial_rrr.csv`.

**Kết quả thực tế:** Đã có binary và core-three survey inference thật. Outcome của dự án khác nhãn gộp trong §3.1 nên không so trực tiếp accuracy.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Chưa tái lập nhãn đầu ra thực thi của Chang; phenotype module PREDIAB1 còn thiếu manifest địa lý/phiên bản/trọng số.

<a id="c03"></a>

### C03 — Tính hợp lý và tác động của quy trình missing-data/preprocessing

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.3; 3.3.1; trang 4, 5. Bằng chứng: E06: tr. 4, §/bảng 3.3; E21: tr. 5, §/bảng 3.3.1; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** PROCEDURE_VERIFIED_HARM_UNTESTED. Bài mô tả thêm 5% null rồi xóa hàng thiếu và MinMax scaling. Thao tác này được xác minh; chưa chứng minh rằng nó gây sai lệch hay định lượng ảnh hưởng lên kết quả.

**Đã triển khai:** Mã missing theo codebook; median/mode trong fold cho prediction; complete case và deterministic-imputation sensitivity cho inference; SMOTENC cho biến hỗn hợp.

**Artifacts:** `src/features/engineering.py`; `src/modeling/models.py`; `src/statistics/analysis.py`; `runs/real_final_quick/missingness.csv`; `runs/real_final_quick/sensitivity_or.csv`.

**Kết quả thực tế:** BMI OR complete case 1,8754; median/mode sensitivity 1,8316. Đây không phải multiple imputation và không phải đối chứng preprocessing của Chang.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Cần thí nghiệm cùng cohort/order và uncertainty của imputation. Không kết luận MAR, không kết luận pipeline Chang sai từ mô tả đơn lẻ.

<a id="c04"></a>

### C04 — Nghi vấn leakage do preprocessing/SMOTE trước split

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.3; 4.3; Table 3; trang 4, 6, 10. Bằng chứng: E05: tr. 4, §/bảng 3.3; E07: tr. 10, §/bảng 4.3; nội dung trích ở mục 3.

**Phân loại:** HYPOTHESIS. **Kết luận về phát biểu:** EXECUTION_ORDER_NOT_ESTABLISHED. §4.3 kể normalization/SMOTE trước khi nhắc split, nhưng §3.3 nói partition trước khi đưa dữ liệu vào mô hình. Table 3 không thể hiện split. Thứ tự kể chuyện không chứng minh thứ tự code và có phản chứng phải ghi nhận.

**Đã triển khai:** Pipeline fold-local, split/test checksum, frozen-model hashes, test-access ledger và scientific leakage tests.

**Artifacts:** `src/modeling/splits.py`; `src/modeling/models.py`; `src/evaluation/final.py`; `tests/scientific/test_leakage.py`; `runs/real_final_quick/test_access.json`.

**Kết quả thực tế:** Quy trình phòng ngừa leakage của dự án đã triển khai/kiểm thử; ledger ghi một batch evaluation. Không có thí nghiệm định lượng leakage của Chang.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Cần code hoặc log thực thi của Chang. Không cáo buộc leakage; không tuyên bố đã sửa hay đo được sai lệch của bài đó.

<a id="c05"></a>

### C05 — Đánh giá chiến lược mất cân bằng và phân bố test

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.3; 3.3.1–3.3.2; 4.3; trang 4, 5, 10. Bằng chứng: E21: tr. 5, §/bảng 3.3.1; E07: tr. 10, §/bảng 4.3; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** SMOTE_EXISTS_COMPARATIVE_GAP_NARROWED. Chang có SMOTE và thảo luận ADASYN; nhận định không xử lý imbalance là sai. Khoảng trống có thể bảo vệ là so sánh có kiểm soát các chiến lược trên test giữ phân bố gốc; bài chưa làm rõ phân bố test sau resampling.

**Đã triển khai:** So sánh LR none/class_weight/random_under/SMOTENC trong cùng training CV; chỉ resample trong fold.

**Artifacts:** `src/modeling/experiments.py`; `src/modeling/models.py`; `runs/real_final_quick/development.json`.

**Kết quả thực tế:** CV balanced accuracy: class_weight 0,750592; random_under 0,742842; SMOTENC 0,727271; none tối ưu ngưỡng 0,719743. Các giá trị này là development, không phải kết quả test độc lập từng chiến lược.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Chưa so tất cả chiến lược trên full training; chưa ablate class weighting và threshold riêng; ADASYN chưa triển khai.

<a id="c06"></a>

### C06 — Khẳng định Chang chỉ dùng accuracy

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 4.3; Table 4; Fig.19; trang 10, 11, 12, 13. Bằng chứng: E08: tr. 11, §/bảng 4.3; E09: tr. 12, §/bảng 4.3, Table 4; nội dung trích ở mục 3.

**Phân loại:** UNVERIFIED. **Kết luận về phát biểu:** CONTRADICTED_BY_VERIFIED_EVIDENCE. Bài có precision, sensitivity, specificity, F1, hamming loss, ROC và PR curves. Phản chứng đã xác minh; không được gọi accuracy-only là research gap của Chang.

**Đã triển khai:** Dự án cũng báo cáo nhiều metrics.

**Artifacts:** `src/evaluation/metrics.py`; `runs/real_final_quick/final_metrics.json`.

**Kết quả thực tế:** Có multi-metric evaluation thật, nhưng đây không phải khắc phục một thiếu sót accuracy-only đã tồn tại ở Chang.

**Trạng thái:** NOT_A_VALIDATED_GAP. **Phần còn thiếu:** Loại bỏ cách diễn đạt accuracy-only; chỉ nói bổ sung balanced accuracy, uncertainty hoặc calibration chưa báo cáo rõ.

<a id="c07"></a>

### C07 — Khẳng định Chang không có train/test holdout

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.3; 4.3; trang 4, 10. Bằng chứng: E20: tr. 4, §/bảng 3.3; E07: tr. 10, §/bảng 4.3; nội dung trích ở mục 3.

**Phân loại:** UNVERIFIED. **Kết luận về phát biểu:** CONTRADICTED_BY_VERIFIED_EVIDENCE. Bài nêu train/test 80:20. Điều chưa rõ là tuning, resampling và việc chọn mô hình có độc lập với test hay không; không được suy thành không có test.

**Đã triển khai:** Dự án có 80:20 split, sau đó giới hạn training quick.

**Artifacts:** `src/modeling/splits.py`; `runs/real_final_quick/split.json`.

**Kết quả thực tế:** Test dự án có 84.512 người. Sự hiện diện của split không tự chứng minh mọi bước của bất kỳ pipeline nào đều độc lập.

**Trạng thái:** NOT_A_VALIDATED_GAP. **Phần còn thiếu:** Phân biệt có holdout với có evaluation độc lập sau selection; dùng C08 cho phần còn thiếu bằng chứng.

<a id="c08"></a>

### C08 — CV phát triển và truy vết selection trước final test

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 5.2; 3.3; Table 2; trang 12, 4, 6. Bằng chứng: E10: tr. 12, §/bảng 5.2; E20: tr. 4, §/bảng 3.3; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** AUTHOR_IDENTIFIED_EXTENSION. Tác giả đề xuất cross-validation trong future work. Điều này xác minh hướng mở rộng; không chứng minh không có bất kỳ CV nào trong code. Full-data nested tuning độc lập không được mô tả đủ.

**Đã triển khai:** Stratified 3-fold training CV, threshold grid OOF, hash chọn model trước final evaluation; không coi CV score được dùng selection là unbiased.

**Artifacts:** `configs/experiments.yaml`; `src/modeling/experiments.py`; `runs/real_final_quick/cv_splits.json`; `runs/real_final_quick/development.json`; `runs/real_final_quick/frozen.json`.

**Kết quả thực tế:** 17 experiments thật; CV winner đã lưu là LR class_weight, threshold 0,40, CV BA 0,750592. Audit kiểm lại winner chỉ từ development.json; không chọn từ final metrics.

**Trạng thái:** ADDRESSED_WITHIN_SCOPE. **Phần còn thiếu:** Giải quyết ở phạm vi quy trình quick của dự án; chưa chứng minh superiority so Chang, chưa full/nested standard experiment.

<a id="c09"></a>

### C09 — Thiếu uncertainty/paired comparison trong bảng kết quả báo cáo

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 4.3, Table 4; trang 10, 11, 12. Bằng chứng: E22: tr. 12, §/bảng 4.3, Table 4; E09: tr. 12, §/bảng 4.3, Table 4; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** NARROW_REPORTING_GAP. Table 4 chỉ báo cáo point estimates; không kèm CI hoặc paired comparison ở bảng/phần kết quả này. Không suy ra tác giả chưa bao giờ tính chúng ở ngoài bài.

**Đã triển khai:** Paired respondent bootstrap selected vs fixed baseline và McNemar; OR/RRR dùng CI design-based riêng.

**Artifacts:** `src/evaluation/metrics.py`; `runs/real_final_quick/final_metrics.json`; `runs/real_final_quick/adjusted_or.csv`.

**Kết quả thực tế:** Δ BA 0,172527; CI paired 95% [0,168412;0,175846], 100 replicates quick. Đây là CI conditional fixed models/đơn vị người trả lời, không phải survey prediction CI.

**Trạng thái:** ADDRESSED_WITHIN_SCOPE. **Phần còn thiếu:** Phạm vi giải quyết chỉ một so sánh đã định trước; chưa uncertainty do training/selection, chưa full population predictive variance; chưa so trực tiếp Chang.

<a id="c10"></a>

### C10 — Minority detection, threshold và cost tradeoff

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 4.3, Table 4; trang 11, 12. Bằng chứng: E09: tr. 12, §/bảng 4.3, Table 4; E08: tr. 11, §/bảng 4.3; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** SENSITIVITY_ALREADY_REPORTED_EXTENSION_IS_TRADEOFF. Chang đã báo sensitivity RF 80,45%; không có bằng chứng rằng bỏ qua minority detection hoặc con số đó là không đủ lâm sàng. Hướng mở rộng là BA/threshold/precision–specificity/calibration tradeoff, không phải chữa một thiếu sót đã được chứng minh.

**Đã triển khai:** Class weighting và threshold chọn trong training OOF; test một frozen policy so baseline LR threshold 0,50.

**Artifacts:** `runs/real_final_quick/frozen.json`; `runs/real_final_quick/final_metrics.json`; `runs/real_final_quick/development.json`.

**Kết quả thực tế:** Test sensitivity 0,855088 vs 0,179219, nhưng specificity 0,647117 vs 0,977932 và accuracy 0,674662 vs 0,872148. Không có đối chứng test unweighted LR với ngưỡng cũng tối ưu từ CV.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Chưa tách tác động trọng số và ngưỡng; chưa clinical utility/cost validation; không dùng test hiện tại để chọn ngưỡng mới.

<a id="c11"></a>

### C11 — Calibration chưa được báo cáo trong evaluation đã đọc

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.4; 4.3; Table 4; Fig.19; trang 5, 10, 11, 12, 13. Bằng chứng: E22: tr. 12, §/bảng 4.3, Table 4; E09: tr. 12, §/bảng 4.3, Table 4; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** NARROW_REPORTING_GAP. Metrics/curves được liệt kê không có Brier, log loss hoặc reliability calibration curve. ROC/PR curves không thay thế đánh giá calibration. Kết luận chỉ về nội dung đã báo cáo, không về code không công khai.

**Đã triển khai:** Brier/log loss, calibration bins và figure được tạo; không có bước recalibration được thí nghiệm.

**Artifacts:** `src/evaluation/metrics.py`; `runs/real_final_quick/calibration.csv`; `runs/real_final_quick/final_metrics.json`.

**Kết quả thực tế:** Selected Brier 0,172771 vs 0,093632; log loss 0,514274 vs 0,304767: kém hơn. Đánh giá được thực hiện, gap cải thiện calibration chưa được giải quyết.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Cần calibration model fit trong training và validation mới; không refit/rethreshold bằng test đã xem.

<a id="c12"></a>

### C12 — Thiết kế survey và adjusted population inference

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.1; 3.4; Table A.1; trang 4, 5, 13. Bằng chứng: E01: tr. 4, §/bảng 3.1; E04: tr. 13, §/bảng Appendix, Table A.1; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** OBJECTIVE_EXTENSION_NO_DESIGN_PROCEDURE_REPORTED. Bài dùng processed cohort và feature list không có weights/strata/PSU; phần phương pháp đã đọc không mô tả variance design-based. Đây là mở rộng estimand của dự án, không bằng chứng một nghiên cứu ML đã làm sai standard errors.

**Đã triển khai:** _LLCPWT/_STSTR/_PSU; Taylor PSU score covariance; weighted Table 1/prevalence; logistic OR và core-three multinomial RRR; tham chiếu R độc lập.

**Artifacts:** `src/statistics/survey.py`; `src/statistics/analysis.py`; `tests/scientific/test_r_reference.py`; `runs/real_final_quick/prevalence.json`; `runs/real_final_quick/adjusted_or.csv`; `runs/real_three_inference/multinomial_rrr.csv`; `reports/logs/pytest.log`.

**Kết quả thực tế:** Prevalence domain 10,7052% [10,5303%;10,8826%]; BMI OR 1,8754 [1,7936;1,9610]. Kiểm thử R có log PASS. Không phải unconditional national prevalence hay causal effect.

**Trạng thái:** ADDRESSED_WITHIN_SCOPE. **Phần còn thiếu:** Chưa chứng minh novelty so toàn bộ y văn; complete-case selection, fixed calibrated weights và inference functional form còn hạn chế; prediction CIs không design-based.

<a id="c13"></a>

### C13 — Robustness: missingness, outcome và demographic subgroups

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.3; 4.3; Table 4; trang 4, 10, 11, 12. Bằng chứng: E06: tr. 4, §/bảng 3.3; E22: tr. 12, §/bảng 4.3, Table 4; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** LIMITED_REPORTING_EVIDENCE. Các phần này không cung cấp systematic sensitivity/subgroup performance analysis tương ứng mục tiêu dự án; đó là khoảng trống báo cáo có giới hạn. Không đồng nhất mô tả EDA với robustness study.

**Đã triển khai:** Complete-case/median-mode/borderline sensitivities; core-three inference; descriptive test subgroups sex/race/age.

**Artifacts:** `runs/real_final_quick/sensitivity_or.csv`; `runs/real_final_quick/borderline_sensitivity_or.csv`; `runs/real_final_quick/subgroups.csv`; `runs/real_three_inference/multinomial_rrr.csv`.

**Kết quả thực tế:** BMI OR 1,8754 / 1,8316 / 1,8381 theo ba định nghĩa xử lý. Có 25 subgroup rows; không có confirmatory subgroup equivalence/fairness test.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Chưa full MICE/MNAR, chưa adjusted inference riêng subgroup, chưa predictive robustness qua nhiều splits/seeds hay external cohorts.

<a id="c14"></a>

### C14 — Interpretability và hướng mở rộng SHAP

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 5.2; 3.2; 3.3.3; trang 12, 4, 5. Bằng chứng: E11: tr. 12, §/bảng 5.2; E12: tr. 4, §/bảng 3.2; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** AUTHOR_IDENTIFIED_EXTENSION. Tác giả đề xuất SHAP và đã có PCA/EDA; không thể nói hoàn toàn không interpretability. Gap cụ thể là mở rộng/cải thiện diễn giải có kiểm chứng.

**Đã triển khai:** Adjusted OR/RRR và training-internal permutation importance cho model được chọn.

**Artifacts:** `src/statistics/analysis.py`; `src/modeling/experiments.py`; `runs/real_final_quick/feature_importance.csv`; `runs/real_final_quick/adjusted_or.csv`.

**Kết quả thực tế:** Có OR/RRR thật và permutation importance thật với 2 repeats quick. Chưa có SHAP và chưa kiểm nghiệm stability/usefulness của explanations.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Không gọi permutation importance là SHAP hoặc causal effect; chưa local explanations hay kiểm định độ ổn định feature rankings.

<a id="c15"></a>

### C15 — Đa dạng feature selection và top-k ablation

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.2; 3.3.3; Table 3; trang 4, 5, 6. Bằng chứng: E12: tr. 4, §/bảng 3.2; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** PCA_EXISTS_DIVERSITY_EXTENSION. Bài đã dùng PCA và mô tả 8 thành phần/biến; nhận định không feature selection là sai. Phần mở rộng có cơ sở là so nhiều selectors trên cùng protocol, không phải chứng minh PCA thất bại.

**Đã triển khai:** MI/L1/tree k=10 đã chạy dữ liệu thật; clinical/permutation/RFE/interactions và k=5/10/15/20 có code và synthetic standard execution.

**Artifacts:** `src/features/engineering.py`; `src/modeling/experiments.py`; `runs/real_final_quick/development.json`; `runs/synthetic_standard_verified/development.json`.

**Kết quả thực tế:** CV BA real: full LR 0,719743; MI10 0,716727; tree10 0,712092; L1_10 0,676016. 39 synthetic standard experiments không chứng minh empirical benefit. Chưa có matched PCA baseline.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Chưa full real top-k/permutation/RFE/interactions, chưa chứng minh selector nào cải thiện trên independent final test. k là encoded columns, không số biến gốc.

<a id="c16"></a>

### C16 — Mở rộng ensembles/boosters và kiểm tra lợi ích

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 5.2; 5.2.3; 3.4; trang 12, 13, 5. Bằng chứng: E13: tr. 13, §/bảng 5.2.3; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** AUTHOR_EXTENSION_BENEFIT_IS_HYPOTHESIS. Tác giả đề xuất phát triển ensemble, nhưng RF trong chính bài đã là ensemble. Không nói bài hoàn toàn không ensemble và không coi thêm thuật toán là novelty hay mặc định improvement.

**Đã triển khai:** RF/Extra Trees/boosters/feature ensemble/soft voting/stacking đều đã chạy training CV real.

**Artifacts:** `src/modeling/models.py`; `runs/real_final_quick/development.json`.

**Kết quả thực tế:** CV BA: feature ensemble 0,724564; soft voting 0,723140; stacking 0,703108, đều dưới frozen selected LR 0,750592. Không có test metrics riêng của các ensemble.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Không chứng minh ensemble cải thiện; chưa full training matched budgets/hyperparameter search và chưa faithful RF reproduction của Chang.

<a id="c17"></a>

### C17 — External/temporal validity và clinical generalizability

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 3.1; 5.2; trang 4, 12. Bằng chứng: E01: tr. 4, §/bảng 3.1; E14: tr. 12, §/bảng 5.2; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** SINGLE_COHORT_LIMITATION_EXTENSION. Đánh giá được mô tả trên BRFSS2015 subset và future work đề nghị thêm dữ liệu/biến lâm sàng. Đây là bằng chứng giới hạn một cohort; không chứng minh hiệu năng sẽ thất bại ở nơi khác.

**Đã triển khai:** Có subgroup diagnostics trong cùng năm, không có independent population/time.

**Artifacts:** `runs/real_final_quick/run_manifest.json`; `runs/real_final_quick/subgroups.csv`; `reports/VERIFICATION.md`.

**Kết quả thực tế:** Không có dataset/year/site external hoặc temporal validation thật. Subgroup trong cùng holdout không giải quyết external validity.

**Trạng thái:** NOT_TESTED. **Phần còn thiếu:** Cần cohort năm khác/site khác và protocol transportability/calibration; chưa được phép tuyên bố clinical deployment.

<a id="c18"></a>

### C18 — ADASYN-based ensemble được đề xuất trong bài

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 5.2.2–5.2.3; trang 12, 13. Bằng chứng: E13: tr. 13, §/bảng 5.2.3; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** AUTHOR_IDENTIFIED_EXTENSION. Future work chỉ đích danh ADASYN-based ensemble; SMOTENC, class_weight hay generic stacking không tương đương hướng này.

**Đã triển khai:** Không có ADASYN trong model factory/experiment plan đang thực thi.

**Artifacts:** `src/modeling/models.py`; `configs/experiments.yaml`; `runs/real_final_quick/development.json`.

**Kết quả thực tế:** Không có kết quả ADASYN hoặc ADASYN ensemble trên dữ liệu thật hay synthetic.

**Trạng thái:** NOT_IMPLEMENTED. **Phần còn thiếu:** Chưa triển khai/thử nghiệm; với biến phân loại cần thiết kế resampling hợp lệ và đánh giá training-only trước validation mới.

<a id="c19"></a>

### C19 — Genetic/clinical variables và disease ascertainment

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 5.2; trang 12. Bằng chứng: E14: tr. 12, §/bảng 5.2; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** AUTHOR_IDENTIFIED_EXTENSION. Tác giả đề xuất dữ liệu gene/clinical. Các biến self-report BRFSS trong dự án không đáp ứng hướng này và không xác nhận chẩn đoán sinh học.

**Đã triển khai:** Dự án chỉ dùng self-reported cross-sectional BRFSS; không có gene/glucose/HbA1c.

**Artifacts:** `configs/variables.yaml`; `docs/DATA_DICTIONARY.md`.

**Kết quả thực tế:** Không có kết quả triển khai hướng này; adjusted association không thay cho xác nhận lâm sàng.

**Trạng thái:** OUT_OF_SCOPE_NOT_IMPLEMENTED. **Phần còn thiếu:** Cần dữ liệu/thiết kế nghiên cứu khác; không tính là đóng góp đã giải quyết.

<a id="c20"></a>

### C20 — Federated learning/privacy-preserving workflow

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục 5.2.1; trang 12. Bằng chứng: E15: tr. 12, §/bảng 5.2.1; nội dung trích ở mục 3.

**Phân loại:** VERIFIED. **Kết luận về phát biểu:** AUTHOR_IDENTIFIED_EXTENSION. Bài thảo luận FML như future direction về privacy. Data leakage/privacy ở đây khác train-test contamination.

**Đã triển khai:** Pipeline centralized trên public survey; không có federated protocol/privacy experiment.

**Artifacts:** `src/modeling/models.py`; `docs/EXPERIMENT_PLAN.md`.

**Kết quả thực tế:** Không có federated learning, differential privacy hay privacy-leakage evaluation.

**Trạng thái:** OUT_OF_SCOPE_NOT_IMPLEMENTED. **Phần còn thiếu:** Không gộp với C04 và không nhận đã giải quyết bằng preprocessing trong fold.

<a id="c21"></a>

### C21 — Seeds, hyperparameters và khả năng reproduction chính xác

**Nguồn:** DOI [10.1016/j.health.2022.100118](https://doi.org/10.1016/j.health.2022.100118); mục Table 2; Table 3; 3.3; Data availability; trang 6, 4, 13. Bằng chứng: E16: tr. 6, §/bảng Table 2; E17: tr. 6, §/bảng Table 2; E18: tr. 6, §/bảng Table 2; E19: tr. 13, §/bảng Data availability; nội dung trích ở mục 3.

**Phân loại:** PARTIALLY_VERIFIED. **Kết luận về phát biểu:** SOME_PARAMETERS_VERIFIED_REPRODUCTION_UNRESOLVED. Table 2 cung cấp RF random_state=42, LR=0, KNN k=3, DT max_depth=50/entropy. Cụm RF ten trees as depth còn mơ hồ; split/resampling seeds và toàn bộ settings chưa đủ rõ. Không giữ nhãn toàn bộ seeds/hyperparameters UNVERIFIED.

**Đã triển khai:** Project seed/config/CV/split/model hashes; reproduction script gắn nhãn approximate và khác params/cách preprocessing.

**Artifacts:** `configs/project.yaml`; `src/modeling/models.py`; `scripts/reproduce_baseline.py`; `runs/real_final_quick/run_manifest.json`.

**Kết quả thực tế:** Project seed 2015; RF 80 trees/min_leaf5, DT depth6, khác Table 2; Dataset B thật chưa chạy. Synthetic reproduction test chỉ xác minh code.

**Trạng thái:** PARTIALLY_ADDRESSED. **Phần còn thiếu:** Cần faithful reproduction với settings đã xác minh, giải quyết RF ambiguity và source/cohort trước khi so hiệu năng với Chang.

## 5. Kết quả đã đóng băng và những gì có thể kết luận

Dataset A: 441.456 records/330 columns. Cohort binary 422.558; complete case inference 243.529. Prediction split: 338.046 training-pool, capped 4.000 cho quick; final test 84.512. Dự án dùng 19 raw predictors được định nghĩa riêng, khác processed feature/cohort/label của Chang. Full real core-three inference có output; three-class prediction chỉ được xác minh synthetic.

Selected policy đã đóng băng: `logistic`, `class_weight`, threshold 0.40; CV BA 0.750592. Comparator là unweighted same-cohort LR, threshold 0,50, không phải reproduction RF của Chang. Training-CV unweighted LR ở threshold đã chọn 0,20 có BA 0,719743; điều đó khác baseline cố định 0,50 dùng trong final comparison.

| Metric test đã lưu | Selected | Fixed baseline | Hiệu selected − baseline |
|---|---|---|---|
| accuracy | 0.674662 | 0.872148 | -0.197487 |
| balanced_accuracy | 0.751103 | 0.578576 | +0.172527 |
| sensitivity | 0.855088 | 0.179219 | +0.675869 |
| specificity | 0.647117 | 0.977932 | -0.330815 |
| precision | 0.270032 | 0.553532 | -0.283500 |
| f1 | 0.410447 | 0.270770 | +0.139677 |
| macro_f1 | 0.592895 | 0.600351 | -0.007456 |
| roc_auc | 0.830679 | 0.829565 | +0.001115 |
| pr_auc | 0.412887 | 0.414846 | -0.001959 |
| brier | 0.172771 | 0.093632 | +0.079138 |
| log_loss | 0.514274 | 0.304767 | +0.209507 |

Δ BA = 0.172527, paired conditional bootstrap 95% CI [0.168412; 0.175846], 100 replicates. Đây là hiệu hai **policies** cùng cohort, không cô lập tác động class weighting vì threshold cũng khác. Không có test comparison với unweighted LR được threshold-tune tương đương; audit không tính thêm comparison đó từ test đã mở.

ROC-AUC tăng rất nhỏ (khoảng 0,001115), không phải bước nhảy về discrimination. Precision, accuracy, specificity, macro-F1, PR-AUC, Brier và log loss đi theo hướng kém hơn. Binary-positive F1 tăng nhưng macro-F1 giảm; không được dùng từ improved F1 không chỉ rõ định nghĩa. Brier/log loss càng thấp càng tốt. Không gọi calibration gap đã giải quyết chỉ vì đã tạo calibration plot.

Selected accuracy 67,47% không đạt target 82,26%. Baseline nội bộ accuracy 87,21% cũng không chứng minh vượt Chang vì cohort/outcome/evaluation khác. Chang RF sensitivity 80,45% không thể so trực tiếp với 85,51% của dự án. CI predictive là respondent bootstrap conditional trên fixed models, không bao gồm selection/training uncertainty hay complex-survey prediction uncertainty; chỉ 100 replicates quick nên precision Monte Carlo còn hạn chế.

Lưu ý feature count: trường k=10 trong experiment original là tham số không được dùng để cắt features; RankingSelector(original) giữ toàn bộ cột sau encoding. Chỉ MI/L1/tree k=10 thực sự chọn 10 encoded columns; không gọi original là bộ 10 biến gốc.

## 6. Đóng góp khoa học thực sự và mức độ mới

1. **Bằng chứng thực nghiệm có giới hạn:** so sánh một operating policy đã chọn bằng CV với comparator định trước trên cùng holdout cho thấy minority detection/BA tăng, đồng thời specificity, PPV và calibration giảm. Kết quả tradeoff này có giá trị báo cáo; không phải thuật toán mới hoặc clinical-utility validation.

2. **Phân tích dịch tễ đã thực thi:** weighted prevalence và adjusted prevalence OR/RRR cùng design variance; BMI OR 1,8754 (CI 1,7936–1,9610) và các sensitivity đã có. Đây là ước lượng associational cho một domain xác định. Không có systematic novelty review đủ chứng minh phát hiện BMI/diabetes là mới; không có causal inference.

3. **Giá trị phương pháp và reproducibility:** protocol cố định, fold-local preprocessing, survey score covariance có numerical R reference, frozen artifacts và ledger. Đây là chất lượng nghiên cứu/engineering được chứng minh trong dự án; không phải một estimator mới hay bằng chứng quy trình không công khai của Chang chắc chắn sai.

4. **Forensic literature clarification:** xác minh bất nhất cohort/label, sửa section references và metadata tham số từ PDF, đồng thời bác bỏ các gap bị gán quá mức. Đây là kết quả audit có chứng cứ; chưa tái dựng được pipeline của tác giả.

5. **Chưa phải đóng góp đã chứng minh:** thêm XGBoost/LightGBM/CatBoost/voting/stacking; SHAP chưa có; ADASYN/federated/genetic data chưa có; top-k full real chưa chạy; superiority so với paper, external validity và calibration improvement chưa chứng minh. Negative CV findings của ensemble được giữ nguyên, không chọn lại theo final test.

## 7. Integrity và giới hạn audit

Audit chỉ đọc PDF, source/config, development logs và final artifacts đã lưu. Winner và threshold được kiểm lại bằng **training-CV scores**, rồi so với frozen.json trước khi đọc final_metrics để mô tả. Không fit/refit, predict, resample, tính metrics lại từ test rows, tìm threshold từ test, hoặc chạy final_evaluate. Final test ledger vẫn evaluation_count=1. SHA256 source/config, frozen models, splits, CV indices, result JSON, checkpoints và ledger được so trước/sau; xem evidence/research_gap_audit_provenance.json.

Ledger/hash cho thấy artifacts nhất quán và audit không sửa chúng; không phải bằng chứng tuyệt đối về mọi truy cập thủ công trong quá khứ. Full-cohort inference có trước prediction split, nên các lựa chọn prediction chỉ có thể xem là prespecified theo protocol/metadata; audit không dựng một preregistration công khai có timestamp độc lập.

Permutation importance là exploratory trên training-internal split sau khi model class đã được chọn bằng development; không phải independent confirmatory explanation evaluation. Với permutation selector, preprocessing của outer training được thực hiện trước internal split; outer validation vẫn ở ngoài fold, nhưng không nên tuyên bố mọi inner validation hoàn toàn không dùng thông tin preprocessing của inner holdout.

Không chạy thêm ML để lấp gap sau khi đã xem test. Các bước tương lai phải có kế hoạch training/validation trước, giữ công khai lịch sử test cũ; đổi output folder/split trên cùng respondents không tự tạo external test độc lập.

## 8. Tệp đối chiếu và cách kiểm lại

- [research_gap_evidence.csv](research_gap_evidence.csv): 21 rows, DOI/section/pages/quotes, classification, implementation, result và phần còn thiếu. Bản cùng nội dung ở project-root research_gap_evidence.csv.

- docs/chang_gap_catalog.json: danh mục machine-readable; PDF bản lưu giữ nguyên và source SHA256.

- reports/evidence/research_gap_audit_provenance.json: protected artifacts, source identity và kết quả kiểm không đổi model/test.

- `python scripts/audit_research_gaps.py --verify-only`: xác minh quotes trong đúng trang PDF, paths, CSV, hashes và selection từ training CV; không chạy mô hình hoặc test evaluation.
