# GIAI ĐOẠN 4: Động cơ Hybrid RAG Pháp lý VAS & Soi Thuyết minh BCTC (`stage_4_rag_legal_notes`)

## 1. Mục tiêu Giai đoạn 4
1. Xây dựng kho văn bản chuẩn mực kế toán – kiểm toán Việt Nam (`legal_corpus/`) gồm **VSA 240**, **Thông tư 99/2025/TT-BTC** (thay thế **Thông tư 200/2014/TT-BTC** từ 01/01/2026 — căn cứ lập & trình bày BCTC cũng như trích lập dự phòng trên BCTC), **Thông tư 48/2019/TT-BTC (và TT 24/2022/TT-BTC)** (căn cứ xác định chi phí dự phòng được trừ khi tính thuế TNDN & khung tham chiếu tuổi nợ), **VAS 26** và **Sổ tay Thủ tục Kiểm toán Pháp chứng**.
2. Xây dựng bộ đọc **PDF Thuyết minh BCTC** (có kiểm tra mật độ ký tự để nhận diện PDF scan) và chia đoạn bảo toàn số trang/điều khoản.
3. Triển khai động cơ tìm kiếm lai **`Hybrid RRF Retriever` (`Okapi BM25` + `TF-IDF Semantic N-gram` + `Reciprocal Rank Fusion`)** giúp đối chiếu tự động các chỉ số bị gắn cờ đỏ (Red Flags) với quy định pháp lý và thuyết minh BCTC.
4. Đánh giá độ chính xác truy xuất trên bộ 20 câu hỏi tình huống kiểm toán chuẩn và xuất báo cáo [`REPORT_STAGE_4_RAG_BENCHMARK.md`](REPORT_STAGE_4_RAG_BENCHMARK.md).

## 2. Cấu trúc File trong Thư mục
- [`04_hybrid_rag_engine.py`](04_hybrid_rag_engine.py): Module xây dựng kho văn bản, đọc PDF, truy xuất Hybrid RRF và đánh giá benchmark.
- [`04_rag_evaluation_walkthrough.ipynb`](04_rag_evaluation_walkthrough.ipynb): Jupyter Notebook thử nghiệm truy vấn pháp lý & soi Thuyết minh BCTC.
- [`legal_corpus/`](legal_corpus/): Thư mục chứa các tài liệu chuẩn mực có cấu trúc Điều/Khoản.
- [`REPORT_STAGE_4_RAG_BENCHMARK.md`](REPORT_STAGE_4_RAG_BENCHMARK.md): Báo cáo đánh giá `Hit Rate@1`, `Hit Rate@3`, `MRR` và `Citation Accuracy`.
