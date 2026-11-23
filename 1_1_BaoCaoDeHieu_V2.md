# CẨM NANG TRI THỨC DỄ HIỂU (PHIÊN BẢN V2 — CHI TIẾT & CÓ VÍ DỤ SỐ THỰC TẾ)
## DỰ ÁN `FinAudit AI — FinForensics`: Giải mã Toàn bộ Thuật ngữ, Ký hiệu, Công thức Kinh tế – Kế toán – Kiểm toán – AI & Web

> **Đối tượng đọc:** Tài liệu này được biên soạn mở rộng từ [`01_Bao_Cao_Kien_Thuc_Tu_Co_Ban_Den_Nang_Cao_FinAudit_AI.md`](01_Bao_Cao_Kien_Thuc_Tu_Co_Ban_Den_Nang_Cao_FinAudit_AI.md) dành riêng cho **người mới bắt đầu**, giải thích từng **thuật ngữ, ký hiệu, công thức** theo cách trực quan nhất, kèm **2 ví dụ doanh nghiệp xuyên suốt được tính tay từng bước chính xác đến 4 chữ số thập phân**, giúp bạn đọc đến đâu hiểu ngay đến đó và tự tin thuyết trình, phản biện tại cuộc thi **SE-Hackathon Challenge 2026 (Trường Kinh tế – ĐH Công nghiệp Hà Nội)**.

---

## MỤC LỤC CHI TIẾT

1. [PHẦN 0: BẢNG TRA CỨU KÝ HIỆU QUY ƯỚC & BỘ SỐ LIỆU MẪU XUYÊN SUỐT](#phần-0-bảng-tra-cứu-ký-hiệu-quy-ước--bộ-số-liệu-mẫu-xuyên-suốt)
2. [PHẦN I: GIẢI MÃ TỪNG KIẾN THỨC KINH TẾ – KẾ TOÁN – KIỂM TOÁN (CÓ TÍNH TAY TỪNG BƯỚC)](#phần-i-giải-mã-từng-kiến-thức-kinh-tế--kế-toán--kiểm-toán-có-tính-tay-từng-bước)
   - [1.1. Ba mảnh ghép Báo cáo Tài chính (Cập nhật Thông tư 99/2025/TT-BTC thay thế TT 200/2014/TT-BTC)](#11-ba-mảnh-ghép-báo-cáo-tài-chính-cập-nhật-thông-tư-992025tt-btc-thay-thế-tt-2002014tt-btc)
   - [1.2. Lý thuyết Kinh tế & Khung ESG-G (Giải thích bằng Ví dụ Đời thường)](#12-lý-thuyết-kinh-tế--khung-esg-g-giải-thích-bằng-ví-dụ-đời-thường)
   - [1.3. Chất lượng Lợi nhuận & Hiện tượng Dồn tích (Sloan, 1996; Dechow et al., 2010)](#13-chất-lượng-lợi-nhuận--hiện-tượng-dồn-tích-sloan-1996-dechow-et-al-2010)
   - [1.4. Giải phẫu Chi tiết 8 Biến của Beneish M-Score (1999) — Tính Tay Từng Biến](#14-giải-phẫu-chi-tiết-8-biến-của-beneish-m-score-1999--tính-tay-từng-biến)
   - [1.5. Giải phẫu Mô hình Altman Z''-Score Thị trường Mới nổi (2005) — Tính Tay Từng Biến](#15-giải-phẫu-mô-hình-altman-z-score-thị-trường-mới-nổi-2005--tính-tay-từng-biến)
   - [1.6. Chỉ số Đặc thù Việt Nam & Phân định Pháp lý (TT 99/2025, TT 200/2014, TT 48/2019, VSA 240)](#16-chỉ-số-đặc-thù-việt-nam--phân-định-pháp-lý-tt-992025-tt-2002014-tt-482019-vsa-240)
   - [1.7. Lọc Ngành ICB & Chuẩn hóa Robust Z-Score (Giải mã Con số 1.4826 & Ví dụ Tính tay)](#17-lọc-ngành-icb--chuẩn-hóa-robust-z-score-giải-mã-con-số-14826--ví-dụ-tính-tay)
3. [PHẦN II: GIẢI MÃ TỪNG KIẾN THỨC CÔNG NGHỆ, DỮ LIỆU, AI & TRIỂN KHAI WEB](#phần-ii-giải-mã-từng-kiến-thức-công-nghệ-dữ-liệu-ai--triển-khai-web)
   - [2.1. Kiến trúc 3 Tầng (Ví dụ "Tổ Kiểm toán 3 Chuyên gia")](#21-kiến-trúc-3-tầng-ví-dụ-tổ-kiểm-toán-3-chuyên-gia)
   - [2.2. Xử lý Dữ liệu Tài chính: 4 Lỗi Chết người & Ví dụ Minh họa](#22-xử-lý-dữ-liệu-tài-chính-4-lỗi-chết-người--ví-dụ-minh-họa)
   - [2.3. Thuật toán Isolation Forest (2008) & Công thức Điểm Rủi ro 0–100](#23-thuật-toán-isolation-forest-2008--công-thức-điểm-rủi-ro-0100)
   - [2.4. AI Có Giải thích — SHAP (2017): Ví dụ "Chia tiền Taxi" & Đọc Biểu đồ Thác nước](#24-ai-có-giải-thích--shap-2017-ví-dụ-chia-tiền-taxi--đọc-biểu-đồ-thác-nước)
   - [2.5. Giải mã 4 Lớp Kiểm chứng Khoa học (Spearman, Jaccard & Backtest)](#25-giải-mã-4-lớp-kiểm-chứng-khoa-học-spearman-jaccard--backtest)
   - [2.6. Giải mã Hybrid RAG: Chunking, BM25, Vector Search, RRF & Đánh giá Hit Rate / MRR](#26-giải-mã-hybrid-rag-chunking-bm25-vector-search-rrf--đánh-giá-hit-rate--mrr)
   - [2.7. Triển khai Web App Streamlit: Offline vs. Online, Cache & Deploy Public](#27-triển-khai-web-app-streamlit-offline-vs-online-cache--deploy-public)
4. [PHẦN III: BỘ CÂU HỎI PHẢN BIỆN KHÓ NHẤT CỦA BAN GIÁM KHẢO KINH TẾ & GỢI Ý TRẢ LỜI](#phần-iii-bộ-câu-hỏi-phản-biện-khó-nhất-của-ban-giám-khảo-kinh-tế--gợi-ý-trả-lời)

---

## PHẦN 0: BẢNG TRA CỨU KÝ HIỆU QUY ƯỚC & BỘ SỐ LIỆU MẪU XUYÊN SUỐT

### 0.1. Bảng Tra cứu Nhanh Các Ký hiệu Thường gặp
Trước khi đi vào công thức, hãy xem bảng quy ước này như "từ điển bỏ túi" — bất cứ khi nào thấy một chữ viết tắt, bạn chỉ cần đối chiếu lại đây:

| Ký hiệu | Tên đầy đủ (Tiếng Anh / Tiếng Việt) | Ý nghĩa dễ hiểu nhất |
| :--- | :--- | :--- |
| **$t$** và **$t-1$** | Kỳ hiện tại và Kỳ trước liền kề | Ví dụ: nếu đang phân tích BCTC năm **2025** thì $t = 2025$ và $t-1 = 2024$. |
| **VAS** | Vietnamese Accounting Standards | Hệ thống Chuẩn mực Kế toán Việt Nam. |
| **VSA** | Vietnamese Standards on Auditing | Hệ thống Chuẩn mực Kiểm toán Việt Nam (VD: VSA 240 về gian lận). |
| **B01-DN** | Báo cáo Tình hình Tài chính *(trước 2026: Bảng Cân đối Kế toán)* | Bảng kê toàn bộ **Tài sản**, **Nợ phải trả** và **Vốn chủ sở hữu** tại ngày cuối kỳ (theo TT 99/2025/TT-BTC). |
| **B02-DN** | Báo cáo Kết quả Hoạt động Kinh doanh (KQKD) | Bảng tính **Doanh thu – Chi phí = Lợi nhuận** trong cả năm. |
| **B03-DN** | Báo cáo Lưu chuyển Tiền tệ (LCTT) | Bảng ghi chép **tiền mặt thực sự vào/ra** doanh nghiệp. |
| **B09-DN** | Bản Thuyết minh Báo cáo Tài chính | Văn bản diễn giải chi tiết các con số trên B01, B02, B03 (thường dài 40–80 trang PDF). |
| **DT / Sales** | Doanh thu thuần (Net Revenue) | Tổng tiền bán hàng sau khi trừ chiết khấu, hàng bán bị trả lại. |
| **COGS** | Cost of Goods Sold (Giá vốn hàng bán) | Chi phí trực tiếp sản xuất hoặc nhập mua hàng hóa đã bán ra. |
| **LNG / GP** | Lợi nhuận gộp (Gross Profit) | $\text{LNG} = \text{Doanh thu thuần} - \text{Giá vốn hàng bán}$. |
| **SG&A** | Selling, General & Administrative Expenses | Tổng **Chi phí bán hàng** + **Chi phí quản lý doanh nghiệp**. |
| **EBIT** | Earnings Before Interest and Taxes | Lợi nhuận trước chi phí lãi vay và thuế thu nhập doanh nghiệp. |
| **NI / LNST** | Net Income (Lợi nhuận sau thuế) | Con số lãi/lỗ cuối cùng trên sổ sách kế toán sau khi đã nộp thuế. |
| **CFO** | Cash Flow from Operating Activities | Lưu chuyển tiền thuần từ hoạt động kinh doanh (**tiền tươi thật thu được từ bán hàng**). |
| **TSNH / CA** | Tài sản ngắn hạn (Current Assets) | Tài sản có thể đổi ra tiền trong vòng $\le 12$ tháng (tiền, phải thu NH, tồn kho...). |
| **TSCĐ / PP&E** | Tài sản cố định hữu hình (Property, Plant & Equipment) | Nhà xưởng, máy móc, thiết bị sản xuất thực tế. |
| **TTS / TA** | Tổng Tài sản (Total Assets) | Toàn bộ giá trị tài sản doanh nghiệp đang nắm giữ ($\text{TSNH} + \text{TSDH}$). |
| **VCSH / Equity** | Vốn chủ sở hữu (Book Value of Equity) | Phần tài sản thực sự thuộc về cổ đông sau khi trả hết nợ ($\text{TTS} - \text{Tổng Nợ}$). |
| **ICB** | Industry Classification Benchmark | Chuẩn phân loại ngành chứng khoán quốc tế (Sản xuất, BĐS, Bán lẻ, Công nghệ, Ngân hàng...). |
| **Median & MAD** | Trung vị & Độ lệch tuyệt đối trung vị | Thước đo "giá trị ở giữa" và "độ phân tán" **không bị phá hỏng bởi các con số quá dị biệt**. |
| **ESG (G)** | Environmental – Social – **Governance** | Phát triển bền vững; trụ cột **G** là Quản trị & Minh bạch tài chính. |

---

### 0.2. Bộ Số liệu Mẫu Xuyên suốt: So sánh 2 Doanh nghiệp Sản xuất Giả định
Để bạn **thấy tận mắt từng công thức hoạt động ra sao**, toàn bộ Phần I dưới đây sẽ lấy cùng một bộ số liệu hoàn chỉnh (đã cân đối chuẩn kế toán 100%) của **2 doanh nghiệp cùng ngành Sản xuất** (đơn vị tính: **Tỷ đồng**):

- **Công ty A — "Công ty Minh Bạch":** Làm ăn tăng trưởng đều đặn, thu tiền mặt tốt, biên lợi nhuận ổn định, ít vay nợ.
- **Công ty B — "Công ty Thổi Số":** Chạy doanh số cuối năm bằng cách cho nợ ồ ạt, biên lãi gộp tụt dốc, kéo giảm tỷ lệ khấu hao, đẩy nhiều tiền vào *Phải thu khác dài hạn* và *Chi phí XDCB dở dang*, báo lãi sổ sách `+65 tỷ` nhưng dòng tiền kinh doanh `CFO` lại âm `-65 tỷ`!

| Chỉ tiêu BCTC (Đơn vị: Tỷ VNĐ) | Mã số BCTC | Minh Bạch $t-1$ (2024) | Minh Bạch $t$ (2025) | Thổi Số $t-1$ (2024) | Thổi Số $t$ (2025) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **I. Báo cáo Tình hình Tài chính (`B01-DN`)** | | | | | |
| Tiền & tương đương tiền | `110` | 145,0 | 182,0 | 40,0 | 20,0 |
| Phải thu ngắn hạn của khách hàng | `131` | 120,0 | 130,0 | 150,0 | **300,0** |
| Trả trước cho người bán ngắn hạn | `132` | 20,0 | 22,0 | 50,0 | **80,0** |
| Phải thu ngắn hạn khác | `136` | 15,0 | 16,0 | 40,0 | 30,0 |
| Hàng tồn kho | `140` | 150,0 | 160,0 | 120,0 | 110,0 |
| $\rightarrow$ **Tài sản ngắn hạn (TSNH)** | `100` | **450,0** | **510,0** | **400,0** | **540,0** |
| Tài sản cố định hữu hình ròng (PP&E) | `221` | 400,0 | 430,0 | 350,0 | 340,0 |
| Đầu tư tài chính dài hạn | `250` | 50,0 | 60,0 | 50,0 | 40,0 |
| Tài sản dài hạn khác *(gồm Phải thu dài hạn khác `216` + XDCB dở dang `242`)* | `216+242` | 100,0 *(trong đó PT khác DH = 0)* | 100,0 *(PT khác DH = 0)* | 200,0 *(PT khác DH = 0)* | **430,0** *(trong đó PT khác DH = 220, XDCB = 210)* |
| $\rightarrow$ **TỔNG TÀI SẢN (TTS)** | `270` | **1.000,0** | **1.100,0** | **1.000,0** | **1.350,0** |
| Nợ ngắn hạn | `310` | 250,0 | 270,0 | 520,0 | **900,0** |
| Nợ dài hạn | `330` | 100,0 | 90,0 | 230,0 | 250,0 |
| $\rightarrow$ **Tổng Nợ phải trả** | `300` | **350,0** | **360,0** | **750,0** | **1.150,0** |
| **Vốn chủ sở hữu (VCSH)** | `400` | **650,0** | **740,0** | **250,0** | **200,0** |
| *(Trong đó: LNST chưa phân phối lũy kế)* | `421` | 280,0 | 360,0 | -20,0 | **-120,0** |
| **II. Báo cáo KQKD (`B02-DN`)** | | | | | |
| Doanh thu thuần (DT) | `10` | 1.000,0 | 1.120,0 | 1.000,0 | **1.350,0** |
| Giá vốn hàng bán (COGS) | `11` | 700,0 | 772,8 | 700,0 | 1.012,5 |
| Lợi nhuận gộp (LNG) | `20` | 300,0 | 347,2 | 300,0 | 337,5 |
| Chi phí bán hàng + Quản lý DN (SG&A) | `25+26` | 120,0 | 132,0 | 160,0 | 240,0 |
| Lợi nhuận thuần từ HĐKD (EBIT) | `30` | 180,0 | 215,2 | 140,0 | 97,5 |
| Lợi nhuận sau thuế (NI) | `60` | 140,0 | 168,0 | 100,0 | **+65,0** |
| **III. Báo cáo LCTT (`B03-DN`)** | | | | | |
| Lưu chuyển tiền thuần từ HĐKD (**CFO**) | `20` | **+165,0** | **+190,0** | +60,0 | **-65,0** |
| Khấu hao TSCĐ & BĐS đầu tư | `02` | 50,0 | 55,0 | 50,0 | **35,0** |

*(Bạn có thể kiểm tra ngay: Ở cả 2 công ty và cả 2 năm, phương trình $\text{Tổng Tài sản} = \text{Tổng Nợ} + \text{VCSH}$ đều khớp chính xác tuyệt đối 100%, ví dụ: Minh Bạch 2025: $1.100 = 360 + 740$; Thổi Số 2025: $1.350 = 1.150 + 200$).*

---

## PHẦN I: GIẢI MÃ TỪNG KIẾN THỨC KINH TẾ – KẾ TOÁN – KIỂM TOÁN (CÓ TÍNH TAY TỪNG BƯỚC)

### 1.1. Ba mảnh ghép Báo cáo Tài chính (Cập nhật Thông tư 99/2025/TT-BTC thay thế TT 200/2014/TT-BTC)

#### A. Cập nhật Pháp lý Bắt buộc Phải Biết Năm 2026
- **Trước ngày 01/01/2026 (Dữ liệu lịch sử 2020–2025):** Doanh nghiệp Việt Nam lập BCTC theo **Thông tư 200/2014/TT-BTC**. Biểu mẫu số 1 gọi là *"Bảng Cân đối Kế toán"*.
- **Từ ngày 01/01/2026 trở đi:** Bộ Tài chính ban hành **Thông tư 99/2025/TT-BTC** (ngày 27/10/2025) chính thức **thay thế Thông tư 200/2014/TT-BTC**.
  - Thay đổi dễ thấy nhất tại **Phụ lục IV**: Đổi tên *"Bảng Cân đối Kế toán"* thành **"Báo cáo Tình hình Tài chính"** (`Mẫu B01-DN`) để đồng bộ với chuẩn quốc tế IFRS.
  - Thay đổi về tài khoản tại **Phụ lục II**: Chuẩn hóa tên một số tài khoản (ví dụ `TK 112` gọi rõ là *Tiền gửi không kỳ hạn*) và bổ sung chỉ tiêu mới (như *Tài sản sinh học*).
  - **Điểm cực lợi cho AI dữ liệu (`FinAudit AI`):** Thông tư 99/2025 quy định **tuyệt đối không thay đổi "Mã số" cố định của các chỉ tiêu** trên B01-DN, B02-DN, B03-DN. Nhờ đó, code Python của ta có thể đọc liền mạch dữ liệu năm 2020–2025 (TT 200) nối tiếp sang năm 2026+ (TT 99) mà không bị đứt gãy!

#### B. Cách Nhớ Bản chất 3 Báo cáo Bằng Hình ảnh Đời thường
Hãy tưởng tượng một doanh nghiệp giống như **cá nhân bạn**:
1. **Báo cáo Tình hình Tài chính (`B01-DN` — Trước đây là BCĐKT):** Giống như việc tối ngày 31/12 bạn mở ví và kiểm kê: Bạn đang có **tài sản** gì (tiền trong ví, xe máy, tiền bạn bè đang nợ bạn = 100 triệu), bạn đang **nợ** ai (nợ thẻ tín dụng 30 triệu), vậy **tài sản ròng thực sự của bạn (Vốn chủ sở hữu)** là 70 triệu. Luôn đúng công thức: $\text{Tài sản} = \text{Nợ} + \text{VCSH}$.
2. **Báo cáo Kết quả Kinh doanh (`B02-DN` — KQKD):** Giống như sổ ghi chép cả năm bạn kiếm được bao nhiêu (Lương + Bán hàng) trừ đi chi phí ăn ở, đi lại = Tiền lãi trong năm. **Cạm bẫy nằm ở đây:** Kế toán ghi nhận theo *nguyên tắc dồn tích* — cứ giao hàng xuất hóa đơn là tính vào "Doanh thu" và "Lãi", **dù khách hàng chưa trả tiền mặt**!
3. **Báo cáo Lưu chuyển Tiền tệ (`B03-DN` — LCTT):** Giống như **sao kê tài khoản ngân hàng thực tế**. Tiền chỉ được ghi khi thực sự "ting ting" vào tài khoản hoặc trừ tiền ra khỏi tài khoản. Trong đó **CFO (Dòng tiền từ hoạt động kinh doanh)** là "mạch máu" quan trọng nhất: Nếu sổ sách bảo lãi 65 tỷ nhưng sao kê bán hàng `CFO` lại âm `-65 tỷ` (như **Công ty Thổi Số** ở bảng trên), chắc chắn có dấu hiệu bất thường cần kiểm tra ngay!

---

### 1.2. Lý thuyết Kinh tế & Khung ESG-G (Giải thích bằng Ví dụ Đời thường)

1. **Bất cân xứng Thông tin (*Information Asymmetry* — Akerlof, 1970, Giải Nobel Kinh tế 2001):**
   - *Ví dụ đời thường:* Bạn đi mua một chiếc xe máy cũ. Người bán biết rõ xe từng bị ngập nước hay bổ máy, còn bạn chỉ nhìn thấy vỏ xe sơn bóng loáng. Vì sợ mua nhầm xe kém chất lượng ("quả chanh" — *Lemons*), bạn ép giá hoặc không dám mua.
   - *Ánh xạ sang tài chính:* Ban Giám đốc nắm rõ nợ xấu bên trong công ty, còn Ngân hàng và Nhà đầu tư chỉ thấy BCTC. `FinAudit AI` đóng vai **"thợ máy soi khung gầm tự động"**, giảm bất cân xứng thông tin để dòng vốn chảy vào đúng doanh nghiệp làm ăn thật.
2. **Lý thuyết Đại diện (*Agency Theory* — Jensen & Meckling, 1976):**
   - *Ví dụ đời thường:* Bạn mở quán cà phê rồi thuê một quản lý và thưởng nếu doanh thu tháng đạt 200 triệu. Người quản lý có thể xả khuyến mãi lỗ vốn hoặc bán chịu cho người quen để ép doanh thu lên 200 triệu lấy thưởng, bất chấp quán bị hụt tiền mặt.
   - *Ánh xạ sang doanh nghiệp:* Lợi ích ngắn hạn của Ban Điều hành (thưởng KPI, giữ giá cổ phiếu) xung đột với lợi ích dài hạn của cổ đông & chủ nợ $\rightarrow$ sinh ra **Quản trị lợi nhuận (Earnings Management)**.
3. **Tam giác Gian lận (*Fraud Triangle* — Cressey, 1953):**
   - Một vụ thao túng BCTC thường có đủ 3 chân kiềng: **(1) Áp lực** (ví dụ: sắp đến hạn trả nợ 900 tỷ nợ ngắn hạn mà tiền mặt chỉ còn 20 tỷ như Công ty Thổi Số), **(2) Cơ hội** (kiểm soát nội bộ lỏng lẻo, giao dịch với công ty sân sau khó bị soi), và **(3) Biện minh** ("làm đẹp sổ năm nay để ngân hàng gia hạn khoản vay, năm sau thị trường tốt lên sẽ trả hết").
4. **Thống kê Thiệt hại Thực tế (ACFE Report to the Nations, 2024):**
   - Trong 1.921 vụ gian lận nghề nghiệp trên toàn cầu, **gian lận BCTC** chỉ chiếm **5%** số vụ nhưng gây thiệt hại trung vị **cao nhất mọi loại gian lận: 766.000 USD/vụ** (gấp hơn 6 lần gian lận biển thủ tài sản thông thường).
5. **Liên kết ESG — Trụ cột G (Governance — Quản trị Bền vững):**
   - Cuộc thi SE-Hackathon hướng tới *tương lai bền vững*. Bền vững không chỉ là trồng cây xanh (**E** – Môi trường) hay từ thiện (**S** – Xã hội), mà còn là **minh bạch tài chính & quản trị doanh nghiệp trung thực (G – Governance)**. Một thị trường tài chính minh bạch giúp ngăn chặn đổ vỡ dây chuyền (như các bê bối trái phiếu/cổ phiếu) và bảo vệ hàng triệu nhà đầu tư nhỏ lẻ.

---

### 1.3. Chất lượng Lợi nhuận & Hiện tượng Dồn tích (Sloan, 1996; Dechow et al., 2010)

Theo **Sloan (1996)** (*The Accounting Review*), lợi nhuận kế toán luôn gồm 2 phần:
$$\text{Lợi nhuận (NI)} = \text{Tiền mặt thực thu (CFO)} + \text{Khoản dồn tích trên sổ sách (Accruals)}$$

- **Bản chất dễ nhớ:** 1 đồng lợi nhuận đến từ **tiền tươi (`CFO`)** rất bền vững. Ngược lại, 1 đồng lợi nhuận đến từ **dồn tích (`Accruals`)** (ví dụ: bán chịu chưa thu được tiền) rất dễ bị "bốc hơi" ở các năm sau khi khách hàng bùng nợ.

#### Công thức 1: Tỷ số Chất lượng Dòng tiền (`CFO / NI`)
$$\text{CFO/NI} = \frac{\text{CFO}_t}{\text{NI}_t}$$
- **Ngưỡng đọc hiểu:** $\ge 1.0$ là rất tốt (lãi đi kèm tiền thật); $< 0.5$ là yếu; **âm (khi $\text{NI} > 0$ và $\text{CFO} < 0$)** là **Phân kỳ dòng tiền nghiêm trọng**.
- **Tính tay trên 2 công ty mẫu (Năm 2025):**
  - *Công ty Minh Bạch:* $\text{CFO/NI} = \dfrac{190}{168} = \mathbf{1.1310}$ $\rightarrow$ **Cực tốt!** Mỗi 1 đồng lãi sổ sách mang về 1,13 đồng tiền mặt thực tế.
  - *Công ty Thổi Số:* $\text{CFO/NI} = \dfrac{-65}{65} = \mathbf{-1.0000}$ $\rightarrow$ **Báo động đỏ!** Sổ sách báo lãi `+65 tỷ`, nhưng kinh doanh lại làm chảy máu `-65 tỷ` tiền mặt.

#### Công thức 2: Tỷ số Dồn tích (`Accrual Ratio`)
$$\text{Accrual Ratio} = \frac{\text{NI}_t - \text{CFO}_t}{\text{Tổng Tài sản bình quân}} = \frac{\text{NI}_t - \text{CFO}_t}{(\text{TTS}_t + \text{TTS}_{t-1}) / 2}$$
- **Ngưỡng đọc hiểu:** Gần `0` hoặc hơi âm là chất lượng cao; dương lớn (VD: $> +0.10$, tức > 10% tổng tài sản) là dấu hiệu lợi nhuận "trên giấy" quá nặng.
- **Tính tay trên 2 công ty mẫu:**
  - *Công ty Minh Bạch:* $\dfrac{168 - 190}{(1.100 + 1.000)/2} = \dfrac{-22}{1.050} = \mathbf{-0.0210}$ (`-2,10%`) $\rightarrow$ Chất lượng lợi nhuận rất thực chất.
  - *Công ty Thổi Số:* $\dfrac{65 - (-65)}{(1.350 + 1.000)/2} = \dfrac{+130}{1.175} = \mathbf{+0.1106}$ (`+11,06%`) $\rightarrow$ **Vượt ngưỡng +10%**, báo hiệu dồn tích quá mức!

---

### 1.4. Giải phẫu Chi tiết 8 Biến của Beneish M-Score (1999) — Tính Tay Từng Biến

Phương trình gốc của **Giáo sư Messod D. Beneish (1999)** (*Financial Analysts Journal*):

$$M = -4.84 + 0.920\cdot\text{DSRI} + 0.528\cdot\text{GMI} + 0.404\cdot\text{AQI} + 0.892\cdot\text{SGI} + 0.115\cdot\text{DEPI} - 0.172\cdot\text{SGAI} + 4.679\cdot\text{TATA} - 0.327\cdot\text{LVGI}$$

- **Quy tắc đọc kết quả:**
  - Nếu **$M > -1.78$** (ví dụ: `-0.84`, `+0.50` — lưu ý với số âm, `-0.84` **LỚN HƠN** `-1.78`!) $\rightarrow$ **Cảnh báo Đỏ:** Có xác suất cao doanh nghiệp đang thao túng/làm đẹp lợi nhuận.
  - Nếu **$M \le -1.78$** (ví dụ: `-2.33`, `-3.10`) $\rightarrow$ **Vùng Bình thường:** Ít có dấu hiệu thao túng.

Dưới đây là phần giải phẫu **từng biến trong 8 biến** kèm **tính tay từng bước** cho cả **Công ty Minh Bạch** và **Công ty Thổi Số**:

#### 1. `DSRI` — Chỉ số Ngày Phải thu (*Days' Sales in Receivables Index*)
- **Công thức:** $\text{DSRI} = \dfrac{\text{Phải thu KH}_t / \text{DT}_t}{\text{Phải thu KH}_{t-1} / \text{DT}_{t-1}}$
- **Giải nghĩa dễ hiểu:** So sánh tỷ lệ *bán chịu* năm nay với năm trước. Nếu `DSRI = 1.0`, tốc độ tăng nợ phải thu bằng tốc độ tăng doanh thu (bình thường). Nếu **`DSRI > 1.0`**, khách hàng nợ tăng nhanh hơn nhiều so với doanh thu $\rightarrow$ nghi vấn doanh nghiệp **ép đẩy hàng cho đại lý cuối năm** hoặc **xuất hóa đơn khống** để thổi doanh thu!
- **Tính tay:**
  - *Minh Bạch:* $\dfrac{130 / 1.120}{120 / 1.000} = \dfrac{0.11607}{0.12000} = \mathbf{0.9673}$ *(Tốt: thu nợ còn nhanh hơn năm ngoái)*
  - *Thổi Số:* $\dfrac{300 / 1.350}{150 / 1.000} = \dfrac{0.22222}{0.15000} = \mathbf{1.4815}$ *(Đáng nghi: tỷ lệ bán chịu vọt tăng +48,15%!)*

#### 2. `GMI` — Chỉ số Biên Lợi nhuận Gộp (*Gross Margin Index*)
- **Công thức:** $\text{GMI} = \dfrac{\text{Biên LNG}_{t-1}}{\text{Biên LNG}_t} = \dfrac{\text{LNG}_{t-1} / \text{DT}_{t-1}}{\text{LNG}_t / \text{DT}_t}$
- **Giải nghĩa dễ hiểu:** Chú ý năm trước ($t-1$) nằm ở **tử số**, năm nay ($t$) nằm ở **mẫu số**! Do đó, khi **`GMI > 1.0`** nghĩa là **biên lãi gộp năm nay bị thu hẹp/xấu đi** so với năm ngoái $\rightarrow$ doanh nghiệp đang mất sức cạnh tranh, dẫn đến **áp lực phải chỉnh sửa sổ sách** để giữ vẻ ngoài đẹp đẽ.
- **Tính tay:**
  - *Minh Bạch:* $\dfrac{300 / 1.000}{347.2 / 1.120} = \dfrac{0.3000}{0.3100} = \mathbf{0.9677}$ *(Tốt: biên lãi gộp cải thiện từ 30% lên 31%)*
  - *Thổi Số:* $\dfrac{300 / 1.000}{337.5 / 1.350} = \dfrac{0.3000}{0.2500} = \mathbf{1.2000}$ *(Cảnh báo: biên lãi gộp tụt mạnh từ 30% xuống 25%!)*

#### 3. `AQI` — Chỉ số Chất lượng Tài sản (*Asset Quality Index*)
- **Công thức:** $\text{AQI} = \dfrac{1 - (\text{TSNH}_t + \text{TSCĐ}_t + \text{ĐT dài hạn}_t) / \text{TTS}_t}{1 - (\text{TSNH}_{t-1} + \text{TSCĐ}_{t-1} + \text{ĐT dài hạn}_{t-1}) / \text{TTS}_{t-1}}$
- **Giải nghĩa dễ hiểu:** Trong một doanh nghiệp, *TSNH + TSCĐ hữu hình + Đầu tư dài hạn* là nhóm tài sản "rõ ràng, nhìn thấy được". Phần còn lại ($1 - \text{tỷ trọng nhóm rõ ràng}$) chính là **tài sản dài hạn "mờ ám"** (như *Chi phí XDCB dở dang*, *Phải thu dài hạn khác*, *Chi phí trả trước dài hạn*). Khi **`AQI > 1.0`**, tỷ trọng tài sản "mờ ám" đang phình to $\rightarrow$ nghi vấn doanh nghiệp **vốn hóa chi phí** (lẽ ra phải trừ vào chi phí làm giảm lãi năm nay, nhưng lại nhét vào tài sản dài hạn để "giấu lỗ").
- **Tính tay:**
  - *Minh Bạch:* Tử số $= 1 - (510+430+60)/1.100 = 0.0909$; Mẫu số $= 1 - (450+400+50)/1.000 = 0.1000 \Rightarrow \text{AQI} = \dfrac{0.0909}{0.1000} = \mathbf{0.9091}$ *(Tốt)*
  - *Thổi Số:* Tử số $= 1 - (540+340+40)/1.350 = 0.3185$; Mẫu số $= 1 - (400+350+50)/1.000 = 0.2000 \Rightarrow \text{AQI} = \dfrac{0.3185}{0.2000} = \mathbf{1.5926}$ *(Rất đáng nghi: tỷ trọng tài sản dài hạn mờ ám tăng vọt từ 20% lên 31,85%!)*

#### 4. `SGI` — Chỉ số Tăng trưởng Doanh thu (*Sales Growth Index*)
- **Công thức:** $\text{SGI} = \dfrac{\text{DT}_t}{\text{DT}_{t-1}}$
- **Giải nghĩa dễ hiểu:** Bản thân tăng trưởng không phải gian lận, nhưng nghiên cứu thực nghiệm cho thấy doanh nghiệp tăng trưởng quá nóng (`SGI` rất cao) thường chịu áp lực lớn về vốn và kỳ vọng thị trường, khiến hệ thống kiểm soát nội bộ không theo kịp và xác suất thao túng cao hơn.
- **Tính tay:**
  - *Minh Bạch:* $1.120 / 1.000 = \mathbf{1.1200}$ *(Tăng 12% bền vững)*
  - *Thổi Số:* $1.350 / 1.000 = \mathbf{1.3500}$ *(Tăng nóng 35% nhưng đi kèm nợ phải thu tăng gấp đôi!)*

#### 5. `DEPI` — Chỉ số Khấu hao (*Depreciation Index*)
- **Công thức:** $\text{DEPI} = \dfrac{\text{KH}_{t-1} / (\text{TSCĐ}_{t-1} + \text{KH}_{t-1})}{\text{KH}_t / (\text{TSCĐ}_t + \text{KH}_t)}$
- **Lưu ý cực quan trọng với BCTC Việt Nam:** Trên Báo cáo KQKD Việt Nam (`B02-DN`) không có dòng riêng cho Khấu hao. Bạn **bắt buộc lấy Khấu hao TSCĐ từ Báo cáo Lưu chuyển Tiền tệ gián tiếp (`B03-DN`, Mã số `02`)**!
- **Giải nghĩa dễ hiểu:** Chú ý năm $t-1$ lại nằm trên tử số! Nếu **`DEPI > 1.0`**, nghĩa là **tỷ lệ trích khấu hao máy móc năm nay bị giảm xuống** (ví dụ: sửa sổ kế toán kéo dài tuổi thọ máy móc từ 5 năm lên 10 năm để chi phí khấu hao mỗi năm giảm đi một nửa $\rightarrow$ lãi kế toán tự động tăng thêm!).
- **Tính tay:**
  - *Minh Bạch:* $\dfrac{50/(400+50)}{55/(430+55)} = \dfrac{0.11111}{0.11340} = \mathbf{0.9798}$ *(Ổn định)*
  - *Thổi Số:* $\dfrac{50/(350+50)}{35/(340+35)} = \dfrac{0.12500}{0.09333} = \mathbf{1.3393}$ *(Nghi vấn: tỷ lệ khấu hao giảm bất thường từ 12,5% xuống 9,33%, giúp "tiết kiệm" ~15 tỷ chi phí sổ sách!)*

#### 6. `SGAI` — Chỉ số Chi phí Bán hàng & Quản lý (*SG&A Expenses Index*)
- **Công thức:** $\text{SGAI} = \dfrac{\text{SG\&A}_t / \text{DT}_t}{\text{SG\&A}_{t-1} / \text{DT}_{t-1}}$
- **Giải nghĩa dễ hiểu:** Đo mức độ phình to của chi phí vận hành so với doanh thu. Trong phương trình Beneish gốc, biến này mang hệ số âm nhẹ (`-0.172`).
- **Tính tay:**
  - *Minh Bạch:* $\dfrac{132 / 1.120}{120 / 1.000} = \dfrac{0.11786}{0.12000} = \mathbf{0.9821}$
  - *Thổi Số:* $\dfrac{240 / 1.350}{160 / 1.000} = \dfrac{0.17778}{0.16000} = \mathbf{1.1111}$

#### 7. `TATA` — Tổng Dồn tích trên Tổng Tài sản (*Total Accruals to Total Assets*)
- **Công thức:** $\text{TATA} = \dfrac{\text{LN từ HĐKD (EBIT)}_t - \text{CFO}_t}{\text{TTS}_t}$
- **Giải nghĩa dễ hiểu:** Đây là **biến "sát thủ" có trọng số lớn nhất (`+4.679`)** trong toàn bộ mô hình Beneish! Nó đo chênh lệch giữa lợi nhuận sổ sách và tiền mặt thực thu trên mỗi đồng tài sản. `TATA` càng dương lớn $\rightarrow$ điểm `M-Score` tăng vọt ngay lập tức.
- **Tính tay:**
  - *Minh Bạch:* $\dfrac{215.2 - 190.0}{1.100} = \mathbf{+0.0229}$ *(Rất nhỏ, tiền bám sát lợi nhuận)*
  - *Thổi Số:* $\dfrac{97.5 - (-65.0)}{1.350} = \dfrac{162.5}{1.350} = \mathbf{+0.1204}$ *(Rất lớn: hơn 12% tổng tài sản là lợi nhuận dồn tích không có tiền mặt!)*

#### 8. `LVGI` — Chỉ số Đòn bẩy Tài chính (*Leverage Index*)
- **Công thức:** $\text{LVGI} = \dfrac{\text{Tổng Nợ}_t / \text{TTS}_t}{\text{Tổng Nợ}_{t-1} / \text{TTS}_{t-1}}$
- **Giải nghĩa dễ hiểu:** `LVGI > 1.0` cho thấy doanh nghiệp vay nợ ngày càng nhiều hơn so với tổng tài sản.
- **Tính tay:**
  - *Minh Bạch:* $\dfrac{360 / 1.100}{350 / 1.000} = \dfrac{0.3273}{0.3500} = \mathbf{0.9351}$ *(Giảm tỷ lệ nợ)*
  - *Thổi Số:* $\dfrac{1.150 / 1.350}{750 / 1.000} = \dfrac{0.8519}{0.7500} = \mathbf{1.1358}$ *(Nợ đã chiếm tới 85,2% tổng tài sản!)*

#### TỔNG KẾT LẮP VÀO PHƯƠNG TRÌNH BENEISH M-SCORE:
- **Công ty Minh Bạch:**
  $$M = -4.84 + 0.920(0.9673) + 0.528(0.9677) + 0.404(0.9091) + 0.892(1.1200) + 0.115(0.9798) - 0.172(0.9821) + 4.679(0.0229) - 0.327(0.9351) = \mathbf{-2.3277}$$
  $\rightarrow$ Vì $-2.3277 \le -1.78$: **AN TOÀN (Không có dấu hiệu thao túng).**

- **Công ty Thổi Số:**
  $$M = -4.84 + 0.920(1.4815) + 0.528(1.2000) + 0.404(1.5926) + 0.892(1.3500) + 0.115(1.3393) - 0.172(1.1111) + 4.679(0.1204) - 0.327(1.1358) = \mathbf{-0.8411}$$
  $\rightarrow$ Vì $-0.8411 > -1.78$: **CẢNH BÁO ĐỎ (Vượt xa ngưỡng cảnh báo thao túng lợi nhuận!).**

---

### 1.5. Giải phẫu Mô hình Altman $Z''$-Score Thị trường Mới nổi (2005) — Tính Tay Từng Biến

#### Tại sao Việt Nam dùng bản $Z''$-Score (Emerging Market) thay vì bản $Z$-Score 1968?
- Bản gốc 1968 thiết kế cho nhà máy sản xuất niêm yết tại Mỹ, có chứa biến `Giá trị vốn hóa thị trường / Tổng nợ` (bị nhiễu bởi đầu cơ cổ phiếu và không dùng được cho doanh nghiệp chưa niêm yết/SME) và biến `Doanh thu / Tổng tài sản` (vốn rất lệch giữa ngành dịch vụ và sản xuất).
- **Altman (1995, 2005)** tinh chỉnh thành bản **$Z''$-Score cho Thị trường Mới nổi** (bỏ biến vòng quay tài sản, thay vốn hóa thị trường bằng **Giá trị sổ sách Vốn chủ sở hữu** và cộng hằng số chuẩn hóa `3.25` tương ứng thang xếp hạng trái phiếu quốc tế):

$$Z'' = 3.25 + 6.56 X_1 + 3.26 X_2 + 6.72 X_3 + 1.05 X_4$$

| Biến | Công thức | Ý nghĩa kinh tế | Minh Bạch (2025) | Thổi Số (2025) |
| :---: | :--- | :--- | :---: | :---: |
| **$X_1$** | $\dfrac{\text{TSNH} - \text{Nợ ngắn hạn}}{\text{TTS}}$ | **Thanh khoản ngắn hạn:** Âm nghĩa là lấy nợ ngắn hạn đi nuôi tài sản dài hạn (rất dễ mất thanh khoản!). | $\dfrac{510 - 270}{1.100} = \mathbf{+0.2182}$ | $\dfrac{540 - 900}{1.350} = \mathbf{-0.2667}$ |
| **$X_2$** | $\dfrac{\text{LNST chưa phân phối}}{\text{TTS}}$ | **Sức tích lũy dài hạn:** Doanh nghiệp làm ăn lâu năm có tích lũy được lợi nhuận hay đang lỗ lũy kế? | $\dfrac{360}{1.100} = \mathbf{+0.3273}$ | $\dfrac{-120}{1.350} = \mathbf{-0.0889}$ |
| **$X_3$** | $\dfrac{\text{EBIT}}{\text{TTS}}$ | **Sức sinh lời thực chất (ROA trước thuế & lãi vay):** Trọng số lớn nhất (`6.72`)! | $\dfrac{215.2}{1.100} = \mathbf{+0.1956}$ | $\dfrac{97.5}{1.350} = \mathbf{+0.0722}$ |
| **$X_4$** | $\dfrac{\text{VCSH (Sổ sách)}}{\text{Tổng Nợ phải trả}}$ | **Tấm đệm an toàn vốn:** Vốn chủ sở hữu đủ che chắn bao nhiêu phần nợ vay? | $\dfrac{740}{360} = \mathbf{2.0556}$ | $\dfrac{200}{1.150} = \mathbf{0.1739}$ |

#### Tính kết quả $Z''$-Score:
- **Công ty Minh Bạch:**
  $$Z'' = 3.25 + 6.56(0.2182) + 3.26(0.3273) + 6.72(0.1956) + 1.05(2.0556) = \mathbf{9.2212}$$
  $\rightarrow$ Vì $9.2212 > 2.60$: **VÙNG AN TOÀN TUYỆT ĐỐI (Safe Zone).**

- **Công ty Thổi Số:**
  $$Z'' = 3.25 + 6.56(-0.2667) + 3.26(-0.0889) + 6.72(0.0722) + 1.05(0.1739) = \mathbf{1.8788}$$
  $\rightarrow$ Vì $1.10 \le 1.8788 \le 2.60$: **VÙNG XÁM CẢNH BÁO (Grey Zone)** — đang tiến gần sát vùng nguy hiểm `< 1.10` (một phần nhờ lợi nhuận sổ sách được "thổi" lên giữ cho $X_3$ còn dương!).

#### Ma trận 4 Góc Phần tư Kết hợp `Beneish M-Score × Altman Z''-Score` (Đọc trong 3 giây):

| | **Altman $Z'' > 2.60$ (Tài chính Khỏe)** | **Altman $Z'' \le 2.60$ (Vùng Xám / Nguy hiểm)** |
| :--- | :--- | :--- |
| **Beneish $M > -1.78$ (Nghi thao túng)** | **Góc 2 — Rủi ro Chất lượng Lợi nhuận:** Tài chính còn đệm tốt nhưng cách ghi nhận lợi nhuận quá "hung hãn", cần soi lại doanh thu & phải thu. | **Góc 1 — RỦI RO TỐI ĐA (Ưu tiên Kiểm toán #1):** Vừa gặp áp lực tài chính/thanh khoản, vừa có dấu hiệu làm đẹp sổ sách *(như Công ty Thổi Số!)*. |
| **Beneish $M \le -1.78$ (Ít dấu hiệu thao túng)** | **Góc 4 — AN TOÀN & MINH BẠCH:** Sức khỏe tài chính vững và lợi nhuận thực chất *(như Công ty Minh Bạch!)*. | **Góc 3 — Rủi ro Kiệt quệ Thuần túy:** Doanh nghiệp khó khăn thật (có thể báo lỗ thật) nhưng không có dấu hiệu giấu số liệu. |

---

### 1.6. Chỉ số Đặc thù Việt Nam & Phân định Pháp lý (`TT 99/2025`, `TT 200/2014`, `TT 48/2019`, `VSA 240`)

#### A. Chỉ số Khoản mục Nhạy cảm (`SRR` — *Sensitive Receivables Ratio*)
$$\text{SRR} = \frac{\text{Phải thu khác (ngắn \& dài hạn)} + \text{Trả trước cho người bán}}{\text{Tổng Tài sản}}$$
- **Vì sao đặc biệt quan trọng tại Việt Nam?** Nếu doanh nghiệp để tăng *Phải thu khách hàng (`131`)* thì rất dễ bị soi doanh thu ảo. Do đó, nhiều doanh nghiệp chuyển tiền cho các công ty sân sau dưới danh nghĩa *đặt cọc hợp tác đầu tư (`Phải thu dài hạn khác 216`)* hoặc *tạm ứng trước tiền mua hàng (`Trả trước người bán 132`)*.
- **Tính tay (Năm 2025):**
  - *Minh Bạch:* $\dfrac{(16 + 0) + 22}{1.100} = \dfrac{38}{1.100} = \mathbf{3.45\%}$ *(Rất sạch)*
  - *Thổi Số:* $\dfrac{(30 + 220) + 80}{1.350} = \dfrac{330}{1.350} = \mathbf{24.44\%}$ *(Gần 1/4 tổng tài sản đang "trôi nổi" ở Phải thu khác & Trả trước người bán — cần mở ngay Thuyết minh BCTC `B09-DN` soi đối tác là ai!)*

#### B. Phân định Pháp lý Cực kỳ Chính xác Giữa **Kế toán Lập BCTC** và **Thuế TNDN** (Điểm 10 trước Giám khảo Kinh tế!)
Một nhầm lẫn rất hay gặp ở sinh viên là trích Thông tư 48/2019/TT-BTC để bảo doanh nghiệp "lập BCTC sai". **Cách hiểu đúng tuyệt đối theo luật hiện hành:**

| Tiêu chí | Căn cứ Lập & Trình bày BCTC (**Mục đích Kế toán**) | Căn cứ Tính Chi phí Được trừ (**Mục đích Thuế TNDN**) |
| :--- | :--- | :--- |
| **Văn bản áp dụng** | - **Thông tư 200/2014/TT-BTC** (cho BCTC lịch sử đến hết năm 2025).<br/>- **Thông tư 99/2025/TT-BTC** (hiệu lực từ **01/01/2026**, thay thế hoàn toàn TT 200/2014). | - **Thông tư 48/2019/TT-BTC** (sửa đổi bởi **TT 24/2022/TT-BTC**, gia hạn hiệu lực theo QĐ 1760/QĐ-BTC). |
| **Quy định cốt lõi về Dự phòng Phải thu Khó đòi (`TK 2293`)** | Dựa trên **nguyên tắc thận trọng và ước tính kế toán về tổn thất thực tế** có bằng chứng đáng tin cậy (khách hàng có dấu hiệu mất khả năng thanh toán là phải trích lập trên BCTC ngay để phản ánh trung thực tài sản). | Khoản 1 Điều 1 TT 48 khẳng định chỉ phục vụ **chi phí được trừ khi tính thuế TNDN** với khung cứng theo tuổi nợ quá hạn: **30%** (6 tháng–<1 năm), **50%** (1–<2 năm), **70%** (2–<3 năm), **100%** ($\ge 3$ năm) kèm đủ biên bản đối chiếu công nợ. |
| **Ví dụ chênh lệch thực tế** | Khách nợ 10 tỷ mới quá hạn 4 tháng nhưng giám đốc khách hàng vừa bị khởi tố/mất tích $\rightarrow$ **Trên BCTC (theo TT 99/2025 & TT 200/2014)** kế toán **phải trích lập dự phòng ngay** để không báo lãi ảo. | Khi quyết toán thuế cuối năm, nếu chưa đủ hồ sơ chứng từ phá sản/truy tố theo điều kiện chặt của TT 48, phần chi phí này có thể bị tạm loại khi tính thuế TNDN (tạo ra *chênh lệch tạm thời*). |

- **Chuẩn mực Kiểm toán VSA 240 (TT 214/2012/TT-BTC):** Yêu cầu kiểm toán viên luôn giữ **thái độ hoài nghi nghề nghiệp** và **mặc định có rủi ro gian lận trong ghi nhận doanh thu**.
- **Chuẩn mực Kế toán VAS 26:** Bắt buộc công khai chi tiết mọi giao dịch & số dư công nợ với **bên liên quan** trên Thuyết minh BCTC (`B09-DN`).

---

### 1.7. Lọc Ngành ICB & Chuẩn hóa Robust Z-Score (Giải mã Con số `1.4826` & Ví dụ Tính tay)

#### A. Vì sao Bắt buộc Loại bỏ Ngân hàng, Chứng khoán, Bảo hiểm?
- Ngân hàng huy động tiền gửi của dân (ghi là *Nợ phải trả*) để cho vay lại (ghi là *Tài sản*). Do đó tỷ lệ Nợ/Tổng tài sản của ngân hàng lành mạnh luôn là **90%–93%**! Nếu mang công thức Altman $Z''$ hay Beneish (thiết kế cho công ty sản xuất/thương mại) áp vào Vietcombank hay Techcombank thì sẽ báo ngân hàng "sắp phá sản" — hoàn toàn sai bản chất!

#### B. Giải mã Công thức `Robust Z-Score` theo Ngành ICB (Vì sao không dùng Trung bình & Độ lệch chuẩn?)
Giả sử một nhóm ngành có **5 doanh nghiệp** với tỷ lệ `SRR` (Phải thu khác + Trả trước / Tổng TS) lần lượt là:
`[8%, 10%, 12%, 15%, 65%]` *(trong đó công ty số 5 có tỷ lệ 65% cực kỳ bất thường!)*.

1. **Nếu dùng Z-Score cổ điển (dựa trên Trung bình `Mean` và Độ lệch chuẩn `SD`):**
   - $\text{Mean} = \dfrac{8 + 10 + 12 + 15 + 65}{5} = \mathbf{22\%}$ *(Bị chính công ty dị biệt 65% kéo vống trung bình ngành lên tận 22%!)*
   - $\text{SD} = \mathbf{24.18\%}$
   - $z_{\text{cổ điển}}(\text{Công ty 5}) = \dfrac{65\% - 22\%}{24.18\%} = \mathbf{+1.78}$ *(Nhỏ hơn ngưỡng bất thường 2.0 $\rightarrow$ Công ty cực kỳ bất thường lại thoát lưới vì tự nó làm méo chuẩn ngành!)*

2. **Nếu dùng `Robust Z-Score` (dựa trên Trung vị `Median` và `MAD`):**
   - **Trung vị (`Median`):** Giá trị đứng chính giữa khi xếp tăng dần `[8%, 10%, 12%, 15%, 65%]` $\Rightarrow \text{Median} = \mathbf{12\%}$ *(Không hề bị kéo lệch bởi con số 65%!)*
   - **Độ lệch tuyệt đối trung vị (`MAD`):** Tính khoảng cách $|x - \text{Median}|$ cho 5 công ty:
     - $|8 - 12| = 4\%$; $|10 - 12| = 2\%$; $|12 - 12| = 0\%$; $|15 - 12| = 3\%$; $|65 - 12| = 53\%$.
     - Sắp xếp tăng dần `[0%, 2%, 3%, 4%, 53%]` $\Rightarrow$ Giá trị ở giữa là $\text{MAD} = \mathbf{3\%}$.
   - **Con số `1.4826` từ đâu ra?** Trong toán thống kê, với phân phối chuẩn (hình chuông), $\text{MAD} \approx 0.6745 \times \text{SD}$. Do đó ta nhân $\text{MAD}$ với $1 / 0.6745 = \mathbf{1.4826}$ để quy đổi `MAD` về cùng đơn vị với độ lệch chuẩn (`SD`)!
   - **Thay vào công thức:**
     $$z_{\text{robust}}(\text{Công ty 5}) = \frac{65\% - 12\%}{1.4826 \times 3\%} = \frac{53\%}{4.4478\%} = \mathbf{+11.92}$$
   $\rightarrow$ **Bắt gọn ngay lập tức!** Điểm `z = +11.92` cho thấy Công ty 5 lệch gấp gần **12 lần độ lệch chuẩn ngành**, trong khi cách tính cổ điển chỉ ra `+1.78` và bỏ sót!

---

## PHẦN II: GIẢI MÃ TỪNG KIẾN THỨC CÔNG NGHỆ, DỮ LIỆU, AI & TRIỂN KHAI WEB

### 2.1. Kiến trúc 3 Tầng (Ví dụ "Tổ Kiểm toán 3 Chuyên gia")

Hãy tưởng tượng hệ thống `FinAudit AI` giống như một **Tổ Kiểm toán 3 Chuyên gia** ngồi cạnh nhau:
1. **Chuyên gia 1 — Kế toán trưởng Máy tính (`Tầng 1: Deterministic Core`):** Chuyên bấm máy tính các công thức Beneish, Altman $Z''$, CFO/NI, SRR bằng Python/Pandas. **Đặc điểm:** Cực kỳ kỷ luật, chính xác 100%, không bao giờ đoán mò hay cộng nhầm 1 đồng.
2. **Chuyên gia 2 — Thám tử Dữ liệu (`Tầng 2: Unsupervised ML — Isolation Forest + SHAP`):** Nhìn cùng lúc 12 chỉ số của hàng trăm doanh nghiệp trong cùng ngành để chỉ ra ai đang có tổ hợp dấu hiệu "lạc lõng/bất thường", rồi vẽ biểu đồ chỉ đích danh *"Chỉ số nào gây nghi ngờ nhiều nhất?"*.
3. **Chuyên gia 3 — Luật sư & Trợ lý Đọc Hồ sơ (`Tầng 3: Grounded Hybrid RAG`):** Mở đúng trang file PDF Thuyết minh BCTC (`B09-DN`) và mở đúng Điều/Khoản của `VSA 240`, `TT 99/2025`, `TT 200/2014`, `TT 48/2019` để đối chiếu. **Nguyên tắc sắt:** Không thấy trong tài liệu thì báo không có, cấm tuyệt đối bịa đặt!

---

### 2.2. Xử lý Dữ liệu Tài chính: 4 Lỗi Chết người & Ví dụ Minh họa

1. **Lỗi Chia cho 0 (`ZeroDivisionError` / `inf`):**
   - *Tình huống:* Một doanh nghiệp mới thành lập hoặc tạm ngừng kinh doanh có `Doanh thu năm trước = 0`. Khi tính $\text{SGI} = \text{DT}_t / \text{DT}_{t-1}$, máy tính chia cho `0` sẽ sinh ra vô cực (`inf`) làm hỏng toàn bộ thuật toán AI phía sau.
   - *Cách xử lý:* Dùng hàm chia an toàn `safe_divide(a, b)`: nếu $|b| < 0.000001$ thì trả về `NaN` (trống — Not a Number) thay vì `inf`.
2. **Lỗi Điền bừa Số `0` (`fillna(0)`):**
   - *Tình huống:* Công ty X thiếu dữ liệu Khấu hao năm ngoái (`NaN`). Nếu người mới viết `df.fillna(0)` rồi tính `DEPI`, kết quả `DEPI = 0` — máy tính sẽ tưởng công ty này "khấu hao siêu tốt", hoàn toàn sai sự thật!
   - *Cách xử lý:* Giữ nguyên `NaN` ở bước tính tỷ số, ghi nhận rõ tỷ lệ thiếu dữ liệu, và chỉ điền bằng **Trung vị ngành (Sector Median)** ngay trước khi đưa vào `Isolation Forest` (nghĩa là coi như bằng mặt bằng trung bình ngành, không phạt cũng không thưởng oan).
3. **Lỗi Ngoại lai Cực đoan (`Extreme Outliers`) & Kỹ thuật `Winsorization (1% – 99%)`:**
   - *Ví dụ tính tay:* Giả sử trong 100 doanh nghiệp, 99 doanh nghiệp có `SGI` (tăng trưởng doanh thu) từ `0.5` đến `2.8`, riêng 1 công ty năm ngoái bán 100 triệu, năm nay bán 50 tỷ nên `SGI = 500`!
   - Nếu đưa thẳng `500` vào thuật toán, toàn bộ thang đo bị nén dẹt lại. Kỹ thuật **Winsorization [1%, 99%]** sẽ giữ nguyên mọi số nằm trong khoảng phân vị 1% đến 99%, còn con số `500` vượt trần 99% (giả sử mốc 99% là `3.0`) sẽ được **"cắt ngọn" về đúng `3.0`** khi đưa vào AI (nhưng trên giao diện Web vẫn hiển thị con số thật `500` để kế toán viên kiểm tra!).
4. **Lỗi Rò rỉ Dữ liệu Thời gian (`Data Leakage / Look-ahead Bias`):**
   - *Ví dụ đời thường:* Bạn muốn kiểm tra xem năm 2022 hệ thống có cảnh báo sớm được công ty Y phá sản năm 2024 hay không. Nếu bạn lấy luôn dữ liệu năm 2023–2024 để tính chuẩn ngành cho năm 2022 thì chẳng khác nào **"xem trước đề thi năm sau rồi tự khen mình đoán giỏi"**. Mọi phép chuẩn hóa cho năm $t$ chỉ được dùng dữ liệu tính đến hết năm $t$.

---

### 2.3. Thuật toán `Isolation Forest` (2008) & Công thức Điểm Rủi ro `0–100`

#### A. Học máy Không giám sát (*Unsupervised*) khác Có giám sát (*Supervised*) chỗ nào?
- **Có giám sát (VD: XGBoost):** Giống như dạy trẻ phân biệt táo ngon và táo hỏng bằng cách đưa sẵn 1.000 quả táo đã dán nhãn "Ngon" / "Hỏng". Nếu bạn **không có sẵn nhãn thật** (vì `vnstock` không có cột nhãn "gian lận"), bạn không thể dạy đúng được.
- **Không giám sát (VD: Isolation Forest):** Không cần ai dán nhãn trước! Bạn đổ 100 quả táo ra bàn; 90 quả màu đỏ tròn đều nằm thành một cụm, còn 10 quả màu xám méo mó nằm tách hẳn ra ngoài $\rightarrow$ thuật toán tự nhận ra ngay 10 quả lạc lõng đó là **Bất thường (Anomaly)**.

#### B. Cơ chế "Chặt cây Cô lập" của `Isolation Forest` (Liu, Ting & Zhou, 2008)
Hãy tưởng tượng lớp học có **30 bạn sinh viên**: 29 bạn ngồi sát cạnh nhau ở giữa phòng, chỉ có **1 bạn ngồi một mình ở góc cuối phòng**.
- Bây giờ ta chơi trò vẽ các đường thẳng ngẫu nhiên chia căn phòng thành 2 nửa cho đến khi tách riêng được từng người vào một ô:
  - Để tách riêng **bạn ngồi một mình ở góc phòng** (điểm bất thường): Chỉ cần **1 hoặc 2 nét cắt** là cô lập xong! (**Độ dài đường đi trên cây rất ngắn**).
  - Để tách riêng một bạn ngồi chen chúc giữa đám đông 29 người (điểm bình thường): Phải cắt đi cắt lại **7–8 nét cắt** mới tách ra được! (**Độ dài đường đi rất dài**).
- Lặp lại trò chơi này trên **300 cây ngẫu nhiên** (`n_estimators = 300`), sau đó lấy độ dài đường đi trung bình $\rightarrow$ Doanh nghiệp nào liên tục bị cô lập chỉ sau vài nét cắt chính là doanh nghiệp có **tổ hợp chỉ số tài chính dị biệt nhất**!

#### C. Ý nghĩa 4 Siêu tham số (Hyperparameters) khi Code
| Tham số | Giá trị chọn | Giải thích dễ hiểu |
| :--- | :---: | :--- |
| `n_estimators` | `300` | Số lượng "cây cô lập" cùng bỏ phiếu. 300 cây giúp điểm số rất ổn định, chạy trên máy 32GB RAM chỉ mất `< 0.5 giây`. |
| `contamination` | `0.10` | Giả định có khoảng **10%** quan sát có mức độ dị biệt cao nhất cần gắn cờ ưu tiên kiểm toán sâu (tương đương top decile). |
| `max_samples` | `'auto'` | Mỗi cây lấy tối đa 256 mẫu con ngẫu nhiên để chống hiện tượng điểm bất thường bị đám đông che khuất (*masking*). |
| `random_state` | `42` | "Chìa khóa khóa ngẫu nhiên" — đảm bảo bạn chạy code hôm nay hay ngày mai trước mặt giám khảo đều ra **chính xác 100% cùng một kết quả**. |

#### D. Quy đổi sang Thang Điểm Rủi ro Tổng hợp (`Composite Forensic Risk Score: 0 – 100`)
Hàm `decision_function` của `Isolation Forest` trả ra số thập phân khó đọc (VD: `-0.08` hay `+0.14`). Để người làm kinh tế nhìn phát hiểu ngay, ta quy đổi 4 trụ cột về cùng thang `0 – 100` (càng cao = rủi ro càng lớn) rồi ghép theo trọng số minh bạch:

$$\text{Composite Risk Score} = 0.35 \times S_{\text{Beneish}} + 0.25 \times S_{\text{Altman}} + 0.15 \times S_{\text{CashQuality}} + 0.25 \times S_{\text{IsoForest}}$$

**Ví dụ minh họa cho 2 công ty mẫu:**
- **Công ty Minh Bạch:** $S_{\text{Beneish}} = 12$, $S_{\text{Altman}} = 5$, $S_{\text{CashQuality}} = 8$, $S_{\text{IsoForest}} = 14$
  $$\Rightarrow \text{Risk Score} = 0.35(12) + 0.25(5) + 0.15(8) + 0.25(14) = 4.2 + 1.25 + 1.2 + 3.5 = \mathbf{10.15 / 100} \quad (\text{Rủi ro Thấp — Xanh ngọc})$$
- **Công ty Thổi Số:** $S_{\text{Beneish}} = 88$, $S_{\text{Altman}} = 62$, $S_{\text{CashQuality}} = 95$, $S_{\text{IsoForest}} = 84$
  $$\Rightarrow \text{Risk Score} = 0.35(88) + 0.25(62) + 0.15(95) + 0.25(84) = 30.8 + 15.5 + 14.25 + 21.0 = \mathbf{81.55 / 100} \quad (\text{Cảnh báo Cao — Đỏ thẫm})$$

---

### 2.4. AI Có Giải thích — `SHAP` (2017): Ví dụ "Chia tiền Taxi" & Đọc Biểu đồ Thác nước

#### A. Hiểu Giá trị Shapley (Nobel Kinh tế 2012) bằng Ví dụ "Đi chung Taxi"
Giả sử 3 bạn **An, Bình, Chi** đi chung 1 chuyến taxi hết tổng cộng **100.000 đ**. Nếu đi riêng thì nhà An gần nhất (hết 30k), nhà Bình xa hơn (hết 60k), nhà Chi xa nhất (hết 90k). Làm sao chia 100.000 đ công bằng nhất?
- Nhà toán học–kinh tế **Lloyd Shapley** chứng minh có **duy nhất một cách chia công bằng tuyệt đối**: tính *mức đóng góp biên trung bình* của từng người qua mọi thứ tự lên xe có thể.
- **Lundberg & Lee (2017)** đưa lý thuyết này vào AI thành **SHAP**: Coi tổng điểm rủi ro của doanh nghiệp giống như **cước taxi**, còn 12 chỉ số tài chính (`DSRI`, `TATA`, `AQI`, `Altman Z''`, `SRR`...) là **12 hành khách**! SHAP tính chính xác **mỗi chỉ số đã đóng góp cộng thêm (`+`) hay giảm bớt (`-`) bao nhiêu điểm rủi ro** so với mức trung bình thị trường (`Base Value`).

#### B. Cách Đọc Biểu đồ Thác nước SHAP (*SHAP Waterfall Chart*) trong 5 giây
Giả sử mức rủi ro trung bình thị trường là **`Base Value = 35.0`**. Với **Công ty Thổi Số (`81.55` điểm)**, biểu đồ thác nước sẽ bóc tách rõ ràng:
- Bắt đầu từ nền thị trường: `35.00` điểm
- **`TATA = +0.1204`** (Dồn tích cao, CFO âm sâu): **Đẩy rủi ro tăng `+16.80`** *(Thanh đỏ dài nhất)*
- **`DSRI = 1.4815`** (Phải thu KH tăng gấp đôi): **Đẩy rủi ro tăng `+11.40`** *(Thanh đỏ)*
- **`SRR = 24.44%`** (Phải thu khác & Trả trước lớn): **Đẩy rủi ro tăng `+9.20`** *(Thanh đỏ)*
- **`AQI = 1.5926`** (Tài sản dài hạn khác tăng mạnh): **Đẩy rủi ro tăng `+6.35`** *(Thanh đỏ)*
- **`Altman Z'' = 1.88`** (Vùng Xám thanh khoản yếu): **Đẩy rủi ro tăng `+4.90`** *(Thanh đỏ)*
- **`SGAI = 1.11`** (Các yếu tố bù trừ nhẹ): **Kéo rủi ro giảm `-2.10`** *(Thanh xanh)*
- **Tổng cộng:** $35.00 + 16.80 + 11.40 + 9.20 + 6.35 + 4.90 - 2.10 = \mathbf{81.55}$!

$\rightarrow$ Thay vì đưa một con số "hộp đen" vô nghĩa, kiểm toán viên nhìn biểu đồ biết ngay **việc đầu tiên phải làm là kiểm tra dòng tiền (`CFO`), công nợ phải thu (`TK 131`) và khoản phải thu khác (`TK 138 / 216`)**!

---

### 2.5. Giải mã 4 Lớp Kiểm chứng Khoa học (`Spearman`, `Jaccard` & `Backtest`)

Vì dùng học máy không giám sát (không bịa nhãn gian lận giả), ta chứng minh độ tin cậy bằng **4 thước đo toán học chuẩn mực**:

1. **Lớp 1 — Unit Test Toán học:** Kiểm tra lại toàn bộ công thức bằng bộ test tự động (`assert abs(ket_qua_code - ket_qua_tinh_tay) < 1e-6`). Yêu cầu sai số = **`0.0000%`**.
2. **Lớp 2 — Hệ số Tương quan Hạng Spearman ($\rho$ — Đọc là "Rô"):**
   - *Giải thích dễ hiểu:* Bạn có 2 bảng xếp hạng rủi ro của 100 công ty: Bảng 1 do **Beneish M-Score** xếp, Bảng 2 do **Isolation Forest** xếp. Hệ số Spearman $\rho$ nằm từ `-1` đến `+1`:
     - $\rho \approx +1$: Hai mô hình xếp hạng gần như giống hệt nhau.
     - $\rho \approx 0$: Hai mô hình chẳng liên quan gì nhau.
     - Nếu $\rho$ dương và có ý nghĩa thống kê ($p < 0.001$), chứng tỏ thuật toán AI không giám sát thực sự học được đúng cấu trúc rủi ro kế toán chứ không chạy ngẫu nhiên!
3. **Lớp 3 — Độ tương đồng Jaccard ($J$) để Kiểm tra Độ ổn định:**
   - **Công thức:**
     $$J(A, B) = \frac{|A \cap B|}{|A \cup B|} = \frac{\text{Số công ty trùng nhau ở cả 2 lần chạy}}{\text{Tổng số công ty khác nhau ở cả 2 lần chạy}}$$
   - **Ví dụ tính tay:** Chạy mô hình lần 1 (`seed = 42`) ra Top 10 công ty rủi ro cao nhất (tập $A$). Chạy lại lần 2 (`seed = 99`) ra Top 10 công ty (tập $B$). Giả sử có **9 công ty trùng nhau** ở cả 2 danh sách:
     - Giao $|A \cap B| = 9$; Hợp $|A \cup B| = 10 + 10 - 9 = 11$.
     - $J(A, B) = \dfrac{9}{11} = \mathbf{81.8\%}$ *(Rất ổn định! Nếu mô hình bập bênh thì Jaccard sẽ tụt xuống 20–30%).*
4. **Lớp 4 — Đối chứng Thực chứng Hồi cứu (Retrospective Backtest):**
   - So sánh phân bố điểm rủi ro của **Nhóm Doanh nghiệp Đầu ngành Minh bạch** (VD: nhóm VN30 phi tài chính như `FPT`, `VNM`, `HPG`, `BMP`) với **Nhóm Doanh nghiệp từng nhận cảnh báo/kiểm soát/ngoại trừ kiểm toán công khai** để chứng minh sự tách biệt rõ rệt về mặt thống kê (kiểm định *Mann-Whitney U test*).

---

### 2.6. Giải mã `Hybrid RAG`: Chunking, `BM25`, Vector Search, `RRF` & Đánh giá `Hit Rate / MRR`

#### A. Chunking & Overlap (Cắt tài liệu có gối đầu)
- Một file PDF Thuyết minh BCTC dài 60 trang không thể nhồi cả cục vào bộ tìm kiếm. Ta cắt thành từng mảnh nhỏ gọi là **Chunk** (khoảng 400–600 ký tự).
- **Overlap (Gối đầu ~80 ký tự):** Giống như khi bạn cắt một tờ báo dài, đoạn 2 sẽ lặp lại 1–2 câu cuối của đoạn 1 để lỡ thông tin quan trọng nằm đúng đường cắt thì không bị đứt nghĩa! Mỗi chunk luôn đính kèm nhãn: `[Tài liệu: TT 99/2025, Phụ lục II]` hoặc `[Thuyết minh B09-DN, Trang 28]`.

#### B. Vì sao phải kết hợp `BM25` + `Vector Search` bằng công thức `RRF`?
- **BM25 (Tìm theo từ khóa chính xác):** Cực giỏi khi bạn gõ mã số chuyên ngành như `TK 2293`, `VSA 240`, `B01-DN`, `TT 99/2025`. Nhưng nếu bạn hỏi *"khách bùng nợ lâu năm xử lý thế nào"* mà trong luật lại viết *"nợ phải thu quá hạn khó đòi"*, BM25 có thể tìm sót!
- **Vector Search (Tìm theo ngữ nghĩa):** Biến câu chữ thành tọa độ toán học (*vector*) và đo góc gần nhau (**Cosine Similarity**), nên hiểu được *"bùng nợ"* gần nghĩa với *"phải thu khó đòi"*. Tuy nhiên nó lại hay nhầm giữa `TK 131` và `TK 138`!
- **Giải pháp Trộn hạng `RRF` (*Reciprocal Rank Fusion*):**
  $$\text{RRF}(d) = \frac{1}{60 + \text{Hạng}_{\text{BM25}}(d)} + \frac{1}{60 + \text{Hạng}_{\text{Vector}}(d)}$$
  *(Hằng số `60` là chuẩn thực nghiệm giúp cân bằng, không để 1 bộ tìm kiếm lấn át hoàn toàn bộ kia).*

**Ví dụ tính tay công thức `RRF` cho 3 đoạn văn bản (`A`, `B`, `C`):**
- Đoạn **A** đứng Hạng `1` ở BM25, Hạng `4` ở Vector $\Rightarrow \text{RRF}(A) = \dfrac{1}{61} + \dfrac{1}{64} = 0.016393 + 0.015625 = \mathbf{0.032018}$
- Đoạn **B** đứng Hạng `2` ở BM25, Hạng `2` ở Vector $\Rightarrow \text{RRF}(B) = \dfrac{1}{62} + \dfrac{1}{62} = 0.016129 + 0.016129 = \mathbf{0.032258}$
- Đoạn **C** đứng Hạng `3` ở BM25, Hạng `1` ở Vector $\Rightarrow \text{RRF}(C) = \dfrac{1}{63} + \dfrac{1}{61} = 0.015873 + 0.016393 = \mathbf{0.032266}$
$\rightarrow$ Đoạn **C** và **B** (đều đạt thứ hạng cao đồng thời ở **cả hai** bộ tìm kiếm từ khóa + ngữ nghĩa) vượt lên đứng đầu bảng!

#### C. Giải mã 3 Chỉ số Đánh giá Chất lượng RAG (Kèm Ví dụ Tính tay trên 3 Câu hỏi)
Giả sử ta thử nghiệm bộ RAG với 3 câu hỏi kiểm toán:
- Câu 1: Đoạn luật đúng nằm ở **Vị trí #1** (Top 1).
- Câu 2: Đoạn luật đúng nằm ở **Vị trí #2** (trong Top 3).
- Câu 3: Đoạn luật đúng nằm ở **Vị trí #1** (Top 1).

1. **`Hit Rate@1` (Tỷ lệ trúng ngay kết quả đầu tiên):** Có 2/3 câu trúng ngay ở vị trí #1 $\Rightarrow \text{Hit@1} = \dfrac{2}{3} = \mathbf{66.7\%}$.
2. **`Hit Rate@3` (Tỷ lệ có mặt trong Top 3 kết quả):** Cả 3/3 câu đều nằm trong Top 3 $\Rightarrow \text{Hit@3} = \dfrac{3}{3} = \mathbf{100\%}$.
3. **`MRR` (*Mean Reciprocal Rank* — Trung bình nghịch đảo thứ hạng):**
   $$\text{MRR} = \frac{1}{3} \left( \frac{1}{1} + \frac{1}{2} + \frac{1}{1} \right) = \frac{2.5}{3} = \mathbf{0.833}$$
   *(Càng gần `1.000` nghĩa là hệ thống càng đưa đúng điều luật cần tìm lên ngay vị trí đầu tiên!)*

---

### 2.7. Triển khai Web App `Streamlit`: Offline vs. Online, Cache & Deploy Public

Hãy hình dung ứng dụng Web giống như **một nhà hàng phở chuyên nghiệp**:
- **Luồng Offline (`stage_1` $\rightarrow$ `stage_3`):** Là công việc **hầm xương, chuẩn bị sẵn nước dùng từ đêm hôm trước** (tải dữ liệu từ `vnstock`, làm sạch, tính 15 chỉ số, train `Isolation Forest`, tính sẵn `SHAP`, lưu thành file nén siêu tốc `.parquet` và `.joblib`).
- **Luồng Online (`stage_5 — app.py`):** Khi khách (Ban Giám khảo) mở trình duyệt Web và bấm chọn mã cổ phiếu, Web App không phải đi tải lại dữ liệu từ đầu mà "múc ngay nước dùng đã chuẩn bị sẵn" bằng cơ chế bộ nhớ đệm **`@st.cache_data`** (lưu bảng dữ liệu trong RAM) và **`@st.cache_resource`** (lưu mô hình AI trong RAM) $\rightarrow$ **Web phản hồi tức thì trong dưới 0,5 giây!**
- **Bảo mật Khóa API (`st.secrets`):** Nếu dùng thêm Gemini/OpenAI API cho trợ lý RAG, tuyệt đối không viết mã khóa (`API_KEY = "AIza..."`) thẳng vào file `.py` đẩy lên GitHub công khai, mà cất vào mục **Secrets** của Streamlit Cloud để tránh bị lộ khóa.

---

## PHẦN III: BỘ CÂU HỎI PHẢN BIỆN KHÓ NHẤT CỦA BAN GIÁM KHẢO KINH TẾ & GỢI Ý TRẢ LỜI

| # | Câu hỏi khó Giám khảo có thể đặt ra | Cách trả lời Sắc bén, Đúng Chuẩn Học thuật |
| :---: | :--- | :--- |
| **1** | *"Tại sao báo cáo vừa nhắc Thông tư 200/2014 vừa nhắc Thông tư 99/2025?"* | Vì dữ liệu BCTC lịch sử (2020–2025) các doanh nghiệp đã công bố được lập theo **Thông tư 200/2014/TT-BTC**; còn từ **01/01/2026**, **Thông tư 99/2025/TT-BTC** chính thức có hiệu lực thay thế TT 200 (đổi *Bảng CĐKT* thành *Báo cáo tình hình tài chính — B01-DN*). Nhờ TT 99/2025 giữ nguyên "Mã số" cố định của các chỉ tiêu, hệ thống của em liên thông trọn vẹn cả quá khứ và hiện tại. |
| **2** | *"Dự phòng phải thu khó đòi trên BCTC căn cứ Thông tư 48/2019 có đúng không?"* | Theo Khoản 1 Điều 1 **Thông tư 48/2019/TT-BTC**, TT 48 chỉ làm cơ sở xác định chi phí được trừ khi **tính thuế TNDN**; còn lập và trình bày dự phòng trên **BCTC** phải tuân thủ pháp luật kế toán (**TT 200/2014** trước 2026 và **TT 99/2025** từ 2026). Hệ thống phân tách rõ hai lớp này và chỉ dùng khung 30–50–70–100% của TT 48 làm mốc tham chiếu tuổi nợ bổ trợ. |
| **3** | *"Tại sao các bạn không dùng AI học sâu hay XGBoost chấm điểm gian lận cho 'xịn' hơn?"* | Vì dữ liệu công khai tại VN chưa có sẵn bộ nhãn "gian lận" chuẩn hóa đủ lớn. Nếu tự lấy công thức Beneish làm nhãn để train XGBoost sẽ mắc lỗi **rò rỉ dữ liệu (Circular Logic)** tạo độ chính xác ảo. Dùng **Isolation Forest không giám sát + Chuẩn hóa theo ngành ICB + SHAP** vừa khoa học 100%, không bịa nhãn, vừa giải thích được tường minh từng chỉ số cho kiểm toán viên. |
| **4** | *"Công ty bị hệ thống chấm 82/100 có nghĩa là họ chắc chắn gian lận đúng không? Các bạn có sợ bị kiện không?"* | **Tuyệt đối không kết luận doanh nghiệp gian lận.** Hệ thống tuân thủ nguyên tắc *thái độ hoài nghi nghề nghiệp* của **VSA 240**, chỉ đóng vai trò **công cụ sàng lọc chỉ báo rủi ro (Forensic Red Flags)** giúp kiểm toán viên và ngân hàng biết cần tập trung kiểm tra sâu vào khoản mục và trang Thuyết minh nào, tiết kiệm 60–70% thời gian đọc hồ sơ. |
| **5** | *"Hệ thống của các bạn có phân tích được Ngân hàng hay Công ty Chứng khoán không?"* | Nhóm đã **chủ động lọc bỏ định chế tài chính (Ngân hàng, Chứng khoán, Bảo hiểm)** theo chuẩn ngành ICB khỏi lõi Beneish & Altman $Z''$, vì cấu trúc BCTC của ngân hàng (theo TT 49/NHNN) không có giá vốn hàng bán hay hàng tồn kho. Các ngân hàng sẽ cần bộ chỉ số chuyên biệt riêng (như CAMELS, tỷ lệ nợ xấu NPL) ở giai đoạn mở rộng sau này. |
| **6** | *"Sản phẩm này có gì khác với Vietstock, CafeF hay FiinPro?"* | CafeF/Vietstock miễn phí nhưng chỉ hiển thị chỉ số bề nổi (P/E, ROE); FiinPro rất mạnh nhưng chi phí hàng trăm triệu/năm dành cho định chế lớn. `FinAudit AI` đánh vào khoảng trống **Pháp chứng Chất lượng Lợi nhuận + Giải thích AI (SHAP) + Soi chéo Thuyết minh PDF & Luật VAS** với chi phí SaaS hợp lý cho ngân hàng vừa/nhỏ, công ty kiểm toán SME và nhà đầu tư cá nhân. |
| **7** | *"Dự án đóng góp gì cho mục tiêu Phát triển Bền vững của cuộc thi?"* | Sản phẩm đánh trực diện vào **Trụ cột G (Governance — Quản trị & Minh bạch)** trong khung **ESG**: giúp phát hiện sớm rủi ro làm đẹp BCTC, hạn chế nợ xấu tín dụng cho hệ thống ngân hàng, bảo vệ cổ đông thiểu số và nâng cao chất lượng phân bổ vốn trên thị trường chứng khoán Việt Nam. |
| **8** | *"Nếu doanh nghiệp nộp BCTC dạng file PDF chụp ảnh đóng dấu (PDF scan) thì RAG xử lý thế nào?"* | Bộ đọc PDF của hệ thống tự động đo mật độ ký tự trên mỗi trang; nếu phát hiện PDF scan không có lớp văn bản gốc, hệ thống sẽ **cảnh báo rõ ràng ngay trên giao diện** thay vì để AI đoán mò gây ảo giác, đồng thời cho phép người dùng dán trực tiếp đoạn thuyết minh cần kiểm tra hoặc dùng bản PDF text chuẩn. |
