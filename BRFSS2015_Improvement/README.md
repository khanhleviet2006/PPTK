# BRFSS 2015 — Feature Optimization & ML Improvement

**Trạng thái: chưa có dữ liệu BRFSS trong môi trường; chưa chạy nghiên cứu và chưa có kết quả lâm sàng.** Mã chạy binary riêng biệt. Không sử dụng kết quả synthetic làm số liệu báo cáo.

## Cài và chạy trên Colab (Python 3.12)

Mở `notebooks/BRFSS2015_Improvement.ipynb`. Mount Google Drive bằng giao diện Colab. Notebook dùng ZIP do người dùng chỉ định: `/content/drive/MyDrive/Diabetes_Statistics_2015/01_Raw_Data/LLCP2015XPT.zip`, kiểm tra file tồn tại và preflight XPT trước khi Train. Lưu dự án và output mới vào Drive để tránh mất khi Colab ngắt phiên.

```bash
python -m pip install -r requirements.txt
python tests/smoke.py
python src/research.py inspect --data /path/LLCP2015XPT.zip --schema schema.reviewed.json --output /path/new_preflight.json
python src/research.py train --data /path/LLCP2015XPT.zip --schema /path/schema.reviewed.json --output /path/new_run_001 --folds 5 --hours 60 --trials 12
# FINAL TEST ĐANG KHÓA. Chỉ mở khóa riêng sau khi cấu hình và giao thức đã được rà soát:
python src/research.py final --data /path/LLCP2015XPT.zip --output /path/new_run_001 --unlock-final
```

Trong workspace hiện tại có thể dùng `/workspace/brfss-venv/bin/python`. Chỉ load joblib từ các run đáng tin cậy. `train` từ chối ghi đè thư mục đã tồn tại; `final` có khóa một lần và kiểm tra hash dữ liệu, cấu hình, pipeline, split. Khi final lỗi, chẩn đoán nguyên nhân và giữ hồ sơ; không xóa khóa để thử cấu hình khác dựa trên Test.

## Bắt buộc trước thí nghiệm thật

1. Xác minh file là BRFSS 2015 gốc, xuất xứ, SHA256 và quyền sử dụng. Không tự tải hoặc thay bằng bộ Kaggle 21 biến/đã cân bằng. CSV đã biến đổi cần codebook chuyển đổi riêng và không được gọi là bản gốc.
2. Đọc **codebook chính thức 2015**: https://www.cdc.gov/brfss/annual_data/annual_2015.html (tìm LLCP 2015 codebook và calculated variables). Truy cập PDF từ môi trường cloud bị proxy chặn (CONNECT 403). Không có trang/bảng nào được xác minh trong lần cập nhật này; xem `00_Audit/codebook_review.md`.
3. `schema.reviewed.json` đã được chuẩn bị dưới dạng **bản nháp chưa được duyệt**, với `codebook_reviewed=false`, danh sách `unverified_items` và trạng thái từng biến. Các mã trong đó chỉ là đề xuất, không được viện dẫn như kết quả đối chiếu CDC. Có thể bắt đầu lại từ `schema.template.json` nếu cần. Với từng biến: ghi loại, missing/refused/don't know, miền hợp lệ, recode và trích dẫn trang/bảng codebook. Không coi mọi số là liên tục. Ví dụ `recode: {"88": 0}` CHỈ dùng khi codebook xác nhận 88 là zero days; không mặc định áp dụng cho các biến khác. Missing được chuyển trước recode và kiểm tra miền hợp lệ sau recode.
4. Chỉ đặt `codebook_reviewed=true` sau khi rà soát thực tế. Code từ chối chạy nếu chưa xác nhận. Thêm biến mới phải có `rationale`, `codebook_reference`, `leakage_review: "safe"`. Danh sách trong `00_Audit/candidate_review.csv` ghi rõ đề xuất missing/valid/recode/scale, lý do loại leakage, nguồn dự kiến và nguồn chưa xác minh. Trường `source_page` để trống có chủ đích.
5. Nhãn gợi ý để **xác minh**: DIABETE3=1 diabetes, =3 no diabetes; =2 gestational-only, =4 prediabetes và mã không trả lời bị loại theo cohort định trước. Đây là binary diabetes vs no diabetes, không phải gộp prediabetes vào controls. Nếu chọn cohort khác, định nghĩa trước trong schema và không dùng kết quả Test cũ để quyết định.
6. Điền `weight`, `strata`, `psu` bằng tên cột thật nếu có; các cột này bị cấm làm predictor. Đây là nghiên cứu dự đoán không trọng số, **không** suy luận đại diện dân số. `population_inference=true` bị từ chối. Phân tích survey-weighted/strata/PSU yêu cầu quy trình survey riêng.
7. Nếu có split cũ hợp lệ, thêm `split_column` với train/test và ghi lịch sử Test cũ trong `cohort_definition`; split được tái dùng. Split có cùng respondent ID hoặc profile trùng ở hai phía bị từ chối, không tự chia lại. Nếu Test đã dùng để chọn mô hình, phải có holdout độc lập trước mọi tuyên bố confirmatory.

## Giao thức đã định trước

- Không bỏ mẫu khó; chỉ loại theo nhãn/cohort đã ghi trước. Giữ các dòng trùng nhưng khóa cùng nhóm. Nhóm là liên thông của profile predictor trùng và `group_column` nếu có. Không có respondent ID thì không thể nhận diện mọi repeated respondent; đây là giới hạn cần báo cáo.
- Split ngoài ~80/20 bằng stratified group fold cố định, seed 2026. Sau đó cùng 5 stratified group CV folds trên Train cho mọi cấu hình. Cần đủ nhóm của hai lớp trong từng fold. Audit nhãn/miền giá trị không học tham số; mọi imputation, scaling, encoding và selection học trong fold Train.
- Baseline LR; B0 median/mode + OHE; B1 numeric missing indicators + categorical missing category; B2 ordinal theo `order` được xác minh; B3 thêm BMI group và log1p số ngày sức khỏe kém nếu có roles. CatBoost dùng native categories, có missing category. Không resampling Test; hiện không dùng resampling.
- MI, L1, RFE (step 20%), permutation trong validation **nội bộ của outer training fold**, RF importance. Xếp hạng theo biến gốc, cộng importance của các one-hot cùng biến; cách cộng có thể thiên lệch về cardinality. Top 5/10/15/20 được cắt theo số biến thực có. Ranking là theo phương pháp, không phải hiệu ứng nhân quả. Xuất fold rankings và mean pairwise Jaccard stability.
- D0 original; D1 Age×BMI, BMI×Activity, Age×Activity; D2 composite; D3 cả hai; D4 chọn top 20 từ tập kết hợp bằng RF. Roles chỉ bật khi đã recode tuổi/BMI/hoạt động sang đơn vị thích hợp; không nhân mã ordinal nhóm tuổi như tuổi thật. BMI `scale` chỉ đổi đơn vị cho BMI grouping (ví dụ xác minh 0.01 với BMI nhân 100); các hệ số tương tác chỉ là biến dự đoán. Với biến tuổi theo nhóm dùng `type=ordinal` và order; muốn so sánh tuổi thật/nhóm cần cấu hình schema riêng, cùng split trước khi mở Test.
- Composites là **số đếm điều kiện khám phá, trọng số bằng nhau**, không phải thang đo y sinh đã kiểm chứng: `composites: {"cardio_count": {"hypertension": [1], "cholesterol": [1]}}`. Missing một thành phần ⇒ missing composite; không tự coi missing là không nguy cơ. Có thể khai báo lifestyle_count, health_status_count bằng các điều kiện được định nghĩa và giải thích trước. Tên ví dụ phải thay bằng cột thật.
- Sáu mô hình chạy cấu hình cơ bản; sau đó tuning tối đa hai họ boosting có CV balanced accuracy tốt nhất, Optuna 12 trials/họ mặc định. Mỗi trial dùng cùng CV protocol. 60 giờ cho sweep/tuning, dự phòng 12 giờ audit/final/report. Giới hạn là **soft** giữa folds/trials; một fit đang chạy không bị kill. Dùng 2 CPU threads; OHE dense có thể tốn RAM, cần theo dõi (ưu tiên CAT native cho nhiều biến). Chưa benchmark thời gian/RAM trên dữ liệu thật; không bảo đảm hoàn tất mọi cấu hình trong 3 ngày.
- Chọn theo CV: sensitivity ≥ baseline − 0.02; accuracy gần nhau trong 0.002 thì ưu tiên balanced accuracy, PR-AUC, sensitivity. Threshold cố định 0.5. Điều kiện này chỉ giữ sensitivity tương đối với baseline, không phải ngưỡng đủ dùng lâm sàng. Không có cam kết clinical safety. Không chọn ngưỡng trên Test. Nếu yêu cầu sensitivity tối thiểu lâm sàng thì phải định trước và chỉnh giao thức chỉ bằng Train.
- Save fitted pipeline và baseline, sau đó `final` đánh giá đúng hai mô hình. CI 95% chênh lệch accuracy dùng paired group bootstrap 2000 lần, giữ tất cả thành viên nhóm. Không mặc định individual IID và không đại diện cho thiết kế survey BRFSS. CV được dùng nhiều lần để chọn cấu hình nên có selection optimism; final holdout độc lập là trọng tâm. Các ablation là exploratory; không có multiplicity-adjusted claims.
- Ensemble optional chưa triển khai, để dành ngân sách cho kiểm chứng mô hình đơn. Không có voting/stacking dùng Test.

## Artifact

Mỗi run chứa `data_audit.csv`, `cohort.json`, `split.npz`, `feature_ranking.csv`, `feature_selection_results.csv`, `feature_engineering_results.csv`, `model_cv_comparison.csv`, `best_model_config.json`, `ablation_results.csv`, `research_summary.md`, fold scores, failures, versions, SHA256, frozen hashes và hai pipelines joblib. `final_test_results.csv`, test probabilities, confusion matrices (TN/FP/FN/TP) và paired CI chỉ xuất sau lệnh final. PR-AUC ở đây là **average precision**, không phải trapezoidal area. CSV bỏ qua cấu hình thất bại; phải đọc `failures.json`, không coi thiếu dòng là đã chạy.

Báo cáo tự sinh theo 10 mục nghiên cứu, kèm bảng CV và bảng Test riêng. Không khẳng định vượt Chang et al. (2022) công bằng khi chưa xác minh cohort, nhãn, prevalence, split và metric tương đương. Accuracy >82.26% chỉ là mục tiêu; ngay cả majority-class predictor trên dữ liệu lệch lớp cũng có thể có accuracy cao. Luôn đọc sensitivity, balanced accuracy và PR-AUC.

## Hạn chế hiện tại

Chưa có raw data hoặc codebook đã rà soát, nên chưa có baseline BRFSS, feature ranking thực, Optuna thực hay Final Test. Chưa xác minh giao thức Chang. Đã có đường dẫn Drive do người dùng cung cấp, nhưng file không có trong môi trường cloud này. Notebook sẽ kiểm tra ZIP, header, CRC/hash và các cột thật khi chạy trong Colab. Việc đầy đủ hóa schema cần codebook và raw-domain audit thật; không tự xác nhận các đề xuất hiện tại.

Ví dụ cấu trúc một mục trong `features` (minh họa schema, **không phải codebook BRFSS**):

```json
{
  "SAMPLE_CONTINUOUS": {
    "type": "continuous",
    "missing_codes": [999],
    "valid_range": [0, 100],
    "recode": {},
    "scale": 1,
    "leakage_review": "safe",
    "rationale": "Replace with biomedical rationale and measurement timing",
    "codebook_reference": "Replace with verified 2015 variable/page/table"
  }
}
```

Biến categorical dùng `valid_values` thay `valid_range`; ordinal thêm `order`. `roles` ánh xạ tên vai trò tới tên cột, ví dụ `{"bmi":"SAMPLE_CONTINUOUS"}` chỉ sau khi đơn vị và mã đã xác minh. Tất cả `valid_values`, `order`, và điều kiện composite được diễn giải **sau recode**. Nhãn không dùng recode predictor.


## Bản cập nhật ZIP và khóa Test

`src/data_io.py` đọc `.zip` chứa đúng một XPT, không gọi `extract`/`extractall`. Kiểm tra đường dẫn thành viên, symlink, encrypted member, kích thước giải nén tối đa 4 GiB, tỷ lệ nén tối đa 200 và CRC. Stream giải nén vào file tạm trên đĩa local, chỉ để parser có thể seek; file tự xóa cả khi lỗi, không tạo bản XPT trong Drive và không đụng ZIP gốc. Cần đủ temporary disk cho kích thước XPT thực. CRC/hash giúp xác định toàn vẹn/định danh, không chứng minh nguồn gốc khi chưa có trusted reference hash.

`inspect` không cần duyệt codebook vì không học/chọn/đánh giá mô hình. Nó đọc metadata và tối đa 1.000 dòng mẫu nội bộ, ghi tên cột, số dòng XPT báo cáo, member/container hashes, cột còn thiếu và trạng thái review. **Đây chưa phải full raw-domain audit.** Báo cáo preflight không được ghi đè. `train` vẫn bị chặn nếu `codebook_reviewed=false`, còn `unverified_items`, hoặc leakage review chưa đạt; kiểm tra miền raw trước recode nếu có `raw_valid_values`.

Notebook sao chép schema nháp vào Drive một lần; chạy lại không ghi đè bản người dùng đã sửa. Notebook không có ô gọi final. CLI `final` mặc định khóa, yêu cầu `--unlock-final` rõ ràng, ngoài marker chống chạy lặp và kiểm tra hash code/schema/pipeline. Không mở khóa trong giai đoạn này.

Giao thức seed/split/5-fold CV, lựa chọn bằng Train, threshold và tuning budget giữ nguyên. Sửa lỗi biên BMI: `pd.cut(..., right=False)` để 18.5 thuộc normal, 25 thuộc overweight, 30 thuộc obese thay vì rơi vào nhóm dưới. Đây là sửa triển khai ngưỡng, không điều chỉnh dựa trên Test. BMI scale trong schema hiện chỉ dùng khi tạo nhóm B3; predictor `_BMI5` và tương tác giữ đơn vị raw trước fold scaling, đã ghi rõ trong schema.

Shortlist hiện có 8 biến gốc active. Top 10/15/20 bị giới hạn về 8; chúng không đại diện các tập 10/15/20 biến khác nhau. `_AGEG5YR` được ghi nhận làm phương án ordinal chưa bật, tránh đưa mã nhóm vào tương tác tuổi theo năm. Composite chưa được bật vì định nghĩa và review còn thiếu. Không được coi D2 rỗng là bằng chứng composite không hiệu quả.

Kiểm thử bổ sung: `python -m unittest discover -s tests -p 'test_*.py'`. Fixture XPT chỉ có 5 dòng giả lập, không có bệnh nhân BRFSS. Không dùng kết quả kiểm thử phần mềm để khẳng định Accuracy >82.26% hay cải thiện công bằng so với Chang et al. (2022).

`audit-codes --data ZIP --schema schema.reviewed.json --output NEW_DIR` chạy độc lập khi schema chưa duyệt: đếm mã raw trên **toàn bộ** dữ liệu cho shortlist định trước và nhãn, xuất `raw_code_counts.csv`/`raw_code_audit.json`. Không split, fit, chọn biến hoặc đánh giá mô hình; không coi tần suất quan sát là xác minh codebook. Notebook chạy bước này trước review gate; cần đủ RAM cho full XPT.
