"""
Task 6: Parse NIR 국가 온실가스 인벤토리 (wide format) -> long format.

Input:  data/NIR인벤토리/*.csv  (utf-8-sig, wide: rows=분야, cols=연도)
Output: data/interim/nir_national_panel.parquet

Columns: year (int), 분야 (str), 배출량_ktco2eq (float)
Unit: the source uses kt CO2-eq; we keep as-is and note in schema.
"""

import glob
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(
    input_dir: str = "data/NIR인벤토리",
    output_path: str = "data/interim/nir_national_panel.parquet",
) -> pd.DataFrame:
    files = glob.glob(f"{input_dir}/*.csv")
    if not files:
        logger.error(f"No CSV files found in {input_dir}")
        return pd.DataFrame()

    path = files[0]
    logger.info(f"Loading NIR from: {path}")

    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df = pd.read_csv(path, encoding=enc, dtype=str)
            logger.info(f"Encoding: {enc}, shape: {df.shape}")
            break
        except Exception as e:
            logger.warning(f"{enc} failed: {e}")
    else:
        logger.error("Cannot decode NIR CSV")
        return pd.DataFrame()

    # First column is '분야 및 연도'; remaining columns are year strings
    id_col = df.columns[0]
    year_cols = [c for c in df.columns[1:] if c.strip().isdigit()]

    df_long = df[[id_col] + year_cols].melt(
        id_vars=[id_col],
        value_vars=year_cols,
        var_name="year",
        value_name="배출량_ktco2eq",
    )
    df_long = df_long.rename(columns={id_col: "분야"})
    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce").astype("Int64")
    df_long["배출량_ktco2eq"] = pd.to_numeric(
        df_long["배출량_ktco2eq"].str.replace(",", "", regex=False), errors="coerce"
    )
    df_long["분야"] = df_long["분야"].str.strip()
    df_long = df_long.dropna(subset=["year", "분야"])
    df_long = df_long.reset_index(drop=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df_long.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(df_long):,} rows -> {output_path}")
    logger.info(f"Years: {sorted(df_long['year'].dropna().unique().tolist())}")
    logger.info(f"Unique 분야: {df_long['분야'].nunique()}")
    return df_long


if __name__ == "__main__":
    main()
