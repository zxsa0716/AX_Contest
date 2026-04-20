"""
fetch_kau_price.py
==================
Wave 1 / Part C — Scrape daily KAU (Korea Allowance Unit) settlement prices
from ets.krx.co.kr for 2019-2023.

The ETS portal uses the same two-step OTP mechanism as the main KRX portal,
but with a different set of OTP parameters and a different Referer.

Primary endpoint discovery
--------------------------
ets.krx.co.kr/contents/ETS/03/03010000/ETS03010000.jsp  (시세조회 page)
Hidden form parameters from page inspection:
  - fromDd / toDd  : date range in YYYYMMDD
  - codeNm         : product name, e.g. "KAU" or blank for all
  - url            : "ETS/ets/dbms/ETS/03/ETS03010000/etsStat03010000"  (approximate)

Because the exact hidden-form parameters require browser JS execution to
observe, this script implements two strategies:

Strategy A (primary): Use the KRX OTP path with ETS-specific parameters.
Strategy B (fallback): Use pykrx if available (pip install pykrx).
Strategy C (last resort): Queue for manual CSV download from ets.krx.co.kr.

Outputs
-------
data/interim/kau_daily_2019_2023.csv  — daily OHLCV
data/interim/kau_annual.csv           — annual averages

Columns (kau_daily)
-------------------
date (YYYY-MM-DD), kau_close, kau_open, kau_high, kau_low, volume_tCO2eq

Usage
-----
    python src/preprocessing/fetch_kau_price.py
"""

from __future__ import annotations

import hashlib
import io
import json
import time
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
LOG_PATH = PROJECT_ROOT / "data" / "raw" / "download_log.json"

# ---------------------------------------------------------------------------
# ETS KRX endpoints
# ---------------------------------------------------------------------------
# CONFIRMED BLOCKER (2026-04-17): The ETS OTP endpoint
# https://ets.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd returns 404.
# The ETS portal appears to have moved or restructured its download API.
# The main KRX data portal (data.krx.co.kr) also requires login for all OTP
# requests (returns "LOGOUT" without credentials).
#
# Manual download: https://ets.krx.co.kr/contents/ETS/03/03010000/ETS03010000.jsp
#   Select product: KAU, set date range per year, click CSV button.
#   Save as: data/interim/kau_daily_YYYY.csv
#
# Alternative: k-re100.or.kr/doc/sub2_4_1.php may expose KAU price history.
ETS_OTP_URL = "https://ets.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
ETS_DOWNLOAD_URL = "https://ets.krx.co.kr/comm/fileDn/download_csv/download.cmd"
ETS_REFERER = "https://ets.krx.co.kr/contents/ETS/03/03010000/ETS03010000.jsp"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": ETS_REFERER,
}

# OTP parameters for KAU daily price query.
# fromDd/toDd will be filled per request.
KAU_OTP_PARAMS_TEMPLATE = {
    "name": "fileDown",
    "url": "ETS/ets/dbms/ETS/03/ETS03010000/etsStat03010000",
    "fromDd": "{fromDd}",
    "toDd": "{toDd}",
    "codeNm": "",
    "csvxls_isNo": "false",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_log() -> list:
    if LOG_PATH.exists():
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(entries: list) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_ets_csv(
    session: requests.Session,
    from_dd: str,
    to_dd: str,
) -> Optional[bytes]:
    """
    Execute the ETS OTP two-step download for a date range.
    Returns raw CSV bytes or None on failure.
    """
    params = {
        k: v.replace("{fromDd}", from_dd).replace("{toDd}", to_dd)
        for k, v in KAU_OTP_PARAMS_TEMPLATE.items()
    }
    try:
        r1 = session.post(ETS_OTP_URL, data=params, timeout=30)
        r1.raise_for_status()
        otp = r1.text.strip()
        if not otp or len(otp) > 200 or "<" in otp:
            print(f"  [ETS OTP ERROR] Unexpected response: {otp[:120]}")
            return None

        time.sleep(0.5)

        r2 = session.post(ETS_DOWNLOAD_URL, data={"code": otp}, timeout=60)
        r2.raise_for_status()

        content = r2.content
        if b"<html" in content[:200].lower():
            print(f"  [ETS DL ERROR] Got HTML instead of CSV for {from_dd}-{to_dd}")
            return None
        return content

    except requests.exceptions.RequestException as exc:
        print(f"  [ETS REQUEST ERROR] {from_dd}-{to_dd}: {exc}")
        return None


def decode_ets_csv(raw: bytes) -> pd.DataFrame:
    for enc in ("euc-kr", "cp949", "utf-8-sig", "utf-8"):
        try:
            text = raw.decode(enc)
            df = pd.read_csv(io.StringIO(text))
            return df
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    raise ValueError("Could not decode ETS CSV")


def standardize_kau_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map KRX ETS column names to the project standard schema.
    Column names vary across the portal; this mapping covers known variants.
    Any unmapped column is kept as-is and flagged in schema_warnings.
    """
    schema_warnings: list[str] = []
    rename_map: dict[str, str] = {}

    for col in df.columns:
        c = col.strip().replace(" ", "")
        if "날짜" in c or "일자" in c or "거래일" in c:
            rename_map[col] = "date"
        elif "종가" in c or "종가(원)" in c or "정산가" in c:
            rename_map[col] = "kau_close"
        elif "시가" in c:
            rename_map[col] = "kau_open"
        elif "고가" in c:
            rename_map[col] = "kau_high"
        elif "저가" in c:
            rename_map[col] = "kau_low"
        elif "거래량" in c:
            rename_map[col] = "volume_tCO2eq"
        elif col not in rename_map.values():
            schema_warnings.append(col)

    df = df.rename(columns=rename_map)

    if schema_warnings:
        print(
            f"  [SCHEMA WARN] Unmapped columns (kept as-is): {schema_warnings}. "
            "Director: manual schema review needed."
        )

    # Parse date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Ensure numeric price/volume columns
    for col in ["kau_close", "kau_open", "kau_high", "kau_low", "volume_tCO2eq"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            )

    return df


def try_pykrx_fallback(year: int) -> Optional[pd.DataFrame]:
    """
    Attempt to fetch KAU daily prices via pykrx if installed.
    pykrx.stock does not cover ETS; this is a no-op placeholder that returns
    None so the caller falls through to the manual queue.
    pykrx does NOT support emissions trading data as of 2024.
    """
    try:
        import pykrx  # noqa: F401
        # pykrx.stock covers equities only; ETS tickers are not supported.
        print(f"  [PYKRX] pykrx installed but ETS data not supported via pykrx.")
    except ImportError:
        pass
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    log_entries = load_log()
    all_frames: list[pd.DataFrame] = []
    manual_required = False

    # Download year by year to keep requests manageable
    print("Fetching KAU daily prices from ets.krx.co.kr (2019-2023)...")

    for year in tqdm(range(2019, 2024), desc="KAU years"):
        from_dd = f"{year}0101"
        to_dd = f"{year}1231"
        label = f"KAU {year}"

        raw = fetch_ets_csv(session, from_dd, to_dd)

        if raw is None:
            # Try pykrx fallback
            df_fallback = try_pykrx_fallback(year)
            if df_fallback is not None:
                all_frames.append(df_fallback)
                continue
            # Both paths failed
            manual_required = True
            log_entries.append({
                "dataset_id": "ets_kau_daily",
                "name": label,
                "target_path": str(INTERIM_DIR / "kau_daily_2019_2023.csv"),
                "url": ETS_OTP_URL,
                "status": "failed",
                "sha256": None,
                "error": "ETS OTP fetch failed; pykrx not applicable",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
            print(f"  [FAIL] {label} — queued for manual download")
            time.sleep(1)
            continue

        try:
            df = decode_ets_csv(raw)
            df = standardize_kau_columns(df)
            sha = sha256_bytes(raw)
            all_frames.append(df)
            print(
                f"  [OK] {label}  rows={len(df)}  sha256={sha[:16]}…"
            )
            log_entries.append({
                "dataset_id": "ets_kau_daily",
                "name": label,
                "target_path": str(INTERIM_DIR / "kau_daily_2019_2023.csv"),
                "url": ETS_DOWNLOAD_URL,
                "status": "success",
                "sha256": sha,
                "error": None,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            manual_required = True
            print(f"  [PARSE ERROR] {label}: {exc}")
            log_entries.append({
                "dataset_id": "ets_kau_daily",
                "name": label,
                "target_path": str(INTERIM_DIR / "kau_daily_2019_2023.csv"),
                "url": ETS_DOWNLOAD_URL,
                "status": "failed",
                "sha256": None,
                "error": str(exc),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })

        time.sleep(1)

    # --- Combine and save ---
    if all_frames:
        daily = pd.concat(all_frames, ignore_index=True)

        # Deduplicate
        if "date" in daily.columns:
            daily = daily.sort_values("date").drop_duplicates(subset=["date"])

        daily_path = INTERIM_DIR / "kau_daily_2019_2023.csv"
        daily.to_csv(daily_path, index=False, encoding="utf-8-sig")
        print(f"\n[SAVED] {daily_path}  total rows={len(daily)}")

        # Annual averages
        if "date" in daily.columns and "kau_close" in daily.columns:
            daily["year"] = pd.to_datetime(daily["date"], errors="coerce").dt.year
            annual = (
                daily.groupby("year")["kau_close"]
                .agg(["mean", "min", "max", "count"])
                .rename(columns={
                    "mean": "kau_close_avg",
                    "min": "kau_close_min",
                    "max": "kau_close_max",
                    "count": "trading_days",
                })
                .reset_index()
            )
            annual_path = INTERIM_DIR / "kau_annual.csv"
            annual.to_csv(annual_path, index=False, encoding="utf-8-sig")
            print(f"[SAVED] {annual_path}")
            print(annual.to_string(index=False))
    else:
        print("[WARN] No data frames collected — all years failed.")

    save_log(log_entries)
    print(f"\nLog saved: {LOG_PATH}")

    if manual_required:
        print(
            "\nMANUAL DOWNLOAD REQUIRED for one or more KAU years.\n"
            "Steps:\n"
            "  1. Open: https://ets.krx.co.kr/contents/ETS/03/03010000/ETS03010000.jsp\n"
            "  2. Set date range per year (e.g. 2019-01-01 to 2019-12-31).\n"
            "  3. Click CSV button to download.\n"
            "  4. Repeat for each missing year and merge into:\n"
            "     data/interim/kau_daily_2019_2023.csv\n"
            "  5. Compute SHA-256 and record in data/README.md."
        )


if __name__ == "__main__":
    main()
