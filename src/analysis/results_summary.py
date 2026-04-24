"""Generate comprehensive summary tables for final report.

Output:
- report/tables/table01_sample.md  — Gold/Silver/Bronze + industry breakdown
- report/tables/table02_data_coverage.md — dataset × firm-year coverage matrix
- report/tables/table03_pattern_results.md — Mann-Kendall tau table
- report/tables/table04_regression.md — main results + robustness
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
MK = ROOT / "data" / "processed" / "trend_mk.csv"
HECKMAN = ROOT / "data" / "processed" / "heckman_results.csv"
OUT = ROOT / "report" / "tables"
OUT.mkdir(parents=True, exist_ok=True)


def table_sample() -> None:
    df = pd.read_parquet(PANEL)
    gold = df.drop_duplicates("stock_code")
    ind = gold["industry"].value_counts()
    out = f"""# Table 1: Gold 표본 구성

**총 Gold 기업**: {len(gold)}개 (KSSB 2028 FY27 대상 ∩ KOSPI ∩ GIR ≥3yr)

## 업종 분포

| 업종 | 기업 수 |
|---|---|
"""
    for i, n in ind.items():
        out += f"| {i} | {n} |\n"
    out += f"\n**총계**: {len(gold)}"
    (OUT / "table01_sample.md").write_text(out, encoding="utf-8")
    print("[saved] table01_sample.md")


def table_coverage() -> None:
    df = pd.read_parquet(PANEL)
    df_analysis = df[df["year"].between(2019, 2023)]

    sources = {
        "GIR Scope 1": "gir_scope1_tco2eq",
        "ESG Scope 1": "esg_scope1_tco2eq",
        "위성 NO₂": "no2_mean",
        "위성 SO₂": "so2_mean",
        "위성 CO": "co_mean",
        "위성 HCHO": "hcho_mean",
        "ERA5 기상": "era5_t2m",
        "ERA5 BLH": "era5_blh",
        "MERRA-2": "merra2_pbltop",
        "ODIAC CO₂": "odiac_sum_tC_year",
        "ASOS 기온": "asos_avgTa_yr",
    }
    n_total = len(df_analysis)
    out = f"""# Table 2: 데이터 커버리지 매트릭스

**분석 기간**: 2019-2023, **기업 수**: {df_analysis['stock_code'].nunique()}, **총 패널 행**: {n_total}

| 데이터 | 가용 | 커버리지 % |
|---|---|---|
"""
    for name, col in sources.items():
        if col in df_analysis.columns:
            nn = df_analysis[col].notna().sum()
            out += f"| {name} | {nn}/{n_total} | {nn/n_total*100:.1f}% |\n"
    (OUT / "table02_data_coverage.md").write_text(out, encoding="utf-8")
    print("[saved] table02_data_coverage.md")


def table_patterns() -> None:
    if not MK.exists():
        return
    df = pd.read_csv(MK)
    pattern_desc = {
        "A_consistent_up": "일관 상승 (GIR·ESG·위성 모두 ↑)",
        "A_consistent_down": "일관 하강 (GIR·ESG·위성 모두 ↓)",
        "B_esg_suspect": "ESG 의심 (GIR·위성 일치, ESG 반대)",
        "C_gir_suspect": "GIR 의심 (ESG·위성 일치, GIR 반대)",
        "D_both_suspect": "최심각 (위성 ≠ GIR · ESG)",
        "mixed": "혼합 (부분 일치)",
        "E_no_trend": "무추세 (|τ|<0.4)",
    }
    out = f"""# Table 3: Mann-Kendall 4중 비교 패턴 분류

**분석**: Gold {len(df)}개사 × 4시계열 (GIR Scope 1, ESG Scope 1, 위성 NO₂, ODIAC CO₂)
**임계값**: |τ|≥0.4 방향 판정

## 패턴 분포

| 패턴 | 설명 | N | 기업 예시 |
|---|---|---|---|
"""
    for p, desc in pattern_desc.items():
        sub = df[df["pattern"] == p]
        if len(sub) == 0:
            continue
        examples = ", ".join(sub["corp_name"].str[:12].tolist()[:5])
        out += f"| **{p.split('_')[0]}** | {desc} | {len(sub)} | {examples} |\n"

    out += "\n## 핵심 발견 기업 (상세)\n\n"
    key_patterns = ["D_both_suspect", "C_gir_suspect", "A_consistent_up"]
    for p in key_patterns:
        sub = df[df["pattern"] == p]
        if len(sub) == 0:
            continue
        out += f"\n### {p.split('_', 1)[0]} — {pattern_desc[p]}\n\n"
        out += "| 기업 | GIR τ | ESG τ | NO₂ τ | ODIAC τ |\n|---|---|---|---|---|\n"
        for _, r in sub.iterrows():
            gir = f"{r['gir_tau']:+.2f}" if pd.notna(r["gir_tau"]) else "—"
            esg = f"{r['esg_tau']:+.2f}" if pd.notna(r["esg_tau"]) else "—"
            no2 = f"{r['no2_tau']:+.2f}" if pd.notna(r["no2_tau"]) else "—"
            od = f"{r['odiac_tau']:+.2f}" if pd.notna(r["odiac_tau"]) else "—"
            out += f"| {r['corp_name']} | {gir} | {esg} | {no2} | {od} |\n"
    (OUT / "table03_pattern_results.md").write_text(out, encoding="utf-8")
    print("[saved] table03_pattern_results.md")


def table_regression() -> None:
    if not HECKMAN.exists():
        out = "# Table 4: 패널 회귀 결과\n\n**상태**: Heckman 2-stage not yet run. Run `python src/analysis/heckman_selection.py`.\n"
    else:
        df = pd.read_csv(HECKMAN)
        out = "# Table 4: Heckman 2-Stage + Fixed Effects Panel\n\n"
        out += "## Stage 2 계수 (클러스터 SE + Bootstrap 95% CI)\n\n"
        out += "| 변수 | β | SE | 95% CI (Boot) |\n|---|---|---|---|\n"
        for _, r in df.iterrows():
            out += (f"| {r['var']} | {r['beta']:+.3f} | {r['se']:.3f} | "
                    f"[{r['ci_lower_boot']:+.3f}, {r['ci_upper_boot']:+.3f}] |\n")
    (OUT / "table04_regression.md").write_text(out, encoding="utf-8")
    print("[saved] table04_regression.md")


if __name__ == "__main__":
    table_sample()
    table_coverage()
    table_patterns()
    table_regression()
