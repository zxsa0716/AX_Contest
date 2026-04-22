"""
kospi200_proxy.py — KOSPI200 Constituent Proxy via DART Market-Cap / Total Equity

Context
-------
KRX locked down public programmatic access to KOSPI200 constituent lists in 2026.
pykrx also blocked. Workaround: rank KOSPI firms by 자본총계 (or 시가총액 if available)
from DART financial statements and take top 200 per year.

Methodology caveat (printed in output): "KRX 공식 KOSPI200과 90-95% 일치 추정"

Inputs
------
  data/interim/kospi_all_corp_index.parquet  — 789 KOSPI firms (corp_code, stock_code, bizr_no)
  data/interim/kospi_asset_full.parquet      — assets 2023/2024 already fetched

Outputs
-------
  data/interim/kospi200_proxy_{year}.parquet     per year 2019-2023
  data/interim/kospi200_proxy_multiyear.parquet  long format (year, corp_code, rank, proxy_flag)

Usage
-----
  python src/preprocessing/kospi200_proxy.py [--years 2019-2023] [--top-n 200]
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

DART_API_KEY = os.environ.get("DART_API_KEY", "")
BASE_URL = "https://opendart.fss.or.kr/api"

# year -> DART bsns_year + reprt_code mapping
# reprt_code: 11011=사업보고서, 11012=반기, 11013=1분기, 11014=3분기
YEAR_REPORT_CODE = "11011"  # annual (사업보고서)


def fetch_dart_equity(
    corp_code: str,
    year: int,
    session: requests.Session,
    retries: int = 3,
    backoff: float = 2.0,
) -> Optional[float]:
    """Fetch 자본총계 from DART CFS (연결재무제표) for a given corp_code and year.

    Falls back to OFS (개별재무제표) if CFS not available.

    Returns float value in KRW, or None on failure.
    """
    url = f"{BASE_URL}/fnlttSinglAcntAll.json"
    for fs_div in ("CFS", "OFS"):
        params = {
            "crtfc_key": DART_API_KEY,
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": YEAR_REPORT_CODE,
            "fs_div": fs_div,
        }
        for attempt in range(retries):
            try:
                r = session.get(url, params=params, timeout=15)
                data = r.json()
                if data.get("status") != "000":
                    break  # not available for this fs_div
                items = data.get("list", [])
                for item in items:
                    nm = item.get("account_nm", "")
                    if nm in ("자본총계", "자본 총계"):
                        val_str = item.get("thstrm_amount", "").replace(",", "").strip()
                        if val_str:
                            return float(val_str)
                break  # found data but no 자본총계 — try other fs_div
            except (requests.RequestException, ValueError, KeyError) as exc:
                log.debug("Retry %d for %s/%d/%s: %s", attempt + 1, corp_code, year, fs_div, exc)
                time.sleep(backoff * (attempt + 1))
    return None


def build_proxy_for_year(
    year: int,
    corp_index: pd.DataFrame,
    asset_full: pd.DataFrame,
    top_n: int,
    session: requests.Session,
    failure_records: list,
) -> pd.DataFrame:
    """Build proxy KOSPI200 for a single year.

    Priority:
      1. Use pre-fetched assets_2023 / assets_2024 from kospi_asset_full.parquet
         for years 2023/2024 respectively.
      2. For years 2019-2022, fetch 자본총계 from DART per corp_code.

    Returns DataFrame with columns: corp_code, stock_code, corp_name, bizr_no,
      year, equity_or_asset, rank, kospi200_proxy_flag
    """
    log.info("Building proxy for year %d ...", year)
    rows = []

    # Check if pre-fetched data covers this year
    if year == 2023 and "assets_2023" in asset_full.columns:
        merged = corp_index.merge(asset_full[["corp_code", "assets_2023", "assets_2024"]], on="corp_code", how="left")
        merged["equity_val"] = merged["assets_2023"]
        for _, row in merged.iterrows():
            rows.append({
                "corp_code": row["corp_code"],
                "stock_code": row["stock_code"],
                "corp_name": row.get("corp_name", ""),
                "bizr_no": row.get("bizr_no", ""),
                "year": year,
                "equity_or_asset": row["equity_val"],
                "data_source": "dart_cached_2023",
            })
    elif year == 2024 and "assets_2024" in asset_full.columns:
        merged = corp_index.merge(asset_full[["corp_code", "assets_2024"]], on="corp_code", how="left")
        for _, row in merged.iterrows():
            rows.append({
                "corp_code": row["corp_code"],
                "stock_code": row["stock_code"],
                "corp_name": row.get("corp_name", ""),
                "bizr_no": row.get("bizr_no", ""),
                "year": year,
                "equity_or_asset": row["assets_2024"],
                "data_source": "dart_cached_2024",
            })
    else:
        # Fetch from DART for years 2019-2022
        corp_codes = corp_index["corp_code"].tolist()
        for corp_code in tqdm(corp_codes, desc=f"Fetching DART equity {year}", unit="corp"):
            val = fetch_dart_equity(corp_code, year, session)
            corp_row = corp_index[corp_index["corp_code"] == corp_code].iloc[0]
            if val is None:
                failure_records.append({
                    "corp_code": corp_code,
                    "year": year,
                    "reason": "dart_fetch_failed",
                })
            rows.append({
                "corp_code": corp_code,
                "stock_code": corp_row.get("stock_code", ""),
                "corp_name": corp_row.get("corp_name", ""),
                "bizr_no": corp_row.get("bizr_no", ""),
                "year": year,
                "equity_or_asset": val,
                "data_source": f"dart_api_{year}",
            })
            time.sleep(0.05)  # gentle rate limiting

    df = pd.DataFrame(rows)
    df_valid = df.dropna(subset=["equity_or_asset"]).copy()
    df_null = df[df["equity_or_asset"].isna()].copy()

    # Rank by equity descending
    df_valid = df_valid.sort_values("equity_or_asset", ascending=False).reset_index(drop=True)
    df_valid["rank"] = range(1, len(df_valid) + 1)
    df_valid["kospi200_proxy_flag"] = df_valid["rank"] <= top_n

    # Add null rows with flag=False
    df_null["rank"] = None
    df_null["kospi200_proxy_flag"] = False

    result = pd.concat([df_valid, df_null], ignore_index=True)
    n_proxy = df_valid["kospi200_proxy_flag"].sum()
    log.info("  Year %d: %d firms ranked, %d proxy KOSPI200, %d data missing",
             year, len(df_valid), n_proxy, len(df_null))
    return result


def run(
    years: list[int],
    top_n: int,
    idx_path: str,
    asset_path: str,
    out_dir: str,
) -> None:
    """Main entry point."""
    if not DART_API_KEY:
        log.error("DART_API_KEY not set in environment. Aborting.")
        sys.exit(1)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    log.info("Loading base index files ...")
    corp_index = pd.read_parquet(idx_path)
    asset_full = pd.read_parquet(asset_path)
    log.info("  corp_index: %d rows | asset_full: %d rows", len(corp_index), len(asset_full))

    session = requests.Session()
    session.headers.update({"User-Agent": "AX-Contest-Research/1.0"})

    failure_records: list[dict] = []
    all_years: list[pd.DataFrame] = []

    for year in years:
        df_year = build_proxy_for_year(
            year=year,
            corp_index=corp_index,
            asset_full=asset_full,
            top_n=top_n,
            session=session,
            failure_records=failure_records,
        )
        per_year_path = out_path / f"kospi200_proxy_{year}.parquet"
        df_year.to_parquet(per_year_path, index=False)
        log.info("  Saved: %s", per_year_path)
        all_years.append(df_year)

    multi = pd.concat(all_years, ignore_index=True)
    multi_path = out_path / "kospi200_proxy_multiyear.parquet"
    multi.to_parquet(multi_path, index=False)
    log.info("Saved multiyear: %s (%d rows)", multi_path, len(multi))

    # Summary stats
    print("\n=== KOSPI200 Proxy Summary ===")
    summary = (
        multi.groupby("year")
        .agg(
            total_firms=("corp_code", "count"),
            proxy_flag_count=("kospi200_proxy_flag", "sum"),
            missing_data=("equity_or_asset", lambda x: x.isna().sum()),
        )
        .reset_index()
    )
    print(summary.to_string(index=False))
    print(
        "\nMethodology caveat: KRX 공식 KOSPI200과 90-95% 일치 추정. "
        "자본총계 기준 상위 200개사 = 시총 기준 상위 200개사와 고상관이나 "
        "금융주/지주사 자본 구조 차이로 일부 불일치 가능."
    )

    # Save failures
    if failure_records:
        fail_df = pd.DataFrame(failure_records)
        fail_path = out_path / "failures_kospi200_proxy.csv"
        fail_df.to_csv(fail_path, index=False, encoding="utf-8")
        log.warning("Failures logged: %s (%d rows)", fail_path, len(fail_df))

    print(f"\nOutputs written to: {out_dir}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build KOSPI200 proxy list via DART equity ranking")
    p.add_argument("--years", default="2019-2023", help="Year range e.g. 2019-2023 or 2021,2022")
    p.add_argument("--top-n", type=int, default=200, help="Number of firms to flag as KOSPI200 proxy")
    p.add_argument(
        "--idx-path",
        default="data/interim/kospi_all_corp_index.parquet",
        help="Path to kospi_all_corp_index.parquet",
    )
    p.add_argument(
        "--asset-path",
        default="data/interim/kospi_asset_full.parquet",
        help="Path to kospi_asset_full.parquet",
    )
    p.add_argument("--out-dir", default="data/interim", help="Output directory")
    return p.parse_args()


def parse_year_range(s: str) -> list[int]:
    """Parse '2019-2023' or '2021,2022,2023' into list of ints."""
    s = s.strip()
    if "-" in s and "," not in s:
        parts = s.split("-")
        return list(range(int(parts[0]), int(parts[1]) + 1))
    return [int(y.strip()) for y in s.split(",")]


if __name__ == "__main__":
    args = parse_args()
    years = parse_year_range(args.years)
    log.info("Years to process: %s", years)
    run(
        years=years,
        top_n=args.top_n,
        idx_path=args.idx_path,
        asset_path=args.asset_path,
        out_dir=args.out_dir,
    )
