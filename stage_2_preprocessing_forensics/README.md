# GIAI ĐOẠN 2: Làm sạch, Tính Chỉ số Pháp chứng & Chuẩn hóa Ngành (`stage_2_preprocessing_forensics`)

## 1. Mục tiêu Giai đoạn 2
1. Làm sạch dữ liệu chuỗi thời gian theo từng doanh nghiệp (`ticker`, `year`), xử lý chia an toàn (`safe_div`), tạo biến trễ `lag-1` không rò rỉ chéo (`year[t] - year[t-1] == 1`) và cắt ngưỡng ngoại lai cực đoan (`Winsorization [1%, 99%]` độc lập theo từng năm — chống Look-ahead Bias).
2. Tính toán **xác định 100% (Deterministic Core)** bộ 18 chỉ số pháp chứng & sức khỏe tài chính:
   - **8 biến & điểm Beneish M-Score (1999):** `DSRI`, `GMI`, `AQI`, `SGI`, `DEPI`, `SGAI`, `TATA`, `LVGI` (ngưỡng `-1.78`).
   - **4 biến & điểm Altman Emerging Market $Z''$-Score (2005, có hằng số `+3.25`):** `X1`, `X2`, `X3`, `X4` (ngưỡng chuẩn EMS: `Safe > 5.85`, `Grey 4.35–5.85`, `Distress < 4.35`).
   - **7 chỉ số Chất lượng Lợi nhuận & Đặc thù Việt Nam:** `cfo_to_ni`, `cfo_to_assets`, `accrual_ratio`, `sensitive_receivables_ratio` (`SRR`), `receivable_to_revenue`, `inventory_to_assets`, `provision_coverage_ratio` (`TK 2293`), `debt_to_assets`.
3. Chạy tự động **5 Bài Kiểm thử Đơn vị Toán học (Unit Tests)** với yêu cầu sai số `0.0000%`.
4. Chuẩn hóa 12 đặc trưng AI theo nhóm ngành ICB bằng **Peer-Group Robust Z-Score** (tự động fallback sang chuẩn toàn thị trường khi ngành có `< 10` DN).
5. Xuất báo cáo đối sánh số liệu chi tiết [`REPORT_STAGE_2_FORENSIC_METRICS.md`](REPORT_STAGE_2_FORENSIC_METRICS.md) và biểu đồ 4 khung [`stage2_forensic_distributions.png`](stage2_forensic_distributions.png).

## 2. Cấu trúc File trong Thư mục
- [`02_forensic_features.py`](02_forensic_features.py): Module tính toán xác định 100%, Unit Tests, biểu đồ 4 khung & xuất báo cáo (có thể import trực tiếp cho GĐ 3 & Web App GĐ 5).
- [`02_forensic_analysis_walkthrough.ipynb`](02_forensic_analysis_walkthrough.ipynb): Jupyter Notebook phân tích thống kê mô tả, Ma trận 4 góc phần tư và so sánh 16 ngành ICB.
- [`stage2_forensic_distributions.png`](stage2_forensic_distributions.png): Biểu đồ phân phối 4 khung chuẩn UTF-8.
- [`REPORT_STAGE_2_FORENSIC_METRICS.md`](REPORT_STAGE_2_FORENSIC_METRICS.md): Báo cáo kiểm chứng toán học, thống kê mô tả, bảng chuẩn ngành và lưu ý bắt buộc cho GĐ 3.

## 3. Cách Chạy & Tự Kiểm Chứng
```powershell
d:\SEHackathon\.venv\Scripts\python.exe stage_2_preprocessing_forensics\02_forensic_features.py
```
