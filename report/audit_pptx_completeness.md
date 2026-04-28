# PPTX 완성도 점검 보고서 (2026-04-28)

본 문서는 5개 thematic PPTX deck의 콘텐츠 완성도와 figure 활용도를 audit한 결과를 기록한다.

---

## 1. 변경 전후 요약

### 변경 전 (commit `01d24c6` 시점)
- **5 decks · 67 slides 총합**
- **사용된 figure 21개 / 미사용 5개** (`fig_gir_timeseries`, `fig_gir_heatmap`, `fig_satellite_scatter`, `fig_odiac_scatter`, `fig_case_studies`)
- **보고서에 추가됐으나 PPT에 미반영된 신규 섹션 4개**: §7.7, §10.6, §10.7, §11.4

### 변경 후 (현 commit)
- **5 decks · 75 slides 총합 (+8 slides)**
- **figure 활용 25/26 (96%)** — `fig_odiac_scatter` 1개만 미사용 (fig_satellite_scatter와 중복 정보)
- **보고서 모든 신규 섹션 PPT 반영 완료**

---

## 2. Deck별 점검 결과

### Deck 1 — KeyFindings (15 → 16 slides)

| # | 변경 | 내용 |
|---|---|---|
| 13 | **신규** | "패턴군 통계적 비교 — 분류 신뢰성 정량화" (§7.7 반영, Kruskal-Wallis H, Fisher 정확검정, Spearman, 산업 FE) |
| 14-16 | renumber | 기존 13(강건성)·14(의의)·15(결론) → 14·15·16 |

**판정**: ✅ 완성. 결과 우선 흐름 유지. 통계 robustness가 hero finding 직후·정책 직전에 들어가 심사위원의 신뢰성 우려를 사전 차단.

### Deck 2 — Background (10 slides, 변경 없음)

**판정**: ✅ 변경 불필요. 배경/문제의식의 narrative arc가 완결적.

### Deck 3 — Data_Methodology (15 → 17 slides)

| # | 변경 | 내용 |
|---|---|---|
| 14 | **신규** | "Gold 23개사 GIR Scope 1 5년 baseline" (`fig_gir_timeseries`) |
| 15 | **신규** | "GIR vs 위성·ODIAC 채널 검증 — 4채널 cross-validation" (`fig_satellite_scatter`) |
| 16-17 | renumber | 기존 14(QC)·15(재현성) → 16·17 |

**판정**: ✅ 완성. 방법론 deck에 분석 대상 raw data 가시화 + 채널 신뢰성 정량 검증이 추가되어 학술적 완결성 확보.

### Deck 4 — PerFirm_Analysis (15 → 17 slides)

| # | 변경 | 내용 |
|---|---|---|
| 14 | **신규** | "Gold 23개사 GIR firm × year 히트맵" (`fig_gir_heatmap`) |
| 15 | **신규** | "4개 핵심 산업시설 firm-by-firm 시계열 비교" (`fig_case_studies`) |
| 16-17 | renumber | 기존 14(종합)·15(정책 함의) → 16·17 |

**판정**: ✅ 완성. firm-by-firm narrative 다음에 전수 heatmap + 4 핵심 case 비교가 포함되어 시각적 매듭 강화.

### Deck 5 — Discussion_Policy (12 → 15 slides)

| # | 변경 | 내용 |
|---|---|---|
| 11 | **신규** | "국제 비교 — 4중 검증 프레임워크의 글로벌 위상" (§10.6 반영, EU CBAM·일본·EPA·IFRS S2) |
| 12 | **신규** | "이해관계자 예상 질문 — 5개 stakeholder 시각" (§10.7 반영, 환경부·KSSB·IR·펀드매니저·시민) |
| 13 | **신규** | "10년 로드맵 — 한국 ESG 검증 인프라 비전" (§11.4 반영, Phase 1-5, 2026-2035) |
| 14-15 | renumber | 기존 11(기여 요약)·12(결론) → 14·15 |

**판정**: ✅ 완성. 정책 deck에 국제 위상·stakeholder 분석·장기 비전이 추가되어 발표의 깊이가 정책 평가자(KSSB·환경부) 수준으로 격상.

---

## 3. Figure 활용 매트릭스 (26 figures)

| # | Figure | Deck/Slide | 상태 |
|---|---|---|---|
| 1 | fig_concept_4channel | D1·S2, D2·S8, D3·S2 | ✅ 다중 활용 |
| 2 | fig_pattern_distribution | D1·S3, D4·S7 | ✅ |
| 3 | fig_posco_4channel_detail | D1·S4, D4·S3 | ✅ |
| 4 | fig_industrial_no2_timeseries | D1·S5, D3·S5 | ✅ |
| 5 | fig_all23_normalized | D1·S6, D4·S6 | ✅ |
| 6 | fig_anomaly_2d | D1·S7, D3·S11 | ✅ |
| 7 | fig_top6_multipanel | D1·S8, D4·S13 | ✅ |
| 8 | fig_heckman_forest | D1·S9·S10, D5·S4 | ✅ |
| 9 | fig_priority_matrix | D1·S11·S12, D3·S8, D5·S7·S8 | ✅ |
| 10 | fig_s5p_4species_korea | D3·S3 | ✅ |
| 11 | fig_map_odiac_seasonal | D3·S6 | ✅ |
| 12 | fig_map_asos_stations | D3·S7 | ✅ |
| 13 | fig_mk_tau_forest | D3·S9 | ✅ |
| 14 | fig_shap_summary | D3·S12 | ✅ |
| 15 | fig_shap_waterfall_top5 | D3·S13 | ✅ |
| 16 | fig_industry_boxplot | D4·S2 | ✅ |
| 17 | fig_industry_timeseries | D4·S4·S10 | ✅ |
| 18 | fig_map_patterns | D4·S11 | ✅ |
| 19 | fig_odiac_change_2019_2023 | D4·S12 | ✅ |
| 20 | fig_map_odiac_korea | D2·S5 | ✅ |
| 21 | fig_map_gold_sites | D2·S6·S9 | ✅ |
| 22 | **fig_gir_timeseries** | **D3·S14 (신규)** | ✅ |
| 23 | **fig_satellite_scatter** | **D3·S15 (신규)** | ✅ |
| 24 | **fig_gir_heatmap** | **D4·S14 (신규)** | ✅ |
| 25 | **fig_case_studies** | **D4·S15 (신규)** | ✅ |
| 26 | fig_odiac_scatter | (없음) | ⚠️ 미사용 |

**활용률**: 25 / 26 = **96.2%**

`fig_odiac_scatter`만 미사용 — `fig_satellite_scatter`(GIR vs 위성 4종 + ODIAC scatter 통합 plot)와 정보 중복이므로 의도적 제외. 필요 시 D3·S15에 추가 panel로 통합 가능.

---

## 4. 보고서 ↔ PPT 섹션 매핑 (커버리지)

| 보고서 섹션 | PPT 위치 | 상태 |
|---|---|---|
| 연구 요약 | D1·S2, D5·S15 | ✅ |
| §1.1 두 채널 신뢰성 문제 | D2·S2 | ✅ |
| §1.2 KSSB 2028 골든 타임 | D2·S3, D1·S16 | ✅ |
| §1.3 위성 + 4중 비교 | D2·S5·S6 | ✅ |
| §2.1-2.3 선행 연구 | D2·S6 | ✅ |
| §3.1 연구 질문 | D2·S7 | ✅ |
| §3.2-3.3 분석 대상·프레임 | D2·S8·S9 | ✅ |
| §3.4 인과 추론 한계 | D5·S3·S4·S5 | ✅ |
| §4.1-4.5 데이터 명세 | D3·S2·S3·S6·S14 | ✅ |
| §5.1 7단계 전처리 | D3·S4·S5·S7 | ✅ |
| §6.1 ERA5 기상보정 | D3·S7 | ✅ |
| §6.2 괴리 지표 | D1·S3·S7 | ✅ |
| §6.3 이상탐지 3층 | D1·S7·S8, D3·S11 | ✅ |
| §6.4 4중 비교 패턴 5종 | D1·S3, D3·S9 | ✅ |
| §6.5 Heckman 2단계 | D1·S9·S10, D3·S10, D5·S4 | ✅ |
| §6.6 SHAP | D3·S12·S13 | ✅ |
| §6.7 우선순위 매트릭스 | D1·S11·S12, D3·S8, D5·S7·S8 | ✅ |
| §6.8 자동화 파이프라인 | D3·S4 | ✅ |
| §7.1 패턴 분류 결과 | D1·S3, D4·S7 | ✅ |
| §7.2 이상탐지 결과 | D1·S7·S8 | ✅ |
| §7.3 패널 회귀 | D1·S9·S10 | ✅ |
| §7.4 우선순위 상위 10 | D1·S11 | ✅ |
| §7.5 SHAP 분해 | D3·S12·S13 | ✅ |
| §7.6 23개사 심층 (8 industry) | D4·S3-S10 | ✅ |
| **§7.7 패턴군 통계 비교** | **D1·S13 (신규)** | ✅ |
| §8.0 좌표 정합성 한계 | D5·S3 | ✅ |
| §9.1-9.3 정책 카드 3종 | D1·S12, D5·S7·S8·S9 | ✅ |
| §9.4 KSSB 즉시 활용 | D1·S12·S16, D5·S15 | ✅ |
| §10.1-10.5 종합 논의 | D5·S2·S3·S4·S5·S6 | ✅ |
| **§10.6 국제 비교** | **D5·S11 (신규)** | ✅ |
| **§10.7 stakeholder Q&A** | **D5·S12 (신규)** | ✅ |
| §11.1-11.3 결론·향후 | D5·S10·S14·S15 | ✅ |
| **§11.4 10년 로드맵** | **D5·S13 (신규)** | ✅ |

**커버리지**: 보고서 모든 절 PPT에 매핑 완료. **빈틈 없음**.

---

## 5. PPT 구성 품질 점검

| 항목 | 점검 | 판정 |
|---|---|---|
| **Cover/Divider 일관성** | 5 decks 모두 동일 design token (BRAND_BLUE, INK, PAPER) | ✅ |
| **Page numbers + footer** | 모든 content slide에 "X / total" + github 표시 | ✅ |
| **Figure aspect ratio** | Image 슬라이드 max 5"H · 11.5"W, aspect-ratio 보존 | ✅ |
| **Prose 흐름** | bullet point 없음, 줄글 한국어 prose 일관 | ✅ |
| **Title hierarchy** | Cover 40pt, Divider 36pt, Content 24pt, Body 13pt | ✅ |
| **Color contrast** | INK 본문 / BRAND_BLUE 강조 / INK_LIGHT 캡션 | ✅ |
| **Section dividers** | 각 deck 구조적 전환점에 §번호 + section title | ✅ |
| **Slide density** | 너무 빽빽하지 않게 word_wrap + space_after Pt(8) | ✅ |

---

## 6. 잠재 개선 항목 (미반영, 추후 옵션)

다음 항목은 본 audit에서 식별됐으나 현재 변경하지 않음. 추후 시간 여유 시 추가 가능.

1. **fig_odiac_scatter 별도 슬라이드** (D3·S16에 추가 panel) — 정보 중복으로 우선순위 낮음
2. **Deck 2에 PRISMA-style flow diagram** — 자료 수집 흐름 시각화. fig_concept_4channel으로 부분 대체됨
3. **Deck 4에 firm-level 23개사 mini-card grid 슬라이드** — 한 화면에 23개사 패턴 라벨 모음
4. **Deck 5에 비용편익 분석 결과 표** (49개사 차등 검증 26억 vs 평등 49억)

---

## 7. 최종 PPT 인벤토리

```
report/decks/
├── 01_KeyFindings.pptx        — 16 slides (4.2MB)
├── 02_Background.pptx         — 10 slides (1.7MB)
├── 03_Data_Methodology.pptx   — 17 slides (5.8MB est.)
├── 04_PerFirm_Analysis.pptx   — 17 slides (5.5MB est.)
└── 05_Discussion_Policy.pptx  — 15 slides (0.6MB est.)

총 75 slides, 발표 시간 60-75분 (5 deck 합산)
단일 deck 발표 시 12-17분 (deck 1 기준)
```

---

## 8. 결론

**완성도 평가**: PPT 5개 deck는 보고서의 모든 핵심 섹션을 빠짐없이 매핑하며, 26개 figure 중 25개를 활용한다. 결과 우선 → 배경 → 방법 → firm 분석 → 정책의 narrative arc가 일관되며, 줄글식 한국어 prose + 고해상도 figure + 일관된 design token이 적용됐다.

**심사위원에게 보여줄 권장 흐름**:
1. **Part 1 (16장 · 12-17분)** 단독 발표 권장 — 결과·통계·정책의 핵심 narrative
2. Q&A 시 Part 3-5 슬라이드를 reference로 호출 가능
3. 발표 자료 inventory + 발표 대본은 `report/presentation_script_01_KeyFindings.md` 참조

**문서 상태**: ✅ 완성. 추가 개선 사항은 §6의 옵션 항목으로 보류.
