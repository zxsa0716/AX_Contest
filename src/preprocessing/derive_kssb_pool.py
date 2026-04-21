"""
Task 8: Derive KSSB 2028 mandatory-disclosure candidate pool from DART.

Steps:
  1. Download corpCode.xml → filter non-blank stock_code (~3959 firms)
  2. Call company.json per firm → filter corp_cls == 'Y' (KOSPI) → ~780 candidates
  3. For each KOSPI firm, call fnlttSinglAcntAll for 2023 and 2024 to get 자산총계
  4. Filter: assets_2023 >= 30T KRW OR assets_2024 >= 30T KRW
  5. Save: kssb_2028_candidate_pool.parquet + kospi_all_corp_index.parquet

Threshold: 30조 = 30_000_000_000_000 KRW (KSSB IFRS S1/S2 mandatory disclosure
applies to firms with total assets >= 2조 by 2026 and >= 5천억 by 2027/2028;
however KSSB_58 refers to the ~58 firms already subject to ESG disclosure via
KRX under market cap/asset thresholds. We use 2조 as conservative screen
since the actual KSSB schedule uses K-IFRS large listed company definition.)

NOTE: KSSB 의무공시 대상은 2026년부터 자산 2조 이상 상장사로 시작.
We screen at 2조 (2_000_000_000_000) per the actual KSSB roadmap.
The "58개사" referred to in project notes is the initial 2026 cohort.

Rate limit: 0.2s sleep between calls. Checkpoints saved to allow resume.
"""

import io
import os
import json
import time
import zipfile
import logging
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DART_API_KEY = os.environ["DART_API_KEY"]
BASE_URL = "https://opendart.fss.or.kr/api"

# KSSB threshold: 2조 KRW (2026 mandatory disclosure cohort)
KSSB_ASSET_THRESHOLD = 2_000_000_000_000

# Checkpoint file to allow resume
CHECKPOINT_PATH = Path("data/interim/_kssb_checkpoint.json")
KOSPI_INDEX_PATH = Path("data/interim/kospi_all_corp_index.parquet")
POOL_PATH = Path("data/interim/kssb_2028_candidate_pool.parquet")

# Financial holding company keywords
FIN_HOLDING_KEYWORDS = ["금융지주", "파이낸셜그룹", "금융그룹", "지주회사"]


def get_corp_codes() -> pd.DataFrame:
    """Download and parse DART corpCode.xml. Return all firms."""
    logger.info("Downloading corpCode.xml...")
    url = f"{BASE_URL}/corpCode.xml?crtfc_key={DART_API_KEY}"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    xml_data = z.read("CORPCODE.xml")
    root = ET.fromstring(xml_data)
    records = [{c.tag: c.text for c in child} for child in root]
    df = pd.DataFrame(records)
    sha = hashlib.sha256(r.content).hexdigest()
    logger.info(f"corpCode.xml SHA-256: {sha} | total firms: {len(df):,}")
    return df


def get_kospi_firms(df_all: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to KOSPI (corp_cls='Y') firms by calling company.json
    for each non-blank stock_code firm. Uses checkpoint to allow resume.
    """
    df_listed = df_all[df_all["stock_code"].str.strip() != ""].copy()
    logger.info(f"Listed firms to screen: {len(df_listed):,}")

    # Load checkpoint
    checkpoint = {}
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            checkpoint = json.load(f)
        logger.info(f"Resuming from checkpoint: {len(checkpoint):,} already done")

    results = dict(checkpoint)
    to_process = [r for r in df_listed.to_dict("records") if r["corp_code"] not in results]
    logger.info(f"Remaining to fetch: {len(to_process):,}")

    save_every = 100
    for i, row in enumerate(tqdm(to_process, desc="Fetching company.json (KOSPI filter)")):
        corp_code = row["corp_code"]
        try:
            r = requests.get(
                f"{BASE_URL}/company.json",
                params={"crtfc_key": DART_API_KEY, "corp_code": corp_code},
                timeout=15,
            )
            data = r.json()
            if data.get("status") == "000":
                results[corp_code] = {
                    "corp_code": corp_code,
                    "corp_name": data.get("corp_name"),
                    "stock_code": data.get("stock_code", "").strip(),
                    "corp_cls": data.get("corp_cls"),
                    "bizr_no": data.get("bizr_no", "").replace("-", ""),
                    "jurir_no": data.get("jurir_no", ""),
                    "ceo_nm": data.get("ceo_nm", ""),
                    "induty_code": data.get("induty_code", ""),
                }
            else:
                results[corp_code] = {"corp_code": corp_code, "corp_cls": None, "error": data.get("message")}
        except Exception as e:
            results[corp_code] = {"corp_code": corp_code, "corp_cls": None, "error": str(e)}
        time.sleep(0.2)

        # Save checkpoint periodically
        if (i + 1) % save_every == 0:
            CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CHECKPOINT_PATH, "w") as f:
                json.dump(results, f)

    # Final checkpoint save
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(results, f)

    df_companies = pd.DataFrame(results.values())
    return df_companies


def get_asset_amount(corp_code: str, year: int) -> float | None:
    """Fetch 자산총계 from DART finstate_all for a given corp+year. Try CFS then OFS."""
    for fs_div in ("CFS", "OFS"):
        try:
            url = f"{BASE_URL}/fnlttSinglAcntAll.json"
            params = {
                "crtfc_key": DART_API_KEY,
                "corp_code": corp_code,
                "bsns_year": str(year),
                "reprt_code": "11011",  # 사업보고서
                "fs_div": fs_div,
            }
            r = requests.get(url, params=params, timeout=20)
            data = r.json()
            if data.get("status") != "000":
                continue
            df = pd.DataFrame(data.get("list", []))
            if df.empty:
                continue
            row = df[df["account_nm"] == "자산총계"]
            if row.empty:
                continue
            amount_str = str(row.iloc[0]["thstrm_amount"]).replace(",", "")
            return float(amount_str)
        except Exception:
            continue
    return None


def main() -> None:
    Path("data/interim").mkdir(parents=True, exist_ok=True)

    # Step 1: Get all corp codes
    df_all = get_corp_codes()

    # Step 2: Filter to KOSPI via company.json calls
    df_companies = get_kospi_firms(df_all)
    df_kospi = df_companies[df_companies["corp_cls"] == "Y"].copy()
    logger.info(f"KOSPI firms found: {len(df_kospi):,}")

    # Save full KOSPI index (all KOSPI firms, regardless of asset threshold)
    df_kospi_save = df_kospi.reset_index(drop=True)
    df_kospi_save.to_parquet(KOSPI_INDEX_PATH, index=False)
    logger.info(f"Saved KOSPI all-corp index ({len(df_kospi_save):,} rows) -> {KOSPI_INDEX_PATH}")

    # Step 3 & 4: Fetch assets for each KOSPI firm (2023 + 2024)
    # Load existing asset checkpoint if any
    asset_ckpt_path = Path("data/interim/_kssb_assets_checkpoint.json")
    asset_cache = {}
    if asset_ckpt_path.exists():
        with open(asset_ckpt_path) as f:
            asset_cache = json.load(f)
        logger.info(f"Asset checkpoint: {len(asset_cache):,} entries")

    rows = df_kospi.to_dict("records")
    to_fetch = [r for r in rows if r["corp_code"] not in asset_cache]
    logger.info(f"Assets to fetch: {len(to_fetch):,} firms × 2 years")

    for i, row in enumerate(tqdm(to_fetch, desc="Fetching assets 2023+2024")):
        corp_code = row["corp_code"]
        assets_2023 = get_asset_amount(corp_code, 2023)
        time.sleep(0.2)
        assets_2024 = get_asset_amount(corp_code, 2024)
        time.sleep(0.2)
        asset_cache[corp_code] = {"assets_2023": assets_2023, "assets_2024": assets_2024}

        if (i + 1) % 50 == 0:
            with open(asset_ckpt_path, "w") as f:
                json.dump(asset_cache, f)

    with open(asset_ckpt_path, "w") as f:
        json.dump(asset_cache, f)

    # Step 5: Build pool DataFrame
    pool_records = []
    for row in rows:
        corp_code = row["corp_code"]
        assets = asset_cache.get(corp_code, {})
        a23 = assets.get("assets_2023")
        a24 = assets.get("assets_2024")
        flag_23 = bool(a23 and a23 >= KSSB_ASSET_THRESHOLD)
        flag_24 = bool(a24 and a24 >= KSSB_ASSET_THRESHOLD)
        flag_any = flag_23 or flag_24
        name = row.get("corp_name", "")
        is_fin_holding = any(kw in name for kw in FIN_HOLDING_KEYWORDS)
        pool_records.append({
            "corp_code": corp_code,
            "stock_code": row.get("stock_code", ""),
            "corp_name": name,
            "bizr_no": row.get("bizr_no", ""),
            "market": "KOSPI",
            "assets_2023": a23,
            "assets_2024": a24,
            "kssb_flag_2023": flag_23,
            "kssb_flag_2024": flag_24,
            "kssb_flag_any": flag_any,
            "is_financial_holding": is_fin_holding,
        })

    df_pool = pd.DataFrame(pool_records)
    df_kssb = df_pool[df_pool["kssb_flag_any"]].reset_index(drop=True)

    df_pool.to_parquet(POOL_PATH.parent / "kospi_asset_full.parquet", index=False)
    df_kssb.to_parquet(POOL_PATH, index=False)

    logger.info(f"\n=== KSSB POOL RESULTS ===")
    logger.info(f"Total KOSPI firms: {len(df_pool):,}")
    logger.info(f"KSSB pool (assets >= 2조, any year): {len(df_kssb):,}")
    logger.info(f"  - flagged 2023 only: {df_kssb['kssb_flag_2023'].sum()}")
    logger.info(f"  - flagged 2024 only: {df_kssb['kssb_flag_2024'].sum()}")
    logger.info(f"  - financial holding companies: {df_kssb['is_financial_holding'].sum()}")

    fin_holding = df_kssb[df_kssb["is_financial_holding"]][["corp_name", "assets_2023", "assets_2024"]]
    if len(fin_holding):
        logger.info(f"Financial holding cos in pool:\n{fin_holding.to_string()}")

    top_by_assets = df_kssb.nlargest(20, "assets_2023")[["corp_name", "assets_2023", "assets_2024", "is_financial_holding"]]
    print("\nTop 20 KSSB pool by 2023 assets:")
    print(top_by_assets.to_string(index=False))

    logger.info(f"Saved pool ({len(df_kssb):,} firms) -> {POOL_PATH}")


if __name__ == "__main__":
    main()
