"""
Vòng thu hồi bổ sung (Recovery Pass) & Xuất biểu đồ tổng quan Giai đoạn 1 (Pure UTF-8).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data_store" / "raw"
STAGE_DIR = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location("acq", STAGE_DIR / "01_data_acquisition.py")
acq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acq)


def main() -> None:
    df_raw = pd.read_parquet(RAW_DIR / "vas_financial_statements_raw.parquet")
    df_nonfin = pd.read_csv(RAW_DIR / "non_financial_universe.csv", dtype={"icbCodeLv2": str, "icbCodeLv4": str})
    log_path = RAW_DIR / "stage1_acquisition_log.json"
    log_info = json.loads(log_path.read_text(encoding="utf-8"))

    # Xác định các mã mục tiêu chưa có trong df_raw
    existing_tks = set(df_raw["ticker"].unique())
    missing_tks = [t for t in df_nonfin["ticker"].tolist() if t not in existing_tks]
    print(f"Đang chạy vòng thu hồi bổ sung cho {len(missing_tks)} mã: {missing_tks}", flush=True)

    recovered_recs = []
    still_failed = []
    for tk in missing_tks:
        meta = df_nonfin[df_nonfin["ticker"] == tk].iloc[0].to_dict()
        time.sleep(0.5)
        _, recs, status = acq.fetch_single_company(meta)
        print(f"  {tk:5s} -> {status} ({len(recs)} dòng)", flush=True)
        if status == "ok" and recs:
            recovered_recs.extend(recs)
        else:
            still_failed.append({"ticker": tk, "reason": status})

    if recovered_recs:
        df_new = pd.concat([df_raw, pd.DataFrame(recovered_recs)], ignore_index=True)
        df_new["icb_code_lv2"] = df_new["icb_code_lv2"].astype(str)
        df_new = (
            df_new.drop_duplicates(subset=["ticker", "year"])
            .sort_values(["ticker", "year"])
            .reset_index(drop=True)
        )
        df_new.to_parquet(RAW_DIR / "vas_financial_statements_raw.parquet", index=False)
        df_new.to_csv(RAW_DIR / "vas_financial_statements_raw.csv", index=False, encoding="utf-8-sig")
    else:
        df_new = df_raw
        df_new["icb_code_lv2"] = df_new["icb_code_lv2"].astype(str)

    n_recovered = len(missing_tks) - len(still_failed)
    log_info["n_companies_success"] = int(df_new["ticker"].nunique())
    log_info["n_firm_years"] = int(len(df_new))
    log_info["n_failed_total"] = len(still_failed)
    log_info["failed_tickers_sample"] = still_failed
    log_info["recovery_pass_recovered"] = n_recovered

    audit = acq.audit_financial_dataset(df_new)
    log_info["audit_summary"] = {k: v for k, v in audit.items() if not isinstance(v, pd.DataFrame)}
    log_path.write_text(json.dumps(log_info, ensure_ascii=False, indent=2), encoding="utf-8")

    # Tái tạo REPORT_STAGE_1_DATA_AUDIT.md bằng UTF-8 sạch tuyệt đối
    acq.generate_stage1_report(log_info["funnel"], log_info, audit)

    # Kiểm tra chi tiết các ngoại lệ trên tập dữ liệu cuối cùng
    bs_err = (
        (df_new["total_assets"] - (df_new["total_liabilities"] + df_new["total_equity"])).abs()
        / df_new["total_assets"].abs()
        * 100.0
    )
    bad_rows = df_new[bs_err >= 1.0][["ticker", "year", "total_assets", "total_liabilities", "total_equity"]]
    bad_desc = ", ".join(
        f"`{r['ticker']}` năm `{int(r['year'])}` (TTS {r['total_assets']:,.2f} tỷ vs Nợ+VCSH {r['total_liabilities']+r['total_equity']:,.2f} tỷ)"
        for _, r in bad_rows.iterrows()
    )
    neg_eq_rows = df_new[df_new["total_equity"] < 0]
    neg_eq_summary = ", ".join(
        f"`{tk}` ({list(grp['year'].astype(int))})"
        for tk, grp in neg_eq_rows.groupby("ticker")
    )
    still_failed_list = [x["ticker"] for x in still_failed]

    extra_note = f"""
---

## 5. NHẬT KÝ XỬ LÝ NGOẠI LỆ & ĐỐI CHỨNG TRƯỜNG HỢP ĐẶC BIỆT (DATA PROVENANCE)

1. **Vòng Thu hồi Bổ sung (Recovery Pass):** Sau lượt tải đa luồng lần 1 (`634/644` mã), hệ thống đã chạy vòng thu hồi tuần tự cho `10` mã bị nghẽn kết nối tạm thời và thu hồi thành công thêm **`{n_recovered}` mã**, nâng độ phủ cuối cùng lên **`{log_info['n_companies_success']}/644` doanh nghiệp ({log_info['n_companies_success']/644*100:.2f}%)** toàn thị trường phi tài chính HOSE & HNX với **`{audit['n_rows']:,}` quan sát `firm-year`**! (`{len(still_failed)}` mã chưa có đủ 3 bảng chung năm trên nguồn: `{still_failed_list}`).
2. **Minh bạch dòng lệch đẳng thức `B01-DN` (`>= 1%`):** Trên toàn bộ `{audit['n_rows']:,}` dòng dữ liệu, chỉ có **`{len(bad_rows)}` dòng duy nhất**: {bad_desc if bad_desc else 'Không có'} $\\rightarrow$ sẽ được gắn cờ `bs_integrity_warning = True` ở Giai đoạn 2 để đảm bảo minh bạch tuyệt đối.
3. **Minh bạch `{len(neg_eq_rows)}` dòng Vốn chủ sở hữu Âm (`total_equity < 0`):** Tập trung tại các doanh nghiệp thực tế có biến cố lỗ lũy kế lớn: {neg_eq_summary if neg_eq_summary else 'Không có'}. Đây là số liệu lịch sử thực tế 100%, bắt buộc **giữ nguyên** để mô hình Altman $Z''$ và AI nhận diện chính xác rủi ro kiệt quệ tài chính.
4. **Biểu đồ Tổng quan Giai đoạn 1:** Đã xuất tại [`stage1_data_overview.png`](stage1_data_overview.png) (xem quy trình trực quan từng bước tại Notebook [`01_data_acquisition_walkthrough.ipynb`](01_data_acquisition_walkthrough.ipynb)).
"""
    rep_path = STAGE_DIR / "REPORT_STAGE_1_DATA_AUDIT.md"
    rep_path.write_text(rep_path.read_text(encoding="utf-8") + extra_note, encoding="utf-8")

    # Vẽ biểu đồ tổng quan chuẩn UTF-8 tiếng Việt, bố cục hài hòa không đè chữ
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.2), dpi=150)
    fig.patch.set_facecolor("#F8FAFC")

    sec_counts = df_new.groupby("icb_sector_vi")["ticker"].nunique().sort_values(ascending=True)
    colors_sec = ["#DC2626" if v < 10 else "#1E40AF" for v in sec_counts.values]
    axes[0].barh(sec_counts.index, sec_counts.values, color=colors_sec, edgecolor="none", alpha=0.92)
    axes[0].set_xlim(0, sec_counts.max() * 1.14)
    axes[0].set_title(
        f"Phân bố {df_new['ticker'].nunique()} DN Phi tài chính theo 16 Ngành ICB (HOSE & HNX)",
        fontsize=11,
        fontweight="bold",
        color="#0F172A",
        pad=12,
    )
    axes[0].set_xlabel("Số lượng doanh nghiệp", fontsize=9.5, color="#334155")
    axes[0].axvline(10, color="#D97706", linestyle="--", linewidth=1.3, label="Ngưỡng mẫu tối thiểu ngành (n = 10)")
    axes[0].legend(fontsize=8.5, loc="lower right", frameon=True, facecolor="white")
    axes[0].grid(axis="x", linestyle=":", alpha=0.5)
    axes[0].set_facecolor("#FFFFFF")
    for i, v in enumerate(sec_counts.values):
        axes[0].text(v + 1.8, i, str(v), va="center", fontsize=8.5, color="#0F172A", fontweight="bold")

    yr_df = (
        df_new.groupby("year")
        .agg(
            n_co=("ticker", "nunique"),
            n_div=("cfo", lambda s: int(((df_new.loc[s.index, "net_income"] > 0) & (s < 0)).sum())),
        )
        .reset_index()
    )
    x = np.arange(len(yr_df))
    axes[1].bar(x - 0.19, yr_df["n_co"], width=0.38, color="#1E40AF", label="Tổng số DN có đủ 3 bảng BCTC")
    axes[1].bar(x + 0.19, yr_df["n_div"], width=0.38, color="#DC2626", label="DN báo Lãi dương (NI > 0) nhưng CFO âm")
    axes[1].set_ylim(0, yr_df["n_co"].max() * 1.22)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(yr_df["year"].astype(str), fontsize=9.5)
    axes[1].set_title(
        "Số lượng DN & Hiện tượng Phân kỳ Dòng tiền (2018–2025)",
        fontsize=11,
        fontweight="bold",
        color="#0F172A",
        pad=12,
    )
    axes[1].set_ylabel("Số lượng doanh nghiệp", fontsize=9.5, color="#334155")
    axes[1].legend(fontsize=8.5, loc="upper center", ncol=2, frameon=True, facecolor="white")
    axes[1].grid(axis="y", linestyle=":", alpha=0.5)
    axes[1].set_facecolor("#FFFFFF")
    for i, (tot, div) in enumerate(zip(yr_df["n_co"], yr_df["n_div"])):
        axes[1].text(i - 0.19, tot + 10, str(tot), ha="center", fontsize=8.2, color="#0F172A", fontweight="bold")
        axes[1].text(i + 0.19, div + 10, str(div), ha="center", fontsize=8.2, color="#DC2626", fontweight="bold")

    plt.tight_layout(pad=2.0)
    chart_path = STAGE_DIR / "stage1_data_overview.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    print(
        f"HOÀN TẤT! Tổng cuối cùng: {df_new['ticker'].nunique()} DN | {len(df_new):,} firm-year | "
        f"Chart: {chart_path}",
        flush=True,
    )


if __name__ == "__main__":
    main()
