# Google Colab — Run all (Python 3.13)

Cập nhật **toàn bộ** thư mục `BRFSS2015-Statistical-Methods` từ GitHub, không chỉ tải notebook. Các ZIP xuất trước bản sửa có thể thiếu bootstrap hoặc `src/data`.

Mở `notebooks/00_Run_All_Colab.ipynb` trên Colab Python 3.13 và chọn **Runtime → Run all**. Các vị trí Drive đã cung cấp được tìm tự động. Có thể cấu hình bằng cell đầu tiên, trước cell bootstrap:

```python
import os
os.environ['BRFSS_REPO'] = '/content/drive/MyDrive/PPTK-main (1)/PPTK-main/BRFSS2015-Statistical-Methods'
os.environ['BRFSS_DATA'] = '/content/drive/MyDrive/Diabetes_Statistics_2015/01_Raw_Data/LLCP2015XPT.zip'
os.environ['BRFSS_PROTOCOL'] = 'NEW_PROTOCOL'
os.environ['BRFSS_PROFILE'] = 'quick'
# Không cần bật trong quá trình phát triển:
os.environ['BRFSS_FINAL_EVALUATION'] = '0'
```

Các notebook có cùng bootstrap và tự khai báo `SYNTHETIC`, `REPO`, `PROJECT`, `DATA`, `OUT`, `PROFILE`, mode, seed và protocol. Mỗi notebook có thể chạy độc lập bằng kernel sạch. `00_Colab_Setup` chỉ kiểm tra/cài môi trường, không yêu cầu dataset. Các notebook phân tích kiểm tra dataset và codebook trước khi chạy.

Bootstrap cài requirements bằng Python của kernel, cài editable và ghi log vào `REPO/runs/bootstrap_logs`. Nếu kernel đã import phiên bản NumPy/pandas/SciPy cũ trước khi pip thay đổi chúng, chọn **Runtime → Restart session**, rồi Run all lại. Không dùng `--ignore-requires-python`. Python ngoài 3.10–3.13 dừng có giải thích. SHAP dùng pin riêng theo phiên bản Python; lock Linux Python 3.13 được lưu riêng, không thay lock lịch sử.

## File bắt buộc trên Drive

- Toàn bộ mã dự án: `pyproject.toml`, các `requirements*.txt`, `src/`, `src_extensions/`, `scripts/`, `configs/`, `docs/` (gồm source manifest và required-source inventory), `notebooks/`.
- Dữ liệu gốc `LLCP2015XPT.zip` chứa một `LLCP2015.XPT`, hoặc XPT đã giải nén. Không cần chép vào Git.
- `codebook15_llcp.pdf` cùng thư mục raw; hoặc đặt `BRFSS_CODEBOOK` tới file đó. Nếu không có file local, bootstrap chỉ tải PDF CDC đã ghi trong source manifest và kiểm tra SHA256. Nếu mạng CDC bị chặn, cần cung cấp PDF local; không bỏ kiểm tra.
- NEW_PROTOCOL không cần checkpoint lịch sử. LEGACY_RESUME cần **toàn bộ** bundle legacy cùng code/config gốc phù hợp manifest, model đã đóng băng, split và test ledger. Chỉ một `split.json` không đủ.

ZIP được giải nén có kiểm tra vào `/content/brfss_xpt/<archive_hash>`; cần khoảng 1.2 GB trống cho XPT, ngoài RAM dành cho phân tích. ZIP gốc không bị sửa. Cache chỉ được dùng lại sau kiểm tra digest; không tải dataset thay thế.

## Chức năng từng notebook

| Notebook | Phạm vi |
|---|---|
| 00 Setup | Cài đặt, kiểm tra cấu trúc, phiên bản, dependency và import; không đọc dataset |
| 00 Run All | Điều phối **core pipeline**: audit → cohort → descriptive → inference → split → develop → report |
| 01–04 | Chạy prerequisite và dừng ở audit/cohort/descriptive/inference tương ứng |
| 05 | Chạy tới split, không fit prediction preprocessing trên Test |
| 06–09 | Chạy cùng core grid với feature selection, baseline, ML và ensemble; dừng ở Train/CV; không phải bốn nghiên cứu độc lập |
| 07 baseline | Baseline logistic cùng cohort; không tự nhận là tái lập chính xác Chang |
| 10 Final Evaluation | Mặc định SKIPPED với thông báo. Chỉ chạy khi `BRFSS_FINAL_EVALUATION=1`, protocol mới được xem xét; một batch model/baseline đã đóng băng |
| 11 Report | Chạy prerequisites tới development và xuất báo cáo; **không** tự mở Test |

Master điều phối các hàm core, không mở/chạy tuần tự 12 notebook còn lại và không tự nhận chạy toàn bộ grid post-audit C01–C21. LEGACY_RESUME không tự chuyển sang protocol mới; thiếu hoặc sai artifact phải dừng. Không dùng notebook mới để tái đánh giá Test lịch sử.

Sau khi xem protocol, frozen model và Train/CV, muốn đánh giá Test của **nghiên cứu mới**, đặt `BRFSS_FINAL_EVALUATION=1` rồi chạy notebook 10 với **cùng** seed/profile/mode/OUT. Không đổi mô hình theo kết quả Test. Không xóa ledger để ép chạy lại.

Outputs mặc định: `REPO/runs/colab_new_protocol_v2` (synthetic: `colab_synthetic_v2`). Có thể đặt `BRFSS_OUT` tới thư mục Drive khác. Dùng cùng cấu hình để resume; signature khác yêu cầu thư mục mới. Không trỏ output mới vào run lịch sử. Báo cáo ghi rõ khi chưa có final metrics; số synthetic không phải bằng chứng dịch tễ.

Các notebook thực thi trên Linux Python 3.13 là bằng chứng gần nhất; việc mount Drive, mạng và Run all trên hosted Google Colab vẫn phải được xác minh riêng. Xem [báo cáo sửa lỗi](COLAB_RUN_ALL_FIX_REPORT.md).
