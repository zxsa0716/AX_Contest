# CLAUDE.md 패치 제안 (ADR-003 반영, 2026-04-20)

디렉터가 직접 CLAUDE.md에 적용할 EXACT before/after 블록이다.
파일을 직접 수정하지 말 것 — 이 문서는 제안서다.

---

## 패치 1: 핵심 구조 (3중 비교 → 4중 비교)

### BEFORE

```
### 핵심 구조
- **3중 비교**: GIR (법정) × ESG (자체보고) × 위성 (독립관측, 기상보정 후)
- **대상**: 코스피200 ∩ GIR 목표관리·배출권 60~80개사 (Gold 샘플 30~50)
- **기간**: 2019~2023 5개년 패널
- **핵심 혁신**: ERA5 기상보정 + Mann-Kendall 방향 일관성 + Heckman 선택편향 통제 + 이상탐지 3층 구조 + SHAP XAI
```

### AFTER

```
### 핵심 구조
- **4중 비교**: GIR (법정) × ESG (자체보고) × 위성 프록시 (NO₂/SO₂/CO, 기상보정 후) × ODIAC-CO₂ (top-down 1km, 직접 탄소 관측)
- **대상**: 코스피200 ∩ GIR 목표관리·배출권 ∩ KSSB 2028 의무화 1차 대상 58개사 교집합 (Gold 샘플 20~40, 최소 확보 목표)
- **기간**: 2019~2023 5개년 패널
- **핵심 혁신**: ERA5 기상보정 + Mann-Kendall 방향 일관성 + Heckman 선택편향 통제 + 이상탐지 3층 구조(부분 지도 학습, 할당계획 변경공고 ground truth) + SHAP XAI + ODIAC top-down CO₂ 물리적 교차 검증
```

---

## 패치 2: 6개 데이터셋 → 18+ 데이터셋 (ADR-002 반영)

### BEFORE

```
### 6개 데이터셋
- **A**: GIR 관리업체 명세서 (data.go.kr, CSV 5개년, encoding=cp949)
- **A-2**: GIR 할당대상업체 주소 → Kakao Local API 지오코딩
- **B**: KRX ESG 포털 + DART 지속가능경영보고서 PDF (GRI 305-1 파싱)
- **C**: Sentinel-5P NO₂ (GEE COPERNICUS/S5P/OFFL/L3_NO2)
- **C-2**: Sentinel-5P SO₂ (GEE COPERNICUS/S5P/OFFL/L3_SO2)
- **D**: DART Open API 재무 + ERA5 기상 (GEE ECMWF/ERA5_LAND/HOURLY)
```

### AFTER

```
### 18+ 데이터셋 (ADR-002 v2 아키텍처)

**법정·행정 데이터 (GIR 계열)**
- **A**: GIR 관리업체 명세서 (data.go.kr, CSV 5개년, encoding=cp949)
- **A-2**: GIR 할당대상업체 주소 → Kakao Local API 지오코딩
- **A-3**: GIR 할당계획 변경공고 — 배출량 수정 기업-연도 쌍 (이상탐지 ground truth label)

**ESG 공시 데이터 (B 계열)**
- **B**: KRX ESG 포털 + DART 지속가능경영보고서 PDF (GRI 305-1 파싱)
- **B-2**: CDP 기후변화 응답 데이터 (보조 검증용)

**위성·원격탐사 데이터 (C 계열)**
- **C**: Sentinel-5P NO₂ (GEE COPERNICUS/S5P/OFFL/L3_NO2)
- **C-2**: Sentinel-5P SO₂ (GEE COPERNICUS/S5P/OFFL/L3_SO2)
- **C-3**: Sentinel-5P CO (GEE COPERNICUS/S5P/OFFL/L3_CO)
- **C-4**: Sentinel-5P HCHO (GEE COPERNICUS/S5P/OFFL/L3_HCHO)
- **C-5**: ODIAC top-down CO₂ (1 km, 직접 탄소 컬럼 — "NO₂는 CO₂가 아니다" 비판 방어)

**기상·보정 데이터 (ERA5 계열)**
- **D-1**: ERA5 기상 (GEE ECMWF/ERA5_LAND/HOURLY — u10, v10, tp, t2m, blh)

**재무·기업 데이터 (D 계열)**
- **D-2**: DART Open API 재무 (매출액·자산총액·업종코드·종업원수)
- **D-3**: KSSB 2028 의무화 58개사 명단 (연결자산 30조↑ KOSPI 기업, 금융위 로드맵 별첨)

참고: ADR-002 `decisions/2026-04-20-data-architecture-v2.md` 전체 명세 참조.
```

---

## 패치 3: 심사 5대 기준 + 정책 타임라인 현행화

### BEFORE (심사 5대 기준 박스 아래 별도 추가 항목 없음)

```
### 심사 5대 기준
1. 분석기법 타당성 (→ 6.1~6.4)
2. 데이터 전처리 (→ 4장·5장)
3. 인사이트 독창성 (→ 6.4 패턴 분류)
4. 결과의 유의성 (→ 6.5~6.6)
5. 활용 방안 (→ 6.7·9장 KEITI 직결 정책)
```

### AFTER

```
### 심사 5대 기준
1. 분석기법 타당성 (→ 6.1~6.4)
2. 데이터 전처리 (→ 4장·5장)
3. 인사이트 독창성 (→ 6.4 패턴 분류, 4중 비교 구조)
4. 결과의 유의성 (→ 6.5~6.6)
5. 활용 방안 (→ 6.7·9장 KEITI 직결 정책, KSSB 2028 즉시 활용 경로)

### 정책 타임라인 (2026-04-20 기준 확정 사항)
- **2026-02-25**: 금융위원회 '지속가능성(ESG) 공시 로드맵(안)' 발표
- **2026-02-26**: KSSB 공시기준 최종 확정 (제1호 IFRS S1, 제2호 IFRS S2 기후, 제101호 추가 선택공시)
- **2026-04 중**: ESG금융추진단 최종 로드맵 확정 예정 (공모전 마감 5/18 직전)
- **2026년~**: EU CBAM 철강·알루미늄·비료·시멘트·수소·전력 6종 본격 과세
- **2028년 (FY27 보고)**: KOSPI 연결자산 30조↑ 약 58개사 의무공시 1차 적용 시작
- **핵심 프레이밍**: "의무화 확정, 2년 앞둔 지금이 검증체계 설계 골든 타임. 대상 58개사 = 우리 Gold 샘플 교집합"
```

---

## 적용 방법 (디렉터 지침)

1. `CLAUDE.md` 파일을 열어 위 BEFORE 블록을 각각 AFTER 블록으로 교체한다.
2. 패치는 독립적으로 적용 가능하다 — 순서 무관.
3. 패치 3의 "정책 타임라인" 항목은 심사 5대 기준 바로 아래에 새 `###` 섹션으로 추가한다.
4. 적용 완료 후 `decisions/` 에 적용 날짜·버전을 ADR에 기록한다.
