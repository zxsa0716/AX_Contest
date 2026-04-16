---
description: Consult a single specialist subagent about a specific question.
argument-hint: <agent-name> <question>
---

# /consult — Single-agent consultation

사용자가 특정 전문 에이전트에게 질문을 위임할 때 사용.

## 사용법

```
/consult <agent-short-name> <question in Korean or English>
```

### Agent short-name mapping
- `policy` → `policy-expert`
- `data` → `corp-data-manager`
- `esg` → `esg-expert`
- `analyst` → `data-analyst`
- `algo` → `algo-researcher`
- `report` → `report-writer`

## Director behavior when this command is invoked

1. Parse `$ARGUMENTS` to extract the agent short-name (first token) and the question (rest).
2. Map short-name to full agent name. If unknown, ask the user which agent they meant.
3. Translate the user's question into a **self-contained English prompt** for the subagent.
   - Include what they already know, what they're trying to decide, and what output format you want.
   - Point the subagent to relevant `참고/` files or `decisions/` entries when applicable.
4. Call the `Agent` tool with `subagent_type=<full-agent-name>`.
5. When the subagent returns, **summarize in Korean** with:
   - 핵심 결론 (1~3 bullets)
   - 디렉터 판단 (너의 해석)
   - 사용자 선택지 또는 다음 단계
6. If the subagent's response reveals a decision point, add `## 결정 필요` section and ask explicitly.

## Example

User: `/consult esg GRI 305-1 항목에서 조직 경계가 control approach인 기업 어떻게 식별?`

Director:
- Invokes `esg-expert` with an English prompt that includes: the current 3-tier sample strategy, example companies, the column we want to produce.
- Receives detailed methodology.
- Replies in Korean: "핵심 결론: 보고서 '보고 경계' 섹션 체크리스트 3개…  / 디렉터 판단: Gold 샘플 기준을 확장 가능 / 사용자 선택: ① 현재 기준 유지 ② control approach 기업 추가 포함"

## Arguments

$ARGUMENTS
