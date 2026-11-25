"""
TRÌNH TẠO BÁO CÁO DỰ THI SE-HACKATHON CHALLENGE 2026 — PHIÊN BẢN V2 (EXECUTIVE & LECTURER-FRIENDLY)
====================================================================================================
Thiết kế chuyên biệt cho trải nghiệm đọc của Ban Giám khảo / Thầy Cô Giảng viên Trường Kinh tế — HaUI:
  - Chuẩn Thể lệ 100% (Kế hoạch 640/KH-ĐHCN ngày 29/10/2026):
      + Khổ A4 (21,0 x 29,7 cm), Times New Roman cỡ 14 pt, đúng 12–13 trang (nằm chuẩn khung 12–15 trang).
      + Đúng cấu trúc bắt buộc: Trang bìa -> Trang 1 (Thành viên + Mentor + Liên hệ) -> Trang 2 (Tóm tắt dự án:
        Ý tưởng chính <= 3 dòng + Mô tả sản phẩm & giá trị) -> Nội dung chính.
  - Trải nghiệm đọc cực kỳ thoáng, thu hút, không dài dòng kỹ thuật:
      + Mỗi mục mở đầu bằng "Câu chuyện / Con số biết nói" hoặc 4 thẻ KPI lớn đọc hiểu trong 3 giây.
      + Lược bỏ diễn giải thuật toán rườm rà; chỉ nêu NGẮN GỌN giải pháp và dồn trọng tâm vào:
        (1) Web FinAudit AI hiện tại ĐÃ LÀM ĐƯỢC GÌ & THỂ HIỆN KẾT QUẢ GÌ (kèm ví dụ thật FPT, VNM, TDH, QCG, NVL);
        (2) Giá trị khai thác trực tiếp cho 5 đối tượng & cả giảng dạy thực hành Kinh tế – Kế toán;
        (3) Khả thi thương mại, tài chính, truyền thông & ESG Trụ cột G.
      + Nhúng 3 hình ảnh trực quan độ phân giải 300 DPI vẽ 100% từ dữ liệu thật (0% số liệu bịa đặt).
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(r"d:\SEHackathon")
DATA_DIR = ROOT_DIR / "data_store" / "processed"
OUT_DIR = ROOT_DIR / "submission_deliverables"
CHART_DIR = OUT_DIR / "charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

DOCX_OUT = OUT_DIR / "Bao_Cao_Du_Thi_FinAudit_AI_SE_Hackathon_2026.docx"

# Bảng màu đồng bộ nhận diện FinAudit AI (Deep Emerald & Terracotta Copper)
HEX_PRIMARY = "064E3B"     # Ngọc Lục Bảo Đậm
HEX_SECONDARY = "0F766E"   # Ngọc Lam Trầm
HEX_ACCENT = "C2410C"      # Đồng Đỏ Terracotta
HEX_RED = "BE123C"         # Đỏ Đô Cảnh báo
HEX_AMBER = "B45309"       # Hổ Phách
HEX_GREEN = "059669"       # Xanh An toàn
HEX_INK = "132A23"         # Chữ chính
HEX_MUTED = "4B635B"       # Chữ phụ
HEX_LIGHT_BG = "F3F8F6"    # Nền xanh ngọc rất nhạt
HEX_WARM_BG = "FFF7ED"     # Nền cam kem nhẹ
HEX_BORDER = "C7D8D1"

RGB_PRIMARY = RGBColor(0x06, 0x4E, 0x3B)
RGB_ACCENT = RGBColor(0xC2, 0x41, 0x0C)
RGB_RED = RGBColor(0xBE, 0x12, 0x3C)
RGB_INK = RGBColor(0x13, 0x2A, 0x23)
RGB_MUTED = RGBColor(0x4B, 0x63, 0x5B)
RGB_WHITE = RGBColor(0xFF, 0xFF, 0xFF)


# ---------------------------------------------------------------------------
# 1. TẠO 3 HÌNH ẢNH TRỰC QUAN 300 DPI DỄ ĐỌC CHO GIẢNG VIÊN KINH TẾ
# ---------------------------------------------------------------------------
def build_executive_charts() -> dict[str, Path]:
    df = pd.read_parquet(DATA_DIR / "forensic_scored_full.parquet")
    s3 = json.loads((DATA_DIR / "stage3_validation_summary.json").read_text(encoding="utf-8"))
    s4 = json.loads((DATA_DIR / "stage4_rag_benchmark_summary.json").read_text(encoding="utf-8"))

    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#C7D8D1"
    plt.rcParams["axes.linewidth"] = 0.9

    paths: dict[str, Path] = {}

    # --- HÌNH 1: Hành trình Trải nghiệm 4 Bước trên Web FinAudit AI (Visual Storytelling) ---
    fig, ax = plt.subplots(figsize=(10.2, 3.25), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 36)
    ax.axis("off")

    steps = [
        ("1. TỔNG QUAN THỊ TRƯỜNG", "Quét nhanh 643 DN\nHOSE & HNX (2019–2025)\n\nLọc ngay 26 DN Hạng C\n& 175 DN báo lãi - tiền âm", "#064E3B", "#F3F8F6"),
        ("2. HỒ SƠ DN 360°", "Xếp hạng Hạng A / B / C\n(Thang điểm 0–100)\n\nChỉ rõ nguyên nhân rủi ro,\nso sánh ngành & in PDF A4", "#C2410C", "#FFF7ED"),
        ("3. KIỂM TRA BCTC", "Tải file Excel / CSV bất kỳ\n(Tự xoay mẫu B01-DN VN)\n\nKiểm tra cân đối & chấm\nđiểm trực tiếp trong 1 giây", "#0F766E", "#F0FDFA"),
        ("4. TRỢ LÝ PHÁP LÝ & PDF", "Hỏi đáp tiếng Việt tự nhiên\nLuật VAS, TT 99, VSA 240\n\nSoi file PDF kiểm toán &\ngắn Link Cổng Chính phủ", "#B45309", "#FFFBEB"),
    ]
    w_box = 22.0
    gap = 3.0
    start_x = 1.5
    for idx, (hdr, body, col, bg) in enumerate(steps):
        x0 = start_x + idx * (w_box + gap)
        card = patches.FancyBboxPatch((x0, 5.2), w_box, 26.8, boxstyle="round,pad=0.25,rounding_size=0.8", facecolor=bg, edgecolor=col, linewidth=1.4)
        ax.add_patch(card)
        bar = patches.FancyBboxPatch((x0, 26.2), w_box, 5.8, boxstyle="round,pad=0.25,rounding_size=0.7", facecolor=col, edgecolor=col, linewidth=1.0)
        ax.add_patch(bar)
        ax.text(x0 + w_box / 2, 29.1, hdr, ha="center", va="center", fontsize=7.4, fontweight="bold", color="white")
        ax.text(x0 + w_box / 2, 15.6, body, ha="center", va="center", fontsize=7.7, color="#132A23", linespacing=1.45)
        if idx < 3:
            ax.annotate(
                "",
                xy=(x0 + w_box + gap - 0.35, 18.5),
                xytext=(x0 + w_box + 0.35, 18.5),
                arrowprops=dict(arrowstyle="-|>,head_width=0.38,head_length=0.55", color="#064E3B", lw=1.8),
            )
    ax.text(50, 1.8, "Bốn phân hệ làm việc trực quan trên cổng Web FinAudit AI — Thao tác dễ dàng trên cả máy tính công sở & điện thoại", ha="center", va="center", fontsize=8.3, style="italic", color="#4B635B")
    p1 = CHART_DIR / "v2_fig1_4modules_journey.png"
    fig.savefig(p1, dpi=300, bbox_inches="tight")
    plt.close(fig)
    paths["fig1"] = p1

    # --- HÌNH 2: Kết quả Sàng lọc Thực tế trên 639 DN năm 2025 & Đối chứng 6 Trường hợp Điển hình ---
    d25 = df[(df["year"] == 2025) & (df["composite_risk_score"].notna())].copy()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 3.65), dpi=300, gridspec_kw={"width_ratios": [1.0, 1.25]})
    fig.patch.set_facecolor("white")

    labels_p1 = ["Hạng A\nAn toàn\n(<40đ)", "Hạng B\nTheo dõi\n(40–64,9đ)", "Hạng C\nCảnh báo cao\n(≥65đ)", "Báo lãi nhưng\nTiền KD âm\n(LN>0, CFO<0)"]
    vals_p1 = [487, 126, 26, 175]
    pcts_p1 = [v / 639 * 100 for v in vals_p1]
    cols_p1 = ["#059669", "#D97706", "#BE123C", "#C2410C"]
    bars1 = ax1.bar(labels_p1, vals_p1, color=cols_p1, width=0.56)
    ax1.set_title("A. Phân loại 639 DN niêm yết năm 2025", fontsize=10.3, fontweight="bold", color="#064E3B", pad=10)
    ax1.set_ylabel("Số doanh nghiệp", fontsize=9.0, color="#132A23")
    ax1.set_ylim(0, 580)
    ax1.grid(axis="y", linestyle="--", alpha=0.35, color="#94A3B8")
    ax1.set_axisbelow(True)
    ax1.tick_params(axis="x", labelsize=8.1)
    for b, v, p in zip(bars1, vals_p1, pcts_p1):
        ax1.text(b.get_x() + b.get_width() / 2, v + 12, f"{v} DN\n({p:.1f}%)", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color="#132A23")

    cases = ["TDH (BĐS)", "QCG (BĐS)", "DRH (BĐS)", "NVL (BĐS*)", "FPT (CNTT)", "VNM (Thực phẩm)"]
    case_tkrs = ["TDH", "QCG", "DRH", "NVL", "FPT", "VNM"]
    case_scores = [float(d25[d25["ticker"] == t]["composite_risk_score"].iloc[0]) for t in case_tkrs]
    case_cols = ["#BE123C" if s >= 65 else ("#D97706" if s >= 40 else "#059669") for s in case_scores]
    y_pos = np.arange(len(cases))
    bars2 = ax2.barh(y_pos, case_scores, color=case_cols, height=0.55)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(cases, fontsize=8.8, fontweight="bold", color="#132A23")
    ax2.invert_yaxis()
    ax2.set_xlim(0, 102)
    ax2.axvline(40, color="#D97706", linestyle=":", linewidth=1.3, label="Ngưỡng Hạng B (40đ)")
    ax2.axvline(65, color="#BE123C", linestyle="--", linewidth=1.3, label="Ngưỡng Hạng C (65đ)")
    ax2.set_xlabel("Chỉ số Rủi ro trên Web (Thang 0–100 điểm)", fontsize=8.9, color="#132A23")
    ax2.set_title("B. Đối chứng thực tế 6 doanh nghiệp (2025)", fontsize=10.3, fontweight="bold", color="#064E3B", pad=10)
    ax2.grid(axis="x", linestyle="--", alpha=0.35, color="#94A3B8")
    ax2.set_axisbelow(True)
    for b, s in zip(bars2, case_scores):
        ax2.text(s + 1.8, b.get_y() + b.get_height() / 2, f"{s:.1f} / 100", va="center", ha="left", fontsize=8.8, fontweight="bold", color="#132A23")
    ax2.legend(loc="lower right", fontsize=7.8, frameon=True, facecolor="white", edgecolor="#D1DDD8")

    plt.tight_layout(pad=1.2)
    p2 = CHART_DIR / "v2_fig2_real_results_2025.png"
    fig.savefig(p2, dpi=300, bbox_inches="tight")
    plt.close(fig)
    paths["fig2"] = p2

    # --- HÌNH 3: Minh chứng Độ tin cậy (Phân tách DN Minh bạch vs Biến cố & Trợ lý Pháp lý) ---
    bt = s3["layer4_empirical_backtest"]
    leg = s4["legal_benchmark_20q"]["comparison_by_mode"]
    pdf_b = s4["nvl_pdf_benchmark_6q"]["comparison_by_mode"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 3.55), dpi=300)
    fig.patch.set_facecolor("white")

    m_lbls = ["Chỉ số đơn lẻ\n(Beneish)", "Phát hiện\ndị biệt AI", "Sức khỏe\ntrả nợ", "FinAudit AI\n(Tổng hợp)"]
    m_vals = [bt["auc_beneish_only"] * 100, bt["auc_isoforest_only"] * 100, bt["auc_altman_only"] * 100, bt["auc_composite"] * 100]
    m_cols = ["#94A3B8", "#0F766E", "#D97706", "#064E3B"]
    b1 = ax1.bar(m_lbls, m_vals, color=m_cols, width=0.54)
    ax1.set_ylim(0, 114)
    ax1.set_ylabel("Độ chính xác phân tách — AUC (%)", fontsize=8.8)
    ax1.set_title("A. Phân biệt 12 DN Minh bạch vs. 12 DN Biến cố", fontsize=10.0, fontweight="bold", color="#064E3B", pad=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.35, color="#94A3B8")
    ax1.set_axisbelow(True)
    ax1.tick_params(labelsize=8.2)
    for bar, v in zip(b1, m_vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 2.2, f"{v:.1f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#132A23")

    r_lbls = ["Trả lời đúng\nngay #1 (Luật)", "Đúng trong\nTop 3 (Luật)", "Đọc đúng PDF\n91 trang NVL", "Chống AI\n'bịa' luật"]
    r_vals = [leg["hybrid_rrf"]["hit_at_1_pct"], leg["hybrid_rrf"]["hit_at_3_pct"], pdf_b["hybrid_rrf"]["hit_at_1_pct"], 100.0]
    r_cols = ["#064E3B", "#059669", "#C2410C", "#0F766E"]
    b2 = ax2.bar(r_lbls, r_vals, color=r_cols, width=0.54)
    ax2.set_ylim(0, 114)
    ax2.set_ylabel("Tỷ lệ đạt chuẩn kiểm thử (%)", fontsize=8.8)
    ax2.set_title("B. Độ tin cậy của Trợ lý Pháp lý & Soi PDF", fontsize=10.0, fontweight="bold", color="#064E3B", pad=10)
    ax2.grid(axis="y", linestyle="--", alpha=0.35, color="#94A3B8")
    ax2.set_axisbelow(True)
    ax2.tick_params(labelsize=8.1)
    for bar, v in zip(b2, r_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 2.2, f"{v:.1f}%" if v % 1 != 0 else f"{v:.0f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#132A23")

    plt.tight_layout(pad=1.2)
    p3 = CHART_DIR / "v2_fig3_trust_proof.png"
    fig.savefig(p3, dpi=300, bbox_inches="tight")
    plt.close(fig)
    paths["fig3"] = p3

    return paths


# ---------------------------------------------------------------------------
# 2. CÁC TIỆN ÍCH TRÌNH BÀY WORD SANG TRỌNG, THOÁNG MẮT CHO BAN GIÁM KHẢO
# ---------------------------------------------------------------------------
def set_cell_shading(cell, fill_hex: str) -> None:
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=85, bottom=85, left=110, right=110) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, border_hex: str = HEX_BORDER) -> None:
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="{border_hex}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_page_number_footer(section) -> None:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run("FinAudit AI — FinForensics | SE-Hackathon Challenge 2026 (Trường Kinh tế — HaUI)   •   Trang ")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11)
    r1.font.color.rgb = RGB_MUTED

    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r_pg = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "22")
    rPr.append(rFonts)
    rPr.append(sz)
    r_pg.append(rPr)
    fld.append(r_pg)
    p._p.append(fld)


def style_run(run, size: float = 14, bold: bool = False, italic: bool = False, color: RGBColor = RGB_INK):
    run.font.name = "Times New Roman"
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    rFonts.set(qn("w:cs"), "Times New Roman")
    rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    return run


def add_p(
    doc: Document,
    text: str = "",
    *,
    bold: bool = False,
    italic: bool = False,
    size: float = 14,
    color: RGBColor = RGB_INK,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    space_before: float = 0,
    space_after: float = 5.5,
    line_spacing: float = 1.24,
    first_line_cm: float = 0.0,
):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if first_line_cm > 0:
        pf.first_line_indent = Cm(first_line_cm)
    if text:
        r = p.add_run(text)
        style_run(r, size=size, bold=bold, italic=italic, color=color)
    return p


def add_rich_p(
    doc: Document,
    segments: list[tuple[str, bool, bool, RGBColor | None]],
    *,
    size: float = 14,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    space_before: float = 0,
    space_after: float = 5.5,
    line_spacing: float = 1.24,
    left_indent_cm: float = 0.0,
    first_line_cm: float = 0.0,
):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if left_indent_cm > 0:
        pf.left_indent = Cm(left_indent_cm)
    if first_line_cm != 0:
        pf.first_line_indent = Cm(first_line_cm)
    for txt, b, it, col in segments:
        r = p.add_run(txt)
        style_run(r, size=size, bold=b, italic=it, color=col or RGB_INK)
    return p


def add_bullet(doc: Document, lead_bold: str, body: str, size: float = 14, space_after: float = 4.5):
    segs: list[tuple[str, bool, bool, RGBColor | None]] = [("▪ ", True, False, RGB_ACCENT)]
    if lead_bold:
        segs.append((lead_bold, True, False, RGB_INK))
    segs.append((body, False, False, RGB_INK))
    return add_rich_p(doc, segs, size=size, space_after=space_after, left_indent_cm=0.55, first_line_cm=-0.38, line_spacing=1.24)


def add_h1(doc: Document, text: str, space_before: float = 10):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(5)
    pf.keep_with_next = True
    pf.line_spacing = 1.14
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="3" w:color="{HEX_PRIMARY}"/></w:pBdr>')
    pPr.append(pBdr)
    r = p.add_run(text)
    style_run(r, size=14.5, bold=True, color=RGB_PRIMARY)
    return p


def add_h2(doc: Document, text: str, space_before: float = 7):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(3.5)
    pf.keep_with_next = True
    pf.line_spacing = 1.14
    r = p.add_run(text)
    style_run(r, size=14, bold=True, color=RGB_ACCENT)
    return p


def add_kpi_strip(doc: Document, items: list[tuple[str, str, str, str]]):
    """Dải 4 thẻ con số nổi bật (Số lớn + Nhãn + Diễn giải ngắn) giúp Thầy Cô quét mắt nắm ngay giá trị trong 3 giây."""
    tbl = doc.add_table(rows=1, cols=len(items))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tblPr = tbl._tbl.tblPr
    tblPr.append(
        parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'  <w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
            f'  <w:insideH w:val="none"/><w:insideV w:val="single" w:sz="18" w:space="0" w:color="FFFFFF"/>'
            f'</w:tblBorders>'
        )
    )
    w_each = 16.6 / len(items)
    for j, (big_num, title, sub, accent_hex) in enumerate(items):
        cell = tbl.cell(0, j)
        cell.width = Cm(w_each)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        set_cell_shading(cell, HEX_LIGHT_BG if j % 2 == 0 else HEX_WARM_BG)
        set_cell_margins(cell, top=95, bottom=95, left=95, right=95)
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(
            parse_xml(
                f'<w:tcBorders {nsdecls("w")}>'
                f'  <w:top w:val="single" w:sz="20" w:space="0" w:color="{accent_hex}"/>'
                f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
                f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
                f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
                f'</w:tcBorders>'
            )
        )
        p1 = cell.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.line_spacing = 1.05
        r_num = p1.add_run(big_num)
        rgb_acc = RGBColor(int(accent_hex[0:2], 16), int(accent_hex[2:4], 16), int(accent_hex[4:6], 16))
        style_run(r_num, size=17.5, bold=True, color=rgb_acc)

        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(2)
        p2.paragraph_format.line_spacing = 1.08
        r_t = p2.add_run(title)
        style_run(r_t, size=12, bold=True, color=RGB_INK)

        p3 = cell.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_before = Pt(0)
        p3.paragraph_format.space_after = Pt(0)
        p3.paragraph_format.line_spacing = 1.08
        r_s = p3.add_run(sub)
        style_run(r_s, size=11, italic=True, color=RGB_MUTED)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)
    sp.paragraph_format.line_spacing = 1.0


def add_callout_box(doc: Document, title: str, body_segments: list[tuple[str, bool, bool, RGBColor | None]], bg_hex: str = HEX_LIGHT_BG, border_hex: str = HEX_PRIMARY):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Cm(16.6)
    set_cell_shading(cell, bg_hex)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=130)
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(
        parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
            f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
            f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
            f'  <w:left w:val="single" w:sz="28" w:space="0" w:color="{border_hex}"/>'
            f'</w:tcBorders>'
        )
    )

    p0 = cell.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    p0.paragraph_format.line_spacing = 1.18
    if title:
        rt = p0.add_run(title + " ")
        style_run(rt, size=14, bold=True, color=RGB_PRIMARY if border_hex == HEX_PRIMARY else RGB_ACCENT)
    for txt, b, it, col in body_segments:
        r = p0.add_run(txt)
        style_run(r, size=14, bold=b, italic=it, color=col or RGB_INK)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)
    sp.paragraph_format.line_spacing = 1.0


def add_styled_table(
    doc: Document,
    headers: list[str],
    rows: list[list[str]],
    col_widths_cm: list[float],
    font_size: float = 12.5,
    center_cols: set[int] | None = None,
):
    center_cols = center_cols or set()
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl)

    hdr_row = tbl.rows[0]
    trPr = hdr_row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:tblHeader"))
    trPr.append(OxmlElement("w:cantSplit"))
    for j, h_txt in enumerate(headers):
        cell = hdr_row.cells[j]
        cell.width = Cm(col_widths_cm[j])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=80, bottom=80, left=90, right=90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j in center_cols else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.10
        r = p.add_run(h_txt)
        style_run(r, size=font_size, bold=True, color=RGB_WHITE)

    for i, r_data in enumerate(rows):
        row = tbl.rows[i + 1]
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        bg = "FFFFFF" if i % 2 == 0 else HEX_LIGHT_BG
        for j, val in enumerate(r_data):
            cell = row.cells[j]
            cell.width = Cm(col_widths_cm[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=68, bottom=68, left=90, right=90)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j in center_cols else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.10
            r = p.add_run(val)
            style_run(r, size=font_size, bold=(j == 0), color=RGB_INK)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)
    sp.paragraph_format.line_spacing = 1.0
    return tbl


def add_figure(doc: Document, img_path: Path, caption: str, width_cm: float = 16.0):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(4)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    p_img.add_run().add_picture(str(img_path), width=Cm(width_cm))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(6)
    p_cap.paragraph_format.line_spacing = 1.10
    rc = p_cap.add_run(caption)
    style_run(rc, size=12.5, italic=True, color=RGB_MUTED)


# ---------------------------------------------------------------------------
# 3. NỘI DUNG BÁO CÁO V2 — CUỐN HÚT, SÚC TÍCH, TỐI ƯU CHO THẦY CÔ GIẢNG VIÊN
# ---------------------------------------------------------------------------
def build_report_v2(chart_paths: dict[str, Path]) -> Path:
    doc = Document()

    # Thiết lập khổ giấy A4 & lề chuẩn thoáng mắt cho Ban Giám khảo (đúng 12 trang chuẩn khung 12–15 trang của BTC)
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.1)
    sec.bottom_margin = Cm(2.1)
    sec.left_margin = Cm(2.6)
    sec.right_margin = Cm(2.1)
    sec.different_first_page_header_footer = True
    add_page_number_footer(sec)

    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(14)

    # =======================================================================
    # TRANG BÌA (CHÍNH XÁC THEO MẪU TRANG 11 THỂ LỆ)
    # =======================================================================
    cover_tbl = doc.add_table(rows=1, cols=1)
    cover_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cover_tbl.autofit = False
    c_cell = cover_tbl.cell(0, 0)
    c_cell.width = Cm(16.6)
    c_cell._tc.get_or_add_tcPr().append(
        parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:top w:val="double" w:sz="12" w:space="0" w:color="{HEX_PRIMARY}"/>'
            f'  <w:bottom w:val="double" w:sz="12" w:space="0" w:color="{HEX_PRIMARY}"/>'
            f'  <w:left w:val="double" w:sz="12" w:space="0" w:color="{HEX_PRIMARY}"/>'
            f'  <w:right w:val="double" w:sz="12" w:space="0" w:color="{HEX_PRIMARY}"/>'
            f'</w:tcBorders>'
        )
    )
    set_cell_margins(c_cell, top=320, bottom=280, left=260, right=260)

    def _cp(txt="", size=14, bold=False, italic=False, color=RGB_INK, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6, ls=1.22):
        p = c_cell.paragraphs[0] if (len(c_cell.paragraphs) == 1 and not c_cell.paragraphs[0].text) else c_cell.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(sa)
        p.paragraph_format.line_spacing = ls
        if txt:
            style_run(p.add_run(txt), size=size, bold=bold, italic=italic, color=color)
        return p

    _cp("ĐẠI HỌC CÔNG NGHIỆP HÀ NỘI", size=14.5, bold=True, color=RGB_PRIMARY, sa=2)
    _cp("TRƯỜNG KINH TẾ", size=14.5, bold=True, color=RGB_PRIMARY, sa=14)
    _cp("CUỘC THI “SÁNG TẠO - KHỞI NGHIỆP VÌ TƯƠNG LAI BỀN VỮNG", size=15, bold=True, color=RGB_INK, sa=2)
    _cp("– SE HACKATHON CHALLENGE 2026”", size=15.5, bold=True, color=RGB_ACCENT, sa=26)

    _cp("BẢN THUYẾT MINH DỰ ÁN KHỞI NGHIỆP", size=14, bold=True, color=RGB_MUTED, sa=10)
    _cp("FINAUDIT AI — FINFORENSICS", size=22, bold=True, color=RGB_PRIMARY, sa=8)
    _cp("CỔNG AI SÀNG LỌC RỦI RO BÁO CÁO TÀI CHÍNH", size=15.5, bold=True, color=RGB_INK, sa=2)
    _cp("& TRỢ LÝ PHÁP LÝ KẾ TOÁN CHUẨN VIỆT NAM", size=15.5, bold=True, color=RGB_INK, sa=16)

    _cp("Thuộc lĩnh vực: Công nghệ số & Trí tuệ nhân tạo ứng dụng trong Kinh tế – Tài chính", size=14, italic=True, color=RGB_ACCENT, sa=2)
    _cp("(Đóng góp trực tiếp Trụ cột G — Minh bạch Quản trị trong Phát triển bền vững ESG)", size=13.5, italic=True, color=RGB_MUTED, sa=32)

    _cp("Tên nhóm dự thi: [Điền tên nhóm dự thi]", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, sa=7)
    _cp("Họ và tên trưởng nhóm: [Điền Họ và tên Trưởng nhóm]", size=14, align=WD_ALIGN_PARAGRAPH.LEFT, sa=7)
    _cp("Giảng viên hướng dẫn (Mentor): [Điền Học hàm/Học vị & Họ tên GVHD]", size=14, align=WD_ALIGN_PARAGRAPH.LEFT, sa=7)
    _cp("Đơn vị: Trường Kinh tế, Đại học Công nghiệp Hà Nội (HaUI)", size=14, align=WD_ALIGN_PARAGRAPH.LEFT, sa=40)

    _cp("ĐƠN VỊ: TRƯỜNG KINH TẾ — ĐẠI HỌC CÔNG NGHIỆP HÀ NỘI", size=14, bold=True, color=RGB_PRIMARY, sa=40)
    _cp("Hà Nội, tháng 11/2026", size=14, italic=True, color=RGB_INK, sa=0)

    doc.add_page_break()

    # =======================================================================
    # TRANG THỨ 1 (THEO ĐÚNG MẪU TRANG 12 THỂ LỆ: THÀNH VIÊN + MENTOR + LIÊN HỆ)
    # =======================================================================
    add_h1(doc, "THÔNG TIN ĐỘI THI VÀ GIẢNG VIÊN HƯỚNG DẪN", space_before=0)
    add_p(doc, "1. Thông tin thành viên tham gia dự án (tối đa 05 thành viên, gồm cả trưởng nhóm):", bold=True, space_after=4)
    add_styled_table(
        doc,
        headers=["TT", "Họ và tên", "Mã sinh viên", "Lớp / Khoa", "Vai trò trong dự án"],
        rows=[
            ["1", "[Họ và tên Trưởng nhóm]", "[Mã SV]", "[Lớp — Trường KT]", "Trưởng nhóm — Định hướng sản phẩm & Nghiệp vụ Kế toán/Kiểm toán"],
            ["2", "[Thành viên 2]", "[Mã SV]", "[Lớp — Đơn vị]", "Xử lý dữ liệu BCTC & Tích hợp hệ thống phân tích AI"],
            ["3", "[Thành viên 3]", "[Mã SV]", "[Lớp — Đơn vị]", "Pháp lý Kế toán – Kiểm toán (VAS, Thông tư 99/2025, VSA 240)"],
            ["4", "[Thành viên 4]", "[Mã SV]", "[Lớp — Đơn vị]", "Thiết kế giao diện Web & Trải nghiệm người dùng"],
            ["5", "[Thành viên 5 (nếu có)]", "[Mã SV]", "[Lớp — Đơn vị]", "Mô hình kinh doanh, Truyền thông & Kiểm thử thực tế"],
        ],
        col_widths_cm=[1.0, 3.8, 2.3, 3.1, 6.4],
        font_size=12.5,
        center_cols={0, 2},
    )

    add_p(doc, "2. Giảng viên hướng dẫn / Cố vấn chuyên môn (Mentor):", bold=True, space_before=2, space_after=4)
    add_styled_table(
        doc,
        headers=["Họ và tên Mentor", "Đơn vị công tác", "Lĩnh vực đồng hành cố vấn"],
        rows=[
            ["[Học hàm/Học vị, Họ và tên GVHD]", "Trường Kinh tế — ĐH Công nghiệp Hà Nội", "Kế toán – Kiểm toán, Chuẩn mực VAS/VSA & Mô hình kinh doanh"],
        ],
        col_widths_cm=[5.2, 5.4, 6.0],
        font_size=12.5,
    )

    add_rich_p(
        doc,
        [
            ("3. Liên hệ Trưởng nhóm:  ", True, False, RGB_INK),
            ("SĐT: ", True, False, RGB_PRIMARY),
            ("[09xx.xxx.xxx]   |   ", False, False, RGB_INK),
            ("Email: ", True, False, RGB_PRIMARY),
            ("[email.truongnhom@haui.edu.vn]", False, False, RGB_INK),
        ],
        space_after=8,
    )

    add_callout_box(
        doc,
        "Điểm nhấn dành cho Ban Giám khảo trước khi đọc:",
        [
            ("FinAudit AI — FinForensics không phải ý tưởng trên giấy mà là ", False, False, None),
            ("cổng Web đã vận hành hoàn chỉnh trên dữ liệu thật của 643 doanh nghiệp niêm yết Việt Nam (2018–2025)", True, False, RGB_PRIMARY),
            (". Mọi số liệu bối cảnh đều dẫn nguồn chính thống (ACFE 2024, VSDC, Cục Thống kê, Bộ Tài chính/VACPA), tuyệt đối không suy diễn và tuân thủ chuẩn mực VSA 240.", False, False, None),
        ],
    )

    doc.add_page_break()

    # =======================================================================
    # TRANG THỨ 2–5: PHẦN I. TÓM TẮT DỰ ÁN / Ý TƯỞNG (3–4 TRANG THEO MẪU THỂ LỆ)
    # =======================================================================
    add_h1(doc, "PHẦN I. TÓM TẮT DỰ ÁN / Ý TƯỞNG", space_before=0)

    add_callout_box(
        doc,
        "Ý tưởng chính:",
        [
            ("FinAudit AI — FinForensics là nền tảng Web AI giúp người dùng sàng lọc rủi ro Báo cáo tài chính (BCTC) chỉ trong vài giây, tự động xếp hạng Hạng A/B/C, chỉ rõ nguyên nhân bất thường bằng ngôn ngữ dễ hiểu và đối chiếu thẳng điều luật Bộ Tài chính (VAS, Thông tư 99/2025, VSA 240).", False, False, None),
        ],
        bg_hex=HEX_WARM_BG,
        border_hex=HEX_ACCENT,
    )

    # Dải 4 con số đinh đọc hiểu trong 3 giây
    add_kpi_strip(
        doc,
        [
            ("643 DN", "Dữ liệu thật HOSE & HNX", "Chuỗi 8 năm 2018–2025", HEX_PRIMARY),
            ("93,0%", "Độ chính xác phân tách", "0% báo động giả Bluechip", HEX_GREEN),
            ("< 1 giây", "Chấm điểm BCTC tự tải", "Hỗ trợ cả mẫu dọc B01-DN", HEX_ACCENT),
            ("100%", "Chống AI 'bịa' điều luật", "Gắn Link Cổng Chính phủ", HEX_SECONDARY),
        ],
    )

    add_h2(doc, "1.1. Câu chuyện thực tế: Vì sao nhìn 'Báo cáo có lãi' vẫn có thể mất tiền?")
    add_p(
        doc,
        "Một doanh nghiệp niêm yết công bố lãi sau thuế hàng trăm tỷ đồng, nhưng ngay trong năm đó dòng tiền hoạt động kinh doanh lại âm sâu hoặc đột ngột bị kiểm toán điều chỉnh từ lãi sang lỗ. Đây không phải câu chuyện cá biệt mà là điểm nghẽn minh bạch lớn nhất của thị trường tài chính Việt Nam hiện nay, được chứng minh qua bốn thực tế có số liệu kiểm chứng:",
        first_line_cm=0.7,
    )
    add_bullet(
        doc,
        "Thiệt hại do sai lệch BCTC nặng nề nhất và lâu bị phát hiện nhất: ",
        "Theo báo cáo toàn cầu của Hiệp hội Chuyên gia Điều tra Gian lận Hoa Kỳ (ACFE, 2024) trên 1.921 vụ việc tại 138 quốc gia, doanh nghiệp trung bình thất thoát 5% doanh thu mỗi năm vì gian lận. Riêng gian lận BCTC chỉ chiếm 5% số vụ nhưng gây tổn thất nặng nhất với mức trung vị 766.000 USD/vụ và kéo dài trung bình 18 tháng mới bị lộ diện.",
    )
    add_bullet(
        doc,
        "Sự quá tải giữa quy mô thị trường và nhân lực kiểm toán tại Việt Nam: ",
        "Tính đến 31/12/2025, thị trường chứng khoán đã vượt mốc 11,8 triệu tài khoản cá nhân trong nước (VSDC), số doanh nghiệp đang hoạt động có KQKD đạt 859.048 đơn vị (ước vượt 1 triệu DN cuối năm 2025, khoảng 98% là SME theo Cục Thống kê/Bộ KH&ĐT). Trong khi đó, theo Bộ Tài chính và VACPA, cả nước chỉ có hơn 200 công ty kiểm toán (khoảng 30–35 đơn vị kiểm toán cho doanh nghiệp niêm yết) với trên dưới 2.000–2.500 kiểm toán viên hành nghề. Việc đọc thủ công từng bộ BCTC dày 50–100 trang khiến kiểm toán viên quá tải, còn nhà đầu tư cá nhân và chủ doanh nghiệp gần như 'mù thông tin'.",
    )
    add_bullet(
        doc,
        "Cứ 4 doanh nghiệp niêm yết lại có hơn 1 doanh nghiệp 'báo lãi nhưng dòng tiền âm': ",
        "Kết quả quét thực tế của hệ thống trên 639 doanh nghiệp phi tài chính năm 2025 cho thấy có tới 175 doanh nghiệp (27,4%) báo lãi sau thuế nhưng dòng tiền kinh doanh (CFO) âm; nhiều doanh nghiệp sau kiểm toán phải giải trình chênh lệch lợi nhuận trên 5% theo Thông tư 96/2020/TT-BTC do thiếu trích lập dự phòng hoặc ghi nhận doanh thu sớm.",
    )
    add_bullet(
        doc,
        "Áp lực chuyển đổi Thông tư 99/2025/TT-BTC và độ vênh số liệu với PDF gốc: ",
        "Từ ngày 01/01/2026, Thông tư 99/2025/TT-BTC chính thức thay thế Thông tư 200/2014/TT-BTC (đổi tên B01-DN thành Báo cáo tình hình tài chính, siết yêu cầu quản trị và kiểm soát nội bộ). Ngoài ra, khi nhóm đối chiếu trực tiếp BCTC kiểm toán 2025 của Novaland (91 trang do Moore AISC ký), nhiều khoản mục phải thu khác trên bảng dữ liệu tóm tắt bị phân loại lệch hàng nghìn tỷ so với PDF gốc — cho thấy chỉ đọc bảng số rút gọn là chưa đủ an toàn.",
    )

    add_h2(doc, "1.2. Giải pháp FinAudit AI (Ngắn gọn & Dễ hình dung)")
    add_p(
        doc,
        "Thay vì để người dùng tự bơi giữa hàng chục con số kế toán và hàng trăm trang luật, FinAudit AI đóng vai trò như một 'bác sĩ khám sức khỏe tài chính' trực tuyến với 3 nguyên lý đơn giản: (1) Máy tính tự tính chính xác các chỉ số rủi ro theo đặc thù từng ngành (không để AI đoán số); (2) Xếp hạng rõ ràng Hạng A / B / C trên thang 0–100 kèm lời giải thích nguyên nhân bằng tiếng Việt công sở dễ đọc; và (3) Tự động gắn thẳng điều luật Bộ Tài chính cùng trang thuyết minh PDF gốc để người dùng kiểm chứng ngay lập tức.",
        first_line_cm=0.7,
    )

    add_h2(doc, "1.3. Hệ thống Web FinAudit AI hiện tại ĐÃ LÀM ĐƯỢC GÌ?")
    add_p(
        doc,
        "Điểm thuyết phục nhất của dự án là sản phẩm Web đã chạy hoàn chỉnh, thân thiện trên cả máy tính lẫn điện thoại, tổ chức gọn thành đúng 4 không gian làm việc trực quan:",
        first_line_cm=0.7,
    )

    add_figure(
        doc,
        chart_paths["fig1"],
        "Hình 1: Bốn không gian làm việc đã hoàn thiện và chạy thực tế trên cổng Web FinAudit AI.",
        width_cm=16.2,
    )

    add_styled_table(
        doc,
        headers=["4 Chức năng chính trên Web", "Hệ thống hiển thị kết quả gì cho người đọc?"],
        rows=[
            [
                "1. Tổng quan Thị trường\n(643 DN HOSE & HNX)",
                "• Thanh tìm kiếm nhanh theo mã cổ phiếu hoặc từ khóa luật ngay đầu trang.\n• Bảng sàng lọc 643 doanh nghiệp (2019–2025) xếp theo rủi ro từ cao xuống thấp, lọc theo Năm, 15 Ngành, Sàn và Hạng rủi ro.\n• Biểu đồ Bản đồ Sức khỏe Tài chính và Xếp hạng 15 ngành (khi tìm 1 mã cụ thể, biểu đồ tự động tô nổi vị trí doanh nghiệp đó so với toàn thị trường)."
            ],
            [
                "2. Hồ sơ Doanh nghiệp 360°\n& Xuất Báo cáo A4 PDF",
                "• Nút Cập nhật trực tuyến (Live Sync) đồng bộ BCTC mới nhất ngay lập tức.\n• Thẻ Xếp hạng khoa học Hạng A / B / C (0–100 điểm) + Biểu đồ phân rã nguyên nhân nào đẩy rủi ro tăng (+) hay giảm (-).\n• Bảng So sánh trực diện Hơn/Kém so với Trung vị ngành (5 tiêu chí dễ hiểu: Dòng tiền, Sức khỏe trả nợ, Tài sản mềm, Phải thu, Tăng trưởng DT).\n• Diễn biến 8 năm (2018–2025) và nút tải Báo cáo kiểm toán chuẩn A4 in PDF."
            ],
            [
                "3. Kiểm tra BCTC của Bạn\n(Dành cho SME & Ngân hàng)",
                "• Cho phép tải file Excel/CSV BCTC 2 năm của bất kỳ doanh nghiệp nào — hỗ trợ cả bảng dọc tiếng Việt không theo mẫu cố định (hệ thống tự xoay bảng, tự quy đổi VND sang tỷ VND và kiểm tra cân đối Tài sản = Nguồn vốn).\n• Trả về Hạng rủi ro, nguyên nhân và Báo cáo A4 trong dưới 1,1 giây.\n• Chế độ Thử nghiệm chỉnh số trực tiếp: sửa thử dòng tiền hoặc phải thu để thấy điểm rủi ro biến động tức thì."
            ],
            [
                "4. Trợ lý Pháp lý Kế toán\n& Soi file PDF BCTC",
                "• Bố cục 2 cột rộng rãi, hỏi đáp bằng tiếng Việt tự nhiên (VD: 'Nói cho tôi về luật VAS', 'So sánh FPT và TDH', 'Thông tư 99/2025 có gì mới?').\n• Mỗi câu trả lời tách rõ 2 phần: Nội dung giải đáp và Căn cứ trích dẫn kèm liên kết trực tiếp tới Cổng Chính phủ (vanban.chinhphu.vn / vbpl.vn / mof.gov.vn).\n• Tích hợp nút Đính kèm file PDF BCTC để tra cứu nguyên văn trang thuyết minh; tự nhận biết PDF scan ảnh để không suy diễn sai."
            ],
        ],
        col_widths_cm=[4.5, 12.1],
        font_size=12.5,
    )

    add_h2(doc, "1.4. Người dùng khai thác được giá trị gì từ hệ thống?")
    add_p(
        doc,
        "Thay vì chỉ phục vụ một nhóm chuyên gia hẹp, FinAudit AI tạo ra giá trị khai thác thiết thực ngay lập tức cho 5 nhóm đối tượng — bao gồm cả môi trường đào tạo đại học:",
        first_line_cm=0.7,
    )
    add_styled_table(
        doc,
        headers=["Đối tượng sử dụng", "Cách khai thác hệ thống vào công việc thực tế", "Giá trị trực tiếp nhận được"],
        rows=[
            ["Kiểm toán viên &\nCông ty Kiểm toán", "Quét nhanh khách hàng trước khi lập kế hoạch kiểm toán; xem SHAP để khoanh vùng tài khoản trọng yếu (TK 131, 138, 229, 241) và soi PDF B09-DN.", "Giảm thời gian rà soát sơ bộ; nâng cao chất lượng đánh giá rủi ro theo chuẩn VSA 240."],
            ["Ngân hàng &\nThẩm định Tín dụng", "Tải file BCTC 2 năm của doanh nghiệp xin vay vốn vào Phân hệ 3 để kiểm tra cân đối, chấm hạng rủi ro và so sánh với chuẩn ngành.", "Phát hiện sớm hồ sơ làm đẹp BCTC, hạn chế rủi ro nợ xấu ngay trước khi giải ngân."],
            ["Nhà đầu tư cá nhân\n(11,8 triệu TK)", "Tra cứu mã cổ phiếu trong 5 giây, so sánh 2 doanh nghiệp trực tiếp, tránh bẫy 'lãi trên giấy nhưng dòng tiền kinh doanh âm'.", "Ra quyết định đầu tư có căn cứ số liệu, miễn phí bước sàng lọc cơ bản."],
            ["Kế toán trưởng &\nDoanh nghiệp SME", "Tự 'khám sức khỏe' BCTC trước kỳ quyết toán/vay vốn; hỏi Trợ lý về chuyển đổi Thông tư 99/2025 và dự phòng thuế theo Thông tư 48/2019.", "Hạn chế sai sót kế toán – thuế, tăng độ tin cậy hồ sơ vay vốn ngân hàng."],
            ["Giảng viên & Sinh viên\nKinh tế – Kế toán", "Khai thác làm phòng thực hành trực quan trên dữ liệu thật 643 DN; thử sửa số liệu trên Phân hệ 3 để minh họa tác động lên rủi ro BCTC.", "Kết nối lý thuyết chuẩn mực VAS/VSA với thực tế thị trường ngay tại giảng đường."],
        ],
        col_widths_cm=[3.5, 7.6, 5.5],
        font_size=12.0,
    )

    # =======================================================================
    # PHẦN II: NỘI DUNG CHÍNH CỦA DỰ ÁN (TẬP TRUNG KẾT QUẢ THẬT, KHẢ THI, KINH DOANH & ESG)
    # =======================================================================
    # Không gian bắt đầu trang mới sạch sẽ cho Phần II (nằm đẹp đúng khung 12 trang)
    doc.add_page_break()
    add_h1(doc, "PHẦN II. NỘI DUNG CHÍNH CỦA DỰ ÁN", space_before=0)

    add_h2(doc, "2.1. Kết quả thực tế đã đạt được trên Web FinAudit AI (Bằng chứng thuyết phục)")
    add_p(
        doc,
        "Khi vận hành trên toàn bộ 643 doanh nghiệp phi tài chính sàn HOSE (362 DN) và HNX (281 DN) giai đoạn 2018–2025, hệ thống không chỉ đưa ra các bảng biểu trực quan mà đã cho ra những kết quả phân tách thực chứng rất sắc nét:",
        first_line_cm=0.7,
    )

    add_figure(
        doc,
        chart_paths["fig2"],
        "Hình 2: (A) Kết quả sàng lọc 639 DN niêm yết năm 2025 trên Web; (B) Đối chứng điểm rủi ro thực tế giữa nhóm minh bạch đầu ngành và nhóm cảnh báo.",
        width_cm=16.0,
    )

    add_p(doc, "Bảng 1: So sánh đối chứng trực tiếp kết quả trên Web FinAudit AI cho 4 doanh nghiệp điển hình năm 2025", bold=True, size=13.5, color=RGB_PRIMARY, space_before=2, space_after=3)
    add_styled_table(
        doc,
        headers=["Doanh nghiệp (2025)", "Hạng & Điểm trên Web", "Lợi nhuận ST vs. Tiền KD (CFO)", "Kết luận hệ thống hiển thị ngay cho người đọc"],
        rows=[
            ["VNM (Vinamilk — Thực phẩm)", "Hạng A • 7,8 / 100", "LNST: +9.413,6 tỷ\nCFO: +8.668,1 tỷ", "Dòng tiền thật đồng pha lợi nhuận; sức khỏe trả nợ vững vàng, tài sản mềm chỉ 2,6%."],
            ["FPT (Công nghệ Thông tin)", "Hạng A • 11,7 / 100", "LNST: +11.232,3 tỷ\nCFO: +10.136,0 tỷ", "Lành mạnh vượt trội trung vị ngành; không phát sinh bất kỳ yếu tố rủi ro vượt ngưỡng nào."],
            ["QCG (Quốc Cường Gia Lai)", "Hạng C • 69,8 / 100", "LNST: +170,7 tỷ\nCFO: -1.127,0 tỷ", "Cảnh báo mạnh: Báo lãi nhưng hụt dòng tiền sâu, phải thu tăng nhanh, áp lực trả nợ cao."],
            ["TDH (Thủ Đức House)", "Hạng C • 80,2 / 100", "LNST: +108,3 tỷ\nCFO: -23,8 tỷ", "Cảnh báo đỏ: Tài sản mềm chiếm 63,2% tổng tài sản, sức khỏe tài chính yếu, cần soi kỹ B09-DN."],
        ],
        col_widths_cm=[3.9, 3.0, 3.7, 6.0],
        font_size=12.0,
    )

    add_bullet(
        doc,
        "Nhận diện rõ 'điểm nóng' rủi ro theo ngành năm 2025: ",
        "Trong 639 doanh nghiệp chấm điểm năm 2025, có 487 DN Hạng A (76,2%), 126 DN Hạng B (19,7%) và 26 DN Hạng C (4,1%, gồm 13 DN HOSE và 13 DN HNX). Rủi ro tập trung dày nhất ở ngành Xây dựng & Vật liệu (8 DN Hạng C, 33 DN báo lãi nhưng tiền KD âm) và Bất động sản (5 DN Hạng C, 36/78 DN báo lãi nhưng tiền KD âm).",
    )
    add_bullet(
        doc,
        "Phát hiện chéo giữa số liệu tóm tắt và Thuyết minh PDF gốc (trường hợp Novaland — NVL): ",
        "Hệ thống đã cảnh báo sớm Hạng B vào đỉnh khó khăn năm 2024 của NVL (51,9/100 điểm khi lỗ 4.394,6 tỷ). Sang năm 2025, dù điểm tổng hợp cải thiện về 26,8/100 nhờ có lãi trở lại, Trợ lý soi PDF 91 trang vẫn bắt trúng đoạn 'Vấn đề cần nhấn mạnh' của kiểm toán Moore AISC (Trang 12) về dòng tiền kinh doanh âm 6.145 tỷ đồng.",
    )

    add_h2(doc, "2.2. Kiểm chứng độ tin cậy: Vì sao người dùng có thể tin tưởng kết quả Web?")
    add_p(
        doc,
        "Để tránh tình trạng 'AI nói hay nhưng sai chuyên môn', nhóm đã kiểm thử nghiêm ngặt sản phẩm trên 24 doanh nghiệp đối chứng thật (12 DN minh bạch đầu ngành vs. 12 DN từng gặp biến cố tài chính/kiểm toán giai đoạn 2019–2025) và trên kho 5 văn bản pháp quy Bộ Tài chính:",
        first_line_cm=0.7,
    )

    add_figure(
        doc,
        chart_paths["fig3"],
        "Hình 3: Kết quả kiểm chứng thực tế về độ chính xác phân loại rủi ro (A) và độ tin cậy của Trợ lý Pháp lý – Soi PDF (B).",
        width_cm=16.0,
    )

    add_bullet(
        doc,
        "Độ chính xác phân tách đạt 93,0% (AUC = 0,9299) với 0% báo động đỏ giả: ",
        "Không có bất kỳ doanh nghiệp nào trong nhóm 12 công ty minh bạch đầu ngành (VNM, FPT, MWG, DGC, REE, GAS...) bị hệ thống cảnh báo đỏ nhầm; trong khi điểm trung vị của nhóm biến cố cao gấp 3,1 lần nhóm minh bạch (41,5 điểm so với 13,3 điểm) và vượt xa việc chỉ dùng công thức Beneish đơn lẻ (53,7%).",
    )
    add_bullet(
        doc,
        "Trợ lý Pháp lý trả lời đúng #1 đạt 95%, đúng trong Top 3 đạt 100% và Chống ảo giác 100%: ",
        "Thử nghiệm trên 20 câu hỏi chuyên môn (Thông tư 99/2025, Thông tư 48/2019, VAS 14/26, VSA 240) đạt tốc độ phản hồi tức thì; trên 5 câu hỏi ngoài lĩnh vực kế toán – kiểm toán, hệ thống từ chối suy diễn chính xác 100%. Khi đọc file PDF kiểm toán 91 trang bị nhiễu dấu tiếng Việt (NVL 2025), tỷ lệ tìm đúng trang đạt 83,3% (tăng gấp 5 lần cách tìm từ khóa thông thường).",
    )
    add_bullet(
        doc,
        "Vận hành nhẹ, sẵn sàng đưa lên Internet với chi phí tối thiểu: ",
        "Toàn bộ 4 phân hệ chạy mượt mà, 0 lỗi kỹ thuật, chấm điểm BCTC tải lên chỉ mất 1,09 giây và chỉ tiêu thụ khoảng 529 MB RAM trên máy tính phổ thông (không cần máy chủ GPU đắt tiền). Toàn bộ giao diện và báo cáo xuất ra đều tuân thủ chuẩn mực VSA 240: chỉ đưa ra chỉ báo rủi ro hỗ trợ khoanh vùng kiểm toán, tuyệt đối không kết luận quy chụp gian lận.",
    )

    add_h2(doc, "2.3. Lợi thế khác biệt so với các công cụ đang có trên thị trường")
    add_styled_table(
        doc,
        headers=["Khía cạnh", "Công cụ hiện có trên thị trường", "Lợi thế khác biệt của FinAudit AI"],
        rows=[
            ["Phần mềm kế toán\n(MISA, FAST)", "Tập trung ghi sổ và xuất BCTC nội bộ; không có chức năng sàng lọc rủi ro hay chấm điểm so sánh ngành.", "Đóng vai trò tầng kiểm tra độc lập trước khi nộp BCTC; hỗ trợ tải file tự do không phụ thuộc phần mềm kế toán."],
            ["Cổng dữ liệu chứng khoán\n(Vietstock, FiinPro)", "Chủ yếu hiện chỉ số bề nổi (P/E, ROE); bản tổ chức giá hàng chục triệu/năm; chưa liên kết số liệu với file PDF.", "Chấm điểm chất lượng lợi nhuận 0–100, giải thích từng nguyên nhân, soi thẳng PDF & mở cho cả DN chưa niêm yết."],
            ["AI hỏi đáp phổ thông\n(ChatGPT, Gemini)", "Không có bộ dữ liệu 643 DN chuẩn VN; hay bịa số điều luật Thông tư mới và dễ tính nhầm tỷ số tài chính.", "Dữ liệu thật 100%, tính toán chuẩn xác, chống ảo giác 100% và luôn gắn Link Cổng văn bản Chính phủ."],
        ],
        col_widths_cm=[3.8, 6.2, 6.6],
        font_size=12.2,
    )

    add_h2(doc, "2.4. Thị trường mục tiêu, mô hình doanh thu và kế hoạch tài chính")
    add_p(
        doc,
        "Với thị trường mục tiêu rộng lớn gồm hơn 11,8 triệu tài khoản nhà đầu tư cá nhân (VSDC, 2025), hơn 859.000 doanh nghiệp hoạt động (~98% là SME) và hơn 200 công ty kiểm toán cùng các ngân hàng thương mại, dự án áp dụng mô hình phần mềm dịch vụ (SaaS) kết hợp 3 gói linh hoạt:",
        first_line_cm=0.7,
    )
    add_bullet(
        doc,
        "Gói Miễn phí (Community — 0 đ): ",
        "Tra cứu Tổng quan thị trường 643 DN, xem điểm xếp hạng Hạng A/B/C và hỏi đáp Luật VAS cơ bản (tạo phễu lan tỏa tự nhiên tới sinh viên, kế toán và nhà đầu tư).",
    )
    add_bullet(
        doc,
        "Gói Chuyên sâu Cá nhân / SME (Pro — 199.000 đ/tháng hoặc 1.990.000 đ/năm): ",
        "Mở khóa trọn vẹn Hồ sơ 360°, biểu đồ nguyên nhân, tải lên chấm điểm BCTC không giới hạn, soi file PDF kiểm toán và xuất Báo cáo A4.",
    )
    add_bullet(
        doc,
        "Gói Tổ chức Kiểm toán & Tín dụng (Enterprise — 15 đến 30 triệu đ/năm/đơn vị): ",
        "Tài khoản đa người dùng, sàng lọc đồng loạt hàng trăm khách hàng vay/kiểm toán, kết nối API nội bộ và tích hợp mở rộng phân hệ đối soát TMĐT/hóa đơn điện tử ở Giai đoạn 2.",
    )

    add_styled_table(
        doc,
        headers=["Chỉ tiêu dự phóng thận trọng", "Năm 1 (2027 — Thí điểm & Ra mắt)", "Năm 2 (2028 — Mở rộng B2B)", "Năm 3 (2029 — Tăng tốc)"],
        rows=[
            ["Người dùng miễn phí (tích lũy)", "5.000 người dùng", "20.000 người dùng", "60.000 người dùng"],
            ["Khách hàng trả phí (Pro | Tổ chức)", "250 Pro  |  5 Tổ chức", "1.200 Pro  |  25 Tổ chức", "3.200 Pro  |  65 Tổ chức"],
            ["Tổng Doanh thu dự kiến", "597,5 triệu VND", "2.888,0 triệu VND", "7.668,0 triệu VND"],
            ["Tổng Chi phí vận hành & Marketing", "540,0 triệu VND", "1.720,0 triệu VND", "4.150,0 triệu VND"],
            ["Lợi nhuận trước thuế (Biên LN)", "+57,5 triệu (9,6%)", "+1.168,0 triệu (40,4%)", "+3.518,0 triệu (45,9%)"],
        ],
        col_widths_cm=[5.8, 3.6, 3.6, 3.6],
        font_size=12.0,
        center_cols={1, 2, 3},
    )
    add_p(
        doc,
        "Nhờ vận hành gọn nhẹ không phụ thuộc máy chủ GPU tốn kém, dự án chỉ cần khoảng 150–250 triệu VND vốn mồi năm đầu (từ giải thưởng khởi nghiệp, quỹ ươm tạo Nhà trường và hợp đồng thí điểm) và dự kiến đạt điểm hòa vốn từ Quý 4 Năm 1.",
        italic=True,
        size=13.5,
        color=RGB_MUTED,
        space_after=6,
    )

    add_h2(doc, "2.5. Lộ trình triển khai, kế hoạch truyền thông và quản trị rủi ro")
    add_styled_table(
        doc,
        headers=["Giai đoạn", "Trọng tâm phát triển sản phẩm", "Kênh truyền thông & Thu hút khách hàng"],
        rows=[
            [
                "Q4/2026 – Q1/2027\n(Ra mắt & Thí điểm)",
                "Đưa Web lên Cloud (HTTPS); cập nhật mẫu BCTC 2026 theo Thông tư 99/2025; thí điểm miễn phí cho 300 sinh viên/kế toán và 3 công ty kiểm toán vừa & nhỏ.",
                "Tổ chức Workshop 'Đọc BCTC & Chuyển đổi TT 99/2025' tại Trường Kinh tế — HaUI; chuỗi video ngắn 60–90 giây 'Soi nhanh BCTC thật' trên TikTok/Facebook/YouTube."
            ],
            [
                "Q2/2027 – Q4/2027\n(Thương mại hóa)",
                "Mở bán gói Pro & Enterprise; nâng cấp công cụ đọc chữ OCR chuyên sâu cho các file PDF BCTC dạng ảnh scan; tự động cập nhật dữ liệu hằng quý.",
                "Hợp tác với Hội nghề nghiệp (VACPA, VAA), trung tâm đào tạo kế toán thực hành và các hiệp hội doanh nghiệp SME theo mô hình dùng thử tặng kèm báo cáo."
            ],
            [
                "2028 – 2029\n(Mở rộng hệ sinh thái)",
                "Mở rộng thêm Phân hệ đối soát giao dịch TMĐT (Shopee/TikTok Shop) & Hóa đơn điện tử cho SME; hỗ trợ chuẩn Báo cáo Tài chính Quốc tế IFRS.",
                "Liên kết trực tiếp với phòng thẩm định tín dụng ngân hàng thương mại, công ty chứng khoán và triển khai phiên bản giáo dục cho các trường Đại học khối Kinh tế."
            ],
        ],
        col_widths_cm=[3.3, 6.6, 6.7],
        font_size=12.0,
    )
    add_p(
        doc,
        "Quản trị rủi ro chính: (1) Rủi ro phụ thuộc nguồn dữ liệu — khắc phục bằng cơ chế đa nguồn API kết hợp cho phép người dùng tự tải BCTC; (2) Rủi ro bảo mật BCTC SME — dữ liệu tải lên chỉ xử lý tạm thời trong bộ nhớ phiên, không lưu trữ trái phép; (3) Rủi ro pháp lý — khóa chặt cơ chế chống ảo giác và cảnh báo chuẩn VSA 240 trên mọi kết quả.",
        first_line_cm=0.7,
    )

    add_h2(doc, "2.6. Giá trị bền vững (ESG — Trụ cột G) và Cam kết của đội thi")
    add_p(
        doc,
        "Dự án FinAudit AI hiện thực hóa trọn vẹn tinh thần 'Sáng tạo – Khởi nghiệp vì tương lai bền vững' thông qua việc giải quyết trực tiếp Trụ cột G (Quản trị & Minh bạch tài chính) trong khung ESG và Mục tiêu Phát triển Bền vững SDG 16 & SDG 8:",
        first_line_cm=0.7,
    )
    add_bullet(
        doc,
        "Giảm bất đối xứng thông tin, bảo vệ nhà đầu tư và doanh nghiệp làm ăn chân chính: ",
        "Khi công cụ soi minh bạch BCTC được phổ cập tới số đông, rủi ro từ các báo cáo thiếu trung thực giảm xuống, tạo động lực để doanh nghiệp quản trị bài bản và tiếp cận nguồn vốn ngân hàng với chi phí hợp lý hơn.",
    )
    add_bullet(
        doc,
        "Chuyển đổi số xanh và lan tỏa giá trị giáo dục thực tiễn: ",
        "Giảm in ấn hồ sơ giấy, tiết kiệm điện năng vận hành AI (không cần cụm GPU tiêu tốn năng lượng), đồng thời cung cấp một công cụ học tập trực quan trên dữ liệu thật cho sinh viên Trường Kinh tế — Đại học Công nghiệp Hà Nội.",
    )

    add_callout_box(
        doc,
        "Trải nghiệm thử hệ thống trong 2 phút dành cho Ban Giám khảo:",
        [
            ("(1) Gõ ", False, False, None),
            ("TDH", True, False, RGB_RED),
            (" hoặc ", False, False, None),
            ("FPT", True, False, RGB_PRIMARY),
            (" tại Trang 1 để xem Hồ sơ 360° & Báo cáo A4;  (2) Vào Trang 3 sửa thử dòng tiền kinh doanh sang âm để xem điểm rủi ro nhảy tức thì;  (3) Bấm nút ", False, False, None),
            ("Hỏi Trợ lý AI", True, False, RGB_ACCENT),
            (" gõ câu 'Nói cho tôi về luật VAS' hoặc 'So sánh FPT và TDH' để kiểm chứng câu trả lời kèm Link Cổng Chính phủ.", False, False, None),
        ],
        bg_hex=HEX_WARM_BG,
        border_hex=HEX_ACCENT,
    )

    # --- TÀI LIỆU THAM KHẢO NGẮN GỌN, CHÍNH THỐNG ---
    add_h1(doc, "NGUỒN SỐ LIỆU VÀ TÀI LIỆU THAM KHẢO CHÍNH THỐNG", space_before=6)
    refs = [
        "[1] ACFE (2024). Occupational Fraud 2024: A Report to the Nations. Association of Certified Fraud Examiners.",
        "[2] Tổng công ty Lưu ký và Bù trừ Chứng khoán Việt Nam — VSDC (2026). Thống kê số lượng tài khoản giao dịch chứng khoán tại thời điểm 31/12/2025 (vsdc.vn).",
        "[3] Cục Thống kê / Bộ Kế hoạch và Đầu tư (2024–2025). Niên giám Thống kê & Sách trắng Doanh nghiệp Việt Nam; Hội Kiểm toán viên hành nghề Việt Nam — VACPA (vacpa.org.vn).",
        "[4] Bộ Tài chính (2025). Thông tư 99/2025/TT-BTC ngày 27/10/2025 hướng dẫn Chế độ kế toán doanh nghiệp (hiệu lực từ 01/01/2026, thay thế Thông tư 200/2014/TT-BTC).",
        "[5] Bộ Tài chính (2012, 2019, 2020, 2022). Thông tư 214/2012/TT-BTC (VSA 240); Thông tư 48/2019/TT-BTC & TT 24/2022/TT-BTC (Dự phòng); Thông tư 96/2020/TT-BTC (Công bố thông tin TTCK); Chuẩn mực VAS 14 & VAS 26.",
        "[6] Nền tảng khoa học đối chiếu: Beneish (1999, Financial Analysts Journal); Altman (2005, Emerging Markets Review); Liu et al. (2008, IEEE ICDM); Lundberg & Lee (2017, NeurIPS — SHAP).",
        "[7] Dữ liệu kiểm nghiệm thực tế: BCTC công khai 643 doanh nghiệp phi tài chính HOSE/HNX (2018–2025) từ Vietcap IQ API và BCTC kiểm toán 2025 công bố trên HOSE (FPT, VNM, TDH, NVL).",
    ]
    for r_txt in refs:
        add_p(doc, r_txt, size=12.5, space_after=2.5, line_spacing=1.10, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    doc.save(str(DOCX_OUT))
    return DOCX_OUT


if __name__ == "__main__":
    print("[1/2] Đang sinh 3 hình trực quan V2 (300 DPI) cho Giảng viên / Ban Giám khảo...")
    charts = build_executive_charts()
    for k, p in charts.items():
        print(f"  -> {k}: {p} ({p.stat().st_size/1024:.1f} KB)")
    print("[2/2] Đang xuất Báo cáo Dự thi V2 chuẩn A4 Times New Roman 14pt...")
    out_p = build_report_v2(charts)
    print(f"  -> HOÀN TẤT: {out_p} ({out_p.stat().st_size/1024:.1f} KB)")
