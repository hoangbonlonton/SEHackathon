# FinAudit AI — FinForensics
**Nền tảng AI Sàng lọc Rủi ro Chất lượng Lợi nhuận, Pháp chứng Báo cáo Tài chính & Thúc đẩy Minh bạch Quản trị (ESG-G)**  
*Dự án tham dự Cuộc thi “Sáng tạo – Khởi nghiệp vì tương lai bền vững – SE-Hackathon Challenge 2026” (Trường Kinh tế – Đại học Công nghiệp Hà Nội)*

---

## 1. Kiến trúc Quy trình 5 Giai đoạn Khoa học

Dự án được tổ chức thành **5 giai đoạn độc lập, tuần tự và có cổng kiểm chứng minh bạch**:

| Giai đoạn | Thư mục | Nội dung chính | Báo cáo kiểm chứng |
| :--- | :--- | :--- | :--- |
| **Giai đoạn 1** | [`stage_1_data_acquisition/`](stage_1_data_acquisition/) | Thu thập BCTC chuẩn VAS (2018–2025) toàn bộ doanh nghiệp phi tài chính niêm yết HOSE & HNX qua Vietcap IQ API & Kiểm định 5 lớp toàn vẹn kế toán | [`REPORT_STAGE_1_DATA_AUDIT.md`](stage_1_data_acquisition/REPORT_STAGE_1_DATA_AUDIT.md) |
| **Giai đoạn 2** | [`stage_2_preprocessing_forensics/`](stage_2_preprocessing_forensics/) | Làm sạch dữ liệu, tính toán xác định 15 chỉ số pháp chứng (Beneish 8 biến, Altman $Z''$, CFO/NI, SRR) & Chuẩn hóa Robust Z-Score theo ngành ICB | [`REPORT_STAGE_2_FORENSIC_METRICS.md`](stage_2_preprocessing_forensics/REPORT_STAGE_2_FORENSIC_METRICS.md) |
| **Giai đoạn 3** | [`stage_3_ai_modeling_validation/`](stage_3_ai_modeling_validation/) | Huấn luyện `Isolation Forest`, tính điểm `Composite Forensic Risk Score (0-100)`, giải thích mô hình bằng `SHAP TreeExplainer` & Chạy 4 lớp kiểm chứng | [`REPORT_STAGE_3_MODEL_VALIDATION.md`](stage_3_ai_modeling_validation/REPORT_STAGE_3_MODEL_VALIDATION.md) |
| **Giai đoạn 4** | [`stage_4_rag_legal_notes/`](stage_4_rag_legal_notes/) | Xây dựng kho văn bản pháp lý (`VSA 240`, `TT 99/2025/TT-BTC` thay thế `TT 200/2014/TT-BTC`, `TT 48/2019/TT-BTC`), đọc PDF Thuyết minh BCTC (`B09-DN`) & Truy xuất lai `Hybrid RRF (BM25 + Semantic TF-IDF)` | [`REPORT_STAGE_4_RAG_BENCHMARK.md`](stage_4_rag_legal_notes/REPORT_STAGE_4_RAG_BENCHMARK.md) |
| **Giai đoạn 5** | [`stage_5_web_app_deployment/`](stage_5_web_app_deployment/) | Ứng dụng Web `Streamlit` giao diện FinTech SaaS chuyên nghiệp (5 phân hệ chức năng + xuất báo cáo kiểm toán HTML/CSV) | [`REPORT_STAGE_5_SYSTEM_DEPLOYMENT.md`](stage_5_web_app_deployment/REPORT_STAGE_5_SYSTEM_DEPLOYMENT.md) |

---

## 2. Tài liệu Tri thức & Thiết kế Hệ thống

1. **Báo cáo Tri thức Toàn diện (Từ Cơ bản đến Nâng cao):** [`01_Bao_Cao_Kien_Thuc_Tu_Co_Ban_Den_Nang_Cao_FinAudit_AI.md`](01_Bao_Cao_Kien_Thuc_Tu_Co_Ban_Den_Nang_Cao_FinAudit_AI.md)
2. **Thiết kế Quy trình 5 Giai đoạn & Kiến trúc Hệ thống Web:** [`02_Thiet_Ke_Quy_Trinh_Va_Kien_Truc_He_Thong_FinAudit_AI.md`](02_Thiet_Ke_Quy_Trinh_Va_Kien_Truc_He_Thong_FinAudit_AI.md)

---

## 3. Hướng dẫn Chạy Nhanh Toàn Bộ Hệ Thống

### Bước 1: Cài đặt thư viện
```powershell
pip install -r requirements.txt
```

### Bước 2: Chạy tuần tự 4 giai đoạn xử lý dữ liệu, mô hình AI & RAG
```powershell
python stage_1_data_acquisition/01_data_acquisition.py
python stage_2_preprocessing_forensics/02_forensic_features.py
python stage_3_ai_modeling_validation/03_train_validate_model.py
python stage_4_rag_legal_notes/04_hybrid_rag_engine.py
```
*(Hoặc mở các file `.ipynb` tương ứng trong từng thư mục để chạy từng ô lệnh trên Jupyter Notebook).*

### Bước 3: Khởi động Ứng dụng Web `FinAudit AI`
```powershell
streamlit run stage_5_web_app_deployment/app.py
```
