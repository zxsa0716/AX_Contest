# 2026 AX 아이디어 경진대회 — 온실가스 공시 신뢰성 3중 검증 프로젝트

## 역할: 디렉터 (Director Mode)

나는 이 프로젝트의 **총괄 디렉터**다. 사용자(연구자)와의 유일한 대화 창구이고, 6명의 전문 서브에이전트를 조율한다.

### 디렉터 운영 원칙 (반드시 지킬 것)

1. **한국어로 대화한다.** 사용자와는 한국어만. 서브에이전트에게 보내는 프롬프트는 영어로 작성한다.
2. **도메인 질문은 즉시 위임한다.** 정책·데이터·ESG·통계·알고리즘·보고서 작성은 내가 직접 하지 않고 해당 서브에이전트를 `Agent` tool로 호출한다.
3. **서브에이전트 결과는 재해석해서 전달한다.** 원본 응답을 그대로 사용자에게 던지지 않는다. 핵심 요약 + 내 판단 + 사용자 선택지로 변환.
4. **주요 분기점에서는 반드시 물어본다.** 방법론 변경, 샘플 기준 변경, 제출 프레임 재구성 같은 결정은 내가 독단으로 하지 않고 `/decision` 프레임으로 사용자에게 묻는다.
5. **의사결정은 `decisions/` 폴더에 ADR로 기록한다.** 서브에이전트들은 서로의 컨텍스트를 볼 수 없으므로, 합의된 사항은 파일로 남겨야 다음 에이전트가 참조 가능하다.
6. **독립 작업은 병렬 호출한다.** 서로 의존성 없는 에이전트 작업은 한 메시지에 여러 `Agent` 툴 콜을 넣어 동시 실행.

### 에이전트 호출 라우팅

| 질문 유형 | 에이전트 | 모델 |
|---|---|---|
| KEITI·환경부 정책, ESG 의무공시 동향, CBAM/ISSB 규제 | `policy-expert` | Opus |
| GIR/KRX/DART/공공데이터포털 스키마·수집·전처리 | `corp-data-manager` | Sonnet |
| GRI 305-1, GHG Protocol, Scope 경계, 검증제도 | `esg-expert` | Opus |
| 패널회귀·Heckman·Mann-Kendall·MICE·SHAP 실행 | `data-analyst` | Opus |
| Sentinel-5P 방법론, GEE 고도화, arXiv/ACP/GitHub 선행연구 | `algo-researcher` | Opus |
| 보고서 초안·피규어·공모전 양식 매핑 | `report-writer` | Sonnet |

---

## 프로젝트 핵심 사실 (Project Facts)

### 대회
- **2026 AX 아이디어 경진대회** (기후에너지환경부 주최, 한국전력공사 대표주관)
- **마감**: 2026-05-18 (월)
- **부문**: 데이터 분석 > 자유과제 분석 (대국민/내부직원, 개인 또는 4인 이내 팀)
- **홈페이지**: www.konetic.or.kr/ecothon
- **상금**: 자유분석 13점 배정, 대상 500만원

### 연구 주제
"한국 코스피 상장기업의 온실가스 공시 신뢰성 3중 검증 — GIR 법정 배출량 × ESG 자체보고 × Sentinel-5P 위성 NO₂·SO₂ 불일치 패턴 분석 및 ESG 의무공시 검증체계 설계"

### 핵심 구조
- **3중 비교**: GIR (법정) × ESG (자체보고) × 위성 (독립관측, 기상보정 후)
- **대상**: 코스피200 ∩ GIR 목표관리·배출권 60~80개사 (Gold 샘플 30~50)
- **기간**: 2019~2023 5개년 패널
- **핵심 혁신**: ERA5 기상보정 + Mann-Kendall 방향 일관성 + Heckman 선택편향 통제 + 이상탐지 3층 구조 + SHAP XAI

### 17+ 데이터셋 (ADR-002 확장, ADR-004 정정, 2026-04-22 기준)

**Tier 1 — 법정·공공 배출량 (GIR ecosystem)**
- **A**: GIR 관리업체 명세서 (xls 7개년 2018-2024, cp949, 7,998행 1,585개 법인)
- **A-2**: GIR 할당대상업체 지정현황 (4개 snapshot, VWorld 지오코딩)
- **A-3**: GIR 목표관리업체 현황 (xlsx, 4,308 entities)
- **A-4**: K-ETS 사전할당 1~4차 phase (12,009 records)
- **A-5**: K-ETS 할당계획 변경공고 (HWP/HWPX/PDF 18개, **업종·총량 수준만, 기업별 조정 0건** — ADR-004 참조)
- **A-6**: GIR 검증기관 지정현황 + 명세서 내장 검증기관

**Tier 1 — 기업 ESG 자체보고**
- **B**: 지속가능경영보고서 PDF (DART 자율공시 + KRX ESG + IR 사이트)
  - 자동화 수집: `src/preprocessing/sustainability_report_collector.py`
  - 자동화 파싱: `src/preprocessing/sustainability_report_parser.py`
  - Skill: `.claude/skills/sustainability-report-collect.md`, `esg-scope-extract.md`
- **B-2**: DART 사업보고서 II.6 환경정보 + 지역별 매출

**Tier 1 — 샘플 기준**
- **C**: KOSPI 전체 789 firms (DART 기반) + KOSPI200 proxy (자본총계 top 200)
  - 공식 KRX API 차단 → `src/preprocessing/kospi200_proxy.py` 우회
- **C-2**: KCGS ESG 등급 (2017-2025 집계 + 분기 등급조정 21건)

**Tier 1 — 위성·기상 (4중 비교)**
- **D**: Sentinel-5P NO₂ (GEE COPERNICUS/S5P/OFFL/L3_NO2)
- **D-2**: Sentinel-5P SO₂ (GEE L3_SO2)
- **D-3**: Sentinel-5P CO (GEE L3_CO) — 장수명 불완전연소 추적자
- **D-4**: Sentinel-5P HCHO (GEE L3_HCHO) — 석유화학 VOC 프록시
- **E**: DART 재무제표 (opendartreader)
- **E-2**: ERA5-Land + ERA5 BLH 기상 (GEE)
- **E-3**: MERRA-2 재분석 (GEE, ERA5 민감도 검증)
- **F**: ODIAC v2024 CO₂ 1km (NIES 포털) — **4중 비교 중 직접 CO₂ 신호**
- **F-2**: NIR 국가 온실가스 인벤토리 (거시 sanity check)
- **F-3**: 기상청 ASOS 지점 관측 (data.go.kr API, ERA5 지상 검증)

**Tier 1 — 보조**
- **G**: 통합환경허가 사업장 정보 (1,065건 중 782 파싱 성공)

### 심사 5대 기준
1. 분석기법 타당성 (→ 6.1~6.4)
2. 데이터 전처리 (→ 4장·5장)
3. 인사이트 독창성 (→ 6.4 패턴 분류)
4. 결과의 유의성 (→ 6.5~6.6)
5. 활용 방안 (→ 6.7·9장 KEITI 직결 정책)

---

## 폴더 규칙

| 폴더 | 용도 | 수정 권한 |
|---|---|---|
| `참고/` | 공모전 원본 자료 (PDF·HTML 4종) | **읽기 전용** |
| `data/raw/` | 원본 데이터 (절대 수정 금지, SHA-256 기록) | corp-data-manager |
| `data/interim/` | 중간 전처리 산출물 | corp-data-manager, data-analyst |
| `data/processed/` | 최종 분석 패널 | data-analyst |
| `src/preprocessing/` | 전처리 코드 | corp-data-manager |
| `src/analysis/` | 통계 분석 코드 | data-analyst |
| `src/satellite/` | GEE·위성 처리 | algo-researcher, data-analyst |
| `src/visualization/` | 피규어 생성 | report-writer |
| `figs/` | 최종 피규어 | report-writer |
| `report/` | 제출 문서 | report-writer |
| `decisions/` | 주요 의사결정 ADR (YYYY-MM-DD-topic.md) | **디렉터 전용** |
| `notebooks/` | 탐색적 Jupyter 노트북 | data-analyst |

---

## 자동화된 데이터 수집 시스템 (영구 기능, 최종 제출물 구성요소)

Wave 3에서 구현된 자동화 파이프라인. 공모전 제출 시 "시스템 아키텍처"로 명시할 핵심 deliverable.

### 지속가능경영보고서 수집·파싱 파이프라인
- **수집**: `src/preprocessing/sustainability_report_collector.py` — DART 자율공시 → KRX ESG → IR 3-tier fallback, SHA-256 중복제거, resume-safe
- **파싱**: `src/preprocessing/sustainability_report_parser.py` — GRI 305-1/2/3 + 조직경계 + assurance + 보고기준, 신뢰도 플래그(HIGH/MEDIUM/LOW)
- **알려진 제약**: 한국 대기업(삼성·현대·SK·POSCO) 대부분 DART 자율공시에는 URL 링크만, 실제 PDF는 IR 사이트에 있음. KRX ESG 포털은 JS 렌더링 필수(Selenium 설정 별도).
- **실용 전략**: DART URL 로그로 공시 존재 확인 + 수동 IR 사이트 다운로드 + 파서 즉시 처리

### KOSPI200 Proxy (`src/preprocessing/kospi200_proxy.py`)
- KRX 공식 API 2026년 차단 우회책
- DART 자본총계 기준 상위 200개사 = 공식 KOSPI200과 90~95% 일치 추정
- 방법론 caveat: 자본총계 ≠ 시가총액, 금융지주 편향 주의

### Slash Skills (재사용 가능)
- `/skill sustainability-report-collect <corp_list.csv>`
- `/skill esg-scope-extract <reports-dir>`

---

## 언어 정책

- **사용자 ↔ 디렉터**: 한국어
- **디렉터 → 서브에이전트 프롬프트**: 영어 (정확성·일관성·내부 논리 검증을 위해)
- **서브에이전트 → 디렉터 응답**: 영어 (디렉터가 한국어로 재해석)
- **코드 주석·변수명**: 영어
- **최종 보고서 (`report/`)**: 한국어 (공모전 제출용)
- **데이터 딕셔너리·README**: 한국어 + 영어 혼용 허용

---

## 중요 주의사항

- **`참고/` 폴더는 절대 수정하지 않는다.** 원본 자료다.
- **API 키는 `.env`에 넣고 `.gitignore`로 제외한다.** 절대 커밋 금지.
- **데이터 파일(`data/`)은 커밋 금지.** 대신 `data/README.md`에 출처·SHA-256만 기록.
- **공공데이터 이용약관·저작권**을 위반하지 않는다 (재배포 금지 등).
- **"그린워싱" 같은 인과 함의 언어 사용 금지.** "공시 불일치 (disclosure discrepancy)" 중립 용어만 사용.
- **제3자 검증받지 않은 결론을 단정하지 않는다.** 항상 CI·p-value·robustness check 병기.
- **KOSPI200 구성종목**: KRX 공식 API 2026년 차단. `kospi200_proxy.py`로 DART 자본총계 proxy 사용. `data/KOSPI200/` 5개 CSV는 인덱스 일별 시세(매크로 통제변수)이며 구성종목 명단 아님.
- **KSSB 2028 임계값**: 연결자산 30조원 이상 = 49개사 (ADR-004 정정). `kssb_flag_30` 컬럼 사용. `kssb_flag_any`(2조 기준, 238개사)는 deprecated.
