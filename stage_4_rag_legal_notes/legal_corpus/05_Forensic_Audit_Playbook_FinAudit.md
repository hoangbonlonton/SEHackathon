# Sổ tay Thủ tục Kiểm toán Pháp chứng FinAudit AI (Ánh xạ 12 Chỉ số SHAP sang Thuyết minh B09-DN & Pháp lý)
- **Tên tài liệu:** FinAudit AI Forensic Audit Playbook v2.0
- **Mục đích:** Kết nối tự động giữa kết quả giải thích AI (12 chỉ số `SHAP` ở Giai đoạn 3) với khoản mục Thuyết minh BCTC (`B09-DN`) cần kiểm tra và căn cứ pháp lý Việt Nam tương ứng (`VSA 240`, `TT 99/2025`, `TT 200/2014`, `TT 48/2019`, `VAS 14`, `VAS 26`).

## Playbook DSRI & AR/Revenue: Rủi ro Phải thu khách hàng tăng nhanh hơn Doanh thu (TK 131)
- **Chỉ số kích hoạt:** `DSRI` (Days Sales in Receivables Index > 1.031 / ngưỡng báo động 1.465) và `AR/Revenue` (Phải thu khách hàng / Doanh thu thuần tăng mạnh so với trung vị ngành ICB).
- **Ý nghĩa pháp chứng:** Doanh thu tăng trên sổ sách nhưng tiền không về tài khoản ngân hàng, tiềm ẩn rủi ro nới lỏng chính sách tín dụng quá mức, ghi nhận doanh thu trước kỳ (*cutoff*), bán hàng ảo (*channel stuffing*), hoặc khách hàng mất khả năng thanh toán nhưng chưa trích dự phòng.
- **Khoản mục B09-DN bắt buộc soi chiếu:** Thuyết minh chi tiết *Phải thu ngắn hạn của khách hàng (TK 131)* theo từng khách hàng lớn (>10%), bảng *Nợ xấu và phân tích tuổi nợ quá hạn*, chi tiết *Dự phòng phải thu khó đòi (TK 2293)*, chi tiết *Hàng bán bị trả lại (TK 5212)* và *Giao dịch bên liên quan*.
- **Căn cứ pháp lý liên kết:** VSA 240 Đoạn 26 (giả định rủi ro gian lận doanh thu), VAS 14 Đoạn 10 (5 điều kiện ghi nhận doanh thu), TT 200/2014 Điều 18 (TK 131) & Điều 45 (TK 2293) / TT 99/2025, TT 48/2019 Điều 6 (khung trích lập 30%-50%-70%-100% theo tuổi nợ cho mục đích thuế & tham chiếu).

## Playbook SRR: Rủi ro Phải thu khác, Trả trước cho người bán & Tài sản mềm (TK 138, 331, 141)
- **Chỉ số kích hoạt:** `SRR` — *Soft Receivables Ratio* = `(Phải thu ngắn hạn khác + Phải thu dài hạn khác + Trả trước cho người bán ngắn hạn) / Tổng tài sản` tăng cao bất thường so với ngành ICB.
- **Ý nghĩa pháp chứng:** Đây là "vùng xám" đặc thù của doanh nghiệp niêm yết Việt Nam (đặc biệt ngành Bất động sản và Xây dựng). Tiền rời khỏi doanh nghiệp dưới danh nghĩa đặt cọc nhận chuyển nhượng dự án, hợp đồng hợp tác kinh doanh (BCC), ủy thác đầu tư, cho vay cá nhân/bên liên quan hoặc tạm ứng nhà thầu kéo dài nhưng không tạo ra tài sản sinh lợi thực sự.
- **Khoản mục B09-DN bắt buộc soi chiếu:** Thuyết minh *Phải thu ngắn hạn khác (`noc10–noc14`)*, *Phải thu dài hạn khác (`noc30–noc34`)*, *Trả trước cho người bán (Mã 132)*, *Tài sản ngắn hạn khác / Tạm ứng (`noc25–noc29`)* và *Số dư với các bên liên quan* theo VAS 26.
- **Căn cứ pháp lý liên kết:** TT 200/2014 Điều 21 (TK 138), Điều 22 (TK 141), Điều 51 (TK 331) / TT 99/2025 Phụ lục II & IV; VAS 26 (thuyết minh bên liên quan); VSA 240 Đoạn 32 (rà soát nghiệp vụ bất thường ngoài hoạt động bình thường).

## Playbook TATA & CFO/Assets: Rủi ro Phân kỳ Lợi nhuận giấy — Dòng tiền âm (Accruals & Cash Quality)
- **Chỉ số kích hoạt:** `TATA` (*Total Accruals to Total Assets* = `(LNST - CFO) / Tổng tài sản` dương lớn > 0.031) và `CFO/Total Assets` (Lưu chuyển tiền thuần HĐKD / Tổng tài sản âm hoặc rất thấp).
- **Ý nghĩa pháp chứng:** Doanh nghiệp báo lãi ròng (`LNST > 0`) nhưng dòng tiền thực từ kinh doanh âm (`CFO < 0` — hiện tượng *Cash Flow Divergence*). Lợi nhuận chủ yếu đến từ các khoản dồn tích trên giấy (tăng phải thu, tồn kho ứ đọng, lãi đánh giá lại tài sản/bán công ty con chưa thu tiền) chứ không tạo ra dòng tiền mặt thực tế.
- **Khoản mục B09-DN bắt buộc soi chiếu:** Báo cáo Lưu chuyển tiền tệ (`B03-DN`) phần điều chỉnh thay đổi vốn lưu động (phải thu, hàng tồn kho, phải trả), Thuyết minh *Doanh thu tài chính (`noc122–noc130`, đặc biệt lãi bán đầu tư `noc155`)*, *Tiền và tương đương tiền (`noc1–noc5`)* và *Hàng tồn kho (`noc15–noc24`)*.
- **Căn cứ pháp lý liên kết:** VSA 240 Đoạn 12 (hoài nghi nghề nghiệp) & Đoạn 32 (kiểm tra bút toán điều chỉnh cuối kỳ và ước tính kế toán); VAS 14 (thực chất doanh thu); TT 99/2025 Điều 17 & Phụ lục IV.

## Playbook AQI & DEPI: Rủi ro Vốn hóa chi phí bất thường, Tài sản dài hạn mờ ám & Giảm tốc Khấu hao
- **Chỉ số kích hoạt:** `AQI` (*Asset Quality Index* > 1.039 — tỷ trọng tài sản dài hạn ngoài TSCĐ hữu hình tăng lên) và `DEPI` (*Depreciation Index* > 1.001 — tốc độ khấu hao TSCĐ hữu hình chậm lại so với năm trước).
- **Ý nghĩa pháp chứng:** Doanh nghiệp có thể trì hoãn ghi nhận chi phí bằng cách vốn hóa chi phí sửa chữa/lãi vay vào *Chi phí xây dựng cơ bản dở dang (TK 241)*, kéo dài thời gian khấu hao TSCĐ để giảm chi phí khấu hao năm hiện tại, hoặc tích tụ *Lợi thế thương mại (Goodwill)* và đầu tư dài hạn kém hiệu quả.
- **Khoản mục B09-DN bắt buộc soi chiếu:** Thuyết minh *Nguyên giá và Hao mòn lũy kế TSCĐ hữu hình (`noc35–noc42`)*, *TSCĐ vô hình (`noc51–noc58`)*, *Chi phí XDCB dở dang (TK 241)*, *Giá gốc và Phân bổ Lợi thế thương mại (`noc147–noc154`)* và *Chính sách khấu hao* (xem có thay đổi thời gian sử dụng hữu ích TSCĐ trong kỳ không).
- **Căn cứ pháp lý liên kết:** TT 200/2014 Điều 46 (TK 241 — XDCB dở dang) / TT 99/2025; VSA 240 Đoạn 32 (rà soát thiên lệch trong ước tính kế toán về thời gian khấu hao và giá trị thu hồi tài sản).

## Playbook GMI, SGI & SGAI: Rủi ro Suy giảm Biên lợi nhuận, Tăng trưởng quá nóng & Phình chi phí quản lý
- **Chỉ số kích hoạt:** `GMI` (*Gross Margin Index* > 1.041 — biên lãi gộp năm nay giảm so với năm trước), `SGI` (*Sales Growth Index* > 1.134 — doanh thu tăng đột biến gây áp lực kiểm soát và vốn lưu động), và `SGAI` (*SG&A Index* > 1.041 — chi phí bán hàng & QLDN tăng nhanh hơn doanh thu).
- **Ý nghĩa pháp chứng:** Biên lãi gộp suy giảm tạo động cơ mạnh để Ban Giám đốc "xào nấu" giá vốn, né tránh trích lập dự phòng giảm giá hàng tồn kho (TK 2294) hoặc thổi doanh thu cuối kỳ. Doanh thu tăng nóng (`SGI` rất cao) ở doanh nghiệp nhỏ hoặc đang tái cấu trúc thường đi kèm doanh thu thương mại biên mỏng hoặc giao dịch nội bộ/bên liên quan.
- **Khoản mục B09-DN bắt buộc soi chiếu:** Thuyết minh *Chi tiết Doanh thu (`noc102–noc105`)*, *Giảm trừ doanh thu & Hàng bán bị trả lại (`noc106–noc112`)*, *Chi tiết Giá vốn & Dự phòng giảm giá HTK (`noc113–noc121`)*, *Chi phí sản xuất kinh doanh theo yếu tố (`noc140–noc145`)*.
- **Căn cứ pháp lý liên kết:** VSA 240 Đoạn 26 & Phụ lục 1 (động cơ/áp lực khi biên lợi nhuận suy giảm); VAS 14 Đoạn 10; TT 48/2019 Điều 4 (dự phòng giảm giá HTK theo NRV).

## Playbook Altman Z'' & LVGI: Rủi ro Kiệt quệ tài chính, Đòn bẩy nợ vay & Khả năng hoạt động liên tục
- **Chỉ số kích hoạt:** `Altman Z'' (EMS 2005)` rơi vào vùng Nguy hiểm (`< 4.35`) hoặc vùng Xám (`4.35–5.85`), và `LVGI` (*Leverage Index* > 1.111 — tỷ số đòn bẩy nợ/tổng tài sản tăng lên).
- **Ý nghĩa pháp chứng:** Áp lực trả nợ đáo hạn (đặc biệt nợ vay dài hạn đến hạn trả và trái phiếu phát hành) làm tăng mạnh động cơ thao túng BCTC nhằm tránh vi phạm cam kết tín dụng (*debt covenants*) hoặc che giấu rủi ro mất khả năng thanh toán/hoạt động liên tục (*Going Concern*).
- **Khoản mục B09-DN bắt buộc soi chiếu:** Thuyết minh *Vay và nợ thuê tài chính ngắn hạn (`noc65–noc67`, đặc biệt Vay dài hạn đến hạn trả `noc67`)*, *Vay dài hạn & Trái phiếu phát hành (`noc93–noc98`)*, *Thuế và các khoản phải nộp Nhà nước (`noc68–noc77`)*, và *Ý kiến kiểm toán viên độc lập* (đoạn nhấn mạnh về khả năng hoạt động liên tục / lỗ lũy kế / nợ ngắn hạn vượt tài sản ngắn hạn).
- **Căn cứ pháp lý liên kết:** VSA 240 Phụ lục 1 (áp lực tài chính và cam kết nợ vay); TT 99/2025 Điều 17 (phân biệt BCTC doanh nghiệp đáp ứng và không đáp ứng giả định hoạt động liên tục); VSA 570 (Hoạt động liên tục).
