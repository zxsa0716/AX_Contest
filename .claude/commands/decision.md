---
description: Director escalates a decision point to the user with structured options.
argument-hint: <topic>
---

# /decision — Escalate decision to user

프로젝트 진행 중 사용자 판단이 필요한 분기점을 구조화해서 제시하고, 결정 후 ADR(Architecture Decision Record)로 기록.

## Director behavior

1. Parse the topic from `$ARGUMENTS`.
2. If decision requires domain evidence, **first** silently call relevant subagent(s) to gather facts (but do not present raw).
3. Present to user in Korean using this structure:

```
## 🧭 결정 필요: [제목]

### 배경
[왜 지금 결정이 필요한지 — 1~2 문장]

### 판단 근거 (에이전트 자문 요약)
- [esg-expert]: [핵심 근거 1]
- [data-analyst]: [핵심 근거 2]

### 선택지

**옵션 A**: [이름]
- 장점: ...
- 단점: ...
- 영향: [이 결정이 변경할 후속 작업]

**옵션 B**: [이름]
- 장점: ...
- 단점: ...
- 영향: ...

**옵션 C (있다면)**: ...

### 디렉터 추천
[내 판단 — 한 옵션 지목 + 이유 2줄. 사용자는 물론 자유롭게 반대 선택 가능]

### ❓ 답변 형식
"A로 진행" / "B로 진행" / "더 조사해봐" / "다른 옵션 제시해봐" 중 하나로 답해주세요.
```

4. 사용자 응답 수신 후:
   - 결정을 `decisions/YYYY-MM-DD-<topic-slug>.md` 파일로 저장
   - 형식: 아래 ADR 템플릿 사용
   - 저장 후 영향받는 에이전트들에게 "결정 통보" 프롬프트에 포함 필요한 내용 메모
   - 사용자에게 저장 경로 알리고 다음 단계 제안

## ADR 파일 형식

```markdown
# ADR-<sequence>: <제목>

**Date**: YYYY-MM-DD
**Status**: Accepted
**Deciders**: 사용자 (연구자), 디렉터

## Context
[배경]

## Decision
[채택된 옵션]

## Consequences
### Positive
- ...
### Negative
- ...
### Neutral
- ...

## Alternatives considered
- 옵션 A: [왜 거절]
- 옵션 B: [왜 거절]

## Related files
- [변경될 코드/데이터/문서 경로]
```

## Arguments

$ARGUMENTS
