# Data Directory — 데이터 관리 규칙

**이 폴더의 실제 데이터 파일은 git에 커밋하지 않는다.** 출처·수집일자·SHA-256만 기록.

## 폴더 구조

```
data/
├── raw/          # 원본 다운로드 (절대 수정 금지)
├── interim/      # 중간 전처리 결과
└── processed/    # 최종 분석 패널
```

## 데이터 출처 인벤토리 (수집 완료 시 업데이트)

| ID | 이름 | 출처 | 수집일 | 파일 | SHA-256 | 담당 |
|----|------|------|--------|------|---------|------|
| A | GIR 관리업체 명세서 2019 | data.go.kr | — | — | — | corp-data-manager |
| A | GIR 관리업체 명세서 2020 | data.go.kr | — | — | — | corp-data-manager |
| A | GIR 관리업체 명세서 2021 | data.go.kr | — | — | — | corp-data-manager |
| A | GIR 관리업체 명세서 2022 | data.go.kr | — | — | — | corp-data-manager |
| A | GIR 관리업체 명세서 2023 | data.go.kr | — | — | — | corp-data-manager |
| A-2 | GIR 할당대상업체 지정현황 | data.go.kr | — | — | — | corp-data-manager |
| B | KRX ESG 보고서 목록 | esg.krx.co.kr | — | — | — | corp-data-manager |
| B | 지속가능경영보고서 PDF | DART | — | — | — | corp-data-manager |
| C | Sentinel-5P NO₂ | GEE | — | — | — | algo-researcher |
| C-2 | Sentinel-5P SO₂ | GEE | — | — | — | algo-researcher |
| D | DART 재무 | DART Open API | — | — | — | corp-data-manager |
| D | ERA5 기상 | GEE | — | — | — | algo-researcher |

## 규칙

1. `raw/` 파일은 다운로드 후 **절대 수정 금지**. 전처리는 반드시 `interim/` 또는 `processed/`로.
2. 다운로드 직후 SHA-256 해시 계산 후 이 표에 기록.
3. 공공데이터 이용약관 준수 (재배포 금지 등).
4. 개인정보 포함 가능한 필드는 `interim/`에서 즉시 마스킹.
