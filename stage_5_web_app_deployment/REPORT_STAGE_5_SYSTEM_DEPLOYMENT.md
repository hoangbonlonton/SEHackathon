# BÁO CÁO NGHIỆM THU GIAI ĐOẠN 5: TRIỂN KHAI HỆ THỐNG WEB APP STREAMLIT CHUẨN FINTECH SAAS (`stage_5_web_app_deployment`)

> **Thời điểm nghiệm thu:** `2026-11-24`  
> **Trạng thái kiểm thử tự động:** **3 / 3 Bộ kiểm thử PASSED (`0` ngoại lệ trên cả 5 phân hệ, `HTTP 200 OK`, tái lập điểm Live Scoring sai số `0.000đ`)**  
> **Tài nguyên đo thực tế (Full-load cả 643 DN + AI + SHAP + RAG + PDF 91 trang):** **`410.5 MB` RAM** (`1.28%` trên máy 32GB RAM — dư giả để triển khai miễn phí trên Streamlit Community Cloud `1 GB RAM`)

---

## 1. KIẾN TRÚC ỨNG DỤNG & HỆ THỐNG THIẾT KẾ GIAO DIỆN (FINTECH DESIGN SYSTEM)

Toàn bộ ứng dụng Web được tổ chức gọn gàng thành 4 module tách biệt trong [`stage_5_web_app_deployment/`](.) theo chuẩn sản phẩm phần mềm thương mại:

| File / Thành phần | Vai trò kỹ thuật | Lý do thiết kế |
| :--- | :--- | :--- |
| [`.streamlit/config.toml`](.streamlit/config.toml) | Cấu hình theme Enterprise Light & giới hạn upload 30 MB | Đồng bộ ngay từ lúc tải trang, tránh giật màu nền khi khởi động. |
| [`ui_components.py`](ui_components.py) | CSS Design System hài hòa + 7 hàm vẽ biểu đồ tương tác Plotly | Tách riêng tầng giao diện giúp code sạch, giữ nhất quán bảng màu **Slate Navy (`#0F172A`) → Royal Blue (`#1E3A8A`)**, nền **Alabaster (`#F8FAFC`)**, thẻ trắng (`#FFFFFF`) và 3 màu ngữ nghĩa **Emerald (`#059669`) / Amber (`#D97706`) / Crimson (`#DC2626`)**. |
| [`live_scoring_service.py`](live_scoring_service.py) | Cầu nối **Live Scoring** & tạo file mẫu Excel/CSV (`Mau_Upload_BCTC_FinAudit_AI.xlsx`) | Tái sử dụng 100% logic gốc của Giai đoạn 2 (`02_forensic_features.py`) & Giai đoạn 3 (`03_train_validate_model.py`), bảo đảm điểm chấm trực tiếp **khớp tuyệt đối `0.000đ`** với điểm đã huấn luyện. |
| [`report_exporter.py`](report_exporter.py) | Xuất **Báo cáo Hồ sơ Kiểm toán Pháp chứng chuẩn A4 (`.html` In PDF)** | Giúp kiểm toán viên, cán bộ tín dụng và Ban Giám khảo tải về in PDF đẹp ngay trên trình duyệt mà không cần cài thư viện nặng. |
| [`app.py`](app.py) | Ứng dụng Streamlit chính điều phối **5 Phân hệ chức năng** | Áp dụng `@st.cache_data` (nạp bảng `.parquet`/`.json` vào RAM) và `@st.cache_resource` (nạp mô hình AI `.joblib`, Hybrid RAG và chỉ mục PDF 1 lần duy nhất) giúp chuyển trang tức thì trong **`0.04s – 0.23s`**. |

---

## 2. CHI TIẾT 5 PHÂN HỆ CHỨC NĂNG ĐÃ HOÀN THIỆN & KẾT NỐI DỮ LIỆU THẬT

1. **Phân hệ 1 — `Tổng quan Thị trường & Quét Rủi ro Ngành ICB`:**
   - Lọc đa chiều theo *Năm (`2019–2025`)*, *15 Ngành ICB*, *Hạng Rủi ro*, *Sàn HOSE/HNX* và *Tìm nhanh mã/tên*.
   - Hiển thị 4 thẻ KPI lớn, **Ma trận Pháp chứng 2D (`Beneish M` vs. `Altman Z''`)**, **Biểu đồ xếp hạng 15 Ngành ICB**, Bảng Screener có thanh tiến trình điểm rủi ro, nút **Mở nhanh Hồ sơ 360°** và xuất **`.CSV`**.
2. **Phân hệ 2 — `Hồ sơ Pháp chứng Doanh nghiệp 360° & SHAP`:**
   - Chọn bất kỳ mã nào trong `643` doanh nghiệp (hoặc bấm 6 phím tắt Demo nhanh ở Sidebar: `TDH`, `QCG`, `NVL`, `DRH`, `FPT`, `VNM`).
   - Hiển thị Banner Định danh, Đồng hồ **Gauge (`0–100`)**, **4 Thẻ Trụ cột**, **Biểu đồ Thác nước SHAP**, **Biểu đồ Radar đối sánh chuẩn ngành**, **Xu hướng Doanh thu–LNST–CFO & Quỹ đạo Rủi ro 8 năm (`2018–2025`)**.
   - Tự động kích hoạt cầu nối **`SHAP → Hybrid RAG`**: trích dẫn điều luật (`VSA 240`, `TT 99/2025`, `TT 200/2014`, `TT 48/2019`, `VAS 14/26`), bóc tách `B09-DN` (nếu thuộc 38 DN trọng điểm) và trích trang `PDF` kiểm toán thật (VD: `NVL 2025` trích **Trang 12 — Moore AISC nhấn mạnh hoạt động liên tục**), kèm nút **Xuất Báo cáo Kiểm toán `.HTML` chuẩn A4** & **`.CSV`**.
3. **Phân hệ 3 — `Phòng Thẩm định BCTC Mới (Upload & What-If Live Scoring)`:**
   - Cho phép tải file mẫu Excel/CSV ([Mau_Upload_BCTC_FinAudit_AI.xlsx](../data_store/sample_uploads/Mau_Upload_BCTC_FinAudit_AI.xlsx)) và upload file BCTC mới 2 năm của bất kỳ doanh nghiệp nào, hoặc dùng **What-If Simulator** chỉnh sửa trực tiếp từng chỉ số trên bảng `st.data_editor`.
   - Chạy nối tiếp thời gian thực (`~0.73 giây`): **Trạm 0 (Data Integrity Gate)** → **Chuyên gia 1** → **Chuyên gia 2 (AI + SHAP)** → **Chuyên gia 3 (RAG)** + xuất báo cáo HTML ngay lập tức.
4. **Phân hệ 4 — `Trợ lý AI Soi Thuyết minh PDF & Tra cứu Pháp lý VAS`:**
   - *Tab Pháp lý:* Truy vấn tức thì (`~1.56 ms`) kho 5 văn bản pháp lý bằng **Hybrid RRF**, có 6 câu hỏi mẫu 1-click (kèm câu test **Chống Ảo giác**), cho phép so sánh 4 thuật toán (`Hybrid RRF` vs `BM25 Dual` vs `TF-IDF` vs `BM25 Raw`) và hỗ trợ tùy chọn nhập **Gemini API Key** (mặc định chạy 100% Zero-API).
   - *Tab Soi PDF:* Cho chọn ngay 4 bộ PDF Kiểm toán 2025 thật (`NVL`, `TDH`, `FPT`, `VNM`) hoặc upload file `.pdf` bất kỳ → chẩn đoán chất lượng 3 tầng (`NATIVE_TEXT_CLEAN` / `NOISY_OCR_TEXT` / `SCANNED_IMAGE_PDF`). Với PDF scan ảnh (`FPT, VNM, TDH 2025`), tự động cảnh báo và mở bảng **B09-DN cấu trúc (Kênh 1)** thay thế.
5. **Phân hệ 5 — `Trung tâm Kiểm chứng Khoa học & Quản trị ESG-G`:**
   - Trình bày trực quan toàn bộ kết quả thực nghiệm Giai đoạn 1–4 (`AUC = 0.9299`, `p = 5.77e-22`, `SHAP R² = 0.9964 / MAE = 0.85đ`, `OOT Spearman = 0.9983`, `RAG Hit@3 = 100%`, bảng Backtest 12 Bluechip vs 12 DN Biến cố, bảng đối sánh 6 chiều `B09-DN` và tam giác 3 nguồn `NVL 2025`), tác động **ESG – Trụ cột G** và lộ trình Phase 2.

---

## 3. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG & ĐO HIỆU NĂNG THỰC TẾ (`test_stage5_app.py`)

Toàn bộ kết quả kiểm thử tự động lưu tại [`stage5_deployment_test_log.json`](../data_store/processed/stage5_deployment_test_log.json):

| Hạng mục Kiểm thử | Chỉ số đo thực tế | Kết quả |
| :--- | :--- | :---: |
| **Test 1A — Live Scoring 2 Công ty Mẫu (Upload Excel)** | `MINH_BACH 2025 = 6.35đ` (*Thấp — An toàn*) vs. `THOI_SO 2025 = 89.15đ` (*Cao — Cảnh báo Đỏ*) trong **`703.0 ms`** | ✅ **PASS** |
| **Test 1B — Đối chứng Tái lập `TDH 2025` (Live vs. GĐ 3)** | `Live = 80.16đ` vs. `Stage 3 = 80.16đ` $\rightarrow$ **Chênh lệch tuyệt đối = `0.000đ`** | ✅ **PASS** |
| **Test 1C — Xuất Báo cáo Hồ sơ Kiểm toán A4 (`.HTML`)** | Sinh thành công `8,126 bytes` UTF-8 hợp lệ, đầy đủ 4 trụ cột, bảng SHAP & khuyến cáo VSA 240 | ✅ **PASS** |
| **Test 2A — Streamlit `AppTest` Khởi động lạnh (Cold Boot)** | Nạp toàn bộ dữ liệu + mô hình AI + RAG + render Phân hệ 1 trong **`0.82 giây`** (`0` lỗi) | ✅ **PASS** |
| **Test 2B — Render cả 5 Phân hệ & Quick-Demo `NVL 2025`** | Phân hệ 1: `0.19s` • Phân hệ 2: `0.21s` • Phân hệ 3: `0.11s` • Phân hệ 4 *(gồm lập chỉ mục PDF 91 tr lần đầu)*: `6.12s` • Phân hệ 5: `0.04s` • Nhảy nhanh `NVL 2025` *(đã cache)*: **`0.05s`** (`0` lỗi trên toàn bộ 5/5 trang) | ✅ **PASS** |
| **Test 3 — Khởi chạy thật `streamlit run` HTTP Server** | `/_stcore/health` & `/` trả về **`HTTP 200 OK`** sau **`0.93 giây`** | ✅ **PASS** |
| **Đo RAM Thực tế (Full-load cả 5 phân hệ + PDF 91 tr)** | **`410.5 MB`** *(ứng dụng độc lập)* / **`492.6 MB`** *(đỉnh trong phiên chạy gộp test)* — `< 1.6%` trên máy 32GB RAM & `< 50%` hạn mức 1GB của Streamlit Cloud | ✅ **PASS** |

---

## 4. HƯỚNG DẪN KHỞI CHẠY NGAY & TRIỂN KHAI PUBLIC CHO BAN GIÁM KHẢO

### A. Chạy trực tiếp trên máy cá nhân (Windows PowerShell — ổ `D:\SEHackathon`)
```powershell
$env:PYTHONIOENCODING="utf-8"
d:\SEHackathon\.venv\Scripts\streamlit.exe run d:\SEHackathon\stage_5_web_app_deployment\app.py
```
Mở trình duyệt tại **`http://localhost:8501`** để trải nghiệm đầy đủ 5 phân hệ!

### B. Triển khai miễn phí công khai trên Streamlit Community Cloud (Gắn QR / Link vào Báo cáo Dự thi)
1. Tạo repository trên GitHub và đẩy dự án lên (gồm `requirements.txt`, `stage_2_preprocessing_forensics/`, `stage_3_ai_modeling_validation/`, `stage_4_rag_legal_notes/`, `stage_5_web_app_deployment/`, `data_store/processed/`, `data_store/models/`, `data_store/sample_uploads/` — tổng dung lượng gọn nhẹ `< 35 MB`).
2. Truy cập [share.streamlit.io](https://share.streamlit.io/) → chọn **New app** → chọn repo & nhánh `main` → đặt **Main file path** là `stage_5_web_app_deployment/app.py` → bấm **Deploy**.
3. Do Web chạy mặc định ở chế độ **Zero-API (`410.5 MB` RAM)**, ứng dụng khởi chạy ổn định 24/7 mà không lo hết quota API hay quá tải RAM khi Ban Giám khảo truy cập đồng thời!
