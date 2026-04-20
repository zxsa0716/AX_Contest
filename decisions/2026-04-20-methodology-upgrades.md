# ADR-003: 방법론 3대 업그레이드 + 정책 서술 현행화

**Date**: 2026-04-20
**Status**: Accepted
**Deciders**: 사용자(연구자), 디렉터

## Context

2026년 4월 기준 한국 ESG 의무공시 상태가 기존 참고 문서 작성 시점과 크게 달라졌다. 또한 데이터 아키텍처 v2(ADR-002)로 ODIAC, 할당계획 변경공고 등이 추가됨에 따라 분석 프레임 자체를 업그레이드할 여지가 생겼다.

## Decision

### 업그레이드 1: 3중 비교 → 4중 비교 (ODIAC 추가)

기존:
```
GIR (법정) × ESG (자체) × 위성 프록시 (NO₂/SO₂)
```
변경:
```
GIR (법정) × ESG (자체) × 위성 프록시 (NO₂/SO₂/CO/HCHO) × ODIAC-CO₂ (top-down 1km)
```
효과: "NO₂는 CO₂가 아니다"는 방법론 비판을 ODIAC의 직접 CO₂ 컬럼으로 물리적으로 해결. Ahn-Goldberg et al. 2025 AGU Advances 방법론 모방.

### 업그레이드 2: 이상탐지 unsupervised → partial supervised

기존: Isolation Forest + LOF + Mann-Kendall 앙상블 — **라벨 없음**

변경: 환경부 할당계획 변경공고에서 추출한 **"GIR 배출량 수정된 기업-연도 쌍"** 을 external validation label로 사용. 모델이 해당 기업들을 "이상"으로 정확히 식별하는지 precision/recall 보고.

효과:
- Isolation Forest contamination sensitivity 분석이 실제 ground truth로 보정됨
- 학술지 리뷰어의 "이상탐지 검증 기준이 자의적" 지적 방어
- 논문 급 방법론 기여로 격상

### 업그레이드 3: Gold 샘플 재정의

기존:
```
Gold = 코스피200 ∩ GIR × 국내매출≥90% × Scope 1 국내/해외 분리기재 × GIR-DART 연계
```
변경:
```
Gold = 위 조건 ∩ KSSB 2028 FY27 의무화 1차 대상 (KOSPI 연결자산 30조원↑ 약 58개사)
```
효과: "본 연구 대상 = 실제 의무화 1차 대상" 프레임 → 정책 즉시 활용성 극대화 → 심사기준 5번(활용방안) 직접 강화.

### 업그레이드 4: Section 9 정책 서술 전면 개정

기존 참고/final_methodology_report.html Section 1.2, 9 요지: "의무화 시기는 2026년 이후로 추진 중이나 구체적 일정은 아직 확정되지 않은 상태"

현실 (2026-04-20 기준):
- **2026-02-25**: FSC '지속가능성(ESG) 공시 로드맵(안)' 발표
- **2026-02-26**: KSSB 공시기준 최종 확정 (제1호 IFRS S1 반영, 제2호 IFRS S2 반영, 제101호 추가 선택공시)
- **2028년 FY27 시작**: KOSPI 연결자산 30조원↑ 약 58개사 의무공시 1차 적용
- **2026-04 중**: ESG금융추진단 최종 로드맵 확정 발표 예정 (공모전 마감 5/18 직전)
- **EU CBAM 2026년**: 철강·알루미늄·비료·시멘트·수소·전력 6종 본격 과세

정책 프레이밍 전환: "의무화 논의 중" → **"의무화 확정, 2년 앞둔 지금이 검증체계 설계 골든 타임, 대상 58개사가 우리 Gold 샘플과 교집합"**

## Consequences

### Positive
- 방법론 방어력·독창성·정책 즉시성 모두 상승
- ADR-002의 데이터 확장과 프레임이 정확히 맞물림
- 원탁회의 8개 한계 중 "ML 컨타미네이션 자의적" + "방향부호 잡음" + "조직경계 불일치" + "인과 주장 불가" 4개를 동시 방어

### Negative
- Gold 샘플이 58개사 부분집합이 될 수 있어 N 감소 우려 (기존 30~50 → 최악 20~30까지 축소 가능)
- 대응: 교집합 완성 시 데이터-analyst가 Bootstrap CI로 소샘플 정량화. Silver 샘플(기존 규칙)을 robustness 비교군으로 병행.

### Neutral
- 논문/보고서 서술이 Liu 2020, Kim 2020 외에 Ahn-Goldberg 2025 (AGU Adv), Fioletov 2025 (ACP), KSSB 2026 기준을 추가 인용해야 함 (report-writer 업무)

## Alternatives considered

- **ODIAC 없이 S5P CO + HCHO만 추가**: 비용 절감되나 직접 CO₂ 컬럼 부재로 방어력 제한. 기각.
- **Gold 샘플 재정의 미적용 (기존 코스피200 교집합 유지)**: 정책 프레임 약화. 기각.
- **Section 9를 분석 결과 나온 후 갱신**: 보고서 쓰면서 모순 수정 부담. 지금 확정 권장. 수락.

## Related files

- `decisions/2026-04-20-data-architecture-v2.md` (ADR-002, pair)
- `참고/final_methodology_report.html` (Section 1.2, Section 6.3, Section 6.4, Section 9 — report-writer가 전면 업데이트)
- `CLAUDE.md` (프로젝트 핵심 사실 → KSSB 2028 추가)
