# 한국 코스피 상장기업 온실가스 공시 신뢰성 3중 검증

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![Status: Submission Ready](https://img.shields.io/badge/status-submission_ready-green.svg)]()

**2026 AX 아이디어 경진대회** 자유분석 부문 응모작 · 마감 2026-05-18

> 한국 기업의 GIR 법정 배출량 × ESG 자체보고 × Sentinel-5P 위성 NO₂·SO₂·CO·HCHO × ODIAC CO₂를 4중 비교하여 공시 불일치 패턴을 식별하고, 2028년 KSSB 의무공시 검증체계 설계안을 제시하는 데이터 분석 프로젝트.

**📋 [SUBMISSION.md](SUBMISSION.md)** — 최종 제출 인벤토리 (5종 deliverable + 폴더 구조 + 재현성 가이드)

---

## 🎯 핵심 결과

### Pattern D (최심각): 공시↑ but 위성·ODIAC↓ — 2개사
| 기업 | GIR τ | ESG τ | NO₂ τ | ODIAC τ |
|---|---|---|---|---|
| **포스코홀딩스** | +1.00 | +0.67 | **−1.00** | **−1.00** |
| **삼성전자** | +0.60 | +1.00 | −0.40 | −0.40 |

### 분석 규모
- **Gold 23개사** × 5년 (2019~2023) = 115 firm-year 패널
- **18개 데이터셋** 통합 (GIR · 126 ESG PDFs · Sentinel-5P 4종 · ODIAC · ERA5 · MERRA-2 · ASOS · DART · KCGS · K-ETS · VWorld 등)
- **이상탐지 3층 앙상블** (Isolation Forest + LOF × Mann-Kendall × KCGS supervised)
- **Heckman 2-stage** + Bootstrap 95% CI
- **ERA5 기상보정** R² 0.67-0.94

### 정책 제언 3가지
1. **KEITI 환경책임투자 플랫폼**에 4중 검증 신뢰성 지수(DRI) 편입
2. **우선순위 매트릭스** 기반 KSSB 2028 49개사 차등 검증 자원 배분
3. **KSSB 제2호 시행령**에 GIR-ESG 대조표 첨부 + 위성 모니터링 연계 의무화

---

## 📁 프로젝트 구조

```
AX_contest/
├── CLAUDE.md              # Claude Code 디렉터 모드 + 프로젝트 사실
├── .claude/
│   ├── agents/            # 6 specialist subagents
│   ├── commands/          # 6 slash commands
│   ├── skills/            # 2 permanent skills (재사용 가능)
│   └── settings.json
├── 참고/                  # 공모전 원본 자료
├── data/
│   ├── raw/               # 원본 데이터 (gitignored — SHA-256만 기록)
│   ├── interim/           # 중간 전처리 결과 (gitignored)
│   ├── processed/         # 최종 분석 결과
│   └── schema/            # 데이터 딕셔너리
├── src/
│   ├── preprocessing/     # 12 modules (수집·파싱·매칭)
│   ├── analysis/          # 8 modules (panel·MK·anomaly·Heckman·SHAP·ERA5)
│   ├── satellite/         # 4 modules (S5P·ODIAC·ASOS·validation)
│   └── visualization/     # 5 modules (10 figures)
├── notebooks/             # 탐색적 분석
├── figs/                  # 10 publication figures (300DPI)
├── report/                # 13 markdown drafts + final consolidated
│   ├── full_report_consolidated.md  # 제출용 통합 보고서
│   ├── executive_summary.md         # 1페이지 요약
│   └── final_section{02-08}_*.md    # 본문 섹션
├── decisions/             # 4 ADRs (의사결정 이력)
├── requirements.txt
├── .env.example           # API 키 템플릿
└── .gitignore
```

---

## 🚀 재현 방법

### 1. 환경 구축

```bash
git clone https://github.com/{your-username}/AX_contest_2026.git
cd AX_contest_2026
python -m venv .venv
.venv\Scripts\activate              # Windows
# source .venv/bin/activate         # Mac/Linux
pip install -r requirements.txt
```

### 2. API 키 발급 (5분)

`.env.example`을 `.env`로 복사 후 발급받아 입력:

| 키 | 발급처 | 무료 한도 |
|---|---|---|
| `VWORLD_API_KEY` | [vworld.kr](https://www.vworld.kr/v4po_oprn_s001.do) | 40,000/일 |
| `DART_API_KEY` | [opendart.fss.or.kr](https://opendart.fss.or.kr) | 10,000/일 |
| `GEE_PROJECT_ID` | [earthengine.google.com](https://earthengine.google.com) | 학술 무료 |
| `KMA_API_KEY_DECODED` | [data.kma.go.kr](https://data.kma.go.kr) | 20,000/일 |

### 3. 데이터 수집 + 전처리 (약 6-8시간)

```bash
# 자동화된 ESG 보고서 수집 (DART + KRX + IR fallback)
.venv\Scripts\python.exe src/preprocessing/sustainability_report_collector.py \
  --targets data/interim/gold_corps.csv --years 2019-2023

# GRI 305-1 자동 파싱
.venv\Scripts\python.exe src/preprocessing/sustainability_report_parser.py \
  --reports-dir data/raw/sustainability_reports \
  --out data/interim/esg_reports_parsed.csv

# 위성 + 기상 추출 (GEE, 약 8시간)
.venv\Scripts\python.exe src/satellite/extract_satellite_panel.py \
  --sites data/interim/gold_sites.csv

# ODIAC 60개월 다운로드 + zonal stats
.venv\Scripts\python.exe src/satellite/extract_odiac.py \
  --sites data/interim/gold_sites.csv

# ASOS 5년치
.venv\Scripts\python.exe src/satellite/extract_asos.py \
  --sites data/interim/gold_sites.csv
```

### 4. 전체 분석 + 시각화 (약 5분)

```bash
.venv\Scripts\python.exe src/run_all_analysis.py
```

→ `data/processed/integrated_panel.parquet` (157 × 51), `trend_mk.csv`, `anomaly_classification.csv`, `heckman_results.csv`, `shap_values.csv`, `priority_ranking.csv` 자동 생성  
→ `figs/*.png` 10개, `report/tables/*.md` 4개 자동 재생성

---

## 🤖 Claude Code 디렉터 + 6 에이전트 시스템

이 프로젝트는 [Claude Code](https://claude.ai/code) CLI에서 **디렉터(Opus) + 6 전문 서브에이전트** 구조로 진행됐습니다.

| Agent | 역할 | 모델 |
|---|---|---|
| `policy-expert` | KEITI·환경부·KSSB·CBAM 정책 | Opus |
| `corp-data-manager` | GIR·KRX·DART 수집·전처리 | Sonnet |
| `esg-expert` | GRI 305-1·GHG Protocol·Scope | Opus |
| `data-analyst` | 패널회귀·Heckman·MK·SHAP | Opus |
| `algo-researcher` | Sentinel-5P·GEE·선행연구 | Opus |
| `report-writer` | 보고서·피규어·Gamma | Sonnet |

상세는 `.claude/agents/` 참고. 슬래시 커맨드 6개 (`/consult /roundtable /standup /handoff /decision /paper`) + Skills 2개 (sustainability-report-collect, esg-scope-extract).

---

## 🎤 발표 자료 (5 themed PPTX decks · 67 slides 합계)

기존 단일 60 슬라이드 deck를 5개 thematic deck로 재구성. 각 deck는 단독으로도 완결되며, 발표 시간에 따라 유연 선택 가능. 모든 deck는 script-style flowing Korean prose + uncropped 고해상도 figures + 일관된 design token 적용.

| Deck | 파일명 | 슬라이드 | 내용 |
|---|---|---|---|
| **Part 1** | `report/decks/01_KeyFindings.pptx` | 16 | 결정적 발견 우선 — 패턴 D 2건, 이상탐지 8건, Heckman, 패턴군 통계 비교, 우선순위, 정책 |
| **Part 2** | `report/decks/02_Background.pptx` | 10 | 연구 배경 — 두 채널 ESG 문제, KSSB 2028, 검증 공백, 선행연구 |
| **Part 3** | `report/decks/03_Data_Methodology.pptx` | 17 | 18 데이터셋 + 8단계 분석 파이프라인 + GIR baseline + 4채널 cross-validation |
| **Part 4** | `report/decks/04_PerFirm_Analysis.pptx` | 17 | 23개사 × 8 산업군 firm-by-firm + GIR heatmap + case studies |
| **Part 5** | `report/decks/05_Discussion_Policy.pptx` | 15 | 패턴 D 가설 3, 한계 4, robustness 8, 정책 카드 3, 국제비교, stakeholder Q&A, 10년 로드맵, 결론 |

**생성 명령**: `.venv\Scripts\python.exe src/visualization/generate_pptx_v2.py`

---

## 📊 주요 산출물 (26 figures)

| Figure | 내용 |
|---|---|
| `fig_gir_timeseries.png` | Gold 23사 GIR 5년 추이 |
| `fig_gir_heatmap.png` | 기업×연도 GIR 히트맵 (log scale) |
| `fig_satellite_scatter.png` | GIR vs NO₂/SO₂/CO/HCHO 4-panel |
| `fig_odiac_scatter.png` | GIR vs ODIAC CO₂ 1:1 비교 |
| `fig_case_studies.png` | POSCO/현대제철/SK하이닉스/삼성전자 시계열 |
| `fig_pattern_distribution.png` | 패턴 A/B/C/D/E 분포 |
| `fig_mk_tau_forest.png` | 23사 × 3시계열 Mann-Kendall τ |
| `fig_shap_summary.png` | SHAP beeswarm |
| `fig_shap_waterfall_top5.png` | 상위 5 이상 firm waterfall |
| `fig_priority_matrix.png` | 검증 우선순위 매트릭스 (KSSB 49사) |

---

## 🎓 인용

```bibtex
@misc{ax_contest_2026,
  title  = {한국 코스피 상장기업 온실가스 공시 신뢰성 3중 검증:
            GIR × ESG × Sentinel-5P 위성 4중 비교와 KSSB 2028 의무공시 검증체계},
  author = {Researcher},
  year   = {2026},
  url    = {https://github.com/{your-username}/AX_contest_2026},
  note   = {2026 AX 아이디어 경진대회 자유분석 부문 응모작}
}
```

---

## 📜 라이선스

- **소스 코드**: MIT License (`LICENSE`)
- **데이터**: 각 출처 (GIR/DART/Sentinel-5P/ODIAC/KCGS 등) 별도 라이선스 적용. 데이터 파일은 본 저장소에 포함되지 않음.

---

## 🙏 감사

- 본 연구는 [Claude Code](https://claude.ai/code) (Anthropic Claude Opus 4.7) 디렉터 시스템 위에 구축됐습니다.
- 6명의 전문 서브에이전트 협업 + 4개 ADR 의사결정 추적으로 5주 단독 연구 완성.
- 데이터 출처: 환경부 GIR · 금융감독원 DART · 한국거래소 · 국토교통부 VWorld · 기상청 · ESA Copernicus · NASA ECMWF · NIES (Japan)

---

**문의**: zxsa0716@kookmin.ac.kr
