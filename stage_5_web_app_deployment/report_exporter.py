"""
BỘ XUẤT HỒ SƠ KIỂM TOÁN PHÁP CHỨNG (HTML CHUẨN A4 IN RA PDF)
=============================================================
Tạo báo cáo hoàn chỉnh 1 trang A4 sắc nét cho từng doanh nghiệp, sẵn sàng in PDF
hoặc đính kèm Hồ sơ Kiểm toán / Hồ sơ Thẩm định Tín dụng.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import pandas as pd


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
        tier_bg, tier_fg, tier_bd = "#FEF2F2", "#DC2626", "#FECACA"
    elif score >= 40.0:
        tier_bg, tier_fg, tier_bd = "#FFFBEB", "#D97706", "#FDE68A"
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
        color = "#DC2626" if val >= 0.5 else ("#059669" if val <= -0.5 else "#475569")
        direction = "Đẩy rủi ro tăng" if val > 0.2 else ("Kéo rủi ro giảm" if val < -0.2 else "Trung tính")
        shap_rows_html += (
            f"<tr><td>{escape(lbl)}</td>"
            f"<td style='text-align:right;font-weight:700;color:{color};font-family:monospace;'>{sign}{val:.2f} đ</td>"
            f"<td style='color:{color};'>{direction}</td></tr>"
        )

    rag_html = ""
    if rag_brief and rag_brief.get("top_driver_briefs"):
        for drv in rag_brief["top_driver_briefs"]:
            cites = "".join(
                f"<li><strong>{escape(c['citation'])}</strong>: {escape(c['excerpt'][:220])}...</li>"
                for c in drv.get("legal_citations", [])
            )
            b09_items = ", ".join(
                f"{escape(b['label_vi'])}: <strong>{b['value_bn_vnd']:,.2f} tỷ</strong>"
                for b in drv.get("b09_note_evidence", [])[:5]
            )
            pdf_items = "".join(
                f"<div class='pdf-quote'><strong>{escape(p['citation'])}</strong>: {escape(p['excerpt'][:220])}...</div>"
                for p in drv.get("pdf_evidence", [])
            )
            rag_html += f"""
            <div class="rag-box">
              <div class="rag-title">🚩 {escape(drv['driver_label_vi'])} <span class="rag-pts">(+{drv['shap_points']:.2f}đ SHAP)</span></div>
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

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Hồ sơ Pháp chứng BCTC — {ticker} ({year}) | FinAudit AI</title>
<style>
  @page {{ size: A4; margin: 14mm; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #0F172A; background: #F8FAFC; margin: 0; padding: 20px; }}
  .sheet {{ max-width: 900px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 28px 32px; box-shadow: 0 4px 16px rgba(15,23,42,0.06); }}
  .banner {{ background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); color: #FFFFFF; padding: 20px 24px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; }}
  .banner h1 {{ margin: 4px 0 2px; font-size: 20px; }}
  .banner .sub {{ font-size: 12px; opacity: 0.85; }}
  .score-box {{ background: {tier_bg}; color: {tier_fg}; border: 1.5px solid {tier_bd}; border-radius: 10px; padding: 10px 18px; text-align: center; min-width: 145px; }}
  .score-num {{ font-size: 28px; font-weight: 800; line-height: 1.1; font-family: monospace; }}
  .score-tier {{ font-size: 11px; font-weight: 700; margin-top: 3px; }}
  h2 {{ font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; color: #1E3A8A; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; margin: 22px 0 12px; }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .kpi {{ background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 12px; }}
  .kpi-lbl {{ font-size: 11px; color: #64748B; }}
  .kpi-val {{ font-size: 16px; font-weight: 800; color: #0F172A; margin-top: 3px; font-family: monospace; }}
  .kpi-sub {{ font-size: 11px; color: #475569; margin-top: 2px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  th, td {{ padding: 7px 10px; border-bottom: 1px solid #E2E8F0; text-align: left; }}
  th {{ background: #F1F5F9; color: #334155; font-weight: 700; }}
  .rag-box {{ background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #1E3A8A; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; font-size: 12.5px; }}
  .rag-title {{ font-weight: 700; color: #0F172A; margin-bottom: 6px; }}
  .rag-pts {{ color: #DC2626; font-family: monospace; }}
  .cite-list {{ margin: 4px 0 6px 18px; padding: 0; color: #334155; }}
  .cite-list li {{ margin-bottom: 4px; }}
  .b09-line {{ background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 12px; color: #1E3A8A; }}
  .pdf-quote {{ background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 11.5px; color: #92400E; }}
  .disclaimer {{ margin-top: 20px; padding: 12px 14px; background: #F1F5F9; border-radius: 8px; font-size: 11.5px; color: #475569; line-height: 1.5; }}
  .print-btn {{ margin-bottom: 12px; padding: 8px 16px; background: #1E3A8A; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }}
  @media print {{ .print-btn {{ display: none; }} body {{ background: #fff; padding: 0; }} .sheet {{ box-shadow: none; border: none; padding: 0; }} }}
</style>
</head>
<body>
  <div style="max-width:900px;margin:0 auto;text-align:right;">
    <button class="print-btn" onclick="window.print()">🖨️ In / Lưu thành PDF chuẩn A4</button>
  </div>
  <div class="sheet">
    <div class="banner">
      <div>
        <div class="sub">FINAUDIT AI — FINFORENSICS • HỒ SƠ SÀNG LỌC RỦI RO PHÁP CHỨNG BCTC</div>
        <h1>{ticker} — {comp_name}</h1>
        <div class="sub">Năm tài chính: <strong>{year}</strong> • Sàn: <strong>{exchange}</strong> • Ngành ICB: <strong>{sector}</strong> • Xuất lúc: {now_str}</div>
      </div>
      <div class="score-box">
        <div class="score-num">{score:.1f} / 100</div>
        <div class="score-tier">{tier}</div>
      </div>
    </div>

    <h2>1. Tóm tắt 4 Trụ cột Pháp chứng & Số liệu BCTC Cốt lõi</h2>
    <div class="grid-4">
      <div class="kpi">
        <div class="kpi-lbl">Beneish M-Score (30%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_beneish'), 1)} đ</div>
        <div class="kpi-sub">M = {_fmt_num(row.get('beneish_m_score'), 3)} (Ngưỡng -1.78)</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">Altman Z'' EMS (25%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_altman'), 1)} đ</div>
        <div class="kpi-sub">Z'' = {_fmt_num(row.get('altman_z_double_prime'), 3)} ({escape(str(row.get('altman_zone', '')))})</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">Dòng tiền & Tài sản mềm (20%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_cash_quality'), 1)} đ</div>
        <div class="kpi-sub">CFO/TS: {_fmt_num(float(row.get('cfo_to_assets', 0))*100, 1)}% | SRR: {_fmt_num(float(row.get('sensitive_receivables_ratio', 0))*100, 1)}%</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">AI Isolation Forest (25%)</div>
        <div class="kpi-val">{_fmt_num(row.get('score_isoforest'), 1)} đ</div>
        <div class="kpi-sub">Dị biệt đa chiều theo ngành ICB</div>
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

    <h2>2. Phân rã Giải thích AI (SHAP Waterfall — Nền thị trường Base = {_fmt_num(row.get('shap_base_value', 29.22), 2)} đ)</h2>
    <table>
      <thead>
        <tr><th>Chỉ số tài chính pháp chứng</th><th style="text-align:right;">Đóng góp SHAP</th><th>Chiều tác động</th></tr>
      </thead>
      <tbody>{shap_rows_html}</tbody>
    </table>

    <h2>3. Đối chiếu Pháp lý VAS / VSA 240 / TT 99/2025 & Thuyết minh BCTC (Hybrid RAG)</h2>
    {rag_html}

    <div class="disclaimer">
      <strong>Khuyến cáo Pháp lý & Chuẩn mực Kiểm toán (VSA 240 — TT 214/2012/TT-BTC):</strong>
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
