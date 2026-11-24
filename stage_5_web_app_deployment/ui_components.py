"""
HỆ THỐNG THIẾT KẾ GIAO DIỆN FINTECH SAAS & THƯ VIỆN BIỂU ĐỒ PLOTLY
===================================================================
Bảng màu hài hòa Enterprise FinTech Light:
  - Background: #F8FAFC (Alabaster Slate)
  - Card Surface: #FFFFFF (Border #E2E8F0)
  - Brand Gradient: #0F172A -> #1E3A8A -> #1D4ED8
  - Semantic: Emerald #059669 (An toàn) | Amber #D97706 (Theo dõi) | Crimson #DC2626 (Cảnh báo Đỏ)
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
# 1. BẢNG MÀU CHUẨN & CSS FINTECH SAAS
# ---------------------------------------------------------------------------
PALETTE = {
    "navy": "#0F172A",
    "royal": "#1E3A8A",
    "blue": "#2563EB",
    "bg": "#F8FAFC",
    "card": "#FFFFFF",
    "border": "#E2E8F0",
    "muted": "#64748B",
    "green": "#059669",
    "green_bg": "#ECFDF5",
    "green_bd": "#A7F3D0",
    "amber": "#D97706",
    "amber_bg": "#FFFBEB",
    "amber_bd": "#FDE68A",
    "red": "#DC2626",
    "red_bg": "#FEF2F2",
    "red_bd": "#FECACA",
}

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
        /* Tổng thể nền sạch, dịu mắt */
        .stApp {
            background-color: #F8FAFC;
            color: #0F172A;
        }
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
        }
        .main .block-container {
            padding-top: 1.3rem;
            padding-bottom: 2.5rem;
            max-width: 1380px;
        }
        /* Banner Thương hiệu Gradient Slate Navy -> Royal Blue */
        .fa-hero {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 62%, #1D4ED8 100%);
            color: #FFFFFF;
            padding: 20px 26px;
            border-radius: 14px;
            margin-bottom: 18px;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.12);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
        }
        .fa-hero-kicker {
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #93C5FD;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .fa-hero h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.25;
        }
        .fa-hero p {
            margin: 6px 0 0 0;
            font-size: 13.5px;
            color: #E2E8F0;
            line-height: 1.45;
        }
        .fa-hero-pill {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.22);
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 12px;
            color: #F8FAFC;
            text-align: right;
            line-height: 1.45;
        }
        /* Thẻ KPI chuẩn FinTech */
        .fa-kpi {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 15px 18px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
            height: 100%;
            transition: border-color 0.2s ease;
        }
        .fa-kpi:hover {
            border-color: #94A3B8;
        }
        .fa-kpi-label {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        .fa-kpi-value {
            font-size: 26px;
            font-weight: 800;
            color: #0F172A;
            margin: 5px 0 3px;
            font-variant-numeric: tabular-nums;
            line-height: 1.15;
        }
        .fa-kpi-sub {
            font-size: 12px;
            color: #475569;
        }
        /* Card chứa nội dung */
        .fa-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            margin-bottom: 14px;
        }
        .fa-section-title {
            font-size: 15px;
            font-weight: 800;
            color: #0F172A;
            margin: 6px 0 10px;
            padding-bottom: 6px;
            border-bottom: 2px solid #E2E8F0;
        }
        /* Nhãn màu ngữ nghĩa */
        .fa-badge {
            display: inline-block;
            padding: 4px 11px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            line-height: 1.2;
        }
        .fa-badge-green { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
        .fa-badge-amber { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }
        .fa-badge-red   { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
        .fa-badge-blue  { background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
        /* Thẻ Trích dẫn RAG */
        .fa-rag-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 4px solid #1E3A8A;
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 10px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.03);
        }
        .fa-rag-cite {
            font-size: 12.5px;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 5px;
        }
        .fa-rag-body {
            font-size: 13px;
            color: #334155;
            line-height: 1.55;
        }
        .fa-rag-meta {
            margin-top: 7px;
            font-size: 11.5px;
            color: #64748B;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        }
        /* Tuyên bố VSA 240 */
        .fa-disclaimer {
            background: #F1F5F9;
            border: 1px solid #CBD5E1;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 12px;
            color: #475569;
            line-height: 1.5;
            margin-top: 16px;
        }
        /* Tinh chỉnh Tabs cho sắc nét */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            color: #475569;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E3A8A !important;
            color: #FFFFFF !important;
            border-color: #1E3A8A !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(kicker: str, title: str, subtitle: str, right_badge: str = "") -> None:
    right_html = f'<div class="fa-hero-pill">{right_badge}</div>' if right_badge else ""
    st.markdown(
        f"""
        <div class="fa-hero">
          <div style="flex:1;min-width:260px;">
            <div class="fa-hero-kicker">{escape(kicker)}</div>
            <h1>{escape(title)}</h1>
            <p>{subtitle}</p>
          </div>
          {right_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, sub: str, accent_color: str = "#0F172A") -> None:
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
        return f'<span class="fa-badge fa-badge-blue">{escape(tier)}</span>'
    if score >= 65.0:
        return f'<span class="fa-badge fa-badge-red">🔴 {escape(tier)}</span>'
    if score >= 40.0:
        return f'<span class="fa-badge fa-badge-amber">🟡 {escape(tier)}</span>'
    return f'<span class="fa-badge fa-badge-green">🟢 {escape(tier)}</span>'


def render_vsa240_disclaimer() -> None:
    st.markdown(
        """
        <div class="fa-disclaimer">
          <strong>⚖️ Khuyến cáo Pháp lý & Chuẩn mực Kiểm toán (VSA 240 — TT 214/2012/TT-BTC):</strong>
          Hệ thống <strong>FinAudit AI — FinForensics</strong> xuất các <em>Chỉ báo rủi ro chất lượng lợi nhuận (Forensic Risk Red Flags)</em>
          phục vụ sàng lọc và khoanh vùng trọng tâm kiểm toán theo thái độ hoài nghi nghề nghiệp, <strong>tuyệt đối không kết luận pháp lý về hành vi gian lận</strong>.
          Hệ thống kế toán liên thông <strong>Thông tư 200/2014/TT-BTC</strong> (BCTC lịch sử đến hết 31/12/2025) và
          <strong>Thông tư 99/2025/TT-BTC</strong> (hiệu lực từ 01/01/2026); phân định rõ dự phòng BCTC với dự phòng tính thuế TNDN theo <strong>Thông tư 48/2019/TT-BTC</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 2. THƯ VIỆN BIỂU ĐỒ TƯƠNG TÁC PLOTLY
# ---------------------------------------------------------------------------
def plot_forensic_matrix_2d(df_filtered: pd.DataFrame) -> go.Figure:
    """Ma trận Pháp chứng 2D: Beneish M-Score vs Altman Z''-Score."""
    df = df_filtered.dropna(subset=["beneish_m_score", "altman_z_double_prime", "composite_risk_score"]).copy()
    # Cắt biên hiển thị nhẹ để nhìn rõ đám đông chính (vẫn giữ con số thật trong hover)
    df["x_plot"] = df["altman_z_double_prime"].clip(-2.0, 14.0)
    df["y_plot"] = df["beneish_m_score"].clip(-6.0, 4.0)
    df["size_plot"] = np.clip(np.log1p(df["total_assets"].fillna(10.0).clip(lower=1.0)) * 2.8, 7.0, 24.0)

    tier_colors = {
        "Thấp (An toàn)": PALETTE["green"],
        "Trung bình (Cần theo dõi)": PALETTE["amber"],
        "Cao (Cảnh báo Đỏ)": PALETTE["red"],
    }

    fig = go.Figure()
    # Tô nền vùng nguy hiểm kép (Altman < 4.35 & Beneish > -1.78)
    fig.add_shape(
        type="rect",
        x0=-2.2,
        x1=4.35,
        y0=-1.78,
        y1=4.2,
        fillcolor="rgba(220, 38, 38, 0.07)",
        line_width=0,
        layer="below",
    )
    # Tô nền vùng an toàn kép (Altman > 5.85 & Beneish <= -1.78)
    fig.add_shape(
        type="rect",
        x0=5.85,
        x1=14.3,
        y0=-6.2,
        y1=-1.78,
        fillcolor="rgba(5, 150, 105, 0.06)",
        line_width=0,
        layer="below",
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
                marker=dict(
                    size=sub["size_plot"],
                    color=color,
                    opacity=0.82,
                    line=dict(width=1, color="#FFFFFF"),
                ),
                text=hover_txt,
                hovertemplate="%{text}<extra></extra>",
            )
        )

    # Các đường ngưỡng chuẩn học thuật
    fig.add_hline(
        y=-1.78,
        line_dash="dash",
        line_color=PALETTE["red"],
        line_width=1.4,
        annotation_text="Ngưỡng Beneish M = -1.78",
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color=PALETTE["red"],
    )
    fig.add_vline(
        x=4.35,
        line_dash="dash",
        line_color=PALETTE["red"],
        line_width=1.3,
        annotation_text="Altman Nguy hiểm (4.35)",
        annotation_position="top left",
        annotation_font_size=11,
        annotation_font_color=PALETTE["red"],
    )
    fig.add_vline(
        x=5.85,
        line_dash="dot",
        line_color=PALETTE["green"],
        line_width=1.3,
        annotation_text="Altman An toàn (5.85)",
        annotation_position="bottom right",
        annotation_font_size=11,
        annotation_font_color=PALETTE["green"],
    )

    fig.update_layout(
        title=dict(text="Ma trận Pháp chứng 2D: Beneish M-Score vs. Altman Z''-Score (EMS 2005)", font=dict(size=14, color=PALETTE["navy"])),
        xaxis_title="Altman Z''-Score (Càng sang phải càng vững tài chính →)",
        yaxis_title="Beneish M-Score (Càng lên trên rủi ro thổi số càng cao ↑)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=440,
        margin=dict(l=55, r=25, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1.0, font=dict(size=11.5)),
        xaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#CBD5E1", range=[-2.2, 14.3]),
        yaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#CBD5E1", range=[-6.2, 4.2]),
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
            div_pct=("cash_flow_divergence_flag", lambda s: float(s.fillna(False).mean() * 100.0)),
        )
        .sort_values("median_score", ascending=True)
    )
    colors = [
        PALETTE["red"] if v >= 45 else (PALETTE["amber"] if v >= 32 else PALETTE["royal"])
        for v in agg["median_score"]
    ]
    fig = go.Figure(
        go.Bar(
            y=agg["icb_sector_vi"],
            x=agg["median_score"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{r['median_score']:.1f}đ (Cờ đỏ: {r['red_pct']:.1f}% • n={r['n_firms']})" for _, r in agg.iterrows()],
            textposition="outside",
            textfont=dict(size=11, color=PALETTE["navy"]),
            hovertemplate=(
                "<b>%{y}</b><br>Điểm rủi ro trung vị: <b>%{x:.1f}đ</b><br>"
                "%{text}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=dict(text="Xếp hạng Mức độ Rủi ro Trung vị theo 15 Ngành ICB", font=dict(size=14, color=PALETTE["navy"])),
        xaxis_title="Điểm Rủi ro Pháp chứng Trung vị (0–100)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=440,
        margin=dict(l=15, r=155, t=50, b=45),
        xaxis=dict(gridcolor="#F1F5F9", range=[0, max(float(agg["median_score"].max()) * 1.45, 55.0)] if len(agg) else [0, 60]),
        yaxis=dict(tickfont=dict(size=11.5)),
    )
    return fig


def plot_risk_gauge(score: float, tier: str) -> go.Figure:
    """Đồng hồ Gauge 0–100 hiển thị Composite Risk Score."""
    val = float(score) if pd.notna(score) else 0.0
    bar_color = PALETTE["red"] if val >= 65 else (PALETTE["amber"] if val >= 40 else PALETTE["green"])
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": " đ", "font": {"size": 34, "color": bar_color, "family": "monospace"}},
            title={"text": f"<b>Composite Risk Score</b><br><span style='font-size:12px;color:#64748B'>{tier}</span>", "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94A3B8"},
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "#FFFFFF",
                "borderwidth": 1,
                "bordercolor": "#E2E8F0",
                "steps": [
                    {"range": [0, 40], "color": "#ECFDF5"},
                    {"range": [40, 65], "color": "#FFFBEB"},
                    {"range": [65, 100], "color": "#FEF2F2"},
                ],
                "threshold": {"line": {"color": PALETTE["navy"], "width": 3}, "thickness": 0.78, "value": val},
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        height=245,
        margin=dict(l=22, r=22, t=52, b=10),
    )
    return fig


def plot_shap_waterfall(row: pd.Series) -> go.Figure:
    """Biểu đồ Thác nước SHAP (Top 8 nhân tố ảnh hưởng lớn nhất quanh Base Value)."""
    base_val = float(row.get("shap_base_value", 29.224))
    items = []
    for shap_col, label_vi, raw_col, fmt in SHAP_DISPLAY_META:
        v = row.get(shap_col, np.nan)
        if pd.notna(v):
            raw_v = row.get(raw_col, np.nan)
            if pd.notna(raw_v):
                raw_txt = f"{float(raw_v)*100:.1f}%" if fmt == "pct" else f"{float(raw_v):.2f}"
            else:
                raw_txt = "N/A"
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
            connector={"line": {"color": "#CBD5E1", "width": 1.2}},
            increasing={"marker": {"color": PALETTE["red"]}},
            decreasing={"marker": {"color": PALETTE["green"]}},
            totals={"marker": {"color": PALETTE["royal"]}},
        )
    )
    fig.update_layout(
        title=dict(text="Biểu đồ Thác nước SHAP: Chỉ số nào đẩy rủi ro lên (+) hay kéo xuống (-)?", font=dict(size=14, color=PALETTE["navy"])),
        yaxis_title="Điểm Rủi ro Pháp chứng (0–100)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=400,
        margin=dict(l=45, r=20, t=55, b=95),
        xaxis=dict(tickangle=-25, tickfont=dict(size=10.5)),
        yaxis=dict(gridcolor="#F1F5F9", range=[0, max(105.0, float(row.get("composite_risk_score", 50.0)) + 18.0)]),
    )
    return fig


def plot_sector_radar(row: pd.Series) -> go.Figure:
    """Biểu đồ Radar đối sánh 6 trục rủi ro chuẩn hóa của doanh nghiệp với Trung vị ngành ICB."""
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
    # Đóng vòng radar
    cats_closed = cats + [cats[0]]
    vals_closed = vals + [vals[0]]
    peer_closed = [0.5] * len(cats_closed)  # Ngưỡng sát trung vị ngành (0 = trung vị ngành)

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
            fillcolor="rgba(220, 38, 38, 0.18)" if float(row.get("composite_risk_score", 0)) >= 65 else "rgba(30, 58, 138, 0.18)",
            line=dict(color=PALETTE["red"] if float(row.get("composite_risk_score", 0)) >= 65 else PALETTE["royal"], width=2.4),
        )
    )
    fig.update_layout(
        title=dict(text="Radar Lệch chuẩn Ngành ICB (Càng vươn xa tâm = Càng xấu hơn ngành)", font=dict(size=13.5, color=PALETTE["navy"])),
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, range=[0, 5.2], gridcolor="#E2E8F0", tickfont=dict(size=10)),
            angularaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=11)),
        ),
        paper_bgcolor="#FFFFFF",
        height=370,
        margin=dict(l=45, r=45, t=55, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=-0.16, xanchor="center", x=0.5, font=dict(size=11)),
    )
    return fig


def plot_multiyear_trend(df_comp: pd.DataFrame) -> go.Figure:
    """Biểu đồ 2 tầng đa năm (2018–2025): Doanh thu/LNST/CFO và Quỹ đạo Điểm rủi ro."""
    df = df_comp.sort_values("year").copy()
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.11,
        row_heights=[0.56, 0.44],
        subplot_titles=(
            "Doanh thu thuần vs. Lợi nhuận sau thuế vs. Dòng tiền kinh doanh CFO (Tỷ VND)",
            "Quỹ đạo Điểm Rủi ro Pháp chứng Tổng hợp (Composite Score 0–100)",
        ),
    )

    fig.add_trace(
        go.Bar(x=df["year"], y=df["net_revenue"], name="Doanh thu thuần", marker_color="#CBD5E1", opacity=0.75),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["year"], y=df["net_income"], name="LN Sau thuế (LNST)", mode="lines+markers", line=dict(color=PALETTE["royal"], width=2.5), marker=dict(size=7)),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["year"], y=df["cfo"], name="Dòng tiền HĐKD (CFO)", mode="lines+markers", line=dict(color=PALETTE["green"], width=2.5, dash="dot"), marker=dict(size=7, symbol="diamond")),
        row=1,
        col=1,
    )

    df_sc = df.dropna(subset=["composite_risk_score"])
    pt_colors = [
        PALETTE["red"] if v >= 65 else (PALETTE["amber"] if v >= 40 else PALETTE["green"])
        for v in df_sc["composite_risk_score"]
    ]
    fig.add_trace(
        go.Scatter(
            x=df_sc["year"],
            y=df_sc["composite_risk_score"],
            name="Composite Risk Score",
            mode="lines+markers+text",
            text=[f"{v:.1f}" for v in df_sc["composite_risk_score"]],
            textposition="top center",
            line=dict(color=PALETTE["navy"], width=2.5),
            marker=dict(size=9, color=pt_colors, line=dict(width=1.5, color="#FFFFFF")),
        ),
        row=2,
        col=1,
    )
    fig.add_hline(y=65, line_dash="dash", line_color=PALETTE["red"], line_width=1.2, row=2, col=1)
    fig.add_hline(y=40, line_dash="dot", line_color=PALETTE["amber"], line_width=1.2, row=2, col=1)

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=490,
        margin=dict(l=55, r=25, t=42, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1.0, font=dict(size=11)),
    )
    fig.update_yaxes(gridcolor="#F1F5F9", row=1, col=1)
    fig.update_yaxes(gridcolor="#F1F5F9", range=[0, 105], title_text="Điểm (0–100)", row=2, col=1)
    fig.update_xaxes(dtick=1, row=2, col=1)
    return fig


def plot_validation_benchmarks(stage3_sum: dict[str, Any], stage4_sum: dict[str, Any]) -> tuple[go.Figure, go.Figure]:
    """2 biểu đồ kiểm chứng trung tâm: (1) Backtest AUC GĐ3 & (2) Benchmark RAG GĐ4."""
    bt = stage3_sum["layer4_empirical_backtest"]
    fig_auc = go.Figure(
        go.Bar(
            x=["Beneish đơn lẻ", "AI IsoForest đơn lẻ", "Altman Z'' đơn lẻ", "FinAudit Composite (4 Trụ cột)"],
            y=[bt["auc_beneish_only"], bt["auc_isoforest_only"], bt["auc_altman_only"], bt["auc_composite"]],
            marker_color=["#94A3B8", "#3B82F6", "#059669", "#1E3A8A"],
            text=[f"{v:.4f}" for v in [bt["auc_beneish_only"], bt["auc_isoforest_only"], bt["auc_altman_only"], bt["auc_composite"]]],
            textposition="outside",
            textfont=dict(size=12, color=PALETTE["navy"]),
        )
    )
    fig_auc.update_layout(
        title=dict(text="Backtest Thực chứng (12 Bluechip vs 12 DN Biến cố): So sánh AUC-ROC", font=dict(size=13.5, color=PALETTE["navy"])),
        yaxis=dict(range=[0, 1.12], title="AUC-ROC (1.00 = Tối đa)", gridcolor="#F1F5F9"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=340,
        margin=dict(l=45, r=20, t=48, b=40),
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
            marker_color=PALETTE["royal"],
            text=[f"{leg[m]['hit_at_1_pct']:.0f}%" for m in m_order],
            textposition="outside",
        )
    )
    fig_rag.add_trace(
        go.Bar(
            name="PDF Nhiễu OCR NVL 2025 — Hit@1 (%)",
            x=m_names,
            y=[pdf_b[m]["hit_at_1_pct"] for m in m_order],
            marker_color=PALETTE["green"],
            text=[f"{pdf_b[m]['hit_at_1_pct']:.1f}%" for m in m_order],
            textposition="outside",
        )
    )
    fig_rag.update_layout(
        barmode="group",
        title=dict(text="Đối chứng Động cơ RAG: Pháp lý VAS (20Q) & PDF Nhiễu OCR NVL 2025 (6Q)", font=dict(size=13.5, color=PALETTE["navy"])),
        yaxis=dict(range=[0, 118], title="Hit Rate@1 (%)", gridcolor="#F1F5F9"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=340,
        margin=dict(l=45, r=20, t=48, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1.0, font=dict(size=11)),
    )
    return fig_auc, fig_rag
