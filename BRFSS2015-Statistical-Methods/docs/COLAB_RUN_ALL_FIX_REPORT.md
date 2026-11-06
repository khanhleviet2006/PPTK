# Colab Run all fix report — Python 3.13

Ngày: 2026-11-06. Base commit: `2875da3a9fb51b68ed06c69ad2e7f4f1986c3768`. Commit sửa được cung cấp trong bàn giao và Git history; không tạo hash tự tham chiếu giả trong nội dung commit.

## Nguyên nhân gốc và sửa đổi

| Lỗi | Nguyên nhân có bằng chứng | Sửa |
|---|---|---|
| Python 3.13 bị chặn | `requires-python <3.13` và guard trong verifier/notebook; pip 3.13 đã tái hiện lỗi package requires a different Python | Chỉ mở `<3.14` sau khi cài wheel và chạy tests trên CPython 3.13.17 |
| Dependency mở rộng | SHAP 0.47.2 không có wheel dùng được cho cp313 | Pin `shap==0.49.1` cho Python >=3.13, giữ 0.47.2 cho Python cũ; test selector/SHAP thực tế |
| REPO không tìm được | Nhiều cell dùng cwd/parent và mặc định Drive khác nhau | Cell loader giống nhau và bootstrap dùng chung; ưu tiên explicit hợp lệ, tìm các vị trí có giới hạn và kiểm tra pyproject + source layout |
| SYNTHETIC/biến chưa khai báo | Cell phụ thuộc biến khởi tạo của cell/notebook khác | Mỗi notebook tự mount, tìm source và khởi tạo đầy đủ biến trong cell đầu tiên |
| pip editable thất bại | Metadata chặn Python 3.13; lỗi trước đây không hiển thị đủ pip output | Đã cài editable thực tế trên 3.13, không bỏ guard; bootstrap lưu stdout/stderr và báo log cùng Python đang dùng |
| Thiếu src.data | Ignore rule `data/` và filter đóng gói loại cả source package | Đã khôi phục code gốc trong commit trước; test ZIP/source archive tiếp tục xác minh; inventory runtime phát hiện mọi file thiếu |
| Thiếu split lịch sử | Git history không chứa checkpoint; split có trong archive phục hồi local | Ghi provenance/hash trong báo cáo trước; không tạo giả hoặc xuất riêng split thành bộ legacy đầy đủ; legacy vẫn audit toàn bộ artifacts |
| Master tự đánh giá Test | Bản trước đi tới report qua evaluate | Master mặc định develop + báo cáo không final; wrapper đòi `allow_final=True` khi gọi evaluate/report; notebook 10 mặc định skip và báo lý do |
| Notebook 11 bị chặn real data | Guard lịch sử ngăn cả việc tạo báo cáo | Notebook 11 tạo báo cáo core hiện tại mà không evaluate Test; kết quả chưa có được ghi unavailable |

Không thay outcome, quy tắc missing-code hay thiết kế khảo sát để làm tests pass. Không sửa các model hoặc final metrics lịch sử. Các báo cáo cũ giữ trạng thái lịch sử; báo cáo hiện tại nằm dưới OUT riêng.

## Kiến trúc và scope

Tất cả notebook dùng `scripts/notebook_bootstrap.py` (standard-library trước khi cài dependencies), kiểm tra `docs/required_source_files.json`, kiểm tra version đang load so với installed metadata, active dependency closure và imports của src/src_extensions/scripts. Global pip conflicts ngoài graph dự án được hiển thị riêng. Thiếu hay sai dependencies của nghiên cứu vẫn dừng.

Dependency graph core: audit → cohort → descriptive → inference → split → development. Report đọc artifacts hiện có. Final evaluation là nhánh **opt-in** sau phát triển/đóng băng, không phải điều kiện tạo development report. Các bước qua core pipeline vẫn giữ signature, atomic checkpoints, split seed/ID hash, model hashes và ledger một lần. Master không chạy notebook khác và không phải tất cả thí nghiệm post-audit.

Biến cấu hình và file Drive bắt buộc nằm trong [COLAB_QUICK_START.md](COLAB_QUICK_START.md). Điểm cài đặt mới có log và restart guidance. Kết quả thay đổi binary packages trong kernel đang chạy cần restart; không có cách an toàn để thay NumPy đã import mà luôn bảo đảm không restart.

## Tính hợp lệ khoa học

Train/Test isolation, codebook-only recoding, training-fold imputation/scaling/encoding/selection và SMOTENC trong pipeline được giữ nguyên. Threshold và model được chọn bằng training OOF, không dùng final metrics. CV sau chọn cấu hình là optimistic development evidence. Bootstrap prediction CI không được gọi là CI thiết kế mẫu. Inference sử dụng trọng số, strata và PSU riêng.

Binary DIABETE3=1 đối chiếu 3; pregnancy-only/borderline/unknown không bị âm thầm đưa vào âm tính chính. Ba nhóm core biểu thị self-reported no/borderline/diabetes; không phải xác nhận sinh hóa. Module prediabetes không suy diễn người chưa có thông tin là âm tính. Không xem feature importance là nhân quả hoặc accuracy đơn lẻ là cải thiện so với Chang.

NEW_PROTOCOL chỉ tạo nghiên cứu nội bộ mới với protocol/signature/split manifest riêng. Độ chồng lấp với Test lịch sử không được mặc định bằng 0; đây không phải validation độc lập của model cũ. Không chuyển legacy sang new âm thầm. Legacy thiếu checkpoint, code gốc hoặc ledger hợp lệ phải dừng. Không tái chạy final test thật trong lần sửa này.

## Bằng chứng kiểm thử

Bằng chứng máy đọc và notebook có outputs: `reports/colab_py313_validation/`.

| Mức | Trạng thái |
|---|---|
| STATIC_PASS | Compile, Ruff lint/format, structure inventory, internal import audit, notebook schema |
| UNIT_TEST_PASS | Suite Python 3.13: 66 passed, 2 skipped (R chưa cấu hình) |
| INTEGRATION_PASS | Synthetic pipeline, leakage guards, split/ledger/resume và baseline trong suite |
| LOCAL_NOTEBOOK_EXECUTION_PASS | PASS — cả 13 notebook chạy 2 kernel sạch Python 3.13.17; master source-only chạy 2 lần, không mở Test |
| COLAB_RUNTIME_VERIFIED | UNVERIFIED — không có session hosted Colab/Drive credentials ở môi trường này |
| REAL_DATA_VERIFIED | PASS có giới hạn — XPT gốc 441.456 dòng/330 cột; audit, thống kê, suy luận, Train/CV và development report; không final evaluation |

Môi trường sạch dùng CPython 3.13.17 Linux, kernel Jupyter có argv trỏ chính xác tới interpreter đó. Lock mới giữ phiên bản môi trường đã cài, không thay lock 3.12 lịch sử. Wheel-only install đã phát hiện SHAP thiếu wheel; lần test ban đầu thiếu optional dependencies có hai lỗi xgb/shap, sau cài đủ cả hai test đã pass. Không che giấu các bước thất bại trong quá trình sửa.

## Giới hạn

Hosted Google Colab, mount Drive thực, đường truyền CDC từ tài khoản người dùng và restart UI thực tế: **UNVERIFIED**. Đường dẫn có dấu cách, kernel sạch, cài editable và kiểm tra stale loaded version được kiểm tra gần nhất trên Linux. Final real-data evaluation không chạy; không có claim hiệu năng mới. ZIP lớn cần đủ dung lượng giải nén và dataframe cần RAM thích hợp. R-reference tests chưa cấu hình cho lượt này, nên báo SKIPPED thay vì PASS.

Các protected artifacts legacy được đối chiếu với archive trước mở rộng: tất cả model, manifest, split, frozen metrics và ledger trong danh sách PROTECTED giữ nguyên mã băm. Git hiện chỉ có branch main, không có tag (kiểm tra bằng git ls-remote --heads --tags). Notebook archive và báo cáo cũ là lịch sử, không nằm trong 13 notebook hoạt động được chứng nhận ở lượt này.

CLI mặc định cũng dừng ở develop; evaluate/report đòi --final-evaluation. Root GitHub Actions workflow chạy matrix Python 3.12/3.13, có cài optional dependencies trước các tests selector. Kết quả Actions hosted của commit mới phải xem riêng trên GitHub; không coi định nghĩa workflow là bằng chứng đã chạy Actions.

## File thay đổi trong lượt này

- `pyproject.toml`
- `requirements-research-extensions.txt`
- `requirements-tested-colab-linux-py313.lock`
- `README.md`
- `QUICK_START.md`
- `.github/workflows/tests.yml`
- `docs/required_source_files.json`
- `docs/COLAB_QUICK_START.md`
- `docs/COLAB_RUN_ALL_FIX_REPORT.md`
- `docs/COLAB_END_TO_END.md`
- `docs/COLAB_RUNBOOK.md`
- `scripts/notebook_bootstrap.py`
- `scripts/colab_runtime.py`
- `scripts/verify_environment.py`
- `scripts/validate_notebooks.py`
- `scripts/run_pipeline.py`
- `tests/unit/test_notebook_bootstrap.py`
- `notebooks/00_Colab_Setup.ipynb`
- `notebooks/00_Run_All_Colab.ipynb`
- `notebooks/01_Data_Audit.ipynb`
- `notebooks/02_Cohort_and_Outcome.ipynb`
- `notebooks/03_Descriptive_Statistics.ipynb`
- `notebooks/04_Statistical_Inference.ipynb`
- `notebooks/05_Prediction_Preprocessing.ipynb`
- `notebooks/06_Feature_Selection.ipynb`
- `notebooks/07_Baseline_Reproduction.ipynb`
- `notebooks/08_Advanced_ML.ipynb`
- `notebooks/09_Ensemble_Experiments.ipynb`
- `notebooks/10_Final_Evaluation.ipynb`
- `notebooks/11_Research_Report.ipynb`
- `.github/workflows/brfss-tests.yml` tại root repository: matrix CI cho thư mục dự án.
- `reports/colab_py313_validation/`: lock/environment/install log, notebook đã chạy, kết quả audit và bảo toàn legacy.
