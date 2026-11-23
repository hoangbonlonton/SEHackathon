# GIAI ĐOẠN 3: Huấn luyện AI Không giám sát, Giải thích SHAP & Kiểm chứng (`stage_3_ai_modeling_validation`)

## 1. Mục tiêu Giai đoạn 3
1. Huấn luyện mô hình **`Isolation Forest`** trên không gian 12 đặc trưng pháp chứng đã chuẩn hóa theo ngành ICB để phát hiện các tổ hợp bất thường đa chiều.
2. Tổng hợp điểm **`Composite Forensic Risk Score (0 - 100)`** và phân loại 3 mức độ rủi ro (`Thấp`, `Cần theo dõi`, `Cảnh báo Cao`).
3. Tích hợp **`SHAP TreeExplainer`** để giải thích đóng góp của từng chỉ số tài chính vào điểm rủi ro của mỗi doanh nghiệp và tự động sinh nhận định bằng ngôn ngữ kiểm toán tiếng Việt.
4. Thực hiện **4 Lớp Kiểm chứng Khoa học** (Kiểm thử toán học, Kiểm định hội tụ đa mô hình, Kiểm định độ ổn định tham số, và Đối chứng thực chứng trên nhóm doanh nghiệp thực tế) và xuất báo cáo [`REPORT_STAGE_3_MODEL_VALIDATION.md`](REPORT_STAGE_3_MODEL_VALIDATION.md).

## 2. Cấu trúc File trong Thư mục
- [`03_train_validate_model.py`](03_train_validate_model.py): Script huấn luyện `Isolation Forest`, tính giá trị `SHAP`, chạy 4 lớp kiểm chứng và lưu mô hình vào `../data_store/models/`.
- [`03_model_explainability_walkthrough.ipynb`](03_model_explainability_walkthrough.ipynb): Jupyter Notebook trực quan hóa SHAP Waterfall và ma trận kiểm chứng.
- [`REPORT_STAGE_3_MODEL_VALIDATION.md`](REPORT_STAGE_3_MODEL_VALIDATION.md): Báo cáo kết quả mô hình & các con số kiểm chứng minh bạch.
