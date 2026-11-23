# BÁO CÁO QUY TRÌNH, KẾT QUẢ & PHÂN TÍCH GIAI ĐOẠN 1: THU THẬP VÀ KIỂM ĐỊNH DỮ LIỆU NGUỒN

> **Thời điểm thực thi:** `2026-11-23 09:52:34`  
> **Nguồn dữ liệu thực tế:** `Vietcap IQ Insight API (https://iq.vietcap.com.vn/)` (100% dữ liệu BCTC kiểm toán/công bố công khai của doanh nghiệp niêm yết Việt Nam, **không có dữ liệu giả lập**)  
> **Đơn vị tiền tệ chuẩn hóa:** `Tỷ VNĐ (Billion VND)`  
> **Chuẩn mực kế toán:** Chuỗi dữ liệu lịch sử `2018–2025` lập theo **Thông tư 200/2014/TT-BTC**, đã chuẩn hóa theo cấu trúc mã số cố định liên thông trực tiếp với **Thông tư 99/2025/TT-BTC** (có hiệu lực từ `01/01/2026`, đổi tên *Bảng CĐKT* thành *Báo cáo Tình hình Tài chính — B01-DN*).

---

## 1. QUY TRÌNH THỰC HIỆN CỤ THỂ TỪNG BƯỚC (STEP-BY-STEP LOG)

### Bước 1.1: Thiết lập Môi trường Độc lập trên Ổ D & Khảo sát Nguồn Dữ liệu Thực tế
- Khởi tạo môi trường ảo Python độc lập tại `d:\SEHackathon\.venv` (đảm bảo toàn bộ gói cài đặt và bộ đệm lưu trong `d:\SEHackathon`, không ghi dữ liệu dự án ra ổ C).
- **Phát hiện thực nghiệm quan trọng khi kiểm thử nguồn API:**
  - Thư viện `vnstock 6.0.1` từ năm 2026 đã chuyển route `fundamental.equity.balance_sheet` sang nguồn trả phí/yêu cầu khóa riêng (`FHSC_API_KEY`).
  - Nhóm đã kiểm định trực tiếp các nguồn công khai chuẩn hóa tại Việt Nam và lựa chọn **Vietcap IQ Insight API** (`https://iq.vietcap.com.vn/api/iq-insight-service/v1/`) — nguồn dữ liệu nghiên cứu tài chính chính thống cung cấp đầy đủ **3 bảng BCTC chuẩn VAS (`BALANCE_SHEET`, `INCOME_STATEMENT`, `CASH_FLOW`)** giai đoạn **2018–2025** kèm **Danh mục phân loại ngành ICB cấp 2** cho toàn bộ doanh nghiệp niêm yết.

### Bước 1.2: Phễu Lọc Phạm vi Nghiên cứu Khoa học (Sample Selection Funnel)
Quy trình lọc mẫu được thực hiện tự động, minh bạch qua script [`01_data_acquisition.py`](01_data_acquisition.py):

| Bước lọc | Quy tắc lọc khoa học | Số lượng doanh nghiệp | Tỷ trọng / Ghi chú |
| :--- | :--- | :---: | :--- |
| **1. Toàn thị trường Việt Nam** | Tải danh mục đầy đủ từ Vietcap IQ Screener (`HSX`, `HNX`, `UPCoM`) | **1,519** | Lưu tại `data_store/raw/universe_catalog_all.csv` |
| **2. Lọc sàn niêm yết chính thức** | Chỉ giữ **HOSE** và **HNX** (loại bỏ `808` mã UPCoM do chuẩn công bố thông tin không đồng đều) | **711** | Tập doanh nghiệp niêm yết chuẩn mực |
| **3. Loại bỏ Định chế Tài chính** | Loại trừ 3 ngành ICB đặc thù: *Ngân hàng*, *Dịch vụ tài chính (Chứng khoán)*, *Bảo hiểm* (`-67` mã) | **644** | Do cấu trúc BCTC theo TT 49/NHNN & TT 210/TT-BTC không tương thích công thức Beneish & Altman $Z''$ |
| **4. Thu thập thành công đủ 3 bảng BCTC (2018–2025)** | Tải đồng bộ `B01-DN`, `B02-DN`, `B03-DN` và giao chung tập năm có đủ cả 3 bảng | **643** | Tỷ lệ thu thập thành công: **99.84%** (`1` mã không có/thiếu BCTC) |

### Bước 1.3: Chuẩn hóa Dấu Kế toán (Sign Normalization) — Điểm Kỹ thuật Sống còn
Khi kiểm tra trực tiếp dữ liệu gốc từ API trên 6 mã thực tế (`FPT`, `VNM`, `HPG`, `NVL`, `HBC`, `HAG`), phát hiện quy ước dấu gốc của Vietcap IQ như sau:
- Các khoản chi phí trên `B02-DN` (`isa4`: Giá vốn, `isa8`: Chi phí lãi vay, `isa9`: Chi phí bán hàng, `isa10`: Chi phí QLDN) và `bsa14` (Dự phòng nợ phải thu khó đòi — `TK 2293`) được lưu dưới **dạng số âm**.
- Script đã **chuẩn hóa dấu nhất quán về quy ước toán học của Beneish & Altman**:
  - `cogs = -isa4`; `selling_expenses = -isa9`; `admin_expenses = -isa10`; `sga_expenses = -(isa9 + isa10)` *(bảo toàn cả trường hợp hoàn nhập chi phí làm giảm chi phí ròng)*.
  - `interest_expense = -isa8`; `ebit = isa16 - isa8` (tức $\text{LN trước thuế} + \text{Chi phí lãi vay}$).
  - `provision_doubtful_debts = |bsa14|`.
- Toàn bộ đơn vị tiền tệ gốc (VNĐ) được quy đổi về **Tỷ VNĐ** (`chia 1e9`) để tối ưu tính dễ đọc, tránh tràn số dấu phẩy động và giữ nguyên chính xác mọi tỷ số tài chính.

---

## 2. KẾT QUẢ THU THẬP ĐƯỢC (CON SỐ THỰC TẾ 100%)

### 2.1. Tổng quan Quy mô Tập Dữ liệu
- **Tổng thời gian thu thập toàn bộ thị trường phi tài chính HOSE/HNX:** `636.75 giây` (trên kết nối đa luồng `6 workers`, chạy mượt với bộ nhớ RAM tiêu thụ < 250MB).
- **Tổng số doanh nghiệp thu thập thành công:** **`643` doanh nghiệp phi tài chính** (HOSE & HNX).
- **Tổng số quan sát năm-doanh nghiệp (`firm-year`):** **`5,007` dòng** (giai đoạn `2018 – 2025`).
- **Số quan sát có đủ dữ liệu 2 năm liên tiếp ($t$ và $t-1$) để tính Beneish M-Score:** **`4,351` dòng** (**86.90%**).
- **File lưu trữ đã tạo:**
  - `data_store/raw/vas_financial_statements_raw.parquet` (siêu gọn cho đọc/ghi tốc độ cao)
  - `data_store/raw/vas_financial_statements_raw.csv` (mở trực tiếp bằng Excel để kiểm tra đối chiếu bằng tay)
  - `data_store/raw/stage1_acquisition_log.json` (nhật ký thu thập chi tiết)

### 2.2. Phân bố Dữ liệu theo Năm Tài chính (`2018 – 2025`)

| Năm | Tổng số DN | Số DN sàn HOSE | Số DN sàn HNX | Tổng Tài sản Trung vị (Tỷ VNĐ) | LNST Trung vị (Tỷ VNĐ) | Dòng tiền CFO Trung vị (Tỷ VNĐ) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 609 | 339 | 270 | 811.9 | 38.8 | 29.1 |
| **2019** | 609 | 340 | 269 | 906.5 | 37.5 | 35.3 |
| **2020** | 615 | 341 | 274 | 949.0 | 33.1 | 42.0 |
| **2021** | 622 | 345 | 277 | 1,122.5 | 42.3 | 19.8 |
| **2022** | 632 | 354 | 278 | 1,232.9 | 37.5 | 21.0 |
| **2023** | 637 | 359 | 278 | 1,279.9 | 31.4 | 33.1 |
| **2024** | 642 | 362 | 280 | 1,304.9 | 40.4 | 39.5 |
| **2025** | 641 | 362 | 279 | 1,417.3 | 48.3 | 36.5 |

### 2.3. Phân bố Dữ liệu theo 16 Nhóm Ngành ICB Phi Tài chính

| Nhóm Ngành ICB (Tiếng Việt / Tiếng Anh) | Số DN | Số `firm-year` | Tổng TS Trung vị (Tỷ) | Doanh thu Trung vị (Tỷ) | Ghi chú Chuyên môn |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Xây dựng và Vật liệu (Construction & Materials) | 123 | 955 | 935.0 | 545.4 |
| Hàng & Dịch vụ Công nghiệp (Industrial Goods & Services) | 99 | 776 | 526.6 | 576.6 |
| Bất động sản (Real Estate) | 79 | 619 | 3,713.3 | 621.6 |
| Điện, nước & xăng dầu khí đốt (Utilities) | 57 | 448 | 1,352.3 | 1,085.4 |
| Tài nguyên Cơ bản (Basic Resources) | 54 | 417 | 1,300.3 | 1,981.1 |
| Thực phẩm và đồ uống (Food & Beverage) | 52 | 395 | 1,492.7 | 1,454.6 |
| Hóa chất (Chemicals) | 38 | 293 | 1,090.1 | 1,557.8 |
| Hàng cá nhân & Gia dụng (Personal & Household Goods) | 31 | 246 | 1,012.5 | 942.8 |
| Y tế (Health Care) | 26 | 205 | 1,026.4 | 671.2 |
| Truyền thông (Media) | 19 | 146 | 166.9 | 301.5 |
| Công nghệ Thông tin (Technology) | 16 | 127 | 556.5 | 678.0 |
| Bán lẻ (Retail) | 15 | 115 | 733.4 | 2,899.3 |
| Du lịch và Giải trí (Travel & Leisure) | 15 | 118 | 768.8 | 233.8 |
| Ô tô và phụ tùng (Automobiles & Parts) | 12 | 91 | 2,708.3 | 3,551.1 |
| Dầu khí (Oil & Gas) | 6 | 48 | 24,242.7 | 12,547.7 | ⚠️ *Nhóm mẫu nhỏ (<10 DN), cần gộp/fallback chuẩn thị trường khi tính Robust Z-Score*
| Viễn thông (Telecommunications) | 1 | 8 | 101.6 | 153.3 | ⚠️ *Nhóm mẫu nhỏ (<10 DN), cần gộp/fallback chuẩn thị trường khi tính Robust Z-Score*

### 2.4. Kiểm định Toàn vẹn Kế toán (5 Lớp Đối chứng — Quality Gate 1)

| Chỉ tiêu Kiểm định | Kết quả Thực tế | Tỷ lệ Đạt / Quy mô | Đánh giá |
| :--- | :---: | :---: | :--- |
| **1. Đẳng thức B01-DN** (`Tổng TS = Nợ phải trả + VCSH`, sai số `< 1%`) | `5,006 / 5,007` dòng | **99.98%** *(khớp tuyệt đối `<0.01%`: `5,005` dòng)* | **ĐẠT XUẤT SẮC** |
| **2. Đẳng thức B02-DN** (`LN gộp = DT thuần - Giá vốn`, sai số `< 1%`) | `5,001 / 5,001` dòng | **100.00%** *(khớp tuyệt đối `<0.01%`: `5,001` dòng)* | **ĐẠT XUẤT SẮC** |
| **3. Quan sát có Tổng Tài sản $\le 0$ hoặc trống** | `0` dòng | `0.00%` | Cần loại bỏ khỏi mẫu số ở GĐ 2 |
| **4. Quan sát có Vốn chủ sở hữu Âm (`total_equity < 0`)** | `5` dòng | `0.10%` | **GIỮ NGUYÊN & GẮN CỜ** (tín hiệu kiệt quệ thực tế) |
| **5. Quan sát có Phân kỳ Dòng tiền (`LNST > 0` nhưng `CFO < 0`)** | `1,387` dòng | **27.70%** | Chứng minh tính thực tiễn cực cao của bài toán chất lượng lợi nhuận tại VN! |

### 2.5. Đối chiếu Thực tế 6 Doanh nghiệp Tiêu biểu Năm 2025 (Đơn vị: Tỷ VNĐ)

| Mã CK | Sàn | Ngành ICB | Tổng Tài sản | Doanh thu thuần | LNST (`NI`) | Dòng tiền `CFO` | Dự phòng PTKĐ (`TK 2293`) | Sai số `B01-DN` |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **FPT** | HOSE | Công nghệ Thông tin | 88,142.0 | 70,112.8 | 11,232.3 | 10,136.0 | 586.2 | 0.0000% |
| **VNM** | HOSE | Thực phẩm và đồ uống | 53,312.4 | 63,645.9 | 9,413.6 | 8,668.1 | 33.8 | 0.0000% |
| **HPG** | HOSE | Tài nguyên Cơ bản | 257,899.2 | 156,116.1 | 15,514.9 | 17,365.9 | 132.5 | 0.0000% |
| **NVL** | HOSE | Bất động sản | 249,907.8 | 6,965.7 | 1,861.4 | -6,145.4 | 76.8 | 0.0000% |
| **HAG** | HOSE | Thực phẩm và đồ uống | 26,381.6 | 7,432.3 | 2,240.2 | 940.5 | 43.7 | 0.0000% |

### 2.6. Bảng Kiểm định Độ Đầy đủ (Completeness Audit) của Toàn bộ 35 Chỉ tiêu Kế toán

| Tên cột chuẩn hóa | Mã Vietcap IQ | Mã số VAS | Tên khoản mục tiếng Việt | Tỷ lệ có dữ liệu (`Non-Null`) | Tỷ lệ khác 0 (`Non-Zero`) | Trung vị (Tỷ VNĐ) |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| `total_assets` | `bsa53` | B01-DN (270) | Tổng cộng tài sản | 100.00% | 100.00% | 1,122.10 |
| `current_assets` | `bsa1` | B01-DN (100) | Tài sản ngắn hạn | 100.00% | 100.00% | 588.35 |
| `cash_and_equivalents` | `bsa2` | B01-DN (110) | Tiền và các khoản tương đương tiền | 100.00% | 100.00% | 53.85 |
| `short_term_investments` | `bsa5` | B01-DN (120) | Đầu tư tài chính ngắn hạn | 100.00% | 70.00% | 16.47 |
| `short_term_receivables` | `bsa8` | B01-DN (130) | Các khoản phải thu ngắn hạn (tổng) | 100.00% | 100.00% | 211.84 |
| `accounts_receivable` | `bsa9` | B01-DN (131) | Phải thu ngắn hạn của khách hàng | 100.00% | 99.52% | 124.56 |
| `prepayments_to_suppliers` | `bsa10` | B01-DN (132) | Trả trước cho người bán ngắn hạn | 100.00% | 98.62% | 12.21 |
| `other_receivables_st` | `bsa13` | B01-DN (136) | Phải thu ngắn hạn khác | 100.00% | 99.40% | 17.07 |
| `provision_doubtful_debts` | `bsa14` | B01-DN (137) | Dự phòng phải thu ngắn hạn khó đòi (TK 2293) | 100.00% | 77.21% | 3.02 |
| `inventory` | `bsa15` | B01-DN (140) | Hàng tồn kho (ròng) | 100.00% | 97.08% | 114.85 |
| `other_receivables_lt` | `bsa27` | B01-DN (216) | Phải thu dài hạn khác | 100.00% | 68.64% | 0.56 |
| `ppe_net` | `bsa30` | B01-DN (221) | Tài sản cố định hữu hình (giá trị còn lại) | 100.00% | 98.84% | 96.15 |
| `fixed_assets_total` | `bsa29` | B01-DN (220) | Tài sản cố định (tổng) | 100.00% | 99.04% | 126.29 |
| `construction_in_progress` | `bsa188` | B01-DN (242) | Chi phí xây dựng cơ bản dở dang | 100.00% | 73.16% | 4.01 |
| `long_term_investments` | `bsa43` | B01-DN (250) | Đầu tư tài chính dài hạn | 100.00% | 66.15% | 8.60 |
| `total_liabilities` | `bsa54` | B01-DN (300) | Nợ phải trả | 100.00% | 100.00% | 464.39 |
| `current_liabilities` | `bsa55` | B01-DN (310) | Nợ ngắn hạn | 100.00% | 100.00% | 339.26 |
| `short_term_debt` | `bsa56` | B01-DN (320) | Vay và nợ thuê tài chính ngắn hạn | 100.00% | 81.97% | 102.82 |
| `long_term_liabilities` | `bsa67` | B01-DN (330) | Nợ dài hạn | 100.00% | 83.38% | 24.42 |
| `long_term_debt` | `bsa71` | B01-DN (338) | Vay và nợ thuê tài chính dài hạn | 100.00% | 58.96% | 5.00 |
| `total_equity` | `bsa78` | B01-DN (400) | Vốn chủ sở hữu | 100.00% | 100.00% | 493.22 |
| `retained_earnings` | `bsa90` | B01-DN (421) | Lợi nhuận sau thuế chưa phân phối | 100.00% | 100.00% | 65.59 |
| `net_revenue` | `isa3` | B02-DN (10) | Doanh thu thuần về bán hàng & CCDV | 100.00% | 99.88% | 811.62 |
| `cogs` | `isa4` | B02-DN (11) | Giá vốn hàng bán | 100.00% | 99.80% | 623.66 |
| `gross_profit` | `isa5` | B02-DN (20) | Lợi nhuận gộp | 100.00% | 99.86% | 130.94 |
| `selling_expenses` | `isa9` | B02-DN (25) | Chi phí bán hàng | 100.00% | 82.62% | 15.18 |
| `admin_expenses` | `isa10` | B02-DN (26) | Chi phí quản lý doanh nghiệp | 100.00% | 99.84% | 34.56 |
| `sga_expenses` | `-(isa9+isa10)` | B02-DN (25+26) | Tổng chi phí bán hàng & QLDN (SG&A) | 100.00% | 100.00% | 60.04 |
| `interest_expense` | `isa8` | B02-DN (23) | Chi phí lãi vay | 100.00% | 87.98% | 9.91 |
| `operating_income` | `isa11` | B02-DN (30) | Lợi nhuận thuần từ hoạt động kinh doanh | 100.00% | 100.00% | 45.28 |
| `ebt` | `isa16` | B02-DN (50) | Tổng lợi nhuận kế toán trước thuế | 100.00% | 100.00% | 48.77 |
| `ebit` | `isa16 - isa8` | B02-DN (50+23) | Lợi nhuận trước lãi vay và thuế (EBIT) | 100.00% | 100.00% | 69.63 |
| `net_income` | `isa20` | B02-DN (60) | Lợi nhuận sau thuế TNDN | 100.00% | 100.00% | 38.15 |
| `cfo` | `cfa18` | B03-DN (20) | Lưu chuyển tiền thuần từ HĐKD (CFO) | 100.00% | 100.00% | 32.06 |
| `depreciation` | `cfa2` | B03-DN (02) | Khấu hao TSCĐ và BĐS đầu tư (LCTT gián tiếp) | 100.00% | 89.95% | 17.27 |

---

## 3. PHÂN TÍCH CHUYÊN SÂU VỀ KẾT QUẢ THU ĐƯỢC

1. **Độ tin cậy & Tính toàn vẹn số liệu cực kỳ cao:**
   - Tập dữ liệu đạt **643 doanh nghiệp phi tài chính** với **5,007 quan sát `firm-year`** trải dài 8 năm (`2018–2025`), gấp hơn **3 lần** quy mô ước tính ban đầu (~150–200 DN), bao phủ gần như **100% doanh nghiệp phi tài chính niêm yết trên cả hai sàn HOSE và HNX**.
   - Tỷ lệ khớp phương trình kế toán cơ bản (`Tổng Tài sản = Nợ phải trả + Vốn chủ sở hữu`) đạt **99.98%** và đẳng thức lợi nhuận gộp (`LN gộp = DT thuần - Giá vốn`) đạt **100.00%**, khẳng định dữ liệu nguồn cực sạch và quy ước chuẩn hóa dấu chính xác tuyệt đối.
2. **Bằng chứng thực chứng rõ nét về "Bài toán Chất lượng Lợi nhuận" tại Việt Nam:**
   - Ngay từ dữ liệu thô Giai đoạn 1 đã xuất hiện tới **`1,387` quan sát (27.70% toàn bộ thị trường)** rơi vào trạng thái **báo lãi sổ sách dương (`NI > 0`) nhưng dòng tiền hoạt động kinh doanh thực tế âm (`CFO < 0`)**!
   - Ví dụ thực tế ngay trên bảng đối chiếu năm 2025: Các doanh nghiệp đầu ngành minh bạch (`FPT`, `VNM`, `HPG`) đều có dòng tiền `CFO` dương mạnh bám sát lợi nhuận sau thuế (`FPT`: NI 11.232 tỷ vs CFO 10.136 tỷ; `HPG`: NI 15.515 tỷ vs CFO 17.366 tỷ), trong khi doanh nghiệp chịu áp lực thanh khoản/bất động sản như `NVL` báo lãi `+1.861 tỷ` nhưng dòng tiền `CFO` âm tới `-6.145 tỷ`!
3. **Phân hóa rõ rệt cấu trúc tài sản giữa các nhóm ngành ICB:**
   - Quy mô tổng tài sản trung vị giữa các ngành chênh lệch rất lớn (VD: *Dầu khí*, *Bất động sản*, *Tài nguyên cơ bản* có quy mô tài sản cao gấp nhiều lần *Truyền thông* hay *Công nghệ*). Điều này khẳng định thiết kế **Chuẩn hóa theo nhóm ngành ICB (`Peer-Group Robust Z-Score`)** ở Giai đoạn 2 là bắt buộc và hoàn toàn đúng đắn.

---

## 4. NHỮNG NỘI DUNG QUAN TRỌNG CẦN LƯU Ý CHO GIAI ĐOẠN 2

Để Giai đoạn 2 (`stage_2_preprocessing_forensics`) tính toán không bị lỗi số học hay sai lệch mô hình AI, cần ghi nhớ **5 lưu ý kỹ thuật – nghiệp vụ bắt buộc** rút ra trực tiếp từ dữ liệu Giai đoạn 1:

1. **Xử lý biến `depreciation` (`cfa2`) bị thiếu hoặc bằng 0 (`0` dòng thiếu, `503` dòng = 0):**
   - Một số doanh nghiệp lập LCTT theo **phương pháp trực tiếp** (không có dòng khấu hao `cfa2` trên `B03-DN`). Khi tính biến `DEPI` trong Beneish M-Score, tuyệt đối **không điền số `0`** (gây chia 0). Quy tắc chuẩn: nếu `depreciation` trống hoặc `<= 0` ở kỳ $t$ hoặc $t-1$, gán **`DEPI = 1.0`** (trung tính — theo đúng quy ước của Beneish 1999 khi thiếu thông tin khấu hao) và gắn cờ `depi_imputed_flag = True` để minh bạch.
2. **Xử lý các ngành ICB có số lượng doanh nghiệp nhỏ (`< 10` doanh nghiệp):**
   - Trong 16 ngành phi tài chính có một số ngành mẫu nhỏ: **Dầu khí (6 DN), Viễn thông (1 DN)**.
   - Nếu một ngành chỉ có 1 hoặc 6 doanh nghiệp (VD: *Viễn thông* chỉ có 1 công ty trên HOSE/HNX), `MAD` của ngành đó sẽ bằng `0`! **Quy tắc xử lý ở GĐ 2:** Với bất kỳ nhóm `(ngành, năm)` nào có số lượng `< 10` doanh nghiệp (hoặc `MAD < 1e-6`), tự động **gộp/fallback về Median & MAD toàn thị trường phi tài chính năm đó** và ghi rõ cờ `benchmark_scope = 'market_fallback'`.
3. **Xử lý Doanh thu bằng 0 (`11` dòng) & Vốn chủ sở hữu âm (`5` dòng):**
   - Các dòng có `net_revenue <= 0` hoặc `total_assets <= 0` sẽ khiến các tỷ số có mẫu số là Doanh thu (`DSRI`, `GMI`, `SGAI`) hoặc Tổng tài sản không xác định $\rightarrow$ Dùng `safe_divide` trả về `NaN`, chỉ đưa vào chấm điểm đầy đủ các quan sát có `total_assets > 0` và `net_revenue > 0`.
   - Các dòng có **Vốn chủ sở hữu âm (`total_equity < 0`)** (như doanh nghiệp lỗ lũy kế vượt vốn góp) **PHẢI GIỮ NGUYÊN** khi tính $X_4 = \text{VCSH}/\text{Tổng Nợ}$ trong Altman $Z''$-Score vì $X_4 < 0$ sẽ kéo $Z''$ xuống vùng Nguy hiểm — phản ánh đúng bản chất kiệt quệ tài chính!
4. **Cắt ngưỡng ngoại lai cực đoan (`Winsorization [1%, 99%]`):**
   - Một số công ty bất động sản/xây dựng có doanh thu tăng đột biến khi bàn giao dự án (`SGI > 20`) hoặc phải thu năm trước gần bằng 0 (`DSRI > 30`). Ở GĐ 2 bắt buộc lưu song song **giá trị gốc (`raw`)** để hiển thị trung thực cho kiểm toán viên và **giá trị đã cắt ngưỡng (`winsorized`)** để tính `Beneish M-Score`, `Robust Z-Score` và huấn luyện `Isolation Forest`.
5. **Chính sách chuyển tiếp Thông tư 200/2014 $\rightarrow$ Thông tư 99/2025:**
   - Toàn bộ dữ liệu lịch sử 2018–2025 được thu thập nhất quán theo mã số chỉ tiêu cố định, sẵn sàng tiếp nhận trực tiếp các file BCTC năm 2026+ lập theo **Thông tư 99/2025/TT-BTC** (`B01-DN: Báo cáo tình hình tài chính`) mà không cần sửa cấu trúc thuật toán.

---

## 5. NHẬT KÝ XỬ LÝ NGOẠI LỆ & ĐỐI CHỨNG TRƯỜNG HỢP ĐẶC BIỆT (DATA PROVENANCE)

1. **Vòng Thu hồi Bổ sung (Recovery Pass):** Sau lượt tải đa luồng lần 1 (`634/644` mã), hệ thống đã chạy vòng thu hồi tuần tự cho `10` mã bị nghẽn kết nối tạm thời và thu hồi thành công thêm **`9` mã**, nâng độ phủ cuối cùng lên **`643/644` doanh nghiệp (99.84%)** toàn thị trường phi tài chính HOSE & HNX với **`5,007` quan sát `firm-year`**! (`1` mã chưa có đủ 3 bảng chung năm trên nguồn: `['AMY']`).
2. **Minh bạch dòng lệch đẳng thức `B01-DN` (`>= 1%`):** Trên toàn bộ `5,007` dòng dữ liệu, chỉ có **`1` dòng duy nhất**: `KSD` năm `2022` (TTS 132.50 tỷ vs Nợ+VCSH 140.19 tỷ) $\rightarrow$ sẽ được gắn cờ `bs_integrity_warning = True` ở Giai đoạn 2 để đảm bảo minh bạch tuyệt đối.
3. **Minh bạch `5` dòng Vốn chủ sở hữu Âm (`total_equity < 0`):** Tập trung tại các doanh nghiệp thực tế có biến cố lỗ lũy kế lớn: `HVN` ([2022, 2023, 2024]), `TTF` ([2019, 2020]). Đây là số liệu lịch sử thực tế 100%, bắt buộc **giữ nguyên** để mô hình Altman $Z''$ và AI nhận diện chính xác rủi ro kiệt quệ tài chính.
4. **Biểu đồ Tổng quan Giai đoạn 1:** Đã xuất tại [`stage1_data_overview.png`](stage1_data_overview.png) (xem quy trình trực quan từng bước tại Notebook [`01_data_acquisition_walkthrough.ipynb`](01_data_acquisition_walkthrough.ipynb)).
