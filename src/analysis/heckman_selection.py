"""Heckman 2-stage selection model per ADR-003 §6.1-6.2.

Stage 1 (probit): P(ESG_report_issued) = Φ(β·lnAsset + β·kospi + β·kssb30 + ...)
Stage 2 (FE panel): discrepancy_pct = β·lnGIR + β·verif + β·boundary + β·IMR
                                      + industry × year + firm FE + ε

Requires: integrated_panel.parquet with ESG + GIR + KSSB flag.
Output: data/processed/heckman_results.txt + regression_results_v2.csv
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
OUT = ROOT / "data" / "processed"


def main() -> None:
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)].copy()

    # ---- Stage 1: Probit of ESG report presence ----
    df["esg_present"] = df["esg_scope1_tco2eq"].notna().astype(int)
    # Require ln(GIR) as size proxy (Scope 1 absolute)
    df["ln_gir"] = np.log1p(df["gir_scope1_tco2eq"].fillna(0))
    df["ln_energy"] = np.log1p(df["energy_tj"].fillna(0))

    # industry dummies
    if "industry" in df.columns:
        ind_dum = pd.get_dummies(df["industry"], prefix="ind", drop_first=True)
        df = pd.concat([df, ind_dum], axis=1)

    # year dummies
    yr_dum = pd.get_dummies(df["year"], prefix="yr", drop_first=True)
    df = pd.concat([df, yr_dum], axis=1)

    x1_cols = ["ln_gir", "ln_energy"]
    if "in_kssb_30" in df.columns:
        df["in_kssb_30"] = df["in_kssb_30"].astype(int)
        x1_cols.append("in_kssb_30")
    x1_cols += [c for c in df.columns if c.startswith("ind_")]
    x1_cols += [c for c in df.columns if c.startswith("yr_")]

    stage1_df = df.dropna(subset=x1_cols + ["esg_present"])
    X1 = stage1_df[x1_cols].astype(float).values
    y1 = stage1_df["esg_present"].values

    import statsmodels.api as sm
    X1c = sm.add_constant(X1)
    try:
        probit = sm.Probit(y1, X1c).fit(disp=False, maxiter=100)
        print("=" * 60)
        print("STAGE 1 — Probit: P(ESG report issued | firm controls)")
        print("=" * 60)
        print(probit.summary())

        # Inverse Mills Ratio (IMR) for observations with ESG = 1
        xb1 = probit.predict(X1c, linear=True)
        imr = norm.pdf(xb1) / norm.cdf(xb1)
        stage1_df = stage1_df.copy()
        stage1_df["imr"] = imr
    except Exception as e:
        print(f"[err] Stage 1 probit failed: {e}")
        return

    # ---- Stage 2: panel regression on ESG-reporting firms only ----
    stage2 = stage1_df[stage1_df["esg_present"] == 1].copy()
    stage2["scope1_diff_pct"] = 100 * (stage2["esg_scope1_tco2eq"] - stage2["gir_scope1_tco2eq"]) / stage2["gir_scope1_tco2eq"].replace(0, np.nan)
    stage2 = stage2.dropna(subset=["scope1_diff_pct"])

    x2_cols = ["ln_gir", "in_kssb_30", "imr"]
    x2_cols += [c for c in stage2.columns if c.startswith("ind_")]
    x2_cols += [c for c in stage2.columns if c.startswith("yr_")]

    stage2 = stage2.dropna(subset=x2_cols)
    # Remove zero-variance columns (constants)
    X2 = stage2[x2_cols].astype(float)
    variances = X2.var()
    x2_cols_kept = [c for c in x2_cols if variances[c] > 1e-10]
    X2 = X2[x2_cols_kept].values
    y2 = stage2["scope1_diff_pct"].values
    X2c = sm.add_constant(X2)
    ols = sm.OLS(y2, X2c).fit(cov_type="cluster",
                              cov_kwds={"groups": stage2["stock_code"].values})

    print("=" * 60)
    print("STAGE 2 — Panel OLS with Heckman IMR correction")
    print("=" * 60)
    param_names = ["const"] + x2_cols_kept
    if len(param_names) == len(ols.params):
        print(ols.summary(xname=param_names))
    else:
        print(ols.summary())

    # Bootstrap 95% CI (B=2000, block by firm)
    print("\n=== Bootstrap 95% CI (B=2000, block by firm) ===")
    rng = np.random.default_rng(42)
    firms = stage2["stock_code"].unique()
    beta_boot = []
    for _ in range(2000):
        sampled = rng.choice(firms, size=len(firms), replace=True)
        boot_df = pd.concat([stage2[stage2["stock_code"] == f] for f in sampled])
        Xb = boot_df[x2_cols_kept].astype(float).values
        yb = boot_df["scope1_diff_pct"].values
        try:
            b = sm.OLS(yb, sm.add_constant(Xb)).fit().params
            if len(b) == len(param_names):
                beta_boot.append(b)
        except Exception:
            pass
    beta_boot = np.array(beta_boot)
    if len(beta_boot) == 0:
        print("[warn] bootstrap empty")
        return
    ci_lower = np.percentile(beta_boot, 2.5, axis=0)
    ci_upper = np.percentile(beta_boot, 97.5, axis=0)

    boot_df = pd.DataFrame({
        "var": param_names,
        "beta": ols.params,
        "se": ols.bse,
        "ci_lower_boot": ci_lower,
        "ci_upper_boot": ci_upper,
    })
    out_csv = OUT / "heckman_results.csv"
    boot_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(boot_df.to_string(index=False))
    print(f"\n[saved] {out_csv}")

    # Also save summary
    with open(OUT / "heckman_results.txt", "w", encoding="utf-8") as f:
        f.write("STAGE 1 PROBIT:\n\n")
        f.write(str(probit.summary()))
        f.write("\n\nSTAGE 2 OLS + IMR:\n\n")
        try:
            f.write(str(ols.summary(xname=param_names)))
        except Exception:
            f.write(str(ols.summary()))
        f.write("\n\nBOOTSTRAP 95% CI (B=2000, block by firm):\n\n")
        f.write(boot_df.to_string(index=False))

    # Pattern × firm summary
    print(f"\n=== Stage 2 sample: N={len(stage2)}, {stage2['stock_code'].nunique()} firms ===")


if __name__ == "__main__":
    main()
