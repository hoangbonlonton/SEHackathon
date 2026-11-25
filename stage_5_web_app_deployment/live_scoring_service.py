"""
DỊCH VỤ CHẤM ĐIỂM TRỰC TIẾP (LIVE SCORING BRIDGE) & TẠO FILE MẪU UPLOAD BCTC
=============================================================================
Kết nối trực tiếp dữ liệu người dùng tải lên (CSV/Excel hoặc nhập tay trên Web App)
đi qua tuần tự:
  Trạm 0: Kiểm định Toàn vẹn Số liệu (Data Integrity Gate)
  Trạm 1: Chuyên gia 1 (02_forensic_features.compute_deterministic_forensics + Peer Robust Z-Score)
  Trạm 2: Chuyên gia 2 (03_train_validate_model.score_new_observations -> Isolation Forest + SHAP)
"""

from __future__ import annotations

from datetime import datetime
import importlib.util
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
STAGE2_PATH = ROOT_DIR / "stage_2_preprocessing_forensics" / "02_forensic_features.py"
STAGE3_PATH = ROOT_DIR / "stage_3_ai_modeling_validation" / "03_train_validate_model.py"
SAMPLE_DIR = ROOT_DIR / "data_store" / "sample_uploads"

REQUIRED_UPLOAD_COLS = [
    "ticker",
    "year",
    "icb_sector_vi",
    "total_assets",
    "current_assets",
    "cash_and_equivalents",
    "accounts_receivable",
    "prepayments_to_suppliers",
    "other_receivables_st",
    "provision_doubtful_debts",
    "inventory",
    "other_receivables_lt",
    "ppe_net",
    "long_term_investments",
    "total_liabilities",
    "current_liabilities",
    "total_equity",
    "retained_earnings",
    "net_revenue",
    "cogs",
    "gross_profit",
    "sga_expenses",
    "ebit",
    "net_income",
    "cfo",
    "depreciation",
]

OPTIONAL_NUMERIC_DEFAULTS = {
    "short_term_investments": 0.0,
    "short_term_receivables": None,  # Tự tính = AR + prepayments + other_st - provision nếu thiếu
    "fixed_assets_total": None,      # Mặc định = ppe_net nếu thiếu
    "construction_in_progress": 0.0,
    "short_term_debt": 0.0,
    "long_term_liabilities": None,   # Tự tính = total_liabilities - current_liabilities nếu thiếu
    "long_term_debt": 0.0,
    "selling_expenses": 0.0,
    "admin_expenses": 0.0,
    "interest_expense": 0.0,
    "operating_income": None,
    "ebt": None,
}

# 2 công ty mẫu đã kiểm chứng tính tay trong 1_1_BaoCaoDeHieu_V2.md (đơn vị: Tỷ VND)
SAMPLE_WORKED_EXAMPLES: list[dict[str, Any]] = [
    # Công ty Minh Bạch (2024 & 2025)
    {
        "ticker": "MINH_BACH",
        "company_name": "CTCP Mẫu Minh Bạch (Ví dụ đối chứng An toàn)",
        "icb_sector_vi": "Thực phẩm và đồ uống",
        "year": 2024,
        "total_assets": 1000.0,
        "current_assets": 550.0,
        "cash_and_equivalents": 180.0,
        "short_term_receivables": 132.0,
        "accounts_receivable": 100.0,
        "prepayments_to_suppliers": 20.0,
        "other_receivables_st": 15.0,
        "provision_doubtful_debts": 3.0,
        "inventory": 238.0,
        "other_receivables_lt": 5.0,
        "ppe_net": 400.0,
        "construction_in_progress": 10.0,
        "long_term_investments": 35.0,
        "total_liabilities": 350.0,
        "current_liabilities": 200.0,
        "short_term_debt": 50.0,
        "long_term_debt": 80.0,
        "total_equity": 650.0,
        "retained_earnings": 240.0,
        "net_revenue": 1000.0,
        "cogs": 700.0,
        "gross_profit": 300.0,
        "sga_expenses": 100.0,
        "operating_income": 190.0,
        "ebit": 195.0,
        "net_income": 150.0,
        "cfo": 168.0,
        "depreciation": 50.0,
    },
    {
        "ticker": "MINH_BACH",
        "company_name": "CTCP Mẫu Minh Bạch (Ví dụ đối chứng An toàn)",
        "icb_sector_vi": "Thực phẩm và đồ uống",
        "year": 2025,
        "total_assets": 1100.0,
        "current_assets": 620.0,
        "cash_and_equivalents": 230.0,
        "short_term_receivables": 143.5,
        "accounts_receivable": 110.0,
        "prepayments_to_suppliers": 22.0,
        "other_receivables_st": 15.0,
        "provision_doubtful_debts": 3.5,
        "inventory": 246.5,
        "other_receivables_lt": 5.0,
        "ppe_net": 430.0,
        "construction_in_progress": 10.0,
        "long_term_investments": 35.0,
        "total_liabilities": 360.0,
        "current_liabilities": 200.0,
        "short_term_debt": 45.0,
        "long_term_debt": 70.0,
        "total_equity": 740.0,
        "retained_earnings": 320.0,
        "net_revenue": 1150.0,
        "cogs": 793.5,
        "gross_profit": 356.5,
        "sga_expenses": 115.0,
        "operating_income": 231.0,
        "ebit": 236.0,
        "net_income": 185.0,
        "cfo": 210.0,
        "depreciation": 55.0,
    },
    # Công ty Thổi Số (2024 & 2025)
    {
        "ticker": "THOI_SO",
        "company_name": "CTCP Mẫu Thổi Số (Ví dụ mô phỏng Cảnh báo Đỏ)",
        "icb_sector_vi": "Bất động sản",
        "year": 2024,
        "total_assets": 1000.0,
        "current_assets": 500.0,
        "cash_and_equivalents": 60.0,
        "short_term_receivables": 238.0,
        "accounts_receivable": 120.0,
        "prepayments_to_suppliers": 40.0,
        "other_receivables_st": 80.0,
        "provision_doubtful_debts": 2.0,
        "inventory": 202.0,
        "other_receivables_lt": 100.0,
        "ppe_net": 320.0,
        "construction_in_progress": 50.0,
        "long_term_investments": 30.0,
        "total_liabilities": 650.0,
        "current_liabilities": 460.0,
        "short_term_debt": 220.0,
        "long_term_debt": 150.0,
        "total_equity": 350.0,
        "retained_earnings": 10.0,
        "net_revenue": 1000.0,
        "cogs": 700.0,
        "gross_profit": 300.0,
        "sga_expenses": 100.0,
        "operating_income": 115.0,
        "ebit": 130.0,
        "net_income": 90.0,
        "cfo": 25.0,
        "depreciation": 40.0,
    },
    {
        "ticker": "THOI_SO",
        "company_name": "CTCP Mẫu Thổi Số (Ví dụ mô phỏng Cảnh báo Đỏ)",
        "icb_sector_vi": "Bất động sản",
        "year": 2025,
        "total_assets": 1350.0,
        "current_assets": 600.0,
        "cash_and_equivalents": 18.0,
        "short_term_receivables": 558.0,
        "accounts_receivable": 320.0,
        "prepayments_to_suppliers": 80.0,
        "other_receivables_st": 160.0,
        "provision_doubtful_debts": 2.0,
        "inventory": 24.0,
        "other_receivables_lt": 260.0,
        "ppe_net": 260.0,
        "construction_in_progress": 190.0,
        "long_term_investments": 40.0,
        "total_liabilities": 1020.0,
        "current_liabilities": 680.0,
        "short_term_debt": 390.0,
        "long_term_debt": 290.0,
        "total_equity": 330.0,
        "retained_earnings": -45.0,
        "net_revenue": 1450.0,
        "cogs": 1189.0,
        "gross_profit": 261.0,
        "sga_expenses": 190.0,
        "operating_income": 95.0,
        "ebit": 115.0,
        "net_income": 125.0,
        "cfo": -145.0,
        "depreciation": 22.0,
    },
]


def _load_module(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Không thể nạp module {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def ensure_sample_upload_files() -> tuple[Path, Path]:
    """Tạo sẵn file mẫu CSV & Excel chuẩn VAS trong data_store/sample_uploads/ để người dùng tải về dùng ngay."""
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = SAMPLE_DIR / "Mau_Upload_BCTC_FinAudit_AI.csv"
    xlsx_path = SAMPLE_DIR / "Mau_Upload_BCTC_FinAudit_AI.xlsx"

    df_sample = pd.DataFrame(SAMPLE_WORKED_EXAMPLES)
    df_sample.to_csv(csv_path, index=False, encoding="utf-8-sig")

    guide_rows = [
        ("ticker", "Mã hoặc tên viết tắt doanh nghiệp (VD: CONG_TY_A)", "Bắt buộc"),
        ("company_name", "Tên đầy đủ doanh nghiệp", "Khuyến nghị"),
        ("icb_sector_vi", "Tên ngành ICB tiếng Việt (VD: Bất động sản, Xây dựng và Vật liệu, Công nghệ Thông tin...)", "Bắt buộc"),
        ("year", "Năm tài chính (Cần ít nhất 2 năm liên tiếp, VD: 2024 và 2025)", "Bắt buộc"),
        ("total_assets", "Tổng cộng tài sản — B01-DN Mã 270 (Đơn vị: Tỷ VND)", "Bắt buộc"),
        ("current_assets", "Tài sản ngắn hạn — B01-DN Mã 100 (Tỷ VND)", "Bắt buộc"),
        ("cash_and_equivalents", "Tiền và tương đương tiền — B01-DN Mã 110 (Tỷ VND)", "Bắt buộc"),
        ("accounts_receivable", "Phải thu ngắn hạn của khách hàng — B01-DN Mã 131 (Tỷ VND)", "Bắt buộc"),
        ("prepayments_to_suppliers", "Trả trước cho người bán ngắn hạn — B01-DN Mã 132 (Tỷ VND)", "Bắt buộc"),
        ("other_receivables_st", "Phải thu ngắn hạn khác — B01-DN Mã 136 (Tỷ VND)", "Bắt buộc"),
        ("provision_doubtful_debts", "Dự phòng phải thu ngắn hạn khó đòi (TK 2293 — ghi số DƯƠNG, Tỷ VND)", "Bắt buộc"),
        ("inventory", "Hàng tồn kho ròng — B01-DN Mã 140 (Tỷ VND)", "Bắt buộc"),
        ("other_receivables_lt", "Phải thu dài hạn khác — B01-DN Mã 216 (Tỷ VND)", "Bắt buộc"),
        ("ppe_net", "TSCĐ hữu hình giá trị còn lại — B01-DN Mã 221 (Tỷ VND)", "Bắt buộc"),
        ("construction_in_progress", "Chi phí XDCB dở dang — B01-DN Mã 242 (Tỷ VND)", "Tùy chọn"),
        ("long_term_investments", "Đầu tư tài chính dài hạn — B01-DN Mã 250 (Tỷ VND)", "Bắt buộc"),
        ("total_liabilities", "Tổng nợ phải trả — B01-DN Mã 300 (Tỷ VND)", "Bắt buộc"),
        ("current_liabilities", "Nợ ngắn hạn — B01-DN Mã 310 (Tỷ VND)", "Bắt buộc"),
        ("total_equity", "Vốn chủ sở hữu — B01-DN Mã 400 (Tỷ VND, có thể âm)", "Bắt buộc"),
        ("retained_earnings", "LNST chưa phân phối — B01-DN Mã 421 (Tỷ VND, có thể âm)", "Bắt buộc"),
        ("net_revenue", "Doanh thu thuần — B02-DN Mã 10 (Tỷ VND)", "Bắt buộc"),
        ("cogs", "Giá vốn hàng bán — B02-DN Mã 11 (ghi số DƯƠNG, Tỷ VND)", "Bắt buộc"),
        ("gross_profit", "Lợi nhuận gộp — B02-DN Mã 20 (Tỷ VND)", "Bắt buộc"),
        ("sga_expenses", "Tổng chi phí bán hàng + QLDN — B02-DN Mã 25+26 (số DƯƠNG, Tỷ VND)", "Bắt buộc"),
        ("ebit", "Lợi nhuận trước lãi vay & thuế EBIT (EBT + Lãi vay, Tỷ VND)", "Bắt buộc"),
        ("net_income", "Lợi nhuận sau thuế TNDN — B02-DN Mã 60 (Tỷ VND)", "Bắt buộc"),
        ("cfo", "Lưu chuyển tiền thuần HĐKD (CFO) — B03-DN Mã 20 (Tỷ VND, âm/dương)", "Bắt buộc"),
        ("depreciation", "Khấu hao TSCĐ & BĐS đầu tư — B03-DN Mã 02 (số DƯƠNG, Tỷ VND)", "Bắt buộc"),
    ]
    df_guide = pd.DataFrame(guide_rows, columns=["Tên cột chuẩn", "Diễn giải chỉ tiêu VAS (TT 99/2025 & TT 200/2014)", "Yêu cầu"])

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_sample.to_excel(writer, sheet_name="Du_Lieu_BCTC_Mau", index=False)
        df_guide.to_excel(writer, sheet_name="Huong_Dan_Nhap_Lieu", index=False)

    return csv_path, xlsx_path


def validate_and_normalize_upload(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    """
    Trạm 0 — Data Integrity Gate:
    Kiểm tra cấu trúc cột, chuyển đổi số, tự điền các cột phụ hợp lệ và kiểm tra phương trình kế toán VAS.
    """
    df = df_raw.copy()
    df.columns = [str(c).strip() for c in df.columns]
    checks: list[dict[str, str]] = []

    missing = [c for c in REQUIRED_UPLOAD_COLS if c not in df.columns]
    if missing:
        checks.append(
            {
                "status": "ERROR",
                "title": "Thiếu cột dữ liệu bắt buộc",
                "detail": f"File tải lên đang thiếu {len(missing)} cột: {', '.join(missing)}",
            }
        )
        return df, checks

    if "company_name" not in df.columns:
        df["company_name"] = df["ticker"].astype(str)
    if "exchange" not in df.columns:
        df["exchange"] = "UPLOAD"
    if "icb_sector_en" not in df.columns:
        df["icb_sector_en"] = df["icb_sector_vi"]

    # Ép kiểu số an toàn
    num_cols = [c for c in REQUIRED_UPLOAD_COLS if c not in ("ticker", "icb_sector_vi")] + list(OPTIONAL_NUMERIC_DEFAULTS.keys())
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["year"] = df["year"].astype(int)
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()

    # Điền các cột phụ tùy chọn theo đúng quan hệ kế toán VAS
    for col, default_val in OPTIONAL_NUMERIC_DEFAULTS.items():
        if col not in df.columns:
            if col == "short_term_receivables":
                df[col] = (
                    df["accounts_receivable"].fillna(0)
                    + df["prepayments_to_suppliers"].fillna(0)
                    + df["other_receivables_st"].fillna(0)
                    - df["provision_doubtful_debts"].fillna(0)
                ).clip(lower=0.0)
            elif col == "fixed_assets_total":
                df[col] = df["ppe_net"].fillna(0)
            elif col == "long_term_liabilities":
                df[col] = (df["total_liabilities"] - df["current_liabilities"]).clip(lower=0.0)
            elif col == "operating_income":
                df[col] = df["ebit"]
            elif col == "ebt":
                df[col] = df["ebit"] - df.get("interest_expense", 0.0)
            else:
                df[col] = float(default_val) if default_val is not None else 0.0

    # Kiểm tra phương trình cân đối B01-DN: TA = TL + EQ
    bs_err = (df["total_assets"] - (df["total_liabilities"] + df["total_equity"])).abs() / df["total_assets"].abs().clip(lower=1e-6)
    n_bs_bad = int((bs_err >= 0.01).sum())
    if n_bs_bad == 0:
        checks.append(
            {
                "status": "PASS",
                "title": "Cân đối B01-DN (Tổng TS = Nợ phải trả + VCSH)",
                "detail": f"Khớp 100% ({len(df)}/{len(df)} dòng có sai số < 1%).",
            }
        )
    else:
        checks.append(
            {
                "status": "WARN",
                "title": "Cảnh báo lệch cân đối B01-DN",
                "detail": f"Có {n_bs_bad}/{len(df)} dòng lệch Tổng TS vs (Nợ + VCSH) >= 1%. Vẫn tiếp tục chấm điểm nhưng cần kiểm tra lại số nhập.",
            }
        )

    # Kiểm tra phương trình lãi gộp B02-DN: GP = Rev - COGS
    gp_err = (df["gross_profit"] - (df["net_revenue"] - df["cogs"])).abs() / df["net_revenue"].abs().clip(lower=1e-6)
    n_gp_bad = int((gp_err >= 0.02).sum())
    if n_gp_bad == 0:
        checks.append(
            {
                "status": "PASS",
                "title": "Khớp Lợi nhuận gộp B02-DN (DT - Giá vốn = LN gộp)",
                "detail": f"Khớp 100% ({len(df)}/{len(df)} dòng).",
            }
        )
    else:
        checks.append(
            {
                "status": "WARN",
                "title": "Cảnh báo chênh lệch Lợi nhuận gộp B02-DN",
                "detail": f"Có {n_gp_bad}/{len(df)} dòng chênh lệch giữa (Doanh thu - Giá vốn) và Lợi nhuận gộp.",
            }
        )

    # Kiểm tra chuỗi 2 năm liên tiếp
    df = df.sort_values(["ticker", "year"]).reset_index(drop=True)
    has_pair = df.groupby("ticker")["year"].diff().eq(1).any()
    if has_pair:
        n_tickers = int(df["ticker"].nunique())
        checks.append(
            {
                "status": "PASS",
                "title": "Đủ chuỗi thời gian 2 năm liên tiếp (t-1 & t)",
                "detail": f"Nhận diện {n_tickers} doanh nghiệp với đủ cặp năm liên tiếp để tính Beneish 8 biến, Altman Z'', AI & SHAP.",
            }
        )
    else:
        checks.append(
            {
                "status": "ERROR",
                "title": "Thiếu chuỗi 2 năm liên tiếp",
                "detail": "Mỗi doanh nghiệp cần tối thiểu 2 năm liền kề (VD: 2024 và 2025) để tính các chỉ số tăng trưởng DSRI, GMI, SGI, AQI, DEPI.",
            }
        )

    return df, checks


def run_live_scoring_pipeline(
    df_user_raw: pd.DataFrame,
    df_market_ref: pd.DataFrame,
    benchmarks_df: pd.DataFrame,
    artifacts: dict[str, Any],
) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    """
    Chạy trọn vẹn pipeline Live Scoring cho dữ liệu BCTC mới tải lên:
      1. Trạm 0: validate_and_normalize_upload()
      2. Trạm 1: Stage 2 compute_deterministic_forensics() + Winsorize theo phân vị [1%, 99%] năm 2025
                 + Peer-Group Robust Z-Score theo đúng Ngành ICB của người dùng (từ sector_benchmarks_by_year.parquet)
      3. Trạm 2: Stage 3 score_new_observations() -> Isolation Forest + Composite (0-100) + SHAP TreeExplainer V2
    """
    df_clean, checks = validate_and_normalize_upload(df_user_raw)
    if any(c["status"] == "ERROR" for c in checks):
        return df_clean, checks

    s2 = _load_module("finaudit_stage2_mod", STAGE2_PATH)
    s3 = _load_module("finaudit_stage3_mod", STAGE3_PATH)

    # Trạm 1A: Tính toàn bộ chỉ số gốc xác định 100%
    df_feat = s2.compute_deterministic_forensics(df_clean)

    # Trạm 1B: Cắt ngưỡng Winsorization [1%, 99%] dựa trên phân vị tham chiếu thị trường (năm mới nhất 2025)
    ref_2025 = df_market_ref[df_market_ref["year"] == 2025]
    for col in s2.WINSOR_COLS:
        raw_col = f"{col}_raw"
        ref_s = ref_2025[raw_col].dropna() if raw_col in ref_2025.columns else pd.Series(dtype=float)
        if len(ref_s) >= 20:
            lo = float(ref_s.quantile(0.01))
            hi = float(ref_s.quantile(0.99))
            df_feat[col] = df_feat[raw_col].clip(lower=lo, upper=hi)
        else:
            df_feat[col] = df_feat[raw_col]

    # Tính lại Beneish M-Score & Altman Z''-Score ổn định giống hệt Giai đoạn 2
    gmi_p95 = float(ref_2025["gmi"].dropna().quantile(0.95)) if "gmi" in ref_2025.columns else 2.5
    gmi_for_m = df_feat["gmi"].copy()
    bad_gm = df_feat["has_lag1"] & df_feat["gm_negative_flag"] & gmi_for_m.isna() & (~df_feat["zero_revenue_flag"])
    gmi_for_m = gmi_for_m.where(~bad_gm, gmi_p95)

    elig = df_feat["has_lag1"] & (~df_feat["zero_revenue_flag"]) & df_feat["tata"].notna()
    df_feat["beneish_m_score"] = np.where(
        elig,
        -4.84
        + 0.920 * df_feat["dsri"].fillna(1.0)
        + 0.528 * gmi_for_m.fillna(1.0)
        + 0.404 * df_feat["aqi"].fillna(1.0)
        + 0.892 * df_feat["sgi"].fillna(1.0)
        + 0.115 * df_feat["depi"].fillna(1.0)
        - 0.172 * df_feat["sgai"].fillna(1.0)
        + 4.679 * df_feat["tata"]
        - 0.327 * df_feat["lvgi"].fillna(1.0),
        np.nan,
    )
    df_feat["beneish_flag"] = df_feat["beneish_m_score"] > s2.BENEISH_THRESHOLD

    df_feat["altman_z_double_prime"] = (
        3.25
        + 6.56 * df_feat["altman_x1"]
        + 3.26 * df_feat["altman_x2"]
        + 6.72 * df_feat["altman_x3"]
        + 1.05 * df_feat["altman_x4"]
    )
    df_feat["altman_zone"] = np.select(
        [
            df_feat["altman_z_double_prime"].isna(),
            df_feat["altman_z_double_prime"] > s2.ALTMAN_SAFE_THRESHOLD,
            df_feat["altman_z_double_prime"] >= s2.ALTMAN_DISTRESS_THRESHOLD,
        ],
        ["Insufficient", "Safe", "Grey"],
        default="Distress",
    )

    # Trạm 1C: Tính Peer-Group Robust Z-Score từ bảng chuẩn ngành đã lưu (sector_benchmarks_by_year.parquet)
    # Nếu năm tải lên > 2025 hoặc < 2019, neo về mốc chuẩn mới nhất năm 2025 của đúng ngành ICB đó
    bench_lookup: dict[tuple[str, int, str], tuple[float, float]] = {}
    for _, br in benchmarks_df.iterrows():
        bench_lookup[(str(br["icb_sector_vi"]), int(br["year"]), str(br["feature"]))] = (
            float(br["sector_median"]),
            float(br["robust_scale"]),
        )

    # Chuẩn fallback toàn thị trường năm 2025 cho từng đặc trưng
    mkt_fallback: dict[str, tuple[float, float]] = {}
    for feat in s2.AI_FEATURE_COLS:
        s = ref_2025[feat].dropna()
        med = float(s.median()) if len(s) > 0 else 0.0
        mad = float((s - med).abs().median()) if len(s) > 0 else 1.0
        scale = 1.4826 * mad
        if scale < 1e-4:
            scale = float(s.std()) if len(s) > 1 and float(s.std()) > 1e-4 else 1.0
        mkt_fallback[feat] = (med, scale)

    z_cols_dict: dict[str, list[float]] = {}
    for feat in s2.AI_FEATURE_COLS:
        z_vals = []
        for _, r in df_feat.iterrows():
            val = r.get(feat, np.nan)
            if pd.isna(val):
                z_vals.append(np.nan)
                continue
            sec = str(r["icb_sector_vi"])
            yr_q = int(r["year"])
            key = (sec, yr_q, feat)
            if key not in bench_lookup:
                key = (sec, 2025, feat)
            med, scale = bench_lookup.get(key, mkt_fallback[feat])
            z = float(np.clip((float(val) - med) / max(scale, 1e-4), -6.0, 6.0))
            z_vals.append(z)
        z_cols_dict[f"z_{feat}"] = z_vals

    df_feat = pd.concat([df_feat.copy(), pd.DataFrame(z_cols_dict, index=df_feat.index)], axis=1)

    # Trạm 2: Chạy trực tiếp Isolation Forest + Composite (0-100) + SHAP TreeExplainer V2
    df_scored = s3.score_new_observations(df_feat, artifacts)
    return df_scored, checks


# ---------------------------------------------------------------------------
# 2. BỘ NHẬN DIỆN & ÁNH XẠ LINH HOẠT FILE BCTC KHÔNG THEO MẪU 26 CỘT
# ---------------------------------------------------------------------------
def _norm_header(text: Any) -> str:
    s = str(text or "").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


FLEX_COLUMN_ALIASES: dict[str, list[str]] = {
    "ticker": ["ticker", "ma ck", "ma chung khoan", "ma dn", "ma doanh nghiep", "symbol", "code", "cong ty"],
    "company_name": ["company_name", "ten cong ty", "ten doanh nghiep", "doanh nghiep", "ten dn"],
    "icb_sector_vi": ["icb_sector_vi", "nganh", "nganh icb", "nganh nghe", "linh vuc", "sector"],
    "year": ["year", "nam", "nam tai chinh", "ky bao cao", "nien do"],
    "total_assets": ["total_assets", "tong cong tai san", "tong tai san", "ma so 270", "ms 270", "270"],
    "current_assets": ["current_assets", "tai san ngan han", "ts ngan han", "ma so 100", "ms 100", "100"],
    "cash_and_equivalents": ["cash_and_equivalents", "tien va cac khoan tuong duong tien", "tien va tuong duong tien", "tien mat", "ma so 110", "110"],
    "accounts_receivable": ["accounts_receivable", "phai thu ngan han cua khach hang", "phai thu khach hang", "phai thu kh", "tk 131", "131"],
    "prepayments_to_suppliers": ["prepayments_to_suppliers", "tra truoc cho nguoi ban", "tra truoc nguoi ban", "132"],
    "other_receivables_st": ["other_receivables_st", "phai thu ngan han khac", "phai thu khac ngan han", "136"],
    "provision_doubtful_debts": ["provision_doubtful_debts", "du phong phai thu ngan han kho doi", "du phong phai thu kho doi", "du phong kho doi", "137", "2293"],
    "inventory": ["inventory", "hang ton kho", "ton kho", "140", "141"],
    "other_receivables_lt": ["other_receivables_lt", "phai thu dai han khac", "phai thu khac dai han", "216"],
    "ppe_net": ["ppe_net", "tai san co dinh huu hinh", "tscd huu hinh", "tai san co dinh", "tscd", "221", "220"],
    "long_term_investments": ["long_term_investments", "dau tu tai chinh dai han", "dau tu dai han", "250"],
    "total_liabilities": ["total_liabilities", "no phai tra", "tong no phai tra", "tong no", "300"],
    "current_liabilities": ["current_liabilities", "no ngan han", "310"],
    "total_equity": ["total_equity", "von chu so huu", "von csh", "vcsh", "400"],
    "retained_earnings": ["retained_earnings", "loi nhuan sau thue chua phan phoi", "lnst chua phan phoi", "loi nhuan chua phan phoi", "421"],
    "net_revenue": ["net_revenue", "doanh thu thuan", "doanh thu thuan ve ban hang", "doanh thu ban hang", "doanh thu", "revenue"],
    "cogs": ["cogs", "gia von hang ban", "gia von"],
    "gross_profit": ["gross_profit", "loi nhuan gop", "lai gop"],
    "sga_expenses": ["sga_expenses", "chi phi ban hang va quan ly", "chi phi bh va qldn", "tong chi phi ban hang", "sga"],
    "selling_expenses": ["selling_expenses", "chi phi ban hang"],
    "admin_expenses": ["admin_expenses", "chi phi quan ly doanh nghiep", "chi phi qldn"],
    "ebit": ["ebit", "loi nhuan truoc lai vay va thue", "loi nhuan thuan tu hoat dong kinh doanh", "loi nhuan tu hdkd"],
    "net_income": ["net_income", "loi nhuan sau thue", "lnst", "loi nhuan rong", "lai sau thue"],
    "cfo": ["cfo", "luu chuyen tien thuan tu hoat dong kinh doanh", "luu chuyen tien tu hdkd", "dong tien hdkd", "dong tien kinh doanh"],
    "depreciation": ["depreciation", "khau hao tscd", "khau hao tai san co dinh", "chi phi khau hao", "khau hao"],
}

CORE_MANDATORY_FLEX = [
    "year", "total_assets", "current_assets", "total_liabilities",
    "current_liabilities", "total_equity", "net_revenue", "net_income", "cfo",
]


def _parse_vn_number(val: Any) -> float:
    """Chuyển đổi an toàn số định dạng VN/Quốc tế (VD: '1.250,5', '(45.2)', '1,250.5') sang float."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return np.nan
    if isinstance(val, (int, float, np.number)):
        return float(val)
    s = str(val).strip()
    if not s or s in ("-", "--", "N/A", "nan", "None"):
        return np.nan
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("() ").replace(" ", "")
    # Nếu có cả dấu chấm và phẩy: phân biệt kiểu VN (1.234,56) vs US (1,234.56)
    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif s.count(".") >= 2:
        # Số tiền VND ngăn cách hàng nghìn bằng nhiều dấu chấm (VD: 1.000.000.000.000)
        s = s.replace(".", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        num = float(s)
        return -abs(num) if neg else num
    except ValueError:
        return np.nan


def _try_transpose_vertical_bctc(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Tự động nhận diện bảng BCTC trình bày dọc chuẩn VAS (cột 1 = Chỉ tiêu, các cột sau = Năm 2024, 2025...) và xoay ngang."""
    year_cols: list[tuple[Any, int]] = []
    for c in df_raw.columns:
        m = re.search(r"\b(201[5-9]|202[0-9])\b", str(c))
        if m:
            year_cols.append((c, int(m.group(1))))
    if len(year_cols) < 2:
        return df_raw, False

    # Tìm cột chứa tên chỉ tiêu văn bản dài nhất
    text_col = None
    best_str_score = -1
    for c in df_raw.columns:
        if any(c == yc for yc, _ in year_cols):
            continue
        vals = df_raw[c].dropna().astype(str)
        score = sum(1 for v in vals if len(v.strip()) >= 6 and re.search(r"[a-zA-ZÀ-ỹ]", v))
        if score > best_str_score:
            best_str_score = score
            text_col = c
    if text_col is None or best_str_score < 4:
        return df_raw, False

    rows_out: list[dict[str, Any]] = []
    for orig_col, yr in year_cols:
        rec: dict[str, Any] = {"year": yr}
        for _, r in df_raw.iterrows():
            lbl = str(r.get(text_col, "")).strip()
            if lbl:
                rec[lbl] = _parse_vn_number(r.get(orig_col))
        rows_out.append(rec)
    return pd.DataFrame(rows_out), True


def smart_normalize_uploaded_bctc(
    df_raw: pd.DataFrame,
    default_ticker: str = "DN_MOI",
    default_sector: str = "Xây dựng và Vật liệu",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Nhận file BCTC Excel/CSV linh hoạt (cả file chuẩn 26 cột lẫn file tiếng Việt tự xuất hoặc bảng dọc B01-DN):
      1. Tự nhận diện & xoay bảng dọc (Chỉ tiêu × Năm) nếu cần.
      2. Tự khớp tên cột tiếng Việt / mã số chỉ tiêu VAS sang 26 cột chuẩn.
      3. Tự tính hoặc điền an toàn các chỉ tiêu phụ bị thiếu (kèm danh sách minh bạch cho người dùng),
         đảm bảo mô hình AI vận hành ổn định, không bao giờ lỗi sập trang.
    """
    df_work, was_transposed = _try_transpose_vertical_bctc(df_raw.copy())
    df_work.columns = [str(c).strip() for c in df_work.columns]

    mapped_cols: dict[str, str] = {}
    used_src: set[str] = set()

    # Khớp chính xác trước, khớp từ khóa tiếng Việt sau
    norm_src = {c: _norm_header(c) for c in df_work.columns}
    for std_col, aliases in FLEX_COLUMN_ALIASES.items():
        if std_col in df_work.columns and std_col not in used_src:
            mapped_cols[std_col] = std_col
            used_src.add(std_col)
            continue
        matched_src = None
        for al in aliases:
            al_n = _norm_header(al)
            for orig_c, norm_c in norm_src.items():
                if orig_c in used_src:
                    continue
                if norm_c == al_n or (len(al_n) >= 5 and al_n in norm_c):
                    matched_src = orig_c
                    break
            if matched_src is not None:
                break
        if matched_src is not None:
            mapped_cols[std_col] = matched_src
            used_src.add(matched_src)

    out = pd.DataFrame(index=df_work.index)
    for std_col, src_col in mapped_cols.items():
        if std_col in ("ticker", "company_name", "icb_sector_vi"):
            out[std_col] = df_work[src_col].astype(str).str.strip()
        else:
            out[std_col] = df_work[src_col].apply(_parse_vn_number)

    if "ticker" not in out.columns:
        out["ticker"] = default_ticker.strip().upper() or "DN_MOI"
    if "company_name" not in out.columns:
        out["company_name"] = out["ticker"]
    if "icb_sector_vi" not in out.columns:
        out["icb_sector_vi"] = default_sector

    # Chuẩn hóa đơn vị: nếu Tổng TS > 10^9 (người dùng để đơn vị VND đồng thay vì Tỷ VND) -> tự quy đổi về Tỷ VND
    unit_scaled = False
    if "total_assets" in out.columns and out["total_assets"].dropna().abs().median() > 1e8:
        unit_scaled = True
        for col in out.columns:
            if col not in ("ticker", "company_name", "icb_sector_vi", "year"):
                out[col] = out[col] / 1e9

    # Suy luận an toàn các cột phụ kế toán nếu người dùng upload file rút gọn (không đủ 26 cột)
    auto_estimated: list[str] = []
    if "sga_expenses" not in out.columns and ("selling_expenses" in out.columns or "admin_expenses" in out.columns):
        out["sga_expenses"] = out.get("selling_expenses", 0.0).fillna(0.0).abs() + out.get("admin_expenses", 0.0).fillna(0.0).abs()
        auto_estimated.append("Chi phí BH & QLDN (cộng từ CP bán hàng + CP quản lý)")
    if "cogs" in out.columns:
        out["cogs"] = out["cogs"].abs()
    if "provision_doubtful_debts" in out.columns:
        out["provision_doubtful_debts"] = out["provision_doubtful_debts"].abs()
    if "sga_expenses" in out.columns:
        out["sga_expenses"] = out["sga_expenses"].abs()
    if "depreciation" in out.columns:
        out["depreciation"] = out["depreciation"].abs()

    if "gross_profit" not in out.columns and "net_revenue" in out.columns and "cogs" in out.columns:
        out["gross_profit"] = out["net_revenue"] - out["cogs"]
        auto_estimated.append("Lợi nhuận gộp (= Doanh thu thuần - Giá vốn)")
    elif "cogs" not in out.columns and "net_revenue" in out.columns and "gross_profit" in out.columns:
        out["cogs"] = (out["net_revenue"] - out["gross_profit"]).clip(lower=0.0)
        auto_estimated.append("Giá vốn hàng bán (= Doanh thu thuần - LN gộp)")
    elif "cogs" not in out.columns and "gross_profit" not in out.columns and "net_revenue" in out.columns:
        out["cogs"] = (out["net_revenue"] * 0.78).clip(lower=0.0)
        out["gross_profit"] = out["net_revenue"] - out["cogs"]
        auto_estimated.append("Giá vốn & Lợi nhuận gộp (ước lượng mặc định do file thiếu)")

    if "sga_expenses" not in out.columns and "gross_profit" in out.columns and "net_income" in out.columns:
        out["sga_expenses"] = (out["gross_profit"] - out["net_income"]).clip(lower=0.0)
        auto_estimated.append("Chi phí BH & QLDN (ước lượng từ LN gộp - LNST)")
    if "ebit" not in out.columns and "net_income" in out.columns:
        out["ebit"] = out["net_income"] * 1.25
        auto_estimated.append("Lợi nhuận trước lãi vay & thuế EBIT (ước lượng từ LNST)")

    fallback_zero_labels = {
        "cash_and_equivalents": "Tiền & tương đương tiền",
        "accounts_receivable": "Phải thu khách hàng",
        "prepayments_to_suppliers": "Trả trước cho người bán",
        "other_receivables_st": "Phải thu ngắn hạn khác",
        "provision_doubtful_debts": "Dự phòng nợ khó đòi",
        "inventory": "Hàng tồn kho",
        "other_receivables_lt": "Phải thu dài hạn khác",
        "ppe_net": "Tài sản cố định hữu hình",
        "long_term_investments": "Đầu tư tài chính dài hạn",
        "retained_earnings": "Lợi nhuận chưa phân phối",
        "depreciation": "Chi phí khấu hao TSCĐ",
    }
    for col, lbl_vi in fallback_zero_labels.items():
        if col not in out.columns:
            out[col] = 0.0
            auto_estimated.append(f"{lbl_vi} (mặc định 0 do file không có)")

    missing_core = [c for c in CORE_MANDATORY_FLEX if c not in mapped_cols and c not in out.columns]
    report = {
        "was_transposed": was_transposed,
        "unit_scaled_from_vnd": unit_scaled,
        "mapped_count": len(mapped_cols),
        "mapped_cols": mapped_cols,
        "auto_estimated": auto_estimated,
        "missing_core": missing_core,
        "is_standard_26": len(auto_estimated) == 0 and not was_transposed,
    }
    return out, report


# ---------------------------------------------------------------------------
# 3. ĐỒNG BỘ DỮ LIỆU THỜI GIAN THỰC THEO YÊU CẦU TỪ VIETCAP IQ API
# ---------------------------------------------------------------------------
VIETCAP_BASE_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1"
VIETCAP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://iq.vietcap.com.vn/",
    "Origin": "https://iq.vietcap.com.vn",
}


def sync_company_live_from_vietcap(
    ticker: str,
    meta_row: pd.Series,
    df_market_ref: pd.DataFrame,
    benchmarks_df: pd.DataFrame,
    artifacts: dict[str, Any],
) -> tuple[pd.DataFrame | None, str, str]:
    """
    Gọi trực tiếp API công khai Vietcap IQ cho 1 mã doanh nghiệp (3 bảng B01/B02/B03),
    sau đó chạy lại pipeline chấm điểm AI + SHAP trong ~2 giây để cập nhật số liệu mới nhất theo thời gian thực.
    """
    tkr = ticker.strip().upper()
    now_str = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    sec_by_year: dict[str, dict[int, dict[str, Any]]] = {}

    try:
        with httpx.Client(headers=VIETCAP_HEADERS, timeout=12.0) as client:
            for sec in ("BALANCE_SHEET", "INCOME_STATEMENT", "CASH_FLOW"):
                resp = client.get(f"{VIETCAP_BASE_URL}/company/{tkr}/financial-statement?section={sec}")
                if resp.status_code != 200:
                    return None, f"Không thể kết nối Vietcap IQ (mã HTTP {resp.status_code}). Hệ thống giữ nguyên dữ liệu đã lưu.", now_str
                payload = resp.json()
                ymap: dict[int, dict[str, Any]] = {}
                for r in payload.get("data", {}).get("years", []):
                    yr = r.get("yearReport")
                    if yr is not None and 2018 <= int(yr) <= 2027:
                        ymap[int(yr)] = r
                sec_by_year[sec] = ymap
    except Exception as exc:
        return None, f"Tạm thời không kết nối được máy chủ dữ liệu trực tuyến ({type(exc).__name__}). Đang dùng dữ liệu đã kiểm định cục bộ.", now_str

    common_years = sorted(
        set(sec_by_year["BALANCE_SHEET"]) & set(sec_by_year["INCOME_STATEMENT"]) & set(sec_by_year["CASH_FLOW"])
    )
    if len(common_years) < 2:
        return None, f"API chưa trả đủ 2 năm liên tiếp cho mã {tkr}. Đang giữ nguyên dữ liệu cục bộ.", now_str

    def _f(v: Any) -> float:
        try:
            return float(v) if v is not None and v != "" else np.nan
        except (TypeError, ValueError):
            return np.nan

    def _pos(v: Any) -> float:
        x = _f(v)
        return -x if not np.isnan(x) else np.nan

    scale = 1e9
    recs: list[dict[str, Any]] = []
    for yr in common_years:
        b = sec_by_year["BALANCE_SHEET"][yr]
        i = sec_by_year["INCOME_STATEMENT"][yr]
        f = sec_by_year["CASH_FLOW"][yr]
        selling = _pos(i.get("isa9"))
        admin = _pos(i.get("isa10"))
        sga = (0.0 if np.isnan(selling) else selling) + (0.0 if np.isnan(admin) else admin)
        ebt = _f(i.get("isa16"))
        int_exp = _pos(i.get("isa8"))
        ebit = ebt + (0.0 if np.isnan(int_exp) else int_exp) if not np.isnan(ebt) else np.nan
        prov_raw = _f(b.get("bsa14"))
        recs.append(
            {
                "ticker": tkr,
                "company_name": str(meta_row.get("company_name", tkr)),
                "exchange": str(meta_row.get("exchange", "HOSE")),
                "icb_sector_vi": str(meta_row.get("icb_sector_vi", "Phi tài chính")),
                "year": yr,
                "total_assets": _f(b.get("bsa53")) / scale,
                "current_assets": _f(b.get("bsa1")) / scale,
                "cash_and_equivalents": _f(b.get("bsa2")) / scale,
                "short_term_investments": _f(b.get("bsa5")) / scale,
                "short_term_receivables": _f(b.get("bsa8")) / scale,
                "accounts_receivable": _f(b.get("bsa9")) / scale,
                "prepayments_to_suppliers": _f(b.get("bsa10")) / scale,
                "other_receivables_st": _f(b.get("bsa13")) / scale,
                "provision_doubtful_debts": (abs(prov_raw) / scale) if not np.isnan(prov_raw) else 0.0,
                "inventory": _f(b.get("bsa15")) / scale,
                "other_receivables_lt": (_f(b.get("bsa27")) / scale) if not np.isnan(_f(b.get("bsa27"))) else 0.0,
                "ppe_net": _f(b.get("bsa30")) / scale,
                "fixed_assets_total": _f(b.get("bsa29")) / scale,
                "construction_in_progress": (_f(b.get("bsa188")) / scale) if not np.isnan(_f(b.get("bsa188"))) else 0.0,
                "long_term_investments": (_f(b.get("bsa43")) / scale) if not np.isnan(_f(b.get("bsa43"))) else 0.0,
                "total_liabilities": _f(b.get("bsa54")) / scale,
                "current_liabilities": _f(b.get("bsa55")) / scale,
                "short_term_debt": (_f(b.get("bsa56")) / scale) if not np.isnan(_f(b.get("bsa56"))) else 0.0,
                "long_term_liabilities": (_f(b.get("bsa67")) / scale) if not np.isnan(_f(b.get("bsa67"))) else 0.0,
                "long_term_debt": (_f(b.get("bsa71")) / scale) if not np.isnan(_f(b.get("bsa71"))) else 0.0,
                "total_equity": _f(b.get("bsa78")) / scale,
                "retained_earnings": (_f(b.get("bsa90")) / scale) if not np.isnan(_f(b.get("bsa90"))) else 0.0,
                "net_revenue": _f(i.get("isa3")) / scale,
                "cogs": _pos(i.get("isa4")) / scale,
                "gross_profit": _f(i.get("isa5")) / scale,
                "selling_expenses": (selling / scale) if not np.isnan(selling) else 0.0,
                "admin_expenses": (admin / scale) if not np.isnan(admin) else 0.0,
                "sga_expenses": sga / scale,
                "interest_expense": (int_exp / scale) if not np.isnan(int_exp) else 0.0,
                "operating_income": _f(i.get("isa11")) / scale,
                "ebt": ebt / scale if not np.isnan(ebt) else np.nan,
                "ebit": ebit / scale if not np.isnan(ebit) else np.nan,
                "net_income": _f(i.get("isa20")) / scale,
                "cfo": _f(f.get("cfa18")) / scale,
                "depreciation": (_f(f.get("cfa2")) / scale) if not np.isnan(_f(f.get("cfa2"))) else 0.0,
            }
        )

    df_live_raw = pd.DataFrame(recs)
    df_scored, checks = run_live_scoring_pipeline(df_live_raw, df_market_ref, benchmarks_df, artifacts)
    if any(c["status"] == "ERROR" for c in checks):
        return None, f"Dữ liệu trực tuyến của {tkr} chưa đủ điều kiện chấm điểm.", now_str
    max_yr = int(df_scored["year"].max())
    return df_scored, f"Đã đồng bộ dữ liệu trực tuyến mới nhất từ Vietcap IQ ({len(common_years)} năm, đến năm {max_yr}) lúc {now_str}.", now_str
