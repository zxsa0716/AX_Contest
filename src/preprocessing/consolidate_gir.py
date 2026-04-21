"""
Task 1: Consolidate GIR 명세서 (온실가스 에너지 목표관리 명세서) 7 years (2018-2024).

Input:  data/GIR명세서/*.xls  (7 files)
Output: data/interim/gir_manifest_panel.parquet

Schema (uniform across all years):
  번호, 관장기관, 법인명, 대상년도, 지정구분, 지정업종(목표)/<br />계획업종(할당),
  온실가스 배출량(tCO₂eq), 에너지 사용량(TJ), 검증수행기관, 비고
"""

import re
import glob
import logging
import hashlib
from pathlib import Path

import pandas as pd
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Canonical output column names
COL_MAP = {
    "번호": "row_no",
    "관장기관": "관장기관",
    "법인명": "법인명",
    "대상년도": "year_reported",
    "지정구분": "지정구분",
    "지정업종(목표)/<br />계획업종(할당)": "지정업종",
    "온실가스 배출량(tCO₂eq)": "scope1_tco2eq",
    "에너지 사용량(TJ)": "energy_tj",
    "검증수행기관": "검증수행기관",
    "비고": "비고",
}

PREFIXES_TO_STRIP = [
    "주식회사", "㈜", "(주)", "(유)", "(재)", "(사)", "(사단법인)",
    "유한회사", "사단법인", "재단법인",
]


def normalize_corp_name(name: str) -> str:
    """Lowercase, remove whitespace and common legal-form prefixes/suffixes."""
    if not isinstance(name, str):
        return ""
    s = name.strip()
    # Remove trailing/leading legal forms
    for pfx in PREFIXES_TO_STRIP:
        s = re.sub(r"^\s*" + re.escape(pfx) + r"\s*", "", s)
        s = re.sub(r"\s*" + re.escape(pfx) + r"\s*$", "", s)
    # Remove all whitespace and lower
    s = re.sub(r"\s+", "", s).lower()
    return s


def load_one_year(path: str) -> pd.DataFrame:
    """Load a single GIR 명세서 xls file and return a cleaned DataFrame."""
    path = Path(path)
    # Parse year from filename  e.g. 명세서 주요정보_2021년.xls
    m = re.search(r"_(\d{4})년", path.name)
    year = int(m.group(1)) if m else None

    try:
        df = pd.read_excel(path, dtype=str)
    except Exception as e:
        logger.error(f"Failed to read {path}: {e}")
        return pd.DataFrame()

    # Rename columns
    df = df.rename(columns={c: COL_MAP.get(c, c) for c in df.columns})

    # Inject year from filename (overrides possibly dirty 대상년도 column)
    df["year"] = year
    df["file_source"] = str(path)

    # Numeric coercion
    for col in ("scope1_tco2eq", "energy_tj"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.replace(",", "", regex=False), errors="coerce")

    # Strip whitespace on string columns
    for col in ("법인명", "관장기관", "지정구분", "지정업종", "검증수행기관"):
        if col in df.columns:
            df[col] = df[col].str.strip()

    # Derived normalized name
    df["법인명_normalized"] = df["법인명"].apply(normalize_corp_name)

    return df


def main(
    input_dir: str = "data/GIR명세서",
    output_path: str = "data/interim/gir_manifest_panel.parquet",
) -> pd.DataFrame:
    files = sorted(glob.glob(f"{input_dir}/*.xls"))
    logger.info(f"Found {len(files)} GIR 명세서 files")

    frames = []
    for f in tqdm(files, desc="Loading GIR 명세서"):
        df = load_one_year(f)
        if not df.empty:
            frames.append(df)

    panel = pd.concat(frames, ignore_index=True)

    # Keep only rows with actual company data
    panel = panel[panel["법인명"].notna() & (panel["법인명"] != "")]

    # Ensure final column order
    final_cols = [
        "year", "법인명", "법인명_normalized", "관장기관",
        "지정구분", "지정업종", "scope1_tco2eq", "energy_tj",
        "검증수행기관", "file_source",
    ]
    for c in final_cols:
        if c not in panel.columns:
            panel[c] = None
    panel = panel[final_cols]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(panel):,} rows -> {output_path}")

    # ---- Summary stats ----
    logger.info("=== SUMMARY ===")
    logger.info(f"Total rows: {len(panel):,}")
    logger.info(f"Unique 법인명_normalized: {panel['법인명_normalized'].nunique():,}")
    logger.info(f"Years covered: {sorted(panel['year'].dropna().unique().tolist())}")
    has_verifier = panel["검증수행기관"].notna() & (panel["검증수행기관"] != "")
    logger.info(f"Rows with 검증수행기관 non-null: {has_verifier.sum():,}")

    top20 = (
        panel[panel["year"] == 2023]
        .nlargest(20, "scope1_tco2eq")[["법인명", "scope1_tco2eq", "지정업종"]]
    )
    print("\nTop 20 largest emitters in 2023:")
    print(top20.to_string(index=False))

    return panel


if __name__ == "__main__":
    main()
