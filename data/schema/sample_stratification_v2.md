# Sample Stratification Specification v2 (ADR-003 Implementation)

**Status**: Draft for director approval — Decisions A & B (§7) required before corp-data-manager begins classification build.
**Supersedes**: 참고/final_methodology_report.html Section 5.P3 (Gold/Silver/Bronze v1)
**Governs**: `data/interim/company_universe.parquet`, `data/interim/gold_silver_bronze.parquet`

---

## 1. KSSB 2028 FY27 Target Universe — Operational Definition

### 1.1 What "KOSPI 연결자산 30조원↑" means operationally

- **Exchange**: KOSPI only (KOSDAQ 제외)
- **Asset metric**: K-IFRS 연결재무제표 자산총계 (consolidated total assets), `ifrs-full:Assets`
- **Threshold**: ≥ 30조 KRW at fiscal year-end
- **Pool size**: ~58개사 (KOSPI 시가총액의 약 6.9%)
- **Phase-in**: FY27 (2028 보고) ≥ 30조 → FY29 ≥ 10조 → FY30+ 확대

### 1.2 Reference year

FSC 로드맵(안) 특정 연도 미지정. 보수적 운영 규칙:
- **Primary**: FY2024 연결자산 (로드맵 시점 최신 감사)
- **Secondary**: FY2023 연결자산 (cross-check)
- **Inclusion rule**: 둘 중 하나라도 ≥ 30조 → 후보 포함

### 1.3 58-company list

**2026-04-20 기준 공식 명단 미공표.** 직접 파생 필요.

### 1.4 Derivation procedure

```
Step 1: KRX KOSPI 전체 종목 (~780개) 확보
Step 2: DART corp_code ↔ stock_code 매핑
Step 3: DART finstate CFS fetch (2023, 2024)
  - Endpoint: /api/fnlttSinglAcntAll.json
  - params: corp_code, bsns_year, reprt_code=11011, fs_div=CFS
  - extract: account_nm='자산총계' → thstrm_amount
Step 4: Filter assets_2024 >= 30e12 OR assets_2023 >= 30e12
Step 5: data/interim/kssb_2028_candidate_pool.parquet
Step 6: Sanity check: expected N = 55~65
```

**Edge cases**: 금융지주 별도 플래그, OFS-only 기업 fallback, 2024-2026 합병/분할 기업 제외.

---

## 2. Sample Tier Definitions v2

Year-by-year 평가 후 **firm-level 최종 tier** 결정 (panel balance 유지).

### 2.1 Gold (primary analysis)

```
G1: KOSPI 200 ∈ ≥3/5 years (2019-2023)
G2: GIR managed entity ≥3/5 years
G3: KSSB 2028 candidate (kssb_flag_any == True)
G4: domestic_revenue_ratio ≥ 0.90 in ≥3/5 years
    Source priority: DART II.6 지역별 매출 > 세그먼트 주석 > 수출/내수 split
G5: ESG report with explicit domestic/overseas Scope 1 split
    OR firm operates domestic only (zero material overseas subsidiary per DART 종속회사)
G6: ≥3 years both GIR AND ESG Scope 1 available
G7: No M&A/spinoff > 20% asset change in 2019-2023
```

### 2.2 Silver (robustness)

```
S1: KOSPI 200 ≥3/5 years
S2: GIR managed entity ≥3/5 years
S3: NOT Gold (fails at least one of G3-G5)
S4: domestic_revenue_ratio ≥ 0.70 in ≥3/5 years AND ≥3yrs Scope 1 available
S5: No §2.5 M&A exclusion event
```

### 2.3 Bronze (descriptive only)

```
B1: GIR managed entity ≥2/5 years
B2: NOT Gold AND NOT Silver
B3: Not in §2.5 exclusion list
```
Bronze = **기술 통계만, 회귀·패턴 분류 제외**.

### 2.4 Excluded

- <2 years Scope 1 available
- Section 2.5 M&A/spinoff watchlist
- 사업자번호 매칭 실패
- Panel 기간 중 상장폐지/청산

### 2.5 M&A / Spinoff 초기 Watchlist

corp-data-manager가 DART 최대주주 변동·분할/합병 공시로 검증:
- LG화학 → LG에너지솔루션 분할 (2020-12)
- SK이노베이션 → SK온 물적분할 (2021-10)
- 현대중공업 지주 전환 + 재상장 (2019-2021)
- POSCO → POSCO홀딩스 + 철강 물적분할 (2022-03)
- 삼성바이오로직스 지분 구조 변동 (2018-2019)

**규칙**: 사건이 ≥2/5 year에 발생 또는 연말 걸침 → Gold/Silver 제외. 초기(2019)만 발생하고 이후 안정 → Silver 유지 + `mna_flag_post_2019` 플래그.

---

## 3. Boundary Correction Factor (Silver)

### 3.1 Formula
```
corrected_ESG_Scope1[i,t] = reported_ESG_Scope1[i,t] × domestic_revenue_ratio[i,t]
```

### 3.2 Caveats
- **Upper-bound approximation**, not ground truth
- 국내·해외 배출집약도 동일 가정 (보통 틀림)
- Sensitivity check용, primary 추정량 아님
- 양쪽 수치 모두 보고 (`correction_applied ∈ {none, upper_bound, not_applicable}`)

### 3.3 Dropout
`domestic_revenue_ratio < 0.70` 이면 Silver 불가 → Bronze 강등.

---

## 4. Per-Company Checklist Schema

`data/interim/company_tier_checklist.parquet` 주요 컬럼:

| Column | Source | Note |
|---|---|---|
| corp_code | DART | 8자리 |
| stock_code | KRX | 6자리 |
| business_no | GIR/DART | 사업자등록번호 (primary join) |
| corp_name_kr | DART | — |
| year | — | 2019-2023 |
| kospi200_flag | KRX 정기/수시 변경 | year-varying |
| gir_managed_flag | data.go.kr 15053947 | year-varying |
| gir_scheme | {목표관리, 배출권, both, none} | year-varying |
| k_ets_phase | {Phase1/2/3, none} | 경계 변화 포착 |
| gir_tier | {T1, T2, T3, mixed} | 지배적 Tier |
| assets_consolidated_2023 | DART CFS | KRW |
| assets_consolidated_2024 | DART CFS | KRW |
| kssb_flag_any | derived | assets ≥ 30e12 at any |
| domestic_revenue_ratio | DART II.6 | 0.0-1.0 |
| domestic_revenue_source | {II.6_region, segment_note, export_import, manual} | — |
| esg_report_issued | KRX ESG + DART | year-varying |
| esg_report_standard | {GRI, IFRS_S2, TCFD, KSSB, mixed, none} | — |
| esg_scope1_reported | GRI 305-1 parsing | tCO₂eq |
| esg_scope1_domestic_split | parsed | bool |
| esg_scope1_domestic_only | parsed | if split==True |
| domestic_only_operations | DART 종속회사 | bool |
| third_party_assurance | assurance letter | bool |
| assurance_standard | {ISAE_3410, ISAE_3000, AA1000AS, none} | — |
| assurance_level | {reasonable, limited, none} | — |
| assurance_provider | 검증기관명 | — |
| organizational_boundary | {operational_control, financial_control, equity_share, unspecified} | — |
| mna_event_flag | DART 합병/분할공시 | — |
| mna_material_flag | derived > 20% asset change | — |
| parsing_confidence | pdfplumber + manual | {HIGH, MEDIUM, LOW} |
| tier_final | derived | {Gold, Silver, Bronze, Excluded} |
| tier_exclusion_reason | E-code from §2.4 | str\|null |

---

## 5. Expected N Estimates

| Tier | Low | Central | High |
|---|---|---|---|
| KOSPI 200 ∩ GIR | 55 | 70 | 85 |
| ∩ KSSB 2028 | 28 | 38 | 48 |
| **Gold (∩ G4-G7)** | **18** | **26** | **35** |
| Silver | 25 | 34 | 45 |
| Bronze | 12 | 18 | 25 |
| Excluded | 5 | 8 | 12 |

**Most likely Gold N: 22-30** — ADR-003 "worst case 20-30" 경계선.

### 5.2 Mitigation Ladder (Gold N < 25)

1. G4 완화: domestic_revenue_ratio ≥ 0.85 (G4→G4') — "Gold-relaxed" 병행 보고
2. G7 완화: 2019년 단일 M&A 이벤트만 허용
3. G1 완화: KOSPI200 ≥ 2/5 years
4. **최후의 수단**: G3(KSSB) 제거 → 디렉터 승인 필요, 정책 프레임 약화

Gold N < 20 → halt, user `/decision` 필요.

### 5.3 Bootstrap CI 의무

Gold 최종 N과 관계없이 모든 회귀 결과에 95% Bootstrap CI (B=2000, firm-level block) 보고.

---

## 6. Heckman Selection Impact

### 6.1 1st-stage probit 재정식화
```
P(ESG_report_with_domestic_split = 1)[i,t] = Φ(
    α₀
  + α₁·ln(Assets)               # size
  + α₂·KOSPI200_flag            # listing visibility
  + α₃·KSSB_pool_flag           # REGULATORY DISTANCE (new)
  + α₄·domestic_revenue_ratio   # operational scope
  + α₅·industry_dummies
  + α₆·year_dummies
  + α₇·GIR_Tier                 # measurement accuracy
  + η
)
```

### 6.2 KSSB ≥30조 threshold를 instrument로 사용
- **Exogeneity 논거**: 30조 임계값은 규제 bright line이지 기업 특성 아님. 자산은 sticky함.
- **2nd-stage**: `KSSB_pool_flag` 제외 (exclusion restriction)
- **Robustness**: 20-40조 범위 RD 민감도 분석
- **Caveat**: 58개사 pool은 probit 자유도 제약 — wide CI 예상. `ln(Assets)`와 near-collinearity 가능 → VIF > 10이면 fallback (descriptive first stage)

### 6.3 이점
- "selection control" → "regulatory discontinuity identification"으로 격상
- "우리 샘플 = 의무화 1차 대상" 정책 narrative 직결

---

## 7. Decisions Required from Director

### 7.1 Decision A — Gold = ∩ (KSSB ∩ KOSPI200) or ∪ (KSSB ∪ KOSPI200)?

| Option | Meaning | N impact | Pro | Con |
|---|---|---|---|---|
| **A1 (권장)** | ∩ (KSSB ∩ KOSPI200) | Gold ~22-30 | 타이트한 정책 narrative | 낮은 N |
| A2 | ∪ | Gold ~40-55 | 큰 N | "1차 mandate target" 프레임 희석 |

**추천**: **A1**. §5.2 mitigation으로 N 부족 대응.

### 7.2 Decision B — KOSPI200 membership 처리

| Option | Rule | 권장 |
|---|---|---|
| **B1 (권장)** | year-varying, ≥3/5 years | ✓ |
| B2 | 5년 전부 멤버십 유지 | 작은 N |
| B3 | 1년만 멤버십 있어도 OK | 일시적 멤버 희석 |

**추천**: **B1**.

---

## 8. References

- WRI/WBCSD *Corporate Accounting and Reporting Standard* (2004) Ch.3 (조직경계), Ch.4 (Scope 1/2/3)
- GRI 305: Emissions 2016, Disclosure 305-1 (a-g)
- IFRS S2 *Climate-related Disclosures* paragraphs 29-31
- KSSB 지속가능성 공시기준서 제2호 (2026-02-26 확정)
- 금융위 '지속가능성(ESG) 공시 로드맵(안)' 2026-02-25
- 환경부 '온실가스 배출량 산정·보고·검증 지침' 2024 제4장 (Tier 1/2/3)

---

## 9. Ready for Execution — Gating

| Item | Status |
|---|---|
| Schema definition (§4) | Ready |
| Tier logic (§2) | **Blocked on Decision A** |
| KSSB pool derivation (§1.4) | Ready |
| Boundary correction (§3) | Ready |
| Heckman reformulation (§6) | Ready (post §2) |
| M&A watchlist (§2.5) | Initial ready, verification pending |
| KOSPI200 rule (§7.2) | **Blocked on Decision B** |

**Unblock**: Decisions A & B 확정 시 corp-data-manager 즉시 착수. 예상 기간 5일 (pool derivation 2일 + checklist 구축 3일).
