"""
Task 2: Consolidate GIR 할당대상업체 (4 snapshots) into a unified panel.

Input:  data/GIR할당대상/*.xlsx  (4 snapshots, skiprows=2, actual header on row index 0 after skip)
Output: data/interim/gir_allocated_panel.parquet

Notes:
- The xlsx files have 2 merged header rows; skiprows=2 reads row 0 as data.
  Actual column headers are in that first data row, so we do header=None + manual assignment.
- snapshot_year is parsed from the filename timestamp (YYYYMMDD prefix).
- 계획기간 identifies which K-ETS phase (1-4).
- We deduplicate keeping the most-recent snapshot per 업체명.
"""

import re
import glob
import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from consolidate_gir import normalize_corp_name

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLS = ["순번", "계획기간", "지정연도", "업종", "업체명", "소재지", "적용기준"]


def load_one_snapshot(path: str) -> pd.DataFrame:
    """Load a single 할당대상업체 xlsx snapshot."""
    path = Path(path)
    # Extract snapshot timestamp from filename e.g. 할당대상업체현황_20260420223117.xlsx
    m = re.search(r"_(\d{8})", path.name)
    snapshot_ts = int(m.group(1)) if m else 0
    snapshot_year = int(str(snapshot_ts)[:4]) if snapshot_ts else None

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Title rows 0-2 are merged cells / blank; header is row 3 (0-based)
        # skiprows=3 skips first 3 rows, then pandas uses the next row as header
        df_raw = pd.read_excel(path, skiprows=3, header=0, dtype=str)

    if df_raw.empty:
        return pd.DataFrame()

    # Rename to expected columns (they should already match)
    df_raw.columns = [str(c).strip() for c in df_raw.columns]

    # Check for expected columns
    missing = [c for c in EXPECTED_COLS if c not in df_raw.columns]
    if missing:
        logger.warning(f"{path.name}: missing columns {missing}; got {df_raw.columns.tolist()}")

    df_raw["snapshot_ts"] = snapshot_ts
    df_raw["snapshot_year"] = snapshot_year
    df_raw["file_source"] = str(path)
    return df_raw


def main(
    input_dir: str = "data/GIR할당대상",
    output_path: str = "data/interim/gir_allocated_panel.parquet",
) -> pd.DataFrame:
    files = sorted(glob.glob(f"{input_dir}/*.xlsx"))
    logger.info(f"Found {len(files)} 할당대상 snapshot files")

    frames = []
    for f in tqdm(files, desc="Loading 할당대상"):
        df = load_one_snapshot(f)
        if not df.empty:
            frames.append(df)

    panel = pd.concat(frames, ignore_index=True)

    # Keep rows with actual company name
    panel = panel[panel["업체명"].notna() & (panel["업체명"] != "")]

    # Normalize numeric columns
    for col in ("지정연도", "계획기간", "순번"):
        if col in panel.columns:
            panel[col] = pd.to_numeric(panel[col], errors="coerce")

    # Normalized name
    panel["업체명_normalized"] = panel["업체명"].str.strip().apply(normalize_corp_name)
    panel["소재지"] = panel["소재지"].str.strip() if "소재지" in panel.columns else None

    # Deduplicate: keep most-recent snapshot per 업체명_normalized
    panel_dedup = (
        panel.sort_values("snapshot_ts", ascending=False)
        .drop_duplicates(subset=["업체명_normalized"], keep="first")
        .reset_index(drop=True)
    )

    final_cols = [
        "snapshot_year", "계획기간", "지정연도", "업종",
        "업체명", "업체명_normalized", "소재지", "적용기준",
        "snapshot_ts", "file_source",
    ]
    for c in final_cols:
        if c not in panel_dedup.columns:
            panel_dedup[c] = None
    panel_dedup = panel_dedup[final_cols]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    panel_dedup.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(panel_dedup):,} deduplicated rows -> {output_path}")
    logger.info(f"Total before dedup: {len(panel):,} rows")
    logger.info(f"계획기간 distribution:\n{panel_dedup['계획기간'].value_counts().to_string()}")
    return panel_dedup


if __name__ == "__main__":
    main()
