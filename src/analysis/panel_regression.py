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

    # Formula
    X = df[["ln_gir", "in_kssb_30"]].astype(float)
    X = X.dropna()
    y = df.loc[X.index, "disc_pct"].dropna()
    X = X.loc[y.index]

    print(f"Regression N: {len(y)}, firms: {y.index.get_level_values(0).nunique()}")
    try:
        mod = PanelOLS(y, X, entity_effects=True, time_effects=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        print(res.summary)
        with open(OUT / "regression_results.txt", "w", encoding="utf-8") as f:
            f.write(str(res.summary))
    except Exception as e:
        print(f"[err] regression failed: {e}")


if __name__ == "__main__":
    main()
