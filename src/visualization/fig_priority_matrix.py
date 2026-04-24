"""Figure 10: Policy priority matrix — verification allocation by 4-axis score.

Per ADR-003 §6.7:
  priority_score = w1·discrepancy_severity + w2·satellite_inconsistency
                 + w3·Tier_inverse + w4·verif_inverse

Output: figs/fig_priority_matrix.png (2D scatter with quadrants + KSSB labels)
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, str(Path(__file__).parent))
from style import setup_style, INDUSTRY_COLORS, PATTERN_COLORS

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
MK = ROOT / "data" / "processed" / "trend_mk.csv"
ANOM = ROOT / "data" / "processed" / "anomaly_classification.csv"
FIGS = ROOT / "figs"


def priority_score(mk_row, anom_row) -> float:
    """Composite priority score for verification."""
    # discrepancy severity: |esg - gir|/gir percentile via MK tau difference
    esg_gir_disagree = 0.0
    if pd.notna(mk_row.get("gir_tau")) and pd.notna(mk_row.get("esg_tau")):
        esg_gir_disagree = abs(mk_row["gir_tau"] - mk_row["esg_tau"]) / 2.0

    # satellite inconsistency: |gir - sat|
    sat_gir_disagree = 0.0
    if pd.notna(mk_row.get("gir_tau")) and pd.notna(mk_row.get("no2_tau")):
        sat_gir_disagree += abs(mk_row["gir_tau"] - mk_row["no2_tau"]) / 2.0
    if pd.notna(mk_row.get("gir_tau")) and pd.notna(mk_row.get("odiac_tau")):
        sat_gir_disagree += abs(mk_row["gir_tau"] - mk_row["odiac_tau"]) / 2.0
    sat_gir_disagree /= 2

    # anomaly class severity
    cls = anom_row.get("anomaly_class", "normal") if anom_row is not None else "normal"
    cls_score = {"structural": 3, "longitudinal": 2, "transient": 1, "normal": 0}.get(cls, 0)

    # Weighted composite
    return 0.4 * esg_gir_disagree + 0.4 * sat_gir_disagree + 0.2 * (cls_score / 3)


def main() -> None:
    setup_style()
    mk = pd.read_csv(MK)
    anom = pd.read_csv(ANOM) if ANOM.exists() else pd.DataFrame()
    panel = pd.read_parquet(PANEL)

    # One row per firm (aggregated across years)
    ind_map = panel.drop_duplicates("stock_code").set_index("stock_code")["industry"].to_dict()
    kssb_map = panel.drop_duplicates("stock_code").set_index("stock_code")["in_kssb_30"].to_dict() \
        if "in_kssb_30" in panel.columns else {}

    if not anom.empty:
        anom_firm = anom.groupby("stock_code")["anomaly_class"].agg(
            lambda x: pd.Series(x).value_counts().index[0]
        ).reset_index()
    else:
        anom_firm = pd.DataFrame(columns=["stock_code", "anomaly_class"])

    mk["stock_code"] = mk["stock_code"].astype(str).str.zfill(6)
    anom_firm["stock_code"] = anom_firm["stock_code"].astype(str).str.zfill(6) if len(anom_firm) else anom_firm["stock_code"]

    merged = mk.merge(anom_firm, on="stock_code", how="left")
    merged["industry"] = merged["stock_code"].map(lambda s: ind_map.get(s, "other"))
    merged["in_kssb"] = merged["stock_code"].map(lambda s: kssb_map.get(s, False))

    # Compute priority components
    merged["x_disc"] = merged.apply(
        lambda r: abs(r.get("gir_tau", 0) - r.get("esg_tau", 0))/2
            if pd.notna(r.get("esg_tau")) else 0,
        axis=1
    )
    merged["y_sat"] = merged.apply(
        lambda r: (abs(r.get("gir_tau", 0) - r.get("no2_tau", 0))/2
                   + abs(r.get("gir_tau", 0) - r.get("odiac_tau", 0))/2) / 2
            if pd.notna(r.get("no2_tau")) else 0,
        axis=1
    )
    merged["priority"] = merged.apply(
        lambda r: priority_score(r.to_dict(), {"anomaly_class": r.get("anomaly_class", "normal")}),
        axis=1
    )

    fig, ax = plt.subplots(figsize=(11, 8))
    for _, r in merged.iterrows():
        color = INDUSTRY_COLORS.get(r["industry"], "#999999")
        size = 80 + 200 * r["priority"]
        edge = "red" if r["in_kssb"] else "black"
        lw = 1.5 if r["in_kssb"] else 0.5
        ax.scatter(r["x_disc"], r["y_sat"], s=size, c=color, alpha=0.7,
                   edgecolors=edge, linewidth=lw)
        # Label top priority firms
        if r["priority"] > 0.25:
            ax.annotate(r["corp_name"][:10], (r["x_disc"], r["y_sat"]),
                        fontsize=8, xytext=(5, 5), textcoords="offset points")

    # Quadrant lines
    ax.axvline(merged["x_disc"].median(), color="gray", linestyle=":", alpha=0.5)
    ax.axhline(merged["y_sat"].median(), color="gray", linestyle=":", alpha=0.5)
    ax.text(ax.get_xlim()[1]*0.95, ax.get_ylim()[1]*0.95, "즉시 검증 대상",
            ha="right", va="top", fontsize=11, fontweight="bold",
            bbox=dict(facecolor="#ffcccc", edgecolor="red", alpha=0.7))

    ax.set_xlabel("GIR vs ESG 괴리 (|Δτ|/2)")
    ax.set_ylabel("GIR vs 위성·ODIAC 괴리 (|Δτ| 평균)")
    ax.set_title("검증 우선순위 매트릭스 (Gold 23개사)\n"
                 "크기 = 종합 priority, 빨간 테두리 = KSSB 2028 1차 대상")

    # Industry legend
    for ind, color in INDUSTRY_COLORS.items():
        if ind in merged["industry"].values:
            ax.scatter([], [], c=color, label=ind, s=60, alpha=0.7)
    ax.legend(loc="lower right", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    out = FIGS / "fig_priority_matrix.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {out}")

    # Also save top-10 priority list
    top = merged.sort_values("priority", ascending=False).head(10)[
        ["stock_code", "corp_name", "industry", "in_kssb",
         "x_disc", "y_sat", "priority", "anomaly_class", "pattern"]
    ]
    out_csv = ROOT / "data" / "processed" / "priority_ranking.csv"
    top.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"[saved] {out_csv}")
    print(top.to_string(index=False))


if __name__ == "__main__":
    main()
