"""
BỘ XUẤT HỒ SƠ KIỂM TOÁN PHÁP CHỨNG (HTML CHUẨN A4 IN RA PDF)
=============================================================
Tạo báo cáo hoàn chỉnh 1 trang A4 sắc nét cho từng doanh nghiệp, sẵn sàng in PDF
hoặc đính kèm Hồ sơ Kiểm toán / Hồ sơ Thẩm định Tín dụng.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
import sys
from typing import Any

import pandas as pd

_CUR_DIR = str(Path(__file__).resolve().parent)
if _CUR_DIR not in sys.path:
    sys.path.insert(0, _CUR_DIR)

from ui_components import BRAND_EMBLEM_SVG, format_rag_markdown_to_html, translate_altman_zone, trim_excerpt_clean


def _fmt_bn(val: Any) -> str:
    if val is None or pd.isna(val):
        return "N/A"
    return f"{float(val):,.2f} tỷ"


def _fmt_num(val: Any, digits: int = 3) -> str:
    if val is None or pd.isna(val):
        return "N/A"
    return f"{float(val):.{digits}f}"


def generate_html_audit_report(
    row: pd.Series,
    rag_brief: dict[str, Any] | None = None,
) -> str:
    """Sinh mã HTML chuẩn A4 có CSS in ấn đẹp mắt (Print-to-PDF) từ dữ liệu thật của doanh nghiệp."""
    ticker = escape(str(row.get("ticker", "N/A")))
    year = int(row.get("year", 2025))
    comp_name = escape(str(row.get("company_name", ticker)))
    sector = escape(str(row.get("icb_sector_vi", "Phi tài chính")))
    exchange = escape(str(row.get("exchange", "HOSE/HNX")))
    score = float(row.get("composite_risk_score", 0.0)) if pd.notna(row.get("composite_risk_score")) else 0.0
    tier = escape(str(row.get("risk_tier", "Chưa xếp hạng")))

    if score >= 65.0:
        tier_bg, tier_fg, tier_bd = "#FFF1F2", "#BE123C", "#FECDD3"
    elif score >= 40.0:
        tier_bg, tier_fg, tier_bd = "#FFF7ED", "#C2410C", "#FDBA74"
    else:
        tier_bg, tier_fg, tier_bd = "#ECFDF5", "#059669", "#A7F3D0"

    shap_labels = [
        ("shap_risk_cfo", "CFO/Tổng TS thấp (Dòng tiền yếu/âm)"),
        ("shap_risk_altman", "Altman Z'' thấp (Sức khỏe tài chính yếu)"),
        ("shap_risk_dsri", "DSRI (Phải thu KH tăng nhanh hơn DT)"),
        ("shap_risk_tata", "TATA (Dồn tích lợi nhuận trên giấy)"),
        ("shap_risk_sgi", "SGI (Tăng trưởng DT quá nóng)"),
        ("shap_risk_aqi", "AQI (Tài sản dài hạn mờ ám tăng)"),
        ("shap_risk_srr", "SRR (Phải thu khác & Trả trước cao)"),
        ("shap_risk_gmi", "GMI (Biên lãi gộp suy giảm)"),
        ("shap_risk_depi", "DEPI (Tốc độ khấu hao TSCĐ giảm)"),
        ("shap_risk_ar_rev", "Phải thu NH / Doanh thu cao"),
        ("shap_risk_lvgi", "LVGI (Đòn bẩy nợ vay tăng nhanh)"),
        ("shap_risk_sgai", "SGAI (Chi phí BH & QLDN phình to)"),
    ]
    shap_items = []
    for col, lbl in shap_labels:
        if col in row and pd.notna(row[col]):
            shap_items.append((lbl, float(row[col])))
    shap_items.sort(key=lambda x: abs(x[1]), reverse=True)

    shap_rows_html = ""
    for lbl, val in shap_items[:8]:
        sign = "+" if val >= 0 else ""
        color = "#BE123C" if val >= 0.5 else ("#059669" if val <= -0.5 else "#4B635B")
        direction = "Đẩy rủi ro tăng" if val > 0.2 else ("Kéo rủi ro giảm" if val < -0.2 else "Trung tính")
        shap_rows_html += (
            f"<tr><td>{escape(lbl)}</td>"
            f"<td style='text-align:right;font-weight:700;color:{color};font-family:monospace;'>{sign}{val:.2f} đ</td>"
            f"<td style='color:{color};'>{direction}</td></tr>"
        )

    rag_html = ""
    if rag_brief and rag_brief.get("top_driver_briefs"):
        for drv in rag_brief["top_driver_briefs"]:
            cite_items = []
            for c in drv.get("legal_citations", []):
                ex_clean, _ = trim_excerpt_clean(c.get("excerpt", ""), 260)
                cite_items.append(
                    f"<li><strong>{escape(c['citation'])}</strong>: {format_rag_markdown_to_html(ex_clean)}</li>"
                )
            cites = "".join(cite_items)
            b09_items = ", ".join(
                f"{escape(b['label_vi'])}: <strong>{b['value_bn_vnd']:,.2f} tỷ</strong>"
                for b in drv.get("b09_note_evidence", [])[:5]
            )
            pdf_blocks = []
            for p in drv.get("pdf_evidence", []):
                p_clean, _ = trim_excerpt_clean(p.get("excerpt", ""), 260)
                pdf_blocks.append(
                    f"<div class='pdf-quote'><strong>{escape(p['citation'])}</strong>: {format_rag_markdown_to_html(p_clean)}</div>"
                )
            pdf_items = "".join(pdf_blocks)
            rag_html += f"""
            <div class="rag-box">
              <div class="rag-title">Cờ rủi ro: {escape(drv['driver_label_vi'])} <span class="rag-pts">(+{drv['shap_points']:.2f}đ SHAP)</span></div>
              <ul class="cite-list">{cites}</ul>
              {f'<div class="b09-line"><strong>Bóc tách Thuyết minh B09-DN:</strong> {b09_items}</div>' if b09_items else ''}
              {pdf_items}
            </div>
            """
    else:
        rag_html = (
            "<p style='color:#059669;font-weight:600;'>Không phát sinh cờ đỏ SHAP vượt ngưỡng (+0.5đ). "
            "Các chỉ số trọng yếu nằm trong vùng lành mạnh so với trung vị ngành ICB.</p>"
        )

    def _bar_html(val: Any) -> str:
        v = max(0.0, min(100.0, float(val))) if val is not None and pd.notna(val) else 0.0
        col = "#BE123C" if v >= 65 else ("#B45309" if v >= 40 else "#059669")
        return f"<div class='bar-track'><div class='bar-fill' style='width:{v:.1f}%;background:{col};'></div></div>"

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Hồ sơ Pháp chứng BCTC — {ticker} ({year}) | FinAudit AI</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@600;700;800&family=Merriweather:wght@700;900&family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  @page {{ size: A4; margin: 14mm; }}
  body {{ font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; font-size: 15px; color: #132A23; background: #FAF8F5; margin: 0; padding: 20px; }}
  .sheet {{ max-width: 920px; margin: 0 auto; background: #FFFFFF; border: 1px solid #C9D8D2; border-radius: 5px; padding: 28px 32px; box-shadow: 0 4px 16px rgba(6,78,59,0.08); }}
  .banner {{ background: linear-gradient(135deg, #043628 0%, #064E3B 52%, #0F766E 100%); color: #FFFFFF; border-bottom: 4px solid #C2410C; padding: 20px 24px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; gap: 16px; }}
  .brand-row {{ display: flex; align-items: center; gap: 8px; font-family: 'Merriweather', Georgia, serif; font-size: 14px; font-weight: 700; letter-spacing: 0.3px; color: #E2EFEA; }}
  .dual-gold {{ color: #FDE68A; }}
  .banner h1 {{ margin: 6px 0 4px; font-size: 24px; font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; font-weight: 900; letter-spacing: -0.01em; line-height: 1.25; }}
  .banner .sub {{ font-size: 14px; color: #E2EFEA; }}
  .score-box {{ background: {tier_bg}; color: {tier_fg}; border: 2px solid {tier_bd}; border-radius: 5px; padding: 12px 18px; text-align: center; min-width: 160px; }}
  .score-num {{ font-size: 31px; font-weight: 800; line-height: 1.1; font-family: 'JetBrains Mono', monospace; }}
  .score-tier {{ font-size: 13.5px; font-weight: 700; margin-top: 4px; }}
  h2 {{ font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; font-size: 17.5px; font-weight: 900; color: #064E3B; border-bottom: 2px solid #C9D8D2; padding-bottom: 6px; margin: 22px 0 12px; }}
  h2 span {{ color: #C2410C; }}
  .scale-strip {{ display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; background: #FAF8F5; border: 1px solid #C9D8D2; border-radius: 4px; padding: 8px 13px; font-size: 13.5px; margin-bottom: 10px; }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .kpi {{ background: #FAF8F5; border: 1px solid #C9D8D2; border-top: 3.5px solid #064E3B; border-radius: 5px; padding: 12px 14px; }}
  .kpi-lbl {{ font-size: 13px; color: #4B635B; font-weight: 700; }}
  .kpi-val {{ font-size: 20px; font-weight: 800; color: #132A23; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }}
  .kpi-sub {{ font-size: 12.8px; color: #4B635B; margin-top: 2px; }}
  .bar-track {{ width: 100%; height: 7px; background: #E4ECE8; border-radius: 3px; overflow: hidden; margin-top: 7px; }}
  .bar-fill {{ height: 100%; border-radius: 3px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14.5px; }}
  th, td {{ padding: 9px 11px; border-bottom: 1px solid #D1DDD8; text-align: left; }}
  th {{ background: #F0F4F2; color: #064E3B; font-family: 'Roboto', Arial, sans-serif; font-weight: 700; }}
  .rag-box {{ background: #FAF8F5; border: 1px solid #C9D8D2; border-left: 4px solid #064E3B; border-radius: 5px; padding: 14px 16px; margin-bottom: 10px; font-size: 14.5px; line-height: 1.62; }}
  .rag-title {{ font-family: 'Roboto', Arial, sans-serif; font-weight: 800; color: #132A23; margin-bottom: 6px; }}
  .rag-pts {{ color: #BE123C; font-family: 'JetBrains Mono', monospace; }}
  .cite-list {{ margin: 4px 0 6px 18px; padding: 0; color: #132A23; }}
  .cite-list li {{ margin-bottom: 5px; }}
  .b09-line {{ background: #F0FDFA; border: 1px solid #99F6E4; border-radius: 4px; padding: 9px 12px; margin-top: 6px; font-size: 14px; color: #064E3B; }}
  .pdf-quote {{ background: #FFF7ED; border: 1px solid #FDBA74; border-radius: 4px; padding: 9px 12px; margin-top: 6px; font-size: 14px; color: #9A3412; }}
  .disclaimer {{ margin-top: 20px; padding: 14px 16px; background: #F0F4F2; border-top: 3px solid #064E3B; border-radius: 5px; font-size: 13.8px; color: #4B635B; line-height: 1.6; }}
  .print-btn {{ margin-bottom: 12px; padding: 10px 20px; background: #C2410C; color: #fff; border: 2px solid #9A3412; border-radius: 4px; cursor: pointer; font-family: 'Roboto', sans-serif; font-weight: 700; font-size: 15px; }}
  @media print {{ .print-btn {{ display: none; }} body {{ background: #fff; padding: 0; }} .sheet {{ box-shadow: none; border: none; padding: 0; }} }}
</style>
</head>
<body>
  <div style="max-width:900px;margin:0 auto;text-align:right;">
    <button class="print-btn" onclick="window.print()">In / Lưu thành PDF chuẩn A4</button>
  </div>
  <div class="sheet">
    <div class="banner">
      <div>
        <div class="brand-row">{BRAND_EMBLEM_SVG} <span>FINAUDIT <span class="dual-gold">AI</span> — FINFORENSICS • HỒ SƠ PHÁP CHỨNG BCTC</span></div>
        <h1>{ticker} — <span class="dual-gold">{comp_name}</span></h1>
        <div class="sub">Năm tài chính: <strong>{year}</strong> • Sàn: <strong>{exchange}</strong> • Ngành ICB: <strong>{sector}</strong> • Xuất lúc: {now_str}</div>
      </div>
      <div class="score-box">
        <div class="score-num">{score:.1f} / 100</div>
        <div class="score-tier">{tier}</div>
      </div>
    </div>

    <h2>1. Tóm tắt <span>4 Trụ cột Pháp chứng</span> &amp; Số liệu BCTC Cốt lõi</h2>
    <div class="scale-strip">
      <span><strong>Thang điểm Rủi ro (0–100đ):</strong></span>
      <span><strong style="color:#059669;">&lt; 40đ</strong> Thấp (An toàn)</span>
      <span><strong style="color:#B45309;">40–64.9đ</strong> Trung bình (Theo dõi)</span>
      <span><strong style="color:#BE123C;">&ge; 65đ</strong> Cao (Cảnh báo Đỏ)</span>
    </div>
    <div class="grid-4">
      <div class="kpi">
        <div class="kpi-lbl">1. Nguy cơ Thổi số (30%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_beneish'), 1)} đ</div>
        <div class="kpi-sub">Chỉ số Beneish = {_fmt_num(row.get('beneish_m_score'), 2)} (Ngưỡng -1.78)</div>
        {_bar_html(row.get('score_beneish'))}
      </div>
      <div class="kpi">
        <div class="kpi-lbl">2. Sức khỏe Trả nợ (25%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_altman'), 1)} đ</div>
        <div class="kpi-sub">{escape(translate_altman_zone(row.get('altman_zone', '')))} (Altman = {_fmt_num(row.get('altman_z_double_prime'), 2)})</div>
        {_bar_html(row.get('score_altman'))}
      </div>
      <div class="kpi">
        <div class="kpi-lbl">3. Chất lượng Dòng tiền (20%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_cash_quality'), 1)} đ</div>
        <div class="kpi-sub">Tiền KD/TS: {_fmt_num(float(row.get('cfo_to_assets', 0))*100, 1)}% | TS mềm: {_fmt_num(float(row.get('sensitive_receivables_ratio', 0))*100, 1)}%</div>
        {_bar_html(row.get('score_cash_quality'))}
      </div>
      <div class="kpi">
        <div class="kpi-lbl">4. Bất thường Ngành (25%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_isoforest'), 1)} đ</div>
        <div class="kpi-sub">Đánh giá dị biệt so với cùng ngành</div>
        {_bar_html(row.get('score_isoforest'))}
      </div>
    </div>

    <table style="margin-top:12px;">
      <thead>
        <tr><th>Tổng Tài sản (270)</th><th>Vốn CSH (400)</th><th>Doanh thu thuần (10)</th><th>LN Sau thuế (60)</th><th>Dòng tiền CFO (20)</th><th>Phải thu KH (131)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>{_fmt_bn(row.get('total_assets'))}</strong></td>
          <td>{_fmt_bn(row.get('total_equity'))}</td>
          <td>{_fmt_bn(row.get('net_revenue'))}</td>
          <td>{_fmt_bn(row.get('net_income'))}</td>
          <td><strong>{_fmt_bn(row.get('cfo'))}</strong></td>
          <td>{_fmt_bn(row.get('accounts_receivable'))}</td>
        </tr>
      </tbody>
    </table>

    <h2>2. Phân rã Giải thích AI <span>(SHAP Waterfall — Base = {_fmt_num(row.get('shap_base_value', 29.22), 2)} đ)</span></h2>
    <table>
      <thead>
        <tr><th>Chỉ số tài chính pháp chứng</th><th style="text-align:right;">Đóng góp SHAP</th><th>Chiều tác động</th></tr>
      </thead>
      <tbody>{shap_rows_html}</tbody>
    </table>

    <h2>3. Đối chiếu <span>Pháp lý VAS / VSA 240 / TT 99/2025</span> &amp; Thuyết minh BCTC</h2>
    {rag_html}

    <div class="disclaimer">
      <strong>Khuyến cáo Pháp lý &amp; Chuẩn mực Kiểm toán (VSA 240 — TT 214/2012/TT-BTC):</strong>
      Báo cáo này được tạo tự động bởi hệ thống <em>FinAudit AI — FinForensics</em> nhằm cung cấp các
      <strong>Chỉ báo rủi ro chất lượng lợi nhuận (Forensic Risk Red Flags)</strong> hỗ trợ khoanh vùng trọng tâm kiểm toán
      và thẩm định tín dụng theo thái độ hoài nghi nghề nghiệp. Kết quả không phải là kết luận pháp lý về hành vi gian lận
      và không thay thế ý kiến kiểm toán độc lập hay quyết định đầu tư. Chuẩn mực kế toán áp dụng liên thông
      <strong>Thông tư 200/2014/TT-BTC</strong> (niên độ đến hết 31/12/2025) và <strong>Thông tư 99/2025/TT-BTC</strong> (từ 01/01/2026).
    </div>
  </div>
</body>
</html>
"""
