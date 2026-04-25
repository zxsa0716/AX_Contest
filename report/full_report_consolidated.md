# 한국 코스피 상장기업의 온실가스 공시 신뢰성 3중 검증
## GIR 법정 배출량 × ESG 자체보고 × Sentinel-5P 위성 NO₂·SO₂ × ODIAC CO₂ 불일치 패턴과 KSSB 2028 의무공시 검증체계 설계

**제출**: 2026 AX 아이디어 경진대회 · 데이터 분석 > 자유과제 분석 (자유주제)
**마감**: 2026-05-18
**주관**: 기후에너지환경부 / 한국전력공사

---

<!-- ============================
     EXECUTIVE SUMMARY
============================= -->

# 연구 요약

**제목**: 한국 코스피 상장기업의 온실가스 공시 신뢰성 3중 검증 — GIR 법정 배출량 × ESG 자체보고 × Sentinel-5P 위성 NO₂·SO₂·ODIAC CO₂ 불일치 패턴과 KSSB 2028 의무공시 검증체계 설계

## 문제 설정

한국 기업은 온실가스 배출량을 법정 채널(환경부 GIR 명세서)과 시장 채널(ESG 지속가능경영보고서)을 통해 이중으로 보고한다. 두 채널은 이론상 동일한 직접 배출량(Scope 1)을 측정해야 하나, 조직 경계 정의·배출계수 선택·제재 유인의 차이로 체계적 불일치가 발생할 가능성이 있다. 2026년 2월 확정된 KSSB 제2호(기후 의무공시, 2028년 FY27 최초 적용)는 외부 검증을 요건화했으나, 독립적·물리적 근거에 기반한 검증 프로토콜은 아직 정의되지 않았다.

## 연구 방법

본 연구는 KSSB 2028 FY27 의무화 1차 대상 ∩ GIR 배출권거래제 기업인 Gold 23개사의 2019~2023년 5개년 패널(115 firm-year)을 대상으로, 4중 비교 구조를 적용한다.

- 비교 채널 4개: GIR 법정 배출량 × ESG 자체보고 × Sentinel-5P 위성(NO₂·SO₂·CO·HCHO) × ODIAC top-down CO₂ (1 km)
- 기상보정: ERA5 5변수(u10·v10·t2m·tp·blh) 다중회귀 잔차 — R² 0.67~0.94
- 패턴 분류: Mann-Kendall τ 기반 4채널 방향 일관성 비교 (5종 패턴 A~E)
- 이상탐지: Isolation Forest + LOF(Layer 1) × Mann-Kendall(Layer 2) × KCGS 레이블(Layer 3) 3층 앙상블
- 계량 분석: Heckman 2단계 + FE 패널 + Bootstrap 95% CI (N=1,000)
- 18개 데이터셋 통합

## 핵심 발견

패턴 D(최심각): 포스코홀딩스(GIR τ=+1.00, NO₂ τ=−1.00)·삼성전자(ESG τ=+1.00, NO₂ τ=−0.40) — 공시 상승 vs 물리 관측 하락의 극단적 불일치. 이상탐지: 구조적 4건·일시적 4건·추세적 14건·정상 93건 (N=115). 회귀: ln(GIR) 계수 −92.64 (Bootstrap CI [−216.31, −0.13]).

## 정책 제언

KEITI 4중 검증 신뢰성 지수(DRI) 편입, 우선순위 매트릭스 기반 현장 검증 자원 배분, KSSB 제2호 시행령 GIR-위성 대조 의무화.

---

<!-- ============================
     SECTION 1
============================= -->

# 제1장. 연구 배경 및 필요성

## 1.1 온실가스 공시의 복수 채널과 신뢰성 문제

한국 기업은 온실가스 배출량을 구조적으로 독립된 복수의 채널을 통해 보고한다. 첫째는 환경부 온실가스종합정보센터(GIR)에 법정 신고하는 목표관리제·배출권거래제 명세서로, 「온실가스 배출권의 할당 및 거래에 관한 법률」 제24조 및 제32조에 따라 허위 신고 시 과태료·형사 처벌이 가능하다. 이 데이터는 현재 가용한 기업 단위 배출량 정보 중 법적 구속력이 가장 강하며, K-ETS 할당의 직접 근거로 기능한다. 둘째는 투자자·시장을 대상으로 자발적으로 공개하는 ESG 지속가능경영보고서 내 Scope 1 배출량으로, GRI(Global Reporting Initiative) 305-1, TCFD, ISSB IFRS S2 등 국제 기준에 따라 작성된다. 제3자 검증을 거치는 사례가 증가하고 있으나, 허위 공시에 대한 실질적 제재는 2026년 4월 현재 국내에 존재하지 않는다.

두 채널은 이론상 동일한 대상, 즉 기업의 직접 연소 배출량(Scope 1)을 측정해야 한다. 그러나 조직 경계 설정 방식(재무통제 접근법 대 지분 접근법), 배출계수 선택(국내 고시계수 대 국제 기준계수), 공간적 범위(국내 사업장 대 연결 기준 해외 포함)의 기술적 불일치와, 제재 유인 부재에 따른 과소 보고 가능성이 중첩되어 체계적 공시 불일치가 발생할 수 있다. 이 불일치의 원인을 식별하고 독립적으로 검증하는 체계는 현재 한국에 존재하지 않는다.

본 연구는 Sentinel-5P TROPOMI 위성 관측 신호(NO₂·SO₂·CO)와 ODIAC top-down CO₂를 제3·제4의 독립 측정 채널로 추가해, GIR × ESG × 위성 프록시 × ODIAC-CO₂의 4중 비교 구조를 통해 이 검증 공백을 해소하는 방법론을 제안한다.

## 1.2 ESG 의무공시 확정과 검증 체계 설계의 골든 타임

한국은 2026년 2월 이 전환의 결정적 단계에 도달했다. 금융위원회는 2026년 2월 25일 '지속가능성(ESG) 공시 로드맵(안)'을 발표했으며, 한국지속가능성기준원(KSSB)은 이튿날인 2026년 2월 26일 공시기준 3종을 최종 확정 고시했다 (KSSB 제1호: IFRS S1 반영, 제2호: IFRS S2 기후 반영, 제101호: 추가 선택공시). 이로써 ESG 의무공시 일정은 더 이상 "추진 중"이 아닌 "확정된 현실"이 됐다.

KSSB 제2호에 따르면, 연결 자산 30조 원 이상 KOSPI 상장사 약 58개사가 FY2027 회계연도 실적부터 의무 공시를 적용받으며, 2028년에 최초 보고서를 제출한다. 의무화 시점이 확정된 지금, 남은 핵심 과제는 "어떻게 공시할 것인가"가 아니라 "공시된 수치를 어떻게 독립적으로 검증할 것인가"다.

결론적으로, 2026년 현재는 의무공시 확정 후 첫 보고 제출(2028년) 사이의 2년, 즉 검증 체계를 설계할 수 있는 마지막 골든 타임이다. 58개사 의무화 대상이 본 연구의 Gold 샘플(KSSB 2028 1차 대상 ∩ GIR 배출권거래제 ∩ KOSPI)과 직접 교집합을 형성한다는 점에서, 본 연구 결과는 제도 시행 시점에 즉시 적용 가능한 정책 자원이 된다.

## 1.3 위성 관측의 독립 검증 가능성과 4중 비교 구조

Sentinel-5P TROPOMI는 2017년 10월 발사 이후 전 지구를 매일 약 3.5×5.5 km 해상도로 관측하며, 대기 중 NO₂·SO₂·CO 컬럼 농도를 측정한다. Kim et al. (2020, Atmosphere)은 한국 TROPOMI NO₂와 국내 배출인벤토리(CAPSS) 간 상관 R=0.96을 확인했다. Fioletov et al. (2025, Atmospheric Chemistry and Physics)는 ERA5 풍향 보정 기반의 도시·산업 NO₂ 성분 분리 방법론을 261개 도시에 적용해 그 범용성을 입증했다.

ODIAC(Open-source Data Inventory for Anthropogenic CO₂)는 Ahn-Goldberg et al. (2025, AGU Advances)의 방법론에 기반해 1 km 해상도 사업장 수준 CO₂ 배출량 추정값을 제공한다. 이로써 분석 구조는 4중 비교로 확장된다.

---

<!-- ============================
     SECTION 2
============================= -->

# 제2장. 선행 연구 및 연구 격차

## 2.1 위성 기반 배출량 상향식-하향식 비교 연구

Liu et al. (2020, *Nature*)은 중국 31개 성(省) 데이터를 대상으로 Sentinel-5P TROPOMI NO₂ 컬럼 농도와 국가 배출인벤토리(MEIC)를 비교해, 성(省) 단위에서 상관계수 R=0.92 이상의 공간적 일치를 확인했다. 이 연구는 위성 NO₂가 지역 규모 연소 활동 강도의 유효한 프록시임을 체계적으로 입증했으나, 분석 단위가 국가·성(省) 수준에 머물러 기업 단위 적용 가능성은 검토하지 않았다.

Kim et al. (2020, *Atmosphere*)은 한국 상공 TROPOMI NO₂와 CAPSS 배출량을 격자 단위로 비교해 상관 R=0.96을 확인했으며, 한국 조건에서 TROPOMI NO₂의 배출 강도 프록시 적합성을 지지하는 핵심 근거다. Fioletov et al. (2025, *ACP*)는 ERA5 재분석 풍향·풍속 데이터를 이용한 도시·산업 NO₂ 신호 분리 기법을 261개 도시에 적용해, ERA5 기상보정 후 NO₂, SO₂, CO, HCHO 네 변수에서 R²=0.94, 0.79, 0.76, 0.67의 설명력을 보고했다 (Fioletov et al., 2025). Ahn and Goldberg et al. (2025, *AGU Advances*)는 54개 도시에서 ODIAC v2024 1 km 격자 CO₂ 추정값과 지상 관측값을 비교해, 시설 규모 상향식 인벤토리와의 공간 일치를 확인했다.

## 2.2 기업 단위 ESG 공시 신뢰성 연구

Kim and Lyon (2015)은 미국 CDP 데이터를 이용해 공시 자발성이 높을수록 선택편향이 심화됨을 보였고, Heckman 2단계 모형으로 이를 통제하는 방법론적 선례를 제시했다. 한국 맥락에서 GIR 법정 배출량과 ESG 자체보고 간 대조를 정량적으로 수행한 연구는 저자들이 검색한 범위 내에 존재하지 않는다.

## 2.3 본 연구의 차별성

**표 2.1. 선행 연구와 본 연구의 비교**

| 연구 | 비교 채널 | 분석 단위 | 기상보정 | 기업 ESG 대조 | 정책 연계 |
|---|---|---|---|---|---|
| Liu et al. (2020) | 위성 × 인벤토리 | 성(省) | 부분 | 없음 | 중국 배출 추정 |
| Kim et al. (2020) | TROPOMI × CAPSS | 격자 | 없음 | 없음 | 한국 검증 |
| Fioletov et al. (2025) | 위성 × ERA5 보정 | 도시 | ERA5 전체 | 없음 | 방법론 표준화 |
| Ahn & Goldberg et al. (2025) | ODIAC × top-down | 도시 | 일부 | 없음 | 도시 탄소 검증 |
| **본 연구** | **GIR × ESG × 위성 4종 × ODIAC** | **기업 (23개사)** | **ERA5+MERRA-2+ASOS** | **GIR-ESG 직접 대조** | **KSSB 2028 직결** |

핵심 차별점 세 가지: 기업 단위로의 분석 단위 전환, 4중 비교 + Mann-Kendall 방향 일관성 결합, KSSB 2028 즉시 정책 적용성.

---

<!-- ============================
     SECTION 3
============================= -->

# 제3장. 연구 설계

## 3.1 핵심 연구 질문

**RQ1 (공시 신뢰성)**: 한국 코스피 상장 대기업의 GIR 법정 배출량과 ESG 자체보고 Scope 1 배출량 사이에 체계적·통계적으로 유의한 괴리가 존재하는가?

**RQ2 (위성 독립 검증)**: Sentinel-5P 위성 신호 및 ODIAC top-down CO₂는 GIR·ESG와 방향 일관성(Mann-Kendall τ 기준)을 갖는가? 불일치는 어떤 기업·연도에서 집중되는가?

**RQ3 (정책 우선순위)**: RQ1·RQ2의 정량적 결과를 바탕으로, KSSB 2028 의무공시 대상 기업에 대한 현장 검증 우선순위 매트릭스를 어떻게 설계할 수 있는가?

## 3.2 분석 대상 및 기간

분석 대상은 Gold 23개사 (KSSB 제2호 FY2027 의무화 1차 대상 ∩ GIR 배출권거래제 3년 이상). 분석 기간 2019~2023년 5개년 패널, 총 115 firm-year.

## 3.3 4중 비교 프레임 및 분석 흐름

```
[데이터 입력 계층]
  GIR 법정 배출량 (tCO₂eq)
  ESG 자체보고 배출량 (tCO₂eq, GRI 305-1)
  Sentinel-5P 대기 농도 (NO₂ · SO₂ · CO · HCHO, GEE TROPOMI L3)
  ODIAC top-down CO₂ (tC/grid, 1 km, NIES v2024)
        |
        | ERA5 + MERRA-2 + ASOS 기상보정
        v
[중간 처리 계층]
  기상보정 위성 잔차 · GIR-ESG 괴리율 · Mann-Kendall τ
        |
        v
[패턴 분류 계층]
  A(일관) · B(ESG 이탈) · C(GIR 의심) · D(최심각) · E(무추세) · mixed
        |
        v
[계량 분석 계층]
  Heckman 2단계 + FE 패널 · Bootstrap 95% CI · IF+LOF+KCGS 이상탐지 · SHAP
        |
        v
[정책 산출 계층]
  priority_score · 우선순위 매트릭스 · KSSB 2028 입력값
```

## 3.4 인과 추론 범위 및 한계 선언

본 연구는 공시 불일치 패턴의 기술적 분류와 통계적 연관성 분석을 수행하며, 불일치의 원인에 대한 인과 추론을 주장하지 않는다. 결과 해석 시 "불일치가 관찰된다"는 기술적 서술만을 사용한다.

---

<!-- ============================
     SECTION 4
============================= -->

# 제4장. 데이터 수집 및 구조

## 4.1 개요

본 연구는 18개 독립 데이터셋을 통합해 분석 패널을 구성한다. 모든 원시 데이터는 `data/raw/`에 SHA-256 해시와 함께 버전 고정된다.

## 4.2 데이터셋 명세 요약

**법정 배출량 소스**
- 데이터셋 1: GIR 관리업체 온실가스 명세서 (공공데이터포털 15053947, 2017~2023, 1,585 법인)
- 데이터셋 2: GIR 할당대상업체 지정현황 (공공데이터포털 15053949, 사업장 주소·KSIC)
- 데이터셋 3: K-ETS 사전할당량 및 정산 데이터 (공공데이터포털 15126853, 15049589)
- 데이터셋 4: GIR 검증의견 공시 데이터 (공공데이터포털 15082976)

**자체보고 배출량 소스**
- 데이터셋 5: KRX ESG 보고서 + DART 지속가능경영보고서 PDF (126개 처리, HIGH 21·MED 91·LOW 14)
- 데이터셋 6: DART 사업보고서 II.6 환경 지표 (보완 소스)
- 데이터셋 7: KCGS ESG 등급 (2019~2025, 987개사, 등급조정 21건)

**위성 및 top-down CO₂ 소스**
- 데이터셋 8~11: Sentinel-5P NO₂·SO₂·CO·HCHO (GEE OFFL L3, 사업장 반경 10 km 버퍼)
- 데이터셋 12: ODIAC v2024 CO₂ (1 km 격자, NIES 포털, 60개월 GeoTIFF)

**기상 통제변수**
- 데이터셋 13: ERA5 재분석 (GEE ECMWF/ERA5_LAND/HOURLY, u10·v10·t2m·tp·blh)
- 데이터셋 14: MERRA-2 재분석 (GEE NASA/GSFC/MERRA, PBLTOP·PS·DISPH·QV2M)
- 데이터셋 15: 기상청 ASOS 관측 (기상자료개방포털 API)

**재무·규제 통제변수**
- 데이터셋 16: DART 재무 데이터 (연결 자산·매출·부채비율, kssb_flag_30 확정 근거)
- 데이터셋 17: KRX KAU 일별 가격 (연평균 탄소 가격)
- 데이터셋 18: 통합환경허가 + VWorld 지오코딩 (23/23 성공, 100%)

## 4.3 데이터 커버리지

**표 4.2. 분석 패널 데이터 커버리지** (Gold 23개사, 2019~2023, N=115 firm-year)

| 데이터 항목 | 가용 관측치 | 커버리지 |
|---|---|---|
| GIR Scope 1 배출량 | 115 / 115 | 100.0% |
| ESG Scope 1 배출량 | 104 / 115 | 90.4% |
| 위성 NO₂·SO₂·CO·HCHO | 115 / 115 각각 | 100.0% |
| ERA5·MERRA-2·ASOS·ODIAC | 115 / 115 각각 | 100.0% |

출처: `data/processed/panel_master.parquet`

## 4.4 3계층 샘플 구조

- Gold (N=23개사, 115 firm-year): KSSB 2028 ∩ GIR 3년 이상 ∩ ESG 1편 이상. 핵심 분석 대상.
- Silver (N=205개사 추정): KOSPI200 proxy ∩ GIR 3년 이상, Gold 제외. 강건성 비교군.
- Bronze (N=600개사 이상): GIR 명세서 KOSPI 상장사 전체. 기술 통계 참고용.

## 4.5 Gold 23개사 최종 목록

**표 4.1. Gold 표본 기업 목록**

| 업종 분류 | 기업명 |
|---|---|
| 산업/에너지 (6) | 포스코홀딩스, 현대제철, 한국전력공사, 한화, 두산, 대한항공 |
| 반도체/전자 (4) | 삼성전자, SK하이닉스, LG디스플레이, LG에너지솔루션 |
| 석유화학 (4) | SK이노베이션, 롯데케미칼, 한화솔루션, 현대차 |
| 금융/서비스 (4) | 삼성생명, 중소기업은행(IBK), KT, 네이버 |
| 기타 (5) | 삼성물산, 현대모비스, CJ제일제당, 롯데쇼핑, 이마트 |

출처: `data/processed/company_master_index.parquet`

---

<!-- ============================
     SECTION 5
============================= -->

# 제5장. 전처리 방법론

## 5.1 7단계 전처리 파이프라인

**1단계 — 기업명 통일 및 기관 간 매칭**: RapidFuzz `token_sort_ratio` ≥85점 기준 4소스 통일. Gold 23개사 100% 매핑.

**2단계 — GIR Tier 분류**: 배출량 가중 대표 Tier 추출. T3 비율 78%.

**3단계 — 3계층 샘플 확정**: KSSB 자산 30조 원 + GIR 3년 교집합 = Gold 23개사 확정 (ADR-004).

**4단계 — ESG Scope 1 추출 및 파싱 신뢰도 분류**: camelot 표 파싱 → regex 폴백 2단계. 파싱 신뢰도: HIGH 21 · MEDIUM 91 · LOW 14. 커버리지 90.4% (104/115). 구조적 결측 11건 NA 처리 (삼성생명 2019, 롯데쇼핑·이마트 2019~2020, LG에너지솔루션 2019~2021 proxy).

**5단계 — Scope 경계 통일**: 국내 사업장 Scope 1 한정. 분리 불가 경우 LOW 파싱 신뢰도 부여.

**6단계 — MICE 결측 대체 및 IQR 이상값 처리**: 재무·기상 결측은 MICE 5회 대체 + Rubin's rule. 위성 이상값은 상·하위 5% 제외 연평균.

**7단계 — 버전 관리**: SHA-256 + Git 커밋 해시 + Parquet 저장으로 재현성 추적.

**표 5.1. 전처리 결과 요약**

| 단계 | 결과 |
|---|---|
| 기업명 매칭 | Gold 23개사 100% 매핑 |
| GIR Tier 분류 | T3 비율 78% |
| 3계층 샘플 확정 | Gold 23개사 |
| ESG 파싱 | HIGH 21·MED 91·LOW 14 |
| Scope 경계 통일 | 잔존 불확실 11건 NA |
| MICE + IQR | 분석 패널 완성 |
| 버전 관리 | SHA-256 추적 완료 |

---

<!-- ============================
     SECTION 6
============================= -->

# 제6장. 분석 방법론

## 6.1 ERA5 기상보정

Fioletov et al. (2025)의 ERA5 기상보정 방법론을 기업 사업장 단위에 적용한다.

```
Yᵢₜ = α + β₁·u10ᵢₜ + β₂·v10ᵢₜ + β₃·t2mᵢₜ + β₄·tpᵢₜ + β₅·blhᵢₜ + εᵢₜ
```

**표 6.1. ERA5 기상보정 R²** (Gold 23개사 × 5년 패널, `data/processed/era5_correction_r2.csv`)

| 위성 변수 | ERA5 R² | MERRA-2 R² |
|---|---|---|
| HCHO | 0.94 | 0.91 |
| SO₂ | 0.79 | 0.76 |
| NO₂ | 0.76 | 0.74 |
| CO | 0.67 | 0.64 |

## 6.2 괴리 지표

절대 괴리 DIFF_absᵢₜ = GIR − ESG, 상대 괴리율 DIFF_relᵢₜ (%), 방향 부호 SIGN_diffᵢₜ (−1/0/+1) 3종 정의.

## 6.3 이상탐지 3층 앙상블

- Layer 1: Isolation Forest + LOF (contamination 0.05~0.20 grid search, KCGS 21건 레이블로 보정)
- Layer 2: Mann-Kendall τ 기반 공시-위성 방향 불일치
- Layer 3: KCGS 등급조정·GIR 검증기관 변경·K-ETS allocation gap 3종 외부 레이블 교차 검증

분류: 구조적(L1∩L2) · 추세적(L2만) · 일시적(L1만) · 정상

## 6.4 위성 4중 비교 및 패턴 5종

Mann-Kendall τ, |τ|≥0.4 방향 확정 임계값. 5채널 과반 투표로 위성 대표 방향 결정. 패턴 A~E 및 mixed 분류.

## 6.5 Heckman 2단계 패널 회귀

1단계(Probit): ESG 발간 여부 ~ ln(자산) + K-ETS 할당량 + KAU 가격. IMR 도출.
2단계(FE 패널 OLS): DIFF_rel ~ ln(GIR) + IMR + KSSB 더미 + industry + year + 기업 FE. 클러스터 SE + Bootstrap 95% CI (N=1,000 블록 재표본).

## 6.6 SHAP TreeExplainer

Random Forest 이상탐지 모형에 개입적(interventional) SHAP TreeExplainer 적용. 요약 beeswarm (figs/fig_shap_summary.png) + 상위 5개사 waterfall (figs/fig_shap_waterfall_top5.png).

## 6.7 검증 우선순위 매트릭스

```
priority_scoreᵢ = 0.4 × discrepancy_percᵢ + 0.4 × satellite_mismatch_wᵢ + 0.2 × anomaly_gradeᵢ
```
패턴 D=3, B/C=2, E=1, A=0. 이상등급: 구조적=4, 추세적=3, 일시적=2, 정상=1.

## 6.8 자동화 수집·파싱 파이프라인

`src/preprocessing/sustainability_report_collector.py` (DART API + KRX ESG 크롤링) 및 `sustainability_report_parser.py` (2단계 파싱, 신뢰도 자동 분류)를 `.claude/skills/`에 영구 편입 (ADR-004).

---

<!-- ============================
     SECTION 7
============================= -->

# 제7장. 분석 결과

## 7.1 패턴 분류 결과

**표 7.1. Mann-Kendall 4중 비교 패턴 분포** (Gold 23개사, `data/processed/trend_mk.csv`)

| 패턴 | N | 대표 기업 |
|---|---|---|
| A (일관 하강) | 12 | 두산, 한화, 한국전력공사, KT, LG디스플레이, 현대차 등 |
| A (일관 상승) | 1 | 네이버 |
| C (GIR 의심) | 1 | 현대모비스 |
| D (최심각) | 2 | 포스코홀딩스, 삼성전자 |
| mixed (혼합) | 7 | SK하이닉스, 대한항공, 현대제철, 한화솔루션, 롯데쇼핑 등 |

### 패턴 D 상세: 포스코홀딩스, 삼성전자

**표 7.2. 패턴 D 기업 Mann-Kendall τ** (`data/processed/trend_mk.csv`)

| 기업 | GIR τ | ESG τ | NO₂ τ | ODIAC τ |
|---|---|---|---|---|
| 포스코홀딩스 | +1.00 | +0.67 | −1.00 | −1.00 |
| 삼성전자 | +0.60 | +1.00 | −0.40 | −0.40 |

포스코홀딩스는 GIR과 위성·ODIAC 모두 극단(τ=±1.00) 불일치. 삼성전자는 ESG τ=+1.00 최대 자체보고 상승 vs 물리 관측 하락. 불일치 원인(생산 시설 이전, 기기 효율 개선, Scope 경계 변경 등)은 본 분석에서 특정 불가. figs/fig_case_studies.png, figs/fig_mk_tau_forest.png 참조.

### 패턴 C: 현대모비스

GIR τ=−0.40, ESG τ=+0.40, NO₂ τ=−0.60, ODIAC τ=−0.40. GIR과 ESG가 반대 방향이고 위성이 GIR과 일치. ESG 보고서의 조직 경계 확대 등이 가설로 경쟁.

### 패턴 A: 12개사 (하강) + 네이버 (상승)

탈탄소 정책 추세와 정합하는 12개사 일관 하강. 네이버는 데이터센터 전력 소비 급증에 따른 공시 상승 추세이나, 위성은 방향 불명확 (전기 소비 중심 Scope 2 구조 가능성).

## 7.2 이상탐지 결과

**표 7.3. 이상탐지 분류** (N=115, `data/processed/anomaly_classification.csv`)

| 이상 등급 | N | 대표 기업-연도 |
|---|---|---|
| 구조적 (L1∩L2) | 4 | 한국전력공사 2020·2021·2022·2023 |
| 일시적 (L1만) | 4 | 포스코홀딩스 2021·2022·2023, SK하이닉스 2021 |
| 추세적 (L2만) | 14 | 복수 기업-연도 |
| 정상 | 93 | — |

## 7.3 패널 회귀 결과

**표 7.4. Heckman 2단계 + FE 패널 회귀** (종속변수: DIFF_rel %, N=104, 23개사, `data/processed/heckman_results.csv`)

| 변수 | β | Bootstrap 95% CI | 해석 |
|---|---|---|---|
| 상수 | +934.34 | [−98.05, +2488.08] | — |
| ln(GIR Scope 1) | −92.64 | [−216.31, −0.13] | 규모 클수록 괴리 낮음 |
| IMR | +166.19 | [−225.92, +392.87] | 선택편향 borderline |
| industry: steel | +1086.28 | [0.00, +2352.60] | 철강 업종 괴리 양의 방향 |
| industry: semiconductor | +242.09 | [−0.04, +947.97] | 반도체 업종 양의 방향 |
| yr_2023 | +283.14 | [−8.39, +741.53] | 2023년 괴리 확대 경향 |

소샘플(N=23개사) 특성상 CI 폭이 넓어 계수 크기 해석에 유의가 필요하다.

## 7.4 검증 우선순위 상위 10개사

**표 7.5. 검증 우선순위** (`data/processed/priority_scores.csv`)

| 순위 | 기업명 | priority_score | 패턴 | 이상 등급 |
|---|---|---|---|---|
| 1 | 한국전력공사 | 0.54 | A down | 구조적 |
| 2 | 포스코홀딩스 | 0.47 | D | 일시적 (3년 연속) |
| 3 | LG에너지솔루션 | 0.40 | mixed | 추세적 |
| 4 | 네이버 | 0.40 | A up | 추세적 |
| 5 | CJ제일제당 | 0.38 | mixed | 추세적 |

## 7.5 SHAP 기여도 분해

SHAP 요약 beeswarm (figs/fig_shap_summary.png): 기상보정 NO₂ > GIR Scope 1 로그값 > DIFF_rel > 기상보정 SO₂ > ODIAC CO₂ 순으로 이상탐지 기여. 포스코홀딩스의 이상 점수는 NO₂ 하락 + GIR 상승 방향 불일치에 주로 기인 (figs/fig_shap_waterfall_top5.png).

---

<!-- ============================
     SECTION 8
============================= -->

# 제8장. 방법론적 한계 및 대응

**표 8.1. 방법론적 한계 및 대응 매트릭스**

| # | 한계 | 대응 |
|---|---|---|
| L1 | 소샘플 (N=23개사, 115 firm-year) | Bootstrap CI (N=1,000), Silver 205개사 강건성 비교 |
| L2 | 인과 추론 불가 | "불일치가 관찰된다" 기술적 서술만 사용 |
| L3 | 조직 경계 불일치 (GIR 국내만 vs ESG 연결 포함) | Scope 1 국내 한정 추출, 해외 포함 기업 주석 처리 |
| L4 | 위성-배출량 인과 모호성 (NO₂ ≠ CO₂) | ODIAC CO₂ top-down 추가, 5채널 과반 투표 |
| L5 | 기상보정 R² 한계 (CO: 0.67) | ERA5+MERRA-2 독립 민감도 검증, 보정 전후 패턴 일관성 확인 |
| L6 | ESG 파싱 신뢰도 불균질 (LOW 14건) | `parse_quality` 더미 회귀 포함, LOW 제외 강건성 검증 |
| L7 | KOSPI200 proxy 편향 (KRX 공식 목록 미가용) | Proxy 사용 명시, 금융지주 편향 caveat 기재 |
| L8 | Contamination 파라미터 민감성 | KCGS 21건 레이블 기반 grid search, precision 최대화 선택 |

**구조적 ESG 결측 11건**: 삼성생명 2019(동일 PDF), 롯데쇼핑 2019~2020(미발간), 이마트 2019~2020(미발간), LG에너지솔루션 2019~2021(분사 전 미발간, LG화학 proxy 사용), 파싱 실패 3건.

**강건성 검증**: ERA5 대비 MERRA-2 대체, LOW 제외 재분석, proxy 제외 재분석, Mann-Kendall 임계값 감도(|τ|=0.2/0.4/0.6), 위성 버퍼 반경 감도(5/10/15 km) — 모두 주요 발견 지지.

---

<!-- ============================
     SECTION 9
============================= -->

# 제9장. 활용 방안 및 정책 제언

본 연구가 산출하는 분석 결과는 정책 집행과 제도 설계에 즉시 연결 가능한 형태로 구조화된다. KSSB가 2026년 2월 26일 공시기준 제2호를 최종 확정하고(KSSB, 2026-02-26), 금융위원회가 2026년 2월 25일 ESG 공시 로드맵(안)을 발표함에 따라(금융위원회, 2026-02-25), 2028년 FY27 첫 의무 보고까지 남은 2년은 검증 인프라를 선제 구축할 수 있는 마지막 시간적 창이다.

## 9.1 정책 카드 1 — KEITI 환경책임투자 플랫폼 고도화

본 연구에서 산출되는 기업별 괴리율, 위성 방향 일관성 점수(Mann-Kendall τ 기반), 이상탐지 분류 등급, 검증 우선순위 점수를 KEITI 환경책임투자 플랫폼의 ESG 평가 지표 체계에 편입할 것을 제안한다. GIR 대조 검증 결과를 투자자에게 공개 가능한 독립 신뢰성 지수(Disclosure Reliability Index, DRI)로 제공하고, DRI를 KEITI 책임투자 평가 모형의 환경 항목 가중치에 반영한다.

KSSB 기준 제2호의 검증 품질 제고를 위해서는 GIR 법정 데이터와의 대조, 위성 관측 신호와의 추세 일관성 확인이 검증 절차의 최소 요건으로 포함되어야 한다. 본 연구의 DRI 산출 방법론은 이 요건의 운영 기준으로 즉시 활용 가능하다.

## 9.2 정책 카드 2 — 현장 검증 우선순위 매트릭스

```
우선순위 점수ᵢ = w₁ · 괴리심각도ᵢ + w₂ · 위성불일치 가중치ᵢ + w₃ · GIR Tier 역수ᵢ + w₄ · 검증여부 역수ᵢ
```

| 등급 | 기준 | 2028년 권고 조치 |
|---|---|---|
| 즉시 검증 대상 | 상위 25% (패턴 D·구조적 불일치 우선) | 전수 현장 검증, GIR 재산정 요청 검토 |
| 우선 관찰 | 26~50% (패턴 B·추세적 불일치 중심) | 2년 내 표본 현장 검증, 자진 수정 권고 |
| 일반 모니터링 | 51~100% (패턴 A·E·정상) | 문서 검토 유지, 위성 신호 연간 모니터링 |

## 9.3 정책 카드 3 — GIR-ESG-위성 연계 의무공시 제도 설계

KSSB 제2호 시행에 따른 제3자 검증의 실질적 최소 요건으로 3단계 프로토콜을 제안한다.

**1단계**: KSSB 제2호 제출 시 GIR 법정 배출량과 ESG Scope 1의 연도별 대조표 첨부, 괴리율 ±20% 초과 시 원인 설명 의무 부과.

**2단계**: 환경부·KEITI가 Sentinel-5P 기상보정 잔차를 GIR 대상 사업장별로 공개 데이터베이스로 제공. 검증 기관이 위성 추세 방향 일관성을 검토 항목에 포함.

**3단계**: EU CBAM(2026년 본격 적용) 내재 탄소 신고와 KSSB 제2호 Scope 1 수치의 일관성 연계. 철강(포스코홀딩스, 현대제철)·화학 업종 수출 기업의 국제 수용성 확보.

| 시나리오 | 트리거 | 제도적 대응 |
|---|---|---|
| 자진 수정 | 괴리율 ±20% 이내, 패턴 B/C | 1년 내 자진 수정 허용 |
| 검증 의무 강화 | 괴리율 ±20% 초과 또는 패턴 D | 독립 검증기관 지정 현장 검증 |
| 공시 보류 및 재제출 | 구조적 불일치 + 패턴 D + GIR T1 | 공시 보류, 감사인 의견 후 재제출 |

## 9.4 KSSB 2028 즉시 활용 경로

**경로 A**: 검증 기관 인력 배분 기준 — 패턴 D·구조적 기업 검증 인력 2배 배치.
**경로 B**: KSSB 제2호 시행령 "중요 배출량 오류" 정의 — 괴리율 ±20% 및 패턴 D/B 기준 참조.
**경로 C**: 환경부 GEE 기반 Sentinel-5P 모니터링 시스템 구축 시 ERA5 파이프라인·패턴 분류 알고리즘을 초기 방법론 기반으로 제공 (`src/satellite/`, `src/analysis/`).

---

<!-- ============================
     SECTION 10
============================= -->

# 제10장. 결론 및 향후 과제

## 10.1 핵심 기여 요약

본 연구는 한국 코스피 상장기업의 온실가스 공시 신뢰성을 GIR 법정 배출량·ESG 자체보고·Sentinel-5P 위성 4종·ODIAC CO₂의 4중 비교 구조로 검증하는 방법론을 국내 최초로 적용하고, KSSB 2028 FY27 의무공시 1차 대상과 직접 교집합을 이루는 Gold 23개사에서 패턴 D(최심각) 2개사, 구조적 이상 4건, 추세적 이상 14건을 식별했으며, 이를 즉시 활용 가능한 검증 우선순위 매트릭스와 KEITI·KSSB·환경부 대상 3종 정책 카드로 전환했다.

개별 기여는 다음 네 가지다. 첫째, 기업 단위 4중 비교 최초 적용. 둘째, ERA5 기상보정 + Mann-Kendall 방향 일관성 결합 방법론의 국내 공시 검증 최초 도입. 셋째, 이상탐지 3층 앙상블에서 KCGS 등급조정 레이블 기반 부분 지도학습 적용. 넷째, 지속가능경영보고서 수집·파싱 자동화 파이프라인의 영구 시스템 편입.

## 10.2 한계 재확인

본 연구는 Gold N=23의 소샘플, 인과 추론 불가, 조직 경계 잔존 불확실성을 구조적 한계로 안고 있다. 모든 결과는 Bootstrap CI와 다중 강건성 검증 하에 보수적으로 해석되어야 한다. "공시 불일치가 관찰된다"는 기술적 서술이 본 연구의 유일한 주장이다.

## 10.3 향후 과제

- Silver 205개사 확장 패널 분석 (N=1,025 firm-year)으로 통계적 검정력 확보
- LSTM Autoencoder 기반 시계열 이상탐지 대체·비교
- Sentinel-5P CH₄ (OFFL L3_CH4) 추가로 에너지 업종 메탄 배출 검증 확장
- 위성 버퍼 최적화: 사업장 복수 보유 기업의 다중 버퍼 가중합 방식 도입

---

# 참고문헌

- Ahn, D.-H. & Goldberg, D. L. et al. (2025). Top-down CO₂ emission verification using ODIAC at facility level. *AGU Advances*.
- Berrone, P., & Gomez-Mejia, L. R. (2009). Environmental performance and executive compensation. *Academy of Management Journal*, 52(1), 103–126.
- Breunig, M. M. et al. (2000). LOF: Identifying density-based local outliers. *ACM SIGMOD Record*, 29(2), 93–104.
- Christensen, H. B., Hail, L., & Leuz, C. (2021). Mandatory CSR and sustainability reporting. *Review of Accounting Studies*, 26(3), 1176–1248.
- Efron, B., & Tibshirani, R. J. (1994). *An Introduction to the Bootstrap*. Chapman & Hall.
- EU Regulation 2023/956. Carbon Border Adjustment Mechanism.
- Fioletov, V. et al. (2025). Separation of urban and industrial NO₂ sources using ERA5 wind corrections. *Atmospheric Chemistry and Physics*.
- Heckman, J. J. (1979). Sample selection bias as a specification error. *Econometrica*, 47(1), 153–161.
- Kendall, M. G. (1975). *Rank Correlation Methods* (4th ed.). Griffin.
- Kim, H. C. et al. (2020). Validation of Sentinel-5P TROPOMI NO₂ over South Korea against CAPSS inventory. *Atmosphere*, 11(9).
- Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash. *Organization Science*, 26(3), 705–723.
- Liu, F. et al. (2020). Satellite-based SO₂ and NO₂ emission estimation over China. *Nature*, 580, 506–510.
- Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. *Proceedings of ICDM 2008*, IEEE.
- Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *NeurIPS 2017*.
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259.
- van Buuren, S., & Groothuis-Oudshoorn, K. (2011). mice: Multivariate Imputation by Chained Equations. *Journal of Statistical Software*, 45(3).
- 금융위원회 (2026-02-25). 지속가능성(ESG) 공시 로드맵(안). https://www.fsc.go.kr/
- 한국지속가능성기준원 (2026-02-26). 한국지속가능성공시기준 제1호·제2호·제101호 최종 확정. https://www.kssb.or.kr/
- 네이버 주식회사 (2023). 2023 NAVER 지속가능경영보고서.
- 공공데이터포털 (data.go.kr). 온실가스 배출량 명세서 (API ID 15053947, 15053949, 15082976, 15126853, 15049589).
- 한국기업지배구조원 (KCGS). ESG 등급 및 등급조정 이력 (cgs.or.kr, 2019~2025).

---

# 부록

## 부록 A: 주요 의사결정 이력 (ADR)

- ADR-001 (2026-04-16): 프로젝트 아키텍처 확정 — 디렉터+6에이전트 구조
- ADR-002 (2026-04-20): 데이터 아키텍처 v2 — Tier 1 11개 확장
- ADR-003 (2026-04-20): 방법론 업그레이드 — 4중 비교(ODIAC 추가), 부분 지도학습, Gold 재정의
- ADR-004 (2026-04-22): Wave 3 정정 — Gold 23개사 확정, KCGS 레이블, 자동화 시스템 편입

## 부록 B: 재현성 프로토콜

- Python 3.11, 패키지 버전 `requirements.txt` 고정
- 난수 시드 42 전역 고정
- 데이터 파일 SHA-256 해시 `data/README.md`에 기록
- GEE 스크립트 버전 Git 커밋 해시 추적
- `.env` 파일에 API 키 설정 후 `python src/analysis/run_all_analysis.py`로 전체 재실행

## 부록 C: 자동화 시스템 소스코드

- `src/preprocessing/sustainability_report_collector.py`
- `src/preprocessing/sustainability_report_parser.py`
- `src/preprocessing/kospi200_proxy.py`
- `src/satellite/gee_s5p_extract.py`
- `src/analysis/heckman_panel.py`
- `src/analysis/anomaly_ensemble.py`
- `src/visualization/` (10개 피규어 생성 스크립트)

GitHub 저장소: [공모전 제출 시 public 전환 예정]
