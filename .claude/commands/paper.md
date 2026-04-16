---
description: Quick literature search via algo-researcher — find recent papers on a specific topic.
argument-hint: <search keywords>
---

# /paper — Quick literature lookup

algo-researcher 또는 esg-expert 를 경량 호출해서 최신 논문을 빠르게 찾는 단축 커맨드.

## 사용법

```
/paper <keywords>
```

## Director behavior

1. Parse keywords from `$ARGUMENTS`.
2. Decide domain:
   - Satellite, remote sensing, anomaly detection, GEE → `algo-researcher`
   - ESG methodology, GHG accounting, organizational boundary → `esg-expert`
   - Policy, regulation, disclosure → `policy-expert`
   - If ambiguous, default to `algo-researcher`
3. Craft a **short** English prompt asking for:
   - Top 5 recent (last 24 months preferred) papers
   - For each: title, authors, venue, year, 1-line key finding, URL
   - Recommend which 1–2 are most relevant to cite in this project
4. Keep the subagent prompt **terse** — this is a quick lookup, not a deep scan.
5. Return to user in Korean:

```
## 📚 논문 검색 결과: [keywords]

1. **[Title]** (Authors, Year, Venue)
   - 핵심: [1 line]
   - URL: ...
   
2. ...

### 인용 추천
- 우리 연구에 가장 가까운 것: [#N] — 이유
- 방법론 비교용: [#M]
```

6. If no good results, say so explicitly and suggest broader keywords.

## When NOT to use

- For deep methodological scans → use `/consult algo` instead (full agent deep dive)
- For policy timeline lookups → use `/consult policy`

## Arguments

$ARGUMENTS
