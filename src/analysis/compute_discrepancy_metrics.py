"""Compute discrepancy metrics + Mann-Kendall trend for each firm.

Inputs: data/processed/integrated_panel.parquet
Output:
  data/processed/discrepancy_metrics.csv — firm-year metrics
  data/processed/trend_mk.csv — firm-level Mann-Kendall for each time series
  data/processed/pattern_classification.csv — pattern A~E per firm

Pattern logic (per ADR-003 + ADR-004):
  For each firm, compute Mann-Kendall τ and p for 4 time series:
    GIR Scope 1, ESG Scope 1 (if available), satellite (NO2+SO2 stack or ODIAC),
    satellite weather-corrected residual (TBD Phase 2)
  Pattern A: all ↑, consistent
  Pattern B: GIR↑, ESG↓, sat↑ → ESG suspect
  Pattern C: GIR↓, ESG↑, sat↑ → GIR suspect
  Pattern D: GIR↑, ESG↑, sat↓ OR similar inconsistency → both suspect
  Pattern E: no significant trend in any (p > 0.1 all)
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import pymannkendall as mk

ROOT = Path(__file__).resolve().parents[2]
IN_PQ = ROOT / "data" / "processed" / "integrated_panel.parquet"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def compute_mk(series: pd.Series, alpha: float = 0.1, tau_min: float = 0.4) -> dict:
    """Mann-Kendall with loosened significance per ADR-003 (small-sample panel).
    alpha=0.1 and |tau|>=0.4 threshold for directional classification.
    """
    vals = series.dropna().values
    if len(vals) < 3:
        return {"tau": np.nan, "p": np.nan, "trend": "insufficient",
                "dir": "insufficient", "slope": np.nan, "n": len(vals)}
    r = mk.original_test(vals, alpha=alpha)
    # Direction: based on tau sign + threshold (weaker than p)
    tau = float(r.Tau)
    if abs(tau) >= tau_min:
        direction = "increasing" if tau > 0 else "decreasing"
    else:
        direction = "flat"
    return {
        "tau": tau,
        "p": float(r.p),
        "trend": r.trend,
        "dir": direction,
        "slope": float(r.slope),
        "n": len(vals),
    }


def pattern_from_trends(gir_dir: str, esg_dir: str, sat_dir: str, odiac_dir: str) -> str:
    """Classify pattern based on 4 time series' direction (tau-based classification).

    Uses satellite (NO2) as primary atmospheric signal; ODIAC as CO2 top-down check.
    Default to satellite when ODIAC missing; use both when available.
    """
    dirs = {"gir": gir_dir, "esg": esg_dir, "sat": sat_dir, "odiac": odiac_dir}
    valid = {k: v for k, v in dirs.items() if v in ("increasing", "decreasing", "flat")}
    if len(valid) < 2:
        return "E_no_trend"
    ups = [k for k, v in valid.items() if v == "increasing"]
    dns = [k for k, v in valid.items() if v == "decreasing"]
    flats = [k for k, v in valid.items() if v == "flat"]

    # All same direction?
    if len(ups) >= len(valid) - len(flats) and len(ups) >= 2:
        return "A_consistent_up"
    if len(dns) >= len(valid) - len(flats) and len(dns) >= 2:
        return "A_consistent_down"

    # Satellite says up, GIR up, ESG down → ESG suspect
    if "sat" in valid and valid["sat"] == "increasing":
        if valid.get("gir") == "increasing" and valid.get("esg") == "decreasing":
            return "B_esg_suspect"
        if valid.get("gir") == "decreasing" and valid.get("esg") == "increasing":
            return "C_gir_suspect"
        if valid.get("gir") == "decreasing" and valid.get("esg") == "decreasing":
            return "D_both_suspect"
    if "sat" in valid and valid["sat"] == "decreasing":
        if valid.get("gir") == "decreasing" and valid.get("esg") == "increasing":
            return "C_gir_suspect"
        if valid.get("gir") == "increasing" and valid.get("esg") == "decreasing":
            return "B_esg_suspect"
        if valid.get("gir") == "increasing" and valid.get("esg") == "increasing":
            return "D_both_suspect"

    return "mixed"


def main() -> None:
    df = pd.read_parquet(IN_PQ)
    # restrict to 2019-2023 for comparison
    panel = df[(df["year"] >= 2019) & (df["year"] <= 2023)].copy()

    metrics_rows = []
    for key, grp in panel.groupby(["stock_code", "corp_name"]):
        stock, name = key
        grp = grp.sort_values("year")
        m = {"stock_code": stock, "corp_name": name, "n_years": len(grp)}

        # GIR trend
        gm = compute_mk(grp["gir_scope1_tco2eq"])
        for k, v in gm.items():
            m[f"gir_{k}"] = v

        # ESG trend (if available)
        if "esg_scope1_tco2eq" in grp.columns and grp["esg_scope1_tco2eq"].notna().sum() >= 3:
            em = compute_mk(grp["esg_scope1_tco2eq"])
        else:
            em = {"tau": np.nan, "p": np.nan, "trend": "insufficient", "n": 0}
        for k, v in em.items():
            m[f"esg_{k}"] = v

        # Satellite NO2 trend
        if "no2_mean" in grp.columns:
            nm = compute_mk(grp["no2_mean"])
        else:
            nm = {"tau": np.nan, "p": np.nan, "trend": "insufficient", "n": 0}
        for k, v in nm.items():
            m[f"no2_{k}"] = v

        # ODIAC trend
        if "odiac_sum_tC_year" in grp.columns:
            om = compute_mk(grp["odiac_sum_tC_year"])
        else:
            om = {"tau": np.nan, "p": np.nan, "trend": "insufficient", "n": 0}
        for k, v in om.items():
            m[f"odiac_{k}"] = v

        # Pattern classification — use `dir` (tau-based) instead of `trend` (p-based)
        m["pattern"] = pattern_from_trends(
            m.get("gir_dir", "insufficient"),
            m.get("esg_dir", "insufficient"),
            m.get("no2_dir", "insufficient"),
            m.get("odiac_dir", "insufficient"),
        )

        # Discrepancy stats (requires ESG)
        if "esg_scope1_tco2eq" in grp.columns and "scope1_diff_pct" in grp.columns:
            m["mean_disc_pct"] = grp["scope1_diff_pct"].mean()
            m["max_abs_disc_pct"] = grp["scope1_diff_pct"].abs().max()

        metrics_rows.append(m)

    out = pd.DataFrame(metrics_rows)
    out.to_csv(OUT / "trend_mk.csv", index=False, encoding="utf-8-sig")
    print(f"[done] {len(out)} firms → trend_mk.csv")
    print(f"\nPattern distribution:")
    print(out["pattern"].value_counts())
    print(f"\nGIR trend: {out['gir_trend'].value_counts().to_dict()}")
    print(f"NO2 trend: {out['no2_trend'].value_counts().to_dict()}")
    print(f"ODIAC trend: {out['odiac_trend'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
