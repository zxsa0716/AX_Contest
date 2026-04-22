---
name: sustainability-report-collect
description: Collect Korean company sustainability reports (지속가능경영보고서) from DART, KRX ESG portal, and IR pages for target companies over years 2019-2023. Downloads PDFs, records SHA-256, and logs all results.
---

## When to invoke

Use this skill when the user asks to:
- "지속가능경영보고서를 다운로드해줘"
- "ESG 보고서 PDF 수집해줘"
- Collect sustainability reports for a list of companies
- Download GRI reports for the Gold/Silver sample
- Resume a partially-completed report collection

## Inputs

| Input | How to provide | Required |
|---|---|---|
| `corp_list.csv` | Path to CSV with columns: `corp_code`, `stock_code`, `corp_name` | Required (or --corp-codes) |
| Year range | e.g. `2019-2023` | Default: 2019-2023 |
| Sources | `dart,krx,ir` | Default: dart,krx |
| Single corp_code | e.g. `00126380` | Alternative to CSV |

## How to invoke

```bash
# Standard: full Gold corps list
python src/preprocessing/sustainability_report_collector.py \
  --targets data/interim/gold_corps.csv \
  --years 2019-2023 \
  --sources dart,krx

# Demo: single company
python src/preprocessing/sustainability_report_collector.py \
  --corp-codes 00126380 \
  --years 2022-2023 \
  --sources dart

# Resume (skips already-downloaded)
python src/preprocessing/sustainability_report_collector.py \
  --targets data/interim/gold_corps.csv \
  --years 2019-2023 \
  --sources dart,krx
```

## Outputs

| File | Description |
|---|---|
| `data/raw/sustainability_reports/{stock_code}/{year}_sustainability.pdf` | Downloaded PDF |
| `data/raw/sustainability_reports/_download_log.jsonl` | Line-delimited JSON log with url, sha256, status per download |

## Important behavior notes

1. **DART source**: Searches for `지속가능경영보고서등관련사항(자율공시)` filings. Most large-cap Korean companies (Samsung, SK, LG, POSCO) file a voluntary disclosure on DART but store the actual PDF on their corporate IR website — not on DART servers. For these, the collector logs `url_found_no_direct_pdf` with the DART viewer URL.

2. **KRX ESG source**: Attempts undocumented KRX API first. Selenium ChromeDriver fallback available but requires manual setup. Most KRX reports also redirect to company IR sites.

3. **Direct PDF companies**: Mid-cap companies sometimes upload PDFs directly to DART. The `attach_doc_list` API call finds these automatically.

4. **Resume-safe**: Already-downloaded files are detected by SHA-256 match and skipped.

5. **Rate limiting**: 1 request/second per thread, 5 threads max. Do not increase above 10 threads to avoid DART API blocks.

## Known limitations

- Samsung Electronics, Hyundai, SK Innovation: PDF on corporate website only, requires manual IR page visit
- KRX ESG portal: JS-rendered, requires Selenium + ChromeDriver for full automation
- Minimum viable result: DART detects filing existence + viewer URL for all 5 years per company

## After collection

Run the parser:
```bash
python src/preprocessing/sustainability_report_parser.py \
  --reports-dir data/raw/sustainability_reports \
  --out data/interim/esg_reports_parsed.csv
```

Or use the `/skill esg-scope-extract` skill.
