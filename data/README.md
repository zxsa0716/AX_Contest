# Data Directory — 데이터 관리 규칙

**이 폴더의 실제 데이터 파일은 git에 커밋하지 않는다.** 출처·수집일자·SHA-256만 기록.

## 폴더 구조

```
data/
├── raw/          # 원본 다운로드 (절대 수정 금지)
│   ├── gir_manifest/       # GIR 관리업체 명세서 (연도별)
│   ├── gir_allocated/      # GIR 할당대상업체 지정현황
│   ├── gir_target/         # GIR 목표관리대상업체 현황
│   ├── kets_allocation/    # K-ETS 사전할당량 3차 계획기간
│   ├── nir/                # 국가 온실가스 인벤토리
│   ├── gir_verifier/       # 온실가스 검증기관 지정현황
│   ├── integrated_permit/  # 통합환경허가 사업장 정보공개
│   ├── air_emission/       # 사업장 대기오염물질 측정값
│   ├── energy_diagnosis/   # 한국에너지공단 에너지진단통계
│   └── download_log.json   # 모든 다운로드 시도 기록 (자동 생성)
├── interim/      # 중간 전처리 결과
│   ├── kospi200_YYYY.csv         # KRX KOSPI200 구성종목 (연도별)
│   ├── kospi200_industry.csv     # KRX 업종분류 스냅샷
│   ├── kau_daily_2019_2023.csv   # KAU 일별 시세
│   ├── kau_annual.csv            # KAU 연도별 평균
│   ├── kcgs_esg_grades.csv       # KCGS ESG 등급
│   └── failures_<dataset>.csv    # 수집 실패 기록 (자동 생성)
└── processed/    # 최종 분석 패널
```

## 수집 상태 범례

| 상태 | 의미 |
|------|------|
| ✅ 완료 | 파일 존재, SHA-256 기록 |
| 🔧 수동필요 | 브라우저 직접 다운로드 필요 (URL 제공) |
| ⛔ 차단됨 | 기술적 차단 확인 (사유 기재) |
| ⏳ 대기중 | Tier 2 착수 전 |

---

## 데이터 출처 인벤토리 — Tier 1 (ADR-002 확정)

### GIR 공공데이터 (data.go.kr)

| ADR ID | 이름 | 데이터셋 ID | 출처 URL | 수집일 | 파일 경로 | SHA-256 | 인코딩 | 상태 | 담당 |
|--------|------|------------|----------|--------|-----------|---------|--------|------|------|
| 1 / A | GIR 관리업체 명세서 2019 | 15053947 | [링크](https://www.data.go.kr/data/15053947/fileData.do) | — | `data/raw/gir_manifest/2019.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 1 / A | GIR 관리업체 명세서 2020 | 15053947 | [링크](https://www.data.go.kr/data/15053947/fileData.do) | — | `data/raw/gir_manifest/2020.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 1 / A | GIR 관리업체 명세서 2021 | 15053947 | [링크](https://www.data.go.kr/data/15053947/fileData.do) | — | `data/raw/gir_manifest/2021.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 1 / A | GIR 관리업체 명세서 2022 | 15053947 | [링크](https://www.data.go.kr/data/15053947/fileData.do) | — | `data/raw/gir_manifest/2022.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 1 / A | GIR 관리업체 명세서 2023 | 15053947 | [링크](https://www.data.go.kr/data/15053947/fileData.do) | — | `data/raw/gir_manifest/2023.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 2 / A-2 | GIR 할당대상업체 2019 | 15053949 | [링크](https://www.data.go.kr/data/15053949/fileData.do) | — | `data/raw/gir_allocated/2019.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 2 / A-2 | GIR 할당대상업체 2020 | 15053949 | [링크](https://www.data.go.kr/data/15053949/fileData.do) | — | `data/raw/gir_allocated/2020.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 2 / A-2 | GIR 할당대상업체 2021 | 15053949 | [링크](https://www.data.go.kr/data/15053949/fileData.do) | — | `data/raw/gir_allocated/2021.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 2 / A-2 | GIR 할당대상업체 2022 | 15053949 | [링크](https://www.data.go.kr/data/15053949/fileData.do) | — | `data/raw/gir_allocated/2022.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 2 / A-2 | GIR 할당대상업체 2023 | 15053949 | [링크](https://www.data.go.kr/data/15053949/fileData.do) | — | `data/raw/gir_allocated/2023.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| A-3 | GIR 목표관리대상업체 2019~2023 | 15053948 | [링크](https://www.data.go.kr/data/15053948/fileData.do) | — | `data/raw/gir_target/YYYY.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 3 | K-ETS 사전할당량 3차 계획기간 | 15126853 | [링크](https://www.data.go.kr/data/15126853/fileData.do) | — | `data/raw/kets_allocation/kets_allocation_3rd.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| NIR | 국가 온실가스 인벤토리 | 15049589 | [링크](https://www.data.go.kr/data/15049589/fileData.do) | — | `data/raw/nir/nir_latest.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| 4 | 온실가스 검증기관 지정현황 | 15082976 | [링크](https://www.data.go.kr/data/15082976/fileData.do) | — | `data/raw/gir_verifier/gir_verifier.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| T2-1 | 통합환경허가 사업장 정보공개 | 15123597 | [링크](https://www.data.go.kr/data/15123597/fileData.do) | — | `data/raw/integrated_permit/integrated_permit.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| T2-2 | 사업장 대기오염물질 측정값 | 15122803 | [링크](https://www.data.go.kr/data/15122803/fileData.do) | — | `data/raw/air_emission/air_emission.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |
| T2-3 | 한국에너지공단 에너지진단통계 | 15044902 | [링크](https://www.data.go.kr/data/15044902/fileData.do) | — | `data/raw/energy_diagnosis/energy_diagnosis.csv` | — | cp949 | 🔧 수동필요 | corp-data-manager |

> **자동화 차단 사유**: DATA_GO_KR_KEY 환경변수 미설정. 발급 URL: https://www.data.go.kr/ugs/selectPublicDataUseGuideView.do
> 키 발급 후 `DATA_GO_KR_KEY=<키값>` .env에 추가하면 `download_data_go_kr.py`가 자동 시도함.
> 단, data.go.kr fileData 데이터셋은 API 키 없이도 브라우저에서 직접 다운로드 가능.

---

### KRX 시장 데이터

| ADR ID | 이름 | 출처 URL | 수집일 | 파일 경로 | SHA-256 | 상태 | 담당 | 비고 |
|--------|------|----------|--------|-----------|---------|------|------|------|
| 6 | KOSPI200 구성종목 2019 | [KRX](https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd) | — | `data/interim/kospi200_2019.csv` | — | ⛔ 차단됨 | corp-data-manager | KRX 로그인 필요 (2026-04-17 확인) |
| 6 | KOSPI200 구성종목 2020 | [KRX](https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd) | — | `data/interim/kospi200_2020.csv` | — | ⛔ 차단됨 | corp-data-manager | 상동 |
| 6 | KOSPI200 구성종목 2021 | [KRX](https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd) | — | `data/interim/kospi200_2021.csv` | — | ⛔ 차단됨 | corp-data-manager | 상동 |
| 6 | KOSPI200 구성종목 2022 | [KRX](https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd) | — | `data/interim/kospi200_2022.csv` | — | ⛔ 차단됨 | corp-data-manager | 상동 |
| 6 | KOSPI200 구성종목 2023 | [KRX](https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT00301.cmd) | — | `data/interim/kospi200_2023.csv` | — | ⛔ 차단됨 | corp-data-manager | 상동 |
| 6 | KRX 업종분류 스냅샷 | [KRX](https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT03901.cmd) | — | `data/interim/kospi200_industry.csv` | — | ⛔ 차단됨 | corp-data-manager | KRX 로그인 필요 |
| 7 | KAU 일별 시세 2019~2023 | [ETS](https://ets.krx.co.kr/contents/ETS/03/03010000/ETS03010000.jsp) | — | `data/interim/kau_daily_2019_2023.csv` | — | ⛔ 차단됨 | corp-data-manager | ETS OTP endpoint 404 (2026-04-17) |
| 7 | KAU 연도별 평균 | 상동 | — | `data/interim/kau_annual.csv` | — | ⛔ 차단됨 | corp-data-manager | kau_daily 수집 후 자동 생성 |

> **KRX 차단 우회 방법**:
> 1. KRX 정보데이터시스템 회원가입 → https://data.krx.co.kr 에서 로그인 후 수동 CSV 다운로드.
> 2. 또는 KRX OpenAPI (openapi.krx.co.kr) 별도 API 키 신청.
> 3. KAU 가격 대안: k-re100.or.kr/doc/sub2_4_1.php 또는 환경부 K-ETS 통계 연보 PDF.

---

### KCGS ESG 등급

| ADR ID | 이름 | 출처 URL | 수집일 | 파일 경로 | SHA-256 | 상태 | 담당 | 비고 |
|--------|------|----------|--------|-----------|---------|------|------|------|
| 16 | KCGS ESG 등급 2019~2023 | [KCGS](https://www.cgs.or.kr/business/esg_tab04.jsp) | — | `data/interim/kcgs_esg_grades.csv` | — | ⛔ 차단됨 | corp-data-manager | JS consent gate (2026-04-17 확인) |

> **KCGS 차단 우회 방법**:
> 1. Selenium + headless Chrome으로 consent 클릭 후 페이지 데이터 추출.
> 2. KCGS 연간 보도자료 PDF (https://www.cgs.or.kr/news/press_list.jsp) 파싱.
> 3. esgdata@cgs.or.kr 에 연구목적 데이터 요청 (공식 경로).

---

### ESG 자체보고 데이터

| ADR ID | 이름 | 출처 URL | 수집일 | 파일 경로 | SHA-256 | 상태 | 담당 |
|--------|------|----------|--------|-----------|---------|------|------|
| 9 / B | KRX ESG 보고서 목록 | [KRX ESG](https://esg.krx.co.kr) | — | — | — | ⏳ 대기중 | corp-data-manager |
| 9 / B | 지속가능경영보고서 PDF | [DART](https://dart.fss.or.kr) | — | — | — | ⏳ 대기중 | corp-data-manager |
| 8 | DART 사업보고서 II.6 (재무) | [DART API](https://opendart.fss.or.kr) | — | — | — | ⏳ 대기중 | corp-data-manager |
| 17 | Assurance letter 메타 | ESG PDF 내부 파싱 | — | — | — | ⏳ 대기중 | corp-data-manager |

---

### 위성·기상 데이터

| ADR ID | 이름 | 출처 | 수집일 | 파일 경로 | SHA-256 | 상태 | 담당 |
|--------|------|------|--------|-----------|---------|------|------|
| 10 / C | Sentinel-5P NO₂ | GEE COPERNICUS/S5P/OFFL/L3_NO2 | — | — | — | ⏳ 대기중 | algo-researcher |
| 10 / C-2 | Sentinel-5P SO₂ | GEE COPERNICUS/S5P/OFFL/L3_SO2 | — | — | — | ⏳ 대기중 | algo-researcher |
| 12 | Sentinel-5P CO | GEE COPERNICUS/S5P/OFFL/L3_CO | — | — | — | ⏳ 대기중 | algo-researcher |
| 13 | Sentinel-5P HCHO | GEE COPERNICUS/S5P/OFFL/L3_HCHO | — | — | — | ⏳ 대기중 | algo-researcher |
| 11 / D | ERA5 기상 | GEE ECMWF/ERA5_LAND/HOURLY | — | — | — | ⏳ 대기중 | algo-researcher |
| 14 | ODIAC v2024 CO₂ 1km | NIES 포털 | — | — | — | ⏳ 대기중 | algo-researcher |
| 15 | MERRA-2 재분석 | GEE NASA/MERRA-2 | — | — | — | ⏳ 대기중 | algo-researcher |

---

### 기타 공공 데이터

| ADR ID | 이름 | 출처 | 수집일 | 파일 경로 | SHA-256 | 상태 | 담당 |
|--------|------|------|--------|-----------|---------|------|------|
| 5 | 환경부 할당계획 변경공고 | me.go.kr 보도·공고 | — | — | — | ⏳ 대기중 | corp-data-manager |
| T2-KMA | KMA ASOS 지점 관측 | data.kma.go.kr | — | — | — | ⏳ 대기중 | data-analyst |

---

## SHA-256 해시 기록 (다운로드 완료 항목)

아직 완료된 항목 없음. 파일 수동 다운로드 후 아래 명령어로 해시 계산:

```bash
python -c "import hashlib; print(hashlib.sha256(open('경로', 'rb').read()).hexdigest())"
```

---

## 규칙

1. `raw/` 파일은 다운로드 후 **절대 수정 금지**. 전처리는 반드시 `interim/` 또는 `processed/`로.
2. 다운로드 직후 SHA-256 해시 계산 후 이 표에 기록.
3. 공공데이터 이용약관 준수 (재배포 금지 등).
4. 개인정보 포함 가능한 필드는 `interim/`에서 즉시 마스킹.
5. `download_log.json`은 모든 시도를 기록 — 성공/실패/수동필요 전부.
6. GIR 데이터는 인코딩 cp949. 로드 시 반드시 `pd.read_csv(..., encoding='cp949')`.
7. 사업자등록번호는 digit-only 정규화 후 매칭 키로 사용.
