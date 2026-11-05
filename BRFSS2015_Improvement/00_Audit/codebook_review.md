# CDC BRFSS 2015 — trạng thái đối chiếu

**Chưa thể hoàn tất đối chiếu nguồn. `codebook_reviewed=false`.** Tên `schema.reviewed.json` là tên file đích theo workflow, không biểu thị rằng nội dung đã được duyệt. Tất cả mã cụ thể trong schema/CSV hiện là **đề xuất chưa xác minh**, không phải trích xuất từ codebook đã đọc.

Nguồn chính thức dự kiến:

- Landing page: https://www.cdc.gov/brfss/annual_data/annual_2015.html
- PDF dự kiến: https://www.cdc.gov/brfss/annual_data/2015/pdf/codebook15_llcp.pdf

Lần kiểm tra 2026-11-05: request qua proxy được cấu hình, TLS verification giữ nguyên, thất bại `CONNECT tunnel failed, response 403`. Không tải được PDF; không có checksum tài liệu hoặc trang/bảng nào đã được đọc để viện dẫn. Không thể xác nhận tính hiện hành của URL PDF. Không lấy thông tin từ bộ Kaggle hoặc codebook năm khác để thay thế. Đã lưu bản nháp bổ sung `www.cdc.gov` và `cdc.gov` vào allowed domains; snapshot runtime vẫn chưa có các domain này. Người dùng cần review/lưu cấu hình mạng; publish cấu hình môi trường nếu giao diện yêu cầu. Draft save không tự áp dụng runtime hoặc xuất bản.

## Đối chiếu từng ứng viên — tất cả còn PENDING_SOURCE_REVIEW

|Biến|Đề xuất cần kiểm tra|Leakage/timing và quyết định|
|---|---|---|
|DIABETE3|1 diabetes; 3 no; loại 2 gestational-only, 4 prediabetes, 7/9/system missing|Chỉ là target binary. Chưa xác minh định nghĩa từng nhãn hoặc giao thức Chang.|
|_BMI5|Range đề xuất 1..9999; system missing; scale 0.01 kg/m² cho nhóm BMI|Active dạng liên tục raw. Phải kiểm tra calculated-variable rules/giá trị BMI không hợp lý; không tự coi 9999 là missing.|
|_AGE80|Range đề xuất 18..80; hệ số 1; kiểm tra imputation/top-coding|Active tuổi theo năm; cần xác minh cả ý nghĩa imputed/top-coded.|
|_AGEG5YR|Order đề xuất 1..13; 14 missing; hệ số 1|Phương án ordinal inactive, không diễn giải mã nhóm như số tuổi.|
|EXERANY2|Valid raw đề xuất 1/2; 7/9 missing; 2→0, 1 giữ nguyên|Active categorical binary sau recode; kiểm tra hoạt động ngoài công việc, recall window và skip patterns.|
|PHYSHLTH|Raw đề xuất 1..30/88; 77/99 missing; 88→0|Active continuous days; system blank không đồng nghĩa zero.|
|MENTHLTH|Raw đề xuất 1..30/88; 77/99 missing; 88→0|Active continuous days; phải kiểm tra độc lập với PHYSHLTH.|
|HIGHBP3|Đề xuất 1/2/3/4 categorical; 7/9 missing; không recode|Giữ riêng pregnancy-only và borderline theo đề xuất; cần kiểm tra chẩn đoán sau diabetes/reverse causation.|
|TOLDHI2|Đề xuất 1/2 categorical; 7/9 missing; không recode|Cần kiểm tra screening eligibility, blank/skip, thời điểm diagnosis; chưa được gắn safe.|
|SMOKE100|Đề xuất 1/2 categorical; 7/9 missing; không recode|Lifetime exposure, không mặc định current smoker; source/timing review pending.|
|INSULIN|Chưa xác minh mã/miền; không điền mã đoán cho biến bị loại|Loại bảo thủ vì thông tin điều trị có thể trực tiếp tiết lộ target.|
|DIABAGE2|Chưa xác minh mã/miền; không điền mã đoán cho biến bị loại|Loại bảo thủ vì tuổi chẩn đoán điều kiện trên target.|
|_LLCPWT / _STSTR / _PSU|Tên vai trò weight/strata/PSU đề xuất; chưa xác minh domain/định nghĩa hoặc cột thực|Chỉ metadata, cấm predictor. Workflow không làm suy luận survey population.|

Nguồn dẫn ở mức **URL dự kiến** được ghi cho từng biến trong schema và candidate_review.csv. `citation_page=null` / `source_page` rỗng là các dẫn nguồn còn thiếu, không phải lỗi trình bày. `verification_status=UNVERIFIED_PROPOSAL`, `leakage_review=pending` cho mọi active feature. Không được chỉ sửa cờ tổng thành true.

## Dữ liệu thật chưa truy cập

Đường dẫn người dùng cung cấp: `/content/drive/MyDrive/Diabetes_Statistics_2015/01_Raw_Data/LLCP2015XPT.zip`. `/content/drive` không được gắn trong cloud workspace hiện tại. Chưa biết XPT member thật, hash, số dòng/cột, missing distributions, prior split hoặc lịch sử sử dụng Test. Notebook Colab mới sẽ kiểm tra ZIP trực tiếp và lưu preflight vào Drive, không ghi đè ZIP hoặc giải nén thủ công.

## Điều kiện để hoàn tất review

1. Truy cập PDF CDC thật, ghi URL resolved, document/version, SHA256, trang và bảng của từng biến/target/design variable. Kiểm tra calculated variables cùng questionnaire khi cần.
2. Xác nhận từng đề xuất missing/refused/don't know/system missing, miền raw và sau recode, scale/top coding; sửa proposal theo nguồn, không theo hiệu năng Test.
3. Kiểm tra XPT metadata và full raw-domain audit của dữ liệu thật. Preflight 1.000 dòng không chứng minh mọi mã trong toàn bộ dữ liệu hợp lệ. Không suy ra missing codes chỉ từ tần suất quan sát.
4. Ghi lịch sử split/Test trước đây và tái sử dụng split hợp lệ nếu có. Không tự chia lại dựa trên điểm Test cũ. Review diagnosis-time ambiguity; xác định rõ concurrent-status prediction, không tuyên bố incident-risk forecasting.
5. Chỉ sau khi giải quyết các mục mới ghi active feature `verification_status=VERIFIED`, `leakage_review=safe`, cập nhật citations, bỏ mục đã giải quyết khỏi `unverified_items`, rồi đặt `codebook_reviewed=true`. Không tự duyệt toàn bộ từ việc download thành công.
6. Giữ Final Test khóa. So sánh baseline và các biến thể bằng Train/CV theo protocol cũ. Comparability với Chang et al. (2022) vẫn chưa xác minh.
