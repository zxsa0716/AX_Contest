"""더 다양한 위성·데이터 시각화 (10+ 신규 figures).

(1) S5P 4종 한국 지도 4-panel (NO₂·SO₂·CO·HCHO 2023 평균)
(2) ODIAC 2019 vs 2023 변화 비교
(3) 업종별 시계열 4-panel (steel/petrochem/semicon/finance)
(4) 23 firms 5-year all-channel grid (small multiples)
(5) 4중 비교 시계열 (포스코 대표 사례)
(6) Heckman 계수 forest plot
(7) 이상탐지 scatter (괴리 vs 위성 불일치)
(8) 업종별 괴리율 boxplot
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import rasterio

import sys
sys.path.insert(0, str(Path(__file__).parent))
from style import setup_style, INDUSTRY_COLORS, PATTERN_COLORS

ROOT = Path(__file__).resolve().parents[2]
ODIAC = ROOT / "data" / "interim" / "odiac_clip_kr"
SAT = pd.read_csv(ROOT / "data" / "interim" / "satellite_panel_residuals.csv",
                   on_bad_lines="skip", low_memory=False)
PANEL = pd.read_parquet(ROOT / "data" / "processed" / "integrated_panel.parquet")
SITES = pd.read_csv(ROOT / "data" / "interim" / "gold_sites.csv")
MK = pd.read_csv(ROOT / "data" / "processed" / "trend_mk.csv")
HECK = pd.read_csv(ROOT / "data" / "processed" / "heckman_results.csv")
FIGS = ROOT / "figs"

KR_LON = (124.0, 132.0)
KR_LAT = (33.0, 39.0)


def fig_s5p_4species_korea():
    """S5P 4종 한국 평균 지도 (사이트 기반 그리드 보간)."""
    setup_style()
    yr_data = SAT[SAT["year"] == 2023].groupby("site_id").agg({
        "lat": "first", "lon": "first",
        "no2_mean": "mean", "so2_mean": "mean",
        "co_mean": "mean", "hcho_mean": "mean"
    }).reset_index()
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    species_cfg = [
        ("no2_mean", "NO₂ (×10⁵ mol/m²)", 1e5, "Reds", axes[0, 0]),
        ("so2_mean", "SO₂ (×10⁴ mol/m²)", 1e4, "Oranges", axes[0, 1]),
        ("co_mean",  "CO (×10² mol/m²)",  1e2, "Greens",  axes[1, 0]),
        ("hcho_mean","HCHO (×10⁵ mol/m²)",1e5, "Purples", axes[1, 1]),
    ]
    for col, label, scale, cmap, ax in species_cfg:
        sizes = (yr_data[col].fillna(0) * scale).clip(lower=0)
        sc = ax.scatter(yr_data["lon"], yr_data["lat"],
                       c=sizes, s=200, cmap=cmap,
                       edgecolors="black", linewidth=0.6)
        ax.set_xlim(*KR_LON); ax.set_ylim(*KR_LAT)
        ax.set_aspect("equal"); ax.grid(alpha=0.3)
        ax.set_title(label, fontweight="bold")
        plt.colorbar(sc, ax=ax, fraction=0.04)
        ax.set_xlabel("경도"); ax.set_ylabel("위도")
    plt.suptitle("그림 X1. Sentinel-5P 4종 위성 신호 — Gold 23사 사업장 평균 (2023)\n"
                 "각 사업장 10km buffer 연평균값 (ERA5 보정 전 원시값)", y=1.00, fontsize=13)
    plt.tight_layout()
    out = FIGS / "fig_s5p_4species_korea.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_odiac_change_2019_2023():
    """ODIAC 2019 vs 2023 변화 비교 (3 panel: 2019·2023·차이)."""
    setup_style()
    f19 = ODIAC / "odiac2024_1km_excl_intl_1907_KR.tif"
    f23 = ODIAC / "odiac2024_1km_excl_intl_2307_KR.tif"
    if not f19.exists() or not f23.exists():
        print(f"[skip] ODIAC 2019/2023 missing"); return
    with rasterio.open(f19) as s19:
        d19 = s19.read(1); b19 = s19.bounds
    with rasterio.open(f23) as s23:
        d23 = s23.read(1)
    diff = d23 - d19
    fig, axes = plt.subplots(1, 3, figsize=(17, 6))
    extent = [b19.left, b19.right, b19.bottom, b19.top]
    vmax = max(np.percentile(d19[d19 > 0], 99), np.percentile(d23[d23 > 0], 99))
    for ax, data, title, cmap in [
        (axes[0], d19, "2019-07", "hot"),
        (axes[1], d23, "2023-07", "hot"),
    ]:
        m = np.ma.masked_less_equal(data, 0)
        im = ax.imshow(m, extent=extent, norm=LogNorm(vmin=0.01, vmax=vmax),
                       cmap=cmap, origin="upper")
        ax.scatter(SITES["lon"], SITES["lat"], c="cyan", s=20, marker="^",
                   edgecolors="white", linewidth=0.3)
        ax.set_xlim(*KR_LON); ax.set_ylim(*KR_LAT); ax.set_aspect("equal")
        ax.set_title(title, fontweight="bold")
        plt.colorbar(im, ax=ax, fraction=0.04, label="tC/cell")
    # Diff
    dmax = max(abs(np.percentile(diff, 99)), abs(np.percentile(diff, 1)))
    im = axes[2].imshow(diff, extent=extent, vmin=-dmax/3, vmax=dmax/3,
                        cmap="RdBu_r", origin="upper")
    axes[2].scatter(SITES["lon"], SITES["lat"], c="black", s=20, marker="^")
    axes[2].set_xlim(*KR_LON); axes[2].set_ylim(*KR_LAT); axes[2].set_aspect("equal")
    axes[2].set_title("2023 − 2019 (감소=파랑, 증가=빨강)", fontweight="bold")
    plt.colorbar(im, ax=axes[2], fraction=0.04, label="ΔtC/cell")
    plt.suptitle("그림 X2. ODIAC CO₂ 2019 vs 2023 변화 (7월 기준)", y=1.02, fontsize=13)
    plt.tight_layout()
    out = FIGS / "fig_odiac_change_2019_2023.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_industry_timeseries():
    """업종별 GIR 시계열 4-panel."""
    setup_style()
    df = PANEL[PANEL["year"].between(2019, 2023)].copy()
    industries = df["industry"].dropna().unique()
    n = len(industries)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows), sharex=True)
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for ax, ind in zip(axes, industries):
        sub = df[df["industry"] == ind]
        for stock, g in sub.groupby("stock_code"):
            g = g.sort_values("year")
            name = g["corp_name"].iloc[0][:12]
            ax.plot(g["year"], g["gir_scope1_tco2eq"] / 1e6, "o-",
                    label=name, alpha=0.8, linewidth=1.5)
        ax.set_ylabel("GIR Scope 1 (Mt)")
        ax.set_title(f"{ind} ({len(sub['stock_code'].unique())}개사)", fontweight="bold")
        ax.set_xticks([2019, 2020, 2021, 2022, 2023])
        ax.legend(fontsize=7, loc="best")
        ax.grid(alpha=0.3)
    for j in range(n, len(axes)):
        axes[j].axis("off")
    plt.suptitle("그림 X3. 업종별 GIR Scope 1 5년 추이 (2019-2023)", y=1.00, fontsize=13)
    plt.tight_layout()
    out = FIGS / "fig_industry_timeseries.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_all23_smallmultiples():
    """23 firms × 5년 GIR + 위성 + ODIAC small multiples grid."""
    setup_style()
    df = PANEL[PANEL["year"].between(2019, 2023)]
    firms = df.drop_duplicates("stock_code").sort_values("gir_scope1_tco2eq", ascending=False)
    n = len(firms)
    cols = 5
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(20, 3.5 * rows))
    axes = axes.flatten()
    for ax, (_, frow) in zip(axes, firms.iterrows()):
        code = frow["stock_code"]
        sub = df[df["stock_code"] == code].sort_values("year")
        if sub.empty:
            ax.axis("off"); continue
        # Normalize each series to 2019=100 for comparison
        def norm(s):
            base = s.iloc[0] if not s.empty and s.iloc[0] != 0 else 1
            return s / base * 100
        ax.plot(sub["year"], norm(sub["gir_scope1_tco2eq"]), "o-",
                color="black", linewidth=1.8, label="GIR")
        if sub["esg_scope1_tco2eq"].notna().sum() >= 3:
            ax.plot(sub["year"], norm(sub["esg_scope1_tco2eq"]), "s-",
                    color="#888", linewidth=1.3, label="ESG", alpha=0.7)
        if sub["no2_mean"].notna().sum() >= 3:
            ax.plot(sub["year"], norm(sub["no2_mean"]), "^--",
                    color="#D55E00", linewidth=1.2, label="NO₂", alpha=0.7)
        if sub["odiac_sum_tC_year"].notna().sum() >= 3:
            ax.plot(sub["year"], norm(sub["odiac_sum_tC_year"]), "v--",
                    color="#0072B2", linewidth=1.2, label="ODIAC", alpha=0.7)
        ax.axhline(100, color="gray", linestyle=":", alpha=0.4)
        name = frow["corp_name"][:12]
        ax.set_title(f"{name}", fontsize=9, fontweight="bold")
        ax.set_xticks([2019, 2021, 2023])
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.3)
        if ax == axes[0]:
            ax.legend(fontsize=6, loc="best")
    for j in range(n, len(axes)):
        axes[j].axis("off")
    plt.suptitle("그림 X4. Gold 23사 4채널 정규화 시계열 (2019=100, GIR 배출 내림차순)\n"
                 "검정=GIR · 회색=ESG · 주황=위성NO₂ · 파랑=ODIAC", y=1.00, fontsize=13)
    plt.tight_layout()
    out = FIGS / "fig_all23_normalized.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_posco_4channel_detail():
    """포스코홀딩스 4중 비교 디테일 (D 패턴 대표 사례)."""
    setup_style()
    df = PANEL[(PANEL["stock_code"] == "005490") & PANEL["year"].between(2019, 2023)].sort_values("year")
    if df.empty:
        print("[skip] no POSCO data"); return
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    cfg = [
        (axes[0, 0], "gir_scope1_tco2eq", "GIR 법정 (MtCO₂eq)", 1e6, "black"),
        (axes[0, 1], "esg_scope1_tco2eq", "ESG 자체보고", 1, "#888"),
        (axes[1, 0], "no2_mean", "위성 NO₂ (×10⁵ mol/m²)", 1/1e-5, "#D55E00"),
        (axes[1, 1], "odiac_sum_tC_year", "ODIAC CO₂ (×10⁵ tC)", 1/1e5, "#0072B2"),
    ]
    for ax, col, label, scale, color in cfg:
        if col in df.columns and df[col].notna().any():
            vals = df[col] / scale if scale > 1 else df[col] * scale
            ax.plot(df["year"], vals, "o-", color=color, linewidth=2.5, markersize=8)
            ax.set_title(label, fontweight="bold")
            ax.set_ylabel(label.split("(")[0].strip())
            ax.set_xticks([2019, 2020, 2021, 2022, 2023])
            ax.grid(alpha=0.3)
            # Trend
            from scipy.stats import linregress
            mask = vals.notna()
            if mask.sum() >= 3:
                x = df.loc[mask, "year"].values
                y = vals[mask].values
                slope, intercept, r, _, _ = linregress(x, y)
                ax.plot(x, slope * x + intercept, "--", color=color, alpha=0.4, linewidth=1)
                ax.text(0.05, 0.95, f"slope: {slope:+.2g}\nR²={r**2:.2f}",
                        transform=ax.transAxes, va="top",
                        bbox=dict(facecolor="white", alpha=0.8))
    plt.suptitle("그림 X5. 포스코홀딩스 4중 비교 디테일 (D 패턴 대표 사례)\n"
                 "GIR·ESG ↑↑ vs 위성·ODIAC ↓↓ — 공시-물리측정 방향 완벽 반대",
                 y=1.02, fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = FIGS / "fig_posco_4channel_detail.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_heckman_forest():
    """Heckman 계수 forest plot."""
    setup_style()
    df = HECK.copy()
    fig, ax = plt.subplots(figsize=(11, max(5, 0.5 * len(df))))
    y_pos = np.arange(len(df))
    colors = ["#D55E00" if (l > 0) == (u > 0) and abs(b) > 1 else "#888"
              for b, l, u in zip(df["beta"], df["ci_lower_boot"], df["ci_upper_boot"])]
    ax.scatter(df["beta"], y_pos, c=colors, s=80, zorder=10)
    for i, (b, l, u) in enumerate(zip(df["beta"], df["ci_lower_boot"], df["ci_upper_boot"])):
        ax.plot([l, u], [i, i], color=colors[i], linewidth=2, alpha=0.7)
    ax.axvline(0, color="black", linestyle=":", alpha=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df["var"], fontsize=10)
    ax.set_xlabel("계수 β (Bootstrap 95% CI)")
    ax.set_title("그림 X6. Heckman Stage 2 계수 Forest Plot (Bootstrap B=2000, firm-block)\n"
                 "주황=유의 (CI가 0 미포함), 회색=비유의", fontweight="bold")
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    out = FIGS / "fig_heckman_forest.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_anomaly_scatter_2d():
    """이상탐지 2D scatter (괴리율 × 위성 일관성)."""
    setup_style()
    mk = MK.copy()
    mk["stock_code"] = mk["stock_code"].astype(str).str.zfill(6)
    # x = |GIR-ESG τ 차이|, y = |GIR-위성 τ 차이|
    mk["x_disc"] = (mk["gir_tau"] - mk["esg_tau"]).abs() / 2
    mk["y_sat"]  = ((mk["gir_tau"] - mk["no2_tau"]).abs() +
                    (mk["gir_tau"] - mk["odiac_tau"]).abs()) / 4
    fig, ax = plt.subplots(figsize=(11, 9))
    for pat, color in PATTERN_COLORS.items():
        sub = mk[mk["pattern"] == pat]
        if len(sub) == 0: continue
        size = 350 if pat == "D_both_suspect" else 150
        ax.scatter(sub["x_disc"], sub["y_sat"], c=color, s=size,
                   alpha=0.8, edgecolors="black", linewidth=1, label=f"{pat} ({len(sub)})")
        if pat in ("D_both_suspect", "C_gir_suspect", "A_consistent_up"):
            for _, r in sub.iterrows():
                ax.annotate(r["corp_name"][:10], (r["x_disc"], r["y_sat"]),
                            fontsize=9, fontweight="bold", xytext=(8, 8),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    # Quadrant lines
    ax.axvline(mk["x_disc"].median(), color="gray", linestyle=":", alpha=0.5)
    ax.axhline(mk["y_sat"].median(), color="gray", linestyle=":", alpha=0.5)
    ax.text(0.97, 0.97, "즉시 검증 대상\n(높은 괴리·위성 불일치)",
            transform=ax.transAxes, ha="right", va="top",
            bbox=dict(facecolor="#ffe5e5", edgecolor="red"))
    ax.set_xlabel("GIR-ESG 괴리도 |Δτ|/2", fontsize=11)
    ax.set_ylabel("GIR-위성·ODIAC 불일치도", fontsize=11)
    ax.set_title("그림 X7. Gold 23사 이상탐지 2D 분포 (Mann-Kendall τ 차이 기반)",
                 fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = FIGS / "fig_anomaly_2d.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_industry_boxplot():
    """업종별 괴리율 boxplot."""
    setup_style()
    df = PANEL[PANEL["year"].between(2019, 2023)].copy()
    df["disc_pct"] = (df["esg_scope1_tco2eq"] - df["gir_scope1_tco2eq"]) / df["gir_scope1_tco2eq"] * 100
    df = df.dropna(subset=["disc_pct", "industry"])
    fig, ax = plt.subplots(figsize=(11, 7))
    industries = df["industry"].unique()
    data = [df[df["industry"] == i]["disc_pct"].values for i in industries]
    bp = ax.boxplot(data, labels=industries, patch_artist=True, widths=0.6)
    for patch, ind in zip(bp["boxes"], industries):
        patch.set_facecolor(INDUSTRY_COLORS.get(ind, "#999"))
        patch.set_alpha(0.7)
    ax.axhline(0, color="black", linestyle=":", alpha=0.5)
    ax.set_ylabel("괴리율 = (ESG − GIR) / GIR × 100 (%)", fontsize=11)
    ax.set_title("그림 X8. 업종별 GIR-ESG 괴리율 분포 (2019-2023, firm-year)",
                 fontweight="bold")
    ax.grid(alpha=0.3, axis="y")
    plt.xticks(rotation=15)
    plt.tight_layout()
    out = FIGS / "fig_industry_boxplot.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


if __name__ == "__main__":
    fig_s5p_4species_korea()
    fig_odiac_change_2019_2023()
    fig_industry_timeseries()
    fig_all23_smallmultiples()
    fig_posco_4channel_detail()
    fig_heckman_forest()
    fig_anomaly_scatter_2d()
    fig_industry_boxplot()
    print("\n=== 8 new figures generated ===")
