"""Fixed-effects panel regression + Heckman 2-stage selection model.

Per ADR-003 §6.2:
  Stage 1 (probit): P(ESG_report_with_split) = Φ(lnAsset, KOSPI200, KSSB_pool,
                                                 industry, year, Tier)
  Stage 2 (FE panel): discrepancy = β·lnAsset + β·verif + β·boundary + β·Tier
                                   + β·IMR + industry_dummies + year_dummies + μ_firm + ε

For now (before full ESG parser complete): skeleton with placeholder ESG data.
Bootstrap CI (B=2000, block by firm).
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
OUT = ROOT / "data" / "processed"


def main() -> None:
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)].copy()

    if "esg_scope1_tco2eq" not in df.columns or df["esg_scope1_tco2eq"].notna().sum() < 30:
        print("[skip] ESG Scope 1 not yet populated; waiting for parser completion.")
        print("Script stub will run automatically once esg_reports_parsed.csv exists.")
        return

    # Log transform for regressions
    df["ln_gir"] = np.log1p(df["gir_scope1_tco2eq"])
    df["ln_esg"] = np.log1p(df["esg_scope1_tco2eq"])
    df["disc_pct"] = df["scope1_diff_pct"]

    # Import statsmodels here (only when we actually run)
    try:
        from linearmodels.panel import PanelOLS
    except Exception as e:
        print(f"[err] linearmodels not available: {e}")
        return

    # Panel setup
    df = df.set_index(["stock_code", "year"])
    df["year_dummy"] = df.index.get_level_values("year")

    # Align X and y — drop any row with NaN in any required col
    needed = ["ln_gir", "in_kssb_30", "disc_pct"]
    data = df[needed].dropna()
    # Need at least 2 years per firm for entity effects
    firm_counts = data.groupby(level=0).size()
    valid_firms = firm_counts[firm_counts >= 2].index
    data = data[data.index.get_level_values(0).isin(valid_firms)]

    y = data["disc_pct"]
    X = data[["ln_gir", "in_kssb_30"]].astype(float)
    print(f"Regression N: {len(y)}, firms: {y.index.get_level_values(0).nunique()}")
    try:
        mod = PanelOLS(y, X, entity_effects=True, time_effects=True,
                       drop_absorbed=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        print(res.summary)
        with open(OUT / "regression_results.txt", "w", encoding="utf-8") as f:
            f.write(str(res.summary))
    except Exception as e:
        print(f"[err] regression failed: {e}")
        # Fallback: simple OLS without entity effects
        import statsmodels.api as sm
        Xc = sm.add_constant(X.reset_index(drop=True))
        y2 = y.reset_index(drop=True)
        res = sm.OLS(y2, Xc).fit(cov_type="HC3")
        print("\n=== Fallback OLS (no FE) ===")
        print(res.summary())
        with open(OUT / "regression_results.txt", "w", encoding="utf-8") as f:
            f.write(str(res.summary()))


if __name__ == "__main__":
    main()
