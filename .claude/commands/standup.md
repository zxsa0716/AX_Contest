---
description: Daily status check — scan project state and report what's done, blocked, and next.
---

# /standup — Project state audit

프로젝트 전체 현황을 빠르게 점검.

## Director behavior

1. **Read silently** (no agent calls needed):
   - `git log --oneline -20` — recent commits
   - `git status` — uncommitted changes
   - `data/README.md` — data inventory table
   - `decisions/` folder — list of ADRs
   - `src/` subfolder contents
   - `figs/` folder contents
   - `report/` folder contents

2. **Produce a Korean standup report** structured as:

```
## 🗓 오늘 현황 (YYYY-MM-DD)

### ✅ 완료된 것
- [항목 + 커밋 해시 또는 산출물 경로]

### 🔄 진행 중
- [파일 수정 중인 작업]

### 🚧 블로커
- [해결 필요한 것 — 데이터 미도착, API 키 미발급, 결정 미정 등]

### 📅 남은 시간
- 마감 5/18까지 D-[숫자]일
- 이번 주 목표: [한 문장]

### ➡️ 다음 단계 제안 (3개)
1. [구체적 action, 담당 agent 명시]
2. …
3. …
```

3. **Do not invoke subagents** for this command — it's a silent scan + report. Standup should be fast.

4. If anything critical is missing (e.g., no data yet but we're in week 3), flag explicitly.

## Frequency

당신이 매일 오전 1회 호출 권장. 주 중반 블로커 조기 발견용.
