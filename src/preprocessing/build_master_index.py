"""
Task 9: Build master company matching index.

Joins:
  - GIR 명세서 unique 법인명 (from gir_manifest_panel.parquet)
  - GIR 할당대상 unique 업체명 (from gir_allocated_panel.parquet)
  - K-ETS 사전할당 unique 업체명 (from kets_allocation_panel.parquet)
  - DART KOSPI full corp index (from kospi_all_corp_index.parquet)
  - 통합환경허가 기업명 (from integrated_permit_sites.parquet)

Matching strategy:
  1. Exact match on normalized name
  2. RapidFuzz token_sort_ratio >= 85

Output:
  data/interim/company_master_index.parquet
  data/interim/match_review.csv   (LOW/MEDIUM confidence rows for human review)
"""

import logging
import uuid
from pathlib import Path
from typing import Optional

import pandas as pd
from rapidfuzz import fuzz, process
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

FUZZY_THRESHOLD = 85
INTERIM = Path("data/interim")


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_parquet_safe(path: str | Path) -> Optional[pd.DataFrame]:
    p = Path(path)
    if not p.exists():
        logger.warning(f"File not found: {p}")
        return None
    df = pd.read_parquet(p)
    logger.info(f"Loaded {p.name}: {len(df):,} rows")
    return df


def deduplicate_names(df: pd.DataFrame, name_col: str, norm_col: str) -> pd.DataFrame:
    """Return unique normalized names with the most common canonical form."""
    return (
        df[[name_col, norm_col]]
        .dropna(subset=[norm_col])
        .drop_duplicates(subset=[norm_col])
        .rename(columns={name_col: "corp_name_src", norm_col: "name_normalized"})
        .reset_index(drop=True)
    )


def fuzzy_match_batch(
    query_names: list[str],
    choices: list[str],
    threshold: int = FUZZY_THRESHOLD,
) -> dict[str, Optional[tuple[str, float]]]:
    """
    For each query name, find the best match in choices using token_sort_ratio.
    Returns dict: query -> (best_choice, score) or None if below threshold.
    """
    results = {}
    for q in tqdm(query_names, desc="Fuzzy matching", mininterval=1.0):
        if not q:
            results[q] = None
            continue
        match = process.extractOne(q, choices, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
        results[q] = match  # (choice, score, idx) or None
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main(
    output_path: str = "data/interim/company_master_index.parquet",
    review_path: str = "data/interim/match_review.csv",
) -> pd.DataFrame:

    # ── Load all source DataFrames ────────────────────────────────────────────

    gir = load_parquet_safe(INTERIM / "gir_manifest_panel.parquet")
    allocated = load_parquet_safe(INTERIM / "gir_allocated_panel.parquet")
    kets = load_parquet_safe(INTERIM / "kets_allocation_panel.parquet")
    dart_kospi = load_parquet_safe(INTERIM / "kospi_all_corp_index.parquet")
    permit = load_parquet_safe(INTERIM / "integrated_permit_sites.parquet")
    kssb_pool = load_parquet_safe(INTERIM / "kssb_2028_candidate_pool.parquet")

    # ── Build seed universe from GIR manifest (primary source) ───────────────
    # GIR has most complete coverage for emission firms

    if gir is None:
        logger.error("GIR manifest not available — cannot build master index")
        return pd.DataFrame()

    # GIR: unique normalized names + years they appear
    gir_years = (
        gir.groupby("법인명_normalized")["year"]
        .apply(lambda x: sorted(x.dropna().unique().tolist()))
        .reset_index()
        .rename(columns={"법인명_normalized": "name_normalized", "year": "in_gir_years"})
    )
    gir_names = (
        gir.groupby("법인명_normalized")["법인명"]
        .first()
        .reset_index()
        .rename(columns={"법인명_normalized": "name_normalized", "법인명": "corp_name_gir"})
    )
    gir_verifier = (
        gir.groupby("법인명_normalized")["검증수행기관"]
        .apply(lambda x: x.dropna().any())
        .reset_index()
        .rename(columns={"법인명_normalized": "name_normalized", "검증수행기관": "has_verifier"})
    )

    # ── Build auxiliary sets for matching ────────────────────────────────────

    # DART KOSPI: normalized name
    if dart_kospi is not None:
        from consolidate_gir import normalize_corp_name
        dart_kospi["name_normalized"] = dart_kospi["corp_name"].apply(normalize_corp_name)
        dart_dict = dart_kospi.set_index("name_normalized")[["corp_code", "stock_code", "corp_name", "bizr_no"]].to_dict("index")
        dart_names = list(dart_dict.keys())
    else:
        dart_dict = {}
        dart_names = []

    # KSSB pool flags
    kssb_set = set()
    if kssb_pool is not None:
        from consolidate_gir import normalize_corp_name
        kssb_set = set(kssb_pool["corp_name"].apply(normalize_corp_name).tolist())

    # Allocated set
    alloc_set = set()
    if allocated is not None:
        alloc_set = set(allocated["업체명_normalized"].dropna().tolist())

    # K-ETS set (any phase)
    kets_phase_map: dict[str, list[int]] = {}
    if kets is not None:
        for norm, grp in kets.groupby("업체명_normalized"):
            kets_phase_map[norm] = sorted(grp["phase"].dropna().unique().tolist())
    kets_set = set(kets_phase_map.keys())

    # Permit set
    permit_set = set()
    if permit is not None:
        permit_set = set(permit["기업명_normalized"].dropna().tolist())

    # ── Start with GIR universe ───────────────────────────────────────────────
    universe = gir_years.merge(gir_names, on="name_normalized", how="left")
    universe = universe.merge(gir_verifier, on="name_normalized", how="left")

    # ── Step 1: Exact match each source against DART ──────────────────────────
    logger.info("Step 1: Exact match GIR universe against DART KOSPI...")
    universe["corp_code"] = universe["name_normalized"].map(
        lambda n: dart_dict.get(n, {}).get("corp_code")
    )
    universe["stock_code"] = universe["name_normalized"].map(
        lambda n: dart_dict.get(n, {}).get("stock_code")
    )
    universe["bizr_no"] = universe["name_normalized"].map(
        lambda n: dart_dict.get(n, {}).get("bizr_no")
    )
    universe["corp_name_dart"] = universe["name_normalized"].map(
        lambda n: dart_dict.get(n, {}).get("corp_name")
    )

    exact_matched = universe["corp_code"].notna().sum()
    logger.info(f"  Exact match hit: {exact_matched:,} / {len(universe):,}")

    # ── Step 2: Fuzzy match unmatched GIR names against DART ─────────────────
    if dart_names:
        logger.info("Step 2: Fuzzy match unmatched GIR names against DART KOSPI...")
        unmatched_mask = universe["corp_code"].isna()
        unmatched_norms = universe.loc[unmatched_mask, "name_normalized"].tolist()

        fuzzy_results = fuzzy_match_batch(unmatched_norms, dart_names)

        fuzzy_corp_code = []
        fuzzy_stock_code = []
        fuzzy_bizr_no = []
        fuzzy_score = []
        fuzzy_dart_name = []

        for norm in unmatched_norms:
            match = fuzzy_results.get(norm)
            if match:
                matched_norm, score, _ = match
                info = dart_dict.get(matched_norm, {})
                fuzzy_corp_code.append(info.get("corp_code"))
                fuzzy_stock_code.append(info.get("stock_code"))
                fuzzy_bizr_no.append(info.get("bizr_no"))
                fuzzy_score.append(score)
                fuzzy_dart_name.append(info.get("corp_name"))
            else:
                fuzzy_corp_code.append(None)
                fuzzy_stock_code.append(None)
                fuzzy_bizr_no.append(None)
                fuzzy_score.append(None)
                fuzzy_dart_name.append(None)

        fuzzy_df = pd.DataFrame({
            "name_normalized": unmatched_norms,
            "_fuzzy_corp_code": fuzzy_corp_code,
            "_fuzzy_stock_code": fuzzy_stock_code,
            "_fuzzy_bizr_no": fuzzy_bizr_no,
            "_fuzzy_score": fuzzy_score,
            "_fuzzy_dart_name": fuzzy_dart_name,
        })

        # Merge fuzzy results back on name_normalized
        universe = universe.merge(fuzzy_df, on="name_normalized", how="left")

        # Fill main columns from fuzzy where exact was missing
        for col_pair in [
            ("corp_code", "_fuzzy_corp_code"),
            ("stock_code", "_fuzzy_stock_code"),
            ("bizr_no", "_fuzzy_bizr_no"),
            ("corp_name_dart", "_fuzzy_dart_name"),
        ]:
            main_col, fuzzy_col = col_pair
            if fuzzy_col in universe.columns and main_col in universe.columns:
                mask = universe[main_col].isna() & universe[fuzzy_col].notna()
                universe.loc[mask, main_col] = universe.loc[mask, fuzzy_col]

        fuzzy_filled = universe["_fuzzy_corp_code"].notna().sum()
        logger.info(f"  Fuzzy match additional hits: {fuzzy_filled:,}")

    # ── Membership flags ──────────────────────────────────────────────────────
    universe["in_kospi"] = universe["corp_code"].notna()
    # KSSB pool: match by normalized name OR by corp_code
    kssb_corp_codes = set()
    if kssb_pool is not None and "corp_code" in kssb_pool.columns:
        kssb_corp_codes = set(kssb_pool["corp_code"].dropna().tolist())
    universe["in_kssb_pool"] = (
        universe["name_normalized"].isin(kssb_set) |
        universe["corp_code"].isin(kssb_corp_codes)
    )
    universe["in_gir_allocated"] = universe["name_normalized"].isin(alloc_set)
    universe["in_kets"] = universe["name_normalized"].isin(kets_set)
    universe["in_integrated_permit"] = universe["name_normalized"].isin(permit_set)

    # K-ETS phase flags
    universe["kets_phases"] = universe["name_normalized"].map(
        lambda n: kets_phase_map.get(n, [])
    )

    # ── Confidence assignment ─────────────────────────────────────────────────
    import math

    def assign_confidence(row) -> str:
        if not row["in_kospi"]:
            return "LOW"
        score = row.get("_fuzzy_score")
        # NaN means no fuzzy attempt was made → came from exact match
        if score is None or (isinstance(score, float) and math.isnan(score)):
            return "HIGH"  # Exact normalized-name match
        if score >= 90:
            return "HIGH"
        if score >= 85:
            return "MEDIUM"
        return "LOW"

    universe["match_confidence"] = universe.apply(assign_confidence, axis=1)

    # ── Canonical name ────────────────────────────────────────────────────────
    universe["corp_name_canonical"] = universe["corp_name_dart"].fillna(universe["corp_name_gir"])

    # ── Master ID ─────────────────────────────────────────────────────────────
    universe["master_id"] = [str(uuid.uuid4()) for _ in range(len(universe))]

    # ── Final column selection ────────────────────────────────────────────────
    keep_cols = [
        "master_id", "corp_name_canonical", "corp_name_gir", "corp_name_dart",
        "name_normalized", "corp_code", "stock_code", "bizr_no",
        "in_kospi", "in_kssb_pool",
        "in_gir_years", "in_gir_allocated", "in_kets", "kets_phases",
        "in_integrated_permit", "has_verifier",
        "match_confidence",
    ]
    if "_fuzzy_score" in universe.columns:
        keep_cols.append("_fuzzy_score")

    for c in keep_cols:
        if c not in universe.columns:
            universe[c] = None

    master = universe[keep_cols].reset_index(drop=True)

    # ── Save ──────────────────────────────────────────────────────────────────
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    master.to_parquet(output_path, index=False)
    logger.info(f"Saved master index ({len(master):,} rows) -> {output_path}")

    # Review queue: MEDIUM + LOW that are in KOSPI
    review = master[
        (master["match_confidence"].isin(["MEDIUM", "LOW"])) &
        master["in_kospi"]
    ][["master_id", "corp_name_gir", "corp_name_dart", "name_normalized",
       "corp_code", "match_confidence", "_fuzzy_score"] if "_fuzzy_score" in master.columns
      else ["master_id", "corp_name_gir", "corp_name_dart", "name_normalized",
             "corp_code", "match_confidence"]
    ].reset_index(drop=True)
    review.to_csv(review_path, index=False, encoding="utf-8-sig")
    logger.info(f"Review queue ({len(review):,} rows) -> {review_path}")

    # ── Summary ───────────────────────────────────────────────────────────────
    logger.info("\n=== MASTER INDEX SUMMARY ===")
    logger.info(f"Total unique firms in master: {len(master):,}")
    logger.info(f"In KOSPI (matched to DART): {master['in_kospi'].sum():,}")
    logger.info(f"In KSSB pool (assets>=2조): {master['in_kssb_pool'].sum():,}")
    logger.info(f"In GIR allocated: {master['in_gir_allocated'].sum():,}")
    logger.info(f"In K-ETS: {master['in_kets'].sum():,}")
    logger.info(f"In 통합환경허가: {master['in_integrated_permit'].sum():,}")
    logger.info(f"Has verifier: {master['has_verifier'].sum():,}")
    logger.info(f"Confidence distribution:\n{master['match_confidence'].value_counts().to_string()}")

    return master


if __name__ == "__main__":
    main()
