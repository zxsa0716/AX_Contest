# Schema: gir_manifest_panel.parquet

**Source**: data/GIR명세서/*.xls (7 files, 2018-2024)  
**Output**: data/interim/gir_manifest_panel.parquet  
**Builder**: src/preprocessing/consolidate_gir.py  
**Rows**: 7,998 | **Unique firms (normalized)**: 1,585  
**Unit**: tCO₂eq (Scope 1 direct emissions, site-level)

## Column Dictionary

| Column | Korean Name | Type | Example | Role | Notes |
|--------|-------------|------|---------|------|-------|
| year | 대상연도 | int | 2023 | key | Parsed from filename, overrides 대상년도 column |
| 법인명 | 법인명 | str | "주식회사 포스코" | key | Original legal name, raw |
| 법인명_normalized | 법인명 (정규화) | str | "포스코" | match-key | Lowercase, no whitespace, no legal-form prefixes |
| 관장기관 | 관장기관 | str | "산업통상자원부" | control | Ministry responsible for this firm |
| 지정구분 | 지정구분 | str | "사업장" | control | "사업장" (site-level) or "업체" (company-level). CRITICAL: affects aggregation |
| 지정업종 | 지정업종 | str | "1차 철강 제조업" | control | Sector. Source column has HTML `<br />` stripped |
| scope1_tco2eq | 온실가스 배출량 | float | 71971881.0 | value | Scope 1 direct GHG emissions in tCO₂eq. Site-level. |
| energy_tj | 에너지 사용량 | float | 1191.0 | value | Energy consumption in TJ |
| 검증수행기관 | 검증수행기관 | str | "(재)한국품질재단" | control | Third-party verifier name; 7,997/7,998 non-null |
| file_source | 파일 경로 | str | "data/GIR명세서/..." | meta | Source xls file path |

## Aggregation Notes

- This table is **site-level** (사업장 level).
- To get company-level Scope 1: groupby `법인명_normalized` (or `사업자등록번호` when available) and sum `scope1_tco2eq`.
- `지정구분 == "업체"` rows are already company-aggregates — do not double-count.
- Year 2024 data is preliminary (배출량 신고 전 확정 전).

## Known Issues

- No `사업자등록번호` (business registration number) in source — entity matching relies on normalized company name.
- Schema is identical across all 7 years (no drift detected).
- `고성그린파워 주식회사` appears twice in 2023 top-20 — likely dual-site reporting. Normal.
