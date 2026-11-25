"""
BỘ ĐIỀU PHỐI HỘI THOẠI PHÁP CHỨNG THÔNG MINH (CONVERSATIONAL FORENSIC ASSISTANT)
================================================================================
Giải quyết triệt để vấn đề hỏi đáp tự nhiên tiếng Việt trên Trợ lý AI FinAudit:
  1. Hiểu câu chào hỏi, hỏi hướng dẫn sử dụng, hỏi khái niệm tự nhiên ("nói cho tôi về luật VAS",
     "TT 99 có gì mới?", "VSA 240 là gì?", "Beneish/Altman/SHAP là gì?").
  2. Trả lời trực tiếp từ dữ liệu thật 643 DN HOSE/HNX + 38 B09-DN ("TDH 2025 thế nào?",
     "So sánh FPT và TDH", "Top 5 công ty cảnh báo đỏ", "Ngành nào rủi ro nhất?").
  3. Chuẩn hóa câu hỏi khẩu ngữ tiếng Việt (loại bỏ từ đệm "nói cho tôi về...", mở rộng viết tắt
     VAS/VSA/TT99/TT48/BCTC/HTK) trước khi truy vấn Hybrid RRF để KHÔNG từ chối nhầm câu hỏi chuyên ngành.
  4. Bảo toàn 100% Cổng Chống Ảo giác (Anti-Hallucination) với các câu hỏi thực sự ngoài phạm vi
     (thời tiết, thể thao, nấu ăn, chính trị...) kèm lời từ chối lịch sự và gợi ý cách hỏi.
  5. Chạy 100% cục bộ (Zero-API, < 5 ms), không bịa số liệu hay điều luật ngoài nguồn.
"""

from __future__ import annotations

from html import escape
import re
import unicodedata
from typing import Any

import pandas as pd

from ui_components import format_rag_markdown_to_html, trim_excerpt_clean

# ---------------------------------------------------------------------------
# 1. CHUẨN HÓA TIẾNG VIỆT & TỪ ĐIỂN NHẬN DIỆN MIỀN NGHIỆP VỤ
# ---------------------------------------------------------------------------
def _strip_accents(text: str) -> str:
    if not text:
        return ""
    s = text.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", s)


def _norm(text: str) -> str:
    s = _strip_accents(text).lower()
    s = re.sub(r"[^a-z0-9/%\.\-\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# Các cụm từ khẩu ngữ mở đầu/kết thúc làm loãng vector TF-IDF khi người dùng hỏi tự nhiên
CONVERSATIONAL_WRAPPERS = [
    r"\bnoi cho toi ve\b",
    r"\bnoi cho minh ve\b",
    r"\bnoi ve\b",
    r"\bke cho toi ve\b",
    r"\bke ve\b",
    r"\bgiai thich cho toi\b",
    r"\bgiai thich giup toi\b",
    r"\bgiai thich ve\b",
    r"\bgiai thich\b",
    r"\bcho toi biet ve\b",
    r"\bcho toi biet\b",
    r"\bcho minh biet\b",
    r"\bcho toi hoi ve\b",
    r"\bcho toi hoi\b",
    r"\bcho minh hoi\b",
    r"\bgiup toi hieu ve\b",
    r"\bgiup toi hieu\b",
    r"\bgiup toi\b",
    r"\bgiup minh\b",
    r"\btom tat ve\b",
    r"\btom tat\b",
    r"\btrinh bay ve\b",
    r"\btrinh bay\b",
    r"\bban hay\b",
    r"\bhay noi\b",
    r"\bla gi\b",
    r"\bla sao\b",
    r"\bnhu the nao\b",
    r"\bthe nao\b",
    r"\bra sao\b",
    r"\bco gi moi\b",
    r"\bgom nhung gi\b",
    r"\bduoc khong\b",
    r"\bkhong vay\b",
    r"\btoi muon biet\b",
    r"\bminh muon biet\b",
    r"\btoi muon hoi\b",
    r"\bminh muon hoi\b",
    r"\bquy dinh gi\b",
    r"\bnoi dung gi\b",
    r"\bban oi\b",
    r"\bnhe\b",
    r"\bnha\b",
    r"\bnhi\b",
    r"\bvay\b",
    r"\bdi\b",
]

# Từ khóa neo miền Kế toán / Kiểm toán / BCTC / FinAudit AI (có 1 cụm này = chắc chắn trong phạm vi!)
DOMAIN_ANCHOR_PHRASES = [
    "vas", "vsa", "tt 99", "tt99", "99/2025", "tt 200", "tt200", "200/2014",
    "tt 48", "tt48", "48/2019", "tt 24", "tt24", "24/2022", "214/2012",
    "thong tu", "chuan muc", "ke toan", "kiem toan", "bctc", "bao cao tai chinh",
    "bao cao tinh hinh tai chinh", "bang can doi ke toan", "ket qua kinh doanh",
    "luu chuyen tien", "thuyet minh", "b01", "b02", "b03", "b09",
    "du phong", "doanh thu", "phai thu", "hang ton kho", "ton kho", "khau hao",
    "dong tien", "cfo", "loi nhuan", "lnst", "gia von", "chi phi", "tai san",
    "no phai tra", "no xau", "no qua han", "kho doi", "tuoi no", "trai phieu",
    "vay ngan hang", "von chu so huu", "von hoa", "xay dung co ban", "xdcb",
    "ben lien quan", "gian lan", "hoai nghi", "sai sot trong yeu", "khong che kiem soat",
    "hoat dong lien tuc", "beneish", "m-score", "m score", "altman", "z-score", "z score",
    "shap", "isoforest", "isolation forest", "dsri", "gmi", "aqi", "sgi", "depi",
    "sgai", "lvgi", "tata", "srr", "phan ky dong tien", "diem rui ro", "canh bao do",
    "phap chung", "finaudit", "finforensics", "esg", "quan tri", "minh bach",
    "tk 131", "tk 138", "tk 229", "tk 241", "tk 331", "tk 141", "tk 521",
    "thue tndn", "nrv", "ifrs", "ias 1", "co phieu", "chung khoan", "hose", "hnx",
    "nganh icb", "bluechip", "kiem dinh", "backtest", "auc", "rag", "ocr", "pdf",
]

# Các mã CK trùng với từ phổ thông hoặc tên chuẩn mực (chỉ nhận là mã CK khi có ngữ cảnh "mã/công ty/cp")
AMBIGUOUS_TICKERS = {
    "API", "CAN", "DAT", "FIT", "HAT", "NET", "NHA", "ONE", "PAN", "SAM", "SAV", "VSA",
    "GMI", "SGI", "AQI", "ESG", "PDF", "RAG", "VAS", "CFO", "SRR", "BCTC", "SHAP",
}

COMPANY_NAME_ALIASES: dict[str, str] = {
    "vinamilk": "VNM",
    "sua viet nam": "VNM",
    "novaland": "NVL",
    "nova": "NVL",
    "thu duc house": "TDH",
    "nha thu duc": "TDH",
    "quoc cuong gia lai": "QCG",
    "hoa phat": "HPG",
    "the gioi di dong": "MWG",
    "vingroup": "VIC",
    "vinhomes": "VHM",
    "masan": "MSN",
    "sabeco": "SAB",
    "vietnam airlines": "HVN",
    "hang khong viet nam": "HVN",
    "hoa chat duc giang": "DGC",
    "duc giang": "DGC",
    "hoang anh gia lai": "HAG",
    "go truong thanh": "TTF",
    "fpt": "FPT",
    "petrolimex": "PLX",
    "vinh hoan": "VHC",
    "binh minh": "BMP",
    "duoc hau giang": "DHG",
}


def _has_domain_anchor(q_norm: str) -> bool:
    for kw in DOMAIN_ANCHOR_PHRASES:
        if re.search(rf"(?:^|\s){re.escape(kw)}(?:$|\s)", q_norm):
            return True
    return False


def _expand_legal_query(query: str) -> str:
    """Làm sạch từ đệm khẩu ngữ & mở rộng từ viết tắt pháp lý để Hybrid RAG truy xuất chính xác."""
    q_norm = _norm(query)
    cleaned = q_norm
    for pat in CONVERSATIONAL_WRAPPERS:
        cleaned = re.sub(pat, " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    expansions: list[str] = []
    if re.search(r"\b(tt\s*99|99/2025|thong tu 99)\b", q_norm):
        expansions.append("Thông tư 99/2025/TT-BTC Điều 17 Điều 31 B01-DN Báo cáo tình hình tài chính hiệu lực 01/01/2026 thay thế Thông tư 200")
    if re.search(r"\b(tt\s*200|200/2014|thong tu 200)\b", q_norm):
        expansions.append("Thông tư 200/2014/TT-BTC chế độ kế toán doanh nghiệp Điều 18 Điều 45")
    if re.search(r"\b(tt\s*48|48/2019|thong tu 48|no xau|no qua han|du phong kho doi)\b", q_norm):
        expansions.append("Thông tư 48/2019/TT-BTC Điều 6 dự phòng phải thu khó đòi tuổi nợ quá hạn 30% 50% 70% 100% thuế TNDN")
    if re.search(r"\b(tt\s*24|24/2022|thong tu 24)\b", q_norm):
        expansions.append("Thông tư 24/2022/TT-BTC sửa đổi Điều 5 dự phòng đầu tư chứng khoán")
    if re.search(r"\bvas\b", q_norm) and not re.search(r"\bvas\s*(14|26)\b", q_norm):
        expansions.append("Chuẩn mực Kế toán Việt Nam VAS 14 doanh thu bán hàng VAS 26 bên liên quan Thông tư 99/2025 Thông tư 200/2014")
    if re.search(r"\b(vsa\s*240|vsa240|chuan muc kiem toan|gian lan)\b", q_norm):
        expansions.append("VSA 240 Thông tư 214/2012 gian lận báo cáo tài chính Đoạn 12 Đoạn 26 Đoạn 32 thái độ hoài nghi nghề nghiệp")
    if re.search(r"\bhtk\b", q_norm):
        expansions.append("hàng tồn kho dự phòng giảm giá NRV")
    if re.search(r"\btscd\b", q_norm):
        expansions.append("tài sản cố định khấu hao DEPI")
    if re.search(r"\bbctc\b", q_norm):
        expansions.append("báo cáo tài chính B01-DN B02-DN B03-DN B09-DN")

    base_q = cleaned if len(cleaned) >= 3 else query.strip()
    if expansions:
        return f"{base_q} {' '.join(expansions)}"
    return base_q


# ---------------------------------------------------------------------------
# 2. BỘ NHẬN DIỆN MÃ CỔ PHIẾU & CÂU HỎI DỮ LIỆU THẬT (643 DN + B09-DN)
# ---------------------------------------------------------------------------
def _extract_tickers(query: str, valid_tickers: set[str]) -> list[str]:
    found: list[str] = []
    q_norm = _norm(query)

    # 1. Nhận diện tên công ty phổ biến (Vinamilk, Novaland, Thủ Đức House...)
    for alias, tkr in COMPANY_NAME_ALIASES.items():
        if tkr in valid_tickers and re.search(rf"(?:^|\s){re.escape(alias)}(?:$|\s)", q_norm):
            if tkr not in found:
                found.append(tkr)

    # 2. Nhận diện mã CK viết rõ sau từ khóa ("mã VSA", "công ty NHA", "cp TDH")
    for m in re.finditer(r"\b(?:ma|co phieu|cp|cong ty|ctcp|ticker|dn)\s+([a-z0-9]{3})\b", q_norm):
        cand = m.group(1).upper()
        if cand in valid_tickers and not (cand == "VSA" and "240" in q_norm):
            if cand not in found:
                found.append(cand)

    # 3. Nhận diện mã 3 ký tự ASCII không dấu độc lập (loại trừ từ trùng nghĩa & tiếng Việt có dấu)
    for raw_tok in re.findall(r"\b[A-Za-z0-9]{3}\b", query):
        cand = raw_tok.upper()
        if cand in valid_tickers and cand not in AMBIGUOUS_TICKERS:
            # Nếu viết thường, chỉ nhận nếu không phải từ tiếng Việt phổ thông
            if raw_tok.isupper() or cand in {"TDH", "FPT", "VNM", "NVL", "QCG", "DRH", "HPG", "MWG", "VIC", "VHM", "HAG", "TTF", "LDG", "HVN", "DGC", "REE", "PNJ", "GAS", "SAB", "BMP", "DHG", "VHC", "CTR"}:
                if cand not in found:
                    found.append(cand)
    return found[:3]


def _extract_year(query: str, default_year: int = 2025) -> int:
    for m in re.finditer(r"\b(2019|2020|2021|2022|2023|2024|2025)\b", query):
        return int(m.group(1))
    return default_year


def _render_single_company_answer(
    ticker: str,
    year_req: int,
    df_all: pd.DataFrame,
    df_b09: pd.DataFrame,
) -> tuple[str, str]:
    sub = df_all[(df_all["ticker"] == ticker) & (df_all["composite_risk_score"].notna())].sort_values("year")
    if sub.empty:
        return (
            f"Không tìm thấy dữ liệu chấm điểm cho mã {ticker}",
            f"<p>Mã <strong>{escape(ticker)}</strong> hiện chưa có năm tài chính hợp lệ trong tập 643 DN phi tài chính.</p>",
        )
    sub_yr = sub[sub["year"] == year_req]
    row = sub_yr.iloc[0] if not sub_yr.empty else sub.iloc[-1]
    yr_used = int(row["year"])
    score = float(row["composite_risk_score"])
    tier = str(row["risk_tier"])
    col = "#BE123C" if score >= 65 else ("#B45309" if score >= 40 else "#059669")
    bg = "#FFF1F2" if score >= 65 else ("#FFFBEB" if score >= 40 else "#ECFDF5")

    div_txt = (
        "<strong style='color:#BE123C;'>Có phân kỳ dòng tiền (Báo lãi sau thuế nhưng CFO âm)</strong>"
        if bool(row.get("cash_flow_divergence_flag", False))
        else "<strong style='color:#059669;'>Dòng tiền đồng pha với lợi nhuận</strong>"
    )

    b09_sub = df_b09[(df_b09["ticker"] == ticker) & (df_b09["year"] == yr_used)]
    b09_block = ""
    if len(b09_sub) > 0:
        b0 = b09_sub.iloc[0]
        b09_block = (
            f"<div style='margin-top:10px;padding:10px 14px;background:#F0FDFA;border:1px solid #99F6E4;border-left:3.5px solid #0F766E;border-radius:4px;font-size:15.2px;color:#064E3B;'>"
            f"<strong>Thuyết minh B09-DN thật ({ticker} {yr_used}):</strong> "
            f"Tiền &amp; TĐT: <strong>{float(b0.get('noc1', 0) or 0):,.2f} tỷ</strong> • "
            f"Hàng tồn kho gộp: <strong>{float(b0.get('noc15', 0) or 0):,.2f} tỷ</strong> • "
            f"Doanh thu gộp: <strong>{float(b0.get('noc101', 0) or 0):,.2f} tỷ</strong>."
            f"</div>"
        )

    html = (
        f"<div style='padding:14px 18px;background:{bg};border:1px solid {col}44;border-left:4px solid {col};border-radius:5px;margin-bottom:10px;'>"
        f"  <div style='font-weight:800;font-size:17.5px;color:#132A23;'>{escape(ticker)} — {escape(str(row['company_name']))} ({yr_used})</div>"
        f"  <div style='margin-top:5px;font-size:16px;color:#132A23;'>"
        f"    Điểm Rủi ro Pháp chứng: <strong style='color:{col};font-family:JetBrains Mono,monospace;font-size:18px;'>{score:.1f} / 100</strong> "
        f"    (<strong style='color:{col};'>{escape(tier)}</strong>) • Ngành: <strong>{escape(str(row['icb_sector_vi']))}</strong> ({escape(str(row['exchange']))})"
        f"  </div>"
        f"</div>"
        f"<div style='font-size:16.2px;line-height:1.72;color:#132A23;'>"
        f"  • <strong>4 Trụ cột:</strong> Beneish <code>{float(row['score_beneish']):.1f}/100</code> (M={float(row['beneish_m_score']):.2f}) | "
        f"Altman Z'' <code>{float(row['score_altman']):.1f}/100</code> (Z''={float(row['altman_z_double_prime']):.2f}) | "
        f"Dòng tiền &amp; SRR <code>{float(row['score_cash_quality']):.1f}/100</code> | AI IsoForest <code>{float(row['score_isoforest']):.1f}/100</code><br/>"
        f"  • <strong>BCTC cốt lõi:</strong> Tổng TS <strong>{float(row['total_assets']):,.1f} tỷ</strong> • "
        f"Doanh thu <strong>{float(row['net_revenue']):,.1f} tỷ</strong> • "
        f"LNST <strong>{float(row['net_income']):,.1f} tỷ</strong> • "
        f"CFO <strong>{float(row['cfo']):,.1f} tỷ</strong><br/>"
        f"  • <strong>Chất lượng dòng tiền:</strong> {div_txt}<br/>"
        f"  • <strong>Giải trình AI (SHAP):</strong> {escape(str(row['top_risk_drivers_vi']))}"
        f"</div>{b09_block}"
        f"<div style='margin-top:10px;font-size:14.6px;color:#4B635B;'>"
        f"Gợi ý: Bạn có thể gõ <code>{ticker}</code> vào Khung Tìm kiếm đầu trang để mở trọn vẹn <strong>Hồ sơ 360° &amp; Thác nước SHAP</strong>."
        f"</div>"
    )
    return f"Hồ sơ Nhanh từ Dữ liệu Thật — {ticker} ({yr_used})", html


def _render_compare_companies_answer(
    tickers: list[str],
    year_req: int,
    df_all: pd.DataFrame,
) -> tuple[str, str]:
    rows_html = []
    for tkr in tickers[:3]:
        sub = df_all[(df_all["ticker"] == tkr) & (df_all["composite_risk_score"].notna())].sort_values("year")
        if sub.empty:
            continue
        sub_y = sub[sub["year"] == year_req]
        r = sub_y.iloc[0] if not sub_y.empty else sub.iloc[-1]
        sc = float(r["composite_risk_score"])
        c = "#BE123C" if sc >= 65 else ("#B45309" if sc >= 40 else "#059669")
        rows_html.append(
            f"<tr>"
            f"<td style='padding:9px 11px;border-bottom:1px solid #D1DDD8;font-weight:800;'>{escape(tkr)} ({int(r['year'])})</td>"
            f"<td style='padding:9px 11px;border-bottom:1px solid #D1DDD8;font-weight:800;color:{c};font-family:JetBrains Mono,monospace;'>{sc:.1f} / 100</td>"
            f"<td style='padding:9px 11px;border-bottom:1px solid #D1DDD8;'>{float(r['beneish_m_score']):.2f}</td>"
            f"<td style='padding:9px 11px;border-bottom:1px solid #D1DDD8;'>{float(r['altman_z_double_prime']):.2f}</td>"
            f"<td style='padding:9px 11px;border-bottom:1px solid #D1DDD8;'>{float(r['net_income']):,.1f} tỷ</td>"
            f"<td style='padding:9px 11px;border-bottom:1px solid #D1DDD8;'>{float(r['cfo']):,.1f} tỷ</td>"
            f"</tr>"
        )
    table_html = (
        f"<table style='width:100%;border-collapse:collapse;font-size:15.5px;margin-top:8px;'>"
        f"<thead><tr style='background:#064E3B;color:#FFFFFF;'>"
        f"<th style='padding:9px 11px;text-align:left;'>Mã CK</th>"
        f"<th style='padding:9px 11px;text-align:left;'>Chỉ số Rủi ro</th>"
        f"<th style='padding:9px 11px;text-align:left;'>Beneish M</th>"
        f"<th style='padding:9px 11px;text-align:left;'>Altman Z''</th>"
        f"<th style='padding:9px 11px;text-align:left;'>LNST</th>"
        f"<th style='padding:9px 11px;text-align:left;'>CFO</th>"
        f"</tr></thead><tbody>{''.join(rows_html)}</tbody></table>"
        f"<div style='margin-top:10px;font-size:14.8px;color:#4B635B;'>"
        f"Thang điểm: <strong>&lt; 40/100</strong> Hạng A (An toàn) • <strong>40–64.9/100</strong> Hạng B (Theo dõi) • <strong>&ge; 65/100</strong> Hạng C (Cảnh báo Cao)."
        f"</div>"
    )
    return f"So sánh Pháp chứng Trực tiếp ({' vs. '.join(tickers[:3])})", table_html


def _render_market_summary_answer(q_norm: str, year_req: int, df_all: pd.DataFrame) -> tuple[str, str]:
    df_y = df_all[(df_all["year"] == year_req) & (df_all["composite_risk_score"].notna())].copy()
    if df_y.empty:
        year_req = int(df_all.dropna(subset=["composite_risk_score"])["year"].max())
        df_y = df_all[(df_all["year"] == year_req) & (df_all["composite_risk_score"].notna())].copy()

    n_all = len(df_y)
    n_red = int((df_y["composite_risk_score"] >= 65.0).sum())
    n_div = int(df_y["cash_flow_divergence_flag"].fillna(False).sum())
    med = float(df_y["composite_risk_score"].median())

    if "nganh" in q_norm:
        agg = (
            df_y.groupby("icb_sector_vi", as_index=False)
            .agg(n=("ticker", "count"), med=("composite_risk_score", "median"), red=("composite_risk_score", lambda s: int((s >= 65).sum())))
            .sort_values("med", ascending=False)
            .head(5)
        )
        items = "".join(
            f"<li><strong>{escape(r['icb_sector_vi'])}:</strong> Trung vị <code>{r['med']:.1f}/100</code> ({r['red']}/{r['n']} DN Cảnh báo Cao)</li>"
            for _, r in agg.iterrows()
        )
        html = (
            f"<div style='font-size:16.2px;line-height:1.72;color:#132A23;'>"
            f"<strong>Top 5 Ngành ICB có điểm rủi ro trung vị cao nhất năm {year_req}</strong> (trong 15 ngành phi tài chính):<ol style='margin:8px 0 4px 20px;'>{items}</ol>"
            f"</div>"
        )
        return f"Xếp hạng Rủi ro Ngành ICB ({year_req})", html

    top5 = df_y.sort_values("composite_risk_score", ascending=False).head(5)
    items = "".join(
        f"<li><strong>{escape(r['ticker'])}</strong> ({escape(str(r['icb_sector_vi']))}): "
        f"<strong style='color:#BE123C;'>{float(r['composite_risk_score']):.1f}/100</strong> — "
        f"LNST {float(r['net_income']):,.1f} tỷ | CFO {float(r['cfo']):,.1f} tỷ</li>"
        for _, r in top5.iterrows()
    )
    html = (
        f"<div style='font-size:16.2px;line-height:1.72;color:#132A23;'>"
        f"Toàn thị trường HOSE/HNX năm <strong>{year_req}</strong> có <strong>{n_all} DN</strong> được chấm điểm: "
        f"<strong style='color:#BE123C;'>{n_red} DN Hạng C • Cảnh báo Cao ({n_red/max(n_all,1)*100:.1f}%)</strong>, "
        f"<strong>{n_div} DN Phân kỳ dòng tiền ({n_div/max(n_all,1)*100:.1f}%)</strong>, điểm trung vị <code>{med:.1f}/100</code>.<br/>"
        f"<strong>Top 5 doanh nghiệp có chỉ báo rủi ro cao nhất năm {year_req}:</strong>"
        f"<ol style='margin:8px 0 4px 20px;'>{items}</ol>"
        f"<div style='font-size:14.2px;color:#4B635B;'>Lưu ý theo VSA 240: Đây là chỉ báo rủi ro khoanh vùng kiểm toán, không phải kết luận gian lận.</div>"
        f"</div>"
    )
    return f"Thống kê Thị trường & Top Cảnh báo Cao ({year_req})", html


# ---------------------------------------------------------------------------
# 3. TÓM TẮT KHÁI NIỆM CHUYÊN NGÀNH GẮN CHẶT NGUỒN (ZERO HALLUCINATION)
# ---------------------------------------------------------------------------
def _match_concept_overview(q_norm: str) -> tuple[str, str, str] | None:
    """
    Trả về (tiêu đề, đoạn giải thích ngắn chuẩn xác, từ khóa bổ sung truy xuất RAG) cho các câu hỏi
    khái niệm phổ thông để câu trả lời vừa tự nhiên, vừa kèm điều luật gốc trích dẫn ở bên dưới.
    """
    # 1. Hỏi chung về Luật VAS / Chuẩn mực Kế toán Việt Nam (VD: "nói cho tôi về luật VAS", "VAS là gì")
    if re.search(r"\b(luat vas|chuan muc vas|he thong vas|chuan muc ke toan viet nam)\b", q_norm) or (
        re.search(r"\bvas\b", q_norm) and not re.search(r"\bvas\s*(14|26)\b", q_norm) and len(q_norm.split()) <= 9
    ):
        return (
            "Tổng quan về Chuẩn mực Kế toán Việt Nam (VAS) & Chế độ Kế toán",
            (
                "<strong>VAS (Vietnamese Accounting Standards)</strong> là <strong>Hệ thống Chuẩn mực Kế toán Việt Nam</strong> do Bộ Tài chính ban hành "
                "(gồm <strong>26 chuẩn mực</strong> ban hành qua 5 đợt theo Luật Kế toán), quy định các nguyên tắc và phương pháp lập, trình bày Báo cáo tài chính trung thực, hợp lý tại Việt Nam.<br/>"
                "• <strong>2 chuẩn mực trọng tâm soi rủi ro pháp chứng trong FinAudit AI:</strong> "
                "<strong>VAS 14</strong> (<em>Doanh thu và thu nhập khác</em> — QĐ 149/2001/QĐ-BTC, 5 điều kiện ghi nhận doanh thu) và "
                "<strong>VAS 26</strong> (<em>Thông tin về các bên liên quan</em> — QĐ 234/2003/QĐ-BTC, chống che giấu công nợ/giao dịch nội bộ).<br/>"
                "• <strong>Văn bản hướng dẫn Chế độ kế toán đi kèm VAS:</strong> "
                "<strong>Thông tư 200/2014/TT-BTC</strong> áp dụng cho niên độ lịch sử đến hết <code>31/12/2025</code>, và "
                "<strong>Thông tư 99/2025/TT-BTC</strong> thay thế toàn bộ từ <code>01/01/2026</code> (tiệm cận IFRS/IAS 1, đổi tên <code>B01-DN</code> thành <em>Báo cáo tình hình tài chính</em>)."
            ),
            "VAS 14 doanh thu bán hàng VAS 26 bên liên quan Thông tư 99/2025 Điều 17 Điều 31",
        )

    # 2. Hỏi chung về Thông tư 99/2025
    if re.search(r"\b(tt\s*99|tt99|99/2025|thong tu 99)\b", q_norm) and len(q_norm.split()) <= 16:
        return (
            "Tóm tắt nhanh Thông tư 99/2025/TT-BTC (Chế độ Kế toán Mới)",
            (
                "<strong>Thông tư 99/2025/TT-BTC</strong> (ban hành ngày <code>27/10/2025</code>, có hiệu lực từ <code>01/01/2026</code>) thay thế toàn bộ <strong>Thông tư 200/2014/TT-BTC</strong>, TT 75/2015, TT 53/2016 và TT 195/2012.<br/>"
                "• <strong>Điểm đổi mới nổi bật:</strong> Đổi tên Mẫu <code>B01-DN</code> từ <em>Bảng cân đối kế toán</em> thành <strong>Báo cáo tình hình tài chính</strong> (tiệm cận IFRS / IAS 1), đồng thời giữ tính kế thừa hệ thống mã số chỉ tiêu để liên thông chuỗi dữ liệu lịch sử 2018–2025."
            ),
            "Thông tư 99/2025 Điều 17 Điều 18 Điều 31 đổi tên B01-DN hiệu lực thay thế Thông tư 200",
        )

    # 3. Hỏi chung về VSA 240
    if re.search(r"\b(vsa\s*240|vsa240|chuan muc kiem toan 240)\b", q_norm) and len(q_norm.split()) <= 16:
        return (
            "Tóm tắt nhanh Chuẩn mực Kiểm toán Việt Nam VSA 240",
            (
                "<strong>VSA 240</strong> (ban hành kèm <strong>Thông tư 214/2012/TT-BTC</strong>) quy định trách nhiệm của kiểm toán viên liên quan đến gian lận khi kiểm toán BCTC.<br/>"
                "• <strong>3 nguyên tắc cốt lõi ứng dụng trong FinAudit AI:</strong> "
                "(1) Duy trì <em>thái độ hoài nghi nghề nghiệp</em> (Đoạn 12–14); "
                "(2) <em>Giả định bắt buộc về rủi ro gian lận trong ghi nhận doanh thu</em> (Đoạn 26); "
                "(3) <em>3 thủ tục kiểm toán bắt buộc đối phó khống chế kiểm soát</em> (Đoạn 32). Hệ thống chỉ cung cấp <strong>chỉ báo rủi ro (Red Flags)</strong>, tuyệt đối không kết luận quy chụp gian lận."
            ),
            "VSA 240 Đoạn 04 Đoạn 12 Đoạn 26 Đoạn 32 hoài nghi nghề nghiệp gian lận doanh thu",
        )

    # 4. Hỏi chung về Thông tư 48/2019 & dự phòng
    if re.search(r"\b(tt\s*48|tt48|48/2019|thong tu 48)\b", q_norm) and len(q_norm.split()) <= 16:
        return (
            "Tóm tắt nhanh Thông tư 48/2019/TT-BTC & TT 24/2022/TT-BTC (Dự phòng)",
            (
                "<strong>Thông tư 48/2019/TT-BTC</strong> (sửa đổi bởi TT 24/2022/TT-BTC) hướng dẫn trích lập dự phòng làm cơ sở tính <strong>chi phí được trừ thuế TNDN</strong> (khác với mục đích trình bày BCTC theo TT 200/2014 & TT 99/2025).<br/>"
                "• <strong>Khung tỷ lệ trích dự phòng nợ phải thu quá hạn (Điều 6):</strong> "
                "6 tháng – dưới 1 năm: <code>30%</code> • 1 – dưới 2 năm: <code>50%</code> • 2 – dưới 3 năm: <code>70%</code> • từ 3 năm trở lên: <code>100%</code>."
            ),
            "Thông tư 48/2019 Điều 6 tỷ lệ trích lập dự phòng nợ quá hạn thuế TNDN",
        )

    # 5. Hỏi về các mô hình AI / Chỉ số định lượng & Thang điểm trong FinAudit AI
    if re.search(r"\b(beneish|m-score|m score|altman|z-score|z score|shap|isolation forest|isoforest|diem rui ro|thang diem|4 tru cot|srr)\b", q_norm):
        return (
            "Cơ chế Chấm điểm Pháp chứng 4 Trụ cột & Giải thích AI (FinAudit AI)",
            (
                "<strong>Điểm Rủi ro Pháp chứng Tổng hợp (0–100đ)</strong> của FinAudit AI kết hợp 4 trụ cột trên 643 DN HOSE/HNX (<code>AUC Backtest = 0.9299</code>, <code>0%</code> cảnh báo đỏ giả trên 12 Bluechip):<br/>"
                "• <strong>Trụ cột 1 — Beneish M-Score (30%):</strong> 8 chỉ số kế toán (<code>DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA</code>); ngưỡng cảnh báo <code>M &gt; -1.78</code>.<br/>"
                "• <strong>Trụ cột 2 — Altman Z''-Score EMS 2005 (25%):</strong> Đo sức khỏe tài chính thị trường mới nổi; <code>&lt; 4.35</code> vùng Nguy hiểm, <code>&gt; 5.85</code> vùng An toàn.<br/>"
                "• <strong>Trụ cột 3 — Dòng tiền CFO &amp; Tài sản mềm SRR (20%):</strong> Phát hiện báo lãi nhưng dòng tiền kinh doanh âm (<code>LN+ / CFO-</code>) và phình to phải thu khác/trả trước.<br/>"
                "• <strong>Trụ cột 4 — AI Isolation Forest (25%):</strong> Phát hiện dị biệt đa chiều trong từng ngành ICB, giải trình cộng tính từng điểm bằng <strong>SHAP Waterfall</strong> (<code>R² = 0.9964</code>, <code>MAE = 0.85đ</code>).<br/>"
                "• <strong>Thang phân hạng:</strong> <code>&lt; 40đ</code> Thấp (An toàn) • <code>40–64.9đ</code> Trung bình (Theo dõi) • <code>&ge; 65đ</code> Cao (Cảnh báo Đỏ)."
            ),
            "Playbook DSRI SRR TATA CFO Altman Beneish SHAP thủ tục kiểm toán",
        )

    # 6. Hỏi về ESG trụ cột G
    if re.search(r"\b(esg|tru cot g|minh bach quan tri)\b", q_norm):
        return (
            "Tác động Phát triển Bền vững — ESG Trụ cột G (Governance)",
            (
                "<strong>FinAudit AI — FinForensics</strong> tập trung giải quyết trực tiếp <strong>Trụ cột G (Quản trị &amp; Minh bạch tài chính)</strong> trong khung ESG:<br/>"
                "• Giảm bất đối xứng thông tin, cảnh báo sớm suy giảm chất lượng lợi nhuận để bảo vệ nhà đầu tư, ngân hàng và nhà cung cấp SME.<br/>"
                "• Liên thông chuẩn hóa dữ liệu từ <strong>TT 200/2014</strong> sang <strong>TT 99/2025/TT-BTC</strong>, hướng tới chuẩn mực báo cáo quốc tế IFRS."
            ),
            "VSA 240 Thông tư 99/2025 minh bạch báo cáo tài chính",
        )

    return None


def _is_greeting_or_help(q_norm: str) -> bool:
    greeting_patterns = [
        r"^(xin chao|chao|chao ban|hello|hi|hey|alo|chao buoi sang|chao buoi chieu|chao buoi toi)\b",
        r"\b(ban la ai|ban lam duoc gi|ban ho tro gi|chuc nang cua ban|huong dan su dung|cach dung|web nay lam gi|gioi thieu ve ban|ban biet gi)\b",
        r"^(cam on|thank|thanks|ok|oke|tot lam|hay qua)\b",
    ]
    return any(re.search(p, q_norm) for p in greeting_patterns)


# ---------------------------------------------------------------------------
# 3B. LIÊN KẾT CHÍNH THỨC CỔNG CHÍNH PHỦ & BỘ TÀI CHÍNH CHO TỪNG VĂN BẢN
# ---------------------------------------------------------------------------
OFFICIAL_GOV_PORTALS: list[tuple[str, str, str, str]] = [
    ("99/2025", "Cổng TTĐT Bộ Tài chính (TT 99/2025)", "https://mof.gov.vn/", "CSDL Quốc gia VBPL"),
    ("200/2014", "CSDL Quốc gia VBPL (TT 200/2014)", "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=200/2014/TT-BTC", "Cổng VBPL Chính phủ"),
    ("48/2019", "CSDL Quốc gia VBPL (TT 48/2019)", "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=48/2019/TT-BTC", "Cổng VBPL Chính phủ"),
    ("24/2022", "CSDL Quốc gia VBPL (TT 24/2022)", "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=24/2022/TT-BTC", "Cổng VBPL Chính phủ"),
    ("214/2012", "CSDL Quốc gia VBPL (VSA 240 — TT 214/2012)", "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=214/2012/TT-BTC", "Cổng VBPL Chính phủ"),
    ("vsa 240", "CSDL Quốc gia VBPL (VSA 240 — TT 214/2012)", "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=214/2012/TT-BTC", "Cổng VBPL Chính phủ"),
    ("vas 14", "CSDL Quốc gia VBPL (VAS 14 — QĐ 149/2001)", "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=149/2001/Q%C4%90-BTC", "Cổng TTĐT Bộ Tài chính"),
    ("vas 26", "CSDL Quốc gia VBPL (VAS 26 — QĐ 234/2003)", "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?Keyword=234/2003/Q%C4%90-BTC", "Cổng TTĐT Bộ Tài chính"),
]


def _gov_link_pill(citation_text: str) -> str:
    low = citation_text.lower()
    for kw, lbl, url, _ in OFFICIAL_GOV_PORTALS:
        if kw in low:
            return (
                f"<div style='margin-top:8px;display:flex;flex-wrap:wrap;gap:8px;'>"
                f"<a href='{url}' target='_blank' rel='noopener noreferrer' "
                f"style='font-size:14px;font-weight:700;color:#064E3B;background:#ECFDF5;border:1px solid #A7F3D0;"
                f"border-left:3px solid #064E3B;padding:5px 12px;border-radius:4px;text-decoration:none;"
                f"box-shadow:0 1px 3px rgba(6,78,59,0.08);'>"
                f"Tra cứu văn bản gốc tại {escape(lbl)} ↗</a>"
                f"<a href='https://vanban.chinhphu.vn/' target='_blank' rel='noopener noreferrer' "
                f"style='font-size:14px;font-weight:700;color:#9A3412;background:#FFF7ED;border:1px solid #FDBA74;"
                f"border-left:3px solid #C2410C;padding:5px 12px;border-radius:4px;text-decoration:none;"
                f"box-shadow:0 1px 3px rgba(194,65,12,0.08);'>"
                f"Cổng Văn bản Chính phủ (vanban.chinhphu.vn) ↗</a></div>"
            )
    return (
        "<div style='margin-top:8px;'>"
        "<a href='https://vbpl.vn/' target='_blank' rel='noopener noreferrer' "
        "style='display:inline-block;font-size:14px;font-weight:700;color:#064E3B;background:#ECFDF5;border:1px solid #A7F3D0;"
        "border-left:3px solid #064E3B;padding:5px 12px;border-radius:4px;text-decoration:none;"
        "box-shadow:0 1px 3px rgba(6,78,59,0.08);'>"
        "Cơ sở dữ liệu Quốc gia về Văn bản Pháp luật (vbpl.vn) ↗</a></div>"
    )


def _suggest_followups(q_norm: str, matched_tickers: list[str], want_pdf: bool, abstained: bool) -> list[str]:
    """Sinh 2–3 câu hỏi gợi ý tiếp nối đúng ngữ cảnh sau khi Trợ lý vừa trả lời."""
    if abstained:
        return [
            "Nói cho tôi về luật VAS",
            "Thông tư 99/2025 có gì mới?",
            "Top 5 công ty cảnh báo đỏ năm 2025",
        ]
    if want_pdf:
        return [
            "Chi tiết các khoản vay và trái phiếu trong file PDF",
            "Thuyết minh hàng tồn kho và dự phòng giảm giá",
            "Ý kiến kiểm toán hoặc vấn đề cần nhấn mạnh",
        ]
    if matched_tickers:
        t0 = matched_tickers[0]
        other = "FPT" if t0 != "FPT" else "TDH"
        return [
            f"So sánh {t0} và {other}",
            f"{t0} theo VSA 240 cần kiểm tra những khoản mục nào?",
            "Top 5 công ty cảnh báo đỏ năm 2025",
        ]
    if "99" in q_norm or "200" in q_norm:
        return [
            "Sự khác nhau giữa Thông tư 48/2019 và Thông tư 99/2025 về dự phòng?",
            "5 điều kiện ghi nhận doanh thu theo VAS 14",
            "3 thủ tục kiểm toán bắt buộc theo VSA 240",
        ]
    if "48" in q_norm or "du phong" in q_norm or "no xau" in q_norm:
        return [
            "Thông tư 99/2025 có hiệu lực khi nào và đổi tên mẫu nào?",
            "Giao dịch bên liên quan theo VAS 26 cần thuyết minh gì?",
            "TDH năm 2025 rủi ro bao nhiêu?",
        ]
    if "vsa" in q_norm or "240" in q_norm:
        return [
            "5 điều kiện ghi nhận doanh thu theo VAS 14",
            "Thông tư 48 quy định dự phòng nợ xấu thế nào?",
            "Top 5 công ty cảnh báo đỏ năm 2025",
        ]
    return [
        "Thông tư 99/2025 có gì mới?",
        "Thông tư 48 quy định dự phòng nợ xấu thế nào?",
        "So sánh FPT và TDH",
    ]


# ---------------------------------------------------------------------------
# 4. HÀM CHÍNH: ĐIỀU PHỐI TRẢ LỜI HỘI THOẠI ĐA LUỒNG (TÁCH RÕ TRẢ LỜI & TRÍCH DẪN)
# ---------------------------------------------------------------------------
def answer_chat_query(
    question: str,
    scope: str,
    legal_retriever: Any,
    df_all: pd.DataFrame,
    df_b09: pd.DataFrame,
    pdf_diag: dict[str, Any] | None = None,
    pdf_ret: Any = None,
    ticker_hint: str | None = None,
    mode_code: str = "hybrid_rrf",
    top_k: int = 3,
    gemini_api_key: str = "",
    gemini_fn: Any = None,
) -> dict[str, Any]:
    """Xử lý câu hỏi tự nhiên, tách bạch rõ ràng Khối Trả lời & Khối Trích dẫn kèm link Cổng Chính phủ."""
    q_clean = question.strip()
    q_norm = _norm(q_clean)

    valid_tickers = set(df_all.dropna(subset=["composite_risk_score"])["ticker"].unique().tolist())
    want_pdf = scope != "Chỉ Tra cứu Luật VAS / TT 99 / VSA 240" and pdf_diag is not None
    want_law = scope != "Chỉ Soi File PDF đính kèm"

    answer_blocks: list[str] = []
    cite_blocks: list[str] = []
    meta_parts: list[str] = []
    hits_for_gemini: list[dict[str, Any]] = []
    abstained_flag = False
    response_title = "Trợ lý Pháp lý & Tài chính FinAudit AI"

    # A. Chào hỏi / Hướng dẫn nhanh
    matched_tickers = _extract_tickers(q_clean, valid_tickers)
    has_anchor = _has_domain_anchor(q_norm)
    if _is_greeting_or_help(q_norm) and not matched_tickers and not has_anchor and not want_pdf:
        welcome_html = (
            "<div style='padding:15px 18px;background:#ECFDF5;border:1px solid #A7F3D0;border-left:4px solid #064E3B;border-radius:5px;font-size:16.5px;line-height:1.72;color:#132A23;'>"
            "<div style='font-size:13.5px;font-weight:800;color:#064E3B;text-transform:uppercase;letter-spacing:0.45px;margin-bottom:6px;'>Nội dung trả lời</div>"
            "Xin chào. Tôi là <strong>Trợ lý Pháp lý &amp; Tài chính FinAudit AI</strong>. Bạn có thể trao đổi tự nhiên về:<br/>"
            "• <strong>Luật &amp; Chuẩn mực Kế toán – Kiểm toán:</strong> VAS 14/26, Thông tư 99/2025, Thông tư 200/2014, Thông tư 48/2019, VSA 240 (kèm trích dẫn &amp; liên kết Cổng Chính phủ).<br/>"
            "• <strong>Tra cứu nhanh 643 DN niêm yết:</strong> Điểm rủi ro, so sánh 2 mã cổ phiếu, danh sách cảnh báo đỏ.<br/>"
            "• <strong>Soi file PDF BCTC:</strong> Bấm nút <strong>Đính kèm PDF</strong> ngay cạnh ô nhập liệu rồi đặt câu hỏi về vay nợ, tồn kho, ý kiến kiểm toán."
            "</div>"
        )
        return {
            "title": "Xin chào — Hướng dẫn Hỏi đáp FinAudit AI",
            "body_html": welcome_html,
            "meta": "Nguồn: Hệ thống Tri thức FinAudit AI",
            "abstained": False,
            "hits_for_gemini": [],
            "followups": [
                "Nói cho tôi về luật VAS",
                "Thông tư 99/2025 có gì mới?",
                "So sánh FPT và TDH",
            ],
        }

    # B. Soi File PDF đính kèm
    if want_pdf and pdf_diag is not None:
        p_st = pdf_diag["quality_status"]
        if p_st == "SCANNED_IMAGE_PDF":
            b09_extra = ""
            if ticker_hint:
                sub_b09 = df_b09[(df_b09["ticker"] == ticker_hint) & (df_b09["year"] == 2025)]
                if len(sub_b09) > 0:
                    r0 = sub_b09.iloc[0]
                    b09_extra = (
                        f"<br/><strong>Số liệu Thuyết minh B09-DN đối chiếu ({ticker_hint} 2025):</strong> "
                        f"Tiền &amp; TĐT: <strong>{float(r0.get('noc1', 0) or 0):,.2f} tỷ</strong> • "
                        f"Hàng tồn kho gộp: <strong>{float(r0.get('noc15', 0) or 0):,.2f} tỷ</strong> • "
                        f"Doanh thu gộp: <strong>{float(r0.get('noc101', 0) or 0):,.2f} tỷ</strong>."
                    )
            answer_blocks.append(
                f"<div style='padding:14px 18px;background:#FFF7ED;border:1px solid #FDBA74;border-left:4px solid #C2410C;border-radius:5px;margin-bottom:10px;font-size:16.2px;line-height:1.7;color:#9A3412;'>"
                f"<div style='font-size:13.5px;font-weight:800;text-transform:uppercase;margin-bottom:5px;'>Kết quả kiểm tra file PDF</div>"
                f"File <strong>{escape(pdf_diag['file_name'])}</strong> ({pdf_diag['n_pages']} trang) là bản <strong>scan hình ảnh không có lớp chữ</strong>. "
                f"Hệ thống không suy diễn trên ảnh mờ mà tự động đối chiếu sang dữ liệu Thuyết minh B09-DN chính thức.{b09_extra}</div>"
            )
            meta_parts.append(f"Tài liệu: {pdf_diag['file_name']} (Scan ảnh → Đối chiếu B09-DN)")
        elif pdf_ret is not None:
            p_res = pdf_ret.search(q_clean, top_k=min(top_k, 3), mode="hybrid_rrf", enable_abstention=False)
            if p_res["results"]:
                top_p = p_res["results"][0]
                answer_blocks.append(
                    f"<div style='padding:14px 18px;background:#ECFDF5;border:1px solid #A7F3D0;border-left:4px solid #064E3B;border-radius:5px;margin-bottom:10px;font-size:16.4px;color:#132A23;line-height:1.7;'>"
                    f"<div style='font-size:13.5px;font-weight:800;color:#064E3B;text-transform:uppercase;margin-bottom:5px;'>Nội dung trả lời từ file PDF</div>"
                    f"Tìm thấy <strong>{len(p_res['results'])} đoạn thuyết minh liên quan</strong> trong <strong>{escape(pdf_diag['file_name'])}</strong>, "
                    f"tập trung rõ nhất tại <strong>{escape(top_p['citation'])}</strong> (chi tiết nguyên văn trích dẫn bên dưới)."
                    f"</div>"
                )
            for h in p_res["results"]:
                hits_for_gemini.append(h)
                ex_p, _ = trim_excerpt_clean(h["full_text"], 580)
                cite_blocks.append(
                    f"<div style='padding:13px 16px;background:#FFF7ED;border:1px solid #FDBA74;border-left:4px solid #C2410C;border-radius:5px;margin-bottom:10px;'>"
                    f"<div style='font-size:16px;font-weight:800;color:#9A3412;margin-bottom:5px;'>Trích dẫn PDF #{h['rank']} • {escape(h['citation'])}</div>"
                    f"<div style='font-size:15.8px;color:#132A23;line-height:1.68;'>{format_rag_markdown_to_html(ex_p)}</div>"
                    f"</div>"
                )
            meta_parts.append(f"Nguồn: {pdf_diag['file_name']}")

    # C. Tra cứu Trực tiếp Dữ liệu 643 DN
    year_req = _extract_year(q_clean, default_year=2025)
    has_explicit_law_kw = bool(
        re.search(r"\b(vas|vsa|tt\s*99|tt\s*200|tt\s*48|99/2025|200/2014|48/2019|thong tu|chuan muc|luat)\b", q_norm)
    )
    is_market_q = bool(
        re.search(r"\b(top\s*\d*|cao nhat|rui ro nhat|canh bao do|nganh nao|bao nhieu cong ty|bao nhieu dn|thong ke thi truong)\b", q_norm)
        and not matched_tickers
    )
    if matched_tickers and not want_pdf:
        if len(matched_tickers) >= 2:
            response_title, cmp_html = _render_compare_companies_answer(matched_tickers, year_req, df_all)
            answer_blocks.append(cmp_html)
            meta_parts.append(f"Nguồn: BCTC niêm yết ({', '.join(matched_tickers)} • {year_req})")
        else:
            response_title, comp_html = _render_single_company_answer(matched_tickers[0], year_req, df_all, df_b09)
            answer_blocks.append(comp_html)
            meta_parts.append(f"Nguồn: BCTC niêm yết ({matched_tickers[0]} • {year_req})")
        if not has_explicit_law_kw:
            return {
                "title": response_title,
                "body_html": "".join(answer_blocks),
                "meta": " • ".join(meta_parts),
                "abstained": False,
                "hits_for_gemini": hits_for_gemini,
                "followups": _suggest_followups(q_norm, matched_tickers, False, False),
            }

    if is_market_q and not want_pdf and not has_explicit_law_kw:
        response_title, mkt_html = _render_market_summary_answer(q_norm, year_req, df_all)
        answer_blocks.append(mkt_html)
        meta_parts.append(f"Nguồn: Dữ liệu 643 DN niêm yết ({year_req})")
        return {
            "title": response_title,
            "body_html": "".join(answer_blocks),
            "meta": " • ".join(meta_parts),
            "abstained": False,
            "hits_for_gemini": hits_for_gemini,
            "followups": _suggest_followups(q_norm, [], False, False),
        }

    # D. Tra cứu Pháp lý — Tách rõ KHỐI TRẢ LỜI vs. KHỐI TRÍCH DẪN + LINK CỔNG CHÍNH PHỦ
    if want_law:
        concept = _match_concept_overview(q_norm)
        if concept is not None:
            c_title, c_overview_html, c_rag_query = concept
            response_title = c_title
            answer_blocks.append(
                f"<div style='padding:15px 18px;background:#ECFDF5;border:1px solid #A7F3D0;border-left:4px solid #064E3B;border-radius:5px;margin-bottom:12px;'>"
                f"<div style='font-size:13.5px;font-weight:800;color:#064E3B;text-transform:uppercase;letter-spacing:0.45px;margin-bottom:6px;'>Nội dung trả lời</div>"
                f"<div style='font-size:16.5px;color:#132A23;line-height:1.72;'>{c_overview_html}</div></div>"
            )
            res = legal_retriever.search(c_rag_query, top_k=min(top_k, 3), mode="hybrid_rrf", enable_abstention=False)
            meta_parts.append("Nguồn: Hệ thống Văn bản Pháp quy Bộ Tài chính")
        else:
            expanded_q = _expand_legal_query(q_clean)
            use_strict_gate = not has_anchor
            res = legal_retriever.search(
                expanded_q if has_anchor else q_clean,
                top_k=top_k,
                mode="hybrid_rrf",
                enable_abstention=use_strict_gate,
            )
            if has_anchor and res["max_bm25_dual"] <= 0.0 and res["max_tfidf_wc"] < 0.02:
                res["abstained"] = True
                res["results"] = []
                res["abstention_reason"] = (
                    "Chưa tìm thấy điều khoản khớp trực tiếp trong 5 văn bản pháp lý hiện có "
                    "(TT 99/2025, TT 200/2014, TT 48/2019, VSA 240, VAS 14/26)."
                )
            meta_parts.append("Nguồn: Hệ thống Văn bản Pháp quy Bộ Tài chính")

        if res["abstained"]:
            if not answer_blocks and not cite_blocks:
                abstained_flag = True
                response_title = "Câu hỏi ngoài phạm vi Kế toán – Kiểm toán"
                answer_blocks.append(
                    "<div style='padding:15px 18px;background:#FFF1F2;border:1px solid #FECDD3;border-left:4px solid #BE123C;border-radius:5px;font-size:16.2px;color:#9F1239;line-height:1.68;'>"
                    "<strong>CỔNG CHỐNG ẢO GIÁC ĐÃ KÍCH HOẠT:</strong><br/>"
                    "Câu hỏi này nằm ngoài phạm vi tri thức Kế toán, Kiểm toán và Báo cáo tài chính của hệ thống. "
                    "Để đảm bảo thông tin chính xác tuyệt đối, tôi xin phép không suy diễn ngoài văn bản."
                    "<div style='margin-top:10px;padding-top:10px;border-top:1px dashed #FECDD3;color:#132A23;font-size:15.5px;'>"
                    "Bạn có thể chọn 1 trong các gợi ý bên dưới hoặc đặt câu hỏi về <strong>VAS, Thông tư 99/2025, Thông tư 48/2019, VSA 240</strong> hoặc <strong>mã cổ phiếu HOSE/HNX</strong>."
                    "</div></div>"
                )
        else:
            if not answer_blocks and res["results"]:
                # Tạo tóm tắt trả lời trực tiếp 1 đoạn gọn gàng trước khi đưa các thẻ Trích dẫn nguyên văn!
                top_hit = res["results"][0]
                lead_clean, _ = trim_excerpt_clean(top_hit["full_text"], 360)
                response_title = f"Giải đáp theo {top_hit['citation'].strip('[]')}"
                answer_blocks.append(
                    f"<div style='padding:15px 18px;background:#ECFDF5;border:1px solid #A7F3D0;border-left:4px solid #064E3B;border-radius:5px;margin-bottom:12px;'>"
                    f"<div style='font-size:13.5px;font-weight:800;color:#064E3B;text-transform:uppercase;letter-spacing:0.45px;margin-bottom:6px;'>Nội dung trả lời chính</div>"
                    f"<div style='font-size:16.5px;color:#132A23;line-height:1.72;'>{format_rag_markdown_to_html(lead_clean)}</div></div>"
                )

            for hit in res["results"]:
                hits_for_gemini.append(hit)
                ex_l, _ = trim_excerpt_clean(hit["full_text"], 620)
                gov_html = _gov_link_pill(hit["citation"] + " " + hit["source_title"])
                cite_blocks.append(
                    f"<div style='padding:13px 16px;background:#FFFFFF;border:1px solid #C9D8D2;border-left:4px solid #0F766E;border-radius:5px;margin-bottom:10px;box-shadow:0 1px 4px rgba(6,78,59,0.04);'>"
                    f"<div style='font-size:16.2px;font-weight:800;color:#064E3B;margin-bottom:5px;'>Căn cứ #{hit['rank']} • {escape(hit['citation'])}</div>"
                    f"<div style='font-size:15.8px;color:#243E36;line-height:1.68;'>{format_rag_markdown_to_html(ex_l)}</div>"
                    f"{gov_html}</div>"
                )

    # E. Tổng hợp mở rộng bằng Gemini (chỉ khi người dùng tự nhập API key)
    if gemini_api_key.strip() and hits_for_gemini and not abstained_flag and gemini_fn is not None:
        gem_txt = gemini_fn(gemini_api_key, q_clean, hits_for_gemini)
        answer_blocks.insert(
            0,
            f"<div style='padding:15px 18px;background:#ECFDF5;border:1px solid #A7F3D0;border-left:4px solid #059669;border-radius:5px;margin-bottom:12px;'>"
            f"<div style='font-size:13.5px;font-weight:800;color:#064E3B;text-transform:uppercase;margin-bottom:6px;'>Tóm tắt mở rộng (Dựa trên nguồn trích dẫn)</div>"
            f"<div style='font-size:16.5px;color:#132A23;line-height:1.7;'>{format_rag_markdown_to_html(gem_txt)}</div></div>",
        )

    # Ghép tách bạch 2 vùng: [Vùng Trả lời] + [Vùng Căn cứ Trích dẫn & Link Chính phủ]
    final_parts = list(answer_blocks)
    if cite_blocks:
        final_parts.append(
            "<div style='margin-top:12px;padding:14px 16px;background:#F3F7F5;border:1px solid #C9D8D2;border-radius:5px;'>"
            "<div style='font-size:13.5px;font-weight:800;color:#4B635B;text-transform:uppercase;letter-spacing:0.45px;margin-bottom:10px;'>"
            "Căn cứ Trích dẫn Pháp lý &amp; Liên kết Cổng Chính phủ</div>"
            + "".join(cite_blocks)
            + "</div>"
        )

    return {
        "title": response_title,
        "body_html": "".join(final_parts),
        "meta": " • ".join(dict.fromkeys(meta_parts)) if meta_parts else "Nguồn: FinAudit AI",
        "abstained": abstained_flag,
        "hits_for_gemini": hits_for_gemini,
        "followups": _suggest_followups(q_norm, matched_tickers, want_pdf, abstained_flag),
    }
