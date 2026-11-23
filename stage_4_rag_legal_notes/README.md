# GIAI ĐOẠN 4: Động cơ Hybrid RAG Pháp lý VAS & Soi Thuyết minh BCTC (`stage_4_rag_legal_notes`)

## 1. Mục tiêu & Kiến trúc 2 Kênh Thực tế
1. **Kho Văn bản Pháp lý Chuẩn hóa (`legal_corpus/` — 5 văn bản, 24 đoạn Section-Aware):**
   - [`01_VSA_240_TT214_2012.md`](legal_corpus/01_VSA_240_TT214_2012.md): VSA 240 (TT 214/2012/TT-BTC — Đoạn 04–06, 12–14, 26 & A28–A30, 31–33, Phụ lục 1).
   - [`02_TT99_2025_TT200_2014_CheDoKeToan.md`](legal_corpus/02_TT99_2025_TT200_2014_CheDoKeToan.md): Thông tư 99/2025/TT-BTC (hiệu lực 01/01/2026 — Điều 17, 18, 31, Phụ lục II & IV) liên thông với Thông tư 200/2014/TT-BTC (niên độ đến hết 31/12/2025 — Điều 18, 20, 21, 22, 45, 46, 51, 79).
   - [`03_TT48_2019_TT24_2022_DuPhong.md`](legal_corpus/03_TT48_2019_TT24_2022_DuPhong.md): Thông tư 48/2019/TT-BTC & TT 24/2022/TT-BTC (Khoản 1 Điều 1 ranh giới dự phòng Thuế TNDN vs BCTC, Điều 4 dự phòng HTK theo NRV, Điều 6 khung tuổi nợ 30%–50%–70%–100%).
   - [`04_VAS_14_DoanhThu_Va_VAS_26_BenLienQuan.md`](legal_corpus/04_VAS_14_DoanhThu_Va_VAS_26_BenLienQuan.md): VAS 14 (QĐ 149/2001 — Đoạn 10 & 16) và VAS 26 (QĐ 234/2003 — Thuyết minh bên liên quan).
   - [`05_Forensic_Audit_Playbook_FinAudit.md`](legal_corpus/05_Forensic_Audit_Playbook_FinAudit.md): Sổ tay Thủ tục Kiểm toán Pháp chứng ánh xạ 12 chỉ số `SHAP` từ Giai đoạn 3 sang khoản mục `B09-DN` & pháp lý tương ứng.
2. **Dữ liệu Thuyết minh BCTC Thật — Kiến trúc 2 Kênh Chống Mù Scan PDF:**
   - **Kênh 1 (Có cấu trúc):** Thu thập trực tiếp `B09-DN` (`section=NOTE`, 166 chỉ tiêu `noc*`) từ **Vietcap IQ Insight API** cho **38 doanh nghiệp trọng điểm** (12 Bluechip Nhóm A + 12 Biến cố Nhóm B + Top-15 Rủi ro 2025), chuẩn hóa sang Tỷ VND và đối sánh chéo 6 chiều với `B01-DN`.
   - **Kênh 2 (Phi cấu trúc — PDF BCTC Kiểm toán thật):** Kiểm định 4 bộ PDF Kiểm toán 2025 công khai từ **Vietstock / HOSE** (`VNM`, `FPT`, `TDH`, `NVL`) + 1 PDF chuẩn tiếng Việt đối chứng bằng **Bộ chẩn đoán 3 tầng** (`NATIVE_TEXT_CLEAN`, `NOISY_OCR_TEXT`, `SCANNED_IMAGE_PDF`).
3. **Động cơ Tìm kiếm Lai `Hybrid RRF Retriever` (Thuần cục bộ, 0 API bắt buộc):**
   - Kết hợp **`Okapi BM25` song dấu tiếng Việt (lọc từ hư)** + **`TF-IDF Word (1,2) + Char_WB (3,5)` (`max_df=0.85`)** qua **Weighted Reciprocal Rank Fusion (`k=30`)** kèm **Cổng Chống Ảo giác (`Anti-Hallucination Abstention Gate`)**.
   - Cầu nối tự động **`SHAP -> Hybrid RAG -> B09-DN / PDF`** phục vụ trực tiếp Web App Giai đoạn 5.

## 2. Cấu trúc File & Đầu ra
- [`04_hybrid_rag_engine.py`](04_hybrid_rag_engine.py): Module động cơ Hybrid RAG, đọc/chẩn đoán PDF, thu thập & đối sánh B09-DN và chạy kiểm chuẩn.
- [`04_rag_evaluation_walkthrough.ipynb`](04_rag_evaluation_walkthrough.ipynb): Jupyter Notebook tương tác kiểm thử truy vấn pháp lý & soi B09-DN/PDF.
- [`stage4_rag_benchmark.png`](stage4_rag_benchmark.png): Bảng điều khiển trực quan 4 biểu đồ kiểm chứng Giai đoạn 4.
- [`REPORT_STAGE_4_RAG_BENCHMARK.md`](REPORT_STAGE_4_RAG_BENCHMARK.md): Báo cáo quy trình, nguồn dữ liệu, kiểm định đối sánh, phân tích kết quả và bảng chú thích thuật ngữ dễ hiểu.
- Dữ liệu đầu ra lưu tại `data_store/processed/`:
  - `real_b09_notes_structured.parquet` & `.csv` (289 dòng × 166 chỉ tiêu `noc*`, đơn vị Tỷ VND)
  - `b09_note_schema_catalog.json` (Danh mục nhãn tiếng Việt & tiếng Anh của 157 chỉ tiêu `NOTE`)
  - `stage4_rag_benchmark_summary.json` (Toàn bộ số liệu kiểm định & 5 hồ sơ Case Studies)
