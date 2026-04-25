# 제6장. 분석 방법론

---

## 6.1 ERA5 기상보정

위성 NO₂·SO₂·CO·HCHO의 연간 컬럼 농도는 배출 활동 외에 기상 조건(풍속·풍향·혼합층 고도·강수)에 의해 체계적으로 변동한다. 이를 보정하지 않으면 기업의 배출 활동이 감소했더라도 기온 역전 또는 저풍속 연도에 위성 신호가 증가하는 허위 양성이 발생한다.

본 연구는 Fioletov et al. (2025, *ACP*)의 ERA5 기상보정 방법론을 기업 사업장 단위에 적용한다. 각 기업-연도의 위성 변수 Y(NO₂, SO₂, CO, HCHO)에 대해 다음의 OLS 회귀를 추정한다.

```
Yᵢₜ = α + β₁·u10ᵢₜ + β₂·v10ᵢₜ + β₃·t2mᵢₜ + β₄·tpᵢₜ + β₅·blhᵢₜ + εᵢₜ
```

여기서 u10·v10은 동서·남북 10 m 바람, t2m은 지면 2 m 기온, tp는 총 강수량, blh는 ERA5 경계층 고도다. 잔차 εᵢₜ가 기상보정 위성 신호(meteorology-corrected satellite signal)로, 이후 모든 위성 관련 분석에 사용된다. MERRA-2 4종 변수(PBLTOP, PS, DISPH, QV2M)를 ERA5 대신 투입한 독립 모형으로 민감도를 검증했다.

**표 6.1. ERA5 기상보정 R² (Gold 23개사 × 5년 패널)**

| 위성 변수 | ERA5 5변수 R² | MERRA-2 R² | 해석 |
|---|---|---|---|
| HCHO | 0.94 | 0.91 | 원시 신호의 94%가 기상 변동성 |
| SO₂ | 0.79 | 0.76 | 원시 신호의 79%가 기상 변동성 |
| NO₂ | 0.76 | 0.74 | 원시 신호의 76%가 기상 변동성 |
| CO | 0.67 | 0.64 | 원시 신호의 67%가 기상 변동성 |

출처: `data/processed/era5_correction_r2.csv`. 기상보정의 높은 R²는 기상 통제의 필요성을 정당화하는 동시에, 보정 잔차가 배출 신호를 반영할 가능성을 지지한다. 보정 전·후 패턴 일관성은 민감도 분석에서 확인됐다 (제8장 참조).

---

## 6.2 괴리 지표 설계

GIR-ESG 공시 불일치를 정량화하기 위해 기업-연도 단위 괴리 지표 3종을 정의한다.

**절대 괴리** (단위: tCO₂eq):
```
DIFF_absᵢₜ = GIR_Scope1ᵢₜ - ESG_Scope1ᵢₜ
```

**상대 괴리율** (단위: %):
```
DIFF_relᵢₜ = (GIR_Scope1ᵢₜ - ESG_Scope1ᵢₜ) / GIR_Scope1ᵢₜ × 100
```

**방향 부호** (−1, 0, +1):
```
SIGN_diffᵢₜ = sign(DIFF_relᵢₜ)
```

양의 DIFF_rel(GIR > ESG)은 법정 신고 대비 자체 보고 과소 공시를, 음의 DIFF_rel(GIR < ESG)은 자체 보고 과대 공시를 의미하나, 조직 경계 차이에 의한 해석 가능성을 배제할 수 없다. 본 연구는 DIFF_rel의 분포·이질성·연도 효과를 기술하되, 방향에 대한 인과 해석을 주장하지 않는다.

---

## 6.3 이상탐지 3층 앙상블

이상탐지는 무감독(비지도), 추세 기반, 부분 지도학습의 3층 앙상블 구조로 설계된다.

**Layer 1 — 무감독 단면 이상탐지 (Isolation Forest + LOF)**

`sklearn`의 `IsolationForest`와 `LocalOutlierFactor`를 6개 특성(GIR Scope 1, 기상보정 NO₂, 기상보정 SO₂, 기상보정 CO, 기상보정 HCHO, DIFF_rel) 기준으로 115 firm-year 패널에 적용했다. Contamination 파라미터는 0.05~0.20 범위에서 grid search를 수행하고, KCGS 등급조정 21건 레이블에 대한 precision이 최대화되는 지점(contamination=0.10)을 선택했다. 두 모형이 동시에 이상으로 분류한 firm-year만 Layer 1 이상으로 확정한다.

**Layer 2 — 추세 기반 이상탐지 (Mann-Kendall)**

기업별 5개년 시계열(GIR, ESG, NO₂, ODIAC) 각각에 대해 Mann-Kendall τ를 계산한다. |τ| ≥ 0.4를 방향 확정 임계값으로 설정한다 (Kendall, 1975). 공시 채널(GIR·ESG) 방향과 위성 채널(NO₂·ODIAC) 방향이 반대인 경우를 Layer 2 이상으로 분류한다.

**Layer 3 — 부분 지도학습 (KCGS 레이블 교차 검증)**

KCGS 등급조정 이벤트(21건), GIR 검증기관 변경 이력, K-ETS 사전할당 대비 실배출 gap의 3종 외부 레이블을 이상탐지 결과와 교차 검증한다. Layer 1·2 이상 분류가 이 외부 레이블과 일치하는 경우 신뢰도를 높이고, 불일치하는 경우 분류를 하향 조정한다 (ADR-004 기준).

**이상 등급 최종 분류:**
- **구조적 이상 (Structural)**: Layer 1 ∩ Layer 2 동시 해당 — 단면·추세 모두 비정상
- **추세적 이상 (Longitudinal)**: Layer 2만 해당 — 추세 방향 불일치, 단면은 정상 범위
- **일시적 이상 (Transient)**: Layer 1만 해당 — 특정 연도 단면 이상, 추세는 일치
- **정상 (Normal)**: Layer 1, 2 모두 해당 없음

---

## 6.4 위성 4중 비교 및 패턴 5종 분류

4중 비교의 핵심은 연도별 방향 일관성이다. 기업별 5개년 시계열 각각에 대해 Mann-Kendall τ를 계산하고, |τ| ≥ 0.4를 방향 확정 임계값으로 설정한다. 4개 채널(GIR·ESG·NO₂·ODIAC)의 방향 조합에 따라 5개 패턴으로 분류한다 (figs/fig_pattern_distribution.png, figs/fig_mk_tau_forest.png 참조).

| 패턴 | 정의 | 해석 |
|---|---|---|
| A (일관) | GIR·ESG·NO₂·ODIAC 방향 일치 | 4채널 공시 일관성 높음 |
| B (ESG 이탈) | ESG만 GIR·위성과 반대 방향 | ESG 자체보고 독립 이탈 |
| C (GIR 의심) | GIR만 ESG·위성과 반대 방향 | GIR 법정 신고 독립 이탈 |
| D (최심각) | GIR·ESG 모두 위성·ODIAC과 반대 | 공시 채널 전반 vs 물리 관측 괴리 |
| E (무추세) | 4채널 모두 |τ| < 0.4 | 5개년 유의 추세 없음 |
| mixed | 위 범주에 해당하지 않는 부분 일치 | 복합 패턴 |

NO₂·SO₂·CO·HCHO 4종 위성 신호와 ODIAC CO₂를 모두 고려해 각 채널에 독립적 Mann-Kendall τ를 계산하고, 5채널 중 과반(3개 이상)의 방향이 일치하는 경우를 위성 대표 방향으로 결정한다. 이 다중 위성 투표 방식은 단일 오염물질 측정 잡음에 대한 강건성을 높인다.

---

## 6.5 Heckman 2단계 패널 회귀

ESG 보고서를 발간하는 기업이 비발간 기업과 체계적으로 다를 경우 (선택편향), OLS 회귀는 ESG 자체보고 기업에 대한 불편추정량을 산출하지 못한다. 이를 처리하기 위해 Heckman 2단계 추정법을 적용한다.

**1단계 — 선택 방정식 (Probit)**:
```
ESG_publishedᵢₜ = γ₀ + γ₁·ln_assetsᵢₜ + γ₂·k_ets_allocationᵢₜ + γ₃·kau_priceₜ + uᵢₜ
```
도구변수로 K-ETS 사전할당량(`k_ets_allocation`)과 KAU 연평균 가격(`kau_price`)을 사용했다. 이 변수들은 ESG 보고 여부에 영향을 미치지만 괴리율에는 직접적 영향이 없는 것으로 가정된다. 1단계 추정에서 IMR(Inverse Mills Ratio)을 산출한다.

**2단계 — 결과 방정식 (FE 패널 OLS)**:
```
DIFF_relᵢₜ = β₀ + β₁·ln_gir_scope1ᵢₜ + β₂·IMRᵢₜ + β₃·in_kssb_30ᵢ 
              + β₄·industryᵢ + β₅·yearₜ + ηᵢ + εᵢₜ
```

기업 고정효과(ηᵢ)와 연도 더미를 포함하며, 표준오차는 기업 단위 클러스터링으로 산출한다. Bootstrap 95% CI는 N=1,000 블록 재표본(기업 단위)으로 계산한다. 소샘플(N=104 관측치, 23개 기업)의 추정 불확실성이 CI 폭에 반영된다.

---

## 6.6 SHAP TreeExplainer 기여도 분해

이상탐지 및 우선순위 매트릭스 산출을 위해 학습된 Random Forest 모형에 SHAP(SHapley Additive exPlanations) `TreeExplainer`를 적용한다 (Lundberg & Lee, 2017). 개입적(interventional) SHAP 값 산출 방식을 채택해 특성 간 상관 구조에 강건한 기여도 분해를 수행한다.

SHAP 분석은 두 수준에서 수행된다. 첫째, 전체 패널 수준의 **요약 beeswarm 플롯** (figs/fig_shap_summary.png)으로 이상탐지에 가장 기여한 특성의 전역적 순위를 시각화한다. 둘째, 이상점 상위 5개사에 대한 **개별 waterfall 플롯** (figs/fig_shap_waterfall_top5.png)으로 각 기업의 이상 분류 원인을 분해한다.

---

## 6.7 검증 우선순위 매트릭스

기업별 KSSB 2028 현장 검증 자원 배분을 위한 우선순위 점수를 다음 가중합으로 산출한다.

```
priority_scoreᵢ = 0.4 × discrepancy_percᵢ  (GIR-ESG 괴리율 백분위)
               + 0.4 × satellite_mismatch_wᵢ (위성 불일치 가중치)
               + 0.2 × anomaly_gradeᵢ        (이상탐지 등급)
```

여기서 `satellite_mismatch_w`는 패턴 D=3, B/C=2, E=1, A=0으로 인코딩하고, `anomaly_grade`는 구조적=4, 추세적=3, 일시적=2, 정상=1로 인코딩한다. 점수는 0~1 범위로 정규화한다. 우선순위 상위 10개사를 figs/fig_priority_matrix.png의 4사분면 매트릭스로 시각화한다 (축: 괴리율 × 위성 불일치 가중치).

---

## 6.8 자동화 수집·파싱 파이프라인

지속가능경영보고서 수집·파싱의 자동화 파이프라인은 다음 두 스크립트로 구성되며, `.claude/skills/` 하위에 영구 시스템 기능으로 편입됐다 (ADR-004).

- `src/preprocessing/sustainability_report_collector.py`: DART API + KRX ESG 포털 크롤링, PDF URL 수집·다운로드 자동화.
- `src/preprocessing/sustainability_report_parser.py`: 2단계 파싱(camelot 표 파싱 → regex 폴백), 신뢰도 자동 분류, SHA-256 해시 추적.

이 파이프라인은 `.env` 파일에 API 키를 설정한 후 즉시 재실행 가능하며, 재현성이 SHA-256으로 추적된다. 본 공모전 제출 보고서의 부록 C(소스코드 GitHub 링크)에 접근 경로가 포함된다.

---

## 참고문헌 (제6장 인용)

- Fioletov, V. et al. (2025). Separation of urban and industrial NO₂ sources using ERA5 wind corrections. *Atmospheric Chemistry and Physics*.
- Heckman, J. J. (1979). Sample selection bias as a specification error. *Econometrica*, 47(1), 153–161.
- Kendall, M. G. (1975). *Rank Correlation Methods* (4th ed.). Griffin.
- Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *NeurIPS 2017*.
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259.
