# GIAI ĐOẠN 1: Thu thập & Kiểm định Dữ liệu Nguồn (`stage_1_data_acquisition`)

## 1. Mục tiêu Giai đoạn 1
1. Thu thập và chuẩn hóa bộ dữ liệu **Báo cáo Tài chính (`B01-DN`: Báo cáo tình hình tài chính / BCĐKT, `B02-DN`: KQKD, `B03-DN`: LCTT)** đa năm (**2018–2025**) theo chuẩn mực Kế toán Việt Nam (VAS — liên thông giữa **Thông tư 200/2014/TT-BTC** cho dữ liệu lịch sử 2018–2025 và **Thông tư 99/2025/TT-BTC** áp dụng từ 01/01/2026) cho **toàn bộ doanh nghiệp phi tài chính niêm yết trên 2 sàn chính thức HOSE và HNX**.
2. Loại bỏ minh bạch 3 ngành Định chế Tài chính (**Ngân hàng**, **Dịch vụ tài chính / Chứng khoán**, **Bảo hiểm**) theo chuẩn ngành **ICB cấp 2** để đảm bảo tính chính xác học thuật tuyệt đối khi tính Beneish M-Score và Altman $Z''$-Score ở Giai đoạn 2.
3. Thực hiện **5 Lớp Kiểm định Toàn vẹn Kế toán (Accounting Integrity Audit — Quality Gate 1)** trên 100% dòng dữ liệu và xuất báo cáo con số minh bạch [`REPORT_STAGE_1_DATA_AUDIT.md`](REPORT_STAGE_1_DATA_AUDIT.md).

## 2. Nguồn Dữ liệu Thực tế & Lưu ý Kỹ thuật
- **Nguồn chính thống:** **Vietcap IQ Insight API** (`https://iq.vietcap.com.vn/api/iq-insight-service/v1/`) — cung cấp đầy đủ danh mục ngành ICB và 3 bảng BCTC chuẩn VAS (`BALANCE_SHEET`, `INCOME_STATEMENT`, `CASH_FLOW`) 8 năm (2018–2025) cho toàn bộ doanh nghiệp niêm yết Việt Nam.
- **Lý do chuyển từ `vnstock 6.0.1` sang gọi trực tiếp Vietcap IQ API:** Qua kiểm thử thực tế ngày 23/11/2026, phiên bản `vnstock 6.0.1` đã chuyển route `fundamental.equity.balance_sheet` sang nguồn riêng yêu cầu API key trả phí (`FHSC_API_KEY`). Gọi trực tiếp Vietcap IQ Insight API qua `httpx` cho kết quả **100% dữ liệu thật, không cần khóa trả phí, tốc độ cao và khớp phương trình kế toán >99%**.

## 3. Cấu trúc File trong Thư mục
- [`01_data_acquisition.py`](01_data_acquisition.py): Script thu thập đa luồng (6 workers, retry + exponential backoff), chuẩn hóa dấu kế toán cho 35 chỉ tiêu VAS, kiểm định 5 lớp toàn vẹn và xuất báo cáo tự động.
- [`01_data_acquisition_walkthrough.ipynb`](01_data_acquisition_walkthrough.ipynb): Jupyter Notebook trực quan hóa phễu chọn mẫu, kiểm chứng đẳng thức kế toán và vẽ biểu đồ phân bố dữ liệu theo 16 ngành ICB & chuỗi thời gian (`stage1_data_overview.png`).
- [`REPORT_STAGE_1_DATA_AUDIT.md`](REPORT_STAGE_1_DATA_AUDIT.md): Báo cáo chi tiết quy trình từng bước, con số thực tế 100%, phân tích kết quả và các lưu ý bắt buộc cho Giai đoạn 2.

## 4. Cách Chạy & Tự Kiểm Chứng
```powershell
d:\SEHackathon\.venv\Scripts\python.exe stage_1_data_acquisition\01_data_acquisition.py
```
Sau khi chạy xong, kiểm tra:
- Dữ liệu gốc chuẩn hóa: `data_store/raw/vas_financial_statements_raw.parquet` và `.csv`
- Nhật ký thu thập: `data_store/raw/stage1_acquisition_log.json`
- Báo cáo kiểm định chi tiết: [`REPORT_STAGE_1_DATA_AUDIT.md`](REPORT_STAGE_1_DATA_AUDIT.md)
