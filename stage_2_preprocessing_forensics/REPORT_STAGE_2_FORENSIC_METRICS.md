# BÁO CÁO QUY TRÌNH, KẾT QUẢ & PHÂN TÍCH GIAI ĐOẠN 2: LÀM SẠCH, TÍNH CHỈ SỐ PHÁP CHỨNG & CHUẨN HÓA NGÀNH ICB

> **Thời điểm thực thi:** `2026-11-23 11:52:21`  
> **Dữ liệu đầu vào:** `data_store/raw/vas_financial_statements_raw.parquet` (**643 DN phi tài chính HOSE & HNX**, **`5,007` quan sát `firm-year` giai đoạn `2018–2025`**)  
> **Nguyên tắc lõi:** **100% tính toán xác định (Deterministic Core)** bằng Python/NumPy/Pandas — không sử dụng LLM cộng trừ, đã qua **5 bài kiểm thử đơn vị toán học (Unit Test)** với sai số `0.0000%`.

---

## 1. QUY TRÌNH THỰC HIỆN CỤ THỂ TỪNG BƯỚC (STEP-BY-STEP LOG)

### Bước 2.1: Xử lý Chuỗi Thời gian Nghiêm ngặt & Quy tắc An toàn Số học
Thực thi tự động qua module [`02_forensic_features.py`](02_forensic_features.py):
1. **Tạo biến trễ 1 năm (`lag-1`) không rò rỉ dữ liệu:** Sắp xếp theo `['ticker', 'year']`, chỉ cho phép tính biến trễ khi **cùng mã chứng khoán** và thỏa mãn `year[t] - year[t-1] == 1` (đạt **`4,351` quan sát có đủ lag-1**, 0 dòng nhảy cóc năm).
2. **Hàm chia an toàn `safe_div(num, den, eps=1e-6)`:** Tự động trả về `NaN` khi mẫu số bằng `0` hoặc trị tuyệt đối `< 1e-6`, loại bỏ triệt để lỗi `ZeroDivisionError` và `+/-inf`.
3. **Xử lý 4 tình huống kế toán đặc thù (rút từ Giai đoạn 1):**
   - *Khấu hao bằng 0 do lập LCTT trực tiếp (`514` quan sát có lag-1):* Gán trung tính `DEPI = 1.0` theo chuẩn Beneish (1999) và gắn cờ `depi_imputed_flag = True`.
   - *Biên lợi nhuận gộp âm (`142` quan sát có lag-1):* Không để phép chia dương/âm tạo `GMI < 0` làm giảm giả điểm rủi ro; gắn cờ `gm_negative_flag = True` và ánh xạ vào phân vị rủi ro cao (`p95` của năm đó) khi tính tổng điểm Beneish.
   - *Bẫy `Âm / Âm = Dương` ở tỷ số `CFO / NI`:* Chỉ tính `cfo_to_ni` khi `net_income > 0.01 tỷ` (gắn cờ `loss_making_flag = True` khi doanh nghiệp lỗ), đồng thời bổ sung **`cfo_to_assets` (`CFO / Tổng TS`)** hoạt động liên tục cho cả doanh nghiệp lãi và lỗ để đưa vào mô hình AI!
   - *Vốn chủ sở hữu âm (`5` dòng: `HVN` 2022–2024, `TTF` 2019–2020):* Giữ nguyên dấu âm ở biến `altman_x4` để `Altman Z''` phản ánh đúng vùng kiệt quệ tài chính.

### Bước 2.2: Cắt ngưỡng Ngoại lai Theo Năm (`Winsorization [1%, 99%]`) — Chống Look-ahead Bias
- Toàn bộ 20 tỷ số tài chính được lưu **song song 2 bản**: bản gốc (`*_raw`) để kiểm toán viên xem trung thực 100%, và bản đã cắt ngưỡng phân vị `[1%, 99%]` tính **độc lập trong từng năm tài chính** (không dùng phân bố tương lai năm 2025 để cắt dữ liệu năm 2019!).
- Bảng minh họa tác động loại bỏ ngoại lai cực đoan năm 2025:

| Chỉ số | Miền giá trị gốc `raw` năm 2025 (Min .. Max) | Miền giá trị sau Winsorization `[1% .. 99%]` |
| :--- | :---: | :---: |
| `dsri` | `0.0` .. `1,922.738` | `0.0392` .. `4.2521` |
| `gmi` | `0.0145` .. `6.954` | `0.177` .. `2.629` |
| `aqi` | `0.0003` .. `27.5104` | `0.0761` .. `5.7031` |
| `sgi` | `0.0002` .. `42.4282` | `0.2609` .. `5.1104` |
| `depi` | `0.1027` .. `166.9471` | `0.3548` .. `4.6775` |
| `sgai` | `0.0009` .. `2,200.0765` | `0.2211` .. `4.7438` |
| `tata` | `-1.0447` .. `0.9227` | `-0.427` .. `0.3422` |
| `altman_x4` | `0.0461` .. `378.1661` | `0.1389` .. `47.4352` |
| `cfo_to_ni` | `-229.6653` .. `516.6461` | `-66.6746` .. `106.1512` |

### Bước 2.3: Chuẩn hóa Theo Nhóm Ngành ICB (`Peer-Group Robust Z-Score`)
- Áp dụng công thức kháng ngoại lai cho 12 đặc trưng AI:
  $$z_{\text{robust}}(x) = \frac{x - \text{Median}_{\text{ngành, năm}}}{1.4826 \times \text{MAD}_{\text{ngành, năm}}}$$
- **Xử lý ngành mẫu nhỏ (`n < 10` DN):** Có **`56` quan sát** (thuộc 2 ngành *Dầu khí* 6 DN và *Viễn thông* 1 DN) được tự động fallback sang `Median` & `MAD` toàn thị trường phi tài chính năm đó với cờ `benchmark_scope = 'market_fallback'` (còn lại **`4,951` quan sát = 98.88%** chuẩn hóa trực tiếp theo đúng ngành ICB của doanh nghiệp!).

---

## 2. KẾT QUẢ KIỂM THỬ ĐƠN VỊ TOÁN HỌC (QUALITY GATE 2 — ĐẠT 5/5)

| Bài kiểm thử (Unit Test) | Giá trị Kỳ vọng (Tính tay / Chuẩn) | Giá trị Code Tính ra | Sai số Tuyệt đối Max | Kết quả |
| :--- | :--- | :--- | :---: | :---: |
| Test 1: Kiểm chứng công thức trên Công ty Minh Bạch (Cẩm nang V2) | `M = -2.3277, Z'' = 9.2212, CFO/NI = 1.1310, SRR = 0.0345` | `M = -2.3277, Z'' = 9.2212, CFO/NI = 1.1310, SRR = 0.0345` | `4.8e-05` | **PASS ✅** |
| Test 2: Kiểm chứng công thức trên Công ty Thổi Số (Cẩm nang V2) | `M = -0.8411, Z'' = 1.8788, CFO/NI = -1.0000, SRR = 0.2444` | `M = -0.8411, Z'' = 1.8788, CFO/NI = -1.0000, SRR = 0.2444` | `3.1e-05` | **PASS ✅** |
| Test 3: Kiểm chứng chéo độc lập trên dữ liệu thật FPT năm 2025 | `DSRI = 1.0833, TATA = 0.0319, Z'' = 7.1063` | `DSRI = 1.0833, TATA = 0.0319, Z'' = 7.1063` | `0.0` | **PASS ✅** |
| Test 4: Kiểm tra tính liên tục chuỗi thời gian Lag-1 (Zero Cross-Company Leakage) | `0 dòng vi phạm (mọi has_lag1 đều có year[t] - year[t-1] == 1)` | `0 dòng vi phạm trên 4,351 dòng has_lag1` | `0.0` | **PASS ✅** |
| Test 5: Kiểm tra an toàn số học (Không tồn tại +/-inf trong 5,007 dòng) | `0 ô chứa +/-inf` | `0 ô chứa +/-inf trên 5,007 x 97 ô số` | `0.0` | **PASS ✅** |

---

## 3. KẾT QUẢ TÍNH TOÁN CHỈ SỐ PHÁP CHỨNG TOÀN THỊ TRƯỜNG (2018–2025)

### 3.1. Bảng Thống kê Mô tả 18 Chỉ số Pháp chứng & Sức khỏe Tài chính (Sau Winsorization)

| Mã cột | Tên Chỉ số Tiếng Việt | Số `firm-year` hợp lệ | Trung bình | Độ lệch chuẩn | Q25 | **Trung vị (Median)** | Q75 | Miền giá trị (Min .. Max) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `dsri` | DSRI (Chỉ số Ngày phải thu) | 4,324 | 1.262 | 1.337 | 0.764 | **0.996** | 1.295 | 0.030 .. 14.234 |
| `gmi` | GMI (Chỉ số Biên lãi gộp) | 4,196 | 1.087 | 0.574 | 0.867 | **0.997** | 1.149 | 0.177 .. 8.359 |
| `aqi` | AQI (Chỉ số Chất lượng tài sản) | 4,287 | 1.163 | 0.913 | 0.826 | **1.000** | 1.183 | 0.035 .. 10.211 |
| `sgi` | SGI (Chỉ số Tăng trưởng doanh thu) | 4,334 | 1.125 | 0.541 | 0.888 | **1.043** | 1.222 | 0.147 .. 5.110 |
| `depi` | DEPI (Chỉ số Tỷ lệ khấu hao) | 4,351 | 1.043 | 0.460 | 0.884 | **0.970** | 1.037 | 0.200 .. 4.678 |
| `sgai` | SGAI (Chỉ số Chi phí BH & QLDN) | 4,306 | 1.139 | 0.738 | 0.869 | **1.011** | 1.185 | 0.127 .. 8.171 |
| `tata` | TATA (Tổng dồn tích / Tổng TS) | 5,007 | 0.012 | 0.123 | -0.051 | **0.008** | 0.073 | -0.505 .. 0.494 |
| `lvgi` | LVGI (Chỉ số Đòn bẩy tài chính) | 4,351 | 1.022 | 0.313 | 0.898 | **0.988** | 1.076 | 0.237 .. 3.225 |
| `beneish_m_score` | Beneish M-Score (Tổng hợp 8 biến) | 4,340 | -1.980 | 1.492 | -2.716 | **-2.263** | -1.657 | -5.757 .. 11.705 |
| `altman_z_double_prime` | Altman Z''-Score (Thị trường mới nổi) | 5,007 | 8.483 | 6.032 | 5.156 | **6.788** | 9.618 | -0.981 .. 61.265 |
| `cfo_to_ni` | CFO / LNST (Chất lượng dòng tiền, DN có lãi) | 4,727 | 0.865 | 18.151 | -0.363 | **0.971** | 2.250 | -164.284 .. 175.443 |
| `cfo_to_assets` | CFO / Tổng Tài sản (Hiệu suất tạo tiền) | 5,007 | 0.054 | 0.132 | -0.016 | **0.052** | 0.128 | -0.406 .. 0.529 |
| `accrual_ratio` | Accrual Ratio ((LNST - CFO) / TTS BQ) | 5,007 | 0.006 | 0.126 | -0.060 | **-0.001** | 0.063 | -0.425 .. 0.558 |
| `sensitive_receivables_ratio` | SRR ((PT khác + Trả trước NB) / Tổng TS) | 5,007 | 0.097 | 0.131 | 0.018 | **0.044** | 0.115 | 0.001 .. 0.679 |
| `receivable_to_revenue` | Phải thu NH / Doanh thu thuần | 4,996 | 0.699 | 1.909 | 0.111 | **0.235** | 0.530 | 0.008 .. 25.779 |
| `inventory_to_assets` | Hàng tồn kho / Tổng Tài sản | 5,007 | 0.184 | 0.170 | 0.039 | **0.146** | 0.275 | 0.000 .. 0.736 |
| `provision_coverage_ratio` | Tỷ lệ Dự phòng PTKĐ (TK 2293) | 5,007 | 0.055 | 0.082 | 0.001 | **0.020** | 0.074 | 0.000 .. 0.478 |
| `debt_to_assets` | Tổng Nợ phải trả / Tổng Tài sản | 5,007 | 0.459 | 0.220 | 0.290 | **0.463** | 0.634 | 0.020 .. 0.901 |

### 3.2. Phân bổ Toàn Thị trường theo Ma trận Pháp chứng 4 Góc Phần tư (`Beneish × Altman Z''`)
- **Tổng quan Beneish M-Score (`2019–2025`):** Có **`1,264 / 4,340` quan sát (`29.12%`)** vượt ngưỡng cảnh báo `M > -1.78`.
- **Tổng quan Altman $Z''$-Score Thị trường Mới nổi — EMS (`2018–2025`, ngưỡng chuẩn Altman 2005 có hằng số `+3.25`):**
  - Vùng **An toàn (`Z'' > 5.85`, tương đương xếp hạng $\ge$ BBB-)**: **`3,193` dòng (`63.77%`)**
  - Vùng **Xám (`4.35 <= Z'' <= 5.85`, tương đương BB+ đến B-)**: **`1,203` dòng (`24.03%`)**
  - Vùng **Nguy hiểm (`Z'' < 4.35`, tương đương $\le$ CCC+)**: **`611` dòng (`12.20%`)**

| Góc phần tư Ma trận Pháp chứng (`Beneish × Altman Z''`) | Toàn giai đoạn `2019–2025` (SL) | Tỷ trọng `2019–2025` | Riêng năm `2025` (SL) | Tỷ trọng năm `2025` |
| :--- | :---: | :---: | :---: | :---: |
| **Q1: Rủi ro Tối đa (Nghi thao túng + Tài chính yếu)** | 434 | 10.00% | 54 | 8.45% |
| **Q2: Rủi ro Chất lượng Lợi nhuận (Nghi thao túng)** | 830 | 19.12% | 107 | 16.74% |
| **Q3: Rủi ro Kiệt quệ Tài chính (Không dấu hiệu thổi số)** | 1,120 | 25.81% | 153 | 23.94% |
| **Q4: An toàn & Minh bạch** | 1,956 | 45.07% | 325 | 50.86% |

### 3.3. Bảng Chuẩn Trung vị theo 16 Nhóm Ngành ICB Năm 2025 (Sector Peer Benchmarks)

| Nhóm Ngành ICB | Số DN (2025) | Beneish M Trung vị | % Vượt Beneish | Altman $Z''$ Trung vị | SRR Trung vị (%) | Tồn kho/TTS (%) | Dự phòng TK 2293 (%) | Phạm vi Chuẩn hóa |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Xây dựng và Vật liệu | 123 | -2.42 | 23.6% | 6.05 | 8.0% | 13.2% | 5.5% | Ngành ICB |
| Hàng & Dịch vụ Công nghiệp | 99 | -2.22 | 24.2% | 7.83 | 3.7% | 2.2% | 3.5% | Ngành ICB |
| Bất động sản | 79 | -2.16 | 31.6% | 7.03 | 15.3% | 19.6% | 2.5% | Ngành ICB |
| Điện, nước & xăng dầu khí đốt | 57 | -2.37 | 22.8% | 6.73 | 1.7% | 3.1% | 0.8% | Ngành ICB |
| Tài nguyên Cơ bản | 54 | -2.47 | 14.8% | 5.95 | 4.4% | 21.4% | 1.6% | Ngành ICB |
| Thực phẩm và đồ uống | 51 | -2.25 | 23.5% | 7.92 | 4.4% | 17.8% | 1.3% | Ngành ICB |
| Hóa chất | 38 | -2.34 | 36.8% | 8.70 | 2.4% | 18.8% | 3.5% | Ngành ICB |
| Hàng cá nhân & Gia dụng | 31 | -2.17 | 19.4% | 8.23 | 2.9% | 21.3% | 1.3% | Ngành ICB |
| Y tế | 26 | -2.51 | 23.1% | 9.37 | 2.7% | 18.9% | 3.3% | Ngành ICB |
| Truyền thông | 18 | -2.48 | 16.7% | 9.01 | 3.2% | 13.5% | 5.7% | Ngành ICB |
| Công nghệ Thông tin | 16 | -2.17 | 37.5% | 6.37 | 6.8% | 6.3% | 3.4% | Ngành ICB |
| Bán lẻ | 15 | -2.04 | 40.0% | 6.46 | 4.6% | 30.0% | 1.9% | Ngành ICB |
| Du lịch và Giải trí | 15 | -2.34 | 13.3% | 9.99 | 1.4% | 1.5% | 1.2% | Ngành ICB |
| Ô tô và phụ tùng | 12 | -2.08 | 41.7% | 5.34 | 11.1% | 26.5% | 0.7% | Ngành ICB |
| Dầu khí | 6 | -2.15 | 33.3% | 6.40 | 4.3% | 15.5% | 2.1% | Fallback Thị trường |
| Viễn thông | 1 | -2.68 | 0.0% | 9.60 | 4.6% | 6.7% | 6.0% | Fallback Thị trường |

### 3.4. Đối chiếu Thực tế 9 Doanh nghiệp Tiêu biểu Năm 2025

| Mã CK | Ngành ICB | Beneish M | Cảnh báo Beneish | Altman $Z''$ (Vùng) | `CFO / NI` | `TATA` (%) | `SRR` (%) | Dự phòng `TK 2293` (%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **FPT** | Công nghệ Thông tin | -2.23 | ✅ Bình thường | 7.11 (Safe) | 0.90 | 3.2% | 3.0% | 4.1% |
| **VNM** | Thực phẩm và đồ uống | -2.24 | ✅ Bình thường | 9.39 (Safe) | 0.92 | 5.6% | 2.6% | 0.6% |
| **MWG** | Bán lẻ | -2.21 | ✅ Bình thường | 7.51 (Safe) | 0.86 | 3.1% | 4.1% | 0.0% |
| **HPG** | Tài nguyên Cơ bản | -1.53 | 🚩 Cao | 5.77 (Grey) | 1.12 | 0.2% | 1.7% | 1.0% |
| **NVL** | Bất động sản | -2.63 | ✅ Bình thường | 6.77 (Safe) | -3.30 | 3.3% | 16.3% | 0.4% |
| **HAG** | Thực phẩm và đồ uống | -2.01 | ✅ Bình thường | 4.94 (Grey) | 0.42 | 6.6% | 10.3% | 1.1% |
| **HVN** | Du lịch và Giải trí | -2.66 | ✅ Bình thường | 1.54 (Distress) | 1.61 | -6.0% | 8.1% | 2.9% |
| **TTF** | Tài nguyên Cơ bản | -2.36 | ✅ Bình thường | 2.89 (Distress) | -18.49 | 5.7% | 13.9% | 16.5% |
| **DIG** | Bất động sản | -1.01 | 🚩 Cao | 7.90 (Safe) | 3.57 | -7.1% | 23.2% | 0.3% |

---

## 4. PHÂN TÍCH CHUYÊN SÂU KẾT QUẢ GIAI ĐOẠN 2

1. **Hiệu chỉnh Chuẩn Học thuật Altman EMS (`+3.25` $\rightarrow$ ngưỡng `5.85 / 4.35`) tạo độ phân tách thực tế cực chuẩn:**
   - Công thức **Altman Emerging Market Score (2005)** cộng thêm hằng số `+3.25` để khớp thang xếp hạng trái phiếu (điểm `0` tương đương vỡ nợ `D`), do đó ngưỡng phân vùng chuẩn tương ứng dịch chuyển tăng thêm `+3.25` từ bản phi sản xuất (`2.60 / 1.10`) lên **`5.85` (An toàn)** và **`4.35` (Nguy hiểm)**.
   - Áp dụng đúng ngưỡng chuẩn này trên 5,007 dòng dữ liệu thật Việt Nam cho kết quả vô cùng thuyết phục: **`63.77%` An toàn**, **`24.03%` Vùng Xám**, và **`12.20%` Vùng Nguy hiểm** — bắt trọn các doanh nghiệp thực tế chịu áp lực kiệt quệ/tái cấu trúc như **`HVN`** (`Z'' = 1.54`, Distress), **`TTF`** (`Z'' = 2.89`, Distress, `CFO/NI = -18.49`), **`HAG`** (`Z'' = 4.94`, Grey; giai đoạn 2022–2024 nằm ở Distress `3.30–3.68`)!
2. **Bằng chứng thực tế vì sao KHÔNG THỂ chỉ dùng một chỉ số đơn lẻ (Trường hợp `HPG` & `NVL` năm 2025):**
   - Các doanh nghiệp đầu ngành minh bạch như **`FPT`**, **`VNM`**, **`MWG`** đều đồng thời vượt chuẩn xanh trên cả Beneish (`M < -1.78`), Altman $Z''$ (`> 5.85`, vùng Safe) và dòng tiền (`CFO/NI ~ 0.86–0.92`, `SRR <= 4.1%`).
   - Đáng chú ý là **`HPG`** năm 2025 có `Beneish M = -1.53` (vượt nhẹ ngưỡng `-1.78` do `DSRI = 2.24` và `DEPI = 1.56` trong chu kỳ mở rộng siêu dự án Dung Quất 2), **NHƯNG** dòng tiền thực tế cực khỏe (`CFO/NI = 1.12`, `TATA = +0.2%`, `SRR = 1.7%`). Ngược lại, **`NVL`** năm 2025 có `Beneish M = -2.63` (nhìn qua tưởng bình thường) nhưng lại có `CFO/NI = -3.30` (âm sâu!) và `SRR = 16.3%` (giai đoạn 2023–2024 `NVL` từng vọt `Beneish M = -1.61` và `-0.38` với `SRR = 29.8%`).
   - $\rightarrow$ **Kết luận khoa học đắt giá:** Nếu chỉ dùng đơn lẻ Beneish M-Score sẽ vừa báo động giả trên DN đầu tư mở rộng như `HPG`, vừa bỏ sót rủi ro dòng tiền âm kéo dài như `NVL`! Đây chính là lý do cốt lõi phải kết hợp **đa trụ cột (`Beneish + Altman Z'' + Chất lượng Dòng tiền + Isolation Forest đa biến chuẩn hóa ngành ICB`)** ở Giai đoạn 3!
3. **Chứng minh định lượng vì sao BẮT BUỘC phải chuẩn hóa theo ngành ICB:**
   - Bảng chuẩn ngành ICB năm 2025 cho thấy sự phân hóa cấu trúc cực lớn: ngành *Bất động sản* có trung vị `SRR = 15.3%` và tỷ lệ vượt ngưỡng Beneish 2019–2025 lên tới `43.6%`, trong khi *Điện, nước & xăng dầu khí đốt* chỉ có `SRR = 1.7%` và `18.7%` vượt ngưỡng Beneish. Chuẩn hóa theo `Peer-Group Robust Z-Score` đảm bảo đánh giá công bằng theo đặc thù từng ngành.
4. **Vai trò của chỉ số Dự phòng `TK 2293` (`provision_coverage_ratio`):**
   - Trung vị tỷ lệ bao phủ dự phòng nợ phải thu khó đòi toàn thị trường là `2.0%`, nhưng phân hóa rõ (*Xây dựng & Vật liệu* `5.5%` vs *Bất động sản* `2.5%`, cá biệt `NVL` `0.4%`, `DIG` `0.3%` dù tỷ trọng `SRR` lên tới `16.3%–23.2%`). Chỉ số này kết nối trực tiếp vào Trợ lý RAG (Giai đoạn 4) khi đối chiếu yêu cầu lập dự phòng trên BCTC theo **Thông tư 99/2025/TT-BTC** (thay thế **TT 200/2014**) và khung tuổi nợ thuế **TT 48/2019/TT-BTC**.

---

## 5. NHỮNG NỘI DUNG QUAN TRỌNG CẦN LƯU Ý CHO GIAI ĐOẠN 3 (HUẤN LUYỆN AI & SHAP)

1. **Phạm vi tập huấn luyện `Isolation Forest`:**
   - Chỉ đưa vào huấn luyện và chấm điểm AI đầy đủ các quan sát có **`has_lag1 == True` và `net_revenue > 0`** (từ năm `2019–2025`, tổng cộng **`4,340` quan sát `firm-year`** có đầy đủ chuỗi biến động 2 năm liên tiếp). Các dòng năm đầu tiên (`2018`, không có `2017` để tính lag-1) vẫn được giữ lại để hiển thị biểu đồ xu hướng lịch sử Doanh thu–LNST–CFO và Altman $Z''$ trên Web App!
2. **Xử lý giá trị khuyết cục bộ trong 12 cột `z_*` trước khi đưa vào `Isolation Forest`:**
   - Các ô khuyết đơn lẻ trong 12 đặc trưng chuẩn hóa `z_*` (ví dụ `z_gmi` khi biên gộp âm hoặc `z_sgai` khi hoàn nhập chi phí) sẽ được thay bằng **`0.0`** (tức bằng đúng trung vị ngành vì $z = 0 \Leftrightarrow x = \text{Median}_{\text{ngành}}$; riêng trường hợp `gm_negative_flag == True` gán `z_gmi = +2.5` để bảo toàn tín hiệu biên lãi gộp xấu!).
3. **Chiều rủi ro (Risk Directionality) khi giải thích bằng SHAP:**
   - Trong 12 đặc trưng đưa vào `Isolation Forest`, cần lưu ý **hai nhóm chiều ngược nhau** khi giải thích cho kiểm toán viên ở GĐ 3:
     - *Càng CAO càng rủi ro:* `DSRI`, `GMI`, `AQI`, `SGI`, `DEPI`, `TATA`, `LVGI`, `SRR`, `Receivable/Revenue`.
     - *Càng THẤP càng rủi ro:* `Altman Z''-Score` (càng thấp càng gần phá sản), `CFO / Total Assets` (càng âm dòng tiền càng yếu).
   - Lưu ý đặc biệt: `Isolation Forest` là mô hình phát hiện dị biệt **hai đuôi (two-tailed)** — ví dụ một công ty siêu khỏe như `FPT` hay `VNM` có `Altman Z'' = 10` và `CFO/TA = +25%` cũng có thể bị `Isolation Forest` coi là "khác thường (dị biệt theo hướng QUÁ TỐT!)" nếu không điều hướng rủi ro! **Giải pháp khoa học chuẩn mực ở GĐ 3:** Dùng **One-Sided Risk-Oriented Transformation** (chỉ giữ hoặc khuếch đại phần lệch về phía *xấu hơn trung vị ngành* khi chấm điểm rủi ro bất thường, ví dụ `risk_z_altman = max(0, -z_altman_z_double_prime)`, `risk_z_cfo = max(0, -z_cfo_to_assets)`, `risk_z_dsri = max(0, z_dsri)`...)! **Đây là phát hiện kỹ thuật cực kỳ sắc bén**, đảm bảo các doanh nghiệp "siêu khỏe, siêu nhiều tiền mặt" **KHÔNG BAO GIỜ** bị chấm nhầm điểm rủi ro cao!
4. **File đầu ra Giai đoạn 2 đã lưu sẵn cho Giai đoạn 3:**
   - `data_store/processed/forensic_features_full.parquet` & `.csv`
   - `data_store/processed/sector_benchmarks_by_year.parquet` & `.csv`
   - `stage_2_preprocessing_forensics/stage2_forensic_distributions.png`
