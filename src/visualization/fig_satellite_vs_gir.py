"""Figure: Satellite NO2/SO2/CO/HCHO + ODIAC CO2 vs GIR Scope 1.

Shows:
- Scatter: yearly GIR Scope 1 vs NO2, SO2, CO, HCHO (4-panel)
- Scatter: yearly GIR Scope 1 vs ODIAC sum (1-panel with industry colors)
- Time series overlay for 3 case study firms (POSCO, 현대제철, SK하이닉스)

Outputs:
- figs/fig_satellite_scatter.png
- figs/fig_odiac_scatter.png
- figs/fig_case_studies.png
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, str(Path(__file__).parent))
from style import setup_style, INDUSTRY_COLORS

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
FIGS = ROOT / "figs"


def fig_satellite_scatter() -> None:
    setup_style()
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)].dropna(subset=["no2_mean", "gir_scope1_tco2eq"])

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    specs = [
        ("no2_mean", "NO₂ (mol/m²)", axes[0, 0]),
        ("so2_mean", "SO₂ (mol/m²)", axes[0, 1]),
        ("co_mean",  "CO (mol/m²)",  axes[1, 0]),
        ("hcho_mean", "HCHO (mol/m²)", axes[1, 1]),
    ]
    for col, ylabel, ax in specs:
        if col not in df.columns:
            continue
        sub = df.dropna(subset=[col])
        for industry, color in INDUSTRY_COLORS.items():
            s = sub[sub["industry"] == industry]
            if len(s) > 0:
                ax.scatter(s["gir_scope1_tco2eq"] / 1e6, s[col],
                           c=color, s=40, alpha=0.7, label=industry)
        ax.set_xlabel("GIR Scope 1 (MtCO₂eq)")
        ax.set_ylabel(ylabel)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"GIR Scope 1 vs 위성 {ylabel.split()[0]}")
        # Correlation
        if len(sub) > 3:
            from scipy.stats import spearmanr
            r, p = spearmanr(sub["gir_scope1_tco2eq"], sub[col])
            ax.text(0.05, 0.95, f"Spearman ρ={r:.2f}\np={p:.3f}",
                    transform=ax.transAxes, va="top",
                    bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray"))
    # Shared legend
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.02))
    plt.suptitle("Gold 23개사 GIR Scope 1 vs Sentinel-5P 위성 신호 (2019~2023)", y=1.01)
    plt.tight_layout()
    out = FIGS / "fig_satellite_scatter.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")


def fig_odiac_scatter() -> None:
    setup_style()
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)].dropna(subset=["odiac_sum_tC_year", "gir_scope1_tco2eq"])

    fig, ax = plt.subplots(figsize=(9, 7))
    for industry, color in INDUSTRY_COLORS.items():
        s = df[df["industry"] == industry]
        if len(s) > 0:
            ax.scatter(s["gir_scope1_tco2eq"] / 1e6,
                       s["odiac_sum_tC_year"] * 3.67 / 1e6,
                       c=color, s=60, alpha=0.7, label=industry, edgecolors="black", linewidth=0.5)

    # 1:1 line
    lim = [1e-2, 1e3]
    ax.plot(lim, lim, "k--", alpha=0.3, label="1:1 line")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("GIR Scope 1 (MtCO₂eq)")
    ax.set_ylabel("ODIAC 연간 CO₂ (MtCO₂, 10km 버퍼)")
    ax.set_title("GIR Scope 1 vs ODIAC 위성 CO₂ (4중 비교의 CO₂ 축)")
    ax.legend(loc="lower right", fontsize=8)
    if len(df) > 3:
        from scipy.stats import spearmanr
        r, p = spearmanr(df["gir_scope1_tco2eq"], df["odiac_sum_tC_year"])
        ax.text(0.05, 0.95, f"Spearman ρ={r:.2f} (p={p:.3f})\nN={len(df)}",
                transform=ax.transAxes, va="top",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray"))
    plt.tight_layout()
    out = FIGS / "fig_odiac_scatter.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")


def fig_case_studies() -> None:
    setup_style()
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)]

    cases = [
        ("005490", "포스코홀딩스"),
        ("004020", "현대제철"),
        ("000660", "SK하이닉스"),
        ("005930", "삼성전자"),
    ]

    fig, axes = plt.subplots(len(cases), 1, figsize=(10, 4 * len(cases)), sharex=True)
    if len(cases) == 1:
        axes = [axes]

    for ax, (stock, name) in zip(axes, cases):
        sub = df[df["stock_code"] == stock].sort_values("year")
        if sub.empty:
            ax.set_title(f"{name} ({stock}) — 데이터 없음")
            continue

        # Left y: GIR (MtCO2eq)
        ax.plot(sub["year"], sub["gir_scope1_tco2eq"] / 1e6, "o-", color="#000000",
                label="GIR Scope 1", linewidth=2)
        ax.set_ylabel("GIR Scope 1 (MtCO₂eq)", color="#000000")
        ax.tick_params(axis="y", labelcolor="#000000")

        # Right y: NO2
        ax2 = ax.twinx()
        if sub["no2_mean"].notna().any():
            ax2.plot(sub["year"], sub["no2_mean"] * 1e4, "s-", color="#D55E00",
                     label="NO₂ ×10⁴", alpha=0.7)
        if sub["odiac_sum_tC_year"].notna().any():
            ax2.plot(sub["year"], sub["odiac_sum_tC_year"] * 3.67 / 1e6, "^-",
                     color="#0072B2", label="ODIAC CO₂ (Mt)", alpha=0.7)
        ax2.set_ylabel("위성 신호 (normalized)", color="#666666")
        ax2.spines["top"].set_visible(False)

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc="best", fontsize=8)

        ax.set_title(f"{name} ({stock}) — GIR vs 위성 4중 비교")
        ax.set_xticks([2019, 2020, 2021, 2022, 2023])
    axes[-1].set_xlabel("연도")
    plt.tight_layout()
    out = FIGS / "fig_case_studies.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")


if __name__ == "__main__":
    fig_satellite_scatter()
    fig_odiac_scatter()
    fig_case_studies()
