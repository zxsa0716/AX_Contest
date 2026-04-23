"""Pattern distribution + Mann-Kendall tau forest plot.

Outputs:
- figs/fig_pattern_distribution.png
- figs/fig_mk_tau_forest.png
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, str(Path(__file__).parent))
from style import setup_style, PATTERN_COLORS, INDUSTRY_COLORS

ROOT = Path(__file__).resolve().parents[2]
MK_CSV = ROOT / "data" / "processed" / "trend_mk.csv"
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
FIGS = ROOT / "figs"


def fig_pattern_distribution() -> None:
    setup_style()
    if not MK_CSV.exists():
        print("[skip] trend_mk.csv not found")
        return
    df = pd.read_csv(MK_CSV)
    counts = df["pattern"].value_counts()

    fig, ax = plt.subplots(figsize=(9, 5))
    pattern_order = ["A_consistent_up", "A_consistent_down",
                     "B_esg_suspect", "C_gir_suspect", "D_both_suspect",
                     "mixed", "E_no_trend"]
    x = []
    y = []
    colors = []
    for p in pattern_order:
        if p in counts.index:
            x.append(p.replace("_", "\n").replace("A\nconsistent", "A 일관").replace("B\nesg\nsuspect", "B ESG 의심")
                       .replace("C\ngir\nsuspect", "C GIR 의심").replace("D\nboth\nsuspect", "D 둘 다 의심")
                       .replace("E\nno\ntrend", "E 무추세"))
            y.append(counts[p])
            colors.append(PATTERN_COLORS.get(p, "#999999"))
    bars = ax.bar(x, y, color=colors, edgecolor="black", linewidth=0.8)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.15, f"{int(h)}",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("기업 수")
    ax.set_title(f"Mann-Kendall 4중 비교 패턴 분류 (Gold {len(df)}개사, 2019~2023)\n"
                 f"tau-기반 방향 분류, |τ|≥0.4")
    plt.xticks(fontsize=9)
    plt.tight_layout()
    out = FIGS / "fig_pattern_distribution.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")


def fig_mk_forest() -> None:
    setup_style()
    if not MK_CSV.exists():
        print("[skip] trend_mk.csv not found")
        return
    df = pd.read_csv(MK_CSV)
    panel = pd.read_parquet(PANEL) if PANEL.exists() else None

    # Industry mapping from panel
    if panel is not None:
        ind_map = panel[["stock_code", "industry"]].drop_duplicates()
        ind_map["stock_code"] = ind_map["stock_code"].astype(str)
        df["stock_code"] = df["stock_code"].astype(str)
        df = df.merge(ind_map, on="stock_code", how="left")

    # Sort by GIR tau
    df = df.sort_values("gir_tau", na_position="last")

    fig, axes = plt.subplots(1, 3, figsize=(13, max(5, 0.35 * len(df))), sharey=True)
    specs = [
        ("gir_tau", "gir_p", "GIR Scope 1"),
        ("no2_tau", "no2_p", "위성 NO₂"),
        ("odiac_tau", "odiac_p", "ODIAC CO₂"),
    ]
    for ax, (tau_col, p_col, title) in zip(axes, specs):
        y_pos = np.arange(len(df))
        colors = df["industry"].map(INDUSTRY_COLORS).fillna("#999999") if "industry" in df.columns else "#444444"
        ax.scatter(df[tau_col], y_pos, c=colors, s=30, alpha=0.8, edgecolors="black", linewidth=0.4)

        # Significance markers
        if p_col in df.columns:
            sig = df[p_col] < 0.1
            ax.scatter(df.loc[sig, tau_col], y_pos[sig.values],
                       marker="*", s=140, facecolors="none", edgecolors="red", linewidth=1.2)

        ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(0.4, color="red", linestyle=":", alpha=0.3)
        ax.axvline(-0.4, color="red", linestyle=":", alpha=0.3)
        ax.set_xlim(-1.05, 1.05)
        ax.set_xlabel("Kendall τ")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

    axes[0].set_yticks(range(len(df)))
    axes[0].set_yticklabels(df["corp_name"].str[:18], fontsize=8)
    plt.suptitle("Mann-Kendall τ Forest Plot — Gold 23개사 × 3 시계열 (2019~2023)\n"
                 "★ = p<0.1 유의성, 세로 점선 = |τ|=0.4 방향 임계값",
                 y=1.00)
    plt.tight_layout()
    out = FIGS / "fig_mk_tau_forest.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")


if __name__ == "__main__":
    fig_pattern_distribution()
    fig_mk_forest()
