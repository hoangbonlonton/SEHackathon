"""
FINAUDIT AI — FINFORENSICS | CỔNG PHÁP CHỨNG TÀI CHÍNH CHUẨN CÔNG SỞ (BẢN V4)
=============================================================================
Dự án: SE-Hackathon Challenge 2026 (Trường Kinh tế — ĐH Công nghiệp Hà Nội)
Kiến trúc 4 Phân hệ Làm việc Thực thụ (Tinh gọn cho Môi trường Công sở):
  1. Tổng quan Thị trường (Cổng Tra cứu, 3 Lối vào Đầu vào, Bảng Sàng lọc 643 DN & Biểu đồ 15 Ngành)
  2. Hồ sơ Doanh nghiệp 360° (Đồng bộ Live Vietcap IQ, Thẻ Xếp hạng Hạng A/B/C, Nguyên nhân SHAP,
     So sánh Hơn/Kém Trung vị Ngành, Diễn biến 8 năm & Xuất Báo cáo A4 PDF)
  3. Kiểm tra BCTC của Bạn (Quy trình 3 Bước, Tải lên Linh hoạt Excel/CSV chuẩn hoặc tự do & Chỉnh số Trực tiếp)
  4. Trợ lý Pháp lý & Soi PDF (Khung Chat rộng toàn màn hình, nút Đính kèm PDF tích hợp,
     Tách rõ Trả lời & Trích dẫn kèm Link Cổng Chính phủ, Gợi ý động sau khi trả lời)
  + Hộp thoại "Giới thiệu Phương pháp & Bằng chứng Kiểm định" ẩn gọn ở Chân trang (dành cho Ban Giám khảo).

Khởi chạy:
  streamlit run stage_5_web_app_deployment/app.py
"""

from __future__ import annotations

from html import escape
import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx
import joblib
import numpy as np
import pandas as pd
import streamlit as st

STAGE5_DIR = Path(__file__).resolve().parent
ROOT_DIR = STAGE5_DIR.parent
DATA_PROCESSED_DIR = ROOT_DIR / "data_store" / "processed"
MODELS_DIR = ROOT_DIR / "data_store" / "models"
SAMPLE_UPLOADS_DIR = ROOT_DIR / "data_store" / "sample_uploads"
STAGE4_PATH = ROOT_DIR / "stage_4_rag_legal_notes" / "04_hybrid_rag_engine.py"
LEGAL_CORPUS_DIR = ROOT_DIR / "stage_4_rag_legal_notes" / "legal_corpus"

if str(STAGE5_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE5_DIR))

from chat_assistant import _gov_link_pill, answer_chat_query
from live_scoring_service import (
    SAMPLE_WORKED_EXAMPLES,
    ensure_sample_upload_files,
    run_live_scoring_pipeline,
    smart_normalize_uploaded_bctc,
    sync_company_live_from_vietcap,
)
from report_exporter import generate_html_audit_report
from ui_components import (
    PALETTE,
    ROLE_PROFILES,
    format_rag_markdown_to_html,
    inject_fintech_css,
    plot_forensic_matrix_2d,
    plot_multiyear_trend,
    plot_sector_risk_ranking,
    plot_shap_waterfall,
    plot_validation_benchmarks,
    render_auto_insight,
    render_kpi_card,
    render_legal_registry_table,
    render_peer_comparison_panel,
    render_scientific_risk_card,
    render_score_scale_legend,
    render_sticky_top_banner,
    render_vsa240_disclaimer,
    render_wizard_steps,
    risk_badge_html,
    translate_altman_zone,
    trim_excerpt_clean,
)

# ---------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG (THU GỌN SIDEBAR MẶC ĐỊNH ĐỂ MỞ RỘNG 100% KHÔNG GIAN CÔNG SỞ)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FinAudit AI — Cổng Pháp chứng Báo cáo Tài chính Việt Nam",
    layout="wide",
    initial_sidebar_state="collapsed",
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
    """Hook tùy chọn Gemini API (chỉ chạy khi người dùng tự nhập API key trong Sidebar)."""
    context_txt = "\n\n".join(f"NGUỒN {h['citation']}:\n{h['full_text'][:1200]}" for h in retrieved_hits[:3])
    prompt = (
        "Bạn là chuyên gia kiểm toán pháp chứng Việt Nam tuân thủ VSA 240 và Thông tư 99/2025/TT-BTC.\n"
        "Chỉ trả lời dựa trên NGUỒN tài liệu cung cấp dưới đây, bắt buộc trích dẫn đúng [Nguồn] trong ngoặc vuông, "
        "không suy diễn ngoài nguồn.\n\n"
        f"CÂU HỎI: {question}\n\n{context_txt}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key.strip()}"
    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if resp.status_code == 200:
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"Không gọi được Gemini API (HTTP {resp.status_code}). Hệ thống hiển thị trực tiếp nguồn trích dẫn cục bộ."
    except Exception as exc:
        return f"Lỗi kết nối Gemini API ({type(exc).__name__}). Hệ thống hiển thị trực tiếp nguồn trích dẫn cục bộ."


# ---------------------------------------------------------------------------
# 2. KHỞI TẠO DỮ LIỆU, TRẠNG THÁI & 4 PHÂN HỆ LÀM VIỆC CHÍNH
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
    "1. Tổng quan Thị trường",
    "2. Hồ sơ Doanh nghiệp 360°",
    "3. Kiểm tra BCTC của Bạn",
    "4. Trợ lý Pháp lý & Soi PDF",
]

NAV_ICONS = [
    ":material/monitoring:",
    ":material/account_balance:",
    ":material/upload_file:",
    ":material/gavel:",
]

BUNDLED_PDF_OPTIONS = [
    "Không đính kèm PDF (Chỉ hỏi Luật & Dữ liệu 643 DN)",
    "NVL_BCTC_2025_Kiemtoan_Hopnhat.pdf (Novaland 2025 — 91 trang)",
    "TDH_BCTC_2025_Kiemtoan_Hopnhat.pdf (Thủ Đức House 2025 — 52 trang)",
    "FPT_BCTC_2025_Kiemtoan_Hopnhat.pdf (FPT 2025 — 73 trang)",
    "VNM_BCTC_2025_Kiemtoan_Hopnhat.pdf (Vinamilk 2025 — 63 trang)",
]

if "active_module" not in st.session_state:
    st.session_state["active_module"] = MODULES[0]
if "active_role" not in st.session_state:
    st.session_state["active_role"] = "Kiểm toán viên"
if "role_selector" not in st.session_state:
    st.session_state["role_selector"] = st.session_state["active_role"]
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TDH"
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = 2025
if "chat_drawer_open" not in st.session_state:
    st.session_state["chat_drawer_open"] = False
if "about_modal_open" not in st.session_state:
    st.session_state["about_modal_open"] = False
if "live_synced_companies" not in st.session_state:
    st.session_state["live_synced_companies"] = {}  # ticker -> {df, msg, synced_at}
if "chat_bundled_pdf" not in st.session_state:
    st.session_state["chat_bundled_pdf"] = BUNDLED_PDF_OPTIONS[0]
if "uploaded_pdf_cache" not in st.session_state:
    st.session_state["uploaded_pdf_cache"] = None
if "m4_active_section" not in st.session_state:
    st.session_state["m4_active_section"] = 0
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "title": "Xin chào — Trợ lý Pháp lý & Tài chính FinAudit AI",
            "body_html": (
                "<div style='font-size:16.5px;line-height:1.72;color:#132A23;'>"
                "Bạn có thể gõ câu hỏi tiếng Việt tự nhiên ở bên dưới về <strong>Luật Kế toán – Kiểm toán</strong> "
                "(VAS, Thông tư 99/2025, Thông tư 48/2019, VSA 240), <strong>số liệu 643 DN niêm yết</strong>, "
                "hoặc bấm nút <strong>Đính kèm PDF</strong> cạnh ô nhập để soi Báo cáo tài chính."
                "</div>"
            ),
            "meta": "Mỗi câu trả lời đều tách rõ nội dung giải đáp và căn cứ trích dẫn kèm liên kết Cổng Chính phủ",
            "abstained": False,
            "followups": [],  # Không hiện gợi ý cố định gây vướng — chỉ gợi ý động SAU khi người dùng hỏi!
        }
    ]


def _navigate_to(module_name: str) -> None:
    st.session_state["active_module"] = module_name
    st.rerun()


def _close_chat_drawer() -> None:
    st.session_state["chat_drawer_open"] = False


def _close_about_modal() -> None:
    st.session_state["about_modal_open"] = False


def _get_active_chat_pdf() -> tuple[dict[str, Any] | None, Any, str | None]:
    up_cache = st.session_state.get("uploaded_pdf_cache")
    if up_cache is not None:
        return up_cache["diag"], up_cache["retriever"], None
    chosen = st.session_state.get("chat_bundled_pdf", BUNDLED_PDF_OPTIONS[0])
    if chosen.startswith("Không đính kèm"):
        return None, None, None
    fname = chosen.split(" ")[0]
    ticker_hint = fname.split("_")[0]
    diag, pdf_ret = load_bundled_pdf_index(fname)
    return diag, pdf_ret, ticker_hint


def _append_chat_turn(
    question: str,
    scope: str = "Tự động (Luật VAS + PDF đính kèm)",
    gemini_api_key: str = "",
) -> None:
    """Thực thi hội thoại tự nhiên (tự chọn động cơ tối ưu nhất, không bắt người dùng chọn mô hình)."""
    q_clean = question.strip()
    if not q_clean:
        return
    st.session_state["chat_messages"].append({"role": "user", "text": q_clean})
    pdf_diag, pdf_ret, ticker_hint = _get_active_chat_pdf()
    reply = answer_chat_query(
        question=q_clean,
        scope=scope,
        legal_retriever=legal_retriever,
        df_all=df_all,
        df_b09=df_b09,
        pdf_diag=pdf_diag,
        pdf_ret=pdf_ret,
        ticker_hint=ticker_hint,
        mode_code="hybrid_rrf",
        top_k=3,
        gemini_api_key=gemini_api_key,
        gemini_fn=call_optional_gemini_synthesis,
    )
    st.session_state["chat_messages"].append(
        {
            "role": "assistant",
            "title": reply["title"],
            "body_html": reply["body_html"],
            "meta": reply["meta"],
            "abstained": reply["abstained"],
            "followups": reply.get("followups", []),
        }
    )


def _render_pdf_attach_popover(prefix: str) -> None:
    """Nút Đính kèm PDF gọn gàng (bấm mới mở, không chiếm chỗ cố định trên giao diện chat)."""
    pdf_diag, _, _ = _get_active_chat_pdf()
    btn_lbl = f"PDF: {pdf_diag['file_name'][:18]}" if pdf_diag is not None else "Đính kèm PDF"
    with st.popover(btn_lbl, icon=":material/attach_file:", width="stretch"):
        st.markdown("**Tải lên file PDF BCTC hoặc chọn mẫu 2025 có sẵn**")
        up_f = st.file_uploader(
            "Tải lên file .PDF từ máy tính / điện thoại",
            type=["pdf"],
            key=f"{prefix}_pdf_uploader",
        )
        if up_f is not None:
            prev = st.session_state.get("uploaded_pdf_cache")
            if prev is None or prev["name"] != up_f.name:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
                    tf.write(up_f.getvalue())
                    tmp_p = Path(tf.name)
                try:
                    with st.spinner(f"Đang đọc và chuẩn hóa {up_f.name}"):
                        d_up, c_up = s4_mod.extract_and_diagnose_pdf(tmp_p)
                        d_up["file_name"] = up_f.name
                        r_up = s4_mod.HybridRAGRetriever(c_up, rrf_k=30) if c_up else None
                        st.session_state["uploaded_pdf_cache"] = {"name": up_f.name, "diag": d_up, "retriever": r_up}
                finally:
                    tmp_p.unlink(missing_ok=True)
            if st.button("Gỡ file PDF đang đính kèm", icon=":material/delete:", key=f"{prefix}_clear_pdf", width="stretch"):
                st.session_state["uploaded_pdf_cache"] = None
                st.rerun()
        else:
            st.selectbox(
                "Hoặc chọn 1 trong 4 bộ PDF Kiểm toán 2025 thật",
                options=BUNDLED_PDF_OPTIONS,
                key=f"{prefix}_bundled_sel",
                index=BUNDLED_PDF_OPTIONS.index(st.session_state["chat_bundled_pdf"])
                if st.session_state["chat_bundled_pdf"] in BUNDLED_PDF_OPTIONS
                else 0,
                on_change=lambda: st.session_state.update({"chat_bundled_pdf": st.session_state[f"{prefix}_bundled_sel"]}),
            )


def _render_chat_workspace(prefix: str, feed_height: int = 560, show_top_attach_bar: bool = True) -> None:
    """Khung trò chuyện rộng rãi, thoáng mát kiểu Gemini, cỡ chữ lớn dễ đọc, chỉ hiện gợi ý động sau khi bot trả lời."""
    pdf_diag, _, _ = _get_active_chat_pdf()
    if pdf_diag is not None and show_top_attach_bar:
        st.info(f"Đang đính kèm tài liệu: **{pdf_diag['file_name']}** ({pdf_diag['n_pages']} trang). Câu hỏi của bạn sẽ được đối chiếu cả nội dung file PDF lẫn Luật VAS.")

    msg_box = st.container(height=feed_height, border=True)
    with msg_box:
        for m in st.session_state["chat_messages"]:
            if m["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(f"<div style='font-size:16.8px;font-weight:600;color:#132A23;line-height:1.65;'>{escape(m['text'])}</div>", unsafe_allow_html=True)
            else:
                with st.chat_message("assistant"):
                    st.markdown(
                        f"<div style='font-size:18px;font-weight:800;color:#064E3B;margin-bottom:8px;'>{escape(m['title'])}</div>"
                        f"{m['body_html']}"
                        f"<div style='margin-top:9px;font-size:14px;color:#4B635B;font-weight:600;'>{escape(m['meta'])}</div>",
                        unsafe_allow_html=True,
                    )

    # CHỈ hiển thị 2–3 nút gợi ý tiếp nối SAU KHI Trợ lý đã trả lời (không cố định vướng víu trước khi hỏi!)
    last_msg = st.session_state["chat_messages"][-1]
    dyn_followups: list[str] = last_msg.get("followups", []) if last_msg.get("role") == "assistant" else []
    if dyn_followups:
        st.caption("Gợi ý câu hỏi tiếp theo:")
        f_cols = st.columns(len(dyn_followups))
        for idx_f, fq in enumerate(dyn_followups):
            if f_cols[idx_f].button(fq, icon=":material/subdirectory_arrow_right:", key=f"{prefix}_dyn_fq_{len(st.session_state['chat_messages'])}_{idx_f}", width="stretch"):
                _append_chat_turn(fq, gemini_api_key=gemini_key)
                st.rerun()

    # Khu nhập liệu rộng rãi, thoáng mát và góc cạnh nghiêm chỉnh
    if show_top_attach_bar:
        bar_attach, bar_form, bar_reset = st.columns([1.15, 5.2, 0.85], gap="small", vertical_alignment="center")
        with bar_attach:
            _render_pdf_attach_popover(prefix)
        with bar_form:
            with st.form(f"{prefix}_input_form", clear_on_submit=True):
                ic1, ic2 = st.columns([4.6, 0.95], gap="small", vertical_alignment="center")
                u_q = ic1.text_input(
                    "Nhập câu hỏi",
                    label_visibility="collapsed",
                    placeholder="Nhập câu hỏi Luật VAS, Thông tư 99/2025, VSA 240, mã cổ phiếu hoặc nội dung file PDF...",
                )
                sent = ic2.form_submit_button("Gửi", icon=":material/send:", type="primary", width="stretch")
                if sent and u_q.strip():
                    _append_chat_turn(u_q.strip(), gemini_api_key=gemini_key)
                    st.rerun()
        with bar_reset:
            if st.button("Làm mới", icon=":material/restart_alt:", key=f"{prefix}_reset_chat", width="stretch"):
                st.session_state["chat_messages"] = st.session_state["chat_messages"][:1]
                st.rerun()
    else:
        with st.form(f"{prefix}_input_form", clear_on_submit=True):
            ic1, ic2 = st.columns([5.0, 1.0], gap="small", vertical_alignment="center")
            u_q = ic1.text_input(
                "Nhập câu hỏi",
                label_visibility="collapsed",
                placeholder="Nhập câu hỏi Luật VAS, Thông tư 99/2025, VSA 240, mã cổ phiếu hoặc nội dung file PDF...",
            )
            sent = ic2.form_submit_button("Gửi", icon=":material/send:", type="primary", width="stretch")
            if sent and u_q.strip():
                _append_chat_turn(u_q.strip(), gemini_api_key=gemini_key)
                st.rerun()


# ---------------------------------------------------------------------------
# 3. SIDEBAR THU GỌN MẶC ĐỊNH (DÀNH CHO MỞ NHANH MẪU ĐỐI CHỨNG & API TÙY CHỌN)
# ---------------------------------------------------------------------------
with st.sidebar:
    role_options = list(ROLE_PROFILES.keys())
    active_role = st.selectbox(
        "Vai trò làm việc",
        options=role_options,
        key="role_selector",
    )
    st.session_state["active_role"] = active_role

    st.markdown("**Mở nhanh 6 Hồ sơ Mẫu (2025)**")
    demo_tickers = ["TDH", "QCG", "NVL", "DRH", "FPT", "VNM"]
    df_2025_scores = (
        df_all[df_all["year"] == 2025]
        .dropna(subset=["composite_risk_score"])
        .set_index("ticker")["composite_risk_score"]
        .to_dict()
    )
    for row_i in range(0, len(demo_tickers), 2):
        c_a, c_b = st.columns(2)
        for col_w, tkr in zip((c_a, c_b), demo_tickers[row_i : row_i + 2]):
            sc_v = float(df_2025_scores.get(tkr, 0.0))
            ico = ":material/report:" if sc_v >= 65 else (":material/warning:" if sc_v >= 40 else ":material/check_circle:")
            if col_w.button(f"{tkr} • {sc_v:.0f}/100", icon=ico, key=f"quick_{tkr}", width="stretch"):
                st.session_state["selected_ticker"] = tkr
                st.session_state["selected_year"] = 2025
                _navigate_to(MODULES[1])

    render_score_scale_legend(compact=True)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    with st.expander("Cài đặt API (Không bắt buộc)"):
        gemini_key = st.text_input(
            "Khóa Gemini API",
            type="password",
            placeholder="Để trống để chạy 100% miễn phí cục bộ",
        )
    if st.button("Giới thiệu Phương pháp & Độ tin cậy", icon=":material/info:", key="btn_sidebar_about", width="stretch"):
        st.session_state["about_modal_open"] = True
        st.rerun()


# ---------------------------------------------------------------------------
# 4. HỘP THOẠI CHAT NỔI RỘNG KIỂU GEMINI (TRÊN TRANG 1, 2, 3) & HỘP THOẠI GIỚI THIỆU
# ---------------------------------------------------------------------------
@st.dialog(
    "Không gian Trợ lý Pháp lý & Tài chính FinAudit AI",
    width="large",
    dismissible=True,
    icon=":material/forum:",
    on_dismiss=_close_chat_drawer,
)
def render_chat_drawer_dialog() -> None:
    """Khi bấm vào 'Hỏi Trợ lý AI', hiển thị khung chat TO và RỘNG RÃI theo bố cục 2 cột kiểu Gemini."""
    rail_col, main_col = st.columns([1.0, 3.1], gap="medium")
    with rail_col:
        with st.container(border=True):
            st.markdown(
                "<div style='font-size:17.5px;font-weight:800;color:#064E3B;margin-bottom:6px;'>Tài liệu PDF Đính kèm</div>"
                "<div style='font-size:14.8px;color:#4B635B;margin-bottom:10px;line-height:1.5;'>"
                "Đính kèm BCTC kiểm toán (.PDF) để soi thuyết minh hoặc để trống để hỏi Luật VAS &amp; 643 DN."
                "</div>",
                unsafe_allow_html=True,
            )
            _render_pdf_attach_popover("drawer_rail")
            pdf_diag, _, _ = _get_active_chat_pdf()
            if pdf_diag is not None:
                st.success(f"Đang gắn: **{pdf_diag['file_name']}** ({pdf_diag['n_pages']} trang)")
            else:
                st.caption("Trạng thái: Hỏi đáp Luật VAS & Dữ liệu 643 DN")

            st.markdown("<hr style='margin:12px 0;border:none;border-top:1px solid #D1DDD8;'/>", unsafe_allow_html=True)
            if st.button("Làm mới cuộc trò chuyện", icon=":material/restart_alt:", key="drawer_rail_reset", width="stretch"):
                st.session_state["chat_messages"] = st.session_state["chat_messages"][:1]
                st.rerun()
            if st.button("Mở toàn trang Pháp lý", icon=":material/open_in_full:", key="drawer_open_full_m4", width="stretch"):
                st.session_state["chat_drawer_open"] = False
                st.session_state["m4_active_section"] = 0
                _navigate_to(MODULES[3])
    with main_col:
        _render_chat_workspace(prefix="drawer", feed_height=520, show_top_attach_bar=False)


@st.dialog(
    "Giới thiệu Phương pháp Khoa học & Bằng chứng Kiểm định",
    width="large",
    dismissible=True,
    icon=":material/verified:",
    on_dismiss=_close_about_modal,
)
def render_about_methodology_dialog() -> None:
    """Ẩn gọn phần kiểm chứng học thuật (AUC, Backtest, ESG) vào mục Giới thiệu — gọn cho dân công sở, đủ cho Ban Giám khảo."""
    bt = s3_sum["layer4_empirical_backtest"]
    l1 = s3_sum["layer1_shap_fidelity"]
    l3 = s3_sum["layer3_stability"]
    leg_rrf = s4_sum["legal_benchmark_20q"]["comparison_by_mode"]["hybrid_rrf"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("Độ chính xác (AUC)", f"{bt['auc_composite']:.4f}", "0% báo động giả trên 12 DN minh bạch", PALETTE["royal"])
    with m2:
        render_kpi_card("Độ khớp Giải thích", f"{l1['surrogate_r2']*100:.2f}%", f"Sai số trung bình {l1['surrogate_mae_points']:.2f} / 100", PALETTE["green"])
    with m3:
        render_kpi_card("Ổn định qua các năm", f"{l3['oot_spearman_rho']*100:.2f}%", "Tương quan xếp hạng 2024–2025", PALETTE["royal"])
    with m4:
        render_kpi_card("Chính xác Trợ lý Luật", f"{leg_rrf['hit_at_3_pct']:.0f}%", f"Đúng #1: {leg_rrf['hit_at_1_pct']:.0f}% • Chống ảo giác: 100%", PALETTE["green"])

    fig_auc, fig_rag = plot_validation_benchmarks(s3_sum, s4_sum)
    c1, c2 = st.columns(2)
    c1.plotly_chart(fig_auc, width="stretch")
    c2.plotly_chart(fig_rag, width="stretch")

    t1, t2, t3 = st.tabs([
        "Đối chứng 12 DN Minh bạch vs. 12 DN Biến cố",
        "Đối sánh Thuyết minh B09-DN & PDF Gốc (NVL 2025)",
        "Tác động ESG (Trụ cột G)",
    ])
    with t1:
        bc1, bc2 = st.columns(2)
        with bc1:
            df_ga = pd.DataFrame(bt["group_a_table"])[["ticker", "sector", "mean_score", "score_2025"]]
            df_ga.columns = ["Mã CK", "Ngành", "TB 7 năm", "2025"]
            st.dataframe(df_ga.round(1), width="stretch", hide_index=True)
        with bc2:
            df_gb = pd.DataFrame(bt["group_b_table"])[["ticker", "sector", "max_score", "peak_year", "score_2025"]]
            df_gb.columns = ["Mã CK", "Ngành", "Điểm đỉnh", "Năm đỉnh", "2025"]
            st.dataframe(df_gb.round(1), width="stretch", hide_index=True)
    with t2:
        tri_df = pd.DataFrame(s4_sum["nvl_2025_triangulation"]["items"])
        tri_df.columns = ["Khoản mục (Tỷ VND)", "B01/B03 API", "B09 API", "PDF Kiểm toán Gốc", "Ghi chú"]
        st.dataframe(tri_df, width="stretch", hide_index=True)
    with t3:
        st.markdown(
            "- **ESG Trụ cột G (Minh bạch Quản trị):** Cảnh báo sớm bất đối xứng thông tin tài chính cho nhà đầu tư, ngân hàng và đối tác.\n"
            "- **Liên thông Pháp lý:** Kết nối BCTC lịch sử theo **Thông tư 200/2014/TT-BTC** (≤ 2025) sang **Thông tư 99/2025/TT-BTC** (từ 01/01/2026)."
        )


def _render_footer_with_about() -> None:
    render_vsa240_disclaimer()
    fc1, fc2 = st.columns([3.5, 1.3], vertical_alignment="center")
    fc1.caption("Dữ liệu công khai từ Vietcap IQ API & Hệ thống văn bản pháp quy Bộ Tài chính (mof.gov.vn / vbpl.vn).")
    if fc2.button("Giới thiệu Phương pháp & Độ tin cậy", icon=":material/verified:", key="btn_footer_about", width="stretch"):
        st.session_state["about_modal_open"] = True
        st.rerun()


# ---------------------------------------------------------------------------
# 5. ĐẦU TRANG CỔNG THÔNG TIN & 4 THƯ MỤC LÀM VIỆC CHÍNH
# ---------------------------------------------------------------------------
def _handle_portal_search(raw_q: str) -> None:
    q_s = raw_q.strip()
    if not q_s:
        return
    valid_tickers = set(df_all.dropna(subset=["composite_risk_score"])["ticker"].unique().tolist())
    q_upper = q_s.upper()
    if q_upper in valid_tickers:
        tkr_years = sorted(
            df_all[(df_all["ticker"] == q_upper) & (df_all["composite_risk_score"].notna())]["year"].unique().tolist(),
            reverse=True,
        )
        st.session_state["selected_ticker"] = q_upper
        st.session_state["selected_year"] = int(tkr_years[0]) if tkr_years else 2025
        _navigate_to(MODULES[1])
    else:
        _append_chat_turn(q_s, gemini_api_key=gemini_key)
        _navigate_to(MODULES[3])


def render_top_command_bar() -> None:
    render_sticky_top_banner(st.session_state["active_role"], st.session_state["active_module"])
    with st.container(key="top_nav_bar"):
        with st.container(horizontal=True, wrap=True, gap="small"):
            for idx_m, (mod_full, mod_ico) in enumerate(zip(MODULES, NAV_ICONS)):
                is_active = st.session_state["active_module"] == mod_full
                if st.button(
                    mod_full,
                    icon=mod_ico,
                    key=f"nav_btn_{idx_m}",
                    type="primary" if is_active else "secondary",
                ):
                    _navigate_to(mod_full)


# ===========================================================================
# PHÂN HỆ 1: TỔNG QUAN THỊ TRƯỜNG (GỌN SẠCH — KHÔNG 3D — CHỈ DẪN NGẮN GỌN)
# ===========================================================================
def render_module_1_market_radar() -> None:
    # Banner nền nghệ thuật Đông Sơn + Khung Tìm kiếm + 3 Lối vào rõ ngay Đầu vào
    with st.container(key="home_portal_hero"):
        st.markdown(
            """
            <div class="fa-portal-hero-title">Sàng lọc Rủi ro Báo cáo Tài chính &amp; <span class="fa-dual-gold">Tra cứu Pháp lý VAS</span></div>
            <div class="fa-portal-hero-sub">Kiểm tra nhanh mức độ minh bạch của 643 doanh nghiệp niêm yết, chấm điểm file BCTC của riêng bạn, hoặc hỏi đáp Luật Kế toán – Kiểm toán</div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(key="global_search_box"):
            s1, s2 = st.columns([4.3, 1.1], gap="small", vertical_alignment="center")
            quick_q = s1.text_input(
                "Tra cứu nhanh trên FinAudit AI",
                label_visibility="collapsed",
                placeholder="Nhập Mã doanh nghiệp (VD: HPG, FPT, TDH) hoặc câu hỏi Luật (VD: Nói cho tôi về luật VAS)",
                key="global_quick_search_input",
            )
            if s2.button("Tìm kiếm", icon=":material/search:", key="btn_global_quick_search", width="stretch"):
                _handle_portal_search(quick_q)

        e1, e2, e3 = st.columns(3, gap="medium")
        if e1.button("Soi 1 trong 643 DN niêm yết • Chỉ cần chọn mã", icon=":material/account_balance:", key="home_entry_0", width="stretch"):
            _navigate_to(MODULES[1])
        if e2.button("Chấm điểm BCTC của bạn • Tải Excel / CSV", icon=":material/upload_file:", key="home_entry_1", width="stretch"):
            _navigate_to(MODULES[2])
        if e3.button("Hỏi Luật VAS & Soi file PDF • Mở Trợ lý", icon=":material/gavel:", key="home_entry_2", width="stretch"):
            _navigate_to(MODULES[3])

    # Khu vực Lọc & Sàng lọc Toàn thị trường
    df_scored_only = df_all.dropna(subset=["composite_risk_score"]).copy()
    avail_years = sorted(df_scored_only["year"].unique().tolist(), reverse=True)
    all_sectors = sorted(df_scored_only["icb_sector_vi"].dropna().unique().tolist())

    st.markdown(
        '<div class="fa-section-title">Sàng lọc Nhanh <span class="fa-sec-accent">643 Doanh nghiệp Niêm yết (HOSE &amp; HNX)</span></div>'
        '<div class="fa-micro-guide">Chọn Năm, Ngành hoặc gõ Mã cổ phiếu để lọc danh sách doanh nghiệp cần ưu tiên kiểm tra.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        f1, f2, f3, f4, f5 = st.columns([0.9, 1.8, 1.4, 1.15, 1.45])
        yr_sel = f1.selectbox("Năm", avail_years, index=0)
        sec_sel = f2.multiselect("Ngành nghề", all_sectors, default=[], placeholder="Tất cả 15 ngành")
        tier_sel = f3.multiselect(
            "Mức cảnh báo",
            ["Cao (Cảnh báo Đỏ)", "Trung bình (Cần theo dõi)", "Thấp (An toàn)"],
            default=[],
            placeholder="Tất cả mức cảnh báo",
        )
        ex_sel = f4.multiselect("Sàn", ["HOSE", "HNX"], default=["HOSE", "HNX"], placeholder="Chọn sàn")
        search_txt = f5.text_input("Tìm mã / tên DN", placeholder="VD: HPG, FPT, TDH")

    df_year_all = df_scored_only[(df_scored_only["year"] == yr_sel) & (df_scored_only["exchange"].isin(ex_sel))].copy()
    df_f = df_year_all.copy()
    if sec_sel:
        df_f = df_f[df_f["icb_sector_vi"].isin(sec_sel)]
    if tier_sel:
        df_f = df_f[df_f["risk_tier"].isin(tier_sel)]
    if search_txt.strip():
        q_s = search_txt.strip().lower()
        df_f = df_f[
            df_f["ticker"].str.lower().str.contains(q_s, na=False)
            | df_f["company_name"].str.lower().str.contains(q_s, na=False)
        ]

    n_firms = len(df_f)
    n_red = int((df_f["composite_risk_score"] >= 65.0).sum())
    pct_red = (n_red / max(n_firms, 1)) * 100.0
    n_div = int(df_f["cash_flow_divergence_flag"].fillna(False).sum())
    pct_div = (n_div / max(n_firms, 1)) * 100.0
    med_score = float(df_f["composite_risk_score"].median()) if n_firms > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Doanh nghiệp đang lọc", f"{n_firms:,}", f"Năm {yr_sel} • Sàn {', '.join(ex_sel)}", PALETTE["royal"])
    with k2:
        render_kpi_card("Hạng C • Cảnh báo Cao", f"{n_red} DN ({pct_red:.1f}%)", "Chỉ số ≥ 65/100 — cần kiểm tra sâu", PALETTE["red"])
    with k3:
        render_kpi_card("Báo lãi nhưng Tiền KD âm", f"{n_div} DN ({pct_div:.1f}%)", "Lợi nhuận dương nhưng thiếu dòng tiền", PALETTE["amber"])
    with k4:
        render_kpi_card(
            "Chỉ số Rủi ro Trung vị",
            f"{med_score:.1f} / 100",
            "Mặt bằng thị trường 7 năm: 29.2 / 100",
            PALETTE["green"] if med_score < 40 else PALETTE["amber"],
            score_pct=med_score,
        )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if df_f.empty:
        st.warning("Không có doanh nghiệp nào khớp bộ lọc. Hãy bỏ bớt điều kiện lọc.")
        _render_footer_with_about()
        return

    df_tbl = df_f.sort_values("composite_risk_score", ascending=False).copy()
    top_firm = df_tbl.iloc[0]
    render_auto_insight(
        f"<strong>Tóm tắt nhanh năm {yr_sel}:</strong> Trong <strong>{n_firms:,} doanh nghiệp</strong> đang xem, "
        f"có <strong>{n_red} DN ở Hạng C (Cảnh báo Cao)</strong>; rủi ro cao nhất hiện là "
        f"<strong>{escape(str(top_firm['ticker']))} ({float(top_firm['composite_risk_score']):.1f}/100)</strong>.",
        tone="red" if n_red > 0 else "green",
    )

    # 2 Tab tinh gọn (Bảng làm việc ở Tab 1 mặc định; Biểu đồ 2D ở Tab 2 — KHÔNG CÓ 3D!)
    tab_list, tab_charts = st.tabs([
        "1. Danh sách Doanh nghiệp Cần Theo dõi (Sắp xếp Rủi ro Cao → Thấp)",
        "2. Biểu đồ Xếp hạng 15 Ngành & Bản đồ Toàn thị trường",
    ])

    with tab_list:
        with st.container(border=True):
            jump_c1, jump_c2, jump_c3 = st.columns([2.4, 1.25, 1.05], vertical_alignment="bottom")
            pick_ticker = jump_c1.selectbox(
                "Chọn 1 doanh nghiệp từ bảng bên dưới để mở Hồ sơ chi tiết 360°",
                options=df_tbl["ticker"].tolist(),
                format_func=lambda t: f"{t} — {df_tbl.loc[df_tbl['ticker']==t, 'company_name'].iloc[0]} ({df_tbl.loc[df_tbl['ticker']==t, 'composite_risk_score'].iloc[0]:.1f}/100)",
            )
            if jump_c2.button("Mở Hồ sơ 360°", icon=":material/open_in_new:", type="primary", width="stretch"):
                st.session_state["selected_ticker"] = pick_ticker
                st.session_state["selected_year"] = int(yr_sel)
                _navigate_to(MODULES[1])

            csv_export = df_tbl[
                [
                    "ticker", "company_name", "exchange", "icb_sector_vi", "year",
                    "composite_risk_score", "risk_tier", "beneish_m_score",
                    "altman_z_double_prime", "cfo_to_assets", "sensitive_receivables_ratio",
                    "net_revenue", "net_income", "cfo", "top_risk_drivers_vi",
                ]
            ].to_csv(index=False, encoding="utf-8-sig")
            jump_c3.download_button(
                "Tải Excel/CSV",
                icon=":material/download:",
                data=csv_export.encode("utf-8-sig"),
                file_name=f"FinAudit_SangLoc_{yr_sel}.csv",
                mime="text/csv",
                width="stretch",
            )

            disp = df_tbl[
                [
                    "ticker", "company_name", "icb_sector_vi", "composite_risk_score",
                    "risk_tier", "cfo_to_assets", "sensitive_receivables_ratio", "top_risk_drivers_vi",
                ]
            ].copy()
            disp["cfo_to_assets"] = (disp["cfo_to_assets"] * 100.0).round(1)
            disp["sensitive_receivables_ratio"] = (disp["sensitive_receivables_ratio"] * 100.0).round(1)
            disp.columns = [
                "Mã CK", "Tên Doanh nghiệp", "Ngành nghề", "Chỉ số Rủi ro (/100)",
                "Phân hạng", "Tiền KD / TS (%)", "Tài sản mềm (%)", "3 Nguyên nhân chính",
            ]
            st.dataframe(
                disp,
                width="stretch",
                height=440,
                hide_index=True,
                column_config={
                    "Chỉ số Rủi ro (/100)": st.column_config.ProgressColumn("Chỉ số Rủi ro (/100)", format="%.1f", min_value=0, max_value=100),
                },
            )

    with tab_charts:
        with st.container(border=True):
            c_left, c_right = st.columns([1.05, 1.15])
            with c_left:
                st.plotly_chart(plot_sector_risk_ranking(df_f, df_market_ref=df_year_all), width="stretch")
            with c_right:
                st.plotly_chart(plot_forensic_matrix_2d(df_f, df_market_ref=df_year_all), width="stretch")

    _render_footer_with_about()


# ===========================================================================
# PHÂN HỆ 2: HỒ SƠ DOANH NGHIỆP 360° (ĐỒNG BỘ LIVE • XẾP HẠNG HẠNG A/B/C • SO SÁNH NGÀNH)
# ===========================================================================
def render_module_2_company_dossier() -> None:
    st.markdown(
        '<div class="fa-section-title" style="margin-top:2px;border-left-color:#C2410C;">Hồ sơ Đánh giá <span class="fa-sec-accent">Doanh nghiệp 360°</span></div>'
        '<div class="fa-micro-guide">Chọn Mã doanh nghiệp và Năm cần thẩm định, hoặc bấm Cập nhật trực tuyến để đồng bộ số liệu mới nhất từ Vietcap IQ.</div>',
        unsafe_allow_html=True,
    )

    tickers_avail = sorted(df_all.dropna(subset=["composite_risk_score"])["ticker"].unique().tolist())
    default_idx = tickers_avail.index(st.session_state["selected_ticker"]) if st.session_state["selected_ticker"] in tickers_avail else 0

    with st.container(border=True):
        sel_c1, sel_c2, sel_c3 = st.columns([2.4, 0.9, 1.3], vertical_alignment="bottom")
        ticker = sel_c1.selectbox(
            "Chọn Mã doanh nghiệp (643 công ty niêm yết)",
            options=tickers_avail,
            index=default_idx,
            format_func=lambda t: f"{t} — {df_all.loc[df_all['ticker']==t, 'company_name'].iloc[-1]}",
        )
        st.session_state["selected_ticker"] = ticker

        # Ưu tiên dữ liệu vừa đồng bộ trực tuyến (nếu người dùng đã bấm nút Live Sync cho mã này)
        live_cache = st.session_state["live_synced_companies"].get(ticker)
        df_comp = live_cache["df"].sort_values("year").copy() if live_cache is not None else df_all[df_all["ticker"] == ticker].sort_values("year").copy()

        valid_years = sorted(df_comp.dropna(subset=["composite_risk_score"])["year"].unique().tolist(), reverse=True)
        yr_idx = valid_years.index(st.session_state["selected_year"]) if st.session_state["selected_year"] in valid_years else 0
        year_sel = sel_c2.selectbox("Năm tài chính", options=valid_years, index=yr_idx)
        st.session_state["selected_year"] = int(year_sel)

        if sel_c3.button("Cập nhật Live (Vietcap IQ)", icon=":material/sync:", key="btn_live_sync_company", width="stretch"):
            meta_r = df_all[df_all["ticker"] == ticker].iloc[-1]
            with st.spinner(f"Đang đồng bộ BCTC trực tuyến mới nhất cho {ticker}"):
                df_synced, msg_sync, ts_sync = sync_company_live_from_vietcap(ticker, meta_r, df_all, df_bench, artifacts)
            if df_synced is not None:
                st.session_state["live_synced_companies"][ticker] = {"df": df_synced, "msg": msg_sync, "synced_at": ts_sync}
                st.session_state["selected_year"] = int(df_synced.dropna(subset=["composite_risk_score"])["year"].max())
                st.rerun()
            else:
                st.warning(msg_sync)

    if live_cache is not None:
        st.success(live_cache["msg"])

    row = df_comp[df_comp["year"] == year_sel].iloc[0]
    prev_rows = df_comp[df_comp["year"] == year_sel - 1]
    prev_row = prev_rows.iloc[0] if len(prev_rows) > 0 else None
    score = float(row["composite_risk_score"])

    def _yoy_badge(cur_v: float, prev_col: str) -> str:
        if prev_row is None or pd.isna(prev_row.get(prev_col)) or abs(float(prev_row[prev_col])) < 1e-3:
            return ""
        pv = float(prev_row[prev_col])
        pct = ((cur_v - pv) / abs(pv)) * 100.0
        col = "#059669" if pct >= 0 else "#BE123C"
        return f"<span style='font-size:12px;font-weight:700;color:{col};margin-left:4px;'>({pct:+.1f}%)</span>"

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

    # Khối trên: Thông tin Định danh & 4 Con số Tài chính (kèm % tăng/giảm) | Thẻ Xếp hạng Khoa học Hạng A/B/C
    top_l, top_r = st.columns([1.65, 1.05], gap="medium")
    with top_l:
        div_tag = (
            '<span class="fa-badge fa-badge-red"><span class="fa-dot fa-dot-red"></span>Báo lãi nhưng Dòng tiền KD âm</span>'
            if bool(row.get("cash_flow_divergence_flag", False))
            else '<span class="fa-badge fa-badge-green"><span class="fa-dot fa-dot-green"></span>Dòng tiền đồng pha lợi nhuận</span>'
        )
        neg_eq_tag = (
            '<span class="fa-badge fa-badge-red"><span class="fa-dot fa-dot-red"></span>Âm Vốn chủ sở hữu</span>'
            if bool(row.get("negative_equity_flag", False))
            else ""
        )
        st.markdown(
            f"""
            <div class="fa-card" style="min-height:262px;display:flex;flex-direction:column;justify-content:space-between;gap:14px;margin-bottom:0;">
              <div>
                <div style="display:flex;align-items:center;flex-wrap:wrap;gap:9px;margin-bottom:7px;">
                  <span style="font-size:29px;font-weight:800;color:#132A23;font-family:var(--fa-font-mono);">{escape(ticker)}</span>
                  {div_tag}{neg_eq_tag}
                </div>
                <div style="font-family:var(--fa-font-head);font-size:23px;font-weight:800;color:#064E3B;">{escape(str(row['company_name']))}</div>
                <div style="font-size:15.8px;color:#4B635B;margin-top:4px;">
                  Ngành: <strong>{escape(str(row['icb_sector_vi']))}</strong> • Sàn: <strong>{escape(str(row['exchange']))}</strong> • Năm: <strong>{year_sel}</strong> (Đơn vị: Tỷ VND)
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;padding-top:13px;border-top:1px solid #D1DDD8;">
                <div><span style="font-size:14.5px;color:#4B635B;font-weight:600;">Tổng Tài sản</span><br/><strong style="font-size:20px;font-family:var(--fa-font-mono);color:#132A23;">{row['total_assets']:,.1f}</strong>{_yoy_badge(float(row['total_assets']), 'total_assets')}</div>
                <div><span style="font-size:14.5px;color:#4B635B;font-weight:600;">Doanh thu thuần</span><br/><strong style="font-size:20px;font-family:var(--fa-font-mono);color:#132A23;">{row['net_revenue']:,.1f}</strong>{_yoy_badge(float(row['net_revenue']), 'net_revenue')}</div>
                <div><span style="font-size:14.5px;color:#4B635B;font-weight:600;">Lợi nhuận sau thuế</span><br/><strong style="font-size:20px;font-family:var(--fa-font-mono);color:{'#059669' if row['net_income']>=0 else '#BE123C'};">{row['net_income']:,.1f}</strong></div>
                <div><span style="font-size:14.5px;color:#4B635B;font-weight:600;">Dòng tiền kinh doanh</span><br/><strong style="font-size:20px;font-family:var(--fa-font-mono);color:{'#059669' if row['cfo']>=0 else '#BE123C'};">{row['cfo']:,.1f}</strong></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_r:
        render_scientific_risk_card(score, str(row["risk_tier"]), ticker=ticker, year=year_sel)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # 4 Thẻ Trụ cột với thang đo chuẩn / 100 điểm
    p1, p2, p3, p4 = st.columns(4)
    s_ben, s_alt, s_csh, s_iso = float(row["score_beneish"]), float(row["score_altman"]), float(row["score_cash_quality"]), float(row["score_isoforest"])

    def _c(v: float) -> str:
        return PALETTE["red"] if v >= 65 else (PALETTE["amber"] if v >= 40 else PALETTE["green"])

    with p1:
        render_kpi_card("1. Nguy cơ Thổi số (30%)", f"{s_ben:.1f} / 100", f"Chỉ số Beneish: {row['beneish_m_score']:.2f} (Ngưỡng -1.78)", _c(s_ben), score_pct=s_ben)
    with p2:
        render_kpi_card("2. Sức khỏe Trả nợ (25%)", f"{s_alt:.1f} / 100", f"{translate_altman_zone(row['altman_zone'])} (Altman: {row['altman_z_double_prime']:.2f})", _c(s_alt), score_pct=s_alt)
    with p3:
        render_kpi_card("3. Chất lượng Dòng tiền (20%)", f"{s_csh:.1f} / 100", f"Tiền KD/TS: {row['cfo_to_assets']*100:.1f}% • TS mềm: {row['sensitive_receivables_ratio']*100:.1f}%", _c(s_csh), score_pct=s_csh)
    with p4:
        render_kpi_card("4. Bất thường Ngành (25%)", f"{s_iso:.1f} / 100", "Bất thường Top 10% ngành" if bool(row["iso_anomaly_flag"]) else "Ổn định trong mặt bằng ngành", _c(s_iso), score_pct=s_iso)

    # Phần A: Giải thích Nguyên nhân (SHAP) + Câu Kết luận Tự động 1 dòng
    st.markdown(
        '<div class="fa-section-title">Phân tích Nguyên nhân <span class="fa-sec-accent">&amp; So sánh Trực diện với Ngành</span></div>',
        unsafe_allow_html=True,
    )
    render_auto_insight(
        f"<strong>Kết luận nguyên nhân ({escape(ticker)} {year_sel}):</strong> {escape(str(row['top_risk_drivers_vi']))}.",
        tone="red" if score >= 65 else ("amber" if score >= 40 else "green"),
    )

    g1, g2 = st.columns([1.05, 1.15], gap="medium")
    with g1:
        with st.container(border=True):
            st.plotly_chart(plot_shap_waterfall(row), width="stretch")
    with g2:
        with st.container(border=True):
            # THAY THẾ Radar khó hiểu bằng Bảng So sánh Trực diện Hơn/Kém so với Trung vị Ngành!
            df_peer = df_all[
                (df_all["icb_sector_vi"] == row["icb_sector_vi"])
                & (df_all["year"] == year_sel)
                & (df_all["composite_risk_score"].notna())
            ]
            if df_peer.empty:
                df_peer = df_all[(df_all["icb_sector_vi"] == row["icb_sector_vi"]) & (df_all["year"] == 2025)]
            render_peer_comparison_panel(row, df_peer)

    # Phần B: Diễn biến 8 năm (Thuần 2D dễ đọc — KHÔNG 3D!)
    st.markdown(
        '<div class="fa-section-title">Diễn biến Tài chính &amp; <span class="fa-sec-accent">Chỉ số Rủi ro qua 8 Năm (2018–2025)</span></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        if bool(row.get("cash_flow_divergence_flag", False)):
            render_auto_insight(
                f"<strong>Lưu ý dòng tiền năm {year_sel}:</strong> {escape(ticker)} ghi nhận lợi nhuận sau thuế <strong>{row['net_income']:,.1f} tỷ</strong> "
                f"nhưng dòng tiền kinh doanh đạt <strong>{row['cfo']:,.1f} tỷ</strong> — cần đối chiếu thu hồi công nợ và tồn kho.",
                tone="amber",
            )
        st.plotly_chart(plot_multiyear_trend(df_comp), width="stretch")

    # Phần C: Đối chiếu Cờ rủi ro -> Luật VAS (kèm link Chính phủ) & Thuyết minh B09-DN
    st.markdown(
        '<div class="fa-section-title">Đối chiếu Tự động: <span class="fa-sec-accent">Điều luật Bộ Tài chính &amp; Thuyết minh BCTC</span></div>',
        unsafe_allow_html=True,
    )
    if pdf_diag is not None and pdf_diag["quality_status"] == "SCANNED_IMAGE_PDF":
        st.info(f"File PDF kiểm toán `{pdf_diag['file_name']}` ({pdf_diag['n_pages']} trang) là bản scan ảnh — hệ thống tự động đối chiếu bằng dữ liệu Thuyết minh B09-DN chính thức bên dưới.")

    def _render_driver_card_html(drv: dict[str, Any], rank_idx: int) -> str:
        cite_blocks = []
        for c in drv["legal_citations"]:
            ex_txt, was_cut = trim_excerpt_clean(c["excerpt"], 300)
            more_tag = "<span class='fa-more-pill'>Xem đầy đủ ↗</span>" if was_cut else ""
            gov_link = _gov_link_pill(c["citation"])
            cite_blocks.append(
                f"<div style='margin-top:8px;padding-bottom:6px;border-bottom:1px dashed #E2EAE7;'>"
                f"<strong style='color:#064E3B;'>[Căn cứ] {escape(c['citation'])}:</strong> "
                f"{format_rag_markdown_to_html(ex_txt)}{more_tag}{gov_link}</div>"
            )
        b09_html = ""
        if drv["b09_note_evidence"]:
            b09_parts = " &nbsp;|&nbsp; ".join(
                f"<strong>{escape(b['label_vi'])}:</strong> {b['value_bn_vnd']:,.2f} tỷ"
                for b in drv["b09_note_evidence"][:6]
            )
            b09_html = (
                f"<div style='margin-top:10px;padding:11px 15px;background:#F0FDFA;border:1px solid #99F6E4;"
                f"border-left:3.5px solid #0F766E;border-radius:4px;font-size:15.5px;color:#064E3B;'>"
                f"<strong>Số liệu Thuyết minh B09-DN ({escape(ticker)} {year_sel}):</strong> {b09_parts}</div>"
            )
        pdf_html = ""
        if drv["pdf_evidence"]:
            for pe in drv["pdf_evidence"]:
                pe_txt, pe_cut = trim_excerpt_clean(pe["excerpt"], 320)
                pe_more = "<span class='fa-more-pill'>Xem trong PDF ↗</span>" if pe_cut else ""
                pdf_html += (
                    f"<div style='margin-top:8px;padding:11px 15px;background:#FFF7ED;border:1px solid #FDBA74;"
                    f"border-left:3.5px solid #C2410C;border-radius:4px;font-size:15.4px;color:#9A3412;'>"
                    f"<strong>Trích từ PDF Kiểm toán {escape(pe['citation'])}:</strong> "
                    f"{format_rag_markdown_to_html(pe_txt)}{pe_more}</div>"
                )
        return (
            f"<div class='fa-rag-card' style='border-left-color:#BE123C;'>"
            f"<div style='font-size:17.5px;font-weight:800;color:#132A23;margin-bottom:7px;'>"
            f"{rank_idx}. {escape(drv['driver_label_vi'])} "
            f"<span style='color:#BE123C;font-family:var(--fa-font-mono);'>(+{drv['shap_points']:.1f} điểm tác động)</span></div>"
            f"<div class='fa-rag-body'>{''.join(cite_blocks)}{b09_html}{pdf_html}</div></div>"
        )

    if rag_brief["top_driver_briefs"]:
        for idx_d, drv in enumerate(rag_brief["top_driver_briefs"], start=1):
            card_html = _render_driver_card_html(drv, idx_d)
            if idx_d == 1:
                st.markdown(card_html, unsafe_allow_html=True)
            else:
                with st.expander(f"Cảnh báo #{idx_d}: {drv['driver_label_vi']} (+{drv['shap_points']:.1f} điểm) — Bấm xem căn cứ luật", expanded=False):
                    st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.success(f"{ticker} ({year_sel}) không phát sinh yếu tố rủi ro vượt ngưỡng cảnh báo; các chỉ tiêu cốt lõi nằm trong vùng an toàn.")

    # Xuất Hồ sơ A4 & CSV
    exp1, exp2 = st.columns(2)
    html_report = generate_html_audit_report(row, rag_brief=rag_brief)
    exp1.download_button(
        "Tải Báo cáo Hồ sơ Kiểm toán A4 (.HTML in PDF)",
        icon=":material/download:",
        data=html_report.encode("utf-8"),
        file_name=f"FinAudit_HoSo_{ticker}_{year_sel}.html",
        mime="text/html",
        type="primary",
        width="stretch",
    )
    exp2.download_button(
        f"Tải dữ liệu 8 năm của {ticker} (.CSV)",
        icon=":material/table_view:",
        data=df_comp.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name=f"FinAudit_DuLieu_{ticker}_2018_2025.csv",
        mime="text/csv",
        width="stretch",
    )
    _render_footer_with_about()


# ===========================================================================
# PHÂN HỆ 3: KIỂM TRA BCTC CỦA BẠN (HỖ TRỢ UPLOAD LINH HOẠT KHÔNG BẮT BUỘC 26 CỘT)
# ===========================================================================
def _display_live_scoring_result(df_live_scored: pd.DataFrame, checks: list[dict[str, str]]) -> None:
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
        st.error("Chưa đủ 2 năm tài chính liền kề hợp lệ để tính chỉ số rủi ro.")
        return

    row_labels = [f"{r['ticker']} ({int(r['year'])}) — {r['composite_risk_score']:.1f} / 100 ({r['risk_tier']})" for _, r in scored_rows.iterrows()]
    sel_idx = st.selectbox("Chọn hồ sơ vừa chấm điểm để xem chi tiết", range(len(row_labels)), format_func=lambda i: row_labels[i])
    row = scored_rows.iloc[sel_idx]

    c1, c2 = st.columns([1.0, 1.45], gap="medium")
    with c1:
        render_scientific_risk_card(float(row["composite_risk_score"]), str(row["risk_tier"]), ticker=str(row["ticker"]), year=int(row["year"]))
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            df_peer = df_all[(df_all["icb_sector_vi"] == row["icb_sector_vi"]) & (df_all["year"] == 2025) & (df_all["composite_risk_score"].notna())]
            render_peer_comparison_panel(row, df_peer)
    with c2:
        with st.container(border=True):
            st.plotly_chart(plot_shap_waterfall(row), width="stretch")
            rag_brief = s4_mod.generate_forensic_rag_brief(row, legal_retriever=legal_retriever)
            if rag_brief["top_driver_briefs"]:
                st.markdown("**Căn cứ Pháp lý & Khoản mục cần ưu tiên soát xét:**")
                for drv in rag_brief["top_driver_briefs"]:
                    cites = " | ".join(c["citation"] for c in drv["legal_citations"])
                    st.markdown(
                        f"<div class='fa-rag-card' style='padding:11px 14px;border-left-color:#BE123C;'>"
                        f"<div class='fa-rag-cite' style='color:#132A23;'>{escape(drv['driver_label_vi'])} "
                        f"<span style='color:#BE123C;'>(+{drv['shap_points']:.1f} điểm)</span></div>"
                        f"<div class='fa-rag-meta'>{escape(cites)}</div></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.success("Hồ sơ tài chính nằm trong vùng an toàn, không phát sinh cảnh báo vượt ngưỡng.")

            html_out = generate_html_audit_report(row, rag_brief=rag_brief)
            st.download_button(
                f"Tải Báo cáo Kiểm toán A4 cho {row['ticker']} ({int(row['year'])}) (.HTML in PDF)",
                icon=":material/download:",
                data=html_out.encode("utf-8"),
                file_name=f"FinAudit_Live_{row['ticker']}_{int(row['year'])}.html",
                mime="text/html",
                type="primary",
                width="stretch",
            )


def render_module_3_live_scoring() -> None:
    st.markdown(
        '<div class="fa-section-title" style="margin-top:2px;border-left-color:#0F766E;">Kiểm tra &amp; Chấm điểm <span class="fa-sec-accent">Báo cáo Tài chính của Bạn</span></div>',
        unsafe_allow_html=True,
    )
    render_wizard_steps()

    all_sectors = sorted(df_all["icb_sector_vi"].dropna().unique().tolist())
    tab_up, tab_whatif = st.tabs(["1. Tải lên File Excel / CSV (Hỗ trợ cả File Mẫu & File Tự do)", "2. Thử nghiệm Chỉnh số Trực tiếp"])

    with tab_up:
        st_c1, st_c2 = st.columns([1.0, 1.35], gap="medium")
        with st_c1:
            with st.container(border=True):
                st.markdown(
                    '<span class="fa-badge fa-badge-green" style="margin-bottom:8px;">TÙY CHỌN 1 • FILE MẪU CHUẨN</span>'
                    '<div style="font-size:19.5px;font-weight:800;color:#064E3B;margin-bottom:6px;">Tải File Mẫu Chuẩn 26 Cột</div>'
                    '<p style="font-size:15.8px;color:#4B635B;margin-bottom:12px;">Cho kết quả chính xác tuyệt đối 100% — đã điền sẵn 2 DN đối chứng (Minh Bạch &amp; Thổi Số).</p>',
                    unsafe_allow_html=True,
                )
                st.download_button("Tải File Mẫu Excel (.XLSX)", icon=":material/download:", data=datasets["xlsx_tpl"].read_bytes(), file_name="Mau_Upload_BCTC_FinAudit_AI.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
                st.download_button("Tải File Mẫu CSV (.CSV)", icon=":material/table_view:", data=datasets["csv_tpl"].read_bytes(), file_name="Mau_Upload_BCTC_FinAudit_AI.csv", mime="text/csv", width="stretch")

        with st_c2:
            with st.container(border=True):
                st.markdown(
                    '<span class="fa-badge fa-badge-copper" style="margin-bottom:8px;">TÙY CHỌN 2 • TẢI FILE CỦA BẠN (LINH HOẠT)</span>'
                    '<div style="font-size:19.5px;font-weight:800;color:#132A23;margin-bottom:5px;">Tải Excel / CSV BCTC 2 Năm bất kỳ</div>'
                    '<p style="font-size:15.5px;color:#4B635B;margin-bottom:10px;">Hỗ trợ cả bảng tiếng Việt không đúng mẫu 26 cột và bảng dọc theo Mẫu B01-DN — hệ thống tự khớp chỉ tiêu &amp; quy đổi tỷ VND.</p>',
                    unsafe_allow_html=True,
                )
                u_m1, u_m2 = st.columns(2)
                def_tkr = u_m1.text_input("Tên/Mã DN (nếu file chưa có)", value="DN_CUA_BAN")
                def_sec = u_m2.selectbox("Ngành đối sánh (nếu file chưa có)", all_sectors, index=all_sectors.index("Xây dựng và Vật liệu") if "Xây dựng và Vật liệu" in all_sectors else 0)
                uploaded = st.file_uploader("Chọn file .XLSX hoặc .CSV (tối thiểu 2 năm liên tiếp)", type=["csv", "xlsx"])
                run_sample_btn = st.button("Chạy thử ngay trên bộ mẫu (Minh Bạch vs. Thổi Số)", icon=":material/play_arrow:", type="primary", width="stretch")

        df_to_score = None
        if uploaded is not None:
            try:
                raw_df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded, sheet_name=0)
                df_norm, map_rep = smart_normalize_uploaded_bctc(raw_df, default_ticker=def_tkr, default_sector=def_sec)
                if map_rep["missing_core"]:
                    st.error(
                        f"File `{uploaded.name}` chưa nhận diện đủ các chỉ tiêu cốt lõi tối thiểu: `{', '.join(map_rep['missing_core'])}`. "
                        "Bạn vui lòng bổ sung các dòng này hoặc dùng File Mẫu Excel bên trái."
                    )
                else:
                    notes = []
                    if map_rep["was_transposed"]:
                        notes.append("tự động xoay bảng dọc B01-DN sang chuẩn năm")
                    if map_rep["unit_scaled_from_vnd"]:
                        notes.append("tự quy đổi đơn vị VND sang Tỷ VND")
                    if map_rep["auto_estimated"]:
                        notes.append(f"tự điền an toàn {len(map_rep['auto_estimated'])} chỉ tiêu phụ bị thiếu")
                    st.info(
                        f"Đã tiếp nhận `{uploaded.name}` ({map_rep['mapped_count']} chỉ tiêu khớp tự động"
                        + (f"; {', '.join(notes)}" if notes else "")
                        + ")."
                    )
                    if map_rep["auto_estimated"]:
                        with st.expander("Xem các chỉ tiêu phụ được hệ thống điền mặc định (để đảm bảo ổn định)"):
                            st.write(" • ".join(map_rep["auto_estimated"]))
                    df_to_score = df_norm
            except Exception as exc:
                st.error(f"Không thể đọc file tải lên: {exc}")
        elif run_sample_btn:
            df_to_score = pd.DataFrame(SAMPLE_WORKED_EXAMPLES)

        if df_to_score is not None:
            df_res, checks = run_live_scoring_pipeline(df_to_score, df_all, df_bench, artifacts)
            _display_live_scoring_result(df_res, checks)

    with tab_whatif:
        with st.container(border=True):
            st.markdown("Chọn 1 doanh nghiệp mẫu rồi **sửa trực tiếp số liệu năm 2025** (VD: đổi Dòng tiền KD sang âm hoặc tăng Phải thu KH) để xem điểm rủi ro thay đổi ngay:")
            w1, w2 = st.columns([1.4, 1.0])
            preset_choice = w1.selectbox(
                "Bộ số liệu khởi đầu (2 năm 2024–2025)",
                [
                    "CTCP Mẫu Thổi Số (Bất động sản — Cảnh báo Cao)",
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

            cur_sec = str(base_2yr["icb_sector_vi"].iloc[-1])
            sec_override = w2.selectbox("Ngành đối sánh", all_sectors, index=all_sectors.index(cur_sec) if cur_sec in all_sectors else 0)
            base_2yr["icb_sector_vi"] = sec_override

            edited_df = st.data_editor(
                base_2yr.reset_index(drop=True),
                width="stretch",
                num_rows="fixed",
                disabled=["ticker", "year", "icb_sector_vi"],
                key=f"whatif_editor_{preset_choice}",
            )
            if st.button("Chấm điểm ngay cho kịch bản vừa chỉnh", icon=":material/play_arrow:", type="primary", width="stretch"):
                df_res, checks = run_live_scoring_pipeline(edited_df, df_all, df_bench, artifacts)
                _display_live_scoring_result(df_res, checks)

    _render_footer_with_about()


# ===========================================================================
# PHÂN HỆ 4: TRỢ LÝ PHÁP LÝ & SOI PDF (BỐ CỤC CỘT DỌC BÊN TRÁI + KHÔNG GIAN GEMINI BÊN PHẢI)
# ===========================================================================
def render_module_4_hybrid_rag() -> None:
    """
    Thiết kế phá cách theo bố cục Gemini:
    - Cột dọc bên trái (left_rail): Gồm Banner 'Trợ lý Pháp lý Kế toán & Soi File PDF BCTC' xếp dọc cùng 3 đầu mục 1, 2, 3.
      Khi rê chuột hiện màu mượt mà, khi click vào đầu mục nào sẽ hiển thị nội dung phần đó ở khung lớn bên phải.
    - Khung chính bên phải (right_stage): Rộng rãi, thoáng mát, hiển thị nội dung của đầu mục đang chọn.
    """
    m4_sections = [
        ("1. Trò chuyện Trợ lý Pháp lý & Đính kèm PDF", ":material/forum:"),
        ("2. Danh mục 5 Văn bản Pháp quy Bộ Tài chính", ":material/gavel:"),
        ("3. Tra cứu Bảng Thuyết minh B09-DN (38 DN)", ":material/table_chart:"),
    ]
    active_sec = int(st.session_state.get("m4_active_section", 0))

    left_rail, right_stage = st.columns([1.05, 2.85], gap="medium")

    with left_rail:
        with st.container(key="legal_portal_hero"):
            st.markdown(
                """
                <div class="fa-legal-rail-title">Trợ lý Pháp lý Kế toán &amp; <span class="fa-dual-gold">Soi File PDF BCTC</span></div>
                <div class="fa-legal-rail-sub">Hỏi đáp tự nhiên về Luật VAS, Thông tư 99/2025, Thông tư 48/2019, VSA 240 — luôn tách rõ nội dung trả lời và trích dẫn kèm liên kết Cổng Chính phủ</div>
                """,
                unsafe_allow_html=True,
            )

        for idx_s, (sec_label, sec_icon) in enumerate(m4_sections):
            is_curr = active_sec == idx_s
            if st.button(
                sec_label,
                icon=sec_icon,
                key=f"m4_nav_{idx_s}",
                type="primary" if is_curr else "secondary",
                width="stretch",
            ):
                st.session_state["m4_active_section"] = idx_s
                st.rerun()

        with st.container(border=True):
            pdf_diag, _, _ = _get_active_chat_pdf()
            if pdf_diag is not None:
                st.markdown(
                    f"<div style='font-size:15px;color:#064E3B;font-weight:700;'>Đang đính kèm PDF:</div>"
                    f"<div style='font-size:14.8px;color:#132A23;margin-top:3px;'>{escape(pdf_diag['file_name'])} ({pdf_diag['n_pages']} trang)</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='font-size:14.8px;color:#4B635B;line-height:1.5;'>"
                    "<strong>Mẹo nhanh:</strong> Chọn mục <strong>1</strong> để chat trực tiếp &amp; tải PDF, mục <strong>2</strong> để mở link văn bản gốc Bộ Tài chính, mục <strong>3</strong> để xem số liệu B09-DN."
                    "</div>",
                    unsafe_allow_html=True,
                )

    with right_stage:
        if active_sec == 0:
            _render_chat_workspace(prefix="m4_main", feed_height=560)
        elif active_sec == 1:
            render_legal_registry_table()
        else:
            with st.container(border=True):
                st.markdown(
                    '<div class="fa-section-title" style="margin-top:0;">Tra cứu Bảng Thuyết minh <span class="fa-sec-accent">B09-DN (38 Doanh nghiệp Trọng điểm)</span></div>',
                    unsafe_allow_html=True,
                )
                b09_tickers = sorted(df_b09["ticker"].dropna().unique().tolist())
                bc1, bc2 = st.columns([2.0, 1.0])
                b_tkr = bc1.selectbox("Chọn doanh nghiệp có Thuyết minh B09-DN chi tiết (38 DN)", b09_tickers, index=b09_tickers.index("TDH") if "TDH" in b09_tickers else 0)
                b_yrs = sorted(df_b09[df_b09["ticker"] == b_tkr]["year"].dropna().unique().tolist(), reverse=True)
                b_yr = bc2.selectbox("Năm thuyết minh", b_yrs, index=0)
                sub_b = df_b09[(df_b09["ticker"] == b_tkr) & (df_b09["year"] == b_yr)]
                if len(sub_b) > 0:
                    r_b09 = sub_b.iloc[0]
                    b09_rows = []
                    for k, meta in schema_b09.items():
                        v = r_b09.get(k, np.nan)
                        if pd.notna(v) and abs(float(v)) > 0.01:
                            b09_rows.append({"Khoản mục Thuyết minh B09-DN": meta.get("title_vi", k), "Giá trị (Tỷ VND)": round(float(v), 2)})
                    st.dataframe(pd.DataFrame(b09_rows), width="stretch", height=480, hide_index=True)

    _render_footer_with_about()


# ---------------------------------------------------------------------------
# 6. ĐIỀU PHỐI 4 PHÂN HỆ, BIỂU TƯỢNG CHAT NỔI & HỘP THOẠI GIỚI THIỆU
# ---------------------------------------------------------------------------
render_top_command_bar()

active_mod = st.session_state["active_module"]
if active_mod == MODULES[0]:
    render_module_1_market_radar()
elif active_mod == MODULES[1]:
    render_module_2_company_dossier()
elif active_mod == MODULES[2]:
    render_module_3_live_scoring()
else:
    render_module_4_hybrid_rag()

# Biểu tượng Chat nổi góc phải dưới hiện trên Trang 1, 2, 3 (ẩn trên Trang 4 vì Trang 4 đã là khung chat lớn!)
if active_mod != MODULES[3]:
    if st.button(
        "Hỏi Trợ lý AI",
        icon=":material/forum:",
        key="fab_chat_launcher",
        help="Mở nhanh hộp thoại hỏi đáp Luật VAS, số liệu 643 DN và soi file PDF",
    ):
        st.session_state["chat_drawer_open"] = True
        st.rerun()

if st.session_state.get("chat_drawer_open", False) and active_mod != MODULES[3]:
    render_chat_drawer_dialog()

if st.session_state.get("about_modal_open", False):
    render_about_methodology_dialog()
