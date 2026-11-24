"""
KIỂM THỬ TỰ ĐỘNG TOÀN DIỆN GIAI ĐOẠN 5 (UNIT + STREAMLIT APPTEST 5 PHÂN HỆ + LIVE HTTP SERVER)
=============================================================================================
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
import joblib
import pandas as pd
from streamlit.testing.v1 import AppTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STAGE5_DIR = Path(__file__).resolve().parent
ROOT_DIR = STAGE5_DIR.parent
sys.path.insert(0, str(STAGE5_DIR))

from live_scoring_service import (
    SAMPLE_WORKED_EXAMPLES,
    ensure_sample_upload_files,
    run_live_scoring_pipeline,
)
from report_exporter import generate_html_audit_report


def main() -> None:
    t0_all = time.perf_counter()
    results: dict = {
        "tested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {},
    }

    print("=" * 76)
    print("KIỂM THỬ GIAI ĐOẠN 5: WEB APP STREAMLIT FINAUDIT AI")
    print("=" * 76)

    # -----------------------------------------------------------------------
    # TEST 1: LIVE SCORING SERVICE & EXPORT HTML + SAMPLE EXCEL/CSV
    # -----------------------------------------------------------------------
    print("[Test 1/3] Kiểm thử Live Scoring Pipeline (Minh Bạch, Thổi Số, TDH 2025) & Xuất HTML...")
    csv_p, xlsx_p = ensure_sample_upload_files()
    df_xlsx = pd.read_excel(xlsx_p, sheet_name=0)
    df_all = pd.read_parquet(ROOT_DIR / "data_store/processed/forensic_scored_full.parquet")
    df_bench = pd.read_parquet(ROOT_DIR / "data_store/processed/sector_benchmarks_by_year.parquet")
    artifacts = joblib.load(ROOT_DIR / "data_store/models/finaudit_stage3_artifacts.joblib")

    t_live = time.perf_counter()
    df_live, checks = run_live_scoring_pipeline(df_xlsx, df_all, df_bench, artifacts)
    live_ms = round((time.perf_counter() - t_live) * 1000.0, 1)

    r_mb = df_live[(df_live["ticker"] == "MINH_BACH") & (df_live["year"] == 2025)].iloc[0]
    r_ts = df_live[(df_live["ticker"] == "THOI_SO") & (df_live["year"] == 2025)].iloc[0]
    score_mb = round(float(r_mb["composite_risk_score"]), 2)
    score_ts = round(float(r_ts["composite_risk_score"]), 2)
    print(f"  -> MINH_BACH 2025: {score_mb}đ ({r_mb['risk_tier']}) | THOI_SO 2025: {score_ts}đ ({r_ts['risk_tier']}) | {live_ms} ms")
    assert score_mb < 35.0, f"MINH_BACH score unexpectedly high: {score_mb}"
    assert score_ts >= 65.0, f"THOI_SO score unexpectedly low: {score_ts}"

    # Đối chứng tái lập TDH 2024-2025 qua Live Scoring vs Stage 3 precomputed
    tdh_cols = [c for c in df_xlsx.columns if c in df_all.columns]
    tdh_2yr = df_all[(df_all["ticker"] == "TDH") & (df_all["year"].isin([2024, 2025]))][tdh_cols].copy()
    tdh_live, tdh_checks = run_live_scoring_pipeline(tdh_2yr, df_all, df_bench, artifacts)
    tdh_live_score = round(float(tdh_live[tdh_live["year"] == 2025]["composite_risk_score"].iloc[0]), 2)
    tdh_stage3_score = round(float(df_all[(df_all["ticker"] == "TDH") & (df_all["year"] == 2025)]["composite_risk_score"].iloc[0]), 2)
    tdh_diff = round(abs(tdh_live_score - tdh_stage3_score), 3)
    print(f"  -> Đối chứng tái lập TDH 2025: Live={tdh_live_score}đ vs Stage3={tdh_stage3_score}đ (chênh {tdh_diff}đ)")
    assert tdh_diff < 1.5, f"TDH live vs Stage 3 mismatch too large: {tdh_diff}"

    # Kiểm thử xuất HTML Audit Report
    html_str = generate_html_audit_report(r_ts, rag_brief=None)
    assert len(html_str) > 4000 and "VSA 240" in html_str and "THOI_SO" in html_str
    print(f"  -> Xuất Báo cáo HTML A4 thành công ({len(html_str):,} bytes).")

    results["tests"]["test1_live_scoring_and_export"] = {
        "status": "PASS",
        "sample_csv": str(csv_p),
        "sample_xlsx": str(xlsx_p),
        "live_latency_ms": live_ms,
        "minh_bach_2025_score": score_mb,
        "minh_bach_2025_tier": str(r_mb["risk_tier"]),
        "thoi_so_2025_score": score_ts,
        "thoi_so_2025_tier": str(r_ts["risk_tier"]),
        "tdh_2025_live_score": tdh_live_score,
        "tdh_2025_stage3_score": tdh_stage3_score,
        "tdh_2025_abs_diff": tdh_diff,
        "html_report_bytes": len(html_str),
    }

    # -----------------------------------------------------------------------
    # TEST 2: STREAMLIT APPTEST QUA CẢ 5 PHÂN HỆ CHỨC NĂNG
    # -----------------------------------------------------------------------
    print("[Test 2/3] Đang chạy Streamlit AppTest kiểm thử toàn bộ 5 phân hệ giao diện...")
    modules_to_test = [
        "1. Tổng quan Thị trường & Radar Ngành",
        "2. Hồ sơ Pháp chứng 360° & SHAP",
        "3. Phòng Thẩm định BCTC Mới (Live)",
        "4. Trợ lý AI Soi PDF & Luật VAS",
        "5. Trung tâm Kiểm chứng & ESG-G",
    ]
    app_path = str(STAGE5_DIR / "app.py")
    at = AppTest.from_file(app_path, default_timeout=45)
    t_boot = time.perf_counter()
    at.run()
    cold_boot_s = round(time.perf_counter() - t_boot, 2)
    assert len(at.exception) == 0, f"Exception on initial load: {at.exception}"
    print(f"  -> Cold boot Phân hệ 1: {cold_boot_s}s | Exceptions: 0")

    module_timings = {"module_1_cold_boot_s": cold_boot_s}
    for idx_m, mod_name in enumerate(modules_to_test, start=1):
        t_m = time.perf_counter()
        at.sidebar.radio[0].set_value(mod_name).run()
        dur_s = round(time.perf_counter() - t_m, 2)
        if len(at.exception) > 0:
            raise AssertionError(f"Exception in {mod_name}: {at.exception}")
        module_timings[f"module_{idx_m}_render_s"] = dur_s
        print(f"  -> PASS {mod_name} | Render time: {dur_s}s | Exceptions: 0")

    # Kiểm thử tương tác bấm nút Demo NVL ở Sidebar (nhảy sang Hồ sơ 360° NVL 2025 + PDF Trang 12!)
    t_nvl = time.perf_counter()
    for btn in at.sidebar.button:
        if "NVL" in btn.label:
            btn.click().run()
            break
    nvl_jump_s = round(time.perf_counter() - t_nvl, 2)
    assert len(at.exception) == 0, f"Exception after clicking NVL quick demo: {at.exception}"
    assert at.session_state["selected_ticker"] == "NVL"
    print(f"  -> PASS Quick-Demo NVL 2025 (Hồ sơ 360° + PDF Moore AISC): {nvl_jump_s}s | Exceptions: 0")

    # Đo RAM thực tế của tiến trình Python sau khi đã nạp đầy đủ cả 5 phân hệ, cache dữ liệu, AI & PDF NVL 91 trang
    try:
        full_ram_mb = round(
            float(
                subprocess.check_output(
                    ["powershell", "-Command", f"(Get-Process -Id {os.getpid()}).WorkingSet64 / 1MB"],
                    text=True,
                    timeout=5,
                ).strip()
            ),
            1,
        )
    except Exception:
        full_ram_mb = None

    results["tests"]["test2_streamlit_apptest_5_modules"] = {
        "status": "PASS",
        "modules_passed": 5,
        "exceptions_count": 0,
        "timings_seconds": module_timings,
        "quick_demo_nvl_seconds": nvl_jump_s,
        "true_full_loaded_ram_mb": full_ram_mb,
    }

    # -----------------------------------------------------------------------
    # TEST 3: KHỞI CHẠY LIVE STREAMLIT SERVER TRÊN LOCALHOST:8505 & ĐO HTTP + RAM
    # -----------------------------------------------------------------------
    print("[Test 3/3] Khởi chạy thực tế `streamlit run` trên http://localhost:8505 và đo sức khỏe + RAM...")
    port = 8505
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(STAGE5_DIR / "app.py"),
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    t_srv = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    server_ready_s = None
    health_code = None
    root_code = None
    ram_mb = None

    try:
        with httpx.Client(timeout=5.0) as client:
            for _ in range(30):
                try:
                    rh = client.get(f"http://127.0.0.1:{port}/_stcore/health")
                    if rh.status_code == 200 and rh.text.strip().lower() == "ok":
                        server_ready_s = round(time.perf_counter() - t_srv, 2)
                        health_code = rh.status_code
                        r_root = client.get(f"http://127.0.0.1:{port}/")
                        root_code = r_root.status_code
                        break
                except Exception:
                    pass
                time.sleep(0.5)

        # Đo RAM tiến trình Streamlit trên Windows qua PowerShell Get-Process
        try:
            ps_out = subprocess.check_output(
                ["powershell", "-Command", f"(Get-Process -Id {proc.pid}).WorkingSet64 / 1MB"],
                text=True,
                timeout=5,
            ).strip()
            ram_mb = round(float(ps_out), 1)
        except Exception:
            ram_mb = None
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    assert health_code == 200 and root_code == 200, f"Live server health check failed: health={health_code}, root={root_code}"
    print(f"  -> Live Server HTTP 200 OK | Thời gian sẵn sàng: {server_ready_s}s | RAM tiến trình: {ram_mb} MB")

    results["tests"]["test3_live_streamlit_http_server"] = {
        "status": "PASS",
        "port_tested": port,
        "health_http_status": health_code,
        "root_http_status": root_code,
        "server_ready_seconds": server_ready_s,
        "process_ram_mb": ram_mb,
    }
    results["total_test_elapsed_seconds"] = round(time.perf_counter() - t0_all, 2)

    out_json = ROOT_DIR / "data_store/processed/stage5_deployment_test_log.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[HOÀN TẤT KIỂM THỬ GIAI ĐOẠN 5 — ALL 3 SUITES PASSED] ({results['total_test_elapsed_seconds']}s)")
    print(f"  -> Log lưu tại: {out_json}")


if __name__ == "__main__":
    main()
