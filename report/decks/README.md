# 발표 자료 5종 thematic deck

본 폴더는 2026 AX 아이디어 경진대회 자유분석 부문 응모작의 발표 자료다. 단일 deck 60장 대신 5개 thematic deck (총 75장)으로 구성하여 발표 시간 배분에 따라 유연 선택 가능하다.

| Part | 파일 | 슬라이드 | 핵심 내용 | 권장 발표 시간 |
|---|---|---|---|---|
| 1 | `01_KeyFindings.pptx` | 16 | 결정적 발견 우선 — 패턴 D 2건, 이상탐지 8건, 통계 비교, Heckman, 우선순위 매트릭스, 정책 | 12-17분 |
| 2 | `02_Background.pptx` | 10 | 연구 배경 — 두 채널 ESG 문제, KSSB 2028 임박, 검증 공백, 선행연구 | 8-10분 |
| 3 | `03_Data_Methodology.pptx` | 17 | 18 데이터셋 + 8단계 분석 파이프라인 + GIR baseline + 4채널 cross-validation | 12-15분 |
| 4 | `04_PerFirm_Analysis.pptx` | 17 | 23개사 × 8 산업군 firm-by-firm + GIR heatmap + 4 산업시설 case studies | 12-15분 |
| 5 | `05_Discussion_Policy.pptx` | 15 | 패턴 D 가설, 한계, robustness, 정책 카드 3종, 국제 비교, stakeholder Q&A, 10년 로드맵, 결론 | 10-13분 |

**전체 발표 시간**: 5개 합산 시 60-70분, Part 1 단독 발표 시 12-17분.

**발표 대본**: `../presentation_script_01_KeyFindings.md` — Part 1 16장 슬라이드별 줄글식 한국어 발표 스크립트, 예상 Q&A 10건, 시간 배분 가이드.

**생성 코드**: `../../src/visualization/generate_pptx_v2.py` — 5개 deck 동시 자동 생성. Python 3.14 + python-pptx 기반.

## 디자인 원칙

- **줄글식 한국어 prose** (bullet point 회피, 자연스러운 문장 흐름)
- **고해상도 figure**, aspect-ratio 보존 (잘림·왜곡 없음)
- **일관된 design token**: BRAND_BLUE `#1E3A8A`, BRAND_TEAL `#0F766E`, INK `#1F2937`, PAPER `#FAFAF7`
- **Cover/Divider/Content 3 layout** typography 계층
- **Page number + footer** (github.com/zxsa0716/AX_Contest)
- **결과 우선** narrative arc (Part 1이 첫 deck)
