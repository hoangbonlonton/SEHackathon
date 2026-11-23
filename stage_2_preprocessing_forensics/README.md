# GIAI ĐOẠN 2: Làm sạch, Tính Chỉ số Pháp chứng & Chuẩn hóa Ngành (`stage_2_preprocessing_forensics`)

## 1. Mục tiêu Giai đoạn 2
1. Làm sạch dữ liệu chuỗi thời gian theo từng doanh nghiệp (`ticker`, `year`), xử lý chia an toàn (`safe_divide`), tính biến trễ 1 kỳ ($t-1$) không rò rỉ chéo và cắt ngưỡng ngoại lai cực đoan (`Winsorization 1% - 99%`).
2. Tính toán **xác định 100% (Deterministic)** bộ 15 chỉ số pháp chứng và sức khỏe tài chính:
   - **8 biến Beneish M-Score (1999):** `DSRI`, `GMI`, `AQI`, `SGI`, `DEPI`, `SGAI`, `TATA`, `LVGI` và tổng điểm `beneish_m_score`.
   - **4 biến Altman Emerging Market $Z''$-Score (2005):** `X1`, `X2`, `X3`, `X4` và tổng điểm `altman_z_double_prime`.
   - **Chỉ số Chất lượng Dòng tiền & Đặc thù Việt Nam:** `cfo_to_ni`, `accrual_ratio`, `sensitive_receivables_ratio` (`SRR`), `receivable_to_revenue`, `inventory_to_assets`.
3. Chuẩn hóa theo nhóm ngành ICB bằng **Peer-Group Robust Z-Score** (dựa trên `Median` và `MAD` của từng ngành).
4. Xuất báo cáo đối sánh số liệu chi tiết [`REPORT_STAGE_2_FORENSIC_METRICS.md`](REPORT_STAGE_2_FORENSIC_METRICS.md).

## 2. Cấu trúc File trong Thư mục
- [`02_forensic_features.py`](02_forensic_features.py): Module tính toán chỉ số pháp chứng, kiểm thử Unit Test toán học và lưu bảng đặc trưng vào `../data_store/processed/`.
- [`02_forensic_analysis_walkthrough.ipynb`](02_forensic_analysis_walkthrough.ipynb): Jupyter Notebook phân tích thống kê mô tả và so sánh chuẩn ngành ICB.
- [`REPORT_STAGE_2_FORENSIC_METRICS.md`](REPORT_STAGE_2_FORENSIC_METRICS.md): Báo cáo kiểm chứng toán học & thống kê phân phối 15 chỉ số.
