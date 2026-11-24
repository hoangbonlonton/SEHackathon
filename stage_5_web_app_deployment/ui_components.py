"""
HỆ THỐNG THIẾT KẾ GIAO DIỆN ĐỘC BẢN FINAUDIT AI (DEEP EMERALD & TERRACOTTA COPPER)
===================================================================================
Áp dụng trực tiếp từ design-system/finaudit-ai/MASTER.md & tokens.css (Phương án 2 đã duyệt):
  - Chủ đạo (Primary):   Ngọc Lục Bảo Đậm (#064E3B) -> Ngọc Lam Trầm (#0F766E)
  - Điểm nhấn (Accent):  Đồng Đỏ Terracotta (#C2410C) | Nền dịu (#FFF7ED)
  - Nền giấy (Surface):  Kem Ngà Ấm (#FAF8F5) | Thẻ Trắng Sứ (#FFFFFF) | Viền (#D1DDD8)
  - Chữ chính (Ink):     Than Rừng Sâu (#132A23) | Chữ phụ (#4B635B)
  - Trạng thái:          An toàn (#059669) | Theo dõi (#B45309) | Cảnh báo Đỏ Đô (#BE123C)
  - Kiểu chữ:            EB Garamond (Tiêu đề pháp lý) + Be Vietnam Pro (Thân chữ sắc nét dấu VN)
  - Responsive:          Cỡ chữ clamp() & touch target >= 44px cho cả Điện thoại (375px) & Máy tính (1440px)
"""

from __future__ import annotations

from html import escape
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ---------------------------------------------------------------------------
# 1. BẢNG MÀU CHUẨN DEEP EMERALD & TERRACOTTA COPPER
# ---------------------------------------------------------------------------
PALETTE = {
    "navy": "#132A23",       # Than Rừng Sâu (chữ tiêu đề & đường chính)
    "emerald": "#064E3B",    # Ngọc Lục Bảo Đậm (Primary)
    "royal": "#064E3B",      # Alias giữ tương thích
    "teal": "#0F766E",       # Ngọc Lam Trầm (Secondary)
    "blue": "#0F766E",       # Alias giữ tương thích
    "copper": "#C2410C",     # Đồng Đỏ Terracotta (CTA / Điểm nhấn đặc biệt)
    "copper_bg": "#FFF7ED",
    "copper_bd": "#FDBA74",
    "bg": "#FAF8F5",         # Kem Ngà Ấm (giấy chứng từ cao cấp)
    "card": "#FFFFFF",
    "muted_bg": "#F0F4F2",
    "border": "#D1DDD8",
    "muted": "#4B635B",
    "green": "#059669",
    "green_bg": "#ECFDF5",
    "green_bd": "#A7F3D0",
    "amber": "#B45309",
    "amber_bg": "#FFFBEB",
    "amber_bd": "#FDE68A",
    "red": "#BE123C",        # Đỏ Đô Bordeaux (sang trọng, tương phản cao)
    "red_bg": "#FFF1F2",
    "red_bd": "#FECDD3",
}

# Hồ sơ 5 tệp người dùng mục tiêu (chỉ định hướng lối tắt vào 5 phân hệ hiện có, không bịa chức năng)
ROLE_PROFILES: dict[str, dict[str, Any]] = {
    "Kiểm toán viên": {
        "short": "Kiểm toán",
        "focus": "Khoanh vùng khoản mục trọng yếu (TK 131, 138, 229, 241), đối chiếu VSA 240 Đoạn 26/32 & soi PDF Thuyết minh B09-DN.",
        "recommended_module_idx": 1,
        "recommended_label": "Mở ngay Hồ sơ Pháp chứng 360° & SHAP",
    },
    "Kế toán doanh nghiệp": {
        "short": "Kế toán",
        "focus": "Kiểm tra cân đối B01/B02 trước khi nộp BCTC, đối chiếu chuyển đổi Thông tư 99/2025 (từ 01/01/2026) và ranh giới dự phòng TT 48/2019.",
        "recommended_module_idx": 3,
        "recommended_label": "Mở ngay Tra cứu Luật VAS / TT 99/2025",
    },
    "Nhà đầu tư": {
        "short": "Nhà đầu tư",
        "focus": "Quét nhanh 643 cổ phiếu HOSE/HNX, tránh bẫy 'lãi trên giấy — dòng tiền CFO âm' và kiểm tra quỹ đạo rủi ro 8 năm (2018–2025).",
        "recommended_module_idx": 0,
        "recommended_label": "Mở ngay Radar Thị trường & Ngành ICB",
    },
    "Nhà cung cấp / Đối tác": {
        "short": "Nhà cung cấp",
        "focus": "Đánh giá sức khỏe thanh toán (Altman Z'', nợ ngắn hạn đến hạn trả) của khách hàng/đối tác trước khi cấp hạn mức công nợ bán chịu.",
        "recommended_module_idx": 1,
        "recommended_label": "Tra cứu sức khỏe thanh toán Đối tác (360°)",
    },
    "Doanh nghiệp SME": {
        "short": "Doanh nghiệp SME",
        "focus": "Tự tải file Excel/CSV BCTC 2 năm để kiểm tra toàn vẹn số liệu, chấm điểm sức khỏe nội bộ và chuẩn bị hồ sơ minh bạch vay vốn ngân hàng.",
        "recommended_module_idx": 2,
        "recommended_label": "Mở ngay Phòng Thẩm định BCTC Mới (Upload)",
    },
}

# Bảng Danh mục Hiệu lực Văn bản Pháp quy chuẩn (thành phần bắt buộc 2 đã duyệt)
LEGAL_REGISTRY_ROWS: list[dict[str, str]] = [
    {
        "Số hiệu Văn bản": "Thông tư 99/2025/TT-BTC",
        "Trích yếu nội dung": "Hướng dẫn Chế độ kế toán doanh nghiệp (Đổi tên B01-DN thành Báo cáo tình hình tài chính, Phụ lục II & IV)",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "27/10/2025",
        "Hiệu lực áp dụng": "Từ 01/01/2026",
        "Trạng thái": "Đang hiệu lực (Thay thế TT 200)",
    },
    {
        "Số hiệu Văn bản": "Thông tư 200/2014/TT-BTC",
        "Trích yếu nội dung": "Chế độ kế toán doanh nghiệp lịch sử (Điều 18 TK 131, Điều 21 TK 138, Điều 45 TK 229, Điều 46 TK 241, Điều 51 TK 331, Điều 79 TK 511)",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "22/12/2014",
        "Hiệu lực áp dụng": "01/01/2015 – 31/12/2025",
        "Trạng thái": "Áp dụng BCTC lịch sử <= 2025",
    },
    {
        "Số hiệu Văn bản": "Thông tư 48/2019/TT-BTC & TT 24/2022/TT-BTC",
        "Trích yếu nội dung": "Trích lập dự phòng làm cơ sở tính chi phí được trừ thuế TNDN (Khoản 1 Điều 1, Điều 4 NRV, Điều 6 tuổi nợ 30–50–70–100%)",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "08/08/2019 & 07/04/2022",
        "Hiệu lực áp dụng": "Đang thi hành",
        "Trạng thái": "Còn hiệu lực (Thuế TNDN)",
    },
    {
        "Số hiệu Văn bản": "VSA 240 (Thông tư 214/2012/TT-BTC)",
        "Trích yếu nội dung": "Trách nhiệm của kiểm toán viên liên quan đến gian lận BCTC (Đoạn 12 Hoài nghi, Đoạn 26 Doanh thu, Đoạn 31–33 Khống chế kiểm soát)",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "06/12/2012",
        "Hiệu lực áp dụng": "Từ 01/01/2014",
        "Trạng thái": "Còn hiệu lực",
    },
    {
        "Số hiệu Văn bản": "VAS 14 (QĐ 149/2001) & VAS 26 (QĐ 234/2003)",
        "Trích yếu nội dung": "Chuẩn mực Doanh thu và thu nhập khác (5 điều kiện Đoạn 10) & Thông tin về các bên liên quan trên B09-DN",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "31/12/2001 & 31/12/2003",
        "Hiệu lực áp dụng": "Đang thi hành",
        "Trạng thái": "Còn hiệu lực",
    },
]

# Biểu trưng hình học tối giản (vector SVG tinh gọn, thay thế hoàn toàn icon emoji đại trà)
BRAND_EMBLEM_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'style="vertical-align:middle;flex-shrink:0;" aria-hidden="true">'
    '<path d="M12 2L4 5.5V11.5C4 16.8 7.4 21.3 12 22.8C16.6 21.3 20 16.8 20 11.5V5.5L12 2Z" '
    'stroke="#FDBA74" stroke-width="1.8" fill="rgba(253,186,116,0.14)"/>'
    '<path d="M8.5 12L10.8 14.3L15.8 9.3" stroke="#FFFFFF" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

PLOTLY_BASE_FONT = dict(family="Be Vietnam Pro, Segoe UI, system-ui, sans-serif", size=13, color=PALETTE["navy"])

SHAP_DISPLAY_META = [
    ("shap_risk_cfo", "CFO/Tổng TS thấp (Dòng tiền yếu/âm)", "cfo_to_assets", "pct"),
    ("shap_risk_altman", "Altman Z'' thấp (Sức khỏe tài chính yếu)", "altman_z_double_prime", "num"),
    ("shap_risk_dsri", "DSRI (Phải thu KH tăng nhanh hơn DT)", "dsri", "num"),
    ("shap_risk_tata", "TATA (Dồn tích lợi nhuận trên giấy)", "tata", "num"),
    ("shap_risk_sgi", "SGI (Tăng trưởng DT quá nóng)", "sgi", "num"),
    ("shap_risk_aqi", "AQI (Tài sản dài hạn mờ ám tăng)", "aqi", "num"),
    ("shap_risk_srr", "SRR (Phải thu khác & Trả trước cao)", "sensitive_receivables_ratio", "pct"),
    ("shap_risk_gmi", "GMI (Biên lãi gộp suy giảm)", "gmi", "num"),
    ("shap_risk_depi", "DEPI (Tốc độ khấu hao TSCĐ giảm)", "depi", "num"),
    ("shap_risk_ar_rev", "Phải thu NH / Doanh thu cao", "receivable_to_revenue", "pct"),
    ("shap_risk_lvgi", "LVGI (Đòn bẩy nợ vay tăng nhanh)", "lvgi", "num"),
    ("shap_risk_sgai", "SGAI (Chi phí BH & QLDN phình to)", "sgai", "num"),
]


def inject_fintech_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;600;700&family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap');

        :root {
            --fa-primary: #064E3B;
            --fa-secondary: #0F766E;
            --fa-accent: #C2410C;
            --fa-accent-soft: #FFF7ED;
            --fa-bg: #FAF8F5;
            --fa-ink: #132A23;
            --fa-card: #FFFFFF;
            --fa-muted-bg: #F0F4F2;
            --fa-muted-fg: #4B635B;
            --fa-border: #D1DDD8;
            --fa-green: #059669;
            --fa-amber: #B45309;
            --fa-red: #BE123C;
            --fa-font-head: 'EB Garamond', Georgia, serif;
            --fa-font-body: 'Be Vietnam Pro', 'Segoe UI', system-ui, sans-serif;
        }

        html, body, .stApp {
            background-color: var(--fa-bg);
            color: var(--fa-ink);
            font-family: var(--fa-font-body);
            font-size: clamp(15.5px, 1.15vw, 17px);
            line-height: 1.6;
        }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            font-size: clamp(15px, 1.1vw, 16.5px);
            line-height: 1.62;
        }
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] p {
            font-size: 15px !important;
            font-weight: 600;
            color: var(--fa-ink);
        }
        .stRadio label p,
        .stCheckbox label p {
            font-size: 15px !important;
            line-height: 1.45;
        }
        .stSelectbox div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"],
        .stTextInput input {
            font-size: 15px !important;
        }
        [data-testid="stCaptionContainer"] p {
            font-size: 13.8px !important;
            color: var(--fa-muted-fg);
            line-height: 1.5;
        }
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid var(--fa-border);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] .stRadio label p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            font-size: 14.8px !important;
        }
        .main .block-container {
            padding-top: 0.75rem;
            padding-bottom: 2.5rem;
            max-width: 1400px;
        }

        /* Thanh Sticky Top Banner Cố định Chuẩn Website Chứng từ Pháp lý */
        .fa-sticky-bar {
            position: sticky;
            top: 2.6rem;
            z-index: 90;
            background: rgba(6, 78, 59, 0.97);
            backdrop-filter: blur(8px);
            color: #FFFFFF;
            border: 1px solid rgba(253, 186, 116, 0.28);
            border-bottom: 3px solid var(--fa-accent);
            border-radius: 12px;
            padding: 11px 18px;
            margin-bottom: 14px;
            box-shadow: 0 6px 18px rgba(6, 78, 59, 0.14);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .fa-sticky-left {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .fa-sticky-brand {
            font-family: var(--fa-font-head);
            font-size: clamp(19px, 1.85vw, 23px);
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: 0.2px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .fa-sticky-tag {
            font-size: 13px;
            font-weight: 600;
            padding: 4px 11px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.24);
            color: #F0FDFA;
            white-space: nowrap;
        }
        .fa-sticky-role {
            font-size: 13.5px;
            font-weight: 700;
            padding: 5px 13px;
            border-radius: 999px;
            background: var(--fa-accent);
            color: #FFFFFF;
            border: 1px solid #FDBA74;
            white-space: nowrap;
        }

        /* Banner Chính Phân hệ — Gradient Ngọc Lục Bảo Đậm + Viền Đồng Đỏ */
        .fa-hero {
            background: linear-gradient(135deg, #064E3B 0%, #0A5F4E 56%, #0F766E 100%);
            color: #FFFFFF;
            padding: clamp(18px, 2.4vw, 26px) clamp(20px, 2.6vw, 30px);
            border-radius: 15px;
            border-bottom: 4px solid var(--fa-accent);
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(6, 78, 59, 0.14);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
        }
        .fa-hero-kicker {
            font-size: 12.5px;
            letter-spacing: 1.1px;
            text-transform: uppercase;
            color: #FDBA74;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .fa-hero h1 {
            margin: 0;
            font-family: var(--fa-font-head);
            font-size: clamp(25px, 2.85vw, 34px);
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.22;
        }
        .fa-hero p {
            margin: 8px 0 0 0;
            font-size: clamp(14.8px, 1.2vw, 16.5px);
            color: #E6F4F1;
            line-height: 1.55;
        }
        .fa-hero-pill {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(253, 186, 116, 0.35);
            padding: 10px 15px;
            border-radius: 10px;
            font-size: 13.5px;
            color: #FAF8F5;
            text-align: right;
            line-height: 1.55;
        }

        /* Thanh Gợi ý Theo Vai trò 5 nhóm người dùng */
        .fa-role-strip {
            background: var(--fa-accent-soft);
            border: 1px solid #FDBA74;
            border-left: 4px solid var(--fa-accent);
            border-radius: 10px;
            padding: 11px 16px;
            margin-bottom: 14px;
            font-size: 14.8px;
            color: #7C2D12;
            line-height: 1.55;
        }

        /* Thẻ KPI Độc bản trên nền Kem Ngà */
        .fa-kpi {
            background: var(--fa-card);
            border: 1px solid var(--fa-border);
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 2px 6px rgba(19, 42, 35, 0.04);
            height: 100%;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        }
        .fa-kpi:hover {
            transform: translateY(-2px);
            border-color: var(--fa-secondary);
            box-shadow: 0 6px 14px rgba(6, 78, 59, 0.08);
        }
        .fa-kpi-label {
            font-size: 13px;
            font-weight: 700;
            color: var(--fa-muted-fg);
            text-transform: uppercase;
            letter-spacing: 0.45px;
        }
        .fa-kpi-value {
            font-size: clamp(23px, 2.3vw, 30px);
            font-weight: 800;
            color: var(--fa-ink);
            margin: 6px 0 4px;
            font-variant-numeric: tabular-nums;
            line-height: 1.15;
            overflow-wrap: anywhere;
        }
        .fa-kpi-sub {
            font-size: 13.5px;
            color: var(--fa-muted-fg);
            line-height: 1.4;
        }

        /* Card & Tiêu đề mục */
        .fa-card {
            background: var(--fa-card);
            border: 1px solid var(--fa-border);
            border-radius: 13px;
            padding: 20px 22px;
            box-shadow: 0 2px 6px rgba(19, 42, 35, 0.04);
            margin-bottom: 14px;
        }
        .fa-section-title {
            font-family: var(--fa-font-head);
            font-size: clamp(20px, 2.0vw, 25px);
            font-weight: 700;
            color: var(--fa-primary);
            margin: 14px 0 12px;
            padding-bottom: 6px;
            border-bottom: 2px solid var(--fa-border);
        }

        /* Nhãn màu ngữ nghĩa kèm chấm trạng thái hình học tối giản */
        .fa-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 13.5px;
            font-weight: 700;
            line-height: 1.25;
            white-space: nowrap;
        }
        .fa-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .fa-dot-green { background: #059669; }
        .fa-dot-amber { background: #B45309; }
        .fa-dot-red   { background: #BE123C; }
        .fa-dot-teal  { background: #0F766E; }

        .fa-badge-green { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
        .fa-badge-amber { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
        .fa-badge-red   { background: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }
        .fa-badge-blue  { background: #F0FDFA; color: #0F766E; border: 1px solid #99F6E4; }
        .fa-badge-copper { background: #FFF7ED; color: #C2410C; border: 1px solid #FDBA74; }

        /* Thẻ Trích dẫn RAG Pháp lý */
        .fa-rag-card {
            background: #FFFFFF;
            border: 1px solid var(--fa-border);
            border-left: 4px solid var(--fa-primary);
            border-radius: 10px;
            padding: 16px 18px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(19, 42, 35, 0.04);
        }
        .fa-rag-cite {
            font-size: 15.5px;
            font-weight: 700;
            color: var(--fa-primary);
            margin-bottom: 6px;
        }
        .fa-rag-body {
            font-size: 15px;
            color: var(--fa-ink);
            line-height: 1.65;
            overflow-wrap: break-word;
        }
        .fa-rag-meta {
            margin-top: 9px;
            font-size: 13px;
            color: var(--fa-muted-fg);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        }

        /* Chân trang Chuẩn Website Pháp lý – Chứng từ (Institutional Footer) */
        .fa-footer {
            margin-top: 26px;
            background: var(--fa-muted-bg);
            border: 1px solid var(--fa-border);
            border-top: 3px solid var(--fa-primary);
            border-radius: 12px;
            padding: 20px 22px;
            color: var(--fa-muted-fg);
            font-size: 14px;
            line-height: 1.62;
        }
        .fa-footer-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
        }
        .fa-footer h4 {
            margin: 0 0 8px 0;
            font-family: var(--fa-font-head);
            font-size: 17px;
            color: var(--fa-primary);
        }

        /* Nút bấm cảm ứng thân thiện Mobile & Desktop (>= 46px) */
        .stButton > button, .stDownloadButton > button {
            min-height: 46px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            padding: 8px 16px;
            transition: all 0.18s ease;
        }
        .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
            background-color: var(--fa-accent) !important;
            border-color: var(--fa-accent) !important;
            color: #FFFFFF !important;
        }
        .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
            background-color: #9A3412 !important;
            border-color: #9A3412 !important;
        }

        /* Tabs sắc nét theo Ngọc Lục Bảo */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            flex-wrap: wrap;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #FFFFFF;
            border: 1px solid var(--fa-border);
            border-radius: 9px;
            padding: 10px 18px;
            min-height: 46px;
            font-size: 15px;
            font-weight: 600;
            color: var(--fa-muted-fg);
        }
        .stTabs [aria-selected="true"] {
            background-color: var(--fa-primary) !important;
            color: #FFFFFF !important;
            border-color: var(--fa-primary) !important;
        }

        /* Bảng dữ liệu cuộn ngang an toàn trên màn hình nhỏ */
        [data-testid="stDataFrame"] {
            overflow-x: auto;
        }

        /* Responsive Mobile (<= 768px) — giữ cỡ chữ >= 15px dễ đọc */
        @media (max-width: 768px) {
            html, body, .stApp {
                font-size: 15px;
            }
            .fa-sticky-bar {
                position: relative;
                top: 0;
                padding: 11px 13px;
            }
            .fa-hero {
                padding: 16px;
            }
            .fa-hero-pill {
                text-align: left;
                width: 100%;
            }
            .fa-footer-grid {
                grid-template-columns: 1fr;
            }
            .fa-card {
                padding: 15px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sticky_top_banner(active_role: str, active_module: str) -> None:
    """Thành phần bắt buộc 1: Thanh Sticky Top Banner rõ ràng, dễ thao tác."""
    role_short = ROLE_PROFILES.get(active_role, {}).get("short", active_role)
    mod_short = active_module.split(".", 1)[-1].strip() if "." in active_module else active_module
    st.markdown(
        f"""
        <div class="fa-sticky-bar">
          <div class="fa-sticky-left">
            <span class="fa-sticky-brand">{BRAND_EMBLEM_SVG} FinAudit AI</span>
            <span class="fa-sticky-tag">TT 99/2025 &amp; TT 200/2014</span>
            <span class="fa-sticky-tag">VSA 240 • 643 DN HOSE/HNX</span>
            <span class="fa-sticky-tag">Phân hệ: {escape(mod_short)}</span>
          </div>
          <div class="fa-sticky-left">
            <span class="fa-sticky-role">Vai trò: {escape(role_short)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_role_guidance_strip(active_role: str) -> None:
    """Hiển thị gợi ý thao tác đúng vai trò trong 5 tệp người dùng (không tạo chức năng giả)."""
    prof = ROLE_PROFILES.get(active_role)
    if not prof:
        return
    st.markdown(
        f"""
        <div class="fa-role-strip">
          <strong>Góc nhìn {escape(active_role)}:</strong> {escape(prof['focus'])}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_legal_registry_table() -> None:
    """Thành phần bắt buộc 2: Danh mục Hiệu lực Văn bản Pháp quy chuẩn Bộ Tài chính."""
    st.markdown('<div class="fa-section-title">Danh mục Văn bản Pháp quy &amp; Trạng thái Hiệu lực Áp dụng</div>', unsafe_allow_html=True)
    df_reg = pd.DataFrame(LEGAL_REGISTRY_ROWS)
    st.dataframe(df_reg, width="stretch", hide_index=True)


def render_hero(kicker: str, title: str, subtitle: str, right_badge: str = "") -> None:
    right_html = f'<div class="fa-hero-pill">{right_badge}</div>' if right_badge else ""
    st.markdown(
        f"""
        <div class="fa-hero">
          <div style="flex:1;min-width:240px;">
            <div class="fa-hero-kicker">{escape(kicker)}</div>
            <h1>{escape(title)}</h1>
            <p>{subtitle}</p>
          </div>
          {right_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, sub: str, accent_color: str = "#064E3B") -> None:
    st.markdown(
        f"""
        <div class="fa-kpi" style="border-top: 3px solid {accent_color};">
          <div class="fa-kpi-label">{escape(label)}</div>
          <div class="fa-kpi-value" style="color:{accent_color};">{escape(value)}</div>
          <div class="fa-kpi-sub">{escape(sub)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge_html(score: float | None, tier: str) -> str:
    if score is None or pd.isna(score):
        return f'<span class="fa-badge fa-badge-blue"><span class="fa-dot fa-dot-teal"></span>{escape(tier)}</span>'
    if score >= 65.0:
        return f'<span class="fa-badge fa-badge-red"><span class="fa-dot fa-dot-red"></span>{escape(tier)}</span>'
    if score >= 40.0:
        return f'<span class="fa-badge fa-badge-amber"><span class="fa-dot fa-dot-amber"></span>{escape(tier)}</span>'
    return f'<span class="fa-badge fa-badge-green"><span class="fa-dot fa-dot-green"></span>{escape(tier)}</span>'


def render_vsa240_disclaimer() -> None:
    """Thành phần bắt buộc 3: Chân trang Chuẩn Website Pháp lý – Chứng từ (Institutional Footer)."""
    st.markdown(
        """
        <div class="fa-footer">
          <div class="fa-footer-grid">
            <div>
              <h4>Tuyên bố Pháp lý chuẩn VSA 240</h4>
              Hệ thống <strong>FinAudit AI — FinForensics</strong> chỉ cung cấp <em>Chỉ báo rủi ro chất lượng lợi nhuận (Forensic Risk Red Flags)</em>
              hỗ trợ khoanh vùng kiểm toán theo thái độ hoài nghi nghề nghiệp (TT 214/2012/TT-BTC),
              <strong>tuyệt đối không kết luận pháp lý về gian lận</strong> và không thay thế ý kiến kiểm toán độc lập.
            </div>
            <div>
              <h4>Nguồn Dữ liệu &amp; Chuẩn mực Áp dụng</h4>
              • BCTC &amp; B09-DN công khai: <strong>Vietcap IQ API</strong> (643 DN, 2018–2025)<br/>
              • PDF Kiểm toán 2025 gốc: <strong>Cổng công bố HOSE / Vietstock</strong><br/>
              • Pháp lý liên thông: <strong>TT 200/2014</strong> (&le;2025), <strong>TT 99/2025</strong> (từ 01/01/2026), <strong>TT 48/2019</strong>, <strong>VAS 14/26</strong>.
            </div>
            <div>
              <h4>Thông tin Dự án &amp; Đối tượng Hỗ trợ</h4>
              Dự án <strong>SE-Hackathon Challenge 2026</strong> — Trường Kinh tế, ĐH Công nghiệp Hà Nội (HaUI).<br/>
              Phục vụ: <em>Kiểm toán • Kế toán • Nhà đầu tư • Nhà cung cấp • Doanh nghiệp SME</em>.<br/>
              Trụ cột phát triển bền vững: <strong>ESG — Pillar G (Minh bạch Quản trị)</strong>.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 2. THƯ VIỆN BIỂU ĐỒ TƯƠNG TÁC PLOTLY (ĐỒNG BỘ DEEP EMERALD & TERRACOTTA COPPER)
# ---------------------------------------------------------------------------
def plot_forensic_matrix_2d(df_filtered: pd.DataFrame) -> go.Figure:
    """Ma trận Pháp chứng 2D: Beneish M-Score vs Altman Z''-Score."""
    df = df_filtered.dropna(subset=["beneish_m_score", "altman_z_double_prime", "composite_risk_score"]).copy()
    df["x_plot"] = df["altman_z_double_prime"].clip(-2.0, 14.0)
    df["y_plot"] = df["beneish_m_score"].clip(-6.0, 4.0)
    df["size_plot"] = np.clip(np.log1p(df["total_assets"].fillna(10.0).clip(lower=1.0)) * 2.8, 7.0, 24.0)

    tier_colors = {
        "Thấp (An toàn)": PALETTE["green"],
        "Trung bình (Cần theo dõi)": PALETTE["amber"],
        "Cao (Cảnh báo Đỏ)": PALETTE["red"],
    }

    fig = go.Figure()
    fig.add_shape(
        type="rect", x0=-2.2, x1=4.35, y0=-1.78, y1=4.2,
        fillcolor="rgba(190, 18, 60, 0.07)", line_width=0, layer="below",
    )
    fig.add_shape(
        type="rect", x0=5.85, x1=14.3, y0=-6.2, y1=-1.78,
        fillcolor="rgba(5, 150, 105, 0.06)", line_width=0, layer="below",
    )

    for tier_name, color in tier_colors.items():
        sub = df[df["risk_tier"] == tier_name]
        if sub.empty:
            continue
        hover_txt = [
            (
                f"<b>{r['ticker']} — {r['company_name']}</b><br>"
                f"Ngành: {r['icb_sector_vi']} ({r['exchange']})<br>"
                f"<b>Composite Risk: {r['composite_risk_score']:.1f} / 100</b><br>"
                f"Beneish M-Score: {r['beneish_m_score']:.3f}<br>"
                f"Altman Z'' EMS: {r['altman_z_double_prime']:.3f}<br>"
                f"Doanh thu: {r['net_revenue']:,.1f} tỷ | CFO: {r['cfo']:,.1f} tỷ"
            )
            for _, r in sub.iterrows()
        ]
        fig.add_trace(
            go.Scatter(
                x=sub["x_plot"],
                y=sub["y_plot"],
                mode="markers",
                name=f"{tier_name} ({len(sub)})",
                marker=dict(size=sub["size_plot"], color=color, opacity=0.84, line=dict(width=1, color="#FFFFFF")),
                text=hover_txt,
                hovertemplate="%{text}<extra></extra>",
            )
        )

    fig.add_hline(
        y=-1.78, line_dash="dash", line_color=PALETTE["red"], line_width=1.4,
        annotation_text="Ngưỡng Beneish M = -1.78", annotation_position="top right",
        annotation_font_size=12.5, annotation_font_color=PALETTE["red"],
    )
    fig.add_vline(
        x=4.35, line_dash="dash", line_color=PALETTE["red"], line_width=1.3,
        annotation_text="Altman Nguy hiểm (4.35)", annotation_position="top left",
        annotation_font_size=12.5, annotation_font_color=PALETTE["red"],
    )
    fig.add_vline(
        x=5.85, line_dash="dot", line_color=PALETTE["green"], line_width=1.3,
        annotation_text="Altman An toàn (5.85)", annotation_position="bottom right",
        annotation_font_size=12.5, annotation_font_color=PALETTE["green"],
    )

    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(text="Ma trận Pháp chứng 2D: Beneish M-Score vs. Altman Z''-Score (EMS 2005)", font=dict(size=15.5, color=PALETTE["emerald"])),
        xaxis_title="Altman Z''-Score (Càng sang phải càng vững tài chính →)",
        yaxis_title="Beneish M-Score (Càng lên trên rủi ro thổi số càng cao ↑)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=470,
        margin=dict(l=60, r=25, t=58, b=55),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1.0, font=dict(size=12.5)),
        xaxis=dict(gridcolor="#F0F4F2", zerolinecolor="#D1DDD8", range=[-2.2, 14.3], tickfont=dict(size=12.5)),
        yaxis=dict(gridcolor="#F0F4F2", zerolinecolor="#D1DDD8", range=[-6.2, 4.2], tickfont=dict(size=12.5)),
    )
    return fig


def plot_sector_risk_ranking(df_filtered: pd.DataFrame) -> go.Figure:
    """Biểu đồ ngang xếp hạng rủi ro trung vị & tỷ lệ cờ đỏ theo Ngành ICB."""
    df = df_filtered.dropna(subset=["composite_risk_score"]).copy()
    agg = (
        df.groupby("icb_sector_vi", as_index=False)
        .agg(
            n_firms=("ticker", "count"),
            median_score=("composite_risk_score", "median"),
            red_pct=("composite_risk_score", lambda s: float((s >= 65.0).mean() * 100.0)),
        )
        .sort_values("median_score", ascending=True)
    )
    colors = [
        PALETTE["red"] if v >= 45 else (PALETTE["copper"] if v >= 32 else PALETTE["emerald"])
        for v in agg["median_score"]
    ]
    fig = go.Figure(
        go.Bar(
            y=agg["icb_sector_vi"],
            x=agg["median_score"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{r['median_score']:.1f}đ (Đỏ: {r['red_pct']:.1f}% • n={r['n_firms']})" for _, r in agg.iterrows()],
            textposition="outside",
            textfont=dict(size=12.5, color=PALETTE["navy"]),
            hovertemplate="<b>%{y}</b><br>Điểm rủi ro trung vị: <b>%{x:.1f}đ</b><br>%{text}<extra></extra>",
        )
    )
    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(text="Xếp hạng Mức độ Rủi ro Trung vị theo 15 Ngành ICB", font=dict(size=15.5, color=PALETTE["emerald"])),
        xaxis_title="Điểm Rủi ro Pháp chứng Trung vị (0–100)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=470,
        margin=dict(l=18, r=175, t=58, b=50),
        xaxis=dict(gridcolor="#F0F4F2", tickfont=dict(size=12.5), range=[0, max(float(agg["median_score"].max()) * 1.54, 58.0)] if len(agg) else [0, 60]),
        yaxis=dict(tickfont=dict(size=12.5)),
    )
    return fig


def plot_risk_gauge(score: float, tier: str) -> go.Figure:
    """Đồng hồ Gauge 0–100 hài hòa với Ngọc Lục Bảo – Đồng Đỏ – Đỏ Đô."""
    val = float(score) if pd.notna(score) else 0.0
    bar_color = PALETTE["red"] if val >= 65 else (PALETTE["copper"] if val >= 40 else PALETTE["green"])
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": " đ", "font": {"size": 38, "color": bar_color, "family": "monospace"}},
            title={"text": f"<b>Composite Risk Score</b><br><span style='font-size:13.5px;color:#4B635B'>{tier}</span>", "font": {"size": 15.5, "color": PALETTE["emerald"]}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#4B635B", "tickfont": {"size": 12}},
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "#FFFFFF",
                "borderwidth": 1,
                "bordercolor": "#D1DDD8",
                "steps": [
                    {"range": [0, 40], "color": "#ECFDF5"},
                    {"range": [40, 65], "color": "#FFF7ED"},
                    {"range": [65, 100], "color": "#FFF1F2"},
                ],
                "threshold": {"line": {"color": PALETTE["navy"], "width": 3}, "thickness": 0.78, "value": val},
            },
        )
    )
    fig.update_layout(font=PLOTLY_BASE_FONT, paper_bgcolor="#FFFFFF", height=265, margin=dict(l=22, r=22, t=58, b=10))
    return fig


def plot_shap_waterfall(row: pd.Series) -> go.Figure:
    """Biểu đồ Thác nước SHAP đồng bộ màu Đỏ Đô (+) / Ngọc Lục Bảo (-) / Ngọc Đậm (Tổng)."""
    base_val = float(row.get("shap_base_value", 29.224))
    items = []
    for shap_col, label_vi, raw_col, fmt in SHAP_DISPLAY_META:
        v = row.get(shap_col, np.nan)
        if pd.notna(v):
            raw_v = row.get(raw_col, np.nan)
            raw_txt = (f"{float(raw_v)*100:.1f}%" if fmt == "pct" else f"{float(raw_v):.2f}") if pd.notna(raw_v) else "N/A"
            short_lbl = label_vi.split("(")[0].strip() + f" ({raw_txt})"
            items.append((short_lbl, float(v)))

    items.sort(key=lambda x: abs(x[1]), reverse=True)
    top_items = items[:8]
    other_sum = sum(x[1] for x in items[8:])

    labels = ["Nền thị trường (Base)"] + [x[0] for x in top_items]
    measures = ["absolute"] + ["relative"] * len(top_items)
    values = [base_val] + [x[1] for x in top_items]
    if abs(other_sum) >= 0.05:
        labels.append("4 chỉ số phụ còn lại")
        measures.append("relative")
        values.append(other_sum)
    labels.append("Điểm Composite dự báo")
    measures.append("total")
    values.append(0.0)

    texts = []
    for m, v in zip(measures, values):
        if m == "absolute":
            texts.append(f"{v:.1f}đ")
        elif m == "total":
            tot = base_val + sum(x[1] for x in items)
            texts.append(f"<b>{tot:.1f}đ</b>")
        else:
            texts.append(f"{v:+.2f}đ")

    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=measures,
            x=labels,
            y=values,
            text=texts,
            textposition="outside",
            textfont=dict(size=12.5),
            connector={"line": {"color": "#D1DDD8", "width": 1.2}},
            increasing={"marker": {"color": PALETTE["red"]}},
            decreasing={"marker": {"color": PALETTE["green"]}},
            totals={"marker": {"color": PALETTE["emerald"]}},
        )
    )
    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(text="Biểu đồ Thác nước SHAP: Chỉ số đẩy rủi ro tăng (+) hay kéo giảm (-)", font=dict(size=15.5, color=PALETTE["emerald"])),
        yaxis_title="Điểm Rủi ro Pháp chứng (0–100)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=430,
        margin=dict(l=50, r=20, t=58, b=108),
        xaxis=dict(tickangle=-25, tickfont=dict(size=12)),
        yaxis=dict(gridcolor="#F0F4F2", tickfont=dict(size=12.5), range=[0, max(108.0, float(row.get("composite_risk_score", 50.0)) + 20.0)]),
    )
    return fig


def plot_sector_radar(row: pd.Series) -> go.Figure:
    """Biểu đồ Radar đối sánh 6 trục rủi ro chuẩn hóa với Trung vị ngành ICB."""
    axes_spec = [
        ("risk_dsri", "Phải thu (DSRI)"),
        ("risk_sgi", "Tăng trưởng DT (SGI)"),
        ("risk_tata", "Dồn tích (TATA)"),
        ("risk_cfo", "Dòng tiền yếu (CFO)"),
        ("risk_srr", "Tài sản mềm (SRR)"),
        ("risk_altman", "Kiệt quệ (Altman)"),
    ]
    cats = [a[1] for a in axes_spec]
    vals = [min(float(row.get(a[0], 0.0) or 0.0), 5.0) for a in axes_spec]
    cats_closed = cats + [cats[0]]
    vals_closed = vals + [vals[0]]
    peer_closed = [0.5] * len(cats_closed)

    is_high = float(row.get("composite_risk_score", 0)) >= 65
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=peer_closed,
            theta=cats_closed,
            fill="toself",
            name="Vùng chuẩn ngành ICB (Lành mạnh)",
            fillcolor="rgba(5, 150, 105, 0.14)",
            line=dict(color=PALETTE["green"], dash="dash", width=1.6),
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=vals_closed,
            theta=cats_closed,
            fill="toself",
            name=f"{row['ticker']} ({int(row['year'])})",
            fillcolor="rgba(190, 18, 60, 0.18)" if is_high else "rgba(194, 65, 12, 0.18)",
            line=dict(color=PALETTE["red"] if is_high else PALETTE["copper"], width=2.4),
        )
    )
    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(text="Radar Lệch chuẩn Ngành ICB (Càng xa tâm càng xấu hơn ngành)", font=dict(size=15, color=PALETTE["emerald"])),
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, range=[0, 5.2], gridcolor="#D1DDD8", tickfont=dict(size=11.5)),
            angularaxis=dict(gridcolor="#D1DDD8", tickfont=dict(size=12.5)),
        ),
        paper_bgcolor="#FFFFFF",
        height=430,
        margin=dict(l=52, r=52, t=60, b=46),
        legend=dict(orientation="h", yanchor="bottom", y=-0.16, xanchor="center", x=0.5, font=dict(size=12.5)),
    )
    return fig


def plot_multiyear_trend(df_comp: pd.DataFrame) -> go.Figure:
    """Biểu đồ 2 tầng đa năm (2018–2025) đồng bộ Deep Emerald & Terracotta Copper."""
    df = df_comp.sort_values("year").copy()
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        row_heights=[0.56, 0.44],
        subplot_titles=(
            "Doanh thu thuần vs. Lợi nhuận sau thuế vs. Dòng tiền kinh doanh CFO (Tỷ VND)",
            "Quỹ đạo Điểm Rủi ro Pháp chứng Tổng hợp (Composite Score 0–100)",
        ),
    )

    fig.add_trace(go.Bar(x=df["year"], y=df["net_revenue"], name="Doanh thu thuần", marker_color="#D1DDD8", opacity=0.84), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["year"], y=df["net_income"], name="LN Sau thuế (LNST)", mode="lines+markers", line=dict(color=PALETTE["emerald"], width=2.8), marker=dict(size=8)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["year"], y=df["cfo"], name="Dòng tiền HĐKD (CFO)", mode="lines+markers", line=dict(color=PALETTE["copper"], width=2.8, dash="dot"), marker=dict(size=8, symbol="diamond")), row=1, col=1)

    df_sc = df.dropna(subset=["composite_risk_score"])
    pt_colors = [PALETTE["red"] if v >= 65 else (PALETTE["copper"] if v >= 40 else PALETTE["green"]) for v in df_sc["composite_risk_score"]]
    fig.add_trace(
        go.Scatter(
            x=df_sc["year"],
            y=df_sc["composite_risk_score"],
            name="Composite Risk Score",
            mode="lines+markers+text",
            text=[f"{v:.1f}" for v in df_sc["composite_risk_score"]],
            textposition="top center",
            textfont=dict(size=12.5, color=PALETTE["navy"]),
            line=dict(color=PALETTE["navy"], width=2.8),
            marker=dict(size=10, color=pt_colors, line=dict(width=1.5, color="#FFFFFF")),
        ),
        row=2,
        col=1,
    )
    fig.add_hline(y=65, line_dash="dash", line_color=PALETTE["red"], line_width=1.3, row=2, col=1)
    fig.add_hline(y=40, line_dash="dot", line_color=PALETTE["copper"], line_width=1.3, row=2, col=1)

    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=520,
        margin=dict(l=60, r=25, t=48, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1.0, font=dict(size=12.5)),
    )
    fig.update_annotations(font_size=14.5, font_color=PALETTE["emerald"])
    fig.update_yaxes(gridcolor="#F0F4F2", tickfont=dict(size=12.5), row=1, col=1)
    fig.update_yaxes(gridcolor="#F0F4F2", tickfont=dict(size=12.5), range=[0, 108], title_text="Điểm (0–100)", row=2, col=1)
    fig.update_xaxes(dtick=1, tickfont=dict(size=12.5), row=2, col=1)
    return fig


def plot_validation_benchmarks(stage3_sum: dict[str, Any], stage4_sum: dict[str, Any]) -> tuple[go.Figure, go.Figure]:
    """2 biểu đồ kiểm chứng trung tâm đồng bộ Ngọc Lục Bảo – Đồng Đỏ."""
    bt = stage3_sum["layer4_empirical_backtest"]
    fig_auc = go.Figure(
        go.Bar(
            x=["Beneish đơn lẻ", "AI IsoForest đơn lẻ", "Altman Z'' đơn lẻ", "FinAudit Composite (4 Trụ cột)"],
            y=[bt["auc_beneish_only"], bt["auc_isoforest_only"], bt["auc_altman_only"], bt["auc_composite"]],
            marker_color=["#94A3B8", PALETTE["teal"], PALETTE["copper"], PALETTE["emerald"]],
            text=[f"{v:.4f}" for v in [bt["auc_beneish_only"], bt["auc_isoforest_only"], bt["auc_altman_only"], bt["auc_composite"]]],
            textposition="outside",
            textfont=dict(size=13, color=PALETTE["navy"]),
        )
    )
    fig_auc.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(text="Backtest Thực chứng (12 Bluechip vs 12 DN Biến cố): So sánh AUC-ROC", font=dict(size=15, color=PALETTE["emerald"])),
        yaxis=dict(range=[0, 1.14], title="AUC-ROC (1.00 = Tối đa)", gridcolor="#F0F4F2", tickfont=dict(size=12.5)),
        xaxis=dict(tickfont=dict(size=12.5)),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=370,
        margin=dict(l=52, r=20, t=54, b=46),
    )

    m_order = ["bm25_raw", "bm25_dual", "tfidf_wc", "hybrid_rrf"]
    m_names = ["BM25 Raw", "BM25 Dual-VN", "TF-IDF Word+Char", "Hybrid RRF (FinAudit)"]
    leg = stage4_sum["legal_benchmark_20q"]["comparison_by_mode"]
    pdf_b = stage4_sum["nvl_pdf_benchmark_6q"]["comparison_by_mode"]

    fig_rag = go.Figure()
    fig_rag.add_trace(
        go.Bar(
            name="20 câu Pháp lý VAS — Hit@1 (%)",
            x=m_names,
            y=[leg[m]["hit_at_1_pct"] for m in m_order],
            marker_color=PALETTE["emerald"],
            text=[f"{leg[m]['hit_at_1_pct']:.0f}%" for m in m_order],
            textposition="outside",
            textfont=dict(size=12.5),
        )
    )
    fig_rag.add_trace(
        go.Bar(
            name="PDF Nhiễu OCR NVL 2025 — Hit@1 (%)",
            x=m_names,
            y=[pdf_b[m]["hit_at_1_pct"] for m in m_order],
            marker_color=PALETTE["copper"],
            text=[f"{pdf_b[m]['hit_at_1_pct']:.1f}%" for m in m_order],
            textposition="outside",
            textfont=dict(size=12.5),
        )
    )
    fig_rag.update_layout(
        font=PLOTLY_BASE_FONT,
        barmode="group",
        title=dict(text="Đối chứng Động cơ RAG: Pháp lý VAS (20Q) & PDF Nhiễu OCR NVL 2025 (6Q)", font=dict(size=15, color=PALETTE["emerald"])),
        yaxis=dict(range=[0, 120], title="Hit Rate@1 (%)", gridcolor="#F0F4F2", tickfont=dict(size=12.5)),
        xaxis=dict(tickfont=dict(size=12.5)),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=370,
        margin=dict(l=52, r=20, t=54, b=46),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1.0, font=dict(size=12)),
    )
    return fig_auc, fig_rag


# ---------------------------------------------------------------------------
# 3. THƯ VIỆN BIỂU ĐỒ 3D PLOTLY WEBGL CÓ CHUYỂN ĐỘNG & CHÚ THÍCH 3D (BƯỚC 4)
# ---------------------------------------------------------------------------
EMERALD_COPPER_COLORSCALE = [
    [0.00, "#064E3B"],  # Ngọc Lục Bảo Đậm — Rất an toàn
    [0.28, "#059669"],  # Xanh Ngọc Lành mạnh
    [0.50, "#D97706"],  # Hổ Phách — Theo dõi
    [0.72, "#C2410C"],  # Đồng Đỏ Terracotta — Rủi ro cao
    [1.00, "#BE123C"],  # Đỏ Đô Bordeaux — Cảnh báo Đỏ nghiêm trọng
]


def _build_3d_danger_wireframe() -> go.Scatter3d:
    """Khung dây 3D đánh dấu Vùng Cảnh báo Kép (Altman <= 4.35, Beneish >= -1.78, CFO/TS <= 0%)."""
    x0, x1 = -2.0, 4.35
    y0, y1 = -1.78, 4.0
    z0, z1 = -35.0, 0.0
    xs = [
        x0, x1, x1, x0, x0, None,
        x0, x1, x1, x0, x0, None,
        x0, x0, None, x1, x1, None, x1, x1, None, x0, x0,
    ]
    ys = [
        y0, y0, y1, y1, y0, None,
        y0, y0, y1, y1, y0, None,
        y0, y0, None, y0, y0, None, y1, y1, None, y1, y1,
    ]
    zs = [
        z0, z0, z0, z0, z0, None,
        z1, z1, z1, z1, z1, None,
        z0, z1, None, z0, z1, None, z0, z1, None, z0, z1,
    ]
    return go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="lines",
        name="Khung Vùng Cảnh báo Kép (Z''≤4.35 • M≥-1.78 • CFO≤0%)",
        line=dict(color="rgba(190, 18, 60, 0.45)", width=2.5, dash="dash"),
        hoverinfo="skip",
        showlegend=True,
    )


def plot_forensic_space_3d_animated(
    df_multiyear: pd.DataFrame,
    selected_year: int = 2025,
    spotlight_tickers: tuple[str, ...] = ("TDH", "QCG", "NVL", "FPT"),
) -> go.Figure:
    """
    Không gian Pháp chứng 3D Động (2019 -> 2025) kèm Play/Pause, thanh trượt Năm & Chú thích 3D.
    Trục X: Altman Z'' EMS | Trục Y: Beneish M-Score | Trục Z: CFO / Tổng Tài sản (%).
    """
    df = df_multiyear.dropna(
        subset=["altman_z_double_prime", "beneish_m_score", "cfo_to_assets", "composite_risk_score", "year"]
    ).copy()
    if df.empty:
        fig_empty = go.Figure()
        fig_empty.update_layout(title="Không có dữ liệu hợp lệ để dựng không gian 3D", height=460)
        return fig_empty

    df["year_int"] = df["year"].astype(int)
    df["x_plot"] = df["altman_z_double_prime"].clip(-2.0, 14.0).round(2)
    df["y_plot"] = df["beneish_m_score"].clip(-6.0, 4.0).round(2)
    df["z_plot"] = (df["cfo_to_assets"] * 100.0).clip(-35.0, 35.0).round(2)
    df["size_plot"] = np.clip(np.log1p(df["total_assets"].fillna(10.0).clip(lower=1.0)) * 2.0, 5.5, 17.5).round(1)
    df["score_r"] = df["composite_risk_score"].round(1)

    years = sorted(df["year_int"].unique().tolist())
    init_year = int(selected_year) if int(selected_year) in years else years[-1]
    init_idx = years.index(init_year)
    wireframe_trace = _build_3d_danger_wireframe()

    def _make_year_trace_and_annots(sub: pd.DataFrame, yr: int) -> tuple[go.Scatter3d, list[dict[str, Any]]]:
        hover_txt = [
            (
                f"<b>{r['ticker']} — {r['company_name']}</b> ({yr})<br>"
                f"{r['icb_sector_vi']} ({r['exchange']})<br>"
                f"<b>Risk: {r['score_r']:.1f}/100</b> ({r['risk_tier']})<br>"
                f"Z'': {r['altman_z_double_prime']:.2f} | M: {r['beneish_m_score']:.2f} | CFO/TS: {r['cfo_to_assets']*100:.1f}%<br>"
                f"DT: {r['net_revenue']:,.1f} tỷ | CFO: {r['cfo']:,.1f} tỷ"
            )
            for _, r in sub.iterrows()
        ]
        pts_trace = go.Scatter3d(
            x=sub["x_plot"].tolist(),
            y=sub["y_plot"].tolist(),
            z=sub["z_plot"].tolist(),
            mode="markers",
            name=f"Doanh nghiệp năm {yr} (n={len(sub)})",
            marker=dict(
                size=sub["size_plot"].tolist(),
                color=sub["score_r"].tolist(),
                colorscale=EMERALD_COPPER_COLORSCALE,
                cmin=0.0,
                cmax=100.0,
                opacity=0.88,
                line=dict(width=0.6, color="#FFFFFF"),
                colorbar=dict(
                    title=dict(text="Điểm Rủi ro<br>(0–100)", font=dict(size=11, color=PALETTE["navy"])),
                    thickness=14,
                    len=0.62,
                    x=1.01,
                    tickvals=[0, 25, 40, 65, 100],
                    ticktext=["0", "25", "40 (TD)", "65 (Đỏ)", "100"],
                ),
            ),
            text=hover_txt,
            hovertemplate="%{text}<extra></extra>",
        )

        # Chú thích 3D rõ ràng (khung vùng rủi ro kép + các mã tiêu biểu hiện diện trong năm)
        annots: list[dict[str, Any]] = [
            dict(
                x=0.6,
                y=2.8,
                z=-28.0,
                text="<b>Vùng Cảnh báo Kép</b><br>Z''≤4.35 • M≥-1.78 • CFO≤0%",
                showarrow=False,
                font=dict(size=12, color=PALETTE["red"]),
                bgcolor="rgba(255, 241, 242, 0.92)",
                bordercolor=PALETTE["red"],
                borderwidth=1.2,
                borderpad=5,
            )
        ]

        pinned_rows = []
        for tkr in spotlight_tickers:
            m = sub[sub["ticker"] == tkr]
            if not m.empty:
                pinned_rows.append(m.iloc[0])
        if len(pinned_rows) < 2 and len(sub) >= 2:
            # Nếu người dùng lọc 1 ngành không có 4 mã mẫu, tự động ghim DN rủi ro cao nhất & an toàn nhất
            top_hi = sub.sort_values("composite_risk_score", ascending=False).iloc[0]
            top_lo = sub.sort_values("composite_risk_score", ascending=True).iloc[0]
            seen_t = {r["ticker"] for r in pinned_rows}
            for cand in (top_hi, top_lo):
                if cand["ticker"] not in seen_t:
                    pinned_rows.append(cand)
                    seen_t.add(cand["ticker"])

        offsets = [(26, -34), (-32, -32), (30, -24), (-28, 28)]
        for idx_p, r in enumerate(pinned_rows[:4]):
            sc = float(r["composite_risk_score"])
            if sc >= 65.0:
                tag_lbl, b_col, bg_col = "Đỏ", PALETTE["red"], "rgba(255, 241, 242, 0.95)"
            elif sc >= 40.0:
                tag_lbl, b_col, bg_col = "TD", PALETTE["copper"], "rgba(255, 247, 237, 0.95)"
            else:
                tag_lbl, b_col, bg_col = "AT", PALETTE["green"], "rgba(236, 253, 245, 0.95)"
            ax_off, ay_off = offsets[idx_p % len(offsets)]
            annots.append(
                dict(
                    x=float(r["x_plot"]),
                    y=float(r["y_plot"]),
                    z=float(r["z_plot"]),
                    text=f"<b>{r['ticker']}</b> ({sc:.1f}đ • {tag_lbl})",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=0.9,
                    arrowwidth=1.5,
                    arrowcolor=b_col,
                    ax=ax_off,
                    ay=ay_off,
                    font=dict(size=12, color=PALETTE["navy"]),
                    bgcolor=bg_col,
                    bordercolor=b_col,
                    borderwidth=1.2,
                    borderpad=4,
                )
            )
        return pts_trace, annots

    frames = []
    init_trace = None
    init_annots: list[dict[str, Any]] = []
    for yr in years:
        sub_y = df[df["year_int"] == yr]
        tr_y, an_y = _make_year_trace_and_annots(sub_y, yr)
        frames.append(
            go.Frame(
                name=str(yr),
                data=[tr_y],
                traces=[0],
                layout=go.Layout(
                    title=dict(
                        text=f"Không gian Pháp chứng 3D Động — Năm {yr} ({len(sub_y)} DN) | Kéo xoay 360° hoặc bấm Phát",
                        font=dict(size=15.5, color=PALETTE["emerald"]),
                    ),
                    scene=dict(annotations=an_y),
                ),
            )
        )
        if yr == init_year:
            init_trace = tr_y
            init_annots = an_y

    fig = go.Figure(data=[init_trace, wireframe_trace], frames=frames)

    slider_steps = [
        dict(
            method="animate",
            label=str(yr),
            args=[
                [str(yr)],
                {"mode": "immediate", "frame": {"duration": 500, "redraw": True}, "transition": {"duration": 0}},
            ],
        )
        for yr in years
    ]

    updatemenus = []
    sliders = []
    if len(years) > 1:
        updatemenus = [
            dict(
                type="buttons",
                direction="left",
                x=0.01,
                y=1.08,
                xanchor="left",
                yanchor="top",
                bgcolor="#FFFFFF",
                bordercolor=PALETTE["border"],
                borderwidth=1,
                font=dict(size=13, color=PALETTE["emerald"]),
                buttons=[
                    dict(
                        label=f"Phát ({years[0]}→{years[-1]})",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 950, "redraw": True},
                                "fromcurrent": False,
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                    dict(
                        label="Tạm dừng",
                        method="animate",
                        args=[
                            [None],
                            {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}},
                        ],
                    ),
                ],
            )
        ]
        sliders = [
            dict(
                active=init_idx,
                yanchor="top",
                xanchor="left",
                currentvalue=dict(
                    prefix="Năm tài chính đang chiếu: ",
                    visible=True,
                    xanchor="right",
                    font=dict(size=12, color=PALETTE["emerald"]),
                ),
                pad=dict(b=6, t=10),
                len=0.92,
                x=0.04,
                y=0.03,
                bgcolor="#F0F4F2",
                activebgcolor=PALETTE["copper"],
                bordercolor=PALETTE["border"],
                steps=slider_steps,
            )
        ]

    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(
            text=f"Không gian Pháp chứng 3D Động — Năm {init_year} ({len(df[df['year_int']==init_year])} DN) | Kéo xoay 360° hoặc bấm Phát",
            font=dict(size=15.5, color=PALETTE["emerald"]),
            x=0.01,
            y=0.98,
        ),
        paper_bgcolor="#FFFFFF",
        height=610,
        margin=dict(l=10, r=15, t=82, b=38),
        legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="right", x=0.98, font=dict(size=12.5)),
        updatemenus=updatemenus,
        sliders=sliders,
        scene=dict(
            uirevision="finaudit_3d_space",
            xaxis=dict(
                title=dict(text="Altman Z'' EMS (→ An toàn)", font=dict(size=13, color=PALETTE["navy"])),
                range=[-2.2, 14.2],
                backgroundcolor="#FAF8F5",
                gridcolor="#D1DDD8",
                zerolinecolor="#94A3B8",
            ),
            yaxis=dict(
                title=dict(text="Beneish M-Score (↑ Rủi ro thổi số)", font=dict(size=13, color=PALETTE["navy"])),
                range=[-6.2, 4.2],
                backgroundcolor="#FAF8F5",
                gridcolor="#D1DDD8",
                zerolinecolor="#94A3B8",
            ),
            zaxis=dict(
                title=dict(text="CFO / Tổng TS (%) (↑ Dòng tiền thật)", font=dict(size=13, color=PALETTE["navy"])),
                range=[-36.0, 36.0],
                backgroundcolor="#F0F4F2",
                gridcolor="#D1DDD8",
                zerolinecolor=PALETTE["copper"],
            ),
            camera=dict(eye=dict(x=1.55, y=-1.65, z=1.08)),
            annotations=init_annots,
        ),
    )
    return fig


def plot_sector_terrain_3d(df_multiyear: pd.DataFrame) -> go.Figure:
    """
    Địa hình Rủi ro 3D (Surface) theo 15 Ngành ICB × 7 Năm (2019–2025).
    Tự động ghim Chú thích 3D vào Đỉnh rủi ro cao nhất, Thung lũng an toàn nhất & Điểm nóng năm mới nhất.
    """
    df = df_multiyear.dropna(subset=["icb_sector_vi", "year", "composite_risk_score"]).copy()
    if df.empty:
        fig_empty = go.Figure()
        fig_empty.update_layout(title="Không có dữ liệu ngành để dựng địa hình 3D", height=460)
        return fig_empty

    df["year_int"] = df["year"].astype(int)
    piv_med = df.pivot_table(index="icb_sector_vi", columns="year_int", values="composite_risk_score", aggfunc="median")
    piv_cnt = df.pivot_table(index="icb_sector_vi", columns="year_int", values="ticker", aggfunc="count").fillna(0)

    # Sắp xếp ngành theo trung vị tổng thể tăng dần để tạo dốc địa hình trực quan từ Ngọc Lục Bảo -> Đồng Đỏ -> Đỏ Đô
    sec_order = piv_med.mean(axis=1).sort_values(ascending=True).index.tolist()
    piv_med = piv_med.loc[sec_order]
    piv_cnt = piv_cnt.loc[sec_order]
    years = sorted(piv_med.columns.tolist())
    piv_med = piv_med[years]
    piv_cnt = piv_cnt[years]

    # Xử lý tình huống người dùng lọc chỉ còn 1 ngành hoặc 1 năm (Surface cần lưới >= 2x2)
    if len(sec_order) < 2 or len(years) < 2:
        agg = (
            df.groupby(["year_int", "icb_sector_vi"], as_index=False)
            .agg(med=("composite_risk_score", "median"), n=("ticker", "count"))
            .sort_values("year_int")
        )
        fig_fb = go.Figure(
            go.Scatter3d(
                x=agg["year_int"],
                y=[0] * len(agg),
                z=agg["med"],
                mode="lines+markers+text",
                text=[f"{v:.1f}đ" for v in agg["med"]],
                line=dict(color=PALETTE["copper"], width=5),
                marker=dict(size=8, color=agg["med"], colorscale=EMERALD_COPPER_COLORSCALE, cmin=10, cmax=70),
            )
        )
        fig_fb.update_layout(
            title=dict(
                text=f"Quỹ đạo 3D Ngành đang lọc: {sec_order[0]} (Chọn >= 2 ngành để xem Bề mặt Địa hình 3D đầy đủ)",
                font=dict(size=13.5, color=PALETTE["emerald"]),
            ),
            paper_bgcolor="#FFFFFF",
            height=520,
            scene=dict(
                xaxis=dict(title=dict(text="Năm", font=dict(size=11.5, color=PALETTE["navy"]))),
                yaxis=dict(title=dict(text="Ngành ICB", font=dict(size=11.5, color=PALETTE["navy"])), tickvals=[0], ticktext=[sec_order[0]]),
                zaxis=dict(title=dict(text="Điểm Rủi ro Trung vị (0–100)", font=dict(size=11.5, color=PALETTE["navy"])), range=[0, 85]),
            ),
        )
        return fig_fb

    z_mat = piv_med.ffill(axis=1).bfill(axis=1).fillna(piv_med.values[~np.isnan(piv_med.values)].mean()).values
    y_idx = list(range(len(sec_order)))
    short_secs = [s if len(s) <= 22 else s[:20] + "…" for s in sec_order]

    hover_mat = []
    for i, sec in enumerate(sec_order):
        row_h = []
        for j, yr in enumerate(years):
            val = float(z_mat[i, j])
            cnt = int(piv_cnt.iloc[i, j])
            row_h.append(
                f"<b>{sec}</b><br>Năm tài chính: <b>{yr}</b><br>"
                f"Điểm Rủi ro Trung vị: <b>{val:.1f} / 100</b><br>"
                f"Số doanh nghiệp: {cnt} DN"
            )
        hover_mat.append(row_h)

    # Tìm tự động các điểm nhấn thật trên địa hình để gắn Chú thích 3D
    max_flat = int(np.argmax(z_mat))
    max_i, max_j = divmod(max_flat, z_mat.shape[1])
    min_flat = int(np.argmin(z_mat))
    min_i, min_j = divmod(min_flat, z_mat.shape[1])
    last_j = z_mat.shape[1] - 1
    hot_last_i = int(np.argmax(z_mat[:, last_j]))

    annots_terrain = [
        dict(
            x=years[max_j],
            y=max_i,
            z=float(z_mat[max_i, max_j]),
            text=f"<b>Đỉnh rủi ro cao nhất</b><br>{short_secs[max_i]} ({years[max_j]}: {z_mat[max_i, max_j]:.1f}đ)",
            showarrow=True,
            arrowhead=2,
            arrowcolor=PALETTE["red"],
            ax=22,
            ay=-44,
            font=dict(size=12, color=PALETTE["red"]),
            bgcolor="rgba(255, 241, 242, 0.95)",
            bordercolor=PALETTE["red"],
            borderwidth=1.2,
            borderpad=4,
        ),
        dict(
            x=years[min_j],
            y=min_i,
            z=float(z_mat[min_i, min_j]),
            text=f"<b>Thung lũng an toàn nhất</b><br>{short_secs[min_i]} ({years[min_j]}: {z_mat[min_i, min_j]:.1f}đ)",
            showarrow=True,
            arrowhead=2,
            arrowcolor=PALETTE["green"],
            ax=-26,
            ay=-38,
            font=dict(size=12, color=PALETTE["emerald"]),
            bgcolor="rgba(236, 253, 245, 0.95)",
            bordercolor=PALETTE["green"],
            borderwidth=1.2,
            borderpad=4,
        ),
    ]
    if not (hot_last_i == max_i and last_j == max_j):
        annots_terrain.append(
            dict(
                x=years[last_j],
                y=hot_last_i,
                z=float(z_mat[hot_last_i, last_j]),
                text=f"<b>Điểm nóng {years[last_j]}</b><br>{short_secs[hot_last_i]} ({z_mat[hot_last_i, last_j]:.1f}đ)",
                showarrow=True,
                arrowhead=2,
                arrowcolor=PALETTE["copper"],
                ax=34,
                ay=-28,
                font=dict(size=12, color=PALETTE["copper"]),
                bgcolor="rgba(255, 247, 237, 0.95)",
                bordercolor=PALETTE["copper"],
                borderwidth=1.2,
                borderpad=4,
            )
        )

    fig = go.Figure(
        data=[
            go.Surface(
                x=years,
                y=y_idx,
                z=z_mat,
                text=hover_mat,
                hoverinfo="text",
                colorscale=EMERALD_COPPER_COLORSCALE,
                cmin=12.0,
                cmax=65.0,
                opacity=0.95,
                lighting=dict(ambient=0.68, diffuse=0.80, roughness=0.45, specular=0.25),
                contours=dict(
                    z=dict(show=True, usecolormap=True, highlightcolor="#C2410C", project_z=True),
                ),
                colorbar=dict(
                    title=dict(text="Trung vị<br>Rủi ro (đ)", font=dict(size=11, color=PALETTE["navy"])),
                    thickness=14,
                    len=0.65,
                ),
            )
        ]
    )
    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(
            text=f"Địa hình Rủi ro 3D theo {len(sec_order)} Ngành ICB × {len(years)} Năm ({years[0]}–{years[-1]})",
            font=dict(size=15.5, color=PALETTE["emerald"]),
            x=0.01,
        ),
        paper_bgcolor="#FFFFFF",
        height=600,
        margin=dict(l=10, r=15, t=58, b=20),
        scene=dict(
            xaxis=dict(
                title=dict(text="Năm tài chính", font=dict(size=13, color=PALETTE["navy"])),
                tickvals=years,
                backgroundcolor="#FAF8F5",
                gridcolor="#D1DDD8",
            ),
            yaxis=dict(
                title=dict(text="Ngành ICB (Thấp → Cao)", font=dict(size=13, color=PALETTE["navy"])),
                tickvals=y_idx,
                ticktext=short_secs,
                tickfont=dict(size=11),
                backgroundcolor="#FAF8F5",
                gridcolor="#D1DDD8",
            ),
            zaxis=dict(
                title=dict(text="Điểm Rủi ro Trung vị (0–100)", font=dict(size=13, color=PALETTE["navy"])),
                range=[0, max(float(np.max(z_mat)) + 12.0, 72.0)],
                backgroundcolor="#F0F4F2",
                gridcolor="#D1DDD8",
            ),
            aspectratio=dict(x=1.1, y=1.55, z=0.82),
            camera=dict(eye=dict(x=1.85, y=-1.45, z=1.05)),
            annotations=annots_terrain,
        ),
    )
    return fig


def plot_company_trajectory_3d_animated(df_comp: pd.DataFrame) -> go.Figure:
    """
    Quỹ đạo Pháp chứng 3D Động Đa năm (2018–2025) cho từng Doanh nghiệp.
    Trục X: Doanh thu thuần | Trục Y: LN Sau thuế | Trục Z: Dòng tiền CFO (Tỷ VND).
    Kèm mặt phẳng tham chiếu CFO = 0, chuyển động nối dài từng năm (Play/Pause) & Chú thích 3D.
    """
    df = df_comp.sort_values("year").dropna(subset=["net_revenue", "net_income", "cfo"]).copy()
    if df.empty:
        fig_empty = go.Figure()
        fig_empty.update_layout(title="Chưa đủ số liệu Doanh thu / LNST / CFO để dựng Quỹ đạo 3D", height=440)
        return fig_empty

    ticker = str(df["ticker"].iloc[-1])
    years = df["year"].astype(int).tolist()
    xs = df["net_revenue"].astype(float).tolist()
    ys = df["net_income"].astype(float).tolist()
    zs = df["cfo"].astype(float).tolist()
    scores = [float(v) if pd.notna(v) else np.nan for v in df["composite_risk_score"]]

    pt_colors = [
        "#4B635B" if pd.isna(sc) else (PALETTE["red"] if sc >= 65.0 else (PALETTE["copper"] if sc >= 40.0 else PALETTE["green"]))
        for sc in scores
    ]
    hovers = [
        (
            f"<b>{ticker} — Năm {yr}</b><br>"
            f"Doanh thu thuần: <b>{x:,.1f} tỷ</b><br>"
            f"LN Sau thuế (LNST): <b>{y:,.1f} tỷ</b><br>"
            f"Dòng tiền HĐKD (CFO): <b>{z:,.1f} tỷ</b><br>"
            f"Composite Risk Score: <b>{'N/A (Năm gốc)' if pd.isna(sc) else f'{sc:.1f} / 100'}</b>"
        )
        for yr, x, y, z, sc in zip(years, xs, ys, zs, scores)
    ]

    # Tính biên trục rộng rãi và mặt phẳng tham chiếu CFO = 0 ("Mặt nước dòng tiền")
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    z_min, z_max = min(zs + [0.0]), max(zs + [0.0])
    x_pad = max((x_max - x_min) * 0.16, abs(x_max) * 0.12, 10.0)
    y_pad = max((y_max - y_min) * 0.18, abs(y_max) * 0.14, 10.0)
    z_pad = max((z_max - z_min) * 0.20, abs(z_max) * 0.14, 10.0)
    xr = [x_min - x_pad, x_max + x_pad]
    yr_rng = [y_min - y_pad, y_max + y_pad]
    zr = [z_min - z_pad, z_max + z_pad]

    waterline_surface = go.Surface(
        x=[xr[0], xr[1]],
        y=[yr_rng[0], yr_rng[1]],
        z=[[0.0, 0.0], [0.0, 0.0]],
        colorscale=[[0.0, "#FDBA74"], [1.0, "#FDBA74"]],
        opacity=0.18,
        showscale=False,
        name="Mặt phẳng CFO = 0 (Dưới mặt này = Dòng tiền âm)",
        hoverinfo="skip",
        showlegend=True,
    )

    def _build_cum_traces(end_i: int) -> list[Any]:
        sl = slice(0, end_i + 1)
        tr_line = go.Scatter3d(
            x=xs[sl],
            y=ys[sl],
            z=zs[sl],
            mode="lines+markers+text",
            name=f"Quỹ đạo {ticker} ({years[0]}–{years[end_i]})",
            text=[str(y) for y in years[sl]],
            textposition="top center",
            textfont=dict(size=10.5, color=PALETTE["navy"]),
            line=dict(color=PALETTE["emerald"], width=5.5),
            marker=dict(
                size=[11 if k == end_i else 8 for k in range(end_i + 1)],
                color=pt_colors[sl],
                line=dict(width=1.5, color="#FFFFFF"),
            ),
            hovertext=hovers[sl],
            hovertemplate="%{hovertext}<extra></extra>",
        )
        tr_head = go.Scatter3d(
            x=[xs[end_i]],
            y=[ys[end_i]],
            z=[zs[end_i]],
            mode="markers",
            name=f"Mốc năm {years[end_i]}",
            marker=dict(size=13, symbol="diamond", color=pt_colors[end_i], line=dict(width=2, color="#132A23")),
            hovertext=[hovers[end_i]],
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
        )
        return [waterline_surface, tr_line, tr_head]

    # Chú thích 3D tự động cho các mốc quan trọng của doanh nghiệp
    annots_comp: list[dict[str, Any]] = [
        dict(
            x=xr[0] + (xr[1] - xr[0]) * 0.14,
            y=yr_rng[1] - (yr_rng[1] - yr_rng[0]) * 0.10,
            z=0.0,
            text="<b>Mặt phẳng CFO = 0</b><br>(Dưới mặt này = Dòng tiền KD âm)",
            showarrow=False,
            font=dict(size=10, color=PALETTE["copper"]),
            bgcolor="rgba(255, 247, 237, 0.88)",
            bordercolor=PALETTE["copper"],
            borderwidth=1,
            borderpad=3,
        )
    ]

    valid_sc_idx = [i for i, sc in enumerate(scores) if pd.notna(sc)]
    pinned_idx: set[int] = set()
    if valid_sc_idx:
        peak_i = max(valid_sc_idx, key=lambda i: scores[i])
        peak_sc = scores[peak_i]
        p_col = PALETTE["red"] if peak_sc >= 65 else (PALETTE["copper"] if peak_sc >= 40 else PALETTE["green"])
        p_bg = "rgba(255, 241, 242, 0.94)" if peak_sc >= 65 else ("rgba(255, 247, 237, 0.94)" if peak_sc >= 40 else "rgba(236, 253, 245, 0.94)")
        annots_comp.append(
            dict(
                x=xs[peak_i],
                y=ys[peak_i],
                z=zs[peak_i],
                text=f"<b>Đỉnh rủi ro {years[peak_i]}</b><br>{peak_sc:.1f}đ (CFO: {zs[peak_i]:,.0f} tỷ)",
                showarrow=True,
                arrowhead=2,
                arrowcolor=p_col,
                ax=28,
                ay=-36,
                font=dict(size=12, color=p_col),
                bgcolor=p_bg,
                bordercolor=p_col,
                borderwidth=1.2,
                borderpad=4,
            )
        )
        pinned_idx.add(peak_i)

    # Nếu có năm phân kỳ LNST > 0 nhưng CFO < 0 khác đỉnh rủi ro, ghim thêm cảnh báo phân kỳ!
    div_idx = [i for i in range(len(years)) if ys[i] > 0 and zs[i] < 0 and i not in pinned_idx]
    if div_idx:
        di = div_idx[-1]
        annots_comp.append(
            dict(
                x=xs[di],
                y=ys[di],
                z=zs[di],
                text=f"<b>Phân kỳ {years[di]}</b><br>LNST +{ys[di]:,.0f} tỷ / CFO {zs[di]:,.0f} tỷ",
                showarrow=True,
                arrowhead=2,
                arrowcolor=PALETTE["copper"],
                ax=-32,
                ay=30,
                font=dict(size=11.5, color=PALETTE["copper"]),
                bgcolor="rgba(255, 247, 237, 0.95)",
                bordercolor=PALETTE["copper"],
                borderwidth=1.2,
                borderpad=4,
            )
        )
        pinned_idx.add(di)

    last_i = len(years) - 1
    if last_i not in pinned_idx:
        sc_last = scores[last_i]
        sc_txt = f"{sc_last:.1f}đ" if pd.notna(sc_last) else "N/A"
        annots_comp.append(
            dict(
                x=xs[last_i],
                y=ys[last_i],
                z=zs[last_i],
                text=f"<b>Năm mới nhất {years[last_i]}</b><br>Điểm rủi ro: {sc_txt}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=PALETTE["emerald"],
                ax=24,
                ay=26,
                font=dict(size=12, color=PALETTE["emerald"]),
                bgcolor="rgba(240, 253, 250, 0.95)",
                bordercolor=PALETTE["emerald"],
                borderwidth=1.2,
                borderpad=4,
            )
        )

    frames = [
        go.Frame(name=str(years[k]), data=_build_cum_traces(k))
        for k in range(len(years))
    ]
    fig = go.Figure(data=_build_cum_traces(last_i), frames=frames)

    updatemenus = []
    sliders = []
    if len(years) > 1:
        updatemenus = [
            dict(
                type="buttons",
                direction="left",
                x=0.01,
                y=1.08,
                xanchor="left",
                yanchor="top",
                bgcolor="#FFFFFF",
                bordercolor=PALETTE["border"],
                borderwidth=1,
                font=dict(size=13, color=PALETTE["emerald"]),
                buttons=[
                    dict(
                        label=f"Chiếu quỹ đạo ({years[0]}→{years[-1]})",
                        method="animate",
                        args=[
                            None,
                            {"frame": {"duration": 780, "redraw": True}, "fromcurrent": False, "transition": {"duration": 0}},
                        ],
                    ),
                    dict(
                        label="Tạm dừng",
                        method="animate",
                        args=[
                            [None],
                            {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}},
                        ],
                    ),
                ],
            )
        ]
        sliders = [
            dict(
                active=last_i,
                yanchor="top",
                xanchor="left",
                currentvalue=dict(
                    prefix="Quỹ đạo đến năm: ",
                    visible=True,
                    xanchor="right",
                    font=dict(size=11.5, color=PALETTE["emerald"]),
                ),
                pad=dict(b=6, t=8),
                len=0.92,
                x=0.04,
                y=0.03,
                bgcolor="#F0F4F2",
                activebgcolor=PALETTE["copper"],
                bordercolor=PALETTE["border"],
                steps=[
                    dict(
                        method="animate",
                        label=str(yr),
                        args=[
                            [str(yr)],
                            {"mode": "immediate", "frame": {"duration": 450, "redraw": True}, "transition": {"duration": 0}},
                        ],
                    )
                    for yr in years
                ],
            )
        ]

    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(
            text=f"Quỹ đạo Pháp chứng 3D Động: {ticker} ({years[0]}–{years[-1]}) — Doanh thu × LNST × Dòng tiền CFO",
            font=dict(size=15.5, color=PALETTE["emerald"]),
            x=0.01,
            y=0.98,
        ),
        paper_bgcolor="#FFFFFF",
        height=570,
        margin=dict(l=10, r=15, t=78, b=36),
        legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="right", x=0.98, font=dict(size=12.5)),
        updatemenus=updatemenus,
        sliders=sliders,
        scene=dict(
            uirevision=f"finaudit_3d_traj_{ticker}",
            xaxis=dict(title=dict(text="Doanh thu thuần (Tỷ VND)", font=dict(size=13, color=PALETTE["navy"])), range=xr, backgroundcolor="#FAF8F5", gridcolor="#D1DDD8"),
            yaxis=dict(title=dict(text="LN Sau thuế — LNST (Tỷ VND)", font=dict(size=13, color=PALETTE["navy"])), range=yr_rng, backgroundcolor="#FAF8F5", gridcolor="#D1DDD8"),
            zaxis=dict(title=dict(text="Dòng tiền HĐKD — CFO (Tỷ VND)", font=dict(size=13, color=PALETTE["navy"])), range=zr, backgroundcolor="#F0F4F2", gridcolor="#D1DDD8", zerolinecolor=PALETTE["copper"]),
            camera=dict(eye=dict(x=1.55, y=-1.55, z=0.95)),
            annotations=annots_comp,
        ),
    )
    return fig
