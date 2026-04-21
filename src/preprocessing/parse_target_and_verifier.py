"""
Task 3 & 4: Parse GIR 목표관리업체 + GIR 검증기관.

Task 3 Output: data/interim/gir_target_panel.parquet
Task 4 Output: data/interim/gir_verifier_list.parquet
"""

import glob
import logging
import re
from pathlib import Path

import pandas as pd

from consolidate_gir import normalize_corp_name

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ── Task 3: GIR 목표관리업체 ──────────────────────────────────────────────────

def parse_target(
    input_dir: str = "data/GIR목표관리",
    output_path: str = "data/interim/gir_target_panel.parquet",
) -> pd.DataFrame:
    """
    The xlsx has merged cells in rows 0-2 (title + blank + header).
    Actual header row is row index 3 (0-based); data starts at row 4.
    """
    files = glob.glob(f"{input_dir}/*.xlsx")
    if not files:
        logger.error(f"No xlsx in {input_dir}")
        return pd.DataFrame()

    path = files[0]
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df_raw = pd.read_excel(path, header=None, dtype=str)

    logger.info(f"Raw shape: {df_raw.shape}")

    # Find the header row: look for a row where '순번' or '지정연도' appears
    header_row_idx = None
    for i in range(min(10, len(df_raw))):
        row_vals = df_raw.iloc[i].fillna("").astype(str).tolist()
        if any(v in ("순번", "지정연도", "관리업체명") for v in row_vals):
            header_row_idx = i
            break

    if header_row_idx is None:
        logger.error("Cannot locate header row in 목표관리 xlsx")
        return pd.DataFrame()

    logger.info(f"Header row index: {header_row_idx}")
    headers = df_raw.iloc[header_row_idx].fillna("").astype(str).str.strip().tolist()
    df = df_raw.iloc[header_row_idx + 1:].copy()
    df.columns = headers
    df = df.reset_index(drop=True)

    # Drop empty rows (where 순번 or 관리업체명 is blank)
    key_col = next((c for c in ("관리업체명", "업체명", "법인명") if c in df.columns), None)
    if key_col:
        df = df[df[key_col].notna() & (df[key_col].str.strip() != "")]

    # Normalize company name
    if key_col:
        df["업체명_normalized"] = df[key_col].apply(normalize_corp_name)

    logger.info(f"Parsed shape: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(df):,} rows -> {output_path}")
    return df


# ── Task 4: GIR 검증기관 ──────────────────────────────────────────────────────

def parse_verifier(
    input_dir: str = "data/GIR검증기관",
    output_path: str = "data/interim/gir_verifier_list.parquet",
) -> pd.DataFrame:
    """
    The xlsx has title rows 0-1 and header row 2. Data rows have NaN rows
    interspersed (sub-designation rows). We extract only rows where column 0
    has a numeric index value.
    """
    files = glob.glob(f"{input_dir}/*.xlsx")
    if not files:
        logger.error(f"No xlsx in {input_dir}")
        return pd.DataFrame()

    path = files[0]
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df_raw = pd.read_excel(path, header=None, dtype=str)

    # Column assignments based on inspection:
    # 0: index, 1: 검증기관명, 2: 지정번호, 3: 지정일·유효기간, 4: 소재지, 5: 지정분야, 6: 비고
    col_names = ["idx", "검증기관명_raw", "지정번호", "지정기간", "소재지", "지정분야", "비고"]
    df_raw.columns = col_names[:len(df_raw.columns)]

    # Keep only rows with numeric index (actual verifier rows, not sub-rows)
    df_raw["_is_main"] = pd.to_numeric(df_raw["idx"], errors="coerce").notna()
    df = df_raw[df_raw["_is_main"]].copy()
    df = df.drop(columns=["_is_main"])

    # Clean 검증기관명: remove embedded newlines
    df["검증기관명"] = (
        df["검증기관명_raw"]
        .str.replace(r"\n", " ", regex=True)
        .str.strip()
        # Remove representative info in parentheses at end
        .str.replace(r"\s*\(.*?\)\s*$", "", regex=True)
        .str.strip()
    )
    df = df.drop(columns=["검증기관명_raw"])
    df["idx"] = pd.to_numeric(df["idx"], errors="coerce").astype("Int64")

    # Clean other fields
    for col in ("지정번호", "지정기간", "소재지", "지정분야"):
        if col in df.columns:
            df[col] = df[col].str.replace(r"\n", " ", regex=True).str.strip()

    df = df.reset_index(drop=True)

    logger.info(f"Parsed {len(df)} verifiers")
    logger.info(df[["idx", "검증기관명"]].to_string())

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(df):,} rows -> {output_path}")
    return df


if __name__ == "__main__":
    parse_target()
    parse_verifier()
