# ADR-002: 데이터 아키텍처 v2 — Tier 1 최대 확장

**Date**: 2026-04-20
**Status**: Accepted
**Deciders**: 사용자(연구자), 디렉터
**Supersedes**: 참고/data_acquisition_guide.html의 7개 데이터셋 설계

## Context

초기 설계는 6개 데이터셋(A, A-2, B, C, C-2, D)으로 구성되었으나, 4개 에이전트(corp-data-manager, esg-expert, algo-researcher, policy-expert)의 전수조사 결과, 현실적으로 가용한 한국 공공·기업·위성·기상·ESG 데이터는 훨씬 다층적이다. 사용자는 "어떻게든 전부" 수집 방침을 지시했다.

## Decision

**Tier 1에 해당하는 11개 데이터셋을 전부 수집 대상으로 확정.** 해당 지역·사업장 확정 후 Tier 2 확장.

### Tier 1 확정 목록 (총 11개)

| # | 데이터셋 | 출처 | 역할 |
|---|---|---|---|
| 1 | GIR 관리업체 명세서 | data.go.kr 15053947 | 법정 Scope 1 기준값 (기존 A) |
| 2 | GIR 할당대상업체 지정현황 | data.go.kr 15053949 | 사업장 주소 (기존 A-2) |
| 3 | **K-ETS 사전할당량 + 정산** | data.go.kr 15126853 + 15049589 | 할당-실배출 gap, Heckman 도구변수 |
| 4 | **GIR 검증의견 공시** | data.go.kr 15082976 | 법정 배출량 자체 신뢰도 메타변수 |
| 5 | **환경부 할당계획 변경공고** | me.go.kr 보도·공고 | **과거 수정 이력 → supervised label** |
| 6 | **KRX 코스피200 + 업종분류** | data.krx.co.kr | 샘플 확정 사전 필수 테이블 |
| 7 | **KRX 배출권 KAU 일별 가격** | ets.krx.co.kr | 탄소가격 압력 매크로 통제변수 |
| 8 | **DART 사업보고서 II.6** | DART Open API | ESG PDF 미발간 기업까지 커버 |
| 9 | KRX ESG 보고서 + GRI 305-1 | esg.krx.co.kr + DART | 자체보고 Scope 1 (기존 B) |
| 10 | Sentinel-5P NO₂ + SO₂ | GEE (기존 C, C-2) | 독립 위성 관측 |
| 11 | DART 재무 + ERA5 기상 | DART API + GEE (기존 D) | 통제변수 |

### 추가 추출 (방법론 업그레이드용)

| # | 데이터셋 | 출처 | 역할 |
|---|---|---|---|
| 12 | **Sentinel-5P CO** | GEE L3_CO | 장수명 불완전연소 추적자 |
| 13 | **Sentinel-5P HCHO** | GEE L3_HCHO | 석유화학 VOC 프록시 |
| 14 | **ODIAC v2024 CO₂ 1km** | NIES 포털 | 4중 비교 중 CO₂ 직접 인벤토리 |
| 15 | **MERRA-2 재분석** | GEE | ERA5 독립 민감도 검증 |
| 16 | **KCGS ESG 등급** | cgs.or.kr | 987개사 독립 ESG 평가 |
| 17 | **Assurance letter 메타** | 기존 ESG PDF 내부 파싱 | 제3자 검증 수준 분류 |

### Tier 2 (Tier 1 완료 후 착수)

- 통합환경허가 · PRTR 사업장 대기배출량
- **기상청 ASOS 지점 관측** (API 키 확보됨)
- MODIS AOD · VIIRS 야간조도
- 에너지사용량 신고 · SBTi/RE100 명단

### 제외 (비용·비현실성)

- MSCI / Sustainalytics / Bloomberg ESG (유료)
- CDP 2024+ 전체 응답서 (유료 전환)
- 국세청 법인세 행정자료 (FOI 수개월)

## Consequences

### Positive
- 공모전 심사기준 "데이터 전처리" depth 극대화
- "국가중점데이터 활용" 가점 조건 확실 충족 (6개 이상의 정부 API)
- 방법론 방어력 격상: NO₂-CO₂ 등가 비판, 기상 의존성 비판, 선택편향 비판 모두 직접 대응 데이터 보유
- 3중 비교 → **4중 비교(+ODIAC)**로 독창성 상승

### Negative
- 초기 수집 공수 5~6일 증가 (4주 스케줄에서 1주차 전부 소모)
- DART 사업보고서 II.6 파싱은 비표준 포맷 → 수작업 비율 존재
- 환경부 변경공고 수집은 자동화 어려움 → 수동 스크래핑

### Neutral
- 데이터 볼륨 증가로 로컬 디스크 관리 필요 (ODIAC GeoTIFF 60개월 × 약 300MB)
- GEE quota 관리 주의 (Export 권장)

## Alternatives considered

- **최소 확장(Tier 1 중 6개만)**: 2~3일 절감되나 ODIAC 없으면 NO₂-CO₂ 비판 방어 불가. 기각.
- **Tier 1 + Tier 2 전부 동시 착수**: 공수 10일+, 4주 일정 붕괴 위험. 기각.
- **유료 소스(MSCI/CDP Full) 구매**: 예산·라이선스 협의 지연, 공모전 4주 내 불가능. 기각.

## Related files

- `CLAUDE.md` (프로젝트 사실 업데이트 필요: 데이터셋 목록 6 → 11+6)
- `data/README.md` (인벤토리 표 전면 확장)
- `.env` / `.env.example` (KMA_API_KEY 추가)
