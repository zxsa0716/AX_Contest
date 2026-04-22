---
name: esg-scope-extract
description: Parse downloaded sustainability report PDFs to extract GRI 305-1 Scope 1 emissions (tCO2eq), Scope 2, Scope 3, third-party assurance metadata, organizational boundary, and reporting standard. Assigns HIGH/MEDIUM/LOW confidence flags.
---

## When to invoke

Use this skill when the user asks to:
- "GRI 305-1 값 추출해줘"
- "Scope 1 파싱해줘"
- "ESG 보고서에서 배출량 데이터 뽑아줘"
- Extract assurance provider or standard from a sustainability report
- Parse all downloaded sustainability report PDFs in batch

## Inputs

| Input | How to provide | Required |
|---|---|---|
| `reports-dir` | Directory with `{stock_code}/{year}*.pdf` structure | Required (batch mode) |
| `--single` | Path to single PDF file | Alternative to batch |
| `--corp-code` | 8-digit DART corp_code (for single mode) | Recommended |
| `--year` | Fiscal year integer (for single mode) | Recommended |

## How to invoke

```bash
# Batch: parse all downloaded PDFs
python src/preprocessing/sustainability_report_parser.py \
  --reports-dir data/raw/sustainability_reports \
  --out data/interim/esg_reports_parsed.csv

# Single file test
python src/preprocessing/sustainability_report_parser.py \
  --single data/raw/sustainability_reports/005930/2022_sustainability.pdf \
  --corp-code 00126380 \
  --year 2022
```

## Outputs

| File | Columns |
|---|---|
| `data/interim/esg_reports_parsed.csv` | corp_code, year, scope1_tco2eq, scope1_confidence, scope2_location_tco2eq, scope2_market_tco2eq, scope3_present, scope3_categories_raw, organizational_boundary, reporting_standard, third_party_assurance, assurance_standard, assurance_level, assurance_provider, parse_success |

## Confidence flag definitions

| Level | Condition |
|---|---|
| `HIGH` | Value extracted from pdfplumber table + unit (tCO₂eq/MtCO₂eq) in same cell/row |
| `MEDIUM` | Value found by regex + unit found within 2 lines; OR table extraction without unit |
| `LOW` | Value found in text search only, no unit confirmation in window |

**Rule**: Only `HIGH` and `MEDIUM` values enter the primary analysis panel. `LOW` goes to manual review.

## Unit normalization

All values normalized to `tCO₂eq`:
- `tCO₂eq`, `tCO₂e`, `t-CO₂eq` → ×1
- `천tCO₂eq`, `ktCO₂eq` → ×1,000
- `MtCO₂eq`, `백만톤` → ×1,000,000

## What this skill cannot do

- Parse scanned image PDFs (needs OCR — not implemented)
- Handle password-protected PDFs
- Guarantee correct extraction if GRI table spans multiple pages in unusual layouts
- Match Korean company names across PDFs to `corp_code` automatically — path-based inference only

## After parsing

The output `esg_reports_parsed.csv` feeds into:
1. `data/processed/panel_main.parquet` — joined with GIR data on `corp_code` + `year`
2. Scope 1 discrepancy analysis: `GIR_scope1 - ESG_scope1` gap calculation
3. Heckman 1st stage: `esg_scope1_domestic_split` + `third_party_assurance` as selection variables

Flag columns for director review:
- `scope1_confidence == 'LOW'` → manual review required before including in panel
- `parse_success == False` → add to `data/interim/failures_esg_parse.csv`
- Ambiguous `총배출량` label → do NOT use; flag for esg-expert consultation
