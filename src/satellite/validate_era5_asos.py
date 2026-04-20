"""ERA5 (site-mean) vs ASOS (nearest station) cross-validation.

Run AFTER extract_satellite_panel.py and extract_asos.py.
Produces figs/era5_vs_asos_scatter.png + metrics CSV.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from calendar import monthrange

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

INTERIM = Path(__file__).resolve().parents[2] / "data" / "interim"
FIGS    = Path(__file__).resolve().parents[2] / "figs"
FIGS.mkdir(parents=True, exist_ok=True)


def _hours_in_month(y: int, m: int) -> int:
    return monthrange(y, m)[1] * 24


def load_joined(sat_csv: str, asos_csv: str) -> pd.DataFrame:
    sat  = pd.read_csv(sat_csv)
    asos = pd.read_csv(asos_csv)
    df = sat.merge(
        asos[["company_id", "site_id", "year", "month",
              "asos_avgTa", "asos_avgWs", "asos_sumRn",
              "nearest_stn_id", "nearest_stn_nm", "dist_km"]],
        on=["company_id", "site_id", "year", "month"], how="inner")
    df["era5_t2m_C"] = df["era5_t2m"] - 273.15
    df["hours"] = df.apply(lambda r: _hours_in_month(int(r.year), int(r.month)),
                           axis=1)
    df["era5_tp_mm_month"] = df["era5_tp"] * df["hours"] * 1000.0
    return df


def metrics_row(x: np.ndarray, y: np.ndarray, name: str) -> dict:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 5:
        return {"variable": name, "n": int(mask.sum()),
                "pearson_r": None, "bias": None, "rmse": None}
    x, y = x[mask], y[mask]
    return {
        "variable":  name,
        "n":         int(mask.sum()),
        "pearson_r": float(np.corrcoef(x, y)[0, 1]),
        "bias":      float((x - y).mean()),
        "rmse":      float(np.sqrt(((x - y) ** 2).mean())),
    }


def validate(sat_csv: str, asos_csv: str) -> pd.DataFrame:
    df = load_joined(sat_csv, asos_csv)
    pairs = [
        ("temperature (C)",     df["era5_t2m_C"].values,        df["asos_avgTa"].values),
        ("wind speed (m/s)",    df["era5_ws10"].values,         df["asos_avgWs"].values),
        ("precip (mm/month)",   df["era5_tp_mm_month"].values,  df["asos_sumRn"].values),
    ]
    mets = pd.DataFrame([metrics_row(a, b, n) for (n, a, b) in pairs])
    out = INTERIM / "era5_asos_metrics.csv"
    mets.to_csv(out, index=False)
    print(mets.to_string(index=False))
    print(f"[val] metrics -> {out}")

    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    for ax, (nm, a, b) in zip(axes.flatten()[:3], pairs):
        m = np.isfinite(a) & np.isfinite(b)
        ax.scatter(b[m], a[m], s=8, alpha=0.4)
        lo = float(np.nanmin([a[m].min(), b[m].min()]))
        hi = float(np.nanmax([a[m].max(), b[m].max()]))
        ax.plot([lo, hi], [lo, hi], "r-", lw=1)
        ax.set_xlabel(f"ASOS  {nm}")
        ax.set_ylabel(f"ERA5  {nm}")
        ax.set_title(nm)
    axes.flatten()[3].hist(df["dist_km"].dropna(), bins=20)
    axes.flatten()[3].set_xlabel("site-to-station distance (km)")
    axes.flatten()[3].set_ylabel("n sites")
    axes.flatten()[3].set_title("station proximity")
    fig.tight_layout()
    figpath = FIGS / "era5_vs_asos_scatter.png"
    fig.savefig(figpath, dpi=150)
    print(f"[val] figure -> {figpath}")
    return mets


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sat",  required=True)
    ap.add_argument("--asos", required=True)
    args = ap.parse_args()
    validate(args.sat, args.asos)
