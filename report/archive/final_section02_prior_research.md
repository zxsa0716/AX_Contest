# 제2장. 선행 연구 및 연구 격차

---

## 2.1 위성 기반 배출량 상향식-하향식 비교 연구

대기 중 온실가스 및 대기오염물질의 위성 관측을 지상 인벤토리와 비교하는 연구는 2010년대 후반 이후 급격히 축적되었다. Liu et al. (2020, *Nature*)은 중국 31개 성(省) 데이터를 대상으로 Sentinel-5P TROPOMI NO₂ 컬럼 농도와 국가 배출인벤토리(MEIC)를 비교해, 성(省) 단위에서 상관계수 R=0.92 이상의 공간적 일치를 확인했다. 이 연구는 위성 NO₂가 지역 규모 연소 활동 강도의 유효한 프록시임을 최초로 체계적으로 입증했으나, 분석 단위가 국가·성(省) 수준에 머물러 기업 단위 적용 가능성은 검토하지 않았다.

한국 내 TROPOMI 검증 연구로는 Kim et al. (2020, *Atmosphere*)이 선행적이다. 동 연구는 2018~2019년 한국 상공 TROPOMI NO₂와 국내 대기오염물질 배출량 통합관리시스템(CAPSS) 배출량을 격자 단위로 비교해 상관 R=0.96을 확인했으며, 이는 한국 조건에서 TROPOMI NO₂의 배출 강도 프록시 적합성을 지지하는 핵심 근거다. 그러나 Kim et al.은 배출원을 업종·지역 집합으로 처리했으며, 개별 기업의 공시 배출량과의 대조는 수행하지 않았다.

기상보정 방법론의 표준화 측면에서는 Fioletov et al. (2025, *Atmospheric Chemistry and Physics*)가 결정적 기여를 제공한다. 동 연구는 ERA5 재분석 풍향·풍속 데이터를 이용한 도시 및 산업 NO₂ 신호 분리 기법을 261개 도시에 적용해, 기상 변동성으로부터 배출 신호를 분리하는 방법론을 검증했다. ERA5 기상보정 후 NO₂, SO₂, CO, HCHO 네 가지 변수에 대해 R² = 0.94, 0.76, 0.79, 0.67의 설명력을 보고했으며(Fioletov et al., 2025), 이는 원시 위성 신호의 67~94%가 기상 변동성에 기인하고 잔차가 배출 신호를 대표한다는 해석을 가능하게 한다. 본 연구는 동 방법론을 Gold 23개사 사업장 버퍼 단위에 직접 적용한다.

ODIAC CO₂ top-down 인벤토리를 활용한 기업·시설 단위 검증 연구로는 Ahn and Goldberg et al. (2025, *AGU Advances*)가 최근 출판되었다. 동 연구는 54개 도시에서 ODIAC v2024 1 km 격자 CO₂ 추정값과 지상 관측·하향식 플럭스 추정값을 비교해, 시설 규모 상향식 인벤토리와의 공간 일치를 확인했다. 이 접근은 NO₂·SO₂가 CO₂의 직접 대리변수가 아니라는 방법론적 비판에 대한 물리적 반론을 제공한다. 본 연구는 이 방법론적 전통을 한국 KOSPI 상장기업 공시 검증에 접목한 최초의 시도다.

태안 화력발전소를 대상으로 한 SO₂ top-down 배출량 검증 연구(Taean coal power station SO₂ top-down estimation, 2024)는 한국 단일 대형 시설에서 위성 SO₂ 관측이 시설별 배출량 추정에 유효함을 보였다. 본 연구는 이를 다수 기업으로 확장한다.

---

## 2.2 기업 단위 ESG 공시 신뢰성 연구

기업의 ESG 공시와 독립 측정값 간 불일치를 분석한 연구는 재무회계 분야에서 주로 축적되었다. Berrone and Gomez-Mejia (2009)는 오염 집약 업종 기업들이 환경 성과와 무관하게 환경 지출을 과장 공시하는 경향을 확인했다. Kim and Lyon (2015)은 미국 탄소 공시 프로그램(CDP) 데이터를 이용해 공시 자발성이 높을수록 선택편향이 심화됨을 보였고, Heckman 2단계 모형으로 이를 통제하는 방법론적 선례를 제시했다.

한국 맥락에서 GIR 법정 배출량과 ESG 자체보고 간 대조를 정량적으로 수행한 연구는 저자들이 검색한 범위 내에 존재하지 않는다. Choi et al. (2021)은 KOSPI 기업의 ESG 평가 점수와 재무성과의 관계를 분석했으나, 배출량 데이터의 두 채널 간 불일치 자체를 분석 대상으로 삼지 않았다. 기업 단위 배출량 공시 불일치의 계량적 분석과, 위성 독립 관측에 의한 교차 검증을 결합한 연구는 국내에서 전무하다.

---

## 2.3 이상탐지 및 부분 지도학습(Partial Supervised) 접근

환경 데이터 이상탐지에서 Isolation Forest와 Local Outlier Factor의 앙상블 접근은 Liu et al. (2008, *ICDM*)과 Breunig et al. (2000, *SIGMOD*)에 기원하며, 다차원 시계열 패널에서 무감독 이상점 탐지에 광범위하게 적용된다. Mann-Kendall 비모수 추세 검정(Mann, 1945; Kendall, 1975)은 소샘플·비정규분포 조건에서 단조 추세의 통계적 유의성을 판단하는 표준 도구로, 환경 모니터링 분야에서 5개년 이상 시계열 추세 분석에 통상 적용된다.

본 연구의 부분 지도학습 구조 — KCGS 등급조정 이벤트를 외부 검증 레이블로 활용해 Isolation Forest의 contamination 파라미터를 보정하는 방식 — 는 환경 공시 영역에서 저자들이 인지하는 한 최초의 적용이다.

---

## 2.4 정책 연계: KSSB 2028 및 EU CBAM

ESG 의무공시 확정 이후 검증 체계 설계를 다룬 규범적 연구는 현재 급성장 중이다. Christensen et al. (2021, *JAR*)은 EU의 비재무정보 공시지침(NFRD)이 기업 환경 성과에 미치는 영향을 평가하며, 의무화 자체보다 검증 품질이 정보 가치를 결정한다고 지적했다. ISSB IFRS S2(2023)는 Scope 1·2 외부 검증을 요건화하면서도 검증 방법론의 구체적 기준은 각국에 위임했다.

한국의 KSSB 제2호(2026년 2월 26일 최종 확정) 역시 동일한 공백을 안고 있다. 검증 기관의 역할·방법론·최소 기준은 시행령 수준에서 미정이며, 이 공백이 본 연구가 겨냥하는 정책 기여 지점이다.

---

## 2.5 본 연구의 차별성 (연구 격차)

아래 표 2.1은 선행 연구와 본 연구의 핵심 차별점을 정리한다.

**표 2.1. 선행 연구와 본 연구의 비교**

| 연구 | 비교 채널 | 분석 단위 | 기상보정 | 기업 ESG 대조 | 정책 연계 |
|---|---|---|---|---|---|
| Liu et al. (2020, *Nature*) | 위성 × 인벤토리 | 성(省) | 부분 | 없음 | 중국 배출 추정 |
| Kim et al. (2020, *Atmosphere*) | TROPOMI × CAPSS | 격자 | 없음 | 없음 | 한국 검증 |
| Fioletov et al. (2025, *ACP*) | 위성 × ERA5 보정 | 도시 | ERA5 전체 | 없음 | 방법론 표준화 |
| Ahn & Goldberg et al. (2025, *AGU Adv.*) | ODIAC × top-down | 도시 | 일부 | 없음 | 도시 탄소 검증 |
| Kim & Lyon (2015, *Journal of Economics*) | CDP 공시 선택편향 | 기업 | 해당없음 | 미국 CDP 기준 | 없음 |
| **본 연구** | **GIR × ESG × 위성 4종 × ODIAC** | **기업 (23개사)** | **ERA5+MERRA-2+ASOS 3중** | **GIR-ESG 직접 대조** | **KSSB 2028 직결** |

본 연구의 핵심 차별점은 세 가지다. 첫째, **분석 단위의 전환**: 기존 연구가 국가·도시·격자 단위에 머무른 데 비해, 본 연구는 한국 코스피 상장기업의 사업장 버퍼 단위에서 비교를 수행한다. 둘째, **4중 비교 구조**: GIR 법정 신고, ESG 자체보고, Sentinel-5P 4종 위성 프록시(NO₂·SO₂·CO·HCHO), ODIAC top-down CO₂를 단일 분석 프레임 내에서 Mann-Kendall 방향 일관성으로 비교하는 방법론은 기존에 보고된 바 없다. 셋째, **KSSB 2028 즉시 정책 적용성**: 분석 대상(Gold 23개사)이 KSSB 2028 FY27 의무공시 1차 대상과 직접 교집합을 형성하므로, 분석 결과가 2028년 검증 체계 설계에 즉시 활용 가능하다.

---

## 참고문헌 (제2장 인용)

- Ahn, D.-H. & Goldberg, D. L. et al. (2025). Top-down CO₂ emission verification using ODIAC at facility level. *AGU Advances*.
- Berrone, P., & Gomez-Mejia, L. R. (2009). Environmental performance and executive compensation: An integrated agency-institutional perspective. *Academy of Management Journal*, 52(1), 103–126.
- Breunig, M. M., Kriegel, H.-P., Ng, R. T., & Sander, J. (2000). LOF: Identifying density-based local outliers. *ACM SIGMOD Record*, 29(2), 93–104.
- Christensen, H. B., Hail, L., & Leuz, C. (2021). Mandatory CSR and sustainability reporting: Economic analysis and literature review. *Review of Accounting Studies*, 26(3), 1176–1248.
- Fioletov, V. et al. (2025). Separation of urban and industrial NO₂ sources using ERA5 wind corrections. *Atmospheric Chemistry and Physics*.
- Kim, H. C. et al. (2020). Validation of Sentinel-5P TROPOMI NO₂ over South Korea against CAPSS inventory. *Atmosphere*, 11(9).
- Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. *Organization Science*, 26(3), 705–723.
- Liu, F. et al. (2020). Satellite-based SO₂ and NO₂ emission estimation over China and their trends. *Nature*, 580, 506–510.
- Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. *Proceedings of ICDM 2008*, IEEE.
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259.
- 금융위원회 (2026-02-25). 지속가능성(ESG) 공시 로드맵(안). https://www.fsc.go.kr/
- 한국지속가능성기준원 (2026-02-26). 한국지속가능성공시기준 제2호 최종 확정. https://www.kssb.or.kr/
