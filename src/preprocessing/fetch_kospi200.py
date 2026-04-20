"""
fetch_kospi200.py
=================
Wave 1 / Part B — Download KOSPI200 constituent list and industry classification
from data.krx.co.kr for each year-end 2019-2023.

The KRX file download system uses a two-step OTP mechanism:
  Step 1: POST to GenerateOTP/generate.cmd  → receive OTP code (plain text)
  Step 2: POST to download_csv/download.cmd with {"code": otp} → CSV bytes

CONFIRMED BLOCKER (2026-04-17): data.krx.co.kr now returns "LOGOUT" for all
  OTP generation requests. As of 2026, the KRX data portal requires a registered
  KRX member login (KRX_ID + KRX_PW) to access the OTP download system.
  pykrx also confirmed this — it prints "KRX 로그인 실패" without credentials.
  Manual browser download or KRX member registration is required.

Manual download URL: https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd
  - Select index: KOSPI200, date: 연도말 기준일, click CSV export.

Outputs
-------
data/interim/kospi200_YYYY.csv      — per-year constituent list
data/interim/kospi200_industry.csv  — KRX industry classification snapshot (latest)
data/raw/download_log.json          — updated with each attempt

Columns in kospi200_YYYY.csv
-----------------------------
종목코드, 종목명, 업종명(KRX 세부업종), 시가총액(원)

Usage
-----
    python src/preprocessing/fetch_kospi200.py
"""

from __future__ import annotations

import hashlib
import io
import json
import time
from datetime import datetime, timezone
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
# KRX endpoints
# ---------------------------------------------------------------------------
KRX_OTP_URL = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
KRX_DOWNLOAD_URL = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
KRX_REFERER = "http://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd"

# Year-end trading dates (last trading day of December) for KOSPI200 snapshot.
# These are the dates when KRX publishes the constituent list snapshot.
YEAR_END_DATES = {
    2019: "20191230",
    2020: "20201230",
    2021: "20211230",
    2022: "20221229",
    2023: "20231228",
}

# OTP parameters for the KOSPI200 constituent list (지수구성종목 MDCSTAT00301)
# url field = the KRX "dbms" path that identifies the report
KOSPI200_OTP_PARAMS_TEMPLATE = {
    "mktId": "STK",
    "idxIndMidclssCd": "02",   # KOSPI200 index code
    "trdDd": "{trdDd}",        # filled per year
    "money": "1",
    "csvxls_isNo": "false",
    "name": "fileDown",
    "url": "dbms/MDC/STAT/standard/MDCSTAT00301",
}

# OTP parameters for KRX industry classification (업종분류)
INDUSTRY_OTP_PARAMS = {
    "mktId": "STK",
    "money": "1",
    "csvxls_isNo": "false",
    "name": "fileDown",
    "url": "dbms/MDC/STAT/standard/MDCSTAT03901",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": KRX_REFERER,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_log() -> list:
    if LOG_PATH.exists():
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(entries: list) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def krx_fetch_csv(
    session: requests.Session,
    otp_params: dict,
    description: str,
) -> Optional[bytes]:
    """
    Execute the KRX two-step OTP download and return raw CSV bytes.
    Returns None on failure (logs the error to stdout).
    """
    try:
        # Step 1: generate OTP
        r1 = session.post(KRX_OTP_URL, data=otp_params, timeout=30)
        r1.raise_for_status()
        otp = r1.text.strip()
        if not otp or len(otp) > 200:
            print(f"  [KRX OTP ERROR] Unexpected OTP response for {description}: {otp[:80]}")
            return None

        time.sleep(0.5)  # polite pause between OTP generation and download

        # Step 2: download CSV
        r2 = session.post(KRX_DOWNLOAD_URL, data={"code": otp}, timeout=60)
        r2.raise_for_status()

        # Sanity check: response should be CSV text, not HTML error page
        content = r2.content
        if b"<html" in content[:200].lower():
            print(f"  [KRX DL ERROR] Got HTML instead of CSV for {description}")
            return None

        return content

    except requests.exceptions.RequestException as exc:
        print(f"  [KRX REQUEST ERROR] {description}: {exc}")
        return None


def decode_krx_csv(raw: bytes) -> pd.DataFrame:
    """Decode KRX CSV bytes (euc-kr) into a DataFrame."""
    for enc in ("euc-kr", "cp949", "utf-8-sig", "utf-8"):
        try:
            text = raw.decode(enc)
            df = pd.read_csv(io.StringIO(text))
            return df
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    raise ValueError("Could not decode KRX CSV with any known encoding")


def standardize_kospi200_columns(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Normalise column names across years.
    KRX column names may vary year-to-year — we map to a stable schema.
    Unknown columns are kept as-is for the schema discovery step.
    """
    rename_map = {}

    # Common variants for stock code
    for col in df.columns:
        col_lower = col.strip().replace(" ", "")
        if "종목코드" in col_lower:
            rename_map[col] = "종목코드"
        elif "종목명" in col_lower and "종목코드" not in col_lower:
            rename_map[col] = "종목명"
        elif "업종명" in col_lower or "업종" in col_lower:
            rename_map[col] = "업종명"
        elif "시가총액" in col_lower:
            rename_map[col] = "시가총액"

    df = df.rename(columns=rename_map)
    df["year"] = year
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    log_entries = load_log()
    manual_queue: list[str] = []

    # --- Per-year KOSPI200 constituent download ---
    print("Fetching KOSPI200 constituent lists (2019-2023)...")
    for year, trd_dd in tqdm(YEAR_END_DATES.items(), desc="KOSPI200 years"):
        out_path = INTERIM_DIR / f"kospi200_{year}.csv"
        if out_path.exists():
            print(f"  [SKIP] {out_path.name} already exists")
            continue

        params = {k: v.replace("{trdDd}", trd_dd) for k, v in
                  KOSPI200_OTP_PARAMS_TEMPLATE.items()}
        raw = krx_fetch_csv(session, params, f"KOSPI200 {year}")

        if raw is None:
            manual_queue.append(f"KOSPI200 {year} ({trd_dd})")
            log_entries.append({
                "dataset_id": "krx_kospi200",
                "name": f"KOSPI200 constituent {year}",
                "target_path": str(out_path),
                "url": KRX_OTP_URL,
                "status": "failed",
                "sha256": None,
                "error": "OTP fetch returned None — see stdout",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
            continue

        try:
            df = decode_krx_csv(raw)
            df = standardize_kospi200_columns(df, year)

            # Schema discovery guard: warn on unexpected column count
            if len(df.columns) < 3:
                print(
                    f"  [SCHEMA WARN] {year}: only {len(df.columns)} columns "
                    f"detected — manual inspection required. Columns: {df.columns.tolist()}"
                )

            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            sha = sha256_bytes(raw)
            print(
                f"  [OK] {out_path.name}  rows={len(df)}  "
                f"cols={df.columns.tolist()}  sha256={sha[:16]}…"
            )
            log_entries.append({
                "dataset_id": "krx_kospi200",
                "name": f"KOSPI200 constituent {year}",
                "target_path": str(out_path),
                "url": KRX_DOWNLOAD_URL,
                "status": "success",
                "sha256": sha,
                "error": None,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            print(f"  [PARSE ERROR] {year}: {exc}")
            manual_queue.append(f"KOSPI200 {year} (parse error: {exc})")
            log_entries.append({
                "dataset_id": "krx_kospi200",
                "name": f"KOSPI200 constituent {year}",
                "target_path": str(out_path),
                "url": KRX_DOWNLOAD_URL,
                "status": "failed",
                "sha256": None,
                "error": str(exc),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })

        time.sleep(1)  # respectful crawl delay

    # --- Industry classification snapshot ---
    print("\nFetching KRX industry classification (업종분류)...")
    industry_path = INTERIM_DIR / "kospi200_industry.csv"
    if industry_path.exists():
        print(f"  [SKIP] {industry_path.name} already exists")
    else:
        raw_ind = krx_fetch_csv(session, INDUSTRY_OTP_PARAMS, "KRX industry classification")
        if raw_ind is None:
            manual_queue.append("KRX industry classification")
            log_entries.append({
                "dataset_id": "krx_industry",
                "name": "KRX 업종분류",
                "target_path": str(industry_path),
                "url": KRX_OTP_URL,
                "status": "failed",
                "sha256": None,
                "error": "OTP fetch returned None",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
        else:
            try:
                df_ind = decode_krx_csv(raw_ind)
                df_ind.to_csv(industry_path, index=False, encoding="utf-8-sig")
                sha_ind = sha256_bytes(raw_ind)
                print(
                    f"  [OK] {industry_path.name}  rows={len(df_ind)}  "
                    f"sha256={sha_ind[:16]}…"
                )
                log_entries.append({
                    "dataset_id": "krx_industry",
                    "name": "KRX 업종분류",
                    "target_path": str(industry_path),
                    "url": KRX_DOWNLOAD_URL,
                    "status": "success",
                    "sha256": sha_ind,
                    "error": None,
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as exc:
                print(f"  [PARSE ERROR] industry: {exc}")
                manual_queue.append(f"KRX industry classification (parse: {exc})")

    save_log(log_entries)
    print(f"\nLog saved: {LOG_PATH}")

    if manual_queue:
        print("\nMANUAL DOWNLOAD REQUIRED for the following:")
        for item in manual_queue:
            print(f"  - {item}")
        print(
            "\nFor KOSPI200 constituent lists, visit:\n"
            "  https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd\n"
            "  Select index=KOSPI200, date=year-end, download CSV.\n"
            "  Save to: data/interim/kospi200_YYYY.csv\n"
            "\nFor industry classification:\n"
            "  https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT03901.cmd\n"
            "  Save to: data/interim/kospi200_industry.csv"
        )


if __name__ == "__main__":
    main()
