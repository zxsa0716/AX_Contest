"""Build gold_sites.csv: site-level lat/lon for 24 Gold companies.

Data sources (priority order per firm):
  1. GIR 할당대상업체 지정현황 (gir_allocated_panel.parquet) — 소재지 column
  2. 통합환경허가 (integrated_permit_sites.parquet) — 주소 column
  3. manual_required — no address found in any automated source

Geocoder: VWorld API 2.0 (국토교통부).
  - ROAD type first, PARCEL fallback.
  - 0.5s sleep between calls to stay within rate limits.

Output: data/interim/gold_sites.csv
Columns:
  company_id, corp_name, stock_code, bizr_no,
  site_id, address, lat, lon,
  industry, geocode_source

Failures: data/interim/failures_gold_sites.csv
"""
from __future__ import annotations

import os
import re
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

VWORLD_ENDPOINT = "https://api.vworld.kr/req/address"
SLEEP_SEC = 0.5  # between geocoding calls to avoid 429


# ---------------------------------------------------------------------------
# Industry mapping: Korean 업종 description -> canonical label
# ---------------------------------------------------------------------------
INDUSTRY_MAP: list[tuple[str, str]] = [
    # steel / iron
    ("제철", "steel"),
    ("철강", "steel"),
    ("1차 철강", "steel"),
    # petrochem
    ("석유화학", "petrochem"),
    ("화학 물질", "petrochem"),
    ("화약", "petrochem"),
    ("축전지", "petrochem"),
    # power / coal / gas
    ("발전", "power_coal"),
    ("송전", "power_coal"),
    ("배전", "power_coal"),
    # cement (none in gold24 but keep for robustness)
    ("시멘트", "cement"),
    # semiconductor / electronics
    ("전자집적회로", "semiconductor"),
    ("액정", "semiconductor"),
    ("반도체", "semiconductor"),
    # finance / service
    ("보험", "finance"),
    ("은행", "finance"),
    ("통신", "finance"),
    ("포털", "finance"),
    # automotive / transportation
    ("자동차", "other"),
    ("항공", "other"),
]


def map_industry(업종: str) -> str:
    """Map Korean 업종 string to canonical industry label."""
    if not isinstance(업종, str):
        return "other"
    for keyword, label in INDUSTRY_MAP:
        if keyword in 업종:
            return label
    return "other"


# ---------------------------------------------------------------------------
# Name normalisation (mirrors entity-matcher logic)
# ---------------------------------------------------------------------------
_STOP = re.compile(
    r"[\s\(\)\（\）\,\.\-\/]|"
    r"(주식회사|주|유|co|ltd|corp|inc|holdings|보험|은행)",
    re.IGNORECASE,
)


def norm_name(s: str) -> str:
    s = str(s).lower()
    s = _STOP.sub("", s)
    return s.strip()


# ---------------------------------------------------------------------------
# VWorld geocoder
# ---------------------------------------------------------------------------
def geocode_vworld(
    address: str,
    api_key: str,
    addr_type: str = "ROAD",
) -> Optional[tuple[float, float]]:
    """Return (lat, lon) in WGS84 or None if lookup fails.

    VWorld API 2.0: request=GetCoord, crs=EPSG:4326
      x = longitude, y = latitude.
    """
    params = {
        "service": "address",
        "request": "GetCoord",
        "version": "2.0",
        "crs": "EPSG:4326",
        "address": address,
        "format": "json",
        "type": addr_type,
        "key": api_key,
    }
    try:
        r = requests.get(VWORLD_ENDPOINT, params=params, timeout=15)
        r.raise_for_status()
        payload = r.json().get("response", {})
        if payload.get("status") != "OK":
            return None
        point = payload.get("result", {}).get("point", {})
        return float(point["y"]), float(point["x"])
    except Exception:
        return None


def geocode_with_fallback(
    address: str,
    api_key: str,
) -> Optional[tuple[float, float]]:
    """Try ROAD type first, then PARCEL."""
    time.sleep(SLEEP_SEC)
    result = geocode_vworld(address, api_key, addr_type="ROAD")
    if result is not None:
        return result
    time.sleep(SLEEP_SEC)
    result = geocode_vworld(address, api_key, addr_type="PARCEL")
    return result


# ---------------------------------------------------------------------------
# HQ addresses for financial / service companies not in GIR allocated
# (중소기업은행 — IBK) and firms not matched by name
# ---------------------------------------------------------------------------
MANUAL_HQ_ADDRESSES: dict[str, dict] = {
    # Keys stored as zero-padded 6-digit strings AND unpadded to handle both forms
    "024110": {  # 중소기업은행 (IBK)
        "address": "서울특별시 중구 을지로 79",
        "industry": "finance",
        "geocode_source": "manual_hq",
    },
    "24110": {  # unpadded fallback
        "address": "서울특별시 중구 을지로 79",
        "industry": "finance",
        "geocode_source": "manual_hq",
    },
}


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------
def build_gold_sites(
    gold_csv: str,
    gir_allocated_parquet: str,
    integrated_permit_parquet: str,
    out_csv: str,
    failures_csv: str,
    api_key: str,
) -> pd.DataFrame:
    """Build site-level geocoded dataframe for Gold 24 companies.

    Args:
        gold_csv: path to data/interim/gold_corps.csv
        gir_allocated_parquet: path to data/interim/gir_allocated_panel.parquet
        integrated_permit_parquet: path to data/interim/integrated_permit_sites.parquet
        out_csv: output path for gold_sites.csv
        failures_csv: path to write geocoding failures
        api_key: VWorld REST API key

    Returns:
        DataFrame with site records.
    """
    # --- load inputs ---
    gold = pd.read_csv(gold_csv)
    # deduplicate (LG디스플레이 appears twice in source)
    gold = gold.drop_duplicates(subset=["stock_code"]).reset_index(drop=True)
    print(f"[build_gold_sites] Gold firms (deduped): {len(gold)}")

    gir = pd.read_parquet(gir_allocated_parquet)
    permit = pd.read_parquet(integrated_permit_parquet)

    # normalise name columns for matching
    gir["_norm"] = gir["업체명_normalized"].apply(norm_name)
    permit["_norm"] = permit["기업명_normalized"].apply(norm_name)

    rows: list[dict] = []
    failures: list[dict] = []

    for _, corp in gold.iterrows():
        company_id = str(corp["corp_code"])
        corp_name = str(corp["corp_name"])
        stock_code = str(corp["stock_code"])
        bizr_no = str(corp["bizr_no"])
        corp_norm = norm_name(corp_name)

        # ---- 1. GIR allocated: match by normalised name ----
        gir_matches = gir[gir["_norm"] == corp_norm]
        if gir_matches.empty:
            # try substring match (e.g. "포스코홀딩스" in "포스코홀딩스 주식회사")
            gir_matches = gir[gir["업체명_normalized"].str.contains(
                corp_norm[:4], na=False, case=False)]

        sites_found: list[dict] = []

        if not gir_matches.empty:
            for _, gm in gir_matches.iterrows():
                addr = str(gm["소재지"]).strip()
                업종 = str(gm.get("업종", ""))
                industry = map_industry(업종)
                sites_found.append({
                    "address": addr,
                    "industry": industry,
                    "geocode_source": "vworld",
                    "_raw_업종": 업종,
                })

        # ---- 2. integrated permit fallback (only if GIR found nothing) ----
        if not sites_found:
            permit_matches = permit[permit["_norm"] == corp_norm]
            if permit_matches.empty:
                permit_matches = permit[permit["기업명_normalized"].str.contains(
                    corp_norm[:4], na=False, case=False)]
            for _, pm in permit_matches.iterrows():
                addr = str(pm["주소"]).strip()
                업종 = str(pm.get("업종", ""))
                industry = map_industry(업종)
                sites_found.append({
                    "address": addr,
                    "industry": industry,
                    "geocode_source": "integrated_permit",
                    "_raw_업종": 업종,
                })

        # ---- 3. manual HQ address for financial companies ----
        if not sites_found and stock_code in MANUAL_HQ_ADDRESSES:
            entry = MANUAL_HQ_ADDRESSES[stock_code]
            sites_found.append({
                "address": entry["address"],
                "industry": entry["industry"],
                "geocode_source": entry["geocode_source"],
                "_raw_업종": "",
            })

        # ---- 4. mark manual_required if nothing found ----
        if not sites_found:
            print(f"  [no address] {corp_name} ({stock_code}) -> manual_required")
            failures.append({
                "company_id": company_id,
                "corp_name": corp_name,
                "stock_code": stock_code,
                "bizr_no": bizr_no,
                "reason": "no_address_found",
            })
            rows.append({
                "company_id": company_id,
                "corp_name": corp_name,
                "stock_code": stock_code,
                "bizr_no": bizr_no,
                "site_id": f"{stock_code}_0001",
                "address": "",
                "lat": None,
                "lon": None,
                "industry": "other",
                "geocode_source": "manual_required",
            })
            continue

        # ---- 5. geocode each site ----
        seq = 1
        for site in sites_found:
            addr = site["address"]
            site_id = f"{stock_code}_{seq:04d}"
            print(f"  [{corp_name}] geocoding site {seq}: {addr[:60]}")
            coords = geocode_with_fallback(addr, api_key)
            if coords is not None:
                lat, lon = coords
                geo_src = site["geocode_source"]
                print(f"    -> lat={lat:.5f}, lon={lon:.5f} [{geo_src}]")
            else:
                lat = lon = None
                geo_src = "vworld_failed"
                print(f"    -> FAILED")
                failures.append({
                    "company_id": company_id,
                    "corp_name": corp_name,
                    "stock_code": stock_code,
                    "bizr_no": bizr_no,
                    "site_id": site_id,
                    "address": addr,
                    "reason": "geocode_api_failure",
                })

            rows.append({
                "company_id": company_id,
                "corp_name": corp_name,
                "stock_code": stock_code,
                "bizr_no": bizr_no,
                "site_id": site_id,
                "address": addr,
                "lat": lat,
                "lon": lon,
                "industry": site["industry"],
                "geocode_source": geo_src if coords else "vworld_failed",
            })
            seq += 1

    # --- write outputs ---
    out_df = pd.DataFrame(rows)
    out_df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\n[build_gold_sites] Wrote {len(out_df)} rows -> {out_csv}")

    fail_df = pd.DataFrame(failures)
    fail_df.to_csv(failures_csv, index=False, encoding="utf-8")
    if not fail_df.empty:
        print(f"[build_gold_sites] {len(fail_df)} failures -> {failures_csv}")

    # --- summary ---
    total = len(out_df)
    geocoded = out_df["lat"].notna().sum()
    manual_req = (out_df["geocode_source"] == "manual_required").sum()
    vworld_failed = (out_df["geocode_source"] == "vworld_failed").sum()
    print(f"\n--- Summary ---")
    print(f"  Total site records  : {total}")
    print(f"  Geocoded (lat+lon)  : {geocoded}")
    print(f"  VWorld failed       : {vworld_failed}")
    print(f"  manual_required     : {manual_req}")

    return out_df


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Build gold_sites.csv for Gold 24 firms.")
    ap.add_argument(
        "--gold-csv",
        default=str(PROJECT_ROOT / "data" / "interim" / "gold_corps.csv"),
    )
    ap.add_argument(
        "--gir-allocated",
        default=str(PROJECT_ROOT / "data" / "interim" / "gir_allocated_panel.parquet"),
    )
    ap.add_argument(
        "--integrated-permit",
        default=str(PROJECT_ROOT / "data" / "interim" / "integrated_permit_sites.parquet"),
    )
    ap.add_argument(
        "--out-csv",
        default=str(PROJECT_ROOT / "data" / "interim" / "gold_sites.csv"),
    )
    ap.add_argument(
        "--failures-csv",
        default=str(PROJECT_ROOT / "data" / "interim" / "failures_gold_sites.csv"),
    )
    args = ap.parse_args()

    api_key = os.environ.get("VWORLD_API_KEY")
    if not api_key:
        print("ERROR: VWORLD_API_KEY not set in .env", file=sys.stderr)
        return 1

    build_gold_sites(
        gold_csv=args.gold_csv,
        gir_allocated_parquet=args.gir_allocated,
        integrated_permit_parquet=args.integrated_permit,
        out_csv=args.out_csv,
        failures_csv=args.failures_csv,
        api_key=api_key,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
