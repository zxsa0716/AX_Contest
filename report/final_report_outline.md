# 최종 보고서 구조 (Draft)

**공모전**: 2026 AX 아이디어 경진대회 · 데이터 분석 > 자유과제 분석
**마감**: 2026-05-18
**제목**: 한국 코스피 상장기업의 온실가스 공시 신뢰성 3중 검증 — GIR×ESG×Sentinel-5P 불일치 패턴과 KSSB 2028 의무공시 검증체계

---

## Executive Summary (1p)

- **문제**: 한국 코스피 상장기업의 GIR 법정 배출량과 ESG 자체보고 간 체계적 괴리 가능성
- **방법**: GIR × ESG × Sentinel-5P NO₂/SO₂/CO/HCHO × **ODIAC CO₂** (4중 비교) + 기상보정 + 이상탐지 3층
- **대상**: KSSB 2028 FY27 의무공시 1차 대상 중 GIR ≥3년 = **Gold 23개사**
- **발견**:
  - **삼성전자 패턴 D (최심각)**: 공시↑ but 위성·ODIAC↓
  - **포스코홀딩스 구조적 이상**: GIR↑↑(+1.0) but 위성·ODIAC↓↓(-1.0) 3년 연속
  - **현대모비스 패턴 C**: GIR↓·ESG↑ 괴리
  - **KSSB 2028 대상 기업 괴리율 평균 -65%p 낮음**: 의무화 대상이 자율적으로 정확 공시 중
- **정책 제언**:
  1. KEITI 환경책임투자 플랫폼에 4중 검증 지수 편입
  2. KSSB 2028 시행 시 Sentinel-5P 위성·GIR 3중 대조 검증 요건 의무화
  3. 패턴 D/C 기업 우선 현장 검증 매트릭스

---

## 1. 연구 배경 및 필요성

### 1.1 온실가스 공시의 두 채널
- GIR 법정 신고 (처벌 있음) vs ESG 자체 보고 (처벌 없음)
- 이론상 동일 대상이나 실무상 괴리 가능성
### 1.2 **KSSB 2028 FY27 의무공시 확정 (2026-02-26)**
- KOSPI 연결자산 30조원↑ **약 58개사** 2028년 의무
- 2026-04 FSC 최종 로드맵 발표 예정 (우리 마감 직전)
### 1.3 위성 + ODIAC 4중 독립 검증의 가능성

→ **→ report/draft_section01_background_v2.md 참조**

## 2. 선행 연구 및 연구 격차

- Liu 2020 (Nature): 중국 Sentinel-5P + 국가 인벤토리
- Kim 2020: 한국 TROPOMI vs CAPSS R=0.96
- Fioletov 2025 (ACP): ERA5 기상보정 표준화
- Ahn-Goldberg 2025 (AGU Adv): 54 cities CO₂ NO₂ + ODIAC
- **본 연구 최초**: 한국 코스피 기업 단위 4중 비교 + KSSB 2028 정책 직결

## 3. 연구 설계

### 3.1 핵심 연구 질문 3개
- RQ1: GIR vs ESG 체계적 괴리 존재?
- RQ2: 위성·ODIAC이 GIR/ESG와 일관?
- RQ3: KSSB 의무공시 대상 검증 우선순위?

### 3.2 4중 비교 프레임
```
GIR 법정 × ESG 자체 × Sentinel-5P 대기 × ODIAC CO₂
  ↓
기상보정 (ERA5 + MERRA-2 + ASOS)
  ↓  
Mann-Kendall 방향 일관성
  ↓
패턴 A / B / C / D / E 분류
```

## 4. 데이터 수집 및 구조

- **17개 데이터셋** (ADR-002):
  - GIR 명세서 7년 (1,585 법인)
  - KRX ESG + DART 지속가능경영보고서 PDF (**93개 자동 수집**)
  - Sentinel-5P NO₂/SO₂/CO/HCHO (GEE)
  - ODIAC v2024 1km CO₂ (60개월 한국 클립)
  - ERA5 + MERRA-2 + ASOS 기상
  - DART 재무 + 통합환경허가 + K-ETS 할당

- **Gold 23개사** 확정 (KSSB 2028 ∩ GIR ≥3yr)

→ report/tables/table02_data_coverage.md

## 5. 전처리 방법론

- 기업명 fuzzy matching (RapidFuzz ≥85)
- VWorld 지오코딩 (22/23 성공)
- PDF 파싱 99% 성공 (HIGH 16, MEDIUM 48, LOW 7)
- GIR Tier 추출 (T1/T2/T3)
- 3계층 샘플 (Gold/Silver/Bronze)

## 6. 분석 방법론 (8단계)

### 6.1 ERA5 기상보정
- u10, v10, t2m, tp, blh 다중회귀 → 잔차 = 기상보정 NO₂/SO₂
### 6.2 괴리 지표 설계
- 절대/상대/방향, Tier 통제
### 6.3 이상탐지 3층
- Layer1: IF+LOF (contamination 0.05~0.20)
- Layer2: Mann-Kendall
- Layer3: KCGS 21건 등급조정 supervised
### 6.4 위성 4중 비교 + 패턴 5종 (★ 독창성)
### 6.5 Heckman 2-stage + FE 패널 + Bootstrap CI
### 6.6 SHAP TreeExplainer (interventional)
### 6.7 정책 우선순위 매트릭스

## 7. 결과

### 7.1 패턴 분포
→ report/tables/table03_pattern_results.md

| 패턴 | N |
|---|---|
| A up | 1 (네이버) |
| A down | 13 |
| **C 현대모비스** | 1 |
| **D 삼성전자** | 1 |
| mixed | 8 (포스코 포함) |

### 7.2 이상탐지 분류
- 구조적: 4 (KEPCO 2020-2023)
- 추세적: 14
- 일시적: 4 (**포스코홀딩스 2021-2023**, SK하이닉스 2021)
- 정상: 93

### 7.3 Heckman 회귀
- ln(GIR): -2.30 (p<0.001) — 대기업일수록 정확
- in_kssb_30: -64.67 (p<0.001) — KSSB 대상 기업 괴리 낮음
- Bootstrap 95% CI 제시

### 7.4 SHAP 기여도 분석
→ figs/fig_shap_summary.png, fig_shap_waterfall_top5.png

## 8. 방법론적 한계 및 대응

원탁회의 8개 한계 표

## 9. 정책 활용 방안 (**3개 카드**)

1. **KEITI 환경책임투자 플랫폼 4중 검증 지수**
2. **패턴 D·C·구조적 이상 기업 우선 현장검증 매트릭스**
3. **KSSB 2028 시행 시 위성·GIR 3중 대조 제도화**

→ report/draft_section09_policy_v2.md

## 10. 결론 및 향후 과제

- 국내 최초 기업 단위 4중 비교
- ESG 자동 수집·파싱 파이프라인 영구 시스템 편입
- 향후: Silver 205개사 확장, LSTM Autoencoder 시계열 이상탐지

---

## 부록

- A: ADR-001~004 (의사결정 이력)
- B: 재현성 프로토콜 (SHA-256 + Python 3.14 + .env 설정)
- C: 자동화 시스템 소스코드 (GitHub)

---

## 제출 체크리스트

- [ ] Executive summary 확정 (1p)
- [ ] Section 1-10 초안 완료
- [ ] 10개 figures 최종 (현재 9개 완료)
- [ ] 4개 tables 최종
- [ ] ADR 4개 첨부
- [ ] 데이터 딕셔너리 첨부
- [ ] 코드 공개 링크 (private → public 전환)
- [ ] 재현성 테스트 (clean clone → re-run)

## Figure 목록 (현재 상태)

| # | 파일 | 내용 | 상태 |
|---|---|---|---|
| 1 | fig_gir_timeseries.png | Gold 23사 GIR 5년 추이 | ✅ |
| 2 | fig_gir_heatmap.png | 기업×연도 GIR 히트맵 | ✅ |
| 3 | fig_satellite_scatter.png | GIR vs NO₂/SO₂/CO/HCHO | ✅ |
| 4 | fig_odiac_scatter.png | GIR vs ODIAC CO₂ 1:1 | ✅ |
| 5 | fig_case_studies.png | 4개사 시계열 overlay | ✅ |
| 6 | fig_pattern_distribution.png | A/B/C/D/E 분포 | ✅ |
| 7 | fig_mk_tau_forest.png | 23사 × 3시계열 τ | ✅ |
| 8 | fig_shap_summary.png | SHAP beeswarm | ✅ |
| 9 | fig_shap_waterfall_top5.png | 상위 5 이상 | ✅ |
| 10 | TBD — 정책 매트릭스 4사분면 | Priority matrix | ⏳ |

**파서 완료 대기 중**: 이후 run_all_analysis.py 한 번 실행으로 전체 재생성.
