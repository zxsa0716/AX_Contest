# CLAUDE.md Patch Proposal v2 — Wave 3 additions

**Status**: Proposal only — do NOT edit CLAUDE.md directly. Director to review and apply.
**Date**: 2026-04-22
**Prepared by**: corp-data-manager

---

## Patch 1: Update "6개 데이터셋" → "17+ 데이터셋"

### Current text (CLAUDE.md line 47-54):

```
### 6개 데이터셋
- **A**: GIR 관리업체 명세서 (data.go.kr, CSV 5개년, encoding=cp949)
- **A-2**: GIR 할당대상업체 주소 → Kakao Local API 지오코딩
- **B**: KRX ESG 포털 + DART 지속가능경영보고서 PDF (GRI 305-1 파싱)
- **C**: Sentinel-5P NO₂ (GEE COPERNICUS/S5P/OFFL/L3_NO2)
- **C-2**: Sentinel-5P SO₂ (GEE COPERNICUS/S5P/OFFL/L3_SO2)
- **D**: DART Open API 재무 + ERA5 기상 (GEE ECMWF/ERA5_LAND/HOURLY)
```

### Replacement text:

```
### 17+ 데이터셋 (ADR-002 기준 Tier 1 확장, 2026-04-20)

**Tier 1 — 법정·공공 배출량**
- **A**: GIR 관리업체 명세서 (data.go.kr, xls 7개년 2018-2024, cp949)
- **A-2**: GIR 할당대상업체 지정현황 (주소 → Kakao Local API 지오코딩)
- **A-3**: K-ETS 사전할당 1~4차 CSV (data.go.kr, cp949)
- **A-4**: GIR 검증의견 공시 (data.go.kr)
- **A-5**: K-ETS 할당계획 변경공고 (HWP/HWPX/PDF 18개 파일, supervised label 소스)

**Tier 1 — 기업 ESG 자체보고**
- **B**: KRX ESG 포털 지속가능경영보고서 + DART 자율공시 (GRI 305-1 파싱)
  - 자동화 수집: `src/preprocessing/sustainability_report_collector.py`
  - 자동화 파싱: `src/preprocessing/sustainability_report_parser.py`
- **B-2**: DART 사업보고서 II.6 (매출 지역별 분포 → 국내매출비율)

**Tier 1 — 시장·샘플 기준**
- **C**: KOSPI200 구성종목 → 자본총계 기반 proxy (Wave 3 구현)
  - `src/preprocessing/kospi200_proxy.py`
- **C-2**: KCGS ESG 등급 (2017-2025, 분기별 등급조정 포함)
  - 집계배포: 완료 | 개별사 등급: 분기조정 PDFs에서 21건 추출

**Tier 1 — 위성·기상**
- **D**: Sentinel-5P NO₂ (GEE COPERNICUS/S5P/OFFL/L3_NO2)
- **D-2**: Sentinel-5P SO₂ (GEE COPERNICUS/S5P/OFFL/L3_SO2)
- **D-3**: Sentinel-5P CO (GEE COPERNICUS/S5P/OFFL/L3_CO) — 장수명 불완전연소
- **D-4**: Sentinel-5P HCHO (GEE COPERNICUS/S5P/OFFL/L3_HCHO) — 석유화학 VOC
- **E**: DART 재무제표 (DART API, 연결/개별재무제표)
- **E-2**: ERA5 기상 (GEE ECMWF/ERA5_LAND/HOURLY)

**Tier 1 — 4중 비교 (ADR-003)**
- **F**: ODIAC v2024 CO₂ 1km (NIES 포털) — 직접 CO₂ top-down 비교
- **F-2**: NIR 국가 온실가스 인벤토리 CSV (국가총량 대비 비중 계산)
- **F-3**: KRX KOSPI200 인덱스 일별 시세 (macro control, data/KOSPI200/ 5 CSV)
```

---

## Patch 2: 폴더 규칙 표에 sustainability_reports 추가

### Append to 폴더 규칙 table:

```
| `data/raw/sustainability_reports/` | 다운로드된 ESG보고서 PDF ({stock_code}/{year}.pdf) | corp-data-manager |
```

---

## Patch 3: 새 섹션 추가 — "자동화된 데이터 수집 시스템 (영구 기능)"

**Insert after 폴더 규칙 table:**

```
---

## 자동화된 데이터 수집 시스템 (영구 기능)

Wave 3에서 구현된 자동화 파이프라인. 최종 제출물의 시스템 아키텍처 구성요소.

### 지속가능경영보고서 수집기 (sustainability_report_collector.py)

`src/preprocessing/sustainability_report_collector.py`

- **Sources (fallback 순서)**: DART 자율공시 → KRX ESG 포털 (Selenium) → IR 페이지
- **DART 동작 방식**: '지속가능경영보고서등관련사항(자율공시)' 검색 → rcept_no 획득
  → attach_doc_list로 첨부 PDF URL 시도 → 없으면 DART 뷰어 URL 기록 (수동 다운로드)
- **알려진 제약**: 삼성전자·대기업 대부분이 PDF를 회사 IR 사이트에만 게시하고
  DART에는 URL만 링크 → KRX ESG 포털 또는 IR 직접 스크래핑 필요
- **SHA-256 중복제거**: 재다운로드 방지
- **출력**: `data/raw/sustainability_reports/{stock_code}/{year}_sustainability.pdf`
  + `data/raw/sustainability_reports/_download_log.jsonl`

### GRI 305-1 파서 (sustainability_report_parser.py)

`src/preprocessing/sustainability_report_parser.py`

- **추출 항목**: Scope 1, Scope 2 (location/market), Scope 3, 조직경계, 제3자검증, 보고기준
- **신뢰도 플래그**: HIGH (표 + 단위 동행) / MEDIUM (정규식 + 단위 근접) / LOW (텍스트 검색)
- **단위 정규화**: tCO₂eq, 천tCO₂eq, MtCO₂eq → tCO₂eq 자동 변환
- **출력**: `data/interim/esg_reports_parsed.csv`

### CLI 사용법

```bash
# 전체 Gold 기업 수집
python src/preprocessing/sustainability_report_collector.py \
  --targets data/interim/gold_corps.csv \
  --years 2019-2023 \
  --sources dart,krx

# 파싱
python src/preprocessing/sustainability_report_parser.py \
  --reports-dir data/raw/sustainability_reports \
  --out data/interim/esg_reports_parsed.csv

# 단일 파일 테스트
python src/preprocessing/sustainability_report_parser.py \
  --single path/to/report.pdf --corp-code 00126380 --year 2022
```

### KOSPI200 Proxy (kospi200_proxy.py)

`src/preprocessing/kospi200_proxy.py`

KRX 접근 차단 상황의 우회책. DART 자본총계 기준 상위 200개사 = KRX 공식 KOSPI200과
90-95% 일치 추정.

- **입력**: `data/interim/kospi_all_corp_index.parquet` (789사), `kospi_asset_full.parquet`
- **출력**: `data/interim/kospi200_proxy_{year}.parquet` per year + `_multiyear.parquet`
- **방법론 주의**: 자본총계 ≠ 시가총액. 금융지주·자본집약 업종 불일치 가능.

---

## 최종 제출물에 포함된 자동화 시스템

공모전 제출 보고서에 다음을 명시:

- `sustainability_report_collector.py`: 한국 코스피 기업의 지속가능경영보고서를
  DART/KRX/IR 3중 소스에서 자동 수집하는 파이프라인 (PDF 저장, SHA-256 기록, 재시도 로직)
- `sustainability_report_parser.py`: GRI 305-1 Scope 1 자동 추출기 (신뢰도 플래그, 단위정규화)
- 재현가능성: `src/preprocessing/` 모든 스크립트 공개, `.env` 키 설정 후 즉시 재실행 가능
```

---

## Patch 4: KOSPI200 데이터 주의사항 추가

### Add to 중요 주의사항:

```
- **KOSPI200 구성종목**: KRX 공식 API 2026년 차단. `kospi200_proxy.py`로 DART 자본총계
  기반 proxy 사용. `data/KOSPI200/` 5개 CSV는 KOSPI200 인덱스 일별 시세(매크로 통제변수)
  이며 구성종목 명단이 아님.
```
