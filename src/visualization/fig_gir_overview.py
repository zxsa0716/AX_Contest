"""Figure: Gold 23 firms GIR Scope 1 time series + industry breakdown.

Outputs:
- figs/fig_gir_overview.png
- figs/fig_gir_heatmap.png
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent))
from style import setup_style, INDUSTRY_COLORS

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
FIGS = ROOT / "figs"
FIGS.mkdir(parents=True, exist_ok=True)


def fig_timeseries() -> None:
    setup_style()
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)]

    fig, ax = plt.subplots(figsize=(10, 6))
    for industry in df["industry"].unique():
        if pd.isna(industry):
            continue
        sub = df[df["industry"] == industry]
        color = INDUSTRY_COLORS.get(industry, "#666666")
        for stock, g in sub.groupby("stock_code"):
            g = g.sort_values("year")
            ax.plot(g["year"], g["gir_scope1_tco2eq"] / 1e6,
                    color=color, alpha=0.6, linewidth=1.2,
                    marker="o", markersize=3)
    # Legend by industry
    for industry, color in INDUSTRY_COLORS.items():
        if industry in df["industry"].unique():
            ax.plot([], [], color=color, label=industry, linewidth=2)
    ax.set_xlabel("연도")
    ax.set_ylabel("GIR Scope 1 배출량 (MtCO₂eq)")
    ax.set_title("Gold 23개사 GIR Scope 1 배출량 추이 (2019~2023)")
    ax.legend(loc="upper right", frameon=True)
    ax.set_xticks([2019, 2020, 2021, 2022, 2023])
    plt.tight_layout()
    out = FIGS / "fig_gir_timeseries.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")


def fig_heatmap() -> None:
    setup_style()
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)]

    pivot = df.pivot_table(
        index="corp_name", columns="year", values="gir_scope1_tco2eq",
        aggfunc="first"
    ) / 1e6  # Mt

    # Sort by 2023 emissions descending
    if 2023 in pivot.columns:
        pivot = pivot.sort_values(2023, ascending=False)

    fig, ax = plt.subplots(figsize=(8, 10))
    # log scale for better visibility
    from matplotlib.colors import LogNorm
    data = pivot.values
    data_masked = np.where(data > 0, data, np.nan)
    im = ax.imshow(data_masked, aspect="auto", cmap="YlOrRd",
                   norm=LogNorm(vmin=max(0.01, np.nanmin(data_masked)),
                                vmax=np.nanmax(data_masked)))
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns.astype(str))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index.str[:25], fontsize=8)
    ax.set_xlabel("연도")
    ax.set_title("Gold 23개사 GIR Scope 1 히트맵 (MtCO₂eq, log scale)")
    plt.colorbar(im, ax=ax, label="배출량 (MtCO₂eq)")
    # Annotate cells
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = data[i, j]
            if v > 0 and not np.isnan(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        fontsize=6, color="white" if v > 10 else "black")
    plt.tight_layout()
    out = FIGS / "fig_gir_heatmap.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")


if __name__ == "__main__":
    fig_timeseries()
    fig_heatmap()
