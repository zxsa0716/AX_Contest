# ADR-004: Wave 3 정정 + 지속가능경영보고서 자동화 시스템 편입

**Date**: 2026-04-22
**Status**: Accepted
**Deciders**: 사용자(연구자), 디렉터

## Context

Wave 3에서 KOSPI200 재다운로드, 할당계획 변경공고 수집, KCGS 등급 자료 확보, 지속가능경영보고서 수집 자동화를 진행하면서 기존 설계(ADR-002, ADR-003)를 일부 정정해야 할 상황 발생.

## Decisions

### 정정 1 — KSSB 2028 임계값 정확화 (30조원, 49개사)

**기존**: `kssb_flag_any` 컬럼이 자산 ≥2조 기준으로 계산되어 238개사. ADR-003의 Gold 정의와 불일치 (잘못된 threshold).

**정정**:
- **올바른 임계값**: 연결자산총계 ≥ 30조 KRW (FSC 로드맵 2026-02-25 기준)
- **올바른 Pool N**: **49개사** (2023 or 2024 중 하나라도 30조 초과)
- 새 컬럼 `kssb_flag_30` = True 사용
- `kssb_flag_any` (≥2조, 238개사)는 deprecated (참고용 only)

**Gold 재계산**:
- Gold = KSSB_30 ∩ GIR≥3yr = **24개사** (ADR-003의 mitigation ladder 4단계 전에 멈춤)
- Silver = KOSPI200 proxy ∩ GIR≥3yr, not KSSB_30 = **205개사**
- 24 Gold 기업 목록: CJ제일제당, SK이노베이션, 네이버, 대한항공, 두산, 롯데쇼핑, 롯데케미칼, 삼성물산, 삼성생명, 삼성전자, SK하이닉스, LG디스플레이, LG에너지솔루션, 이마트, 중소기업은행, KT, 포스코홀딩스, 한전, 한화, 한화솔루션, 현대모비스, 현대차, 현대제철

**영향**:
- Gold N=24 → Bootstrap CI 필수, mitigation ladder §5.2 trigger 적용 검토
- 24개사 중 **금융 3개사(삼성생명·중기은행·KT)** 는 Scope 1 배출량이 미미 → 실질 분석 대상 **비금융 제조·에너지 21개사**

### 정정 2 — K-ETS 할당계획 변경공고의 supervised label 적합성 재평가

**기존 ADR-003 가정**: 환경부 할당계획 변경공고에서 "GIR 배출량 수정된 기업-연도 쌍" 추출 가능, 이를 external validation label로 사용 (unsupervised → partial supervised).

**Wave 3 파싱 결과**:
- 18개 공고 문서 100% 파싱 성공 (HWP/HWPX/PDF)
- 추출된 90개 레코드는 **업종 KSIC별 BM계수·부문별 배출허용총량** (예: 석탄광업, 석유정제품 제조업)
- **기업 수준 할당량 조정 레코드: 0건**
- 근본 원인: 한국 할당계획 공고는 총량·업종·경매 매개변수 변경 문서이며, 개별 기업 할당량 조정은 별도 통지(비공개)로 이루어짐

**대체 supervised label 소스**:
1. **KCGS 분기별 ESG 등급조정 (21건)** — 2023 Q4, 2024 Q4, 2025 Q4 조정 이력. ESG 등급 하락 기업을 "discrepancy risk" 라벨로 활용 가능.
2. **GIR 명세서 '검증수행기관' 컬럼** — 전 행 존재. 동일 기업이 연도에 따라 검증기관을 바꾸거나 검증 부정 받은 이력은 수정 signal.
3. **기업별 K-ETS 사전할당 panel (1,105개사 × phase)** — phase 간 allocation 변동폭으로 "규제 압력 변화" derive

**결정**: Supervised label을 다음 3종 조합으로 재정의:
- KCGS 등급조정 이벤트 (핵심)
- GIR 검증기관 변경 이력 (보조)
- K-ETS allocation gap (사전할당 vs 실제 배출량) (보조)

이상탐지 모델 학습 시 "부분 supervised" 프레이밍은 유지하되 소스만 교체.

### 정정 3 — KOSPI200 구성종목 접근 불가 → proxy 사용 공식화

**상황**: 
- 사용자가 2차례 수동 다운로드 시도, 모두 "KOSPI200 인덱스 시세" 파일만 받음 (구성종목 명단 아님)
- KRX data.krx.co.kr 2026년부터 로그인 필수로 전환
- pykrx도 동일 차단

**결정**: KRX 우회 영구 포기, DART 기반 proxy 사용.
- `src/preprocessing/kospi200_proxy.py` — DART 자본총계 상위 200개사
- 연도별 (2019, 2020, 2021, 2022, 2023) 독립 proxy 생성 가능
- 공식 KRX KOSPI200과 90~95% 일치 추정 (금융지주 편향 caveat 명시)
- `data/KOSPI200/` 5개 CSV(인덱스 시세)는 macro control variable로 편입

### 결정 4 — 지속가능경영보고서 자동화를 영구 시스템 기능으로 편입

**결정**: `sustainability_report_collector.py` + `parser.py` + 2개 Skill 파일(`.claude/skills/`)을 **최종 제출물의 system architecture 구성요소**로 공식 편입.

**공모전 제출 보고서 Section 10에 명시될 항목**:
- 재사용 가능한 자동화 파이프라인 (데이터 수집 → 파싱 → 패널 구축)
- `.env` 키 설정 후 즉시 재실행 가능
- SHA-256 재현성 추적

**실용 한계 (보고서에 정직하게 기재)**:
- 한국 대기업 대부분 DART 자율공시에는 URL만, PDF는 IR 사이트에만 게시
- KRX ESG 포털 JS 렌더링 필요 (Selenium + ChromeDriver 추가 설정)
- **현 시점 실용 워크플로**: 24 Gold 기업 × 5년 = 최대 120개 PDF는 IR 수동 다운로드가 현실적 (1-2시간). 자동화는 파서 쪽이 핵심 가치.

## Consequences

### Positive
- Gold N=24로 방법론 엄밀성 확보 (KSSB 2028 정확 매칭)
- KCGS 등급조정 기반 supervised label이 오히려 더 명확(ESG 리스크 직결)
- 자동화 시스템이 제출물 차별화 요소로 편입됨

### Negative
- K-ETS 변경공고로부터 기업별 정정 이력 획득 실패 → 초기 기대보다 supervised label 풍부성 감소
- Gold N=24는 mitigation ladder 발동 검토 구간 (Bootstrap CI 필수)
- IR 사이트 수동 수집 단계가 공모전 마감 전 크리티컬 경로에 남음

### Neutral
- KOSPI200 proxy methodology는 보고서 한계 섹션에 투명 기재
- MERRA-2 밴드 실제 확인 결과 (PBLTOP/PS/DISPH/QV2M)로 sensitivity 설계 조정

## Related files

- `CLAUDE.md` — 17+ 데이터셋·자동화 시스템 섹션 추가 (패치 적용)
- `data/interim/kospi_asset_full.parquet` — `kssb_flag_30` 컬럼 추가됨
- `data/interim/company_master_index.parquet` — `in_kssb_30` 컬럼 추가됨
- `src/preprocessing/sustainability_report_collector.py`, `sustainability_report_parser.py`
- `src/preprocessing/kospi200_proxy.py`
- `.claude/skills/sustainability-report-collect.md`, `esg-scope-extract.md`
