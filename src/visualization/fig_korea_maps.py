"""8 Korea map / satellite imagery figures.

Outputs:
- fig_map_odiac_korea.png — ODIAC May 2023 한국 전국 (log scale + Gold sites)
- fig_map_odiac_seasonal.png — 4계절 비교 (Jan/Apr/Jul/Oct 2023)
- fig_map_gold_sites.png — Gold 23사 위치 + 산업별 색상
- fig_map_patterns.png — 패턴 분류 한국 지도 (D/C/A 색상)
- fig_map_asos_stations.png — ASOS 5 stations + 23 sites + 매칭선
- fig_concept_4channel.png — 4중 비교 conceptual diagram
- fig_posco_no2_timeseries.png — POSCO 포항 vs 광양 NO₂ 시계열
- fig_top6_multipanel.png — Top 6 emitters GIR + 위성 + ODIAC
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import rasterio
from rasterio.plot import show

import sys
sys.path.insert(0, str(Path(__file__).parent))
from style import setup_style, INDUSTRY_COLORS, PATTERN_COLORS

ROOT = Path(__file__).resolve().parents[2]
ODIAC = ROOT / "data" / "interim" / "odiac_clip_kr"
SITES = pd.read_csv(ROOT / "data" / "interim" / "gold_sites.csv")
PANEL_RES = ROOT / "data" / "interim" / "satellite_panel_residuals.csv"
ASOS = pd.read_csv(ROOT / "data" / "interim" / "asos_panel.csv")
MK = pd.read_csv(ROOT / "data" / "processed" / "trend_mk.csv")
FIGS = ROOT / "figs"

# Korea bbox
KR_LON = (124.0, 132.0)
KR_LAT = (33.0, 39.0)


def _draw_korea_outline(ax):
    """Simple lat/lon grid + bbox; for full detail use cartopy."""
    ax.set_xlim(*KR_LON)
    ax.set_ylim(*KR_LAT)
    ax.set_xlabel("경도 (°E)")
    ax.set_ylabel("위도 (°N)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3, linestyle="--")


def fig_odiac_korea_2023_05():
    setup_style()
    tif = ODIAC / "odiac2024_1km_excl_intl_2305_KR.tif"
    if not tif.exists():
        print(f"[skip] {tif} not found"); return
    with rasterio.open(tif) as src:
        data = src.read(1)
        bounds = src.bounds
    fig, ax = plt.subplots(figsize=(11, 9))
    masked = np.ma.masked_less_equal(data, 0)
    im = ax.imshow(masked, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
                   norm=LogNorm(vmin=max(0.01, masked.min()), vmax=masked.max()),
                   cmap="hot", origin="upper", alpha=0.85)
    # Gold sites
    for ind, color in INDUSTRY_COLORS.items():
        sub = SITES[SITES["industry"] == ind]
        if len(sub):
            ax.scatter(sub["lon"], sub["lat"], c=color, s=120, marker="^",
                       edgecolors="black", linewidth=0.8, label=ind, zorder=10)
    _draw_korea_outline(ax)
    ax.set_title("그림 A. ODIAC v2024 한국 CO₂ 배출 (2023-05, 1km 해상도, log scale)\n"
                 "Gold 23개사 사업장 위치 ▲ overlay")
    cbar = plt.colorbar(im, ax=ax, label="ODIAC tC/cell/month (log)", fraction=0.04)
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    plt.tight_layout()
    out = FIGS / "fig_map_odiac_korea.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_odiac_seasonal():
    setup_style()
    months = [(2023, 1, "1월 (겨울)"), (2023, 4, "4월 (봄)"),
              (2023, 7, "7월 (여름)"), (2023, 10, "10월 (가을)")]
    fig, axes = plt.subplots(2, 2, figsize=(13, 11))
    vmin_global, vmax_global = float("inf"), float("-inf")
    rasters = []
    for yr, mo, label in months:
        tif = ODIAC / f"odiac2024_1km_excl_intl_{yr%100:02d}{mo:02d}_KR.tif"
        if not tif.exists():
            rasters.append((None, None, label))
            continue
        with rasterio.open(tif) as src:
            data = src.read(1)
            bounds = src.bounds
        masked = np.ma.masked_less_equal(data, 0)
        if masked.count():
            vmin_global = min(vmin_global, masked.min())
            vmax_global = max(vmax_global, masked.max())
        rasters.append((masked, bounds, label))
    for (masked, bounds, label), ax in zip(rasters, axes.flatten()):
        if masked is None:
            ax.set_title(f"{label} (데이터 없음)"); continue
        im = ax.imshow(masked, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
                       norm=LogNorm(vmin=max(0.01, vmin_global), vmax=vmax_global),
                       cmap="hot", origin="upper")
        _draw_korea_outline(ax)
        ax.set_title(f"{label}")
        ax.scatter(SITES["lon"], SITES["lat"], c="cyan", s=15, marker="^",
                   edgecolors="white", linewidth=0.3, zorder=10)
    plt.suptitle("그림 B. ODIAC 한국 CO₂ 배출 4계절 비교 (2023, 1km, log scale)", y=1.00, fontsize=14)
    plt.tight_layout()
    out = FIGS / "fig_map_odiac_seasonal.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_gold_sites_map():
    setup_style()
    fig, ax = plt.subplots(figsize=(10, 10))
    for ind, color in INDUSTRY_COLORS.items():
        sub = SITES[SITES["industry"] == ind]
        if len(sub) == 0: continue
        ax.scatter(sub["lon"], sub["lat"], c=color, s=200, marker="o",
                   edgecolors="black", linewidth=1, label=ind, alpha=0.85, zorder=10)
        for _, r in sub.iterrows():
            name = str(r["company_id"])[:8]
            ax.annotate(name, (r["lon"], r["lat"]), fontsize=7,
                        xytext=(5, 5), textcoords="offset points")
    _draw_korea_outline(ax)
    ax.set_title("그림 E. Gold 23개사 사업장 위치 (산업별 색상)\n"
                 "VWorld 지오코딩 기반 ⟂ 100% 매칭 성공")
    ax.legend(loc="upper left", title="산업 분류", fontsize=9)
    plt.tight_layout()
    out = FIGS / "fig_map_gold_sites.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_pattern_map():
    setup_style()
    # Map MK pattern → site
    mk = MK.copy()
    mk["stock_code"] = mk["stock_code"].astype(str).str.zfill(6)
    sites = SITES.copy()
    sites["stock_code"] = sites["stock_code"].astype(str).str.zfill(6)
    merged = sites.merge(mk[["stock_code", "pattern"]], on="stock_code", how="left")
    merged["pattern"] = merged["pattern"].fillna("E_no_trend")

    fig, ax = plt.subplots(figsize=(11, 10))
    pattern_marker = {
        "A_consistent_up": ("o", "↑"), "A_consistent_down": ("o", "↓"),
        "B_esg_suspect": ("s", "B"), "C_gir_suspect": ("D", "C"),
        "D_both_suspect": ("*", "D"), "mixed": ("p", "M"), "E_no_trend": (".", "·"),
    }
    for pat, color in PATTERN_COLORS.items():
        sub = merged[merged["pattern"] == pat]
        if len(sub) == 0: continue
        marker, sym = pattern_marker.get(pat, ("o", ""))
        size = 350 if pat == "D_both_suspect" else 180
        ax.scatter(sub["lon"], sub["lat"], c=color, s=size, marker=marker,
                   edgecolors="black", linewidth=1.2, label=f"{pat} ({len(sub)})", alpha=0.85, zorder=10)
        for _, r in sub.iterrows():
            if pat in ("D_both_suspect", "C_gir_suspect", "A_consistent_up"):
                ax.annotate(str(r["company_id"])[:8], (r["lon"], r["lat"]), fontsize=8,
                            fontweight="bold", xytext=(7, 7), textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))
    _draw_korea_outline(ax)
    ax.set_title("그림 H. Mann-Kendall 패턴 분류 한국 지도\n"
                 "★ D 패턴 (포스코·삼성전자) · ◆ C (현대모비스) · ● A up (네이버) 강조")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()
    out = FIGS / "fig_map_patterns.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_asos_stations_map():
    setup_style()
    asos_unique = ASOS.drop_duplicates("nearest_stn_id")[
        ["nearest_stn_id", "nearest_stn_nm", "lat", "lon", "dist_km"]
    ]
    asos_per_site = ASOS.drop_duplicates("site_id")[
        ["site_id", "company_id", "lat", "lon", "nearest_stn_id", "nearest_stn_nm", "dist_km"]
    ]
    # ASOS station coords (inline minimal — 5 stations actually used)
    stn_coords_data = {
        129: {"stnNm": "서산", "lat": 36.7766, "lon": 126.4939},
        138: {"stnNm": "포항", "lat": 36.0328, "lon": 129.3799},
        152: {"stnNm": "울산", "lat": 35.5822, "lon": 129.3249},
        192: {"stnNm": "진주", "lat": 35.1636, "lon": 128.0400},
        235: {"stnNm": "보령", "lat": 36.3271, "lon": 126.5576},
        266: {"stnNm": "광양", "lat": 34.9407, "lon": 127.6941},
    }
    stn_coords = stn_coords_data

    fig, ax = plt.subplots(figsize=(10, 10))
    # Match lines
    for _, site in asos_per_site.iterrows():
        sc = stn_coords.get(int(site["nearest_stn_id"]))
        if sc:
            ax.plot([site["lon"], sc["lon"]], [site["lat"], sc["lat"]],
                    color="gray", alpha=0.4, linewidth=0.8, zorder=2)
    # Sites
    ax.scatter(asos_per_site["lon"], asos_per_site["lat"], c="red", s=80, marker="^",
               edgecolors="black", linewidth=0.8, label="Gold 23사 사업장", zorder=10)
    # ASOS stations
    used_stations = asos_per_site["nearest_stn_id"].unique()
    for stn_id in used_stations:
        sc = stn_coords.get(int(stn_id))
        if sc:
            ax.scatter(sc["lon"], sc["lat"], c="blue", s=200, marker="*",
                       edgecolors="black", linewidth=1, zorder=11)
            ax.annotate(sc["stnNm"], (sc["lon"], sc["lat"]), fontsize=10,
                        fontweight="bold", xytext=(8, 8), textcoords="offset points")
    _draw_korea_outline(ax)
    avg_d = asos_per_site["dist_km"].mean()
    ax.set_title(f"그림 I. ASOS 지점 5개와 Gold 23사 매칭\n"
                 f"평균 거리 {avg_d:.1f} km (당진·태안·삼천포 > 20 km flag)")
    ax.legend(loc="upper left")
    plt.tight_layout()
    out = FIGS / "fig_map_asos_stations.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_4channel_concept():
    setup_style()
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    boxes = [
        (1, 7, "GIR\n법정 신고", "#1f77b4", "환경부\n사업장 단위"),
        (4, 7, "ESG\n자체 보고", "#ff7f0e", "GRI 305-1\n연결 기준"),
        (1, 3, "Sentinel-5P\n위성 4종", "#2ca02c", "NO₂·SO₂·CO·HCHO\nERA5 보정"),
        (4, 3, "ODIAC\nCO₂ 1km", "#d62728", "NIES top-down\n월별 raster"),
    ]
    for x, y, label, color, sub in boxes:
        ax.add_patch(plt.Rectangle((x, y), 2.2, 1.5, facecolor=color, alpha=0.4, edgecolor="black", linewidth=2))
        ax.text(x + 1.1, y + 1.0, label, ha="center", va="center", fontsize=12, fontweight="bold")
        ax.text(x + 1.1, y + 0.4, sub, ha="center", va="center", fontsize=9, style="italic")

    # Pattern box
    ax.add_patch(plt.Rectangle((7, 4.5), 2.5, 2.5, facecolor="#fff2cc", edgecolor="black", linewidth=2.5))
    ax.text(8.25, 6.5, "패턴 분류\n5종 (A~E)", ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(8.25, 5.5, "Mann-Kendall τ\n방향 일관성", ha="center", va="center", fontsize=10)

    # Arrows
    for x, y in [(3.2, 7.75), (3.2, 3.75)]:
        ax.annotate("", xy=(7, 5.75), xytext=(x, y),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color="gray"))

    # Bottom output
    ax.add_patch(plt.Rectangle((3, 0.5), 4.5, 1.2, facecolor="#e8f5e9", edgecolor="green", linewidth=2))
    ax.text(5.25, 1.1, "검증 우선순위 매트릭스 → KEITI · KSSB 정책 직결",
            ha="center", va="center", fontsize=11, fontweight="bold")
    ax.annotate("", xy=(5.25, 1.7), xytext=(8.25, 4.5),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="green"))

    ax.set_title("그림 J. 4중 비교 분석 프레임워크 (Conceptual Diagram)", fontsize=14, pad=20)
    plt.tight_layout()
    out = FIGS / "fig_concept_4channel.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_posco_no2_timeseries():
    setup_style()
    df = pd.read_csv(PANEL_RES, on_bad_lines="skip", low_memory=False)
    posco_sites = df[df["site_id"].str.contains("POSCO", na=False)]
    if posco_sites.empty:
        print("[skip] no POSCO sites in panel"); return
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    for ax, site_id in zip(axes, posco_sites["site_id"].unique()):
        sub = df[df["site_id"] == site_id].sort_values(["year", "month"])
        sub["date"] = pd.to_datetime(sub["year"].astype(str) + "-" + sub["month"].astype(str) + "-01")
        ax.plot(sub["date"], sub["no2_mean"] * 1e6, "-", color="#444444",
                label="원시 NO₂ (µmol/m²)", alpha=0.7)
        ax.plot(sub["date"], sub["no2_resid"] * 1e6, "-", color="#D55E00",
                label="ERA5 보정 잔차", alpha=0.85, linewidth=1.5)
        ax.set_ylabel("NO₂ 컬럼 (µmol/m²)")
        ax.set_title(f"{site_id}")
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("연-월")
    plt.suptitle("그림 F. POSCO 포항 vs 광양 NO₂ 시계열 (2019-2023, ERA5 보정 전후)", y=1.00)
    plt.tight_layout()
    out = FIGS / "fig_posco_no2_timeseries.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


def fig_top6_multipanel():
    setup_style()
    panel = pd.read_parquet(ROOT / "data" / "processed" / "integrated_panel.parquet")
    # Top 6 by 2023 GIR Scope 1
    top6 = (panel[panel["year"] == 2023]
            .sort_values("gir_scope1_tco2eq", ascending=False)
            .head(6)["stock_code"].tolist())
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for ax, code in zip(axes.flatten(), top6):
        sub = panel[panel["stock_code"] == code].sort_values("year")
        if sub.empty: continue
        name = sub["corp_name"].iloc[0][:15]
        ax.plot(sub["year"], sub["gir_scope1_tco2eq"] / 1e6, "o-", color="black",
                label="GIR (MtCO₂eq)", linewidth=2)
        ax.set_ylabel("GIR Scope 1 (Mt)", color="black")
        ax2 = ax.twinx()
        if sub["no2_mean"].notna().any():
            ax2.plot(sub["year"], sub["no2_mean"] * 1e4, "s--", color="#D55E00",
                     label="NO₂ ×10⁴", alpha=0.7)
        if sub["odiac_sum_tC_year"].notna().any():
            ax2.plot(sub["year"], sub["odiac_sum_tC_year"] * 3.67 / 1e6, "^--",
                     color="#0072B2", label="ODIAC (Mt)", alpha=0.7)
        ax2.set_ylabel("위성 신호", color="gray")
        ax.set_title(f"{name} ({code})")
        ax.set_xticks([2019, 2020, 2021, 2022, 2023])
        l1, lab1 = ax.get_legend_handles_labels()
        l2, lab2 = ax2.get_legend_handles_labels()
        ax.legend(l1 + l2, lab1 + lab2, loc="best", fontsize=7)
    plt.suptitle("그림 G. Top 6 배출 기업 GIR vs 위성·ODIAC 종합 추이 (2019-2023)", y=1.01)
    plt.tight_layout()
    out = FIGS / "fig_top6_multipanel.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[saved] {out}")


if __name__ == "__main__":
    print("=== 8 Korea map figures ===")
    fig_odiac_korea_2023_05()
    fig_odiac_seasonal()
    fig_gold_sites_map()
    fig_pattern_map()
    fig_asos_stations_map()
    fig_4channel_concept()
    fig_posco_no2_timeseries()
    fig_top6_multipanel()
