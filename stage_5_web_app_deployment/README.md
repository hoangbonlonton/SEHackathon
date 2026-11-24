# GIAI ĐOẠN 5: Hệ thống Web App Streamlit Chuẩn FinTech SaaS (`stage_5_web_app_deployment`)

## 1. Kiến trúc & Các File trong Thư mục
- [`app.py`](app.py): Ứng dụng Web chính tích hợp **5 Phân hệ chức năng** chuẩn FinTech SaaS (`@st.cache_data` & `@st.cache_resource`).
- [`ui_components.py`](ui_components.py): Hệ thống thiết kế CSS FinTech hài hòa (`Slate Navy #0F172A` → `Royal Blue #1E3A8A`, `Alabaster #F8FAFC`, `Emerald #059669`, `Amber #D97706`, `Crimson #DC2626`) và thư viện **7 biểu đồ tương tác Plotly** (Ma trận Pháp chứng 2D, Xếp hạng 15 Ngành ICB, Đồng hồ Gauge, Thác nước SHAP, Radar ngành, Xu hướng đa năm, Kiểm chứng AUC/RAG).
- [`live_scoring_service.py`](live_scoring_service.py): Cầu nối chấm điểm trực tiếp (*Upload CSV/Excel* & *What-If Simulator*) nối tuần tự `Trạm 0 (Data Integrity Gate) → GĐ 2 (Beneish/Altman/Peer Robust Z) → GĐ 3 (Isolation Forest + SHAP)` và tạo sẵn file mẫu `Mau_Upload_BCTC_FinAudit_AI.xlsx` & `.csv` tại `data_store/sample_uploads/`.
- [`report_exporter.py`](report_exporter.py): Bộ xuất **Báo cáo Hồ sơ Kiểm toán Pháp chứng chuẩn A4 (`.html` In ra PDF)** kèm đầy đủ 4 trụ cột, giải trình SHAP, trích dẫn luật & khuyến cáo VSA 240.
- [`test_stage5_app.py`](test_stage5_app.py): Bộ kiểm thử tự động 3 lớp (*Live Scoring & Đối chứng tái lập 0.0đ* + *Streamlit AppTest qua cả 5 phân hệ* + *Khởi chạy Live HTTP Server & đo RAM*).
- [`.streamlit/config.toml`](.streamlit/config.toml): Cấu hình theme Enterprise Light & giới hạn upload 30 MB.
- [`REPORT_STAGE_5_SYSTEM_DEPLOYMENT.md`](REPORT_STAGE_5_SYSTEM_DEPLOYMENT.md): Báo cáo nghiệm thu, thông số hiệu năng thực tế & hướng dẫn triển khai.

## 2. Cách Khởi chạy Cục bộ (Local trên ổ `D:\SEHackathon`)
Mở PowerShell tại thư mục `D:\SEHackathon` và chạy:
```powershell
$env:PYTHONIOENCODING="utf-8"
d:\SEHackathon\.venv\Scripts\streamlit.exe run d:\SEHackathon\stage_5_web_app_deployment\app.py
```
Trình duyệt sẽ mở tự động tại `http://localhost:8501`.

## 3. Cách Triển khai Public lên Streamlit Community Cloud (Miễn phí)
1. Đẩy toàn bộ dự án lên GitHub repository (giữ nguyên `requirements.txt`, `stage_2..5`, `data_store/processed/`, `data_store/models/`, `data_store/sample_uploads/`).
2. Đăng nhập [share.streamlit.io](https://share.streamlit.io/) → chọn **New app** → trỏ **Main file path** vào `stage_5_web_app_deployment/app.py`.
3. **Không bắt buộc cấu hình API Key** (Web chạy mặc định 100% chế độ *Zero-API Grounded RAG*). Nếu muốn dùng thêm Gemini tóm tắt mở rộng, chỉ cần nhập key trực tiếp trong ô tùy chọn ở Sidebar.
