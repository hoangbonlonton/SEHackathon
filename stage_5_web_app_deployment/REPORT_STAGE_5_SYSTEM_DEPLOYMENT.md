# BÁO CÁO NGHIỆM THU GIAI ĐOẠN 5: TRIỂN KHAI HỆ THỐNG WEB APP STREAMLIT CHUẨN FINTECH SAAS — BẢN V2 HOÀN CHỈNH (`stage_5_web_app_deployment`)

> **Thời điểm nghiệm thu (Bản V4 Chuẩn Công sở — 4 Phân hệ Làm việc, Live Sync Vietcap IQ, Upload BCTC Linh hoạt, So sánh Ngành Trực diện, Chat Toàn màn hình + Link Cổng Chính phủ):** `2026-11-25 14:47`  
> **Trạng thái kiểm thử tự động:** **ALL SUITES PASSED (`test_stage5_app.py` 3/3 + `verify_chatbot_nlu.py` 19/19 + Live Vietcap IQ Sync FPT `8 năm`) — `0` ngoại lệ, `HTTP 200 OK` trong `0.94s`, sai số tái lập `TDH 2025 = 0.000đ`, upload BCTC dọc tiếng Việt tự do 10 chỉ tiêu PASS**  
> **Tài nguyên đo thực tế (Full-load cả 643 DN + AI + SHAP + RAG + 3D WebGL + PDF 91 trang):** **`481.6 MB` RAM** (`< 50%` hạn mức `1 GB` của Streamlit Community Cloud)

---

## 1. KIẾN TRÚC ỨNG DỤNG & HỆ THỐNG THIẾT KẾ V2 (`DEEP EMERALD & TERRACOTTA COPPER`)

Toàn bộ ứng dụng Web được tổ chức gọn gàng thành 5 thành phần đồng bộ trong [`stage_5_web_app_deployment/`](.) và Hệ thống Thiết kế tại [`design-system/finaudit-ai/`](../design-system/finaudit-ai/):

| File / Thành phần | Vai trò kỹ thuật | Nâng cấp hoàn thiện Bản V2 (V2-1 → V2-3) |
| :--- | :--- | :--- |
| [`assets/finaudit_logo.svg`](assets/finaudit_logo.svg) | Logo Vector SVG Chính thức **FinAudit AI** (Khiên Pháp chứng Ngọc Lục Bảo + Đường Quét Rủi ro Vàng Đồng) | Hiển thị **duy nhất 1 lần** trên Thanh Đầu trang Thống nhất và đồng bộ trong Báo cáo A4 PDF (loại bỏ lặp Logo ở Sidebar). |
| [`.streamlit/config.toml`](.streamlit/config.toml) | Cấu hình theme Deep Emerald & Warm Ivory (`#064E3B` / `#FAF8F5` / `#132A23`) & giới hạn upload 30 MB | Đồng bộ ngay từ khi tải trang, không chớp màu nền. |
| [`ui_components.py`](ui_components.py) | Design System V2 + 3 thành phần Website Pháp lý + **7 biểu đồ 2D chuẩn Mobile & 3 biểu đồ 3D Plotly WebGL động** | • **Typography V2:** `Plus Jakarta Sans` (700/800) + `Be Vietnam Pro` (400–700) + `JetBrains Mono` (600–800) kèm **Tiêu đề Pha 2 Màu** (Trắng Sứ ↔ Vàng Đồng trên nền tối; Ngọc Lục Bảo ↔ Đồng Đỏ trên nền sáng).<br>• **Fix Mobile 100% (`375px`):** Chuyển Thác nước SHAP sang **nằm ngang (`orientation='h'`)** kèm nhãn ngắn gọn (`<= 28` ký tự) & tiêu đề 2 dòng chuẩn Responsive.<br>• **Chuyển động Hiện màu dần (`Progressive Hover Sweep`):** 5 Thư mục Phân hệ & 6 nút Mẫu đối chứng quét màu mượt (`0.65s cubic-bezier`) khi di chuột vào và **khóa màu định danh** của thư mục khi đang ở bên trong (`#064E3B`, `#C2410C`, `#0F766E`, `#B45309`, `#047857`).<br>• **Khung Tìm kiếm Game Jam tương phản cao:** Viền dày `2.5px #132A23`, nền kem ấm `#FEF6E7`, đổ bóng cứng sắc nét `4px 4px 0 #064E3B`, nút Tìm kiếm Đồng Đỏ `#C2410C` nổi bật.<br>• **Thanh điểm 0–100 & Chú giải 3 vùng:** Gắn trực tiếp trên thẻ KPI và Sidebar; dọn sạch **0 emoji hoạt hình**, **0 dấu `**` thô**, **0 dấu `...` cắt cụt**. |
| [`live_scoring_service.py`](live_scoring_service.py) | Cầu nối **Live Scoring** & tạo file mẫu Excel/CSV (`Mau_Upload_BCTC_FinAudit_AI.xlsx`) | Tái sử dụng 100% logic gốc của Giai đoạn 2 (`02_forensic_features.py`) & Giai đoạn 3 (`03_train_validate_model.py`), bảo đảm điểm chấm trực tiếp **khớp tuyệt đối `0.000đ`** với điểm đã huấn luyện. |
| [`report_exporter.py`](report_exporter.py) | Xuất **Báo cáo Hồ sơ Kiểm toán Pháp chứng chuẩn A4 (`.html` In PDF)** | Đồng bộ 100% bản V2: nhúng **Logo SVG chính thức**, font `Plus Jakarta Sans + Be Vietnam Pro + JetBrains Mono`, tiêu đề pha 2 màu, **thanh điểm 0–100** trên 4 trụ cột, chú giải thang điểm 3 vùng, và làm sạch 100% dấu `**` & `...` qua `format_rag_markdown_to_html()` + `trim_excerpt_clean()`. |
| [`chat_assistant.py`](chat_assistant.py) | Bộ Điều phối Hội thoại Pháp chứng Tự nhiên (**Conversational Forensic NLU + Hybrid RAG**) | Hiểu câu chào hỏi/hướng dẫn, chuẩn hóa khẩu ngữ tiếng Việt (VD: *"nói cho tôi về luật VAS"*, *"TT 99 có gì mới?"*) để **không từ chối nhầm**, trả lời trực tiếp dữ liệu thật **643 DN + B09-DN** (*"TDH 2025 rủi ro bao nhiêu?"*, *"So sánh FPT và TDH"*, *"Top 5 cảnh báo đỏ"*), giải thích Beneish/Altman/SHAP, đồng thời giữ nguyên **100% Cổng Chống Ảo giác** cho câu hỏi ngoài phạm vi. |
| [`app.py`](app.py) | Ứng dụng Streamlit chính điều phối **5 Phân hệ chức năng**, **3 Thành phần chuẩn Pháp lý** & **Biểu tượng Chatbox Nổi** | • **Thanh điều hướng ngang 5 Thư mục** có biểu tượng Material vector + hiệu ứng quét màu dần.<br>• **Sidebar tinh gọn:** Bộ chọn 5 Vai trò + 6 Mẫu đối chứng hiển thị **điểm 2025 thật (`TDH • 80đ`, `FPT • 12đ`...)** kèm biểu tượng trạng thái & chú giải thang điểm.<br>• **Biểu tượng Chatbox nổi góc phải dưới (`fab_chat_launcher`):** Bấm mở **Hộp thoại kéo trượt bên phải (`@st.dialog(position="right")`)** hỏi đáp tự nhiên về Luật VAS, dữ liệu 643 DN, tải file PDF & kiểm tra Cổng Chống Ảo giác ngay trên mọi trang (tương thích mượt cả Mobile & Desktop). |

---

## 2. CHI TIẾT 5 PHÂN HỆ CHỨC NĂNG ĐÃ HOÀN THIỆN & KẾT NỐI DỮ LIỆU THẬT

1. **Phân hệ 1 — `Tổng quan Thị trường & Quét Rủi ro Ngành ICB` (Màu nhận diện: Ngọc Lục Bảo `#064E3B`):**
   - Lọc đa chiều theo *Năm (`2019–2025`)*, *15 Ngành ICB*, *Hạng Rủi ro*, *Sàn HOSE/HNX* và *Tìm nhanh mã/tên*.
   - Mặc định hiển thị **Chế độ 2D chuẩn phân tích** (nhanh, sắc nét trên Mobile & Desktop): **Ma trận Pháp chứng 2D (`Beneish M` vs. `Altman Z''`)** + **Xếp hạng 15 Ngành ICB**; cho phép chuyển sang **Chế độ 3D WebGL Động (`2019→2025`)** chỉ với 1 chạm.
   - Bảng Screener đi kèm **Thanh chú giải Thang điểm 3 vùng**, thanh tiến trình điểm `0–100`, nút mở nhanh **Hồ sơ 360°** và xuất **`.CSV`**.
2. **Phân hệ 2 — `Hồ sơ Pháp chứng Doanh nghiệp 360° & SHAP` (Màu nhận diện: Đồng Đỏ `#C2410C`):**
   - Chọn bất kỳ mã nào trong `643` doanh nghiệp (hoặc bấm 6 nút Mẫu đối chứng kèm điểm 2025 thật ở Sidebar).
   - Hiển thị Banner Định danh, Đồng hồ **Gauge (`0–100`)**, **4 Thẻ Trụ cột kèm Thanh điểm 0–100**, **Biểu đồ Thác nước SHAP nằm ngang (chuẩn Mobile 375px)**, **Radar đối sánh chuẩn ngành**, **Quỹ đạo Đa năm 2D mặc định + 3D Động tùy chọn (`2018–2025`)**.
   - Cầu nối tự động **`SHAP → Hybrid RAG`** (Mở sẵn Cờ đỏ #1, gấp gọn cờ #2–#3, sạch 100% dấu `**` & `...`): trích dẫn điều luật (`VSA 240`, `TT 99/2025`, `TT 200/2014`, `TT 48/2019`, `VAS 14/26`), bóc tách `B09-DN` và trang `PDF` kiểm toán thật, kèm nút **Xuất Báo cáo Kiểm toán `.HTML` chuẩn A4 (Logo SVG V2)** & **`.CSV`**.
3. **Phân hệ 3 — `Phòng Thẩm định BCTC Mới (Upload & What-If Live Scoring)` (Màu nhận diện: Ngọc Lam `#0F766E`):**
   - Khung 2 bước đóng thẻ song song liền mạch: Tải file mẫu Excel/CSV ([Mau_Upload_BCTC_FinAudit_AI.xlsx](../data_store/sample_uploads/Mau_Upload_BCTC_FinAudit_AI.xlsx)) → Upload BCTC 2 năm hoặc dùng **What-If Simulator** chỉnh trực tiếp trên bảng.
   - Chạy nối tiếp thời gian thực (`~0.76 giây`): **Trạm 0 (Data Integrity Gate)** → **CG1** → **CG2 (AI + SHAP)** → **CG3 (RAG)** + xuất báo cáo A4 V2 ngay lập tức.
4. **Phân hệ 4 — `Trung tâm Pháp lý VAS & Soi Thuyết minh PDF / B09-DN` (Màu nhận diện: Hổ Phách `#B45309`):**
   - Thẻ mở nhanh **Hộp thoại Chatbox Trợ lý AI** + 4 chủ đề pháp lý mẫu 1 chạm có biểu tượng Material sắc nét (không cắt chữ `...`).
   - *Tab 1:* **Bảng HTML Danh mục Hiệu lực 5 Văn bản Pháp quy Bộ Tài chính** tự xuống dòng 100%, hiển thị trọn vẹn nội dung (TT 99/2025, TT 200/2014, TT 48/2019, VSA 240, VAS 14/26).
   - *Tab 2:* **Chẩn đoán PDF BCTC Kiểm toán 3 tầng toàn màn hình** (chọn 4 bộ PDF 2025 thật hoặc upload `.pdf`) — tự động kích hoạt **Kênh 1 (`B09-DN` cấu trúc)** đối với PDF scan ảnh (`TDH`, `FPT`, `VNM`).
5. **Phân hệ 5 — `Trung tâm Kiểm chứng Khoa học & Quản trị ESG-G` (Màu nhận diện: Xanh Thông `#047857`):**
   - Công khai toàn bộ bằng chứng thực nghiệm Giai đoạn 1–4 (`AUC = 0.9299`, `p = 5.77e-22`, `SHAP R² = 0.9964 / MAE = 0.85đ`, `OOT Spearman = 0.9983`, `RAG Hit@3 = 100%`, Backtest 12 Bluechip vs 12 DN Biến cố, đối sánh 6 chiều `B09-DN` và tam giác 3 nguồn `NVL 2025`), tác động **ESG – Trụ cột G** và lộ trình Phase 2.

---

## 3. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG & ĐO HIỆU NĂNG THỰC TẾ (BẢN V2-3)

Toàn bộ kết quả kiểm thử tự động lưu tại [`stage5_deployment_test_log.json`](../data_store/processed/stage5_deployment_test_log.json):

| Hạng mục Kiểm thử | Chỉ số đo thực tế | Kết quả |
| :--- | :--- | :---: |
| **Test 1A — Live Scoring 2 Công ty Mẫu (Upload Excel)** | `MINH_BACH 2025 = 6.35đ` (*Thấp — An toàn*) vs. `THOI_SO 2025 = 89.15đ` (*Cao — Cảnh báo Đỏ*) trong **`763.2 ms`** | PASS |
| **Test 1B — Đối chứng Tái lập `TDH 2025` (Live vs. GĐ 3)** | `Live = 80.16đ` vs. `Stage 3 = 80.16đ` -> **Chênh lệch tuyệt đối = `0.000đ`** | PASS |
| **Test 1C — Xuất Báo cáo A4 V2-3 (`report_exporter.py`)** | `11,752 bytes` (cơ bản) / `14,851 bytes` (đầy đủ RAG TDH) — có Logo SVG + V2 Fonts + Thanh điểm 0–100 + **`0` dấu `**` + `0` dấu `...`** | PASS |
| **Test 2A — Streamlit `AppTest` Khởi động lạnh (Cold Boot)** | Nạp toàn bộ dữ liệu + AI + SHAP + RAG + render Phân hệ 1 trong **`0.85 giây`** (`0` ngoại lệ) | PASS |
| **Test 2B — Render cả 5 Phân hệ, Quick-Demo & Chat Drawer** | Phân hệ 1: `0.22s` • Phân hệ 2: `0.36s` • Phân hệ 3: `0.07s` • Phân hệ 4 *(gồm lập chỉ mục PDF 91 tr)*: `6.48s` • Phân hệ 5: `0.09s` • Nhảy nhanh `NVL 2025`: `0.29s` • Mở Hộp thoại Chatbox nổi: **`0.52s`** (`0` ngoại lệ) | PASS |
| **Test 2C — Kiểm thử Mobile SHAP, 3D WebGL & Audit V2-3** | SHAP nằm ngang `orientation='h'` (nhãn `<= 28` ký tự), 3 biểu đồ 3D + toggle 2D/3D, 5 màu thư mục & hiệu ứng quét màu dần, khung tìm kiếm Game Jam, **`0` emoji hoạt hình**, **`0` dấu `...` trên giao diện** | PASS |
| **Test 3 — Khởi chạy thật `streamlit run` HTTP Server** | `/_stcore/health` & `/` trả về **`HTTP 200 OK`** sau **`0.9 giây`** | PASS |
| **Đo RAM Thực tế (Full-load cả 5 phân hệ + 3D + PDF 91 tr)** | **`481.6 MB`** (`< 1.6%` trên máy 32GB RAM & `< 50%` hạn mức 1GB của Streamlit Cloud) | PASS |

---

## 4. HƯỚNG DẪN KHỞI CHẠY NGAY & KIỂM TRA TRÊN DESKTOP / MOBILE

### A. Chạy trực tiếp trên máy cá nhân (Windows PowerShell — ổ `D:\SEHackathon`)
```powershell
$env:PYTHONIOENCODING="utf-8"
d:\SEHackathon\.venv\Scripts\streamlit.exe run d:\SEHackathon\stage_5_web_app_deployment\app.py
```
Mở trình duyệt tại **`http://localhost:8501`** (và bấm `F12` → chế độ Điện thoại `375×812` để kiểm chứng biểu đồ Thác nước SHAP nằm ngang, Khung tìm kiếm tương phản cao và Biểu tượng Chatbox nổi góc phải dưới).

### B. Triển khai miễn phí công khai trên Streamlit Community Cloud (Gắn QR / Link vào Báo cáo Dự thi)
1. Đẩy dự án lên GitHub (gồm `requirements.txt`, `stage_2_preprocessing_forensics/`, `stage_3_ai_modeling_validation/`, `stage_4_rag_legal_notes/`, `stage_5_web_app_deployment/`, `data_store/processed/`, `data_store/models/`, `data_store/sample_uploads/` — tổng dung lượng `< 35 MB`).
2. Truy cập [share.streamlit.io](https://share.streamlit.io/) → chọn **New app** → đặt **Main file path** là `stage_5_web_app_deployment/app.py` → bấm **Deploy**.
3. Nhờ chạy mặc định ở chế độ **Zero-API (`481.6 MB` RAM)**, ứng dụng vận hành ổn định 24/7 mà không lo hết quota API khi Ban Giám khảo truy cập đồng thời.
