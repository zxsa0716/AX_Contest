# ADR-001: 프로젝트 아키텍처 — 디렉터 + 6 서브에이전트 구조

**Date**: 2026-04-16
**Status**: Accepted
**Deciders**: 사용자 (연구자), 디렉터

## Context

2026 AX 아이디어 경진대회 (마감 5/18, 약 5주) 자유분석 부문 응모. 주제 "한국 코스피 상장기업 온실가스 공시 신뢰성 3중 검증"은 정책·데이터·ESG 도메인·통계 방법론·원격탐사 알고리즘·보고서 작성이 얽힌 복합 프로젝트. 단일 세션 단일 컨텍스트로는 품질 확보가 어렵다고 판단.

## Decision

Claude Code 메인 세션을 **디렉터**로 운용하고, 6개 전문 서브에이전트를 `.claude/agents/`에 배치.

- `policy-expert` (Opus): KEITI·환경부·ISSB·CBAM 정책
- `corp-data-manager` (Sonnet): GIR·KRX·DART 데이터 수집·전처리
- `esg-expert` (Opus): GRI 305-1·GHG Protocol·조직경계
- `data-analyst` (Opus): 패널회귀·Heckman·Mann-Kendall·SHAP
- `algo-researcher` (Opus): Sentinel-5P·GEE·선행연구 스카우트
- `report-writer` (Sonnet): 보고서·피규어·Gamma 프레젠테이션

사용자↔디렉터 = 한국어, 디렉터↔에이전트 = 영어, 에이전트 내부 = 영어, 최종 보고서 = 한국어.

슬래시 커맨드 6종: `/consult`, `/roundtable`, `/standup`, `/handoff`, `/decision`, `/paper`.

MCP: Scholar Gateway · Consensus · Exa · Gamma (이미 연결됨) + 기본 WebSearch·WebFetch. Notion은 선택.

## Consequences

### Positive
- 전문성별 컨텍스트 격리 → 메인 세션 오염 방지
- 병렬 호출 가능 → 시간 효율
- ADR 체계로 결정 이력 추적
- Opus 4명/Sonnet 2명으로 비용-품질 균형

### Negative
- 서브에이전트 간 직접 통신 불가 → 디렉터가 중개 부담
- 첫 주는 에이전트 튜닝에 시간 소요
- Opus 4명 병렬 호출 시 비용 증가 구간 존재

### Neutral
- Skills는 4주차 이후 반복 패턴 드러날 때 추출
- Sub-session별 재현성은 커밋 ID + ADR로 보완

## Alternatives considered

- **단일 세션 단독 진행**: 컨텍스트 과포화, 전문성 깊이 부족. 기각.
- **모두 Opus**: 비용 대비 효용 낮음. Sonnet으로 충분한 역할은 분리. 기각.
- **외부 Notion에 ADR 기록**: 진행 중 의존성 증가. 로컬 파일 우선, 필요 시 동기화. 보류.

## Related files

- `CLAUDE.md`
- `.claude/agents/*.md`
- `.claude/commands/*.md`
- `.claude/settings.json`
