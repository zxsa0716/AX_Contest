---
description: Document a handoff between agents — record what was done and what the next agent needs to know.
argument-hint: <from-agent> <to-agent> [note]
---

# /handoff — Inter-agent handoff documentation

서브에이전트들은 서로의 컨텍스트를 공유하지 않는다. 한 에이전트가 완료한 작업을 다음 에이전트가 이어받을 때, 디렉터가 명시적으로 인수인계 문서를 기록한다.

## 사용법

```
/handoff <from-agent> <to-agent> [optional note]
```

Short names: `policy`, `data`, `esg`, `analyst`, `algo`, `report`

## Director behavior

1. Parse `$ARGUMENTS` for from/to agents and optional note.
2. **Invoke the `from` agent** with a specific prompt asking it to produce a handoff note containing:
   - What was done (files produced, decisions made)
   - What assumptions the work rests on
   - What the `to` agent needs to know to continue
   - Open questions / flags for director
3. When `from` returns, write the handoff note to `decisions/handoff-<YYYY-MM-DD>-<from>-to-<to>.md`.
4. **Summarize to user in Korean**: what was handed off, where the record is, and suggest the next `/consult <to>` invocation.

## Handoff note format (in the saved file)

```markdown
# Handoff: <from> → <to>
**Date**: YYYY-MM-DD
**Context**: [1 line of what triggered this]

## What was completed
- [Artifact 1: path — what it contains]
- [Artifact 2: ...]

## Assumptions / boundaries
- [Assumption 1]
- [Assumption 2]

## What the receiver needs to know
- [Key fact 1]
- [Key fact 2]

## Open questions (for director)
- [ ] Question 1
- [ ] Question 2
```

## Arguments

$ARGUMENTS
