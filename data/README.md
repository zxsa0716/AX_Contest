# Data Directory — 데이터 관리 규칙

**이 폴더의 실제 데이터 파일은 git에 커밋하지 않는다.** 출처·수집일자·SHA-256만 기록.

## 경로 주의사항 (Wave 2 업데이트)

사용자가 직접 다운로드한 원본 파일은 `data/raw/` 하위가 아닌 아래 비표준 경로에 있다.
derived parquet은 정상적으로 `data/interim/`에 저장된다.

| 원본 경로 | 내용 |
|---|---|
| `data/GIR명세서/` | GIR 명세서 xls 7개년 (2018-2024) |
| `data/GIR할당대상/` | GIR 할당대상 xlsx 4개 스냅샷 |
| `data/GIR목표관리/` | GIR 목표관리업체 xlsx 1개 |
| `data/GIR검증기관/` | GIR 검증기관 xlsx 1개 |
| `data/사전할당/` | K-ETS 사전할당 1~4차 CSV |
| `data/NIR인벤토리/` | 국가 온실가스 인벤토리 CSV |
| `data/통합환경허가/` | 통합환경허가 사업장 CSV |

## 폴더 구조

```
data/
├── GIR명세서/        # 원본 xls 7개년 (사용자 다운로드 경로)
├── GIR할당대상/      # 원본 xlsx 4개 (사용자 다운로드 경로)
├── GIR목표관리/      # 원본 xlsx 1개 (사용자 다운로드 경로)
├── GIR검증기관/      # 원본 xlsx 1개 (사용자 다운로드 경로)
├── 사전할당/         # K-ETS CSV 4개 (사용자 다운로드 경로)
├── NIR인벤토리/      # NIR CSV 1개 (사용자 다운로드 경로)
├── 통합환경허가/     # 통합환경허가 CSV 1개 (사용자 다운로드 경로)
├── interim/          # 중간 전처리 결과 (derive_kssb_pool 등 parquet)
│   ├── gir_manifest_panel.parquet        # Task 1: GIR 7개년 통합
│   ├── gir_allocated_panel.parquet       # Task 2: 할당대상 4스냅샷 통합 (dedup)
│   ├── gir_target_panel.parquet          # Task 3: 목표관리업체 현황
│   ├── gir_verifier_list.parquet         # Task 4: 검증기관 목록
│   ├── kets_allocation_panel.parquet     # Task 5: K-ETS 1~4차 long 포맷
│   ├── nir_national_panel.parquet        # Task 6: 국가 인벤토리 long 포맷
│   ├── integrated_permit_sites.parquet   # Task 7: 통합환경허가 파싱
│   ├── kssb_2028_candidate_pool.parquet  # Task 8: KSSB 2028 후보군 (DART)
│   ├── kospi_all_corp_index.parquet      # Task 8: KOSPI 전체 법인 인덱스
│   ├── company_master_index.parquet      # Task 9: 통합 기업 매칭 인덱스
│   ├── match_review.csv                  # Task 9: 검토 필요 매칭 (MEDIUM/LOW)
│   ├── failures_integrated_permit.csv    # Task 7: 파싱 실패 기록
│   └── kcgs_esg_grades.csv               # 기존
└── processed/        # 최종 분석 패널
```

## 수집 상태 범례

| 상태 | 의미 |
|------|------|
| ✅ 완료 | 파일 존재, SHA-256 기록 |
| 🔧 수동필요 | 브라우저 직접 다운로드 필요 (URL 제공) |
| ⛔ 차단됨 | 기술적 차단 확인 (사유 기재) |
| ⏳ 대기중 | Tier 2 착수 전 |

---

## SHA-256 해시 기록 — Wave 2 수집 완료 (2026-04-17)

### GIR 명세서 (data/GIR명세서/)

| 파일 | SHA-256 | 행수 | 인코딩 |
|------|---------|------|--------|
| 온실가스 에너지 목표관리 명세서 주요정보_2018년.xls | `7453263e641ed631e0c741c5972a0696522a03306ec501ecc57f6374ac082f19` | ~1,100 | xls binary |
| 온실가스 에너지 목표관리 명세서 주요정보_2019년.xls | `857987d2087a9619037da7f03f5b0151ed18ad86399faed579062aeb4f4a942a` | ~1,100 | xls binary |
| 온실가스 에너지 목표관리 명세서 주요정보_2020년.xls | `4e93111374192d357189fab8c36905135b9d4fae7c4e05019b770054a6a8178a` | ~1,100 | xls binary |
| 온실가스 에너지 목표관리 명세서 주요정보_2021년.xls | `5b9ff6825e39e951c49423f885228234302b1c3a863a359897918fea763f5646` | ~1,100 | xls binary |
| 온실가스 에너지 목표관리 명세서 주요정보_2022년.xls | `2a812e4c7736e80b05c1c07ebdcb813b3f7b1bf01de5c82f1b6d0ad21fb90797` | ~1,100 | xls binary |
| 온실가스 에너지 목표관리 명세서 주요정보_2023년.xls | `7bb8a5a3eb3e19281e00145f9c54ee08400765cac7960d9600f00e739b802b9d` | ~1,200 | xls binary |
| 온실가스 에너지 목표관리 명세서 주요정보_2024년.xls | `6240c797fece3cc3512c4115e08415e05a99bbd47b171928233abd5fa6bea74d` | ~1,100 | xls binary |

**Concat 결과**: `data/interim/gir_manifest_panel.parquet` — 7,998행 / 1,585개 고유 법인명 / 전 행 검증기관 비고 있음

### GIR 할당대상 (data/GIR할당대상/)

| 파일 | SHA-256 | K-ETS 계획기간 |
|------|---------|---------------|
| 할당대상업체현황_20260420223117.xlsx | `1931234fc36aedb14d618bf393df4414bf3445cc5407096718852b54da99be05` | 4차 (2025) |
| 할당대상업체현황_20260420223129.xlsx | `66b2206c3eca272ec84f25b745e26e18871c16e05831ae4443a1ce00e2ca4892` | 3차 (2020) |
| 할당대상업체현황_20260420223137.xlsx | `4a802a5b99883c9917238264a215a61a599a4041a32f4f3242c16d2488ebfec4` | 2차 (2017) |
| 할당대상업체현황_20260420223141.xlsx | `94e60648eaceb77fc071c19847da51b71362be19f751dd842b54affa2945e9a2` | 1차 (2014) |

**Concat 결과**: `data/interim/gir_allocated_panel.parquet` — 2,933행 원본 / 992행 dedup (업체명_normalized 기준)

### GIR 목표관리 (data/GIR목표관리/)

| 파일 | SHA-256 | 행수 |
|------|---------|------|
| 목표관리업체현황_20260420223247.xlsx | `79345292591be1ced05f5e8a0768c9ddf7c553c2cd7feb44ab384dc9ced95c62` | 4,308 |

**파싱 결과**: `data/interim/gir_target_panel.parquet` — 4,308행

### GIR 검증기관 (data/GIR검증기관/)

| 파일 | SHA-256 | 기관수 |
|------|---------|--------|
| 20250106 온실가스 검증기관 지정현황.xlsx | `79a53ed5521fc7f00398ae5e789531dc29b46a294b656fc1ee81494a766d6a86` | 13 |

**파싱 결과**: `data/interim/gir_verifier_list.parquet` — 13개 인증기관

### K-ETS 사전할당 (data/사전할당/)

| 파일 | SHA-256 | 인코딩 | 비고 |
|------|---------|--------|------|
| 1차_사전할당_20260420225108.csv | `c1b72201bfcda8d9b3646f3aa56cf69bf9ceea37f1b83b74384eb93ccb01d462` | cp949 | 연도: 2015-2017, 업종 없음 |
| 2차_사전할당_20260420225101.csv | `a6c84c566160ec385fc0b3a79bbf43c068156b248e7baf15d14812317ab2262d` | cp949 | 연도: 2018-2020 |
| 3차_사전할당_20260420225025.csv | `40ddb46c0eb3cf291d93347c03bd2e9558f3f3bc7cb0793d06f9a6fade3a221c` | cp949 | 연도: 2021-2025 |
| 4차_사전할당_20260420224738.csv | `e88a1b9786c91dc6702b0172c64ab421602db617904d8cee04cd9050a65457d0` | cp949 | 연도: 2026-2030, 지정기준 추가 |

**Concat 결과**: `data/interim/kets_allocation_panel.parquet` — 12,009행 long 포맷 / 1,105개 고유 업체

### NIR 국가 인벤토리 (data/NIR인벤토리/)

| 파일 | SHA-256 | 인코딩 | 기간 |
|------|---------|--------|------|
| 기후에너지환경부 온실가스종합정보센터_국가 온실가스 인벤토리 배출량_20251229.csv | `6bce856349a9b7295b29cbe99e5f0eb398dee4d6adc8cbd3cdde5245c690f9e3` | utf-8-sig | 1990-2023 |

**파싱 결과**: `data/interim/nir_national_panel.parquet` — 5,508행 long 포맷 / 161개 분야 / 단위: kt CO₂-eq

### 통합환경허가 (data/통합환경허가/)

| 파일 | SHA-256 | 인코딩 | 행수 |
|------|---------|--------|------|
| 기후에너지환경부 국립환경과학원_통합환경허가사업장 정보공개_20240923.csv | `bf8cdb8660d05c1ff3ff0741209bc39107f02fb98c5efc23187a078a95822f54` | cp949 | 1,065 |

**파싱 결과**: `data/interim/integrated_permit_sites.parquet` — 1,065행 / 782개 기업명·주소 추출 성공 / 283개 파싱 실패 기록 (`failures_integrated_permit.csv`)

---

## DART Task 8 — KSSB 2028 풀 (진행중)

`src/preprocessing/derive_kssb_pool.py` 실행 중 (백그라운드, ~60분 소요).
완료 후 아래 파일 생성됨:
- `data/interim/kssb_2028_candidate_pool.parquet` — 자산 2조+ KOSPI 기업
- `data/interim/kospi_all_corp_index.parquet` — KOSPI 전체 법인 인덱스
- `data/interim/company_master_index.parquet` — DART 매칭 포함 재실행 필요

### Task 9 재실행 필요

Task 8 완료 후 `src/preprocessing/build_master_index.py`를 재실행하면
DART corp_code/stock_code/bizr_no 매칭이 GIR 1,585개 법인에 적용된다.

---

## 데이터셋별 주요 스키마 노트

### GIR 명세서 → gir_manifest_panel.parquet

모든 연도(2018-2024) 동일 스키마. 컬럼명 연도간 변동 없음.
- `scope1_tco2eq`: 사업장 단위 Scope 1 직접 배출량 (tCO₂eq). 단위 주의: 사업장 level이므로 법인 집계 시 `사업자등록번호` 기준 groupby 필요.
- `지정구분`: "사업장" vs "업체" — 집계 단위 다름, 분석 시 구분 필요.
- `검증수행기관`: 전 행 비고 있음 (7,997/7,998). 단, 일부는 공란 문자열일 수 있음.

### K-ETS 사전할당 → kets_allocation_panel.parquet

- Phase 1은 `업종` 없음, `유상여부` 없음 (전부 무상).
- Phase 4는 `지정기준` 추가 (사업장기준/업체기준).
- `allocation_tco2eq` 단위: tCO₂eq (원본 숫자 그대로, 쉼표 제거 후 float 변환).
- Heckman 도구변수로 사용 시 연도별 할당량과 실배출량 gap 계산에 활용.

### NIR 국가 인벤토리 → nir_national_panel.parquet

- 단위: **kt CO₂-eq** (not tCO₂eq). 변환 필요 시 × 1,000.
- `분야 및 연도` 컬럼이 분야명. 총배출량/순배출량/에너지/산업공정 등 162개 행.
- 분석 목적: 기업 배출량의 국가 총량 대비 비중 계산, 거시 트렌드 비교.

---

## 수집 예정 / 차단 항목

### KRX 시장 데이터 (⛔ 차단)

| 이름 | 상태 | 우회 방법 |
|------|------|-----------|
| KOSPI200 구성종목 2019-2023 | ⛔ 차단 | KRX 로그인 후 수동 다운로드 |
| KRX 업종분류 스냅샷 | ⛔ 차단 | 상동 |
| KAU 일별 시세 2019-2023 | ⛔ 차단 | ETS OTP endpoint 404 |

### ESG / 위성 / 기상 (⏳ 대기중)

| 이름 | 담당 | 상태 |
|------|------|------|
| KRX ESG 보고서 + GRI 305-1 | corp-data-manager | ⏳ |
| DART 사업보고서 II.6 | corp-data-manager | ⏳ |
| Sentinel-5P NO₂/SO₂/CO/HCHO | algo-researcher | ⏳ |
| ERA5 기상 | algo-researcher | ⏳ |
| ODIAC v2024 CO₂ | algo-researcher | ⏳ |
| KCGS ESG 등급 | corp-data-manager | ⛔ JS consent gate |

---

## 규칙

1. `raw/` 및 비표준 경로 파일은 다운로드 후 **절대 수정 금지**. 전처리는 반드시 `interim/` 또는 `processed/`로.
2. 다운로드 직후 SHA-256 해시 계산 후 이 표에 기록.
3. 공공데이터 이용약관 준수 (재배포 금지 등).
4. 개인정보 포함 가능한 필드는 `interim/`에서 즉시 마스킹.
5. GIR 데이터는 xls/xlsx 바이너리 포맷 (csv 아님). `pd.read_excel()`로 로드.
6. K-ETS CSV는 인코딩 cp949. 로드 시 반드시 `pd.read_csv(..., encoding='cp949')`.
7. NIR CSV는 utf-8-sig.
8. 사업자등록번호는 digit-only 정규화 후 매칭 키로 사용.
