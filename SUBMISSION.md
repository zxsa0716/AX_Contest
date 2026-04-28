# 2026 AX 아이디어 경진대회 — 최종 제출 인벤토리

**대회**: 2026 AX 아이디어 경진대회 (기후에너지환경부 주최, 한국전력공사 대표주관)
**부문**: 데이터 분석 > 자유과제 분석
**마감**: 2026-05-18 (월)
**제출자**: 김민철 (zxsa0716@kookmin.ac.kr · 국민대 기후변화 인공위성 연구실)
**제출일**: 2026-04-28
**저장소**: https://github.com/zxsa0716/AX_Contest (MIT License, public)

---

## 핵심 deliverable 5종 (최종 제출물)

### 1️⃣ 최종 보고서 (Final Report)

| 파일 | 형식 | 분량 | 내용 |
|---|---|---|---|
| `report/AX_contest_2026_final_report.pdf` | PDF | 5.1 MB | **본문 PDF** — 11장 + 부록 6종, 26 figures embedded, 917 lines markdown 변환 |
| `report/full_report_consolidated.md` | Markdown | 917 lines | 본문 원본 (편집·재현용) |

**보고서 구성** (총 11장 + 부록 A-F)
- 연구 요약 + 1장 배경 + 2장 선행 연구 + 3장 연구 설계 + 4장 데이터 + 5장 전처리 + 6장 분석 방법론 + 7장 분석 결과 (7.7 패턴군 통계 비교 포함) + 8장 한계 + 9장 정책 제언 + 10장 종합 논의 (10.6 국제 비교, 10.7 stakeholder Q&A 포함) + 11장 결론 (11.4 10년 로드맵 포함)
- 부록 A ADR · B 재현성 · C 자동화 시스템 · D Glossary · E firm-level τ 표 · F 발표 자료 인벤토리

### 2️⃣ 발표 자료 (5 thematic PPTX decks · 75 slides)

`report/decks/` 폴더 (`README.md` 포함)

| Part | 파일 | 슬라이드 | 시간 |
|---|---|---|---|
| 1 | `01_KeyFindings.pptx` | 16 | 12-17분 |
| 2 | `02_Background.pptx` | 10 | 8-10분 |
| 3 | `03_Data_Methodology.pptx` | 17 | 12-15분 |
| 4 | `04_PerFirm_Analysis.pptx` | 17 | 12-15분 |
| 5 | `05_Discussion_Policy.pptx` | 15 | 10-13분 |

**디자인**: 줄글식 한국어 prose · 고해상도 figure aspect-ratio 보존 · 일관 design token · cover/divider/content 3 layout · footer + page number

### 3️⃣ 발표 대본 (Presentation Script)

`report/presentation_script_01_KeyFindings.md` (30 KB)

- Part 1 16장 슬라이드 **하나하나** 줄글식 한국어 발표 대본
- 슬라이드별 발표 시간 (45-90초) · 강조 톤 가이드
- 부록 A: 심사위원 예상 질문 10건 + 모범 답변
- 부록 B: 발표 시간 배분 표 (12분 / 17분 / 20분 시나리오)
- 부록 C: 발표 톤 가이드 (속도·호흡·강조·시선·자세·마무리)

### 4️⃣ 시각화 산출물 (26 publication-quality figures)

`figs/*.png` (300 DPI, matplotlib + seaborn)

**핵심 figure 7종** (PPTX Part 1 결과 우선 deck에 사용):
- `fig_concept_4channel.png` — 4중 비교 conceptual diagram
- `fig_pattern_distribution.png` — 5개 패턴 분포 (D=2 firms 표시)
- `fig_posco_4channel_detail.png` — POSCO 4채널 detail (τ=±1.00 hero finding)
- `fig_industrial_no2_timeseries.png` — 4 산업시설 ERA5 보정 전후
- `fig_all23_normalized.png` — 23개사 4채널 정규화 시계열
- `fig_anomaly_2d.png` — 이상탐지 2D 분포
- `fig_priority_matrix.png` — 검증 우선순위 매트릭스

**기타 19종**: ODIAC 한국 지도(seasonal·change), Gold 23사 위치 지도, 패턴 매핑 지도, ASOS 지점, Heckman forest plot, SHAP summary/waterfall, GIR heatmap·timeseries, satellite scatter validation, industry boxplot 등.

### 5️⃣ 분석 코드 (Reproducible Analysis Pipeline)

`src/` 폴더 (Python 3.14 + pandas/numpy/scipy/statsmodels/scikit-learn/shap/pymannkendall/earthengine-api/rasterio/pdfplumber)

```
src/
├── preprocessing/   — 24 modules (수집·파싱·매칭)
├── analysis/        — 8 modules (panel·MK·anomaly·Heckman·SHAP·ERA5)
├── satellite/       — 6 modules (S5P·ODIAC·ASOS·validation)
├── visualization/   — 8 modules (figure 생성 + PPTX 생성)
└── run_all_analysis.py  — 통합 파이프라인
```

**전체 재현**: `git clone` → `.env.example` 복사 → `pip install -r requirements.txt` → `python src/run_all_analysis.py`.

---

## 핵심 발견 (5초 요약)

**Pattern D — 공시↑ vs 위성·ODIAC↓ 극단적 불일치**

| Firm | GIR τ | ESG τ | NO₂ τ | ODIAC τ | priority |
|---|---|---|---|---|---|
| **포스코홀딩스** | **+1.00** | +0.67 | **−1.00** | **−1.00** | 0.47 |
| **삼성전자** | +0.60 | **+1.00** | −0.40 | −0.40 | 0.32 |

이 두 사례는 모두 KSSB 2028 1차 의무공시 적용 대상. 본 연구는 KSSB 시행 직전 검증 자원의 차등 배분 정책 설계에 즉시 활용 가능하다.

**3가지 정책 제언 (즉시 활용 경로)**
1. KEITI 환경책임투자 플랫폼에 **DRI(Disclosure Reliability Index)** 신설
2. priority_score 기반 **3-tier 차등 검증 매트릭스** (47% 비용 절감)
3. KSSB 제2호 시행령에 **GIR-ESG 대조표 첨부 + 위성 모니터링 연계** 의무화

---

## 폴더 구조 (최종 제출 시점)

```
AX_contest/
├── CLAUDE.md                         # 프로젝트 디렉터 모드 + 프로젝트 사실
├── README.md                         # 저장소 안내
├── SUBMISSION.md                     # 본 문서 — 제출 인벤토리
├── LICENSE                           # MIT
├── requirements.txt                  # Python 의존성
├── .env.example                      # API 키 템플릿
├── .gitignore                        # data/raw, logs, .pid 제외
│
├── .claude/                          # Claude Code 디렉터 + 6 에이전트 시스템
│   ├── agents/                       # 6 specialist subagents
│   ├── commands/                     # 6 slash commands
│   ├── skills/                       # 2 영구 skills
│   └── settings.json
│
├── decisions/                        # 4 ADRs (의사결정 이력)
│
├── report/                           # ⭐ 최종 제출 deliverables
│   ├── AX_contest_2026_final_report.pdf  ⭐ 본문 PDF (5.1 MB)
│   ├── full_report_consolidated.md   ⭐ 본문 markdown (917 lines)
│   ├── presentation_script_01_KeyFindings.md  ⭐ 발표 대본 (30 KB)
│   ├── audit_pptx_completeness.md    # PPT 완성도 audit memo
│   ├── decks/                        ⭐ 5개 thematic PPTX decks
│   │   ├── 01_KeyFindings.pptx       (16 slides)
│   │   ├── 02_Background.pptx        (10 slides)
│   │   ├── 03_Data_Methodology.pptx  (17 slides)
│   │   ├── 04_PerFirm_Analysis.pptx  (17 slides)
│   │   ├── 05_Discussion_Policy.pptx (15 slides)
│   │   └── README.md
│   ├── tables/                       # 4 supporting tables
│   │   ├── table01_sample.md
│   │   ├── table02_data_coverage.md
│   │   ├── table03_pattern_results.md
│   │   └── table04_regression.md
│   └── archive/                      # 중간 작업물 (연구 evolution 추적용)
│
├── figs/                             ⭐ 26 publication-quality figures (PNG, 300 DPI)
│
├── src/                              ⭐ 분석 코드 파이프라인
│   ├── preprocessing/                # 24 모듈
│   ├── analysis/                     # 8 모듈
│   ├── satellite/                    # 6 모듈
│   ├── visualization/                # 8 모듈
│   │   └── archive/                  # v1 PPTX generator
│   └── run_all_analysis.py           # 통합 파이프라인
│
├── data/
│   ├── README.md                     # 데이터 출처·SHA-256 기록
│   ├── schema/                       # 데이터 딕셔너리 2종
│   ├── GIR명세서/                   # 7개년 (gitignored)
│   ├── GIR목표관리/, GIR할당대상/, GIR검증기관/
│   ├── KCGS ESG 등급/                # 9 PDFs
│   ├── KOSPI200/                     # 5 CSV (인덱스 일별 시세)
│   ├── NIR인벤토리/, 사전할당/, 통합환경허가/, 할당계획 변경공고/
│   └── (data/raw/, data/interim/, data/processed/는 gitignored)
│
└── 참고/                             # 공모전 원본 자료 (read-only)
    ├── 2026 AX 아이디어 경진대회 홍보책자.pdf
    ├── data_acquisition_guide.html
    ├── final_methodology_report.html
    ├── methodology_roundtable.html
    └── research_plan_AX2026.html
```

---

## 심사 5대 기준 매핑

| 기준 | 본 연구의 대응 |
|---|---|
| **분석기법 타당성** | 8단계 파이프라인 학술 표준 — Mann-Kendall, Heckman 2-stage, IF+LOF+MK 3층 앙상블, ERA5 다중회귀 잔차, SHAP TreeExplainer interventional, Bootstrap B=2000 firm-block CI |
| **데이터 전처리** | 18 데이터셋 통합, 4단계 QC, MICE imputation, ESG 자동 수집·파싱 파이프라인 (90.4% 커버리지), VWorld 지오코딩 |
| **인사이트 독창성** | 한국 firm-level GIR-ESG-위성-ODIAC 4중 비교 최초 적용, 새로운 4채널 패턴 분류 체계 (A·B·C·D·E), KCGS 등급조정 supervised label 부분 지도학습 |
| **결과의 유의성** | 패턴 D 2 firms (POSCO τ=±1.00, 삼성전자), Heckman ln(GIR) 계수 -2.00 [-8.93, -0.21] 유의, Kruskal-Wallis H=17.42 p<0.01, Fisher p=0.018 |
| **활용 방안** | KEITI DRI · 우선순위 매트릭스 (47% 비용 절감) · KSSB 시행령 4가지 요건 · CBAM 대응 · 10년 로드맵 |

---

## 외부 재현성

```bash
git clone https://github.com/zxsa0716/AX_Contest.git
cd AX_Contest
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt

# .env에 API 키 입력 (VWORLD/DART/GEE/KMA — 모두 무료)
cp .env.example .env

# 전체 분석 파이프라인 실행
python src/run_all_analysis.py

# 발표 자료 5개 deck 동시 생성
python src/visualization/generate_pptx_v2.py

# 보고서 PDF 변환
python -c "from markdown_pdf import MarkdownPdf, Section; from pathlib import Path; \
  pdf=MarkdownPdf(toc_level=3); \
  pdf.add_section(Section(Path('report/full_report_consolidated.md').read_text(encoding='utf-8'), root='report')); \
  pdf.save('report/AX_contest_2026_final_report.pdf')"
```

---

**문의**: zxsa0716@kookmin.ac.kr (국민대학교 기후변화 인공위성 연구실)

본 연구는 [Claude Code](https://claude.ai/code) (Anthropic Claude Opus 4.7) **디렉터 + 6 전문 서브에이전트** 시스템 위에 구축됐다. 모든 분석·코드·문서 작성 과정은 4 ADR + GitHub commit history로 추적 가능하다.
