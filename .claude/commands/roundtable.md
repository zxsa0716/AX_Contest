---
description: Run a parallel roundtable — multiple specialists give independent views on one topic.
argument-hint: <topic>
---

# /roundtable — Multi-agent parallel consultation

한 주제에 대해 여러 전문가의 독립 관점을 병렬로 수집하고 디렉터가 종합.

## 사용법

```
/roundtable <topic in Korean or English>
```

## Director behavior

1. Read the topic in `$ARGUMENTS`.
2. Decide which 2–5 agents are relevant (not all 6 — be surgical).
3. Craft **distinct English prompts** for each — each prompt framed from that agent's perspective, explicitly instructed to ignore concerns outside their domain.
4. Call `Agent` tool **in parallel** (multiple tool calls in the same message).
5. When all return, synthesize in Korean:
   - **관점별 요약**: 각 에이전트 결론 1문장씩
   - **합의점**: 공통 인식
   - **충돌점**: 의견이 갈린 지점과 이유
   - **디렉터 종합 판단**
   - **결정 필요 시**: 사용자에게 선택지 제시 + 기록할 decisions/ADR 제안

## Parallelism rule

**반드시 한 메시지 안에서 여러 Agent 툴콜을 동시 실행.** 순차 실행하면 시간이 N배.

## Example

User: `/roundtable 패턴 D 기업 발견 시 보고서에서 기업명을 공개할 것인가`

Director invokes in parallel:
- `policy-expert` ("what are legal and reputational risks of naming")
- `esg-expert` ("is pattern D sufficient technical evidence")
- `report-writer` ("how to frame without naming — precedents in Korean policy reports")

Then synthesizes: "합의점은 '익명 + 업종' 표기. 충돌은 policy vs esg…"

## Arguments

$ARGUMENTS
