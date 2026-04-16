# 2026 AX 아이디어 경진대회 — 온실가스 공시 신뢰성 3중 검증

**대회**: 2026 AX 아이디어 경진대회 (기후에너지환경부)  
**마감**: 2026-05-18  
**부문**: 데이터 분석 > 자유과제  
**주제**: 한국 코스피 상장기업의 GIR 법정 배출량 × ESG 자체보고 × Sentinel-5P 위성 NO₂·SO₂ 3중 비교 및 ESG 의무공시 검증체계 설계

## 프로젝트 구조

```
AX_contest/
├── CLAUDE.md              # 디렉터 운영 규칙 + 프로젝트 사실
├── .claude/
│   ├── agents/            # 6개 서브에이전트 명세 (영어)
│   ├── commands/          # 6개 슬래시 커맨드
│   └── settings.json      # 권한·환경변수
├── 참고/                  # 원본 자료 (읽기 전용)
├── data/                  # 수집·전처리 데이터 (git 제외)
├── src/
│   ├── preprocessing/     # corp-data-manager 영역
│   ├── analysis/          # data-analyst 영역
│   ├── satellite/         # algo-researcher 영역
│   └── visualization/     # report-writer 영역
├── notebooks/             # 탐색적 분석
├── figs/                  # 최종 피규어
├── report/                # 제출 문서
├── decisions/             # ADR (의사결정 기록)
├── requirements.txt
├── .env.example           # API 키 템플릿 (.env는 커밋 금지)
└── .gitignore
```

## 시작하기 (연구자 체크리스트)

1. `.env.example` → `.env` 복사 후 API 키 입력
   - Kakao Local API (data.go.kr 주소 지오코딩)
   - DART Open API (재무·공시)
   - GEE 서비스 계정 JSON (Sentinel-5P·ERA5)
2. Python 가상환경 생성 및 `pip install -r requirements.txt`
3. Claude Code에서 `/standup` 으로 현황 확인
4. `/consult data GIR 2019~2023 스키마 정리해줘` 같은 식으로 에이전트 호출

## 6개 슬래시 커맨드

| 커맨드 | 용도 |
|---|---|
| `/consult <agent> <질문>` | 단일 전문가 자문 |
| `/roundtable <주제>` | 관련 에이전트 병렬 자문 |
| `/standup` | 프로젝트 현황 점검 |
| `/handoff <from> <to>` | 에이전트 간 인수인계 기록 |
| `/decision <주제>` | 주요 분기점 사용자 판단 요청 |
| `/paper <keywords>` | 빠른 논문 검색 |

## 에이전트 단축 이름

`policy` · `data` · `esg` · `analyst` · `algo` · `report`
