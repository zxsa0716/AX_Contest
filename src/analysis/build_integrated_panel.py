"""Build integrated analysis panel — merge all data sources into firm-year panel.

Merges:
- GIR manifest 2018-2024 (Scope 1, 검증수행기관, 지정구분)
- ESG reports parsed (Scope 1/2/3, assurance, boundary) [when available]
- Satellite panel (NO2/SO2/CO/HCHO/ERA5 + MERRA-2) — aggregated monthly → yearly
- ODIAC panel (CO2 tC/month) — aggregated to yearly sum
- ASOS panel (weather ground obs) — aggregated to yearly
- Master index flags (in_kssb_30, in_kospi, n_gir_years)
- Industry, K-ETS allocation, verification history

Output: data/processed/integrated_panel.parquet
  firm × year → all variables
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "data" / "interim"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def _name_norm(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.replace(r"[()\s㈜]", "", regex=True)
    s = s.str.replace("주식회사", "", regex=False).str.replace("(주)", "", regex=False)
    return s.str.lower().str.strip()


def load_gir_manifest() -> pd.DataFrame:
    df = pd.read_parquet(INT / "gir_manifest_panel.parquet")
    df = df.rename(columns={
        "법인명": "corp_name",
        "법인명_normalized": "name_norm",
        "지정구분": "gir_designation",
        "scope1_tco2eq": "gir_scope1_tco2eq",
        "검증수행기관": "verifier",
    })
    # aggregate if multiple rows per firm-year (site-level)
    agg = df.groupby(["name_norm", "year"], as_index=False).agg(
        corp_name=("corp_name", "first"),
        gir_scope1_tco2eq=("gir_scope1_tco2eq", "sum"),
        energy_tj=("energy_tj", "sum"),
        verifier=("verifier", lambda x: "|".join(sorted(set(str(v) for v in x if pd.notna(v))))),
        gir_designation=("gir_designation", "first"),
        n_sites=("corp_name", "count"),
    )
    return agg


def load_master() -> pd.DataFrame:
    mi = pd.read_parquet(INT / "company_master_index.parquet")
    keep = ["master_id", "corp_name_canonical", "stock_code", "bizr_no", "corp_code",
            "in_kospi", "in_kssb_30", "in_gir_allocated", "has_verifier",
            "match_confidence", "name_normalized"]
    keep = [c for c in keep if c in mi.columns]
    mi = mi[keep].rename(columns={"name_normalized": "name_norm",
                                    "corp_name_canonical": "corp_name_master"})
    return mi


def load_gold_sites() -> pd.DataFrame:
    return pd.read_csv(INT / "gold_sites.csv")


def load_satellite_yearly() -> pd.DataFrame:
    path = INT / "satellite_panel_201901_202312.csv"
    df = pd.read_csv(path, on_bad_lines="skip", low_memory=False)
    # Aggregate monthly → yearly per site
    grp_cols = [c for c in ["company_id", "site_id", "industry", "year"] if c in df.columns]
    numeric = ["no2_mean", "so2_mean", "co_mean", "hcho_mean",
               "era5_u10", "era5_v10", "era5_t2m", "era5_tp", "era5_ws10",
               "era5_blh", "merra2_pbltop", "merra2_ps", "merra2_disph", "merra2_qv2m"]
    numeric = [c for c in numeric if c in df.columns]
    agg = df.groupby(grp_cols, as_index=False)[numeric].mean()
    # Now aggregate across sites within a company (if multiple sites)
    agg2 = agg.groupby(["company_id", "year"], as_index=False)[numeric].mean()
    return agg2


def load_odiac_yearly() -> pd.DataFrame:
    path = INT / "odiac_panel.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty:
        return df
    # Monthly → yearly sum (tC/yr) per company
    agg = df.groupby(["company_id", "year"], as_index=False).agg(
        odiac_sum_tC_year=("odiac_sum_tC", "sum"),
        odiac_mean_tC_per_km2=("odiac_mean_tC_per_km2", "mean"),
        odiac_max_tC=("odiac_max_tC", "max"),
        odiac_n_months=("odiac_sum_tC", "count"),
    )
    return agg


def load_asos_yearly() -> pd.DataFrame:
    path = INT / "asos_panel.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    agg = df.groupby(["company_id", "year"], as_index=False).agg(
        asos_avgTa_yr=("asos_avgTa", "mean"),
        asos_avgWs_yr=("asos_avgWs", "mean"),
        asos_sumRn_yr=("asos_sumRn", "sum"),
        asos_dist_km=("dist_km", "first"),
        asos_stn_nm=("nearest_stn_nm", "first"),
    )
    return agg


def load_esg_parsed() -> pd.DataFrame:
    path = INT / "esg_reports_parsed.csv"
    if not path.exists():
        return pd.DataFrame(columns=["stock_code", "year"])
    df = pd.read_csv(path)
    if df.empty:
        return df
    # Parser's 'corp_code' column is actually the stock_code folder name
    if "corp_code" in df.columns and "stock_code" not in df.columns:
        df = df.rename(columns={"corp_code": "stock_code"})
    df["stock_code"] = df["stock_code"].astype(str).str.zfill(6)
    # Filter to HIGH/MEDIUM confidence; LOW noted but not used for merge
    df = df[df["parse_success"] == True]
    return df


def build() -> pd.DataFrame:
    print("[integrated] loading sources...")
    gir = load_gir_manifest()
    print(f"  GIR: {len(gir)} rows, {gir['name_norm'].nunique()} firms")

    master = load_master()
    print(f"  Master: {len(master)} rows")

    gold = load_gold_sites()
    gold["stock_code"] = gold["stock_code"].astype(str).str.zfill(6)
    print(f"  Gold sites: {len(gold)}")

    sat = load_satellite_yearly()
    print(f"  Satellite yearly: {len(sat)} rows")

    odiac = load_odiac_yearly()
    print(f"  ODIAC yearly: {len(odiac)} rows")

    asos = load_asos_yearly()
    print(f"  ASOS yearly: {len(asos)} rows")

    esg = load_esg_parsed()
    print(f"  ESG parsed: {len(esg)} rows")

    # --- Base panel: GIR × Gold ---
    # Attach Gold stock_code via master index (name_norm join)
    gir_m = gir.merge(master[["name_norm", "stock_code", "bizr_no", "corp_code",
                              "in_kospi", "in_kssb_30"]], on="name_norm", how="left")

    # Keep only Gold (in_kssb_30 == True with GIR coverage) for primary panel
    gold_codes = set(gold["stock_code"])
    gir_gold = gir_m[gir_m["stock_code"].isin(gold_codes)].copy()
    print(f"  Gold GIR panel: {len(gir_gold)} rows, {gir_gold['stock_code'].nunique()} firms")

    # Attach industry from Gold sites
    gir_gold = gir_gold.merge(gold[["stock_code", "industry", "company_id"]]
                                .drop_duplicates("stock_code"),
                              on="stock_code", how="left")

    # --- Merge satellite/odiac/asos by company_id × year ---
    # (company_id in sat panel = company_id from sites_seed / gold_sites)
    if not sat.empty:
        gir_gold = gir_gold.merge(sat, on=["company_id", "year"], how="left")
    if not odiac.empty:
        gir_gold = gir_gold.merge(odiac, on=["company_id", "year"], how="left")
    if not asos.empty:
        gir_gold = gir_gold.merge(asos, on=["company_id", "year"], how="left")

    # --- Merge ESG parsed by stock_code × year ---
    if not esg.empty:
        esg_keep = ["stock_code", "year"]
        col_map = {
            "scope1_tco2eq": "esg_scope1_tco2eq",
            "scope1_confidence": "esg_scope1_confidence",
            "scope2_location_tco2eq": "esg_scope2_location",
            "scope2_market_tco2eq": "esg_scope2_market",
            "scope3_present": "esg_scope3_present",
            "assurance_provider": "assurance_provider",
            "assurance_standard": "assurance_standard",
            "assurance_level": "assurance_level",
            "reporting_standard": "reporting_standard",
            "organizational_boundary": "organizational_boundary",
            "third_party_assurance": "third_party_assurance",
        }
        for c in col_map.keys():
            if c in esg.columns:
                esg_keep.append(c)
        esg_slim = esg[esg_keep].rename(columns=col_map)
        gir_gold = gir_gold.merge(esg_slim, on=["stock_code", "year"], how="left")

    # --- Compute discrepancy metrics ---
    if "esg_scope1_tco2eq" in gir_gold.columns:
        gir_gold["scope1_diff_abs"] = gir_gold["esg_scope1_tco2eq"] - gir_gold["gir_scope1_tco2eq"]
        gir_gold["scope1_diff_pct"] = np.where(
            gir_gold["gir_scope1_tco2eq"] > 0,
            100 * gir_gold["scope1_diff_abs"] / gir_gold["gir_scope1_tco2eq"],
            np.nan
        )

    # Column reorder: identifiers → flags → GIR → ESG → satellite → meteo → ODIAC → ASOS
    id_cols = ["company_id", "stock_code", "corp_code", "bizr_no", "corp_name", "industry", "year"]
    flag_cols = ["in_kospi", "in_kssb_30"]
    gir_cols = ["gir_scope1_tco2eq", "energy_tj", "verifier", "gir_designation", "n_sites"]
    esg_cols_out = [c for c in gir_gold.columns if c.startswith("esg_") or c.startswith("scope1_diff_") or c in
                    ("assurance_provider", "assurance_standard", "assurance_level",
                     "reporting_standard", "organizational_boundary")]
    sat_cols_out = [c for c in gir_gold.columns if any(c.startswith(p) for p in
                    ("no2_", "so2_", "co_", "hcho_", "era5_", "merra2_", "odiac_", "asos_"))]
    remaining = [c for c in gir_gold.columns if c not in id_cols + flag_cols + gir_cols + esg_cols_out + sat_cols_out]
    cols = [c for c in (id_cols + flag_cols + gir_cols + esg_cols_out + sat_cols_out + remaining) if c in gir_gold.columns]
    gir_gold = gir_gold[cols]

    return gir_gold


def main() -> None:
    panel = build()
    out_pq = OUT / "integrated_panel.parquet"
    out_csv = OUT / "integrated_panel.csv"
    panel.to_parquet(out_pq, index=False)
    panel.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"\n[done] {len(panel)} rows → {out_pq}")
    print(f"       columns: {len(panel.columns)}")
    # Sanity check
    print("\n=== Panel summary ===")
    print(f"Companies: {panel['stock_code'].nunique()}")
    print(f"Year range: {panel['year'].min()} - {panel['year'].max()}")
    for c in ["gir_scope1_tco2eq", "esg_scope1_tco2eq", "no2_mean", "so2_mean",
              "co_mean", "hcho_mean", "era5_t2m", "odiac_sum_tC_year", "asos_avgTa_yr"]:
        if c in panel.columns:
            nn = panel[c].notna().sum()
            pct = 100 * nn / len(panel)
            print(f"  {c}: {nn}/{len(panel)} non-null ({pct:.0f}%)")


if __name__ == "__main__":
    main()
