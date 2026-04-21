"""
Task 5: Consolidate K-ETS 사전할당 (4 phases) into a unified long-format panel.

Input:  data/사전할당/{1,2,3,4}차_사전할당_*.csv  (cp949)
Output: data/interim/kets_allocation_panel.parquet

Phase schemas:
  Phase 1: 번호, 부문, 업체명, 합계, 2015년, 2016년, 2017년           (no 업종, no 유상여부)
  Phase 2: 번호, 부문, 업종, 업체명, 유상여부, 합계, 2018년, 2019년, 2020년
  Phase 3: 번호, 부문, 업종, 업체명, 유상여부, 2021년, ..., 2025년
  Phase 4: 번호, 부문, 업종, 업체명, 유상여부, 지정기준, 2026년, ..., 2030년

Output long format: phase, 부문, 업종, 업체명, 업체명_normalized, 유상여부, year, allocation_tco2eq
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


def load_phase(path: str, phase: int) -> pd.DataFrame:
    """Load a single K-ETS phase CSV and melt to long format."""
    path = Path(path)
    for enc in ("cp949", "utf-8-sig", "utf-8"):
        try:
            df = pd.read_csv(path, encoding=enc, dtype=str)
            break
        except Exception:
            continue
    else:
        logger.error(f"Cannot decode {path}")
        return pd.DataFrame()

    df.columns = [c.strip() for c in df.columns]

    # Identify year columns
    year_cols = [c for c in df.columns if re.match(r"^\d{4}년$", c.strip())]

    # Build base columns present in file
    base_cols = {
        "부문": "부문",
        "업종": "업종",
        "업체명": "업체명",
        "유상여부": "유상여부",
        "지정기준": "지정기준",
    }
    for col in base_cols:
        if col not in df.columns:
            df[col] = None

    df["phase"] = phase

    # Melt year columns to long
    id_vars = ["phase", "부문", "업종", "업체명", "유상여부", "지정기준"]
    df_long = df[id_vars + year_cols].melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name="year_str",
        value_name="allocation_tco2eq",
    )
    df_long["year"] = df_long["year_str"].str.extract(r"(\d{4})").astype(int)
    df_long.drop(columns=["year_str"], inplace=True)

    # Numeric coercion
    df_long["allocation_tco2eq"] = pd.to_numeric(
        df_long["allocation_tco2eq"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    return df_long


def main(
    input_dir: str = "data/사전할당",
    output_path: str = "data/interim/kets_allocation_panel.parquet",
) -> pd.DataFrame:
    # Map phase number to file glob
    phase_map = {}
    for f in sorted(glob.glob(f"{input_dir}/*.csv")):
        m = re.search(r"(\d)차_사전할당", Path(f).name)
        if m:
            phase_map[int(m.group(1))] = f

    logger.info(f"Found phases: {sorted(phase_map.keys())}")

    frames = []
    for phase, path in tqdm(sorted(phase_map.items()), desc="Loading K-ETS phases"):
        df = load_phase(path, phase)
        if not df.empty:
            frames.append(df)
            logger.info(f"Phase {phase}: {len(df):,} long rows")

    panel = pd.concat(frames, ignore_index=True)
    panel = panel[panel["업체명"].notna() & (panel["업체명"] != "")]
    panel["업체명"] = panel["업체명"].str.strip()
    panel["업체명_normalized"] = panel["업체명"].apply(normalize_corp_name)

    final_cols = [
        "phase", "부문", "업종", "업체명", "업체명_normalized",
        "유상여부", "지정기준", "year", "allocation_tco2eq",
    ]
    for c in final_cols:
        if c not in panel.columns:
            panel[c] = None
    panel = panel[final_cols]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(panel):,} rows -> {output_path}")
    logger.info(f"Unique firms: {panel['업체명_normalized'].nunique():,}")
    logger.info(f"Phase distribution:\n{panel.groupby('phase')['allocation_tco2eq'].sum().to_string()}")
    return panel


if __name__ == "__main__":
    main()
