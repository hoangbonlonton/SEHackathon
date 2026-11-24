"""
FINAUDIT AI — FINFORENSICS | ỨNG DỤNG WEB FINTECH SAAS (STREAMLIT)
==================================================================
Dự án: SE-Hackathon Challenge 2026 (Trường Kinh tế — ĐH Công nghiệp Hà Nội)
Giai đoạn 5: Triển khai hệ thống Web App tích hợp đầy đủ 5 Phân hệ Chức năng:
  1. Tổng quan Thị trường & Quét Rủi ro Ngành ICB (Market & Sector Radar)
  2. Hồ sơ Pháp chứng Doanh nghiệp 360° & Giải thích AI (SHAP Waterfall)
  3. Phòng Thẩm định BCTC Mới (Upload CSV/Excel & What-If Live Scoring Lab)
  4. Trợ lý AI Soi Thuyết minh PDF & Tra cứu Pháp lý VAS/TT 99/2025/VSA 240 (Grounded Hybrid RAG)
  5. Trung tâm Kiểm chứng Khoa học & Quản trị Minh bạch (Validation & Governance Center)

Khởi chạy:
  streamlit run stage_5_web_app_deployment/app.py
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Cấu hình đường dẫn chuẩn (hoạt động dù chạy từ gốc d:\SEHackathon hay từ stage_5_web_app_deployment)
STAGE5_DIR = Path(__file__).resolve().parent
ROOT_DIR = STAGE5_DIR.parent
DATA_PROCESSED_DIR = ROOT_DIR / "data_store" / "processed"
MODELS_DIR = ROOT_DIR / "data_store" / "models"
SAMPLE_UPLOADS_DIR = ROOT_DIR / "data_store" / "sample_uploads"
STAGE4_PATH = ROOT_DIR / "stage_4_rag_legal_notes" / "04_hybrid_rag_engine.py"
LEGAL_CORPUS_DIR = ROOT_DIR / "stage_4_rag_legal_notes" / "legal_corpus"

if str(STAGE5_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE5_DIR))

from live_scoring_service import (
    SAMPLE_WORKED_EXAMPLES,
    ensure_sample_upload_files,
    run_live_scoring_pipeline,
)
from report_exporter import generate_html_audit_report
from ui_components import (
    BRAND_EMBLEM_SVG,
    PALETTE,
    ROLE_PROFILES,
    SHAP_DISPLAY_META,
    inject_fintech_css,
    plot_company_trajectory_3d_animated,
    plot_forensic_matrix_2d,
    plot_forensic_space_3d_animated,
    plot_multiyear_trend,
    plot_risk_gauge,
    plot_sector_radar,
    plot_sector_risk_ranking,
    plot_sector_terrain_3d,
    plot_shap_waterfall,
    plot_validation_benchmarks,
    render_hero,
    render_kpi_card,
    render_legal_registry_table,
    render_role_guidance_strip,
    render_sticky_top_banner,
    render_vsa240_disclaimer,
    risk_badge_html,
)

# ---------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG & NẠP DỮ LIỆU / MÔ HÌNH CÓ BỘ NHỚ ĐỆM (CACHE)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FinAudit AI — FinForensics | Sàng lọc Rủi ro BCTC Chuẩn VAS",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def load_stage4_module():
    spec = importlib.util.spec_from_file_location("finaudit_stage4_mod", str(STAGE4_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Không tìm thấy module Giai đoạn 4 tại {STAGE4_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["finaudit_stage4_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


@st.cache_data(show_spinner=False)
def load_core_datasets() -> dict[str, Any]:
    df_scored = pd.read_parquet(DATA_PROCESSED_DIR / "forensic_scored_full.parquet")
    df_bench = pd.read_parquet(DATA_PROCESSED_DIR / "sector_benchmarks_by_year.parquet")
    df_b09 = pd.read_parquet(DATA_PROCESSED_DIR / "real_b09_notes_structured.parquet")
    schema_b09 = json.loads((DATA_PROCESSED_DIR / "b09_note_schema_catalog.json").read_text(encoding="utf-8"))
    s3_sum = json.loads((DATA_PROCESSED_DIR / "stage3_validation_summary.json").read_text(encoding="utf-8"))
    s4_sum = json.loads((DATA_PROCESSED_DIR / "stage4_rag_benchmark_summary.json").read_text(encoding="utf-8"))
    s2_sum = json.loads((DATA_PROCESSED_DIR / "stage2_metrics_summary.json").read_text(encoding="utf-8"))
    csv_tpl, xlsx_tpl = ensure_sample_upload_files()
    return {
        "df_scored": df_scored,
        "df_bench": df_bench,
        "df_b09": df_b09,
        "schema_b09": schema_b09,
        "s2_sum": s2_sum,
        "s3_sum": s3_sum,
        "s4_sum": s4_sum,
        "csv_tpl": csv_tpl,
        "xlsx_tpl": xlsx_tpl,
    }


@st.cache_resource(show_spinner=False)
def load_ai_and_rag_engines() -> dict[str, Any]:
    artifacts = joblib.load(MODELS_DIR / "finaudit_stage3_artifacts.joblib")
    s4 = load_stage4_module()
    legal_chunks = s4.load_legal_corpus_chunks(LEGAL_CORPUS_DIR)
    legal_retriever = s4.HybridRAGRetriever(legal_chunks, rrf_k=30)
    return {
        "artifacts": artifacts,
        "s4": s4,
        "legal_chunks": legal_chunks,
        "legal_retriever": legal_retriever,
    }


@st.cache_resource(show_spinner=False)
def load_bundled_pdf_index(pdf_filename: str) -> tuple[dict[str, Any], Any]:
    s4 = load_stage4_module()
    pdf_path = SAMPLE_UPLOADS_DIR / pdf_filename
    diag, chunks = s4.extract_and_diagnose_pdf(pdf_path)
    retriever = s4.HybridRAGRetriever(chunks, rrf_k=30) if chunks else None
    return diag, retriever


def call_optional_gemini_synthesis(api_key: str, question: str, retrieved_hits: list[dict[str, Any]]) -> str:
    """Hook tùy chọn Gemini API (chỉ chạy khi người dùng tự nhập API key và bấm nút tổng hợp)."""
    context_txt = "\n\n".join(
        f"NGUỒN {h['citation']}:\n{h['full_text'][:1200]}" for h in retrieved_hits[:3]
    )
    prompt = (
        "Bạn là chuyên gia kiểm toán pháp chứng Việt Nam tuân thủ VSA 240 và Thông tư 99/2025/TT-BTC.\n"
        "Chỉ trả lời dựa trên NGUỒN tài liệu cung cấp dưới đây, bắt buộc trích dẫn đúng [Nguồn] trong ngoặc vuông, "
        "không bịa thêm điều khoản ngoài nguồn.\n\n"
        f"CÂU HỎI: {question}\n\n{context_txt}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key.strip()}"
    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if resp.status_code == 200:
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"Không gọi được Gemini API (HTTP {resp.status_code}). Hệ thống tiếp tục hiển thị kết quả Zero-API Grounded RAG."
    except Exception as exc:
        return f"Lỗi kết nối Gemini API ({type(exc).__name__}). Hệ thống tiếp tục hiển thị kết quả Zero-API Grounded RAG."


# ---------------------------------------------------------------------------
# 2. KHỞI TẠO CSS & TRẠNG THÁI ĐIỀU HƯỚNG SIDEBAR
# ---------------------------------------------------------------------------
inject_fintech_css()
datasets = load_core_datasets()
engines = load_ai_and_rag_engines()

df_all: pd.DataFrame = datasets["df_scored"]
df_bench: pd.DataFrame = datasets["df_bench"]
df_b09: pd.DataFrame = datasets["df_b09"]
schema_b09: dict[str, Any] = datasets["schema_b09"]
s2_sum: dict[str, Any] = datasets["s2_sum"]
s3_sum: dict[str, Any] = datasets["s3_sum"]
s4_sum: dict[str, Any] = datasets["s4_sum"]
artifacts = engines["artifacts"]
s4_mod = engines["s4"]
legal_retriever = engines["legal_retriever"]

MODULES = [
    "1. Tổng quan Thị trường & Radar Ngành",
    "2. Hồ sơ Pháp chứng 360° & SHAP",
    "3. Phòng Thẩm định BCTC Mới (Live)",
    "4. Trợ lý AI Soi PDF & Luật VAS",
    "5. Trung tâm Kiểm chứng & ESG-G",
]

if "active_module" not in st.session_state:
    st.session_state["active_module"] = MODULES[0]
if "nav_radio" not in st.session_state:
    st.session_state["nav_radio"] = st.session_state["active_module"]
if "active_role" not in st.session_state:
    st.session_state["active_role"] = "Kiểm toán viên"
if "role_selector" not in st.session_state:
    st.session_state["role_selector"] = st.session_state["active_role"]
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TDH"
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = 2025

# Đồng bộ an toàn khi bấm nút điều hướng nhanh trước khi khởi tạo widget st.radio
if "pending_module" in st.session_state and st.session_state["pending_module"] in MODULES:
    _target_mod = st.session_state.pop("pending_module")
    st.session_state["nav_radio"] = _target_mod
    st.session_state["active_module"] = _target_mod


def _navigate_to(module_name: str) -> None:
    """Chuyển phân hệ đồng bộ cả trạng thái nội bộ lẫn radio Sidebar."""
    st.session_state["pending_module"] = module_name
    st.session_state["active_module"] = module_name
    st.rerun()


with st.sidebar:
    st.markdown(
        f"""
        <div style="padding:14px 16px;border-radius:12px;background:linear-gradient(135deg,#064E3B,#0F766E);color:#FFFFFF;border-bottom:3px solid #C2410C;margin-bottom:14px;box-shadow:0 4px 12px rgba(6,78,59,0.16);">
          <div style="font-family:'EB Garamond',Georgia,serif;font-size:23px;font-weight:700;letter-spacing:0.2px;display:flex;align-items:center;gap:8px;">{BRAND_EMBLEM_SVG} FinAudit AI</div>
          <div style="font-size:13px;color:#FDBA74;margin-top:4px;font-weight:600;">FinForensics • Chuẩn VAS &amp; TT 99/2025</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    role_options = list(ROLE_PROFILES.keys())
    active_role = st.selectbox(
        "Vai trò sử dụng (5 nhóm đối tượng)",
        options=role_options,
        key="role_selector",
        help="Chọn vai trò của bạn để hiển thị gợi ý thao tác phù hợp trong 5 phân hệ hiện có.",
    )
    st.session_state["active_role"] = active_role

    active_module = st.radio(
        "Điều hướng 5 Phân hệ",
        options=MODULES,
        key="nav_radio",
    )
    st.session_state["active_module"] = active_module

    st.divider()
    st.markdown("**Truy cập nhanh Hồ sơ 360° (Mẫu tiêu biểu)**")
    q_cols = st.columns(3)
    quick_presets = [
        ("TDH", "TDH • Đỏ"),
        ("QCG", "QCG • Đỏ"),
        ("NVL", "NVL • TD"),
        ("DRH", "DRH • TD"),
        ("FPT", "FPT • AT"),
        ("VNM", "VNM • AT"),
    ]
    for i, (tkr, lbl) in enumerate(quick_presets):
        if q_cols[i % 3].button(lbl, key=f"quick_{tkr}", width="stretch"):
            st.session_state["selected_ticker"] = tkr
            st.session_state["selected_year"] = 2025
            _navigate_to(MODULES[1])

    st.divider()
    st.markdown(
        """
        <div style="background:#FAF8F5;border:1px solid #D1DDD8;border-left:3px solid #064E3B;border-radius:10px;padding:12px 14px;font-size:13.8px;color:#132A23;line-height:1.6;">
          <strong style="color:#064E3B;">Phạm vi dữ liệu thực tế:</strong><br/>
          • <strong>643 DN</strong> phi tài chính (HOSE/HNX)<br/>
          • <strong>4,340</strong> firm-years chấm điểm (2019–2025)<br/>
          • <strong>38 DN</strong> bóc tách B09-DN + <strong>4 PDF</strong> 2025<br/>
          • <strong>Zero-API Mode:</strong> Chạy 100% cục bộ
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Tùy chọn Gemini API Key (Không bắt buộc)"):
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza... (Để trống = dùng Zero-API)",
            help="Mặc định hệ thống chạy 100% miễn phí không cần API key. Nhập key nếu muốn AI tóm tắt mở rộng ở Phân hệ 4.",
        )


def render_top_institutional_bar() -> None:
    """Hiển thị Thanh Sticky Top Banner + Ô Tìm kiếm Nhanh Toàn trang + Gợi ý Vai trò (Thành phần bắt buộc 1)."""
    render_sticky_top_banner(st.session_state["active_role"], st.session_state["active_module"])

    role_prof = ROLE_PROFILES.get(st.session_state["active_role"], {})
    rec_idx = int(role_prof.get("recommended_module_idx", 0))
    rec_mod = MODULES[rec_idx]
    rec_lbl = str(role_prof.get("recommended_label", "Đi tới phân hệ gợi ý"))

    u1, u2, u3 = st.columns([2.5, 0.85, 1.65])
    quick_q = u1.text_input(
        "Tra cứu nhanh toàn hệ thống",
        label_visibility="collapsed",
        placeholder="Nhập Mã CK (VD: FPT, TDH, NVL) → Hồ sơ 360° | Hoặc từ khóa Luật (TT 99/2025, VSA 240) → Tra cứu Pháp lý...",
        key="global_quick_search_input",
    )
    if u2.button("Tra nhanh →", key="btn_global_quick_search", width="stretch"):
        raw_q = quick_q.strip()
        if raw_q:
            valid_tickers = set(df_all.dropna(subset=["composite_risk_score"])["ticker"].unique().tolist())
            q_upper = raw_q.upper()
            if q_upper in valid_tickers:
                tkr_years = sorted(
                    df_all[(df_all["ticker"] == q_upper) & (df_all["composite_risk_score"].notna())]["year"].unique().tolist(),
                    reverse=True,
                )
                st.session_state["selected_ticker"] = q_upper
                st.session_state["selected_year"] = int(tkr_years[0]) if tkr_years else 2025
                _navigate_to(MODULES[1])
            else:
                st.session_state["rag_query_text"] = raw_q
                _navigate_to(MODULES[3])

    if st.session_state["active_module"] != rec_mod:
        if u3.button(rec_lbl, key="btn_role_jump", type="primary", width="stretch"):
            _navigate_to(rec_mod)
    else:
        u3.markdown(
            '<div style="min-height:46px;display:flex;align-items:center;justify-content:center;gap:7px;'
            'background:#ECFDF5;border:1px solid #A7F3D0;border-radius:10px;color:#059669;'
            'font-size:13.8px;font-weight:700;padding:0 12px;">'
            '<span class="fa-dot fa-dot-green"></span>Đang ở phân hệ ưu tiên cho vai trò</div>',
            unsafe_allow_html=True,
        )

    render_role_guidance_strip(st.session_state["active_role"])


# ===========================================================================
# PHÂN HỆ 1: TỔNG QUAN THỊ TRƯỜNG & QUÉT RỦI RO NGÀNH ICB
# ===========================================================================
def render_module_1_market_radar() -> None:
    render_hero(
        kicker="PHÂN HỆ 1 • MARKET & SECTOR RADAR",
        title="Tổng quan Thị trường & Quét Rủi ro Pháp chứng Ngành ICB",
        subtitle=(
            "Sàng lọc nhanh toàn bộ 643 doanh nghiệp phi tài chính niêm yết trên HOSE & HNX (2019–2025). "
            "Phát hiện tức thì nhóm doanh nghiệp rơi vào <strong>Cảnh báo Đỏ (&ge; 65đ)</strong> và hiện tượng <strong>Phân kỳ Dòng tiền</strong>."
        ),
        right_badge="<strong>Nguồn dữ liệu:</strong> Vietcap IQ API<br/><strong>Chuẩn mực:</strong> TT 200/2014 &amp; TT 99/2025",
    )

    df_scored_only = df_all.dropna(subset=["composite_risk_score"]).copy()
    avail_years = sorted(df_scored_only["year"].unique().tolist(), reverse=True)
    all_sectors = sorted(df_scored_only["icb_sector_vi"].dropna().unique().tolist())

    with st.container():
        f1, f2, f3, f4 = st.columns([1.1, 2.2, 1.5, 1.4])
        yr_sel = f1.selectbox("Năm tài chính", avail_years, index=0)
        sec_sel = f2.multiselect("Lọc Ngành ICB (để trống = toàn bộ 15 ngành)", all_sectors, default=[])
        tier_sel = f3.multiselect(
            "Hạng Rủi ro",
            ["Cao (Cảnh báo Đỏ)", "Trung bình (Cần theo dõi)", "Thấp (An toàn)"],
            default=[],
        )
        ex_sel = f4.multiselect("Sàn giao dịch", ["HOSE", "HNX"], default=["HOSE", "HNX"])

    df_f_multiyear = df_scored_only[df_scored_only["exchange"].isin(ex_sel)].copy()
    if sec_sel:
        df_f_multiyear = df_f_multiyear[df_f_multiyear["icb_sector_vi"].isin(sec_sel)]
    if tier_sel:
        df_f_multiyear = df_f_multiyear[df_f_multiyear["risk_tier"].isin(tier_sel)]

    search_txt = st.text_input("Tìm nhanh theo mã cổ phiếu hoặc tên doanh nghiệp", placeholder="Nhập VD: TDH, QCG, FPT, Vinamilk...")
    if search_txt.strip():
        q_s = search_txt.strip().lower()
        df_f_multiyear = df_f_multiyear[
            df_f_multiyear["ticker"].str.lower().str.contains(q_s, na=False)
            | df_f_multiyear["company_name"].str.lower().str.contains(q_s, na=False)
        ]

    df_f = df_f_multiyear[df_f_multiyear["year"] == yr_sel].copy()

    # 4 Thẻ KPI lớn
    n_firms = len(df_f)
    n_red = int((df_f["composite_risk_score"] >= 65.0).sum())
    pct_red = (n_red / max(n_firms, 1)) * 100.0
    n_div = int(df_f["cash_flow_divergence_flag"].fillna(False).sum())
    pct_div = (n_div / max(n_firms, 1)) * 100.0
    med_score = float(df_f["composite_risk_score"].median()) if n_firms > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Doanh nghiệp đang quét", f"{n_firms:,}", f"Năm {yr_sel} • Sàn {', '.join(ex_sel)}", PALETTE["royal"])
    with k2:
        render_kpi_card("Cảnh báo Đỏ (>= 65đ)", f"{n_red} ({pct_red:.1f}%)", "Cần ưu tiên kiểm toán pháp chứng sâu", PALETTE["red"])
    with k3:
        render_kpi_card("Phân kỳ Dòng tiền (LN+ / CFO-)", f"{n_div} ({pct_div:.1f}%)", "Báo lãi sau thuế nhưng dòng tiền KD âm", PALETTE["amber"])
    with k4:
        render_kpi_card("Điểm Rủi ro Trung vị", f"{med_score:.1f} / 100", "Thang 0–100 (Nền thị trường 29.2đ)", PALETTE["green"] if med_score < 40 else PALETTE["amber"])

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    if df_f.empty:
        st.warning("Không có doanh nghiệp nào khớp bộ lọc hiện tại. Hãy nới rộng điều kiện lọc.")
        return

    chart_mode_m1 = st.radio(
        "Chế độ hiển thị Biểu đồ Thị trường & Ngành",
        options=[
            "Chế độ 2D Chuẩn phân tích (Mặc định — Nhanh, rõ nét)",
            "Chế độ 3D Tương tác & Chuyển động (2019–2025)",
        ],
        horizontal=True,
        key="m1_chart_mode",
    )

    if chart_mode_m1.startswith("Chế độ 2D"):
        c_left, c_right = st.columns([1.2, 1.0])
        with c_left:
            st.plotly_chart(plot_forensic_matrix_2d(df_f), width="stretch")
        with c_right:
            st.plotly_chart(plot_sector_risk_ranking(df_f), width="stretch")
    else:
        st.caption(
            "Hướng dẫn 3D: Kéo chuột để xoay khối 360°, cuộn để thu phóng, bấm Phát chuyển động để xem 643 doanh nghiệp dịch chuyển từ 2019 → 2025. "
            "Chuyển lại Chế độ 2D khi xem nhanh trên điện thoại."
        )
        tab_3d_space, tab_3d_terrain = st.tabs([
            "Không gian Pháp chứng 3D Động (Altman × Beneish × CFO/TS)",
            "Địa hình Rủi ro 3D theo 15 Ngành ICB × 7 Năm (2019–2025)",
        ])
        with tab_3d_space:
            st.plotly_chart(
                plot_forensic_space_3d_animated(df_f_multiyear, selected_year=int(yr_sel)),
                width="stretch",
            )
        with tab_3d_terrain:
            st.plotly_chart(plot_sector_terrain_3d(df_f_multiyear), width="stretch")

    # Bảng Sàng lọc Doanh nghiệp + Mở nhanh Hồ sơ 360
    st.markdown('<div class="fa-section-title">Bảng Sàng lọc Rủi ro Doanh nghiệp (Sắp xếp theo Điểm Rủi ro giảm dần)</div>', unsafe_allow_html=True)
    df_tbl = df_f.sort_values("composite_risk_score", ascending=False).copy()

    jump_c1, jump_c2, jump_c3 = st.columns([2.2, 1.2, 1.2])
    pick_ticker = jump_c1.selectbox(
        "Chọn nhanh 1 doanh nghiệp từ danh sách lọc để mở Hồ sơ 360°",
        options=df_tbl["ticker"].tolist(),
        format_func=lambda t: f"{t} — {df_tbl.loc[df_tbl['ticker']==t, 'company_name'].iloc[0]} ({df_tbl.loc[df_tbl['ticker']==t, 'composite_risk_score'].iloc[0]:.1f}đ)",
    )
    if jump_c2.button("Mở Hồ sơ 360° của mã này", type="primary", width="stretch"):
        st.session_state["selected_ticker"] = pick_ticker
        st.session_state["selected_year"] = int(yr_sel)
        _navigate_to(MODULES[1])

    csv_export = df_tbl[
        [
            "ticker",
            "company_name",
            "exchange",
            "icb_sector_vi",
            "year",
            "composite_risk_score",
            "risk_tier",
            "beneish_m_score",
            "altman_z_double_prime",
            "cfo_to_assets",
            "sensitive_receivables_ratio",
            "net_revenue",
            "net_income",
            "cfo",
            "top_risk_drivers_vi",
        ]
    ].to_csv(index=False, encoding="utf-8-sig")
    jump_c3.download_button(
        "Tải bảng sàng lọc (.CSV)",
        data=csv_export.encode("utf-8-sig"),
        file_name=f"FinAudit_Market_Radar_{yr_sel}.csv",
        mime="text/csv",
        width="stretch",
    )

    disp = df_tbl[
        [
            "ticker",
            "company_name",
            "icb_sector_vi",
            "composite_risk_score",
            "risk_tier",
            "beneish_m_score",
            "altman_z_double_prime",
            "cfo_to_assets",
            "sensitive_receivables_ratio",
            "top_risk_drivers_vi",
        ]
    ].copy()
    disp["cfo_to_assets"] = (disp["cfo_to_assets"] * 100.0).round(1)
    disp["sensitive_receivables_ratio"] = (disp["sensitive_receivables_ratio"] * 100.0).round(1)
    disp.columns = [
        "Mã CK",
        "Tên Doanh nghiệp",
        "Ngành ICB",
        "Điểm Rủi ro",
        "Hạng Cảnh báo",
        "Beneish M",
        "Altman Z''",
        "CFO/TS (%)",
        "SRR (%)",
        "Giải trình Top-3 SHAP",
    ]
    st.dataframe(
        disp,
        width="stretch",
        height=410,
        hide_index=True,
        column_config={
            "Điểm Rủi ro": st.column_config.ProgressColumn(
                "Điểm Rủi ro", format="%.1f đ", min_value=0, max_value=100
            ),
            "Beneish M": st.column_config.NumberColumn(format="%.2f"),
            "Altman Z''": st.column_config.NumberColumn(format="%.2f"),
        },
    )
    render_vsa240_disclaimer()


# ===========================================================================
# PHÂN HỆ 2: HỒ SƠ PHÁP CHỨNG DOANH NGHIỆP 360° & SHAP WATERFALL
# ===========================================================================
def render_module_2_company_dossier() -> None:
    render_hero(
        kicker="PHÂN HỆ 2 • COMPANY FORENSIC DOSSIER 360°",
        title="Hồ sơ Pháp chứng Doanh nghiệp 360° & Giải thích AI (SHAP + Hybrid RAG)",
        subtitle=(
            "Mổ xẻ toàn diện 1 doanh nghiệp: Chấm điểm 4 trụ cột, giải mã nguyên nhân gốc bằng <strong>Biểu đồ Thác nước SHAP</strong>, "
            "so sánh chuẩn ngành ICB, soi xu hướng đa năm và tự động đối chiếu <strong>Luật VAS / Thuyết minh B09-DN / PDF Kiểm toán</strong>."
        ),
        right_badge="<strong>SHAP Fidelity:</strong> R² = 0.9964 | MAE = 0.85đ<br/><strong>Hội tụ kế toán:</strong> 96.31%",
    )

    tickers_avail = sorted(df_all.dropna(subset=["composite_risk_score"])["ticker"].unique().tolist())
    default_idx = tickers_avail.index(st.session_state["selected_ticker"]) if st.session_state["selected_ticker"] in tickers_avail else 0

    sel_c1, sel_c2 = st.columns([2.4, 1.0])
    ticker = sel_c1.selectbox(
        "Chọn Mã doanh nghiệp (643 công ty phi tài chính HOSE/HNX)",
        options=tickers_avail,
        index=default_idx,
        format_func=lambda t: f"{t} — {df_all.loc[df_all['ticker']==t, 'company_name'].iloc[-1]}",
    )
    st.session_state["selected_ticker"] = ticker

    df_comp = df_all[df_all["ticker"] == ticker].sort_values("year").copy()
    valid_years = sorted(df_comp.dropna(subset=["composite_risk_score"])["year"].unique().tolist(), reverse=True)
    yr_idx = valid_years.index(st.session_state["selected_year"]) if st.session_state["selected_year"] in valid_years else 0
    year_sel = sel_c2.selectbox("Năm phân tích", options=valid_years, index=yr_idx)
    st.session_state["selected_year"] = int(year_sel)

    row = df_comp[df_comp["year"] == year_sel].iloc[0]
    score = float(row["composite_risk_score"])

    # Tự động tìm B09-DN & PDF thật (nếu doanh nghiệp nằm trong nhóm 38 DN / 4 PDF 2025)
    sub_b09 = df_b09[(df_b09["ticker"] == ticker) & (df_b09["year"] == year_sel)]
    b09_row = sub_b09.iloc[0] if len(sub_b09) > 0 else None

    pdf_diag, pdf_ret = None, None
    bundled_pdf_name = f"{ticker}_BCTC_{year_sel}_Kiemtoan_Hopnhat.pdf"
    if (SAMPLE_UPLOADS_DIR / bundled_pdf_name).exists():
        pdf_diag, pdf_ret = load_bundled_pdf_index(bundled_pdf_name)

    rag_brief = s4_mod.generate_forensic_rag_brief(
        row,
        legal_retriever=legal_retriever,
        b09_row=b09_row,
        schema_catalog=schema_b09,
        pdf_retriever=pdf_ret,
        pdf_diag=pdf_diag,
    )

    # Banner Định danh + Đồng hồ Gauge
    top_l, top_r = st.columns([1.85, 1.0])
    with top_l:
        badge = risk_badge_html(score, str(row["risk_tier"]))
        div_tag = (
            '<span class="fa-badge fa-badge-red" style="margin-left:6px;"><span class="fa-dot fa-dot-red"></span>Phân kỳ LN (+) / CFO (-)</span>'
            if bool(row.get("cash_flow_divergence_flag", False))
            else '<span class="fa-badge fa-badge-green" style="margin-left:6px;"><span class="fa-dot fa-dot-green"></span>Dòng tiền đồng pha</span>'
        )
        neg_eq_tag = (
            '<span class="fa-badge fa-badge-red" style="margin-left:6px;"><span class="fa-dot fa-dot-red"></span>Âm Vốn chủ sở hữu</span>'
            if bool(row.get("negative_equity_flag", False))
            else ""
        )
        st.markdown(
            f"""
            <div class="fa-card" style="min-height:265px;display:flex;flex-direction:column;justify-content:space-between;gap:12px;">
              <div>
                <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
                  <span style="font-size:25px;font-weight:800;color:#132A23;font-family:monospace;">{ticker}</span>
                  {badge}{div_tag}{neg_eq_tag}
                </div>
                <div style="font-family:'EB Garamond',Georgia,serif;font-size:22px;font-weight:700;color:#064E3B;">{row['company_name']}</div>
                <div style="font-size:14.5px;color:#4B635B;margin-top:4px;">
                  Ngành ICB: <strong>{row['icb_sector_vi']}</strong> • Sàn: <strong>{row['exchange']}</strong> • Năm tài chính: <strong>{year_sel}</strong>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:10px;padding-top:12px;border-top:1px solid #D1DDD8;font-size:13.8px;">
                <div><span style="color:#4B635B;">Tổng Tài sản</span><br/><strong style="font-size:16.5px;color:#132A23;">{row['total_assets']:,.1f} tỷ</strong></div>
                <div><span style="color:#4B635B;">Doanh thu thuần</span><br/><strong style="font-size:16.5px;color:#132A23;">{row['net_revenue']:,.1f} tỷ</strong></div>
                <div><span style="color:#4B635B;">LN Sau thuế</span><br/><strong style="font-size:16.5px;color:{'#059669' if row['net_income']>=0 else '#BE123C'};">{row['net_income']:,.1f} tỷ</strong></div>
                <div><span style="color:#4B635B;">Dòng tiền CFO</span><br/><strong style="font-size:16.5px;color:{'#059669' if row['cfo']>=0 else '#BE123C'};">{row['cfo']:,.1f} tỷ</strong></div>
              </div>
              <div style="font-size:14.5px;color:#132A23;background:#FAF8F5;padding:10px 12px;border-radius:8px;border:1px solid #D1DDD8;line-height:1.5;">
                <strong style="color:#064E3B;">Nhận định AI (SHAP):</strong> {row['top_risk_drivers_vi']}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_r:
        st.plotly_chart(plot_risk_gauge(score, str(row["risk_tier"])), width="stretch")

    # 4 Thẻ Trụ cột
    p1, p2, p3, p4 = st.columns(4)
    s_ben = float(row["score_beneish"])
    s_alt = float(row["score_altman"])
    s_csh = float(row["score_cash_quality"])
    s_iso = float(row["score_isoforest"])

    def _c(v: float) -> str:
        return PALETTE["red"] if v >= 65 else (PALETTE["amber"] if v >= 40 else PALETTE["green"])

    with p1:
        render_kpi_card("1. Beneish M-Score (30%)", f"{s_ben:.1f} đ", f"M = {row['beneish_m_score']:.3f} (Ngưỡng -1.78)", _c(s_ben))
    with p2:
        render_kpi_card("2. Altman Z'' EMS (25%)", f"{s_alt:.1f} đ", f"Z'' = {row['altman_z_double_prime']:.3f} ({row['altman_zone']})", _c(s_alt))
    with p3:
        render_kpi_card(
            "3. Dòng tiền & SRR (20%)",
            f"{s_csh:.1f} đ",
            f"CFO/TS: {row['cfo_to_assets']*100:.1f}% • SRR: {row['sensitive_receivables_ratio']*100:.1f}%",
            _c(s_csh),
        )
    with p4:
        render_kpi_card("4. AI IsoForest (25%)", f"{s_iso:.1f} đ", "Cờ bất thường Top 10%" if bool(row["iso_anomaly_flag"]) else "Trong vùng đám đông ngành", _c(s_iso))

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Biểu đồ SHAP Waterfall + Radar Ngành
    g1, g2 = st.columns([1.35, 1.0])
    with g1:
        st.plotly_chart(plot_shap_waterfall(row), width="stretch")
    with g2:
        st.plotly_chart(plot_sector_radar(row), width="stretch")

    # Biểu đồ Xu hướng Đa năm (Mặc định 2D chuẩn báo cáo, hỗ trợ bật 3D Quỹ đạo Động có Mặt phẳng CFO = 0)
    st.markdown('<div class="fa-section-title">Quỹ đạo Tài chính &amp; Rủi ro Đa năm (2018–2025)</div>', unsafe_allow_html=True)
    trend_mode_m2 = st.radio(
        "Chế độ hiển thị Quỹ đạo Đa năm",
        options=[
            "Chế độ 2D Hai tầng (Mặc định — Chuẩn báo cáo)",
            "Chế độ 3D Quỹ đạo Động (Doanh thu × LNST × CFO — Kèm mặt phẳng CFO = 0)",
        ],
        horizontal=True,
        key="m2_trend_mode",
    )
    if trend_mode_m2.startswith("Chế độ 2D"):
        st.plotly_chart(plot_multiyear_trend(df_comp), width="stretch")
    else:
        st.caption(
            "Cách đọc Quỹ đạo 3D: Các mốc năm rơi xuống dưới mặt phẳng cam (CFO = 0) cho thấy dòng tiền kinh doanh âm; "
            "bấm Chiếu quỹ đạo để xem doanh nghiệp dịch chuyển từ 2018 đến 2025 hoặc xoay 360°."
        )
        st.plotly_chart(plot_company_trajectory_3d_animated(df_comp), width="stretch")

    # Khung Cầu nối SHAP -> Hybrid RAG (Pháp lý + B09-DN + PDF)
    st.markdown('<div class="fa-section-title">Đối chiếu Tự động: Cờ đỏ SHAP → Luật VAS / TT 99/2025 / VSA 240 &amp; Thuyết minh BCTC</div>', unsafe_allow_html=True)

    if pdf_diag is not None:
        p_st = pdf_diag["quality_status"]
        if p_st == "SCANNED_IMAGE_PDF":
            st.warning(
                f"**Phát hiện PDF Scan ảnh (`{pdf_diag['file_name']}`, {pdf_diag['n_pages']} trang, 0 ký tự/trang):** "
                f"Hệ thống từ chối đoán mù và tự động chuyển sang **Kênh 1 (Thuyết minh B09-DN cấu trúc Vietcap IQ)** bên dưới."
            )
        elif p_st == "NOISY_OCR_TEXT":
            st.info(
                f"**Đã liên kết PDF Kiểm toán thật (`{pdf_diag['file_name']}`, {pdf_diag['n_pages']} trang, nhiễu OCR {pdf_diag['ocr_noise_ratio_pct']}%):** "
                f"Hybrid RRF tự động trích xuất cả số liệu B09-DN lẫn trang PDF gốc có liên quan."
            )

    if rag_brief["top_driver_briefs"]:
        for drv in rag_brief["top_driver_briefs"]:
            cites_html = "".join(
                f"<div style='margin-top:6px;'><strong style='color:#064E3B;'>[Căn cứ] {c['citation']}</strong>: {c['excerpt'][:260]}...</div>"
                for c in drv["legal_citations"]
            )
            b09_html = ""
            if drv["b09_note_evidence"]:
                b09_parts = " &nbsp;|&nbsp; ".join(
                    f"<strong>{b['label_vi']}:</strong> {b['value_bn_vnd']:,.2f} tỷ"
                    for b in drv["b09_note_evidence"][:6]
                )
                b09_html = f"<div style='margin-top:10px;padding:10px 12px;background:#F0FDFA;border:1px solid #99F6E4;border-radius:8px;font-size:14.2px;color:#064E3B;'><strong>Bóc tách Thuyết minh B09-DN thật ({ticker} {year_sel}):</strong> {b09_parts}</div>"
            pdf_html = ""
            if drv["pdf_evidence"]:
                for pe in drv["pdf_evidence"]:
                    pdf_html += f"<div style='margin-top:8px;padding:10px 12px;background:#FFF7ED;border:1px solid #FDBA74;border-radius:8px;font-size:14px;color:#9A3412;'><strong>Trích xuất PDF Kiểm toán {pe['citation']}:</strong> {pe['excerpt']}...</div>"

            st.markdown(
                f"""
                <div class="fa-rag-card" style="border-left-color:#BE123C;">
                  <div style="font-size:16px;font-weight:800;color:#132A23;margin-bottom:4px;">
                    Cờ rủi ro: {drv['driver_label_vi']} <span style="color:#BE123C;font-family:monospace;">(+{drv['shap_points']:.2f}đ SHAP)</span>
                  </div>
                  <div class="fa-rag-body">{cites_html}{b09_html}{pdf_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success(
            f"**{ticker} ({year_sel})** không phát sinh bất kỳ cờ đỏ SHAP nào vượt ngưỡng (`> +0.5đ`). "
            "Các chỉ tiêu Beneish, Altman Z'', dòng tiền CFO và cơ cấu tài sản đều nằm trong vùng lành mạnh hơn trung vị ngành."
        )
        if b09_row is not None:
            st.info(
                f"**Xác nhận nhanh từ Thuyết minh B09-DN ({ticker} {year_sel}):** "
                f"Tiền & TĐT: `{b09_row.get('noc1', 0):,.2f} tỷ` (Tiền gửi NH: `{b09_row.get('noc3', 0):,.2f} tỷ`) • "
                f"Đầu tư TC NH: `{b09_row.get('noc6', 0):,.2f} tỷ` • "
                f"Hàng tồn kho gộp: `{b09_row.get('noc15', 0):,.2f} tỷ`."
            )

    # Nút Xuất Hồ sơ Kiểm toán (HTML/In-PDF & CSV)
    st.markdown('<div class="fa-section-title">Xuất Hồ sơ Kiểm toán Pháp chứng (Audit Working Papers)</div>', unsafe_allow_html=True)
    exp1, exp2 = st.columns(2)
    html_report = generate_html_audit_report(row, rag_brief=rag_brief)
    exp1.download_button(
        "Tải Báo cáo Hồ sơ Kiểm toán (.HTML chuẩn A4 In PDF)",
        data=html_report.encode("utf-8"),
        file_name=f"FinAudit_HoSoPhapChung_{ticker}_{year_sel}.html",
        mime="text/html",
        type="primary",
        width="stretch",
    )
    csv_comp = df_comp.to_csv(index=False, encoding="utf-8-sig")
    exp2.download_button(
        f"Tải toàn bộ dữ liệu 8 năm của {ticker} (.CSV)",
        data=csv_comp.encode("utf-8-sig"),
        file_name=f"FinAudit_DuLieu_{ticker}_2018_2025.csv",
        mime="text/csv",
        width="stretch",
    )
    render_vsa240_disclaimer()


# ===========================================================================
# PHÂN HỆ 3: PHÒNG THẨM ĐỊNH BCTC MỚI (UPLOAD CSV/EXCEL & WHAT-IF LIVE SCORING)
# ===========================================================================
def _display_live_scoring_result(df_live_scored: pd.DataFrame, checks: list[dict[str, str]]) -> None:
    # Hiển thị kết quả Trạm 0 (Data Integrity Gate)
    st.markdown("#### Kết quả Trạm 0 — Kiểm định Toàn vẹn Số liệu (Data Integrity Gate)")
    chk_cols = st.columns(max(len(checks), 1))
    for i, ck in enumerate(checks):
        with chk_cols[i]:
            if ck["status"] == "PASS":
                st.success(f"**[ĐẠT] {ck['title']}**\n\n{ck['detail']}")
            elif ck["status"] == "WARN":
                st.warning(f"**[LƯU Ý] {ck['title']}**\n\n{ck['detail']}")
            else:
                st.error(f"**[LỖI] {ck['title']}**\n\n{ck['detail']}")

    if any(c["status"] == "ERROR" for c in checks):
        return

    scored_rows = df_live_scored.dropna(subset=["composite_risk_score"]).copy()
    if scored_rows.empty:
        st.error("Chưa đủ chuỗi 2 năm liên tiếp hợp lệ để chấm điểm. Hãy kiểm tra lại cột `year`.")
        return

    st.markdown("#### Kết quả Chấm điểm Trực tiếp (Chạy thật qua Chuyên gia 1 → Chuyên gia 2 → Chuyên gia 3)")
    summary_disp = scored_rows[
        [
            "ticker",
            "year",
            "icb_sector_vi",
            "composite_risk_score",
            "risk_tier",
            "beneish_m_score",
            "altman_z_double_prime",
            "cfo_to_assets",
            "sensitive_receivables_ratio",
            "top_risk_drivers_vi",
        ]
    ].copy()
    summary_disp["cfo_to_assets"] = (summary_disp["cfo_to_assets"] * 100).round(1)
    summary_disp["sensitive_receivables_ratio"] = (summary_disp["sensitive_receivables_ratio"] * 100).round(1)
    summary_disp.columns = [
        "Mã DN",
        "Năm",
        "Ngành ICB",
        "Điểm Rủi ro",
        "Hạng Cảnh báo",
        "Beneish M",
        "Altman Z''",
        "CFO/TS (%)",
        "SRR (%)",
        "Top nguyên nhân SHAP",
    ]
    st.dataframe(summary_disp, width="stretch", hide_index=True)

    # Cho chọn 1 dòng vừa chấm để xem chi tiết Gauge + SHAP + RAG + Export HTML
    row_labels = [f"{r['ticker']} ({int(r['year'])}) — {r['composite_risk_score']:.1f}đ ({r['risk_tier']})" for _, r in scored_rows.iterrows()]
    sel_idx = st.selectbox("Xem chi tiết phân tích SHAP & Pháp lý cho hồ sơ vừa chấm", range(len(row_labels)), format_func=lambda i: row_labels[i])
    row = scored_rows.iloc[sel_idx]

    c1, c2 = st.columns([1.0, 1.5])
    with c1:
        st.plotly_chart(plot_risk_gauge(float(row["composite_risk_score"]), str(row["risk_tier"])), width="stretch")
        st.plotly_chart(plot_sector_radar(row), width="stretch")
    with c2:
        st.plotly_chart(plot_shap_waterfall(row), width="stretch")
        rag_brief = s4_mod.generate_forensic_rag_brief(row, legal_retriever=legal_retriever)
        if rag_brief["top_driver_briefs"]:
            st.markdown("**Căn cứ Pháp lý & Thủ tục Kiểm toán tự động gợi ý (Chuyên gia 3):**")
            for drv in rag_brief["top_driver_briefs"]:
                cites = " | ".join(c["citation"] for c in drv["legal_citations"])
                st.markdown(
                    f"""
                    <div class="fa-rag-card" style="padding:12px 14px;border-left-color:#BE123C;">
                      <div class="fa-rag-cite" style="color:#132A23;">Cờ rủi ro: {drv['driver_label_vi']} <span style="color:#BE123C;">(+{drv['shap_points']:.2f}đ)</span></div>
                      <div class="fa-rag-meta">{cites}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("Không có nhân tố SHAP vượt ngưỡng cảnh báo; hồ sơ tài chính nằm trong vùng lành mạnh.")

        html_out = generate_html_audit_report(row, rag_brief=rag_brief)
        st.download_button(
            f"Xuất Báo cáo Kiểm toán cho {row['ticker']} ({int(row['year'])}) (.HTML / In PDF)",
            data=html_out.encode("utf-8"),
            file_name=f"FinAudit_LiveScore_{row['ticker']}_{int(row['year'])}.html",
            mime="text/html",
            type="primary",
            width="stretch",
        )


def render_module_3_live_scoring() -> None:
    render_hero(
        kicker="PHÂN HỆ 3 • UPLOAD & LIVE SCORING LAB",
        title="Phòng Thẩm định BCTC Mới & Giả lập Kịch bản Trực tiếp (What-If)",
        subtitle=(
            "Tải lên file <strong>Excel / CSV</strong> BCTC 2 năm của bất kỳ doanh nghiệp nào (kể cả DN SME chưa niêm yết hoặc báo cáo quý mới) "
            "hoặc chỉnh trực tiếp con số trên bảng để chạy nối tiếp <strong>Tiền kiểm → CG1 → CG2 (AI+SHAP) → CG3 (RAG)</strong> trong ~1 giây."
        ),
        right_badge="<strong>Tốc độ chấm Live:</strong> &lt; 1 giây<br/><strong>Chuẩn đối chiếu:</strong> 15 Ngành ICB",
    )

    tab_up, tab_whatif = st.tabs(["Tải lên File Excel / CSV BCTC Mới", "Giả lập Kịch bản Trực tiếp (What-If Simulator)"])

    with tab_up:
        st.markdown("##### Bước 1: Tải File Mẫu Chuẩn VAS (Đã điền sẵn 2 công ty mẫu *Minh Bạch* & *Thổi Số*)")
        dl1, dl2 = st.columns(2)
        dl1.download_button(
            "Tải File Mẫu Excel (.XLSX — có sheet Hướng dẫn)",
            data=datasets["xlsx_tpl"].read_bytes(),
            file_name="Mau_Upload_BCTC_FinAudit_AI.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
        dl2.download_button(
            "Tải File Mẫu CSV (.CSV chuẩn UTF-8)",
            data=datasets["csv_tpl"].read_bytes(),
            file_name="Mau_Upload_BCTC_FinAudit_AI.csv",
            mime="text/csv",
            width="stretch",
        )

        st.markdown("##### Bước 2: Tải lên file BCTC của bạn (hoặc bấm thử ngay trên bộ mẫu 2 công ty)")
        uploaded = st.file_uploader("Kéo thả file .CSV hoặc .XLSX (tối thiểu 2 năm liên tiếp cho mỗi DN)", type=["csv", "xlsx"])

        run_sample_btn = st.button("Chạy thử ngay trên bộ mẫu (CTCP Minh Bạch vs. CTCP Thổi Số)", type="primary")
        df_to_score = None
        if uploaded is not None:
            try:
                if uploaded.name.lower().endswith(".csv"):
                    df_to_score = pd.read_csv(uploaded)
                else:
                    df_to_score = pd.read_excel(uploaded, sheet_name=0)
                st.info(f"Đã đọc thành công `{uploaded.name}` ({len(df_to_score)} dòng × {df_to_score.shape[1]} cột).")
            except Exception as exc:
                st.error(f"Không thể đọc file tải lên: {exc}")
        elif run_sample_btn:
            df_to_score = pd.DataFrame(SAMPLE_WORKED_EXAMPLES)

        if df_to_score is not None:
            t0 = time.perf_counter()
            df_res, checks = run_live_scoring_pipeline(df_to_score, df_all, df_bench, artifacts)
            elapsed = time.perf_counter() - t0
            st.caption(f"Hoàn tất luồng tuần tự Tiền kiểm → CG1 → CG2 (AI+SHAP) trong `{elapsed:.2f} giây`.")
            _display_live_scoring_result(df_res, checks)

    with tab_whatif:
        st.markdown(
            "Chọn 1 bộ số liệu gốc rồi **chỉnh trực tiếp các con số năm 2025** (VD: thử tăng Phải thu KH lên gấp đôi, hoặc đổi CFO từ dương sang âm) để xem AI & SHAP phản ứng tức thì:"
        )
        preset_choice = st.selectbox(
            "Nạp bộ số liệu khởi đầu (2 năm 2024–2025)",
            [
                "CTCP Mẫu Thổi Số (Bất động sản — Cảnh báo Đỏ)",
                "CTCP Mẫu Minh Bạch (Thực phẩm & Đồ uống — An toàn)",
                "Dữ liệu thật: FPT (2024–2025)",
                "Dữ liệu thật: TDH (2024–2025)",
            ],
        )
        if preset_choice.startswith("CTCP Mẫu Thổi Số"):
            base_2yr = pd.DataFrame([r for r in SAMPLE_WORKED_EXAMPLES if r["ticker"] == "THOI_SO"])
        elif preset_choice.startswith("CTCP Mẫu Minh Bạch"):
            base_2yr = pd.DataFrame([r for r in SAMPLE_WORKED_EXAMPLES if r["ticker"] == "MINH_BACH"])
        else:
            t_pick = "FPT" if "FPT" in preset_choice else "TDH"
            req_plus = [
                "ticker", "company_name", "icb_sector_vi", "year",
                "total_assets", "current_assets", "cash_and_equivalents",
                "short_term_receivables", "accounts_receivable", "prepayments_to_suppliers",
                "other_receivables_st", "provision_doubtful_debts", "inventory",
                "other_receivables_lt", "ppe_net", "construction_in_progress",
                "long_term_investments", "total_liabilities", "current_liabilities",
                "total_equity", "retained_earnings", "net_revenue", "cogs",
                "gross_profit", "sga_expenses", "operating_income", "ebit",
                "net_income", "cfo", "depreciation",
            ]
            base_2yr = df_all[(df_all["ticker"] == t_pick) & (df_all["year"].isin([2024, 2025]))][req_plus].copy()

        all_sectors = sorted(df_all["icb_sector_vi"].dropna().unique().tolist())
        cur_sec = str(base_2yr["icb_sector_vi"].iloc[-1])
        sec_override = st.selectbox("Ngành ICB dùng để đối sánh chuẩn ngành", all_sectors, index=all_sectors.index(cur_sec) if cur_sec in all_sectors else 0)
        base_2yr["icb_sector_vi"] = sec_override

        edited_df = st.data_editor(
            base_2yr.reset_index(drop=True),
            width="stretch",
            num_rows="fixed",
            disabled=["ticker", "year", "icb_sector_vi"],
            key=f"whatif_editor_{preset_choice}",
        )

        if st.button("Chạy Chấm điểm Trực tiếp cho Kịch bản vừa chỉnh", type="primary", width="stretch"):
            t0 = time.perf_counter()
            df_res, checks = run_live_scoring_pipeline(edited_df, df_all, df_bench, artifacts)
            elapsed = time.perf_counter() - t0
            st.caption(f"Hoàn tất chấm điểm kịch bản What-If trong `{elapsed:.2f} giây`.")
            _display_live_scoring_result(df_res, checks)

    render_vsa240_disclaimer()


# ===========================================================================
# PHÂN HỆ 4: TRỢ LÝ AI SOI THUYẾT MINH PDF & TRA CỨU PHÁP LÝ VAS (HYBRID RAG)
# ===========================================================================
def render_module_4_hybrid_rag() -> None:
    render_hero(
        kicker="PHÂN HỆ 4 • GROUNDED HYBRID RAG ASSISTANT",
        title="Trợ lý AI Soi Thuyết minh PDF & Tra cứu Pháp lý VAS / TT 99/2025 / VSA 240",
        subtitle=(
            "Động cơ tìm kiếm lai <strong>BM25 Dual-VN ∥ TF-IDF Word+Char → Weighted RRF</strong> (chạy <code>&lt; 2 ms</code>, không cần API Key). "
            "Tích hợp <strong>Cổng Chống Ảo giác 100%</strong> và <strong>Bộ chẩn đoán PDF 3 tầng</strong> tự cứu mù PDF scan bằng Kênh 1 B09-DN."
        ),
        right_badge="<strong>Legal 20Q:</strong> Hit@1 95% | Hit@3 100%<br/><strong>Anti-Hallucination:</strong> 100% (5/5)",
    )

    tab_law, tab_pdf = st.tabs(["Tra cứu Pháp lý VAS / TT 99/2025 / TT 48 / VSA 240", "Soi File PDF BCTC Kiểm toán & B09-DN (Kiến trúc 2 Kênh)"])

    with tab_law:
        st.markdown("##### Chọn nhanh câu hỏi kiểm toán mẫu (bao gồm câu test chống ảo giác) hoặc gõ câu hỏi của bạn:")
        presets = [
            "Theo Thông tư 99/2025, Bảng cân đối kế toán đổi tên thành gì và hiệu lực khi nào?",
            "Sự khác nhau giữa Thông tư 48/2019 và Thông tư 200/99 khi trích lập dự phòng thuế TNDN và BCTC?",
            "Khoản nợ phải thu quá hạn 1-2 năm và trên 3 năm trích dự phòng bao nhiêu phần trăm?",
            "3 thủ tục kiểm toán bắt buộc đối phó Ban Giám đốc khống chế kiểm soát theo VSA 240?",
            "Nêu 5 điều kiện ghi nhận doanh thu bán hàng theo VAS 14 và rủi ro DSRI > 1.465?",
            "[Test Chống Ảo giác] Dự báo thời tiết Hà Nội ngày mai có mưa bão không?",
        ]
        if "rag_query_text" not in st.session_state:
            st.session_state["rag_query_text"] = presets[0]

        p_cols = st.columns(3)
        for idx, pq in enumerate(presets):
            short_lbl = pq[:46] + ("..." if len(pq) > 46 else "")
            if p_cols[idx % 3].button(short_lbl, key=f"rag_pre_{idx}", width="stretch"):
                st.session_state["rag_query_text"] = pq.replace("[Test Chống Ảo giác] ", "")

        q_col, m_col, k_col = st.columns([3.0, 1.1, 0.7])
        query_in = q_col.text_input("Nhập câu hỏi pháp lý / nghiệp vụ kiểm toán (có dấu hoặc không dấu đều được)", value=st.session_state["rag_query_text"])
        mode_map = {
            "Hybrid RRF (Khuyên dùng)": "hybrid_rrf",
            "Okapi BM25 Dual-VN": "bm25_dual",
            "TF-IDF Word+Char": "tfidf_wc",
            "BM25 Raw (So sánh)": "bm25_raw",
        }
        mode_lbl = m_col.selectbox("Thuật toán truy xuất", list(mode_map.keys()), index=0)
        top_k = k_col.selectbox("Số trích dẫn", [3, 5], index=0)

        if query_in.strip():
            res = legal_retriever.search(
                query_in.strip(),
                top_k=int(top_k),
                mode=mode_map[mode_lbl],
                enable_abstention=True,
            )
            st.caption(
                f"Độ trễ truy xuất: `{res['latency_ms']:.2f} ms` • "
                f"Word TF-IDF max: `{res['max_word_tfidf']:.4f}` • "
                f"Hybrid TF-IDF max: `{res['max_tfidf_wc']:.4f}` • "
                f"BM25 Dual max: `{res['max_bm25_dual']:.2f}`"
            )
            if res["abstained"]:
                st.error(
                    f"**CỔNG CHỐNG ẢO GIÁC ĐÃ KÍCH HOẠT (ANTI-HALLUCINATION ABSTENTION)**\n\n"
                    f"{res['abstention_reason']}"
                )
            else:
                if gemini_key.strip():
                    if st.button("Tóm tắt tổng hợp mở rộng bằng Gemini API (Grounded trên các nguồn dưới)"):
                        with st.spinner("Đang gọi Gemini tổng hợp dựa trên trích dẫn..."):
                            gem_out = call_optional_gemini_synthesis(gemini_key, query_in, res["results"])
                        st.info(gem_out)

                for hit in res["results"]:
                    body_clean = hit["full_text"].replace("\n", "<br/>")
                    st.markdown(
                        f"""
                        <div class="fa-rag-card">
                          <div class="fa-rag-cite">#{hit['rank']} • {hit['citation']}</div>
                          <div class="fa-rag-body">{body_clean}</div>
                          <div class="fa-rag-meta">
                            Score ({res['mode']}): {hit['score']:.5f} &nbsp;|&nbsp;
                            BM25 Dual: {hit['bm25_dual']:.2f} &nbsp;|&nbsp;
                            TF-IDF Word+Char: {hit['tfidf_wc']:.4f} &nbsp;|&nbsp;
                            Tài liệu: {hit['doc_id']}
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # Thành phần bắt buộc 2: Danh mục Hiệu lực Văn bản Pháp quy chuẩn Bộ Tài chính
        render_legal_registry_table()

    with tab_pdf:
        st.markdown("##### Chọn 1 trong 4 bộ PDF Kiểm toán 2025 thật (HOSE/Vietstock) HOẶC tải lên file PDF BCTC của bạn:")
        src_col1, src_col2 = st.columns([1.3, 1.3])
        bundled_options = [
            "NVL_BCTC_2025_Kiemtoan_Hopnhat.pdf (91 trang — OCR Nhiễu, Moore AISC)",
            "TDH_BCTC_2025_Kiemtoan_Hopnhat.pdf (52 trang — Scan ảnh 100%)",
            "FPT_BCTC_2025_Kiemtoan_Hopnhat.pdf (73 trang — Scan ảnh 100%)",
            "VNM_BCTC_2025_Kiemtoan_Hopnhat.pdf (63 trang — Scan ảnh 100%)",
        ]
        chosen_bundled = src_col1.selectbox("Chọn PDF BCTC Kiểm toán 2025 thật có sẵn", bundled_options)
        up_pdf = src_col2.file_uploader("Hoặc tải lên file PDF BCTC / Thuyết minh B09-DN (.pdf)", type=["pdf"])

        diag: dict[str, Any] | None = None
        pdf_ret = None
        active_ticker_for_b09 = None

        if up_pdf is not None:
            tmp_pdf = SAMPLE_UPLOADS_DIR / ".tmp_user_upload.pdf"
            tmp_pdf.write_bytes(up_pdf.getvalue())
            try:
                with st.spinner(f"Đang chẩn đoán và lập chỉ mục `{up_pdf.name}`..."):
                    diag, p_chunks = s4_mod.extract_and_diagnose_pdf(tmp_pdf)
                    diag["file_name"] = up_pdf.name
                    pdf_ret = s4_mod.HybridRAGRetriever(p_chunks, rrf_k=30) if p_chunks else None
            finally:
                tmp_pdf.unlink(missing_ok=True)
        else:
            fname = chosen_bundled.split(" ")[0]
            active_ticker_for_b09 = fname.split("_")[0]
            with st.spinner(f"Đang nạp & chẩn đoán `{fname}`..."):
                diag, pdf_ret = load_bundled_pdf_index(fname)

        if diag is not None:
            d1, d2, d3, d4 = st.columns(4)
            st_status = diag["quality_status"]
            st_color = PALETTE["green"] if st_status == "NATIVE_TEXT_CLEAN" else (PALETTE["amber"] if st_status == "NOISY_OCR_TEXT" else PALETTE["red"])
            with d1:
                render_kpi_card("Phân loại PDF 3 tầng", st_status.replace("_", " "), f"{diag['file_size_mb']} MB • {diag['n_pages']} trang", st_color)
            with d2:
                render_kpi_card("Trang có văn bản", f"{diag['text_pages']} / {diag['n_pages']}", f"Scan/trống: {diag['scan_or_empty_pages']} trang ({diag['scan_ratio_pct']}%)", PALETTE["royal"])
            with d3:
                render_kpi_card("Mật độ ký tự / trang", f"{diag['avg_chars_per_page']:,.1f}", f"Tổng {diag['total_chars']:,} ký tự trích xuất", PALETTE["navy"])
            with d4:
                render_kpi_card("Tỷ lệ nhiễu OCR", f"{diag['ocr_noise_ratio_pct']:.2f}%", f"Đã lập chỉ mục {diag['n_chunks_indexed']} đoạn", PALETTE["amber"] if diag["ocr_noise_ratio_pct"] >= 4 else PALETTE["green"])

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            if st_status == "SCANNED_IMAGE_PDF":
                st.error(f"**CẢNH BÁO PDF SCAN ẢNH:** {diag['recommendation_vi']}")
                if active_ticker_for_b09:
                    sub_b09 = df_b09[(df_b09["ticker"] == active_ticker_for_b09) & (df_b09["year"] == 2025)]
                    if len(sub_b09) > 0:
                        st.success(f"**Tự động kích hoạt Kênh 1 — Bóc tách Thuyết minh B09-DN cấu trúc thật (`{active_ticker_for_b09} 2025`, Vietcap IQ API):**")
                        r_b09 = sub_b09.iloc[0]
                        b09_rows = []
                        for k, meta in schema_b09.items():
                            v = r_b09.get(k, np.nan)
                            if pd.notna(v) and abs(float(v)) > 0.01:
                                b09_rows.append(
                                    {
                                        "Mã trường": k,
                                        "Cấp": f"L{meta.get('level', '')}",
                                        "Khoản mục Thuyết minh B09-DN": meta.get("title_vi", k),
                                        "Giá trị năm 2025 (Tỷ VND)": round(float(v), 2),
                                    }
                                )
                        st.dataframe(pd.DataFrame(b09_rows), width="stretch", height=360, hide_index=True)
            else:
                st.info(f"**Chẩn đoán chất lượng:** {diag['recommendation_vi']}")
                st.markdown("**Tìm nhanh các điểm nóng kiểm toán trong file PDF này:**")
                pdf_quick = [
                    "Vấn đề cần nhấn mạnh giả định hoạt động liên tục lưu chuyển tiền thuần âm",
                    "Thuyết minh vay ngân hàng TMCP chi tiết các khoản vay và trái phiếu",
                    "Thuyết minh hàng tồn kho bất động sản để bán đang xây dựng dở dang",
                    "Bảng cân đối kế toán phải thu ngắn hạn khác dự phòng khó đòi",
                    "Ghi nhận và khấu hao tài sản cố định hữu hình nguyên giá hao mòn",
                ]
                if "pdf_search_q" not in st.session_state:
                    st.session_state["pdf_search_q"] = pdf_quick[0]
                pq_cols = st.columns(len(pdf_quick))
                pq_short = ["Hoạt động liên tục", "Vay & Trái phiếu", "Hàng tồn kho BĐS", "Phải thu khác", "Khấu hao TSCĐ"]
                for i, pq in enumerate(pdf_quick):
                    if pq_cols[i].button(pq_short[i], key=f"pdf_q_{i}", width="stretch"):
                        st.session_state["pdf_search_q"] = pq

                pdf_q_in = st.text_input("Từ khóa soi trong file PDF", value=st.session_state["pdf_search_q"])
                if pdf_ret is not None and pdf_q_in.strip():
                    p_res = pdf_ret.search(pdf_q_in.strip(), top_k=3, mode="hybrid_rrf", enable_abstention=False)
                    st.caption(f"Tìm trên {diag['n_chunks_indexed']} đoạn PDF trong `{p_res['latency_ms']:.2f} ms` (Hybrid RRF kháng nhiễu OCR).")
                    for h in p_res["results"]:
                        st.markdown(
                            f"""
                            <div class="fa-rag-card" style="border-left-color:#059669;">
                              <div class="fa-rag-cite" style="color:#059669;">#{h['rank']} • {h['citation']}</div>
                              <div class="fa-rag-body">{h['full_text'][:900]}</div>
                              <div class="fa-rag-meta">RRF: {h['score']:.5f} &nbsp;|&nbsp; BM25 Dual: {h['bm25_dual']:.2f} &nbsp;|&nbsp; TF-IDF Word+Char: {h['tfidf_wc']:.4f}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    render_vsa240_disclaimer()


# ===========================================================================
# PHÂN HỆ 5: TRUNG TÂM KIỂM CHỨNG KHOA HỌC & QUẢN TRỊ MINH BẠCH (ESG-G)
# ===========================================================================
def render_module_5_validation_governance() -> None:
    render_hero(
        kicker="PHÂN HỆ 5 • VALIDATION & ESG-G GOVERNANCE CENTER",
        title="Trung tâm Kiểm chứng Khoa học 4 Giai đoạn & Tác động Quản trị ESG (Trụ cột G)",
        subtitle=(
            "Công khai toàn bộ bằng chứng kiểm định thực nghiệm trên <strong>643 doanh nghiệp thật (5,007 firm-years)</strong>: "
            "từ phễu lọc dữ liệu, Unit Test công thức, 4 lớp kiểm chứng AI (SHAP, Backtest AUC), đối sánh B09-DN/PDF đến giới hạn minh bạch."
        ),
        right_badge="<strong>Backtest AUC:</strong> 0.9299 (p = 5.77e-22)<br/><strong>Bluechip False Red Flag:</strong> 0.00%",
    )

    bt = s3_sum["layer4_empirical_backtest"]
    l1 = s3_sum["layer1_shap_fidelity"]
    l2 = s3_sum["layer2_convergence"]
    l3 = s3_sum["layer3_stability"]
    leg_rrf = s4_sum["legal_benchmark_20q"]["comparison_by_mode"]["hybrid_rrf"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("Backtest AUC-ROC", f"{bt['auc_composite']:.4f}", f"Mann-Whitney p = {bt['mann_whitney_p']:.2e}", PALETTE["royal"])
    with m2:
        render_kpi_card("SHAP Fidelity (Sau tối ưu V2)", f"R² = {l1['surrogate_r2']:.4f}", f"MAE giảm 68.2%: 2.67 → {l1['surrogate_mae_points']:.2f}đ", PALETTE["green"])
    with m3:
        render_kpi_card("Ổn định Out-of-Time (24–25)", f"ρ = {l3['oot_spearman_rho']:.4f}", f"Jaccard Top-10%: {l3['oot_jaccard_top10']*100:.1f}% • Hội tụ {l2['iso_with_accounting_red_flag_pct']}%", PALETTE["royal"])
    with m4:
        render_kpi_card("Hybrid RAG Pháp lý & OCR", f"Hit@3 = {leg_rrf['hit_at_3_pct']:.0f}%", f"Hit@1: {leg_rrf['hit_at_1_pct']:.0f}% • Chống ảo giác: 100%", PALETTE["green"])

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    fig_auc, fig_rag = plot_validation_benchmarks(s3_sum, s4_sum)
    v1, v2 = st.columns(2)
    with v1:
        st.plotly_chart(fig_auc, width="stretch")
    with v2:
        st.plotly_chart(fig_rag, width="stretch")

    t_ai, t_b09, t_esg = st.tabs([
        "Chi tiết Backtest 12 Bluechip vs. 12 DN Biến cố",
        "Đối sánh 6 Chiều B09-DN & Tam giác 3 Nguồn NVL 2025",
        "Tác động ESG (Trụ cột G) & Lộ trình Mở rộng Phase 2",
    ])

    with t_ai:
        bc1, bc2 = st.columns(2)
        with bc1:
            st.markdown("**Nhóm A — 12 Doanh nghiệp Bluechip Minh bạch (0.00% cảnh báo đỏ giả)**")
            df_ga = pd.DataFrame(bt["group_a_table"])[["ticker", "sector", "mean_score", "max_score", "score_2025"]]
            df_ga.columns = ["Mã CK", "Ngành ICB", "Điểm TB 7 năm", "Điểm Đỉnh", "Điểm 2025"]
            st.dataframe(df_ga.round(2), width="stretch", hide_index=True)
        with bc2:
            st.markdown("**Nhóm B — 12 Doanh nghiệp Biến cố / Tái cấu trúc Thực tế**")
            df_gb = pd.DataFrame(bt["group_b_table"])[["ticker", "sector", "mean_score", "max_score", "peak_year", "score_2025"]]
            df_gb.columns = ["Mã CK", "Ngành ICB", "Điểm TB", "Điểm Đỉnh", "Năm đỉnh", "Điểm 2025"]
            st.dataframe(df_gb.round(2), width="stretch", hide_index=True)

    with t_b09:
        st.markdown("**1. Đối sánh chéo 6 chiều giữa Thuyết minh `B09-DN` (Vietcap NOTE) và `B01-DN` (38 DN × 2018–2025)**")
        cc_df = pd.DataFrame(s4_sum["b09_structured_audit"]["cross_check_b09_vs_b01"])
        cc_df["Tỷ lệ hợp lệ (%)"] = cc_df.apply(lambda r: r.get("accounting_consistent_pct", r["exact_match_pct"]), axis=1)
        st.dataframe(
            cc_df[["metric_pair", "n_comparable_firm_years", "exact_match_within_1pct", "Tỷ lệ hợp lệ (%)", "median_rel_diff_pct"]],
            width="stretch",
            hide_index=True,
        )
        st.markdown("**2. Đối sánh tam giác 3 nguồn `NVL 2025` (`B01 API` vs `B09 API` vs `PDF Kiểm toán Moore AISC, 25/03/2026`)**")
        tri_df = pd.DataFrame(s4_sum["nvl_2025_triangulation"]["items"])
        tri_df.columns = ["Khoản mục BCTC (Tỷ VND)", "B01/B03 API", "B09 API", "PDF Kiểm toán Gốc", "Ghi chú Kiểm toán"]
        st.dataframe(tri_df, width="stretch", hide_index=True)

    with t_esg:
        st.markdown(
            """
            <div class="fa-card">
              <h4 style="margin-top:0;font-family:'EB Garamond',Georgia,serif;font-size:23px;color:#064E3B;">Đóng góp trực tiếp vào Phát triển Bền vững — Trụ cột G (Governance: Quản trị &amp; Minh bạch)</h4>
              <ul style="line-height:1.8;color:#132A23;font-size:15.5px;">
                <li><strong>Bảo vệ Nhà đầu tư &amp; Cổ đông thiểu số:</strong> Cảnh báo sớm bất đối xứng thông tin và dấu hiệu suy giảm chất lượng lợi nhuận trước khi biến cố xảy ra.</li>
                <li><strong>Giảm thiểu Rủi ro Tín dụng cho Ngân hàng &amp; Nhà cung cấp:</strong> Tích hợp nhanh vào khâu tiền thẩm định hồ sơ vay hoặc hạn mức công nợ bán chịu với chi phí SaaS tối ưu cho doanh nghiệp vừa và nhỏ.</li>
                <li><strong>Đón đầu Chuẩn mực Pháp lý Mới (Thông tư 99/2025/TT-BTC):</strong> Liên thông dữ liệu lịch sử 2018–2025 (TT 200/2014) với hệ thống Báo cáo Tình hình Tài chính mới hiệu lực từ 01/01/2026.</li>
              </ul>
              <h4 style="font-family:'EB Garamond',Georgia,serif;font-size:23px;color:#C2410C;margin-top:16px;">Giới hạn Trung thực &amp; Lộ trình Mở rộng Phase 2</h4>
              <ul style="line-height:1.8;color:#132A23;font-size:15.5px;">
                <li><strong>Phạm vi ngành hiện tại:</strong> Tập trung 643 DN phi tài chính; khối Ngân hàng/Chứng khoán/Bảo hiểm (chuẩn TT 49/NHNN) sẽ dùng bộ chỉ số CAMELS/NPL chuyên biệt ở Phase 2.</li>
                <li><strong>PDF Scan ảnh đóng dấu (75% mẫu 2025):</strong> MVP hiện chủ động phát hiện và chuyển sang Kênh 1 (<code>B09-DN</code> cấu trúc); Phase 2 sẽ tích hợp OCR đa phương thức (PaddleOCR / Gemini Vision).</li>
                <li><strong>Mở rộng sản phẩm Phase 2 (<code>OmniReconcile</code>):</strong> Đối soát hóa đơn điện tử &amp; sàn TMĐT cho hộ kinh doanh/SME theo lộ trình NĐ 117/2025 &amp; NĐ 252/2026.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_vsa240_disclaimer()


# ---------------------------------------------------------------------------
# 3. ĐIỀU PHỐI HIỂN THỊ THANH BANNER CỐ ĐỊNH & PHÂN HỆ ĐANG CHỌN
# ---------------------------------------------------------------------------
render_top_institutional_bar()

if active_module == MODULES[0]:
    render_module_1_market_radar()
elif active_module == MODULES[1]:
    render_module_2_company_dossier()
elif active_module == MODULES[2]:
    render_module_3_live_scoring()
elif active_module == MODULES[3]:
    render_module_4_hybrid_rag()
else:
    render_module_5_validation_governance()
