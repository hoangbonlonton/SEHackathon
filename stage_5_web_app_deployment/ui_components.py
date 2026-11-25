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

import base64
from functools import lru_cache
from html import escape
from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


@lru_cache(maxsize=4)
def _load_asset_b64(filename: str) -> str:
    """Đọc ảnh nền nghệ thuật cục bộ thành chuỗi base64 (tải 1 lần, không phụ thuộc mạng)."""
    p = ASSETS_DIR / filename
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode("ascii")


def translate_altman_zone(zone: Any) -> str:
    """Việt hóa hoàn toàn phân vùng sức khỏe tài chính Altman để người dùng doanh nghiệp đọc hiểu ngay."""
    z = str(zone or "").strip().lower()
    if "distress" in z:
        return "Vùng Nguy hiểm"
    if "grey" in z or "gray" in z:
        return "Vùng Cần theo dõi"
    if "safe" in z:
        return "Vùng An toàn"
    return str(zone or "Chưa phân loại")

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
        "Liên kết gốc": "https://mof.gov.vn/",
        "Tên cổng": "Bộ Tài chính (mof.gov.vn)",
    },
    {
        "Số hiệu Văn bản": "Thông tư 200/2014/TT-BTC",
        "Trích yếu nội dung": "Chế độ kế toán doanh nghiệp lịch sử (Điều 18 TK 131, Điều 21 TK 138, Điều 45 TK 229, Điều 46 TK 241, Điều 51 TK 331, Điều 79 TK 511)",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "22/12/2014",
        "Hiệu lực áp dụng": "01/01/2015 – 31/12/2025",
        "Trạng thái": "Áp dụng BCTC lịch sử ≤ 2025",
        "Liên kết gốc": "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=200/2014/TT-BTC",
        "Tên cổng": "CSDL Quốc gia VBPL",
    },
    {
        "Số hiệu Văn bản": "Thông tư 48/2019/TT-BTC & TT 24/2022/TT-BTC",
        "Trích yếu nội dung": "Trích lập dự phòng làm cơ sở tính chi phí được trừ thuế TNDN (Khoản 1 Điều 1, Điều 4 NRV, Điều 6 tuổi nợ 30–50–70–100%)",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "08/08/2019 & 07/04/2022",
        "Hiệu lực áp dụng": "Đang thi hành",
        "Trạng thái": "Còn hiệu lực (Thuế TNDN)",
        "Liên kết gốc": "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=48/2019/TT-BTC",
        "Tên cổng": "CSDL Quốc gia VBPL",
    },
    {
        "Số hiệu Văn bản": "VSA 240 (Thông tư 214/2012/TT-BTC)",
        "Trích yếu nội dung": "Trách nhiệm của kiểm toán viên liên quan đến gian lận BCTC (Đoạn 12 Hoài nghi, Đoạn 26 Doanh thu, Đoạn 31–33 Khống chế kiểm soát)",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "06/12/2012",
        "Hiệu lực áp dụng": "Từ 01/01/2014",
        "Trạng thái": "Còn hiệu lực",
        "Liên kết gốc": "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=214/2012/TT-BTC",
        "Tên cổng": "CSDL Quốc gia VBPL",
    },
    {
        "Số hiệu Văn bản": "VAS 14 (QĐ 149/2001) & VAS 26 (QĐ 234/2003)",
        "Trích yếu nội dung": "Chuẩn mực Doanh thu và thu nhập khác (5 điều kiện Đoạn 10) & Thông tin về các bên liên quan trên B09-DN",
        "Cơ quan ban hành": "Bộ Tài chính",
        "Ngày ban hành": "31/12/2001 & 31/12/2003",
        "Hiệu lực áp dụng": "Đang thi hành",
        "Trạng thái": "Còn hiệu lực",
        "Liên kết gốc": "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=149/2001/Q%C4%90-BTC",
        "Tên cổng": "CSDL Quốc gia VBPL",
    },
]

# Logo Vector Chính thức FinAudit AI (Khiên Pháp chứng + Cột BCTC + Đường kiểm định Vàng Đồng)
BRAND_EMBLEM_SVG = (
    '<svg width="34" height="34" viewBox="0 0 48 48" fill="none" '
    'style="vertical-align:middle;flex-shrink:0;" aria-hidden="true">'
    '<defs>'
    '<linearGradient id="faShieldG" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">'
    '<stop offset="0%" stop-color="#0A5F4E"/><stop offset="100%" stop-color="#042F25"/>'
    '</linearGradient>'
    '<linearGradient id="faCopperG" x1="6" y1="4" x2="42" y2="44" gradientUnits="userSpaceOnUse">'
    '<stop offset="0%" stop-color="#FDE68A"/><stop offset="55%" stop-color="#FDBA74"/><stop offset="100%" stop-color="#C2410C"/>'
    '</linearGradient>'
    '</defs>'
    '<path d="M24 3L6 10.5V23.2C6 34.4 13.5 43.2 24 46C34.5 43.2 42 34.4 42 23.2V10.5L24 3Z" '
    'fill="url(#faShieldG)" stroke="url(#faCopperG)" stroke-width="2.5"/>'
    '<rect x="14" y="25" width="4.2" height="9" rx="1.4" fill="#A7F3D0"/>'
    '<rect x="21.5" y="20" width="4.2" height="14" rx="1.4" fill="#FDE68A"/>'
    '<rect x="29" y="15" width="4.2" height="19" rx="1.4" fill="#FDBA74"/>'
    '<path d="M13 21.5L20 15.5L25.5 18.5L34.5 11.5" stroke="#FFFFFF" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="34.5" cy="11.5" r="2.2" fill="#FDE68A"/></svg>'
)

PLOTLY_BASE_FONT = dict(family="Roboto, Segoe UI, Arial, sans-serif", size=14.8, color=PALETTE["navy"])


def format_rag_markdown_to_html(raw_text: str) -> str:
    """Chuyển đổi sạch chuỗi Markdown (**, `, danh sách, tiêu đề) sang HTML chuẩn, xóa 100% dấu ** thô."""
    if not raw_text:
        return ""
    lines = raw_text.strip().splitlines()
    out_lines: list[str] = []
    for line in lines:
        s = escape(line.strip())
        if not s:
            continue
        # Bỏ ký tự tiêu đề # ở đầu dòng và in đậm
        s = re.sub(r"^#{1,4}\s*(.+)$", r"<strong style='color:#064E3B;font-size:1.03em;'>\1</strong>", s)
        # Chuyển **in đậm** -> <strong> và dọn sạch dấu ** lẻ nếu đoạn trích bị cắt giữa chừng
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = s.replace("**", "")
        # Chuyển `code` -> <code>
        s = re.sub(
            r"`([^`]+)`",
            r"<code style='background:#F0F4F2;color:#064E3B;padding:1px 6px;border-radius:4px;font-family:JetBrains Mono,monospace;font-size:0.93em;'>\1</code>",
            s,
        )
        # Gạch đầu dòng đẹp
        if s.startswith("- "):
            s = "• " + s[2:]
        out_lines.append(s)
    return "<br/>".join(out_lines)


def trim_excerpt_clean(raw_text: str, max_len: int = 340) -> tuple[str, bool]:
    """Cắt đoạn trích dẫn gọn tại ranh giới từ/câu, không cắt cụt giữa từ hay để lại dấu ba chấm thô."""
    txt = (raw_text or "").strip()
    if len(txt) <= max_len:
        return txt, False
    cut = txt[:max_len].rsplit(" ", 1)[0].rstrip(" ,;:-*#•|(")
    if not cut:
        cut = txt[:max_len].rstrip(" ,;:-*#•|(")
    return cut, True


MODULE_FOLDER_COLORS = [
    "#064E3B",  # 1. Thị trường (Ngọc Lục Bảo Đậm)
    "#C2410C",  # 2. Hồ sơ 360° (Đồng Đỏ)
    "#0F766E",  # 3. Thẩm định BCTC (Xanh Lam Đậm)
    "#B45309",  # 4. Luật VAS & PDF (Hổ Phách Pháp lý)
    "#047857",  # 5. Kiểm chứng ESG (Xanh Thông Quản trị)
]

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
    hero_b64 = _load_asset_b64("hero_portal_banner.jpg")
    legal_b64 = _load_asset_b64("legal_portal_banner.jpg")
    hero_bg_css = (
        f"linear-gradient(180deg, rgba(4,47,37,0.34) 0%, rgba(6,78,59,0.44) 100%), url('data:image/jpeg;base64,{hero_b64}')"
        if hero_b64
        else "linear-gradient(135deg, #043628 0%, #064E3B 55%, #0F766E 100%)"
    )
    legal_bg_css = (
        f"linear-gradient(180deg, rgba(124,45,18,0.36) 0%, rgba(154,52,18,0.46) 100%), url('data:image/jpeg;base64,{legal_b64}')"
        if legal_b64
        else "linear-gradient(135deg, #9A3412 0%, #B45309 100%)"
    )

    css_template = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@600;700;800&family=Merriweather:wght@700;900&family=Roboto:ital,wght@0,400;0,500;0,700;0,900;1,400&display=swap');

        :root {
            --fa-primary: #064E3B;
            --fa-secondary: #0F766E;
            --fa-accent: #C2410C;
            --fa-accent-soft: #FFF7ED;
            --fa-gold: #F59E0B;
            --fa-gold-soft: #FEF3C7;
            --fa-bg: #F2F5F4;
            --fa-ink: #132A23;
            --fa-card: #FFFFFF;
            --fa-muted-bg: #EBF0EE;
            --fa-muted-fg: #4B635B;
            --fa-border: #C9D8D2;
            --fa-green: #059669;
            --fa-amber: #B45309;
            --fa-red: #BE123C;
            --fa-font-brand: 'Merriweather', Georgia, serif;
            --fa-font-head: 'Roboto', 'Segoe UI', Arial, sans-serif;
            --fa-font-body: 'Roboto', 'Segoe UI', Arial, sans-serif;
            --fa-font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
        }

        /* Thẻ Đánh giá Rủi ro Khoa học (Hạng A / B / C + Thanh phân đoạn 0-100) — Góc cạnh kiến trúc có chiều sâu */
        .fa-rating-card {
            background: #FFFFFF;
            border: 1.5px solid var(--fa-border);
            border-radius: 5px;
            padding: 20px 22px;
            box-shadow: 0 2px 5px rgba(6, 78, 59, 0.05), 0 8px 22px rgba(6, 78, 59, 0.07);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 262px;
        }
        .fa-rating-grade {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 13px;
            border-radius: 4px;
            font-size: 14.2px;
            font-weight: 800;
            letter-spacing: 0.4px;
            text-transform: uppercase;
        }
        .fa-rating-big {
            font-family: var(--fa-font-mono);
            font-size: clamp(42px, 3.8vw, 52px);
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -1px;
        }
        .fa-rating-denom {
            font-family: var(--fa-font-head);
            font-size: 16.5px;
            font-weight: 700;
            color: var(--fa-muted-fg);
            margin-left: 7px;
        }
        .fa-seg-track {
            position: relative;
            display: grid;
            grid-template-columns: 40fr 25fr 35fr;
            gap: 3px;
            height: 12px;
            border-radius: 3px;
            margin: 14px 0 7px;
        }
        .fa-seg-a { background: #10B981; border-radius: 3px 0 0 3px; opacity: 0.88; }
        .fa-seg-b { background: #F59E0B; opacity: 0.88; }
        .fa-seg-c { background: #E11D48; border-radius: 0 3px 3px 0; opacity: 0.88; }
        .fa-seg-pin {
            position: absolute;
            top: -5px;
            width: 7px;
            height: 22px;
            background: #132A23;
            border: 2px solid #FFFFFF;
            border-radius: 2px;
            transform: translateX(-50%);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
        }
        .fa-insight-strip {
            padding: 13px 18px;
            border-radius: 5px;
            font-size: 16.2px;
            line-height: 1.62;
            margin-bottom: 13px;
            border: 1px solid #C9D8D2;
            border-left-width: 4.5px;
            background: #FFFFFF;
            color: var(--fa-ink);
            box-shadow: 0 2px 6px rgba(6, 78, 59, 0.05);
        }
        .fa-peer-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 15.8px;
        }
        .fa-peer-table th {
            background: #EDF3F1;
            color: #064E3B;
            font-weight: 800;
            text-align: left;
            padding: 12px 14px;
            border-bottom: 2px solid #C9D8D2;
            font-size: 14.8px;
        }
        .fa-peer-table td {
            padding: 12px 14px;
            border-bottom: 1px solid #E2EAE7;
            vertical-align: middle;
        }
        .fa-peer-table tr:hover td {
            background: #F4F9F7;
        }
        .fa-micro-guide {
            font-size: 15.6px;
            color: var(--fa-muted-fg);
            margin: -3px 0 11px 0;
            line-height: 1.54;
        }

        html, body, .stApp {
            background-color: var(--fa-bg);
            color: var(--fa-ink);
            font-family: var(--fa-font-body);
            font-size: clamp(16.8px, 1.18vw, 18.2px);
            line-height: 1.65;
        }
        h1, h2, h3, h4 {
            font-family: var(--fa-font-head) !important;
            letter-spacing: -0.15px;
        }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            font-size: clamp(16.5px, 1.15vw, 17.8px);
            line-height: 1.68;
        }
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] p {
            font-size: 16.2px !important;
            font-weight: 700 !important;
            color: var(--fa-ink) !important;
        }
        .stRadio label p,
        .stCheckbox label p {
            font-size: 16px !important;
            font-weight: 500;
            line-height: 1.5;
        }
        .stSelectbox div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"],
        .stTextInput input {
            font-size: 16.2px !important;
            font-family: var(--fa-font-body) !important;
            border-radius: 4px !important;
        }
        [data-testid="stCaptionContainer"] p {
            font-size: 15px !important;
            color: var(--fa-muted-fg);
            line-height: 1.55;
        }
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid var(--fa-border);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 0.85rem !important;
            padding-bottom: 1.2rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] .stRadio label p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            font-size: 15.5px !important;
        }
        /* Mở rộng không gian hiển thị chuẩn cổng thông tin — chừa khoảng an toàn cho thanh Toolbar Streamlit Cloud */
        [data-testid="stHeader"] {
            background: rgba(242, 245, 244, 0.92) !important;
            backdrop-filter: blur(6px);
            border-bottom: 1px solid rgba(201, 216, 210, 0.6);
        }
        .main .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-top: 3.85rem !important;
            padding-bottom: 2.2rem !important;
            padding-left: clamp(1rem, 2.2vw, 2.2rem) !important;
            padding-right: clamp(1rem, 2.2vw, 2.2rem) !important;
            max-width: 100% !important;
        }

        /* Hiệu ứng Pha 2 Màu cho Tiêu đề (Dual-Tone Typography) */
        .fa-dual-gold {
            background: linear-gradient(90deg, #FDE68A 0%, #FDBA74 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            color: #FDE68A;
            font-weight: 900;
        }
        .fa-sec-accent {
            color: var(--fa-accent);
            font-weight: 800;
        }

        /* Đầu trang Cổng Thông tin Nghiêm chỉnh (lấy cảm hứng dichvucong.gov.vn) — Góc vuông vức sắc sảo */
        .fa-sticky-bar {
            background: #FFFFFF;
            color: var(--fa-ink);
            border: 1px solid var(--fa-border);
            border-top: 4px solid var(--fa-primary);
            border-radius: 5px 5px 0 0;
            padding: 14px 22px;
            margin-bottom: 0;
            box-shadow: 0 2px 8px rgba(6, 78, 59, 0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .fa-sticky-left {
            display: flex;
            align-items: center;
            gap: 14px;
            flex-wrap: wrap;
        }
        .fa-masthead-title {
            font-family: var(--fa-font-brand);
            font-size: clamp(20px, 1.9vw, 25px);
            font-weight: 900;
            color: var(--fa-primary);
            letter-spacing: 0.25px;
            line-height: 1.25;
        }
        .fa-masthead-title span {
            color: var(--fa-accent);
        }
        .fa-masthead-sub {
            font-family: var(--fa-font-body);
            font-size: 14.8px;
            font-style: italic;
            color: var(--fa-muted-fg);
            margin-top: 3px;
        }
        .fa-sticky-tag {
            font-size: 14.2px;
            font-weight: 700;
            padding: 6px 13px;
            border-radius: 4px;
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            border-left: 3px solid #064E3B;
            color: #064E3B;
            white-space: nowrap;
        }
        .fa-sticky-role {
            font-size: 14.2px;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 4px;
            background: #FFF7ED;
            color: #C2410C;
            border: 1px solid #FDBA74;
            border-left: 3px solid #C2410C;
            white-space: nowrap;
        }

        /* BANNER NGHỆ THUẬT TRANG CHỦ (NỀN TRỐNG ĐỒNG + HOA SEN NGỌC LỤC BẢO) */
        .st-key-home_portal_hero {
            background-image: __HERO_BG_CSS__ !important;
            background-size: cover !important;
            background-position: center !important;
            border: 1.5px solid #064E3B !important;
            border-bottom: 4px solid #C2410C !important;
            border-radius: 6px !important;
            padding: 26px 30px 24px !important;
            margin-bottom: 16px !important;
            box-shadow: 0 4px 10px rgba(6, 78, 59, 0.12), 0 12px 28px rgba(6, 78, 59, 0.16) !important;
        }
        .fa-portal-hero-title {
            text-align: center;
            color: #FFFFFF;
            font-family: var(--fa-font-brand);
            font-size: clamp(25px, 2.4vw, 33px);
            font-weight: 900;
            line-height: 1.32;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.30);
            margin: 0 0 8px 0;
        }
        .fa-portal-hero-sub {
            text-align: center;
            color: #ECFDF5;
            font-size: 16.8px;
            font-weight: 500;
            margin: 0 0 16px 0;
            text-shadow: 0 1px 6px rgba(0, 0, 0, 0.24);
        }

        /* 3 Nút Lối vào Đầu vào trên Banner Trang chủ (Lấy cảm hứng 3 ô vàng trên dichvucong.gov.vn) */
        .st-key-home_entry_0 button,
        .st-key-home_entry_1 button,
        .st-key-home_entry_2 button {
            min-height: 64px !important;
            border-radius: 5px !important;
            border: 2px solid #FDE68A !important;
            background-image: linear-gradient(112deg, #C2410C 0%, #EA580C 38%, #FEF3C7 62%, #FDE68A 100%) !important;
            background-size: 260% 100% !important;
            background-position: 100% 0 !important;
            color: #132A23 !important;
            font-family: var(--fa-font-head) !important;
            font-size: 16.2px !important;
            font-weight: 800 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.20) !important;
            transition: background-position 0.55s cubic-bezier(0.22, 1, 0.36, 1), color 0.35s ease, transform 0.22s ease, border-color 0.35s ease !important;
        }
        .st-key-home_entry_0 button *,
        .st-key-home_entry_1 button *,
        .st-key-home_entry_2 button * {
            color: inherit !important;
        }
        .st-key-home_entry_0 button:hover,
        .st-key-home_entry_1 button:hover,
        .st-key-home_entry_2 button:hover {
            background-position: 0% 0 !important;
            color: #FFFFFF !important;
            border-color: #FFFFFF !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.28) !important;
        }

        /* BANNER NGHỆ THUẬT TRANG 4 (CỘT DỌC BÊN TRÁI — CỔNG PHÁP LÝ NỀN ĐỒNG ĐỎ HOA SEN) */
        .st-key-legal_portal_hero {
            background-image: __LEGAL_BG_CSS__ !important;
            background-size: cover !important;
            background-position: center !important;
            border: 1.5px solid #9A3412 !important;
            border-bottom: 4px solid #064E3B !important;
            border-radius: 5px !important;
            padding: 20px 18px 18px !important;
            margin-bottom: 10px !important;
            box-shadow: 0 4px 12px rgba(154, 52, 18, 0.16), 0 10px 24px rgba(154, 52, 18, 0.14) !important;
        }
        .fa-legal-rail-title {
            color: #FFFFFF;
            font-family: var(--fa-font-brand);
            font-size: clamp(20px, 1.75vw, 24px);
            font-weight: 900;
            line-height: 1.32;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.30);
            margin: 0 0 8px 0;
        }
        .fa-legal-rail-sub {
            color: #FFF7ED;
            font-size: 15.2px;
            line-height: 1.54;
            margin: 0;
            text-shadow: 0 1px 6px rgba(0, 0, 0, 0.25);
        }

        /* 3 Đầu mục Hàng dọc (1, 2, 3) dưới Banner Trợ lý Pháp lý (Kiểu bố cục Gemini) */
        .st-key-m4_nav_0 button,
        .st-key-m4_nav_1 button,
        .st-key-m4_nav_2 button {
            justify-content: flex-start !important;
            text-align: left !important;
            min-height: 62px !important;
            border-radius: 5px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            padding: 12px 16px !important;
            background-image: linear-gradient(112deg, #064E3B 0%, #0F766E 42%, #FFFFFF 58%, #FFFFFF 100%) !important;
            background-size: 250% 100% !important;
            background-position: 100% 0 !important;
            border: 1.5px solid #C9D8D2 !important;
            border-left: 4.5px solid #064E3B !important;
            color: #132A23 !important;
            box-shadow: 0 2px 6px rgba(6, 78, 59, 0.05) !important;
            transition: background-position 0.52s cubic-bezier(0.22, 1, 0.36, 1),
                        color 0.35s ease,
                        border-color 0.35s ease,
                        transform 0.22s ease,
                        box-shadow 0.35s ease !important;
        }
        .st-key-m4_nav_1 button {
            border-left-color: #C2410C !important;
            background-image: linear-gradient(112deg, #C2410C 0%, #EA580C 42%, #FFFFFF 58%, #FFFFFF 100%) !important;
        }
        .st-key-m4_nav_2 button {
            border-left-color: #0F766E !important;
            background-image: linear-gradient(112deg, #0F766E 0%, #0D9488 42%, #FFFFFF 58%, #FFFFFF 100%) !important;
        }
        .st-key-m4_nav_0 button *,
        .st-key-m4_nav_1 button *,
        .st-key-m4_nav_2 button * {
            color: inherit !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            text-align: left !important;
        }
        .st-key-m4_nav_0 button:hover,
        .st-key-m4_nav_0 button[kind="primary"],
        .st-key-m4_nav_0 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #064E3B 0%, #0A684F 50%, #0F766E 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important;
            border-color: #064E3B !important;
            transform: translateX(3px);
            box-shadow: 0 5px 15px rgba(6, 78, 59, 0.24) !important;
        }
        .st-key-m4_nav_1 button:hover,
        .st-key-m4_nav_1 button[kind="primary"],
        .st-key-m4_nav_1 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #C2410C 0%, #EA580C 50%, #9A3412 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important;
            border-color: #C2410C !important;
            transform: translateX(3px);
            box-shadow: 0 5px 15px rgba(194, 65, 12, 0.25) !important;
        }
        .st-key-m4_nav_2 button:hover,
        .st-key-m4_nav_2 button[kind="primary"],
        .st-key-m4_nav_2 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #0F766E 0%, #0D9488 50%, #115E59 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important;
            border-color: #0F766E !important;
            transform: translateX(3px);
            box-shadow: 0 5px 15px rgba(15, 118, 110, 0.24) !important;
        }

        /* Lưới 2 Cột Đối tượng Sử dụng (kiểu CÔNG DÂN | DOANH NGHIỆP của dichvucong.gov.vn) */
        .fa-portal-col-head {
            text-align: center;
            font-family: var(--fa-font-head);
            font-size: 19px;
            font-weight: 900;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            padding-bottom: 8px;
            margin: 4px 0 12px 0;
        }
        .st-key-role_link_0 button, .st-key-role_link_1 button, .st-key-role_link_2 button,
        .st-key-role_link_3 button, .st-key-role_link_4 button, .st-key-role_link_5 button {
            justify-content: flex-start !important;
            text-align: left !important;
            min-height: 52px !important;
            background-image: linear-gradient(110deg, #064E3B 0%, #0F766E 36%, #F4F7F6 60%, #F4F7F6 100%) !important;
            background-size: 260% 100% !important;
            background-position: 100% 0 !important;
            border: 1px solid #D9E4DF !important;
            border-left: 4px solid #064E3B !important;
            border-radius: 4px !important;
            color: #132A23 !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            padding: 10px 16px !important;
            transition: background-position 0.52s cubic-bezier(0.22, 1, 0.36, 1), color 0.35s ease, transform 0.2s ease !important;
        }
        .st-key-role_link_3 button, .st-key-role_link_4 button, .st-key-role_link_5 button {
            background-image: linear-gradient(110deg, #C2410C 0%, #EA580C 36%, #FDF6F0 60%, #FDF6F0 100%) !important;
            border-left-color: #C2410C !important;
        }
        .st-key-role_link_0 button *, .st-key-role_link_1 button *, .st-key-role_link_2 button *,
        .st-key-role_link_3 button *, .st-key-role_link_4 button *, .st-key-role_link_5 button * {
            color: inherit !important;
        }
        .st-key-role_link_0 button:hover, .st-key-role_link_1 button:hover, .st-key-role_link_2 button:hover,
        .st-key-role_link_3 button:hover, .st-key-role_link_4 button:hover, .st-key-role_link_5 button:hover {
            background-position: 0% 0 !important;
            color: #FFFFFF !important;
            transform: translateX(3px);
        }

        /* Sơ đồ Quy trình 3 Bước cho Trang 3 (Thẩm định BCTC) */
        .fa-wizard-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-bottom: 16px;
        }
        .fa-wizard-step {
            background: #FFFFFF;
            border: 1.5px solid var(--fa-border);
            border-top: 4px solid var(--fa-secondary);
            border-radius: 5px;
            padding: 16px 18px;
            box-shadow: 0 2px 6px rgba(6, 78, 59, 0.05), 0 6px 16px rgba(6, 78, 59, 0.05);
        }
        .fa-wizard-num {
            display: inline-block;
            background: #0F766E;
            color: #FFFFFF;
            font-family: var(--fa-font-mono);
            font-size: 13.5px;
            font-weight: 800;
            padding: 3px 11px;
            border-radius: 3px;
            margin-bottom: 7px;
        }
        .fa-wizard-title {
            font-size: 17.5px;
            font-weight: 800;
            color: var(--fa-ink);
            margin-bottom: 5px;
        }
        .fa-wizard-desc {
            font-size: 15.2px;
            color: var(--fa-muted-fg);
            line-height: 1.55;
        }

        /* Banner Phụ Gọn (chỉ dùng cho các trang chuyên sâu khi cần tiêu đề ngắn) */
        .fa-hero {
            background: linear-gradient(135deg, #064E3B 0%, #0A5F4E 56%, #0F766E 100%);
            color: #FFFFFF;
            padding: clamp(16px, 1.8vw, 22px) clamp(20px, 2.2vw, 26px);
            border-radius: 5px;
            border-bottom: 4px solid var(--fa-accent);
            margin-bottom: 14px;
            box-shadow: 0 4px 16px rgba(6, 78, 59, 0.12);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .fa-hero-kicker {
            font-size: 13px;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: #A7F3D0;
            font-weight: 700;
            margin-bottom: 3px;
        }
        .fa-hero h1 {
            margin: 0;
            font-family: var(--fa-font-head) !important;
            font-size: clamp(23px, 2.3vw, 30px);
            font-weight: 900;
            color: #FFFFFF;
            line-height: 1.28;
        }
        .fa-hero p {
            margin: 5px 0 0 0;
            font-size: 16.2px;
            color: #E6F4F1;
            line-height: 1.55;
        }
        .fa-hero p code {
            background: rgba(253, 186, 116, 0.2) !important;
            color: #FDE68A !important;
            border: 1px solid rgba(253, 186, 116, 0.45);
            padding: 1px 7px;
            border-radius: 3px;
            font-family: var(--fa-font-mono);
            font-weight: 700;
        }
        .fa-hero-pill {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(253, 186, 116, 0.38);
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 14.8px;
            color: #FAF8F5;
            text-align: right;
            line-height: 1.55;
        }
    """.replace("__HERO_BG_CSS__", hero_bg_css).replace("__LEGAL_BG_CSS__", legal_bg_css)

    st.markdown(
        css_template
        + """
        /* Thanh Gợi ý Theo Vai trò */
        .fa-role-strip {
            background: var(--fa-accent-soft);
            border: 1px solid #FDBA74;
            border-left: 4px solid var(--fa-accent);
            border-radius: 4px;
            padding: 11px 16px;
            margin-bottom: 12px;
            font-size: 15.8px;
            color: #7C2D12;
            line-height: 1.56;
        }

        /* Thẻ KPI Độc bản — Chữ Số Lớn JetBrains Mono & Góc cạnh Kiến trúc */
        .fa-kpi {
            background: var(--fa-card);
            border: 1px solid var(--fa-border);
            border-radius: 5px;
            padding: 17px 19px;
            box-shadow: 0 2px 5px rgba(19, 42, 35, 0.04), 0 6px 16px rgba(6, 78, 59, 0.05);
            height: 100%;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        }
        .fa-kpi:hover {
            transform: translateY(-2px);
            border-color: var(--fa-secondary);
            box-shadow: 0 6px 18px rgba(6, 78, 59, 0.11);
        }
        .fa-kpi-label {
            font-size: 14.2px;
            font-weight: 800;
            color: var(--fa-muted-fg);
            text-transform: uppercase;
            letter-spacing: 0.38px;
        }
        .fa-kpi-value {
            font-family: var(--fa-font-mono);
            font-size: clamp(27px, 2.5vw, 34px);
            font-weight: 800;
            color: var(--fa-ink);
            margin: 7px 0 5px;
            font-variant-numeric: tabular-nums;
            line-height: 1.15;
            overflow-wrap: anywhere;
        }
        .fa-kpi-sub {
            font-size: 15.2px;
            color: var(--fa-muted-fg);
            line-height: 1.48;
        }

        /* Card & Tiêu đề mục Pha 2 Màu có Vạch nhấn dọc */
        .fa-card {
            background: var(--fa-card);
            border: 1px solid var(--fa-border);
            border-radius: 5px;
            padding: 20px 22px;
            box-shadow: 0 2px 5px rgba(19, 42, 35, 0.04), 0 8px 20px rgba(6, 78, 59, 0.05);
            margin-bottom: 14px;
        }
        .fa-section-title {
            font-family: var(--fa-font-head);
            font-size: clamp(21px, 2.05vw, 26px);
            font-weight: 900;
            color: var(--fa-primary);
            margin: 18px 0 12px;
            padding: 4px 0 5px 14px;
            border-left: 4.5px solid var(--fa-accent);
            border-bottom: 1.5px solid var(--fa-border);
            line-height: 1.34;
        }

        /* Nhãn màu ngữ nghĩa vuông vức */
        .fa-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 14.5px;
            font-weight: 700;
            line-height: 1.3;
            white-space: nowrap;
        }
        .fa-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 2px;
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
            border-left: 4.5px solid var(--fa-primary);
            border-radius: 5px;
            padding: 18px 22px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(19, 42, 35, 0.05);
        }
        .fa-rag-cite {
            font-family: var(--fa-font-head);
            font-size: 17.5px;
            font-weight: 800;
            color: var(--fa-primary);
            margin-bottom: 8px;
        }
        .fa-rag-body {
            font-size: 16.5px;
            color: var(--fa-ink);
            line-height: 1.72;
            overflow-wrap: break-word;
        }
        .fa-rag-meta {
            margin-top: 10px;
            font-size: 14.5px;
            color: var(--fa-muted-fg);
            font-family: var(--fa-font-mono);
        }

        /* Bảng Danh mục Văn bản Pháp quy HTML Tự xuống dòng 100% (Không cắt chữ!) */
        .fa-legal-table-wrap {
            background: #FFFFFF;
            border: 1px solid var(--fa-border);
            border-radius: 5px;
            overflow-x: auto;
            box-shadow: 0 2px 8px rgba(19, 42, 35, 0.05);
        }
        .fa-legal-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 16px;
            line-height: 1.62;
        }
        .fa-legal-table th {
            background: var(--fa-primary);
            color: #FFFFFF;
            font-family: var(--fa-font-head);
            font-weight: 700;
            text-align: left;
            padding: 13px 16px;
            font-size: 15.5px;
        }
        .fa-legal-table td {
            padding: 13px 16px;
            border-bottom: 1px solid #E5ECE9;
            vertical-align: top;
            color: var(--fa-ink);
        }
        .fa-legal-table tr:nth-child(even) td {
            background: #FAF8F5;
        }

        /* Khung Chat Box & Hộp thoại Trợ lý AI Rộng rãi kiểu Gemini (Góc cạnh 4px-5px nghiêm chỉnh) */
        .fa-chat-toolbar {
            background: #FFFFFF;
            border: 1.5px solid var(--fa-border);
            border-left: 4.5px solid var(--fa-primary);
            border-radius: 5px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(6, 78, 59, 0.05);
        }
        [data-testid="stChatMessage"] {
            background: #FFFFFF;
            border: 1px solid var(--fa-border);
            border-left: 3.5px solid #064E3B;
            border-radius: 5px !important;
            padding: 16px 20px !important;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(19, 42, 35, 0.04);
        }
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li {
            font-size: 16.5px !important;
            line-height: 1.7 !important;
        }
        [data-testid="stChatInput"] textarea {
            font-size: 16.8px !important;
        }
        /* Mở rộng Hộp thoại (Dialog) Trợ lý AI to, thoáng đãng như không gian làm việc của Gemini */
        [data-testid="stDialog"] [role="dialog"] {
            width: min(94vw, 1340px) !important;
            max-width: 94vw !important;
            border-radius: 6px !important;
            border-top: 4px solid #064E3B !important;
            box-shadow: 0 18px 48px rgba(6, 78, 59, 0.28) !important;
        }
        /* Khu nhập liệu trong Chatbot rộng rãi, thoáng mát và vuông vức */
        [data-testid="stForm"] {
            background: #FFFFFF;
            border: 1.5px solid #B7CEC5 !important;
            border-radius: 5px !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 8px rgba(6, 78, 59, 0.06);
        }
        [data-testid="stForm"] input {
            font-size: 16.8px !important;
            min-height: 46px !important;
            padding: 10px 14px !important;
            border-radius: 4px !important;
        }

        /* Chân trang Chuẩn Website Pháp lý – Chứng từ */
        .fa-footer {
            margin-top: 26px;
            background: var(--fa-muted-bg);
            border: 1px solid var(--fa-border);
            border-top: 3.5px solid var(--fa-primary);
            border-radius: 5px;
            padding: 22px 24px;
            color: var(--fa-muted-fg);
            font-size: 15.5px;
            line-height: 1.68;
        }
        .fa-footer-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        .fa-footer h4 {
            margin: 0 0 8px 0;
            font-family: var(--fa-font-head);
            font-size: 18px;
            font-weight: 800;
            color: var(--fa-primary);
        }

        /* Nút bấm cảm ứng thân thiện Mobile & Desktop (>= 48px, vuông vức 4px-5px, không cắt chữ) */
        .stButton > button, .stDownloadButton > button, [data-testid="stPopover"] > div > button {
            min-height: 48px;
            border-radius: 4px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            padding: 9px 16px !important;
            transition: all 0.16s ease;
            line-height: 1.38;
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

        /* Sửa lỗi dính chữ Thanh Tab & Thêm chuyển động hiện màu dần mượt mà (bo góc 4px) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px !important;
            flex-wrap: wrap;
            border-bottom: 2px solid var(--fa-border);
            padding-bottom: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-image: linear-gradient(110deg, #064E3B 0%, #0F766E 48%, #FFFFFF 52%, #FFFFFF 100%) !important;
            background-size: 230% 100% !important;
            background-position: 100% 0 !important;
            border: 1.5px solid var(--fa-border) !important;
            border-radius: 4px !important;
            padding: 11px 22px !important;
            min-height: 48px !important;
            height: auto !important;
            font-size: 16.2px !important;
            font-weight: 700 !important;
            color: var(--fa-muted-fg) !important;
            transition: background-position 0.5s cubic-bezier(0.22, 1, 0.36, 1), color 0.35s ease, border-color 0.35s ease, transform 0.22s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-position: 0% 0 !important;
            color: #FFFFFF !important;
            border-color: #064E3B !important;
            transform: translateY(-1px);
        }
        .stTabs [data-baseweb="tab"]:hover p {
            color: #FFFFFF !important;
        }
        .stTabs [data-baseweb="tab"] p {
            font-size: 16.2px !important;
            font-weight: 700 !important;
            padding: 0 4px !important;
            transition: color 0.32s ease;
        }
        .stTabs [aria-selected="true"] {
            background-image: linear-gradient(135deg, #064E3B 0%, #0F766E 100%) !important;
            background-size: 100% 100% !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important;
            border-color: var(--fa-primary) !important;
            box-shadow: 0 4px 12px rgba(6, 78, 59, 0.22);
        }
        .stTabs [aria-selected="true"] p {
            color: #FFFFFF !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            display: none !important;
        }

        /* Bảng dữ liệu & Biểu đồ cuộn ngang an toàn trên màn hình nhỏ */
        [data-testid="stDataFrame"],
        [data-testid="stPlotlyChart"] {
            overflow-x: auto;
        }

        /* Khung Card liền mạch cho st.container(border=True) — Góc cạnh 5px có chiều sâu */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1.5px solid var(--fa-border) !important;
            border-radius: 5px !important;
            padding: 16px 20px !important;
            box-shadow: 0 2px 5px rgba(6, 78, 59, 0.04), 0 8px 20px rgba(6, 78, 59, 0.05);
        }

        /* Thanh Điều hướng Ngang 4 Thư mục Phân hệ — Gắn liền dưới Đầu trang, Hiện màu dần khi rê chuột */
        .st-key-top_nav_bar {
            background: #F4F7F5;
            border: 1px solid var(--fa-border);
            border-top: none;
            border-radius: 0 0 5px 5px;
            padding: 10px 16px;
            margin-top: -16px;
            margin-bottom: 16px;
            box-shadow: 0 3px 10px rgba(6, 78, 59, 0.06);
        }
        .st-key-top_nav_bar button {
            min-height: 48px !important;
            border-radius: 4px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            padding: 9px 16px !important;
            background-size: 260% 100% !important;
            background-position: 100% 0 !important;
            transition: background-position 0.65s cubic-bezier(0.22, 1, 0.36, 1),
                        color 0.42s ease,
                        border-color 0.42s ease,
                        transform 0.28s ease,
                        box-shadow 0.42s ease !important;
        }
        .st-key-top_nav_bar button *,
        .st-key-quick_TDH button *, .st-key-quick_QCG button *,
        .st-key-quick_NVL button *, .st-key-quick_DRH button *,
        .st-key-quick_FPT button *, .st-key-quick_VNM button *,
        .st-key-btn_global_quick_search button *,
        .st-key-fab_chat_launcher button * {
            color: inherit !important;
            transition: color 0.35s ease !important;
        }

        /* Màu định danh từng Thư mục Phân hệ — Dần dần hiện màu khi di chuột & Khóa màu khi đang ở trong */
        .st-key-nav_btn_0 button {
            background-image: linear-gradient(112deg, #064E3B 0%, #0A684F 38%, #E6F2EE 62%, #FAF8F5 100%) !important;
            border: 1.5px solid #B7CEC5 !important; color: #064E3B !important;
        }
        .st-key-nav_btn_0 button:hover,
        .st-key-nav_btn_0 button[kind="primary"],
        .st-key-nav_btn_0 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #064E3B 0%, #0A684F 44%, #0F766E 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important; border-color: #064E3B !important;
            box-shadow: 0 5px 14px rgba(6, 78, 59, 0.28) !important; transform: translateY(-2px);
        }

        .st-key-nav_btn_1 button {
            background-image: linear-gradient(112deg, #C2410C 0%, #EA580C 38%, #FFEDD5 62%, #FAF8F5 100%) !important;
            border: 1.5px solid #FDBA74 !important; color: #9A3412 !important;
        }
        .st-key-nav_btn_1 button:hover,
        .st-key-nav_btn_1 button[kind="primary"],
        .st-key-nav_btn_1 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #C2410C 0%, #EA580C 50%, #9A3412 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important; border-color: #C2410C !important;
            box-shadow: 0 5px 14px rgba(194, 65, 12, 0.30) !important; transform: translateY(-2px);
        }

        .st-key-nav_btn_2 button {
            background-image: linear-gradient(112deg, #0F766E 0%, #0D9488 38%, #CCFBF1 62%, #FAF8F5 100%) !important;
            border: 1.5px solid #99F6E4 !important; color: #0F766E !important;
        }
        .st-key-nav_btn_2 button:hover,
        .st-key-nav_btn_2 button[kind="primary"],
        .st-key-nav_btn_2 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #0F766E 0%, #0D9488 50%, #115E59 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important; border-color: #0F766E !important;
            box-shadow: 0 5px 14px rgba(15, 118, 110, 0.28) !important; transform: translateY(-2px);
        }

        .st-key-nav_btn_3 button {
            background-image: linear-gradient(112deg, #B45309 0%, #D97706 38%, #FEF3C7 62%, #FAF8F5 100%) !important;
            border: 1.5px solid #FDE68A !important; color: #92400E !important;
        }
        .st-key-nav_btn_3 button:hover,
        .st-key-nav_btn_3 button[kind="primary"],
        .st-key-nav_btn_3 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #B45309 0%, #D97706 50%, #92400E 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important; border-color: #B45309 !important;
            box-shadow: 0 5px 14px rgba(180, 83, 9, 0.28) !important; transform: translateY(-2px);
        }

        .st-key-nav_btn_4 button {
            background-image: linear-gradient(112deg, #047857 0%, #059669 38%, #D1FAE5 62%, #FAF8F5 100%) !important;
            border: 1.5px solid #A7F3D0 !important; color: #047857 !important;
        }
        .st-key-nav_btn_4 button:hover,
        .st-key-nav_btn_4 button[kind="primary"],
        .st-key-nav_btn_4 button[data-testid="stBaseButton-primary"] {
            background-image: linear-gradient(112deg, #047857 0%, #059669 50%, #065F46 100%) !important;
            background-position: 0% 0 !important;
            color: #FFFFFF !important; border-color: #047857 !important;
            box-shadow: 0 5px 14px rgba(4, 120, 87, 0.28) !important; transform: translateY(-2px);
        }

        /* Hiệu ứng hiện màu dần cho 6 Nút Mẫu Đối chứng Sidebar (Đỏ / Vàng / Xanh) */
        .st-key-quick_TDH button, .st-key-quick_QCG button {
            background-image: linear-gradient(112deg, #BE123C 0%, #E11D48 38%, #FFE4E6 62%, #FFF1F2 100%) !important;
            background-size: 260% 100% !important; background-position: 100% 0 !important;
            border: 1.5px solid #FECDD3 !important; color: #BE123C !important;
            font-family: var(--fa-font-mono) !important; font-size: 13.8px !important;
            transition: background-position 0.55s cubic-bezier(0.22, 1, 0.36, 1), color 0.35s ease, transform 0.22s ease !important;
        }
        .st-key-quick_TDH button:hover, .st-key-quick_QCG button:hover {
            background-position: 0% 0 !important; color: #FFFFFF !important; border-color: #BE123C !important; transform: translateY(-1px);
        }
        .st-key-quick_NVL button, .st-key-quick_DRH button {
            background-image: linear-gradient(112deg, #B45309 0%, #D97706 38%, #FEF3C7 62%, #FFFBEB 100%) !important;
            background-size: 260% 100% !important; background-position: 100% 0 !important;
            border: 1.5px solid #FDE68A !important; color: #B45309 !important;
            font-family: var(--fa-font-mono) !important; font-size: 13.8px !important;
            transition: background-position 0.55s cubic-bezier(0.22, 1, 0.36, 1), color 0.35s ease, transform 0.22s ease !important;
        }
        .st-key-quick_NVL button:hover, .st-key-quick_DRH button:hover {
            background-position: 0% 0 !important; color: #FFFFFF !important; border-color: #B45309 !important; transform: translateY(-1px);
        }
        .st-key-quick_FPT button, .st-key-quick_VNM button {
            background-image: linear-gradient(112deg, #059669 0%, #064E3B 38%, #D1FAE5 62%, #ECFDF5 100%) !important;
            background-size: 260% 100% !important; background-position: 100% 0 !important;
            border: 1.5px solid #A7F3D0 !important; color: #059669 !important;
            font-family: var(--fa-font-mono) !important; font-size: 13.8px !important;
            transition: background-position 0.55s cubic-bezier(0.22, 1, 0.36, 1), color 0.35s ease, transform 0.22s ease !important;
        }
        .st-key-quick_FPT button:hover, .st-key-quick_VNM button:hover {
            background-position: 0% 0 !important; color: #FFFFFF !important; border-color: #059669 !important; transform: translateY(-1px);
        }

        /* KHUNG TÌM KIẾM TƯƠNG PHẢN CAO ĐẶT TRÊN NỀN BANNER NGHỆ THUẬT (CHUẨN CỔNG THÔNG TIN) */
        .st-key-global_search_box,
        .st-key-legal_search_box {
            background: rgba(255, 255, 255, 0.97) !important;
            border: 2px solid #FFFFFF !important;
            border-radius: 5px !important;
            padding: 10px 13px !important;
            margin: 0 auto 15px auto !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.24) !important;
        }
        .st-key-global_search_box input,
        .st-key-legal_search_box input {
            background-color: #FFFFFF !important;
            color: #132A23 !important;
            font-family: var(--fa-font-head) !important;
            font-size: 17px !important;
            font-weight: 600 !important;
            border: 1.5px solid #B7CEC5 !important;
            border-radius: 4px !important;
            padding: 11px 15px !important;
        }
        .st-key-global_search_box input:focus,
        .st-key-legal_search_box input:focus {
            border-color: #C2410C !important;
            box-shadow: 0 0 0 3px rgba(194, 65, 12, 0.18) !important;
        }
        .st-key-global_search_box input::placeholder,
        .st-key-legal_search_box input::placeholder {
            color: #4B635B !important;
            opacity: 0.95 !important;
            font-weight: 500 !important;
        }
        .st-key-global_search_box [data-baseweb="base-input"],
        .st-key-legal_search_box [data-baseweb="base-input"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        .st-key-btn_global_quick_search button,
        .st-key-btn_legal_portal_search button {
            background: #C2410C !important;
            color: #FFFFFF !important;
            border: 2px solid #9A3412 !important;
            border-radius: 4px !important;
            font-family: var(--fa-font-head) !important;
            font-size: 16.5px !important;
            font-weight: 800 !important;
            box-shadow: 0 4px 12px rgba(194, 65, 12, 0.30) !important;
            transition: transform 0.16s ease, box-shadow 0.16s ease, background-color 0.2s ease !important;
        }
        .st-key-btn_global_quick_search button *,
        .st-key-btn_legal_portal_search button * {
            color: #FFFFFF !important;
        }
        .st-key-btn_global_quick_search button:hover,
        .st-key-btn_legal_portal_search button:hover {
            background: #EA580C !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(194, 65, 12, 0.42) !important;
        }

        /* Thanh tiến độ Điểm Rủi ro mini trong Thẻ KPI & Chú giải Thang điểm 3 vùng */
        .fa-score-bar-track {
            position: relative;
            width: 100%;
            height: 8px;
            background: #E8EFEC;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 9px;
        }
        .fa-score-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.45s cubic-bezier(0.22, 1, 0.36, 1);
        }
        .fa-score-bar-ticks {
            display: flex;
            justify-content: space-between;
            font-family: var(--fa-font-mono);
            font-size: 12.2px;
            color: var(--fa-muted-fg);
            margin-top: 4px;
        }
        .fa-scale-legend {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            background: #FAF8F5;
            border: 1px solid var(--fa-border);
            border-radius: 4px;
            padding: 9px 13px;
            font-size: 14.5px;
            color: var(--fa-ink);
        }
        .fa-scale-item {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            white-space: nowrap;
        }
        .fa-more-pill {
            display: inline-flex;
            align-items: center;
            gap: 3px;
            padding: 2px 9px;
            margin-left: 6px;
            border-radius: 3px;
            background: #F0FDFA;
            border: 1px solid #99F6E4;
            color: #0F766E;
            font-size: 13.5px;
            font-weight: 700;
            vertical-align: middle;
        }

        /* Biểu tượng Nút Nổi (Floating Chat Icon) cố định góc phải dưới — Vuông vức kiến trúc, bấm mở Hộp thoại rộng kiểu Gemini */
        .st-key-fab_chat_launcher {
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            z-index: 999 !important;
            width: auto !important;
        }
        .st-key-fab_chat_launcher button {
            border-radius: 5px !important;
            min-height: 54px !important;
            padding: 12px 22px !important;
            background: linear-gradient(135deg, #064E3B 0%, #0F766E 70%, #C2410C 165%) !important;
            border: 2px solid #FDBA74 !important;
            border-left: 5px solid #FDBA74 !important;
            color: #FFFFFF !important;
            font-family: var(--fa-font-head) !important;
            font-size: 16.5px !important;
            font-weight: 800 !important;
            box-shadow: 0 8px 24px rgba(6, 78, 59, 0.36) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        .st-key-fab_chat_launcher button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(194, 65, 12, 0.44) !important;
            background: linear-gradient(135deg, #043628 0%, #064E3B 55%, #C2410C 135%) !important;
        }

        /* Responsive Mobile (<= 768px) — Fix triệt để tràn chữ, biểu đồ, khung tìm kiếm & thanh điều hướng */
        @media (max-width: 768px) {
            html, body, .stApp {
                font-size: 15px;
            }
            .main .block-container,
            [data-testid="stMainBlockContainer"] {
                padding-left: 0.65rem !important;
                padding-right: 0.65rem !important;
                padding-top: 3.5rem !important;
                padding-bottom: 5.8rem !important;
            }
            [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 10px 11px !important;
                border-radius: 12px !important;
            }
            .fa-sticky-bar {
                padding: 10px 12px;
            }
            .fa-hero {
                padding: 14px 15px;
            }
            .fa-hero h1 {
                font-size: 21px;
            }
            .fa-hero-pill {
                text-align: left;
                width: 100%;
            }
            .fa-footer-grid,
            .fa-wizard-grid {
                grid-template-columns: 1fr;
            }
            .st-key-home_portal_hero,
            .st-key-legal_portal_hero {
                padding: 16px 14px 14px !important;
            }
            .fa-card {
                padding: 14px;
            }
            .st-key-top_nav_bar {
                padding: 7px;
            }
            .st-key-top_nav_bar button {
                font-size: 13.5px !important;
                padding: 6px 10px !important;
                min-height: 42px !important;
            }
            .st-key-global_search_box {
                padding: 7px 9px !important;
                box-shadow: 3px 3px 0px #064E3B !important;
            }
            .st-key-global_search_box input {
                font-size: 15px !important;
                padding: 9px 11px !important;
            }
            .st-key-fab_chat_launcher {
                bottom: 14px !important;
                right: 12px !important;
            }
            .st-key-fab_chat_launcher button {
                min-height: 48px !important;
                padding: 9px 16px !important;
                font-size: 14px !important;
            }
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                justify-content: flex-start;
                padding: 10px 14px !important;
            }
            .fa-legal-table th, .fa-legal-table td {
                padding: 9px 10px;
                font-size: 13.8px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sticky_top_banner(active_role: str, active_module: str) -> None:
    """Thành phần bắt buộc 1: Đầu trang Cổng Thông tin Nghiêm chỉnh (chuẩn phong cách dichvucong.gov.vn)."""
    role_short = ROLE_PROFILES.get(active_role, {}).get("short", active_role)
    st.markdown(
        f"""
        <div class="fa-sticky-bar">
          <div class="fa-sticky-left">
            {BRAND_EMBLEM_SVG}
            <div>
              <div class="fa-masthead-title">CỔNG PHÁP CHỨNG TÀI CHÍNH <span>FINAUDIT AI</span></div>
              <div class="fa-masthead-sub">Sàng lọc rủi ro Báo cáo tài chính doanh nghiệp theo chuẩn Việt Nam (VAS • TT 99/2025 • VSA 240)</div>
            </div>
          </div>
          <div class="fa-sticky-left">
            <span class="fa-sticky-tag">643 Doanh nghiệp niêm yết</span>
            <span class="fa-sticky-role">Vai trò: {escape(role_short)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_wizard_steps() -> None:
    """Sơ đồ Quy trình 3 Bước trực quan cho Trang 3 (Giúp người dùng thấy ngay cần cung cấp đầu vào gì)."""
    st.markdown(
        """
        <div class="fa-wizard-grid">
          <div class="fa-wizard-step">
            <span class="fa-wizard-num">BƯỚC 1 • ĐẦU VÀO</span>
            <div class="fa-wizard-title">Cung cấp BCTC 2 năm liên tiếp</div>
            <div class="fa-wizard-desc">Tải file Excel / CSV theo mẫu chuẩn Thông tư 200/99 hoặc chỉnh trực tiếp số liệu mẫu có sẵn.</div>
          </div>
          <div class="fa-wizard-step" style="border-top-color:#064E3B;">
            <span class="fa-wizard-num" style="background:#064E3B;">BƯỚC 2 • PHÂN TÍCH (1 GIÂY)</span>
            <div class="fa-wizard-title">Kiểm tra Cân đối &amp; Chấm điểm AI</div>
            <div class="fa-wizard-desc">Hệ thống kiểm định toàn vẹn kế toán, chấm điểm 4 trụ cột và đối sánh chuẩn ngành tự động.</div>
          </div>
          <div class="fa-wizard-step" style="border-top-color:#C2410C;">
            <span class="fa-wizard-num" style="background:#C2410C;">BƯỚC 3 • ĐẦU RA</span>
            <div class="fa-wizard-title">Xem Nguyên nhân &amp; Tải Báo cáo A4</div>
            <div class="fa-wizard-desc">Nhận biểu đồ chỉ rõ yếu tố gây rủi ro, điều luật đối chiếu và file Báo cáo chuẩn A4 sẵn sàng in PDF.</div>
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
    """Thành phần bắt buộc 2: Danh mục Hiệu lực Văn bản Pháp quy Bộ Tài chính (kèm liên kết tra cứu Cổng Chính phủ)."""
    st.markdown(
        '<div class="fa-section-title">Danh mục <span class="fa-sec-accent">Văn bản Pháp quy &amp; Liên kết Cổng Chính phủ</span></div>',
        unsafe_allow_html=True,
    )
    rows_html = []
    for r in LEGAL_REGISTRY_ROWS:
        st_txt = escape(r["Trạng thái"])
        if "lịch sử" in st_txt.lower():
            badge_cls, dot_cls = "fa-badge-amber", "fa-dot-amber"
        else:
            badge_cls, dot_cls = "fa-badge-green", "fa-dot-green"
        url_g = r.get("Liên kết gốc", "https://vbpl.vn/")
        portal_lbl = escape(r.get("Tên cổng", "vbpl.vn"))
        rows_html.append(
            f"<tr>"
            f"<td style='font-weight:700;color:#064E3B;white-space:nowrap;'>{escape(r['Số hiệu Văn bản'])}</td>"
            f"<td style='line-height:1.56;'>{escape(r['Trích yếu nội dung'])}</td>"
            f"<td style='white-space:nowrap;font-family:var(--fa-font-mono);font-size:13.5px;'>{escape(r['Ngày ban hành'])}</td>"
            f"<td style='white-space:nowrap;font-weight:600;'>{escape(r['Hiệu lực áp dụng'])}</td>"
            f"<td><span class='fa-badge {badge_cls}'><span class='fa-dot {dot_cls}'></span>{st_txt}</span></td>"
            f"<td style='white-space:nowrap;'><a href='{url_g}' target='_blank' rel='noopener noreferrer' "
            f"style='color:#064E3B;font-weight:700;text-decoration:none;border-bottom:1.5px solid #0F766E;'>{portal_lbl} ↗</a></td>"
            f"</tr>"
        )
    st.markdown(
        f"""
        <div class="fa-legal-table-wrap">
          <table class="fa-legal-table">
            <thead>
              <tr>
                <th style="width:18%;">Số hiệu Văn bản</th>
                <th style="width:36%;">Trích yếu nội dung</th>
                <th style="width:11%;">Ban hành</th>
                <th style="width:11%;">Hiệu lực</th>
                <th style="width:11%;">Trạng thái</th>
                <th style="width:13%;">Tra cứu gốc</th>
              </tr>
            </thead>
            <tbody>{''.join(rows_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auto_insight(text_html: str, tone: str = "emerald") -> None:
    """Hiển thị đúng 1 dòng Kết luận Tự động sắc nét ngay đầu biểu đồ để người dùng công sở đọc hiểu trong 3 giây."""
    colors = {
        "red": ("#BE123C", "#FFF7F8"),
        "amber": ("#B45309", "#FFFDF5"),
        "green": ("#059669", "#F2FBF7"),
        "emerald": ("#064E3B", "#F6FAF8"),
    }
    accent, bg = colors.get(tone, colors["emerald"])
    st.markdown(
        f'<div class="fa-insight-strip" style="border-left-color:{accent};background:{bg};">{text_html}</div>',
        unsafe_allow_html=True,
    )


def render_scientific_risk_card(score: float, tier: str, ticker: str = "", year: int = 2025) -> None:
    """
    Thẻ Xếp hạng Rủi ro Khoa học (thay kiểu ghi thô '80.2 đ'):
    - Hiện rõ Điểm chỉ số (thang 0–100) + Hạng A / B / C chuyên nghiệp + Thanh phân đoạn 3 vùng kèm kim vị trí.
    """
    val = max(0.0, min(100.0, float(score) if pd.notna(score) else 0.0))
    if val >= 65.0:
        grade_lbl = "Hạng C • Cảnh báo Cao"
        fg, bg, bd = "#BE123C", "#FFF1F2", "#FECDD3"
        verdict = "Xuất hiện nhiều dấu hiệu rủi ro vượt chuẩn ngành — ưu tiên soát xét kỹ chứng từ gốc."
    elif val >= 40.0:
        grade_lbl = "Hạng B • Cần theo dõi"
        fg, bg, bd = "#B45309", "#FFFBEB", "#FDE68A"
        verdict = "Có một vài chỉ tiêu lệch chuẩn ngành — nên đối chiếu thêm thuyết minh B09-DN."
    else:
        grade_lbl = "Hạng A • An toàn"
        fg, bg, bd = "#059669", "#ECFDF5", "#A7F3D0"
        verdict = "Các chỉ tiêu lợi nhuận, trả nợ và dòng tiền nằm trong vùng lành mạnh."

    st.markdown(
        f"""
        <div class="fa-rating-card" style="border-top:4px solid {fg};">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px;">
              <span style="font-size:14px;font-weight:800;color:#4B635B;text-transform:uppercase;letter-spacing:0.45px;">
                Chỉ số Rủi ro Tổng hợp {f'({escape(ticker)} • {year})' if ticker else ''}
              </span>
              <span class="fa-rating-grade" style="background:{bg};color:{fg};border:1px solid {bd};">{grade_lbl}</span>
            </div>
            <div style="display:flex;align-items:baseline;margin:4px 0 6px;">
              <span class="fa-rating-big" style="color:{fg};">{val:.1f}</span>
              <span class="fa-rating-denom">/ 100 điểm</span>
            </div>
            <div style="font-size:15.5px;color:#243E36;line-height:1.54;">{verdict}</div>
          </div>
          <div>
            <div class="fa-seg-track">
              <div class="fa-seg-a"></div>
              <div class="fa-seg-b"></div>
              <div class="fa-seg-c"></div>
              <div class="fa-seg-pin" style="left:{val:.1f}%;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:13px;font-family:var(--fa-font-mono);color:#4B635B;">
              <span>0 • Hạng A (&lt;40)</span>
              <span>40 • Hạng B</span>
              <span>65 • Hạng C</span>
              <span>100</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_peer_comparison_panel(row: pd.Series, df_sector_peer: pd.DataFrame) -> None:
    """
    Bảng So sánh Trực diện Doanh nghiệp vs. Trung vị Ngành (THAY THẾ Biểu đồ Radar khó hiểu!):
    - Chỉ rõ: Đang so sánh tiêu chí gì? Con số của DN vs. Trung vị ngành? Hơn hay kém ngành bao nhiêu?
    """
    ticker = escape(str(row.get("ticker", "DN")))
    sector = escape(str(row.get("icb_sector_vi", "Cùng ngành")))
    n_peer = len(df_sector_peer)

    def _med(col: str, default: float = 0.0) -> float:
        if df_sector_peer is None or df_sector_peer.empty or col not in df_sector_peer.columns:
            return default
        s = df_sector_peer[col].dropna()
        return float(s.median()) if len(s) > 0 else default

    # 5 tiêu chí cốt lõi dễ hiểu 100% cho kế toán, kiểm toán, tín dụng & nhà đầu tư
    specs = [
        ("Dòng tiền kinh doanh / Tổng tài sản", "cfo_to_assets", "pct", "higher_better", "Tiền thực tạo ra trên mỗi 100đ tài sản"),
        ("Chỉ số Sức khỏe Trả nợ (Altman)", "altman_z_double_prime", "num", "higher_better", "Càng cao càng vững tài chính (>5.85 an toàn)"),
        ("Tài sản mềm (Phải thu khác & Trả trước)", "sensitive_receivables_ratio", "pct", "lower_better", "Tỷ trọng khoản mục dễ ẩn rủi ro / Tổng TS"),
        ("Phải thu khách hàng / Doanh thu", "receivable_to_revenue", "pct", "lower_better", "Tỷ lệ doanh thu chưa thu được tiền mặt"),
        ("Tốc độ Doanh thu so với năm trước", "sgi", "mult", "near_peer", "Mức tăng >1.4 lần ngành dễ có rủi ro thổi số"),
    ]

    worse_cnt = 0
    better_cnt = 0
    rows_html = []
    for title_vi, col, fmt, direction, note_vi in specs:
        v_raw = row.get(col, np.nan)
        m_raw = _med(col, np.nan)
        if pd.isna(v_raw) or pd.isna(m_raw):
            continue
        v = float(v_raw)
        m = float(m_raw)

        if fmt == "pct":
            v_str, m_str = f"{v*100:+.1f}%" if col == "cfo_to_assets" else f"{v*100:.1f}%", f"{m*100:+.1f}%" if col == "cfo_to_assets" else f"{m*100:.1f}%"
            diff_val = (v - m) * 100.0
            diff_txt = f"{diff_val:+.1f} điểm %"
        elif fmt == "mult":
            v_str, m_str = f"{v:.2f} lần", f"{m:.2f} lần"
            diff_val = v - m
            diff_txt = f"{diff_val:+.2f} lần"
        else:
            v_str, m_str = f"{v:.2f}", f"{m:.2f}"
            diff_val = v - m
            diff_txt = f"{diff_val:+.2f}"

        # Phân loại Tốt hơn / Kém hơn / Tương đương ngành rõ ràng
        if direction == "higher_better":
            tol = 1.5 if fmt == "pct" else 0.4
            if diff_val >= tol:
                badge = f"<span class='fa-badge fa-badge-green'>Tốt hơn ngành ({diff_txt})</span>"
                better_cnt += 1
            elif diff_val <= -tol:
                badge = f"<span class='fa-badge fa-badge-red'>Kém hơn ngành ({diff_txt})</span>"
                worse_cnt += 1
            else:
                badge = f"<span class='fa-badge fa-badge-blue'>Tương đương ngành</span>"
        elif direction == "lower_better":
            tol = 2.0
            if diff_val <= -tol:
                badge = f"<span class='fa-badge fa-badge-green'>An toàn hơn ngành ({diff_txt})</span>"
                better_cnt += 1
            elif diff_val >= tol * 2.5:
                badge = f"<span class='fa-badge fa-badge-red'>Rủi ro cao hơn ({diff_txt})</span>"
                worse_cnt += 1
            elif diff_val >= tol:
                badge = f"<span class='fa-badge fa-badge-amber'>Cao hơn ngành ({diff_txt})</span>"
                worse_cnt += 1
            else:
                badge = f"<span class='fa-badge fa-badge-blue'>Tương đương ngành</span>"
        else:  # near_peer (tốc độ doanh thu)
            if v >= max(m * 1.45, 1.40):
                badge = f"<span class='fa-badge fa-badge-red'>Tăng nóng bất thường ({diff_txt})</span>"
                worse_cnt += 1
            elif v < m * 0.70:
                badge = f"<span class='fa-badge fa-badge-amber'>Sụt giảm mạnh ({diff_txt})</span>"
                worse_cnt += 1
            else:
                badge = f"<span class='fa-badge fa-badge-green'>Ổn định gần ngành</span>"
                better_cnt += 1

        rows_html.append(
            f"<tr>"
            f"<td><strong style='color:#132A23;font-size:16px;'>{escape(title_vi)}</strong><br/>"
            f"<span style='font-size:14.2px;color:#4B635B;'>{escape(note_vi)}</span></td>"
            f"<td style='font-family:var(--fa-font-mono);font-weight:800;font-size:16.2px;color:#132A23;white-space:nowrap;'>{v_str}</td>"
            f"<td style='font-family:var(--fa-font-mono);font-weight:600;font-size:15.5px;color:#4B635B;white-space:nowrap;'>{m_str}</td>"
            f"<td>{badge}</td>"
            f"</tr>"
        )

    summary_tone = "red" if worse_cnt >= 3 else ("amber" if worse_cnt >= 1 else "green")
    render_auto_insight(
        f"<strong>So sánh trực diện {ticker} với {n_peer} doanh nghiệp cùng ngành {sector}:</strong> "
        f"Có <strong>{worse_cnt}/5 tiêu chí bất lợi hơn ngành</strong> và <strong>{better_cnt}/5 tiêu chí tích cực</strong>.",
        tone=summary_tone,
    )
    st.markdown(
        f"""
        <div style="overflow-x:auto;">
          <table class="fa-peer-table">
            <thead>
              <tr>
                <th style="width:43%;">Tiêu chí đối chiếu</th>
                <th style="width:16%;">{ticker}</th>
                <th style="width:16%;">Trung vị ngành</th>
                <th style="width:25%;">Đánh giá hơn / kém</th>
              </tr>
            </thead>
            <tbody>{''.join(rows_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(
    kicker: str,
    title: str,
    subtitle: str,
    right_badge: str = "",
    folder_color: str = "#C2410C",
) -> None:
    """Banner Phân hệ tinh gọn với Tiêu đề Pha 2 Màu tự động & Viền màu nhận diện riêng từng Thư mục Phân hệ."""
    right_html = (
        f'<div class="fa-hero-pill" style="border-left:3.5px solid {folder_color};">{right_badge}</div>'
        if right_badge
        else ""
    )
    if " & " in title and "<span" not in title:
        p1, p2 = title.split(" & ", 1)
        title_html = f"{escape(p1)} &amp; <span class='fa-dual-gold'>{escape(p2)}</span>"
    elif "<span" in title:
        title_html = title
    else:
        title_html = escape(title)

    st.markdown(
        f"""
        <div class="fa-hero" style="border-bottom:4px solid {folder_color};border-left:5px solid {folder_color};">
          <div style="flex:1;min-width:240px;">
            <div class="fa-hero-kicker">{escape(kicker)}</div>
            <h1>{title_html}</h1>
            <p>{subtitle}</p>
          </div>
          {right_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    sub: str,
    accent_color: str = "#064E3B",
    score_pct: float | None = None,
) -> None:
    """Thẻ KPI sắc nét — tự động gắn thanh điểm 0–100 trực quan khi truyền score_pct."""
    bar_html = ""
    if score_pct is not None and pd.notna(score_pct):
        pct_clamped = max(0.0, min(100.0, float(score_pct)))
        bar_html = (
            f'<div class="fa-score-bar-track">'
            f'  <div class="fa-score-bar-fill" style="width:{pct_clamped:.1f}%;background:{accent_color};"></div>'
            f'</div>'
            f'<div class="fa-score-bar-ticks"><span>0</span><span>40</span><span>65</span><span>100</span></div>'
        )
    st.markdown(
        f"""
        <div class="fa-kpi" style="border-top: 3.5px solid {accent_color};">
          <div class="fa-kpi-label">{escape(label)}</div>
          <div class="fa-kpi-value" style="color:{accent_color};">{escape(value)}</div>
          <div class="fa-kpi-sub">{escape(sub)}</div>
          {bar_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_scale_legend(compact: bool = False) -> None:
    """Hiển thị thanh chú giải Thang điểm Rủi ro 0–100 rõ ràng (An toàn / Theo dõi / Cảnh báo Đỏ)."""
    if compact:
        st.markdown(
            """
            <div class="fa-scale-legend" style="flex-direction:column;align-items:flex-start;gap:4px;margin-top:6px;">
              <div style="font-size:12px;font-weight:800;color:#064E3B;text-transform:uppercase;letter-spacing:0.4px;">Thang điểm Rủi ro (0–100đ)</div>
              <span class="fa-scale-item"><span class="fa-dot fa-dot-green"></span><code style="font-family:var(--fa-font-mono);color:#059669;">&lt; 40đ</code> An toàn (Lành mạnh)</span>
              <span class="fa-scale-item"><span class="fa-dot fa-dot-amber"></span><code style="font-family:var(--fa-font-mono);color:#B45309;">40–64.9đ</code> Cần theo dõi</span>
              <span class="fa-scale-item"><span class="fa-dot fa-dot-red"></span><code style="font-family:var(--fa-font-mono);color:#BE123C;">&ge; 65đ</code> Cảnh báo Đỏ</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="fa-scale-legend" style="justify-content:space-between;margin-bottom:10px;">
              <span style="font-weight:800;color:#064E3B;">Thang điểm Rủi ro Pháp chứng (0–100đ):</span>
              <div style="display:flex;flex-wrap:wrap;gap:14px;">
                <span class="fa-scale-item"><span class="fa-dot fa-dot-green"></span><strong style="color:#059669;">&lt; 40đ</strong> Thấp (An toàn)</span>
                <span class="fa-scale-item"><span class="fa-dot fa-dot-amber"></span><strong style="color:#B45309;">40–64.9đ</strong> Trung bình (Cần theo dõi)</span>
                <span class="fa-scale-item"><span class="fa-dot fa-dot-red"></span><strong style="color:#BE123C;">&ge; 65đ</strong> Cao (Cảnh báo Đỏ)</span>
              </div>
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
def plot_forensic_matrix_2d(
    df_filtered: pd.DataFrame,
    df_market_ref: pd.DataFrame | None = None,
) -> go.Figure:
    """Bản đồ 2D Sức khỏe Tài chính & Nguy cơ Thổi phồng Lợi nhuận (ngôn ngữ doanh nghiệp dễ hiểu, tự so sánh nền thị trường khi lọc 1 mã)."""
    df = df_filtered.dropna(subset=["beneish_m_score", "altman_z_double_prime", "composite_risk_score"]).copy()
    df["x_plot"] = df["altman_z_double_prime"].clip(-2.0, 14.0)
    df["y_plot"] = df["beneish_m_score"].clip(-6.0, 4.0)
    df["size_plot"] = np.clip(np.log1p(df["total_assets"].fillna(10.0).clip(lower=1.0)) * 2.8, 8.0, 24.0)

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

    # Khi người dùng lọc hẹp (VD gõ 1 mã 'HPG'), vẽ mờ toàn bộ thị trường làm nền để biết mã đang lọc đứng ở đâu!
    is_narrow_filter = df_market_ref is not None and 0 < len(df) <= 15 and len(df_market_ref) > len(df)
    if is_narrow_filter and df_market_ref is not None:
        ref = df_market_ref.dropna(subset=["beneish_m_score", "altman_z_double_prime", "composite_risk_score"]).copy()
        ref = ref[~ref["ticker"].isin(df["ticker"])]
        if not ref.empty:
            fig.add_trace(
                go.Scatter(
                    x=ref["altman_z_double_prime"].clip(-2.0, 14.0),
                    y=ref["beneish_m_score"].clip(-6.0, 4.0),
                    mode="markers",
                    name=f"Mặt bằng thị trường ({len(ref)} DN khác)",
                    marker=dict(size=7, color="#94A3B8", opacity=0.25),
                    hoverinfo="skip",
                )
            )

    for tier_name, color in tier_colors.items():
        sub = df[df["risk_tier"] == tier_name]
        if sub.empty:
            continue
        hover_txt = [
            (
                f"<b>{r['ticker']} — {r['company_name']}</b><br>"
                f"Ngành: {r['icb_sector_vi']} ({r['exchange']})<br>"
                f"<b>Điểm Rủi ro Pháp chứng: {r['composite_risk_score']:.1f} / 100</b><br>"
                f"Dấu hiệu thổi số (Beneish): {r['beneish_m_score']:.2f}<br>"
                f"Sức khỏe trả nợ (Altman): {r['altman_z_double_prime']:.2f} ({translate_altman_zone(r.get('altman_zone', ''))})<br>"
                f"Doanh thu: {r['net_revenue']:,.1f} tỷ | Dòng tiền KD: {r['cfo']:,.1f} tỷ"
            )
            for _, r in sub.iterrows()
        ]
        fig.add_trace(
            go.Scatter(
                x=sub["x_plot"],
                y=sub["y_plot"],
                mode="markers+text" if is_narrow_filter else "markers",
                text=[f"<b>{r['ticker']}</b> ({r['composite_risk_score']:.1f}đ)" for _, r in sub.iterrows()] if is_narrow_filter else None,
                textposition="top center",
                textfont=dict(size=12.5, color=PALETTE["navy"]),
                name=f"{tier_name} ({len(sub)})",
                marker=dict(
                    size=np.maximum(sub["size_plot"], 16.0) if is_narrow_filter else sub["size_plot"],
                    color=color,
                    opacity=0.92 if is_narrow_filter else 0.84,
                    line=dict(width=2 if is_narrow_filter else 1, color="#FFFFFF"),
                ),
                customdata=hover_txt,
                hovertemplate="%{customdata}<extra></extra>",
            )
        )

    fig.add_hline(
        y=-1.78, line_dash="dash", line_color=PALETTE["red"], line_width=1.5,
        annotation_text="<b>Ngưỡng cảnh báo thổi số (-1.78)</b>", annotation_position="top left",
        annotation_font_size=12, annotation_font_color=PALETTE["red"],
        annotation_bgcolor="rgba(255, 241, 242, 0.94)",
        annotation_bordercolor=PALETTE["red"],
        annotation_borderpad=3,
    )
    fig.add_vline(
        x=4.35, line_dash="dash", line_color=PALETTE["red"], line_width=1.4,
        annotation_text="<b>Sức khỏe yếu (4.35)</b>", annotation_position="top left",
        annotation_font_size=12, annotation_font_color=PALETTE["red"],
    )
    fig.add_vline(
        x=5.85, line_dash="dot", line_color=PALETTE["green"], line_width=1.4,
        annotation_text="<b>Tài chính vững (5.85)</b>", annotation_position="bottom right",
        annotation_font_size=12, annotation_font_color=PALETTE["green"],
    )

    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(
            text="<b>Bản đồ Sức khỏe Tài chính & Nguy cơ Thổi số</b><br><span style='font-size:14px;color:#4B635B'>Góc trên bên trái = Vùng rủi ro cao • Góc dưới bên phải = Vùng an toàn</span>",
            font=dict(size=17.2, color=PALETTE["emerald"]),
            x=0.02,
        ),
        xaxis_title="Sức khỏe Tài chính & Trả nợ (Càng sang phải càng vững →)",
        yaxis_title="Nguy cơ Thổi phồng Lợi nhuận (↑ Càng cao càng rủi ro)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=510,
        margin=dict(l=58, r=20, t=78, b=86),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, font=dict(size=13.5)),
        xaxis=dict(gridcolor="#F0F4F2", zerolinecolor="#D1DDD8", range=[-2.2, 14.3], tickfont=dict(size=13.2), automargin=True),
        yaxis=dict(gridcolor="#F0F4F2", zerolinecolor="#D1DDD8", range=[-6.2, 4.2], tickfont=dict(size=13.2), automargin=True),
    )
    return fig


def plot_sector_risk_ranking(
    df_filtered: pd.DataFrame,
    df_market_ref: pd.DataFrame | None = None,
) -> go.Figure:
    """Biểu đồ ngang xếp hạng rủi ro trung vị theo 15 Ngành nghề (tự so sánh toàn thị trường khi lọc 1 mã như HPG)."""
    df = df_filtered.dropna(subset=["composite_risk_score"]).copy()
    selected_sectors = set(df["icb_sector_vi"].dropna().unique().tolist())

    # Tránh lỗi vẽ 1 thanh nâu khổng lồ khi người dùng lọc 1 mã cụ thể -> hiển thị cả 15 ngành và tô nổi ngành của mã đang lọc!
    highlight_mode = df_market_ref is not None and len(selected_sectors) < 3 and len(df_market_ref) > len(df)
    src_df = df_market_ref.dropna(subset=["composite_risk_score"]).copy() if highlight_mode and df_market_ref is not None else df

    agg = (
        src_df.groupby("icb_sector_vi", as_index=False)
        .agg(
            n_firms=("ticker", "count"),
            median_score=("composite_risk_score", "median"),
            red_pct=("composite_risk_score", lambda s: float((s >= 65.0).mean() * 100.0)),
        )
        .sort_values("median_score", ascending=True)
    )
    if highlight_mode:
        colors = [
            PALETTE["copper"] if sec in selected_sectors else "#CBD5D0"
            for sec in agg["icb_sector_vi"]
        ]
        subtitle_txt = "Tô cam: Ngành của doanh nghiệp bạn đang tìm • So với toàn bộ 15 ngành"
    else:
        colors = [
            PALETTE["red"] if v >= 45 else (PALETTE["copper"] if v >= 32 else PALETTE["emerald"])
            for v in agg["median_score"]
        ]
        subtitle_txt = "Điểm rủi ro trung vị & Tỷ lệ doanh nghiệp Cảnh báo Đỏ (≥ 65/100)"

    fig = go.Figure(
        go.Bar(
            y=agg["icb_sector_vi"],
            x=agg["median_score"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{r['median_score']:.1f}/100 (Đỏ {r['red_pct']:.0f}%)" for _, r in agg.iterrows()],
            customdata=[[r["red_pct"], r["n_firms"]] for _, r in agg.iterrows()],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=13.2, color=PALETTE["navy"]),
            hovertemplate="<b>%{y}</b><br>Điểm rủi ro trung vị: <b>%{x:.1f}/100</b><br>Tỷ lệ Cảnh báo Đỏ: %{customdata[0]:.1f}% (trên %{customdata[1]} DN)<extra></extra>",
        )
    )
    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(
            text=f"<b>Xếp hạng Mức độ Rủi ro theo 15 Ngành nghề</b><br><span style='font-size:14px;color:#4B635B'>{subtitle_txt}</span>",
            font=dict(size=17.2, color=PALETTE["emerald"]),
            x=0.02,
        ),
        xaxis_title="Điểm Rủi ro Trung vị của Ngành (thang 0–100)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=510,
        margin=dict(l=18, r=140, t=78, b=54),
        xaxis=dict(gridcolor="#F0F4F2", tickfont=dict(size=13.2), range=[0, max(float(agg["median_score"].max()) * 1.62, 62.0)] if len(agg) else [0, 62]),
        yaxis=dict(tickfont=dict(size=13.2), automargin=True),
    )
    return fig


def plot_risk_gauge(score: float, tier: str) -> go.Figure:
    """Đồng hồ Điểm Rủi ro 0–100 bằng tiếng Việt dễ hiểu (An toàn / Theo dõi / Cảnh báo Đỏ)."""
    val = float(score) if pd.notna(score) else 0.0
    bar_color = PALETTE["red"] if val >= 65 else (PALETTE["copper"] if val >= 40 else PALETTE["green"])
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=val,
            domain={"x": [0.05, 0.95], "y": [0.0, 0.78]},
            number={"suffix": " đ", "font": {"size": 36, "color": bar_color, "family": "JetBrains Mono, monospace"}},
            title={"text": f"<b>Điểm Rủi ro Pháp chứng</b><br><span style='font-size:13.5px;color:{bar_color};font-weight:700;'>{tier}</span>", "font": {"size": 15.5, "color": PALETTE["emerald"]}},
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
    fig.update_layout(font=PLOTLY_BASE_FONT, paper_bgcolor="#FFFFFF", height=275, margin=dict(l=20, r=20, t=68, b=12))
    return fig


def plot_shap_waterfall(row: pd.Series) -> go.Figure:
    """
    Biểu đồ Thác nước Giải thích Nguyên nhân (SHAP) Nằm ngang 100% Tiếng Việt Doanh nghiệp:
    - Mọi vai trò đều đọc hiểu ngay yếu tố nào làm tăng hoặc giảm rủi ro mà không cần biết thuật ngữ học thuật.
    - Tương thích hoàn toàn màn hình điện thoại (375px) và máy tính.
    """
    base_val = float(row.get("shap_base_value", 29.224))
    plain_vi_names = {
        "shap_risk_cfo": "Dòng tiền kinh doanh",
        "shap_risk_altman": "Sức khỏe trả nợ",
        "shap_risk_dsri": "Phải thu KH tăng nhanh",
        "shap_risk_tata": "Lợi nhuận trên giấy",
        "shap_risk_sgi": "Doanh thu tăng nóng",
        "shap_risk_aqi": "Tài sản dài hạn khác",
        "shap_risk_srr": "Phải thu khác & Trả trước",
        "shap_risk_gmi": "Biên lãi gộp giảm",
        "shap_risk_depi": "Giảm tốc khấu hao",
        "shap_risk_ar_rev": "Tỷ lệ Phải thu / DT",
        "shap_risk_lvgi": "Đòn bẩy nợ tăng",
        "shap_risk_sgai": "Chi phí BH & quản lý",
    }
    items = []
    for shap_col, label_vi, raw_col, fmt in SHAP_DISPLAY_META:
        v = row.get(shap_col, np.nan)
        if pd.notna(v):
            raw_v = row.get(raw_col, np.nan)
            raw_txt = (f"{float(raw_v)*100:.1f}%" if fmt == "pct" else f"{float(raw_v):.2f}") if pd.notna(raw_v) else "N/A"
            lbl = f"{plain_vi_names.get(shap_col, label_vi.split('(')[0].strip())} ({raw_txt})"
            items.append((lbl, float(v)))

    items.sort(key=lambda x: abs(x[1]), reverse=True)
    top_items = items[:7]
    other_sum = sum(x[1] for x in items[7:])

    labels = ["Mức trung bình thị trường"] + [x[0] for x in top_items]
    measures = ["absolute"] + ["relative"] * len(top_items)
    values = [base_val] + [x[1] for x in top_items]
    if abs(other_sum) >= 0.05:
        labels.append(f"{len(items) - len(top_items)} yếu tố phụ khác")
        measures.append("relative")
        values.append(other_sum)
    labels.append("Tổng điểm dự báo")
    measures.append("total")
    values.append(0.0)

    texts = []
    for m, v in zip(measures, values):
        if m == "absolute":
            texts.append(f"{v:.1f} điểm")
        elif m == "total":
            tot = base_val + sum(x[1] for x in items)
            texts.append(f"<b>{tot:.1f} / 100</b>")
        else:
            texts.append(f"{v:+.1f}")

    fig = go.Figure(
        go.Waterfall(
            orientation="h",
            measure=measures,
            y=labels,
            x=values,
            text=texts,
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=13.8, color=PALETTE["navy"]),
            connector={"line": {"color": "#D1DDD8", "width": 1.3}},
            increasing={"marker": {"color": PALETTE["red"]}},
            decreasing={"marker": {"color": PALETTE["green"]}},
            totals={"marker": {"color": PALETTE["emerald"]}},
        )
    )
    max_x = max(float(row.get("composite_risk_score", 50.0)), base_val, 35.0) + 26.0
    fig.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(
            text="<b>Phân rã Nguyên nhân làm Tăng (+) hoặc Giảm (-) Chỉ số Rủi ro</b><br><span style='font-size:14px;color:#4B635B'>Đơn vị: Điểm tác động trên thang 0–100 • Đỏ: Tăng rủi ro • Xanh: Giảm rủi ro</span>",
            font=dict(size=17.2, color=PALETTE["emerald"]),
            x=0.02,
        ),
        xaxis_title="Mức tác động vào Chỉ số Rủi ro (thang 0–100 điểm)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=460,
        margin=dict(l=16, r=86, t=78, b=52),
        xaxis=dict(gridcolor="#F0F4F2", tickfont=dict(size=13.2), range=[0, min(max(max_x, 62.0), 122.0)]),
        yaxis=dict(autorange="reversed", tickfont=dict(size=13.5), automargin=True),
    )
    return fig


def plot_sector_radar(row: pd.Series) -> go.Figure:
    """Biểu đồ Radar đối sánh 6 nhóm rủi ro dễ hiểu với Trung vị Ngành."""
    axes_spec = [
        ("risk_dsri", "Phải thu khách hàng"),
        ("risk_sgi", "Tăng trưởng doanh thu"),
        ("risk_tata", "Lợi nhuận trên giấy"),
        ("risk_cfo", "Dòng tiền kinh doanh"),
        ("risk_srr", "Tài sản mềm cao"),
        ("risk_altman", "Áp lực trả nợ"),
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
            name="Mức lành mạnh của ngành",
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
        title=dict(
            text="<b>So sánh 6 Tiêu chí Rủi ro với Trung vị Ngành</b><br><span style='font-size:12.5px;color:#4B635B'>Vùng càng vượt xa vòng xanh càng bất lợi hơn mặt bằng ngành</span>",
            font=dict(size=15, color=PALETTE["emerald"]),
            x=0.02,
        ),
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, range=[0, 5.2], gridcolor="#D1DDD8", tickfont=dict(size=11)),
            angularaxis=dict(gridcolor="#D1DDD8", tickfont=dict(size=12)),
        ),
        paper_bgcolor="#FFFFFF",
        height=445,
        margin=dict(l=46, r=46, t=74, b=54),
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5, font=dict(size=12)),
    )
    return fig


def plot_multiyear_trend(df_comp: pd.DataFrame) -> go.Figure:
    """Biểu đồ 2 tầng diễn biến 8 năm (2018–2025) bằng ngôn ngữ tài chính dễ hiểu."""
    df = df_comp.sort_values("year").copy()
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.14,
        row_heights=[0.55, 0.45],
        subplot_titles=(
            "Doanh thu thuần, Lợi nhuận sau thuế & Dòng tiền kinh doanh (Tỷ VND)",
            "Diễn biến Điểm Rủi ro Pháp chứng qua các năm (0–100đ)",
        ),
    )

    fig.add_trace(go.Bar(x=df["year"], y=df["net_revenue"], name="Doanh thu thuần", marker_color="#D1DDD8", opacity=0.84), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["year"], y=df["net_income"], name="Lợi nhuận sau thuế", mode="lines+markers", line=dict(color=PALETTE["emerald"], width=2.8), marker=dict(size=8)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["year"], y=df["cfo"], name="Dòng tiền kinh doanh", mode="lines+markers", line=dict(color=PALETTE["copper"], width=2.8, dash="dot"), marker=dict(size=8, symbol="diamond")), row=1, col=1)

    df_sc = df.dropna(subset=["composite_risk_score"])
    pt_colors = [PALETTE["red"] if v >= 65 else (PALETTE["copper"] if v >= 40 else PALETTE["green"]) for v in df_sc["composite_risk_score"]]
    fig.add_trace(
        go.Scatter(
            x=df_sc["year"],
            y=df_sc["composite_risk_score"],
            name="Điểm Rủi ro",
            mode="lines+markers+text",
            text=[f"{v:.1f}" for v in df_sc["composite_risk_score"]],
            textposition="top center",
            textfont=dict(size=12, color=PALETTE["navy"]),
            line=dict(color=PALETTE["navy"], width=2.8),
            marker=dict(size=9.5, color=pt_colors, line=dict(width=1.5, color="#FFFFFF")),
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
        height=550,
        margin=dict(l=56, r=20, t=58, b=68),
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5, font=dict(size=13.5)),
    )
    fig.update_annotations(font_size=15.5, font_color=PALETTE["emerald"])
    fig.update_yaxes(gridcolor="#F0F4F2", tickfont=dict(size=13.2), automargin=True, row=1, col=1)
    fig.update_yaxes(gridcolor="#F0F4F2", tickfont=dict(size=13.2), range=[0, 110], title_text="Điểm (0–100)", automargin=True, row=2, col=1)
    fig.update_xaxes(dtick=1, tickfont=dict(size=13.2), row=2, col=1)
    return fig


def plot_validation_benchmarks(stage3_sum: dict[str, Any], stage4_sum: dict[str, Any]) -> tuple[go.Figure, go.Figure]:
    """2 biểu đồ kiểm chứng khoa học tiếng Việt rõ ràng dễ hiểu."""
    bt = stage3_sum["layer4_empirical_backtest"]
    fig_auc = go.Figure(
        go.Bar(
            x=["Chỉ số Thổi số", "AI Dị biệt", "Sức khỏe Nợ", "FinAudit 4 Trụ cột"],
            y=[bt["auc_beneish_only"], bt["auc_isoforest_only"], bt["auc_altman_only"], bt["auc_composite"]],
            marker_color=["#94A3B8", PALETTE["teal"], PALETTE["copper"], PALETTE["emerald"]],
            text=[f"{v:.4f}" for v in [bt["auc_beneish_only"], bt["auc_isoforest_only"], bt["auc_altman_only"], bt["auc_composite"]]],
            textposition="outside",
            textfont=dict(size=12.5, color=PALETTE["navy"]),
        )
    )
    fig_auc.update_layout(
        font=PLOTLY_BASE_FONT,
        title=dict(
            text="<b>Độ chính xác Phân tách DN Minh bạch vs. Biến cố</b><br><span style='font-size:12px;color:#4B635B'>Chỉ số kiểm định AUC (càng gần 1.0 càng chính xác)</span>",
            font=dict(size=15, color=PALETTE["emerald"]),
            x=0.02,
        ),
        yaxis=dict(range=[0, 1.16], title="Độ chính xác (AUC)", gridcolor="#F0F4F2", tickfont=dict(size=12)),
        xaxis=dict(tickfont=dict(size=12)),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=400,
        margin=dict(l=48, r=18, t=70, b=52),
    )

    m_order = ["bm25_raw", "bm25_dual", "tfidf_wc", "hybrid_rrf"]
    m_names = ["Từ khóa gốc", "Song dấu VN", "Khớp ngữ nghĩa", "Động cơ Lai RRF"]
    leg = stage4_sum["legal_benchmark_20q"]["comparison_by_mode"]
    pdf_b = stage4_sum["nvl_pdf_benchmark_6q"]["comparison_by_mode"]

    fig_rag = go.Figure()
    fig_rag.add_trace(
        go.Bar(
            name="Kho Luật VAS (20 câu)",
            x=m_names,
            y=[leg[m]["hit_at_1_pct"] for m in m_order],
            marker_color=PALETTE["emerald"],
            text=[f"{leg[m]['hit_at_1_pct']:.0f}%" for m in m_order],
            textposition="outside",
            textfont=dict(size=12),
        )
    )
    fig_rag.add_trace(
        go.Bar(
            name="PDF Kiểm toán NVL (6 câu)",
            x=m_names,
            y=[pdf_b[m]["hit_at_1_pct"] for m in m_order],
            marker_color=PALETTE["copper"],
            text=[f"{pdf_b[m]['hit_at_1_pct']:.1f}%" for m in m_order],
            textposition="outside",
            textfont=dict(size=12),
        )
    )
    fig_rag.update_layout(
        font=PLOTLY_BASE_FONT,
        barmode="group",
        title=dict(
            text="<b>Tỷ lệ Trả lời Đúng ngay Kết quả #1 (Trợ lý Pháp lý)</b><br><span style='font-size:12px;color:#4B635B'>So sánh 4 phương pháp tìm kiếm trên Luật VAS & PDF Kiểm toán</span>",
            font=dict(size=15, color=PALETTE["emerald"]),
            x=0.02,
        ),
        yaxis=dict(range=[0, 124], title="Tỷ lệ chính xác #1 (%)", gridcolor="#F0F4F2", tickfont=dict(size=12)),
        xaxis=dict(tickfont=dict(size=12)),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=400,
        margin=dict(l=48, r=18, t=70, b=76),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, font=dict(size=12)),
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
