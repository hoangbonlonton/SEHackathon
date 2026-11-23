# GIAI ĐOẠN 3: Huấn luyện AI Không giám sát (`Isolation Forest`), Giải thích `SHAP` & 4 Lớp Kiểm chứng (`stage_3_ai_modeling_validation`)

## 1. Mục tiêu Giai đoạn 3
1. Chuyển đổi 12 đặc trưng chuẩn hóa ngành ICB sang **Không gian Rủi ro Một Phía (`One-Sided Risk Space`)** để chống báo động giả trên doanh nghiệp "siêu khỏe".
2. Huấn luyện mô hình **`Isolation Forest`** (`n_estimators=300`, `max_samples=256`, `contamination=0.10`, `random_state=42`) trên toàn bộ `4,340` quan sát `firm-year` (`2019–2025`).
3. Tổng hợp điểm **`Composite Forensic Risk Score (0 – 100)`** từ 4 trụ cột minh bạch: `0.30*Beneish + 0.25*Altman Z'' + 0.20*CashQuality + 0.25*IsoForest`.
4. Tích hợp **`SHAP TreeExplainer`** (tính cả trực tiếp trên `IsolationForest` và quy đổi chính xác sang đơn vị điểm `0–100`) + tự động sinh câu giải trình tiếng Việt kiểm toán.
5. Thực thi **4 Lớp Kiểm chứng Khoa học** (Độ trung thực SHAP, Hội tụ đa mô hình, Độ ổn định tham số + Out-of-Time `2019–2023 -> 2024–2025`, và Đối chứng thực chứng 12 Bluechip vs 12 DN Biến cố) và xuất báo cáo kèm bảng chú thích ký hiệu dễ hiểu [`REPORT_STAGE_3_MODEL_VALIDATION.md`](REPORT_STAGE_3_MODEL_VALIDATION.md).

## 2. Cấu trúc File trong Thư mục
- [`03_train_validate_model.py`](03_train_validate_model.py): Script huấn luyện, chấm điểm, chạy SHAP & 4 lớp kiểm chứng (có hàm `score_new_observations()` tái sử dụng trực tiếp cho Web App GĐ 5).
- [`03_model_explainability_walkthrough.ipynb`](03_model_explainability_walkthrough.ipynb): Jupyter Notebook theo dõi bảng SHAP và kết quả đối chứng.
- [`stage3_validation_dashboard.png`](stage3_validation_dashboard.png): Biểu đồ 4 khung kiểm chứng mô hình & giải thích SHAP.
- [`REPORT_STAGE_3_MODEL_VALIDATION.md`](REPORT_STAGE_3_MODEL_VALIDATION.md): Báo cáo đầy đủ kết quả, phân tích và bảng chú thích ký hiệu/thuật ngữ đơn giản cho người mới.

## 3. Cách Chạy & Tự Kiểm Chứng
```powershell
d:\SEHackathon\.venv\Scripts\python.exe stage_3_ai_modeling_validation\03_train_validate_model.py
```
