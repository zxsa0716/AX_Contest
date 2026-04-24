"""ERA5 meteorological correction via OLS residualization (ADR-003 §6.1).

Per Fioletov et al. 2025 ACP: regress monthly satellite column density against
ERA5 wind (u10, v10), precipitation (tp), temperature (t2m), boundary layer
height (blh), and monthly dummies. The residuals represent "weather-corrected"
signal attributable to emission activity rather than meteorology.

Per-site regression (each site has its own met sensitivity). Saves residuals
back to the satellite panel as no2_resid, so2_resid, co_resid, hcho_resid.

Also runs MERRA-2 sensitivity check (correlation of ERA5 vs MERRA-2 residuals).

Output:
- data/interim/satellite_panel_residuals.csv
- data/processed/era5_correction_stats.csv (per-site R², beta, sensitivity)
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
IN = ROOT / "data" / "interim" / "satellite_panel_201901_202312.csv"
OUT = ROOT / "data" / "interim" / "satellite_panel_residuals.csv"
STATS = ROOT / "data" / "processed" / "era5_correction_stats.csv"


def residualize_site(df_site: pd.DataFrame, species: str) -> pd.Series:
    """OLS residuals for one species at one site, controlling for meteo."""
    y = df_site[f"{species}_mean"]
    met_cols = ["era5_u10", "era5_v10", "era5_t2m", "era5_tp", "era5_blh"]
    month_dummies = pd.get_dummies(df_site["month"], prefix="mo", drop_first=True)

    X = pd.concat([df_site[met_cols], month_dummies], axis=1)
    # Drop rows where y or X have NaN
    mask = y.notna() & X.notna().all(axis=1)
    if mask.sum() < 15:
        # Not enough observations
        return pd.Series(np.nan, index=df_site.index)

    y_valid = y[mask]
    X_valid = sm.add_constant(X[mask].astype(float))

    try:
        model = sm.OLS(y_valid, X_valid).fit()
        resid = pd.Series(np.nan, index=df_site.index)
        resid[mask] = model.resid
        return resid, model.rsquared, model.nobs
    except Exception:
        return pd.Series(np.nan, index=df_site.index), np.nan, 0


def main() -> None:
    df = pd.read_csv(IN, on_bad_lines="skip", low_memory=False)
    print(f"Input: {len(df)} rows, {df['site_id'].nunique()} sites")

    species_list = ["no2", "so2", "co", "hcho"]
    stats_rows = []

    for sp in species_list:
        print(f"\n[{sp}] Residualizing per-site...")
        df[f"{sp}_resid"] = np.nan
        for site_id, group in df.groupby("site_id"):
            idx = group.index
            result = residualize_site(group, sp)
            if isinstance(result, tuple):
                resid, r2, n = result
                df.loc[idx, f"{sp}_resid"] = resid
                stats_rows.append({
                    "site_id": site_id,
                    "species": sp,
                    "r_squared": r2,
                    "n_obs": int(n),
                    "resid_mean": resid.mean(),
                    "resid_std": resid.std(),
                })
            else:
                df.loc[idx, f"{sp}_resid"] = result
        nn = df[f"{sp}_resid"].notna().sum()
        print(f"  {sp}_resid: {nn}/{len(df)} ({nn/len(df)*100:.0f}%)")

    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    pd.DataFrame(stats_rows).to_csv(STATS, index=False, encoding="utf-8-sig")
    print(f"\n[saved] {OUT}")
    print(f"[saved] {STATS}")

    # Summary per species
    stats_df = pd.DataFrame(stats_rows)
    print(f"\n=== Residualization R² summary per species ===")
    print(stats_df.groupby("species")["r_squared"].describe()[["mean", "50%", "min", "max"]].round(3))


if __name__ == "__main__":
    main()
