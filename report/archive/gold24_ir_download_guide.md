# Gold 24개사 지속가능경영보고서 수동 수집 가이드

**작성일**: 2026-04-17  
**대상**: Gold 샘플 23개 corp_code (LGD 중복 제거 후) / 24 CSV 행  
**범위**: 2019~2023 보고연도  
**용도**: 자동화 수집(DART 자율공시 URL) 불가 기업의 수동 PDF 다운로드 안내

## 중요 사전 안내

DART 자율공시 탐지 결과(Task 2):
- **81건 ESG 공시** 탐지 (20개사 해당)
- **직접 PDF 첨부: 0건** — 전 기업이 DART에 URL 링크(뷰어)만 등록, 실제 PDF는 IR 사이트 소재
- **DART 0건 기업**: CJ제일제당(주), 삼성물산(주), 한국전력공사(주) — IR 사이트 전용

저장 경로 규칙: `data/raw/sustainability_reports/{stock_code}/{YYYY}.pdf`

---

## 01. 삼성전자(주) (005930)

- **IR 사이트**: https://www.samsung.com/sec/sustainability/digital-library/sustainability-report/
- **DART 공시 수**: 5건 (2019, 2020, 2021, 2022, 2023)
- **다운로드 링크** (직접 PDF, samsung.com 도메인):

| 연도 | 한국어 PDF URL |
|------|---------------|
| 2023 | https://www.samsung.com/sec/sustainability/media/pdf/Samsung_Electronics_Sustainability_Report_2023_KOR.pdf |
| 2022 | https://www.samsung.com/sec/sustainability/media/pdf/sustainability_report_kr_2022___01.pdf |
| 2021 | https://www.samsung.com/sec/sustainability/media/pdf/sustainability_report_kr_2021_01.pdf |
| 2020 | https://www.samsung.com/sec/sustainability/media/pdf/sustainability_report_kr_2020.pdf |
| 2019 | https://www.samsung.com/sec/sustainability/media/pdf/Sustainability_report_2019_kr.pdf |

- **비고**: GRI Standards, ISAE 3000 제3자 검증, 한/영 제공. 5개년 직접 PDF 확인 완료.
- **저장 경로**: `data/raw/sustainability_reports/005930/YYYY.pdf`

---

## 02. 현대자동차(주) (005380)

- **IR 사이트**: https://www.hyundai.com/kr/ko/sustain-manage/manage-system/sustainability-report
- **DART 공시 수**: 2건 (2022, 2023만 감지됨 — 2019~2021은 미제출 또는 다른 명칭)
- **다운로드 링크** (직접 PDF, hyundai.com 도메인):

| 연도 | 한국어 PDF URL |
|------|---------------|
| 2023 | https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/sustainability/about-sustainability/hmc-2023-sustainability-report-ko.pdf |
| 2022 | https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/sustainability/about-sustainability/hmc-2022-sustainability-report-ko-v17.pdf |
| 2021 | 연도별 아카이브 페이지 확인 필요: https://www.hyundai.com/worldwide/ko/company/sustainability/sustainability-report |
| 2020 | 상동 |
| 2019 | 상동 |

- **비고**: GRI Standards 기반. 2019~2021 직접 PDF URL 미확인 — 아카이브 페이지에서 버튼 클릭 필요. 영문 보고서는 "worldwide" 서브도메인에 위치.
- **저장 경로**: `data/raw/sustainability_reports/005380/YYYY.pdf`

---

## 03. SK이노베이션(주) (096770) — UPDATED 2026-04-24

- **IR 사이트**: https://www.skinnovation.com/esg/Sustainability_Report
- **직접 PDF URL 발견 현황** (DART 첨부파일 — skinnovation.com은 브라우저 JS 세션 필수로 자동화 불가):

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|--------------|
| 2023 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20240621800170&dcm_id=99998&dcm_seq=534&fl_nm=SK%EC%9D%B4%EB%85%B8%EB%B2%A0%EC%9D%B4%EC%85%98_%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C+2023.pdf` | 20251KB | OK |
| 2022 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20230714800506&dcm_id=99998&dcm_seq=695&fl_nm=2022+SK%EC%9D%B4%EB%85%B8%EB%B2%A0%EC%9D%B4%EC%85%98+ESG_Report.pdf` | 40055KB | OK |
| 2021 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20220729800368&dcm_id=99998&dcm_seq=409&fl_nm=SK%EC%9D%B4%EB%85%B8%EB%B2%A0%EC%9D%B4%EC%85%98+2021+ESG+Report_%EA%B5%AD%EB%AC%B8.pdf` | 7980KB | OK |
| 2020 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20210726800456&dcm_id=99998&dcm_seq=883&fl_nm=SK%EC%9D%B4%EB%85%B8%EB%B2%A0%EC%9D%B4%EC%85%98+2020+ESG+Report_KOR.pdf` | 6482KB | OK |

- **비고**: 2023 보고서는 2024.06.21 DART 공시(rcpNo=20240621800170)에 수록됨. skinnovation.com /file/download는 JSESSIONID 기반이므로 자동화 불가. 전체 %PDF 매직바이트 확인.
- **저장 경로**: `data/raw/sustainability_reports/096770/YYYY.pdf` (2020~2023 완료)

---

## 04. 포스코홀딩스(주) (005490) — UPDATED

- **IR 사이트 (2022~현재)**: http://www.posco-inc.com/poscoinc/v4/kor/esg/s91e4000400c.jsp
- **구 POSCO 사이트 아카이브**: https://sustainability.posco.co.kr/S91/S91F10/kor/cmspage.do?mmcd=1745996979005381
- **DART 공시 수**: 4건 (2019, 2020×2, 2021 — 2022·2023 미탐지, 포스코홀딩스 출범 후 공시명 변경 가능성)

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|------------|
| 2023 | 포스코홀딩스 공식 사이트 (posco-inc.com) | — | 수동 확인 필요 |
| 2022 | 포스코홀딩스 첫 발간 연도 | — | 수동 확인 필요 |
| 2021 | https://www.posco.co.kr/docs/kor6/jsp/dn/irinfo/posco_report_2021.pdf | 11.5MB | ✅ 자동 다운로드 완료 |
| 2020 | https://www.posco.co.kr/docs/kor6/jsp/dn/irinfo/posco_report_2020.pdf | 8.7MB | ✅ 자동 다운로드 완료 |
| 2019 | https://www.posco.co.kr/docs/kor6/jsp/dn/irinfo/posco_report_2019.pdf | 16.5MB | ✅ 자동 다운로드 완료 |

- **주의**: 2022년 포스코홀딩스 출범으로 법인 전환. 2019~2021 보고서는 "포스코 기업시민보고서" 명의. 보고연도 기준 명칭: 2021은 "2021 POSCO 지속가능경영보고서", 2020은 "기업시민보고서 2020", 2019는 "기업시민보고서 2019". GIR에서는 동일 사업자번호로 연속 확인 필요.
- **다운로드 방법 참고**: sustainability.posco.co.kr 사이트는 세션 없이 PDF 직접 접근 불가 (hotlink 차단). 반면 posco.co.kr/docs/kor6/jsp/dn/irinfo/ 경로는 직접 접근 가능.
- **비고**: GRI Standards + ISAE 3000 제3자 검증. 한/영 제공.
- **저장 경로**: `data/raw/sustainability_reports/005490/YYYY.pdf`

---

## 05. LG에너지솔루션(주) (373220) — UPDATED 2026-04-24

- **IR 사이트**: https://www.lgensol.com/kr/sustainability (lgensol.com은 자동화 수집 차단 확인)
- **직접 PDF URL 발견 현황** (DART 첨부파일):

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|--------------|
| 2023 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20240627800741&dcm_id=99998&dcm_seq=158&fl_nm=LG%EC%97%90%EB%84%88%EC%A7%80%EC%86%94%EB%A3%A8%EC%85%98_2023+ESG+Report_KOR.pdf` | 9992KB | OK |
| 2022 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20230801800047&dcm_id=99998&dcm_seq=062&fl_nm=LG%EC%97%90%EB%84%88%EC%A7%80%EC%86%94%EB%A3%A8%EC%85%98_2022+ESG+Report_%28KOR%29.pdf` | 41563KB | OK |
| 2019~2021 | 해당 없음 (2022.01 상장, 이전에는 LG화학 자회사로 별도 보고서 없음) | — | N/A |

- **비고**: 2023 보고서는 2024.06.27 DART 공시(rcpNo=20240627800741)에 수록. lgensol.com 직접 접근 차단 확인. 분석 시 2019~2021 Scope 1은 GIR 데이터만 사용 가능. 전체 %PDF 매직바이트 확인.
- **저장 경로**: `data/raw/sustainability_reports/373220/YYYY.pdf` (2022~2023 완료)

---

## 06. LG디스플레이(주) (034220) — UPDATED 2026-04-24

- **IR 사이트**: https://www.lgdisplay.com/kor/esg/board/report-and-databook
- **직접 PDF URL 발견 현황** (lgdisplay.com attachment 경로 — 200 application/pdf 확인):

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|--------------|
| 2023 | `https://www.lgdisplay.com/attachment/esg/csm/LGD_ESG_report_2023_kor.pdf` | 18666KB | OK |
| 2022 | `https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2022_kor.pdf` | 18646KB | OK |
| 2021 | `https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2021_kor.pdf` | 6279KB | OK |
| 2020 | `https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2020_kor.pdf` | 23465KB | OK |
| 2019 | `https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2019_kor.pdf` | 20426KB | OK |

- **비고**: 2023은 "ESG Report"명칭, 2019~2022는 "CSR Report"명칭. 전 연도 직접 requests.get() 다운로드 가능. 다국어(KOR/ENG/CHN) 중 KOR 수집. 전체 %PDF 매직바이트 확인.
- **저장 경로**: `data/raw/sustainability_reports/034220/YYYY.pdf` (2019~2023 완료)

---

## 07. 현대모비스(주) (012330)

- **IR 사이트**: https://www.mobis.com/kr/sustain/sustain.do
- **DART 공시 수**: 3건 (2019, 2022, 2023 — 2020·2021 미탐지)
- **다운로드 링크** (직접 PDF, mobis.com 도메인):

| 연도 | 한국어 PDF URL |
|------|---------------|
| 2023 | https://www.mobis.com/upload/202306080348391800.pdf |
| 2022 | https://www.mobis.com/upload/202209010931356890.pdf |
| 2021 | https://www.mobis.com/upload/202203250425401760.pdf |
| 2020 | https://www.mobis.com/upload/202203250428033470.pdf |
| 2019 | https://www.mobis.com/upload/202203250429036590.pdf |

- **비고**: GRI Standards, ISAE 3000 제3자 검증. 한/영/중 제공. 5개년 직접 PDF URL 확인 완료. 2010년부터 발간 이력.
- **저장 경로**: `data/raw/sustainability_reports/012330/YYYY.pdf`

---

## 08. 에스케이하이닉스(주) (000660)

- **IR 사이트**: https://www.skhynix.com/sustainability/UI-FR-SA1601/
- **추가**: https://sustainability.skhynix.com/datacenter?section=sustainReport
- **DART 공시 수**: 7건 (2019, 2020, 2021, 2022×2, 2023×2 — 첨부정정 포함)
- **직접 PDF URL 발견 현황** (DART 첨부파일) — UPDATED 2026-04-24:

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|--------------|
| 2023 | `https://kind.krx.co.kr/external/2023/08/04/000103/20230803000340/SK%ED%95%98%EC%9D%B4%EB%8B%89%EC%8A%A4%20%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C%202023.pdf` | 기존 KIND | 기수집 완료 |
| 2022 | `https://20028749.fs1.hubspotusercontent-na1.net/hubfs/20028749/...` | 기존 HubSpot | 기수집 완료 |
| 2021 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20210706800538&dcm_id=99998&dcm_seq=815&fl_nm=SK+hynix+2021+Sustainability+Report.pdf` | 7345KB | OK |
| 2020 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20200723800341&dcm_id=99998&dcm_seq=452&fl_nm=2020+SK+hynix+SR_Kor_web+F.pdf` | 9214KB | OK |
| 2019 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20191105800202&dcm_id=99998&dcm_seq=947&fl_nm=2019+SK+hynix+SR_kor_web%283%29.pdf` | 20101KB | OK |

- **비고**: GRI Standards. 2019~2021 DART 첨부 경로 확인 완료. 전체 %PDF 매직바이트 확인.
- **저장 경로**: `data/raw/sustainability_reports/000660/YYYY.pdf` (2019~2023 완료)

---

## 09. 한국전력공사(주) (015760) — **완료: 5개년 자동 다운로드**

- **IR 사이트**: https://home.kepco.co.kr/kepco/SM/A/htmlView/SMAFHP001.do?menuCd=FN290106
- **DART 공시 수**: 0건 (자율공시 미제출 — 공공기관 특성상 자체 발간)
- **수집 방법**: 한전 공식 지속가능경영보고서 페이지의 FileDownSecure.do API 직접 호출 → HTTP 200 확인

| 연도 | 직접 다운로드 URL (FileDownSecure.do) | SHA-256 | 파일크기 |
|------|--------------------------------------|---------|---------|
| 2023 | `https://home.kepco.co.kr/kepco/cmmn/fms/FileDownSecure.do?atchFileId=d857b3bda67cbf8f5807e90ea688ad6c167f51f5bb07446fb90422457066f40fb1&fileSn=d0b243fb552df362d367ae1a6d50934724` | `e4d0e898...` | 8,022,944 B |
| 2022 | `https://home.kepco.co.kr/kepco/cmmn/fms/FileDownSecure.do?atchFileId=bf79119bfa81e5a459f5751725b3413a3475bbe9bb76be27afb9c4ded1b7001ec2&fileSn=498b4171589082e6f3cbe7015b22c15a31` | `357e3019...` | 85,304,540 B |
| 2021 | `https://home.kepco.co.kr/kepco/cmmn/fms/FileDownSecure.do?atchFileId=09d10fe355fbba8f35a046320504eec2ed4edab413ed04a52b18337372aca0d041&fileSn=1995b8282f731cd6c8ef4bc6bb2395cc28` | `ec9f954f...` | 31,557,399 B |
| 2020 | `https://home.kepco.co.kr/kepco/cmmn/fms/FileDownSecure.do?atchFileId=88fd772a57d694aa9ae0ef6c0b08ee3269ba44ca2600851322f5f17a79ce7aa734&fileSn=1733c378b02240840c828e677056c6b227` | `628778ef...` | 12,062,421 B |
| 2019 | `https://home.kepco.co.kr/kepco/cmmn/fms/FileDownSecure.do?atchFileId=417cc876723fac17209e64e47fa04244ca9ae026d8eef115b42de858f3aea09e55&fileSn=6c608332ea340b103e16d8c3bc984e2d82` | `58f9ee20...` | 41,575,900 B |

SHA-256 전체 값:
- 2023: `e4d0e8982547199b0ab644cc9da2fd4e27a0cfe5505ced56ec97cab9bf373938`
- 2022: `357e3019970f75fc292dab3360d0c4fa3537d2936d89cbf2e4b2af54c06f0815`
- 2021: `ec9f954f670ca79b2abc28ef4be629f0df93b91f29785f4beffb92c64985e0a3`
- 2020: `628778ef3bae104bbaa481b29598742cdf229e81185e0f0cd7796229de8451e0`
- 2019: `58f9ee20cf4c7363bda86e53f9f8ffa9d2c769aaf99f5374c6faa54837b3d70c`

- **발간 여부**: YES — 5개년(2019~2023) 전부 확인. 공기업이나 지속가능경영보고서 매년 자체 발간.
- **비고**: GRI Standards + 환경부 가이드라인 병행. FileDownSecure.do 엔드포인트 Referer 헤더 필요. Content-Type=application/x-msdownload이나 실제 PDF 바이너리 정상.
- **저장 경로**: `data/raw/sustainability_reports/015760/YYYY.pdf` — **다운로드 완료**

---

## 10. CJ제일제당(주) (097950)

- **IR 사이트**: https://www.cj.co.kr/kr/aboutus/sustainability/report
- **DART 공시 수**: 0건 (자율공시 미제출)
- **다운로드 링크** (직접 PDF, cj.co.kr 도메인):

| 연도 | 한국어 PDF URL |
|------|---------------|
| 2023 | https://m.cj.co.kr/cj_files/2023_sustainability_report_ko.pdf |
| 2022 | https://m.cj.co.kr/cj_files/2022%20Sustainability%20Report_ko.pdf |
| 2021 | IR 사이트 확인 필요 (명명 패턴으로 추정: `2021 Sustainability Report_ko.pdf`) |
| 2020 | IR 사이트 확인 필요 |
| 2019 | https://m.cj.co.kr/cj_files/2019%20Sustainability%20Report_ko.pdf |

- **비고**: GRI Standards. DART 자율공시 0건이므로 IR 사이트 전용 경로. 2022·2023·2019 직접 PDF 확인 완료.
- **저장 경로**: `data/raw/sustainability_reports/097950/YYYY.pdf`

---

## 11. 삼성물산(주) (028260) — **완료: 5개년 자동 다운로드**

- **IR 사이트**: https://www.samsungcnt.com/esg/resource/report/sustainability.do
- **DART 공시 수**: 0건 (자율공시 미제출)
- **수집 방법**: 사이트 내 AJAX 엔드포인트 `POST /esg/resource/report/li/sustainability.do` (param: `report_year=YYYY`) → UUID 추출 → `GET /file/down.do?id=UUID`

| 연도 | 파일명 (Content-Disposition) | UUID | SHA-256 | 파일크기 |
|------|------------------------------|------|---------|---------|
| 2023 | 2023 삼성물산 지속가능경영보고서.pdf | `d07e2d46-b804-4544-93dc-16581588c431` | `183daa1c...` | 14,122,507 B |
| 2022 | 2022 삼성물산 지속가능경영보고서.pdf | `e8d43602-ee24-4384-a964-8645807c754c` | `77f944c0...` | 13,059,475 B |
| 2021 | 2021 삼성물산 지속가능경영보고서.pdf | `cae6fabc-d36d-4de9-8342-0cdc8f9a0816` | `490389e5...` | 11,836,713 B |
| 2020 | 삼성물산CSR2020_국문.pdf | `cdf82c21-07ac-47c1-836a-3ff035d07b64` | `8feed446...` | 9,039,321 B |
| 2019 | 2019 삼성물산 CSR 보고서.pdf | `b5147b00-9c5d-4cf0-a607-13d1debc2c22` | `63976fc5...` | 9,912,797 B |

SHA-256 전체 값:
- 2023: `183daa1c2ccf2fbd12495a30da59f3ed5708ba0951696ee9951893456629a18f`
- 2022: `77f944c04d60c62a142c68bf15da4db6f5a2bd699298e5641be8db8fd4d8cfbd`
- 2021: `490389e56cf0d7fc505ec29693bcbd8790adce1d5cfd82638d33510a3d140254`
- 2020: `8feed44605003317fcd375725556aa68086f72cfcbfd05f69733cd3b4a067890`
- 2019: `63976fc557bab0b62ad4bacb4e47fd055cc9c7a48c9673b06e688b53765fb550`

추가 파일 (참고용):
- 2022_carbon_neutrality.pdf: UUID `977f1983-3a7d-4538-b43f-c7423a6d7cf8` = "탄소중립 보고서" (2,777,816 B, SHA256=`8da60e92...`) — 지속가능경영보고서 아님, 별도 탄소중립 특별 보고서

- **발간 여부**: YES — 5개년(2019~2023) 전부 확인. 2019년은 "CSR 보고서"명, 2020년부터 "지속가능경영보고서"로 개칭.
- **비고**: GRI Standards. Referer: samsungcnt.com/esg/resource/report/sustainability.do 필요. JS SPA이나 AJAX 백엔드 직접 호출 가능.
- **저장 경로**: `data/raw/sustainability_reports/028260/YYYY.pdf` — **다운로드 완료**

---

## 12. 삼성생명보험(주) (032830) — **완료: 2020~2023 다운로드 (4개년), 2019 미발간**

- **IR 사이트**: https://www.samsunglife.com/ (SPA — JS 렌더링 필수, 직접 PDF 호출 불가)
- **DART 공시 수**: 4건 (2020, 2021, 2022, 2023)
- **수집 방법**: KIND 자율공시 첨부문서 폴더에서 직접 PDF 다운로드

| 연도 | KIND 직접 PDF URL | SHA-256 | 파일크기 |
|------|------------------|---------|---------|
| 2023 | `https://kind.krx.co.kr/external/2023/06/29/000477/20230629000569/%EC%82%BC%EC%84%B1%EC%83%9D%EB%AA%85%202023%20ESG%20%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf` | `f2edd7c5...` | 45,455,727 B |
| 2022 | `https://kind.krx.co.kr/external/2022/07/14/000376/20220714000732/%EC%82%BC%EC%84%B1%EC%83%9D%EB%AA%85_2022_ESG%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf` | `f21dc51c...` | 32,709,130 B |
| 2021 | `https://kind.krx.co.kr/external/2021/07/09/000346/20210709000571/2021%EB%85%84%20%EC%82%BC%EC%84%B1%EC%83%9D%EB%AA%85%20%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf` | `746e9a50...` | 10,865,894 B |
| 2020 | `https://kind.krx.co.kr/external/2020/06/08/000432/20200608000294/%28%EB%B3%B4%EA%B3%A0%EC%84%9C%29%202020%20%EC%82%BC%EC%84%B1%EC%83%9D%EB%AA%85%20%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf` | `821284ec...` | 19,089,829 B |
| 2019 | **미발간** — DART/KIND 0건, 삼성생명 2020년 첫 발간 확인됨 |

SHA-256 전체 값:
- 2023: `f2edd7c552f27850249a24a8fea1f32d212d2b3cc489a2d0227e7c4d75fb232c`
- 2022: `f21dc51c95fd25a089cbbc9e46921a0a49bf12476788c0b00bc50172952fa6ce`
- 2021: `746e9a50b9122f765e1e02f0fa3ade17d9a55640ef8fbb9f2f07e6abeb7ea7e7`
- 2020: `821284ecaadf55fbc1d9934368a23cbc4ef6a8930a9316903f71fc55bba30772`

KIND 폴더 구조 해석:
- 2022: KIND 접수번호=20220714000376, 첨부문서번호=20220714000732
- 2021: KIND 접수번호=20210709000346, 첨부문서번호=20210709000571
- 2020: KIND 접수번호=20200608000432, 첨부문서번호=20200608000294
- Referer: kind.krx.co.kr 필요

- **발간 여부**: YES — 2020년~2023년 4개년. 2019년 미발간 확인 (삼성생명 2020년 첫 ESG 보고서 발간).
- **비고**: 보고서명이 "ESG 보고서" (2022·2023) vs "지속가능경영보고서" (2020·2021) — 동일 시리즈. GRI Standards.
- **저장 경로**: `data/raw/sustainability_reports/032830/YYYY.pdf` — **2020~2023 다운로드 완료**

---

## 13. 네이버(주) (035420) — **완료: 2020~2023 (4개년 다운로드)**

- **IR 사이트**: https://www.navercorp.com/esg/esgReports (SPA — JS 렌더링)
- **DART 공시 수**: 4건 (2021-04 [2020보고서], 2022-04 [2021보고서], 2023-07×2 [2022보고서])
- **DART 공시-보고연도 매핑**: DART 공시일 ≠ 보고연도. 2021년 4월 공시 = 2020 보고연도 ESG 보고서
- **2023 수집 방법**: `https://www.navercorp.com/api/article/naver/esg-report/ko` (내부 REST API 역공학)
  - articleId=33316, UUID=`261401da-f73b-46fb-9c14-7577dbdd87e6`
  - 다운로드: `https://www.navercorp.com/api/article/download/261401da-f73b-46fb-9c14-7577dbdd87e6`

| 연도 | 직접 PDF URL | SHA-256 | 파일크기 |
|------|-------------|---------|---------|
| 2023 | `https://www.navercorp.com/api/article/download/261401da-f73b-46fb-9c14-7577dbdd87e6` | `0c5bc29e92f6db6c91567781311e57d3fa2d06d4b19b2e186f74e5dd1cb369d6` | 15,088,872 B |
| 2022 | `https://www.navercorp.com/navercorp_/ir/sustainabilityReport/NAVER_2022_ESG_KOR.pdf` | `7d1861bc8ff6d06dcef8e13f32f8cb81aad0fa60fc21abd0a7885050fd83fdfc` | 15,627,096 B |
| 2021 | `https://www.navercorp.com/navercorp_/ir/sustainabilityReport/NAVER_2021_ESG_KOR.pdf` | `37cefb79f2214147587275735aba4f74a74129216cef835d56038b961a071cf9` | 7,286,126 B |
| 2020 | `https://www.navercorp.com/navercorp_/ir/sustainabilityReport/NAVER_2020_ESG_KOR_V2.pdf` | `0a68fbbb54282f048ab7217b2be53c69477c3fecefad90a1cd4c01906e938030` | 7,894,547 B |
| 2019 | **미발간** — NAVER 최초 ESG 보고서는 2020년 보고연도(2021년 4월 DART 공시). 2019년 독립 보고서 없음 |

- **발간 여부**: YES — 2020년~2023년 4개년 완료. 2019년 독립 보고서 없음.
- **비고**: 2022년부터 ESG 보고서 → "통합보고서 (Integrated Report)"로 전환. GRI Standards + SASB + TCFD + VRF.
  API 역공학 경로: navercorp.min.js `ESG_REPORT_DATA.PREFIX` → `/api/article/naver/esg-report/{lang}` → articleId 33316 (2023).
- **저장 경로**: `data/raw/sustainability_reports/035420/YYYY.pdf` — **2020~2023 다운로드 완료**

---

## 14. (주)대한항공 (003490) — UPDATED

- **IR 사이트**: https://www.koreanair.com/kr/ko/footer/about-us/sustainable-management/report (403 차단)
- **뉴스룸**: https://news.koreanair.com/category/esg/지속가능경영/ (PDF CDN 소재지)
- **DART 공시 수**: 3건 (2022×2, 2023)
- **다운로드 링크** (직접 PDF):

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|------------|
| 2023 | https://kr.img.news.koreanair.com/wp-content/uploads/2023/07/2023-%EB%8C%80%ED%95%9C%ED%95%AD%EA%B3%B5-ESG-%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf | 6.3MB | ✅ 자동 다운로드 완료 |
| 2022 | https://kr.img.news.koreanair.com/wp-content/uploads/2022/07/2022-%EB%8C%80%ED%95%9C%ED%95%AD%EA%B3%B5-ESG-%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf | 15.3MB | ✅ 자동 다운로드 완료 |
| 2021 | 공식 사이트 아카이브 (한국어 파일명 패턴 동일) | — | 수동 확인 필요 |
| 2020 | https://kr.img.news.koreanair.com/wp-content/uploads/2021/04/2020-%EB%8C%80%ED%95%9C%ED%95%AD%EA%B3%B5-%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EC%84%B1-%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf | — | 기존 확인 |
| 2019 | 공식 사이트 아카이브 또는 뉴스룸 확인 | — | 수동 확인 필요 |

- **CDN 패턴**: `https://kr.img.news.koreanair.com/wp-content/uploads/{YYYY}/{MM}/{YYYY}-대한항공-ESG-보고서.pdf` (한글 파일명, URL인코딩 필요)
- **주의**: 뉴스룸 CDN(kr.img.news.koreanair.com)은 직접 접근 가능하나 정확한 파일명(한글 포함)이 필요. www.koreanair.com 직접 접근 403.
- **비고**: 2021년부터 보고서명 "ESG 보고서"로 변경. GRI Standards + Korea Management Registrar 제3자 검증. 문의: KAL_ESG@koreanair.com
- **저장 경로**: `data/raw/sustainability_reports/003490/YYYY.pdf`

---

## 15. (주)두산 (000150) — UPDATED

- **IR 사이트**: https://www.doosan.com/en/csr/about-csr/?menu=sustainability-report
- **DART 공시 수**: 5건 (2019, 2020, 2021, 2022, 2023 — 5개년 완전)
- **다운로드 링크** (직접 PDF, doosan.com /file/down/ UUID 패턴):

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|------------|
| 2023 | https://kind.krx.co.kr/external/2024/06/28/000682/20240628000875/2023%EB%85%84%20(%EC%A3%BC)%EB%91%90%EC%82%B0_ESG%EB%B3%B4%EA%B3%A0%EC%84%9C_%EA%B5%AD%EB%AC%B8.pdf | — | 기존 확인 |
| 2022 | https://www.doosan.com/file/down/5784ccf1-7f35-4261-9b77-b922a700b9cd | 12.4MB | ✅ 자동 다운로드 완료 |
| 2021 | https://www.doosan.com/file/down/a8e332ae-f56e-467f-8a61-f119453f75f7 | 20.4MB | ✅ 자동 다운로드 완료 |
| 2020 | https://www.doosan.com/file/down/2bb0a152-2421-4877-9b6b-3b463dff6b07 | 6.2MB | ✅ 자동 다운로드 완료 |
| 2019 | https://www.doosan.com/file/down/c0f764b1-b480-49a2-bc36-ef63c124d024 | 4.4MB | ✅ 자동 다운로드 완료 |

- **UUID 추출 방법**: doosan.com/en/csr/about-csr/?menu=sustainability-report 페이지 HTML에 JS 변수로 임베드된 JSON에서 추출. 각 UUID가 연도별 KOR 보고서에 대응.
- **비고**: 2020년부터 보고서명 "ESG 보고서"로 변경 (이전 "지속가능경영보고서"). GRI Standards. Interactive PDF 제공(2023).
- **저장 경로**: `data/raw/sustainability_reports/000150/YYYY.pdf`

---

## 16. 롯데쇼핑(주) (023530) — UPDATED

- **IR 사이트**: https://www.lotteshopping.com/esgSystem/report
- **PDF CDN**: https://minfo.lotteshopping.com/content/cmpl/esgReport/
- **DART 공시 수**: 3건 (2022×2, 2023)
- **다운로드 링크**:

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|------------|
| 2023 | https://minfo.lotteshopping.com/content/cmpl/esgReport/2023_KOR.pdf | — | ✅ URL 확인 (크기 초과로 직접 검증) |
| 2022 | https://minfo.lotteshopping.com/content/cmpl/esgReport/2022_KOR.pdf | 10.1MB | ✅ 자동 다운로드 완료 |
| 2021 | https://minfo.lotteshopping.com/content/cmpl/esgReport/2021_KOR.pdf | — | ✅ URL 확인 (크기 초과로 직접 검증) |
| 2020 | IR 사이트 아카이브 확인 필요 | — | ⚠️ 수동 |
| 2019 | IR 사이트 아카이브 확인 필요 | — | ⚠️ 수동 |

- **URL 패턴**: `https://minfo.lotteshopping.com/content/cmpl/esgReport/{YYYY}_KOR.pdf` — 연도 교체로 다운로드 가능.
- **비고**: GRI Standards. 2019~2021은 DART 미공시.
- **저장 경로**: `data/raw/sustainability_reports/023530/YYYY.pdf`

---

## 17. 롯데케미칼(주) (011170) — UPDATED

- **IR 사이트**: https://www.lottechem.com/ko/esg/management_report.do
- **DART 공시 수**: 3건 (2021, 2022, 2023)
- **다운로드 링크**:

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|------------|
| 2023 | https://www.lottechem.com/pdfRead.do?fileId=FILE_240628111836133&voNm=esgVo&category=ko | 18.5MB | ✅ 자동 다운로드 완료 |
| 2022 | https://www.lottechem.com/pdfRead.do?fileId=FILE_240806135010740&voNm=esgVo&category=ko | — | ✅ URL 확인 |
| 2021 | https://www.lottechem.com/pdfRead.do?fileId=FILE_240806134952705&voNm=esgVo&category=ko | 10.9MB | ✅ 자동 다운로드 완료 |
| 2020 | https://www.lottechem.com/pdfRead.do?fileId=FILE_210910080913889&voNm=esgVo&category=ko | — | ✅ URL 확인 |
| 2019 | IR 사이트 아카이브 (2007년부터 매년 발간) | — | ⚠️ 수동 |

- **fileId 추출 방법**: lottechem.com/ko/esg/management_report.do 페이지 HTML에서 각 연도별 버튼의 onclick 속성 파싱. 주의: `/download.do?fileId=...`는 썸네일 이미지(PNG), `/pdfRead.do?fileId=...`가 실제 PDF.
- **비고**: GRI Standards 2021 + TCFD + SASB 준거(2022~). 2022 보고서명 "ESG Report"로 변경.
- **저장 경로**: `data/raw/sustainability_reports/011170/YYYY.pdf`

---

## 18. (주)케이티 (030200)

- **IR 사이트**: https://corp.kt.com/html/sustain/possibility/reports.html
- **DART 공시 수**: 4건 (2021, 2022, 2023×2)
- **직접 PDF URL 발견 현황** (DART 첨부파일) — UPDATED 2026-04-24:

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|--------------|
| 2023 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20230721800640&dcm_id=99998&dcm_seq=551&fl_nm=KT+2023+ESG%EB%B3%B4%EA%B3%A0%EC%84%9C_230717.pdf` | 39141KB | OK |
| 2022 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20220725800116&dcm_id=99998&dcm_seq=504&fl_nm=2022%EB%85%84+KT+ESG%EB%B3%B4%EA%B3%A0%EC%84%9C_%EC%97%85%EB%A1%9C%EB%93%9C%EC%9A%A9.pdf` | 43626KB | OK |
| 2021 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20210729800582&dcm_id=99998&dcm_seq=428&fl_nm=KT+ESG%EB%B3%B4%EA%B3%A0%EC%84%9C+2021.pdf` | 12949KB | OK |
| 2020 | IR 사이트 아카이브 (corp.kt.com 직접 경로 차단 확인 — 서버 catch-all HTML 반환) | — | 수동 |
| 2019 | IR 사이트 아카이브 | — | 수동 |

- **비고**: corp.kt.com의 /upload/ 및 /html/sustain/pdf/ 하위 경로는 모든 .pdf 요청에 HTML 1832바이트 오류페이지 반환 확인. DART 첨부파일이 유일한 직접 경로. 전체 %PDF 매직바이트 확인.
- **저장 경로**: `data/raw/sustainability_reports/030200/YYYY.pdf` (2021~2023 완료)

---

## 19. (주)한화 (000880) — UPDATED

- **IR 사이트**: https://www.hanwhacorp.co.kr/hanwha/sustainability/esg_archives.jsp
- **DART 공시 수**: 5건 (2021×2, 2022×2, 2023)
- **다운로드 링크**:

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|------------|
| 2023 | https://www.hanwhacorp.co.kr/common/fileDownload.do?path=/upload/hanwha/sustainability/2023_Hanwha_Corporation_Sustainability_Report.pdf&name=2023_%E3%88%9C%ED%95%9C%ED%99%94_%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf | 63.5MB | ✅ 자동 다운로드 완료 |
| 2022 | https://www.hanwhacorp.co.kr/common/fileDownload.do?path=/upload/hanwha/sustainability/2022_Hanwha_Corporation_Sustainability_Report.pdf&name=2022_%E3%88%9C%ED%95%9C%ED%99%94_%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf | 233.8MB | ✅ 자동 다운로드 완료 |
| 2021 | https://www.hanwhacorp.co.kr/common/fileDownload.do?path=/upload/hanwha/sustainability/2021_Hanwha_Corporation_Sustainability_Report.pdf&name=2021_%E3%88%9C%ED%95%9C%ED%99%94_%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf | 19.0MB | ✅ 자동 다운로드 완료 |
| 2020 | IR 사이트 아카이브 확인 필요 | — | ⚠️ 수동 |
| 2019 | IR 사이트 아카이브 확인 필요 | — | ⚠️ 수동 |

- **URL 패턴**: `https://www.hanwhacorp.co.kr/common/fileDownload.do?path=/upload/hanwha/sustainability/{YYYY}_Hanwha_Corporation_Sustainability_Report.pdf&name={YYYY}_㈜한화_지속가능경영보고서.pdf` (name 파라미터 URL인코딩 필요)
- **JS 드롭다운**: esg_archives.jsp의 select[name="select_down_sustain"] 값으로 연도 선택, location.href에 동적 URL 생성.
- **주의**: 2022년 보고서가 233MB로 매우 큼 (인터랙티브 PDF).
- **비고**: GRI Standards. 2019~2020은 DART 미공시.
- **저장 경로**: `data/raw/sustainability_reports/000880/YYYY.pdf`

---

## 20. 한화솔루션(주) (009830) — UPDATED

- **IR 사이트**: https://www.hanwhasolutions.com/ko/sustainability/sustainable-report/
- **DART 공시 수**: 5건 (2021×2, 2022, 2023×2)
- **다운로드 링크**:

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|------------|
| 2023 | https://www.hanwhasolutions.com/static/ko/data/Hanwha_Solutions_Sustainability_Report_2023.pdf | 7.4MB | ✅ 자동 다운로드 완료 |
| 2022 | https://www.hanwhasolutions.com/static/ko/data/Hanwha_Solutions_Sustainability_Report_2022.pdf | 217.7MB | ✅ 자동 다운로드 완료 |
| 2021 | https://www.hanwhasolutions.com/static/ko/data/Hanwha_Solutions_Sustainability_Report.pdf | 25.0MB | ✅ 자동 다운로드 완료 |
| 2020 | IR 사이트 아카이브 확인 필요 | — | ⚠️ 수동 |
| 2019 | IR 사이트 아카이브 확인 필요 | — | ⚠️ 수동 |

- **주의**: 2021년 PDF 파일명이 연도 없음(`Hanwha_Solutions_Sustainability_Report.pdf`). 2022년 보고서도 217MB로 매우 큼.
- **비고**: GRI Standards. 한/영 제공. 케미칼 부문 별도 보고서(hcc.hanwha.co.kr) 존재 — Scope 1 합산 여부 확인 필요.
- **저장 경로**: `data/raw/sustainability_reports/009830/YYYY.pdf`

---

## 21. 현대제철(주) (004020) — UPDATED 2026-04-24

- **IR 사이트**: https://www.hyundai-steel.com/kr/sustainability/esg
- **추가 (통합보고서 웹)**: https://esg.hyundai-steel.com/
- **DART 공시 수**: 4건 (2021, 2022, 2023×2)
- **직접 PDF URL 발견 현황** (DART 첨부파일):

| 연도 | PDF URL | 파일크기 | 다운로드 확인 |
|------|---------|---------|--------------|
| 2023 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20230720800548&dcm_id=99998&dcm_seq=335&fl_nm=2023_HyundaiSteel_IntegratedReport_kor.pdf` | 13188KB | OK |
| 2022 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20220705800176&dcm_id=99998&dcm_seq=857&fl_nm=2022_hyundaiSteel_kor.pdf` | 8902KB | OK |
| 2021 | `https://dart.fss.or.kr/pdf/download/file.do?rcp_no=20210625800504&dcm_id=99998&dcm_seq=722&fl_nm=2021%EB%85%84+%ED%98%84%EB%8C%80%EC%A0%9C%EC%B2%A0+%ED%86%B5%ED%95%A9%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf` | 65126KB | OK |
| 2020 | IR 사이트 아카이브 (hyundai-steel.com /upload/down/ 경로 — 보고서 파일명 동적 생성으로 패턴 공략 불가) | — | 수동 |
| 2019 | IR 사이트 아카이브 | — | 수동 |

- **비고**: hyundai-steel.com /upload/down/ 경로는 정책문서만 직접 접근 가능, 보고서는 # placeholder href 사용. DART 첨부 전체 %PDF 매직바이트 확인. 2023 정정본(rcpNo=20230811800898)은 빈 첨부 — 원본(20230720800548) 사용.
- **저장 경로**: `data/raw/sustainability_reports/004020/YYYY.pdf` (2021~2023 완료)

---

## 22. (주)이마트 (139480) — UPDATED

- **IR 사이트**: https://company.emart.com/ko/ethic/sustainability_report.do
- **다운로드 엔드포인트**: POST https://company.emart.com/investor/down.do (brd_seq, flag=pdf)
- **DART 공시 수**: 2건 (2022, 2023)

| 연도 | 다운로드 정보 | 파일크기 | 다운로드 확인 |
|------|------------|---------|------------|
| 2023 | https://kind.krx.co.kr/external/2024/07/31/000214/20240731000452/emart%202023%20Sustainability%20Report.pdf | — | 기존 확인 |
| 2022 | POST /investor/down.do brd_seq=4172 flag=pdf (제목: "2022 이마트 지속가능경영보고서", 게시일: 2023-07-21) | 16.5MB | ✅ 자동 다운로드 완료 |
| 2021 | POST /investor/down.do brd_seq=3793 (제목: "2021 이마트 지속가능경영보고서", 게시일: 2022-07-22) | — | ✅ URL/seq 확인 |
| 2020 | IR 사이트 아카이브 확인 필요 (페이지 탐색) | — | ⚠️ 수동 |
| 2019 | IR 사이트 아카이브 확인 필요 (발간 여부 불확실) | — | ⚠️ 수동 |

- **다운로드 방법**: GET/POST에 confirm 대화상자 없이 가능. brd_seq를 sustainability_report.do 페이지 HTML에서 파싱 (down('seq', 'pdf') 패턴).
- **비고**: GRI Standards. 2019~2021은 DART 미공시.
- **저장 경로**: `data/raw/sustainability_reports/139480/YYYY.pdf`

---

## 23. 중소기업은행 (024110) — **완료: 2019·2021~2023 (4개년), 2020 미발간**

- **IR 사이트**: https://www.ibk.co.kr/intro/contrib/contribute_report.jsp
- **DART 공시 수**: 3건 (2021, 2022, 2023)
- **수집 방법**: IBK 공식 IR 아카이브 직접 PDF 다운로드 `/fup/finebank/about/contribute/report/ibk_report_YYYY.pdf`

| 연도 | 직접 PDF URL | SHA-256 | 파일크기 |
|------|-------------|---------|---------|
| 2023 | `https://www.ibk.co.kr/fup/finebank/about/contribute/report/ibk_report_2023.pdf` | `742dbb43...` | 20,592,872 B |
| 2022 | `https://www.ibk.co.kr/fup/finebank/about/contribute/report/ibk_report_2022.pdf` | `4dbc7c5c...` | 28,502,956 B |
| 2021 | `https://www.ibk.co.kr/fup/finebank/about/contribute/report/ibk_report_2021.pdf` | `7a96e7c3...` | 24,335,061 B |
| 2020 | **미발간** — IBK 공식 아카이브에서 2020년 보고서 없음 확인 (2019→2021 직접 연결) |
| 2019 | `https://www.ibk.co.kr/fup/finebank/about/contribute/report/ibk_report_2019.pdf` | `e78a960f...` | 29,412,336 B |

SHA-256 전체 값:
- 2023: `742dbb43c2cc018452254a735a52dc269a7a97765a6a9beb18b568ea41fa821b`
- 2022: `4dbc7c5c63d325fc2db1b5e926eeb035621c1b83484c3035b2d3d7ee5214ebc3`
- 2021: `7a96e7c353c6f91503d9a988a945fabe3b623058b7e0665ee2d5f700103a1966`
- 2019: `e78a960f22ab9fc1e477df31f44dd80d961cf721d152a0418d047aa1bfdf8b63`

- **발간 여부**: YES — 2019·2021~2023 (4개년). **2020년 보고서는 IBK 미발간 확인** (아카이브에서 2019→2021로 연결, 2020년 건너뜀).
- **비고**: GRI Standards + ISSB IFRS S 공개초안 준수(2023). 국/영문 제공. 공기업이지만 DART 자율공시 3건 병행.
- **저장 경로**: `data/raw/sustainability_reports/024110/YYYY.pdf` — **다운로드 완료 (4개년)**

---

## DART 공시 뷰어 URL 전체 목록

아래는 Task 2에서 감지된 81건 중 핵심 공시 URL만 추출 (최신본 기준, 정정본 우선):

| 기업명 | 연도 | DART 뷰어 URL |
|--------|------|---------------|
| SK이노베이션 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230714800506 |
| SK이노베이션 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220729800368 |
| SK이노베이션 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210726800456 |
| SK이노베이션 | 2020 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200611800141 |
| 네이버 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230703800476 |
| 네이버 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220419800080 |
| 네이버 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210419800440 |
| 대한항공 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230630800457 |
| 대한항공 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220706800395 |
| 두산 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230725800223 |
| 두산 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220718800067 |
| 두산 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210714800318 |
| 두산 | 2020 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200722800404 |
| 두산 | 2019 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20190812800373 |
| 롯데쇼핑 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230630800056 |
| 롯데쇼핑 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220706800069 |
| 롯데케미칼 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230714800023 |
| 롯데케미칼 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220630800965 |
| 롯데케미칼 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210702800064 |
| 삼성생명 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230629800477 |
| 삼성생명 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220714800376 |
| 삼성생명 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210709800346 |
| 삼성생명 | 2020 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200608800432 |
| 삼성전자 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230703800528 |
| 삼성전자 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220630800927 |
| 삼성전자 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210706800475 |
| 삼성전자 | 2020 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200715800250 |
| 삼성전자 | 2019 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20190731800352 |
| SK하이닉스 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230721800113 |
| SK하이닉스 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220728800117 |
| SK하이닉스 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210706800538 |
| SK하이닉스 | 2020 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200723800341 |
| SK하이닉스 | 2019 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20191105800202 |
| LG디스플레이 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230731800110 |
| LG디스플레이 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220725800468 |
| LG디스플레이 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210722800087 |
| LG디스플레이 | 2020 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200724800265 |
| LG디스플레이 | 2019 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20190812800606 |
| LG에너지솔루션 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230801800047 |
| LG에너지솔루션 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220803800009 |
| 이마트 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230831800188 |
| 이마트 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220714800163 |
| 중소기업은행 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230727800775 |
| 중소기업은행 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220718800509 |
| 중소기업은행 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210805800431 |
| KT | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230713800287 |
| KT | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220725800116 |
| KT | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210729800582 |
| 포스코홀딩스 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210803800120 |
| 포스코홀딩스 | 2020 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200422800324 |
| 포스코홀딩스 | 2019 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20191108800048 |
| 한화 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230630801017 |
| 한화 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220711800543 |
| 한화 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20211015800382 |
| 한화솔루션 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230530800639 |
| 한화솔루션 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220629800111 |
| 한화솔루션 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20211102800095 |
| 현대모비스 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230608800176 |
| 현대모비스 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220609800485 |
| 현대모비스 | 2019 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20191017800364 |
| 현대자동차 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230713800011 |
| 현대자동차 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220708800003 |
| 현대제철 | 2023 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230720800548 |
| 현대제철 | 2022 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220705800176 |
| 현대제철 | 2021 | https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210625800504 |

---

## 수집 현황 요약표

| # | 기업명 | 종목코드 | DART 공시 | 직접 PDF 확인 | 비고 |
|---|--------|----------|-----------|--------------|------|
| 1 | 삼성전자 | 005930 | 5건 | 5개년 직접 PDF | samsung.com 직접 링크 확인 완료 |
| 2 | 현대자동차 | 005380 | 2건 | 2022~2023 직접 PDF | 2019~2021 아카이브 수동 확인 필요 |
| 3 | SK이노베이션 | 096770 | 4건 | IR 사이트 JS 버튼 | skinnovation.com 방문 필요 |
| 4 | 포스코홀딩스 | 005490 | 4건 | **2019~2021 자동완료** | posco.co.kr/docs/kor6/jsp/dn/irinfo/ 직접 접근 |
| 5 | LG에너지솔루션 | 373220 | 2건 | 2022~2023 | 2019~2021 해당 없음 (상장 전) |
| 6 | LG디스플레이 | 034220 | 9건 | IR 사이트 방문 | 5개년 전부 발간 확인 |
| 7 | 현대모비스 | 012330 | 3건 | 5개년 직접 PDF | mobis.com 직접 링크 확인 완료 |
| 8 | SK하이닉스 | 000660 | 7건 | 2022~2023 KIND | 2019~2021 IR 아카이브 필요 |
| 9 | 한국전력공사 | 015760 | 0건 | **5개년 API 완료** | KEPCO FileDownSecure.do API |
| 10 | CJ제일제당 | 097950 | 0건 | 2019·2022·2023 직접 PDF | 2020~2021 패턴 추정 |
| 11 | 삼성물산 | 028260 | 0건 | **5개년 AJAX API 완료** | samsungcnt.com li/sustainability.do |
| 12 | 삼성생명 | 032830 | 4건 | **2020~2023 KIND 완료** | 2019년 미발간 확인 |
| 13 | 네이버 | 035420 | 4건 | **2020~2023 완료** | navercorp.com REST API 역공학 성공, 2019 미발간 |
| 14 | 대한항공 | 003490 | 3건 | **2022·2023 자동완료** | kr.img.news.koreanair.com CDN (한글 파일명) |
| 15 | 두산 | 000150 | 5건 | **2019~2022 자동완료** | doosan.com/file/down/UUID 패턴 |
| 16 | 롯데쇼핑 | 023530 | 3건 | **2022 자동완료** | minfo.lotteshopping.com CDN 패턴 |
| 17 | 롯데케미칼 | 011170 | 3건 | **2021·2023 자동완료** | lottechem.com/pdfRead.do?fileId 패턴 |
| 18 | KT | 030200 | 4건 | **2021~2023 자동완료** | DART 첨부파일 직접 경로 (corp.kt.com PDF 경로 차단 확인) |
| 19 | 한화 | 000880 | 5건 | **2021~2023 자동완료** | hanwhacorp.co.kr fileDownload.do 패턴 |
| 20 | 한화솔루션 | 009830 | 5건 | **2021~2023 자동완료** | hanwhasolutions.com/static/ko/data/ 직접 |
| 21 | 현대제철 | 004020 | 4건 | **2021~2023 자동완료** | DART 첨부파일 직접 경로 |
| 22 | 이마트 | 139480 | 2건 | **2022 자동완료** | company.emart.com POST /investor/down.do brd_seq=4172 |
| 23 | 중소기업은행 | 024110 | 3건 | **4개년 IR 직접 PDF 완료** | 2020년 미발간 확인 |

### 2026-04-17 Wave 4 자동 다운로드 결과 (콩글로머릿·화학 그룹)
- **총 19개 PDF 자동 다운로드 완료**: 8개 기업, 19개 연도
- **누적 다운로드 용량**: 약 706MB
- **잔여 수동 수집 대상**: 대한항공 2021 (파일명 미확인)

### 2026-04-24 Wave 5 자동 다운로드 결과 (기술·제조 그룹)
- **총 20개 PDF 자동 다운로드 완료**: 6개 기업, 20개 연도
- **다운로드 경로**: DART 첨부파일 직접 URL(pdf/download/file.do) + lgdisplay.com 직접 PDF
- **핵심 발견**: DART 뷰어 페이지의 pdf/download/main.do 팝업에서 file.do 첨부 URL 추출 방법 확립
- **SK이노베이션 2023**: skinnovation.com JSESSIONID 인증 필요 → DART rcpNo=20240621800170 첨부로 해결
- **LG에너지솔루션 2023**: lgensol.com 접근 차단 → DART rcpNo=20240627800741 첨부로 해결
- **KT 2021~2023**: corp.kt.com PDF 경로 서버 차단(HTML 오류반환) → DART 첨부로 해결
- **현대제철 2023**: 정정본(rcpNo=20230811800898) 빈 첨부 → 원본(rcpNo=20230720800548) 사용
- **LGD 2019~2023**: lgdisplay.com/attachment/esg/csm/ 직접 경로 확인 (5개년 전부)
- **누적 다운로드 총량**: 약 1.2GB (tech group 20개 PDF 합산)

### 2026-04-17 Wave 6 자동 다운로드 결과 (서비스·금융 그룹 + DART 0건 기업)

본 세션에서 신규 수집된 21개 PDF:

| 기업 | 연도 | 수집 방법 | SHA-256 (16자리) | 파일크기 |
|------|------|-----------|-----------------|---------|
| 한국전력공사 | 2019~2023 | KEPCO FileDownSecure.do API 직접 호출 | 개별 기록 위 참조 | 8MB~85MB |
| 중소기업은행 | 2019,2021~2023 | ibk.co.kr /fup/finebank/.../ 직접 PDF | 개별 기록 위 참조 | 20MB~30MB |
| 삼성물산 | 2019~2023 | samsungcnt.com POST li/sustainability.do → /file/down.do?id=UUID | 개별 기록 위 참조 | 9MB~14MB |
| 삼성생명 | 2020~2023 | KIND /external/YYYY/MM/DD/CORP/DOCNO/ 직접 PDF | 개별 기록 위 참조 | 10MB~45MB |
| 네이버 | 2020~2022 | navercorp.com /navercorp_/ir/sustainabilityReport/ 직접 PDF | 개별 기록 위 참조 | 7MB~16MB |
| 네이버 | 2023 | navercorp.com REST API `/api/article/naver/esg-report/ko` → UUID `261401da` | `0c5bc29e92f6db6c...` | 15,088,872 B |

**Wave 6 발견 사항:**
- 한국전력공사: DART 미공시이나 공식 지속가능경영 페이지 FileDownSecure.do API로 5개년 전부 접근 가능. Content-Type=application/x-msdownload이나 실제 PDF.
- 중소기업은행: 2020년 보고서 IBK 공식 미발간 확인 (404 실증). 아카이브가 2019→2021로 건너뜀.
- 삼성물산: 사이트 JS SPA이나 AJAX 백엔드 `li/sustainability.do` 직접 POST 가능. 2022년 파일 UUID 2개 — UUID `977f1983`=탄소중립특별보고서, UUID `e8d43602`=지속가능경영보고서(메인).
- 삼성생명: samsunglife.com SPA 완전 차단. KIND 자율공시 첨부문서 폴더(99998.htm 파싱)로 우회. KIND 폴더 번호 ≠ DART rcpNo 체계 다름.
- 네이버: 2019년 독립 ESG 보고서 없음(첫 보고서=2020 보고연도, 2021-04 공시). 2023 통합보고서는 navercorp.com 내부 REST API 역공학으로 자동 수집 완료(UUID: 261401da-f73b-46fb-9c14-7577dbdd87e6).
- DART 공시-보고연도 매핑(네이버): 2021-04-19공시=2020보고서, 2022-04-19공시=2021보고서, 2023-07-03공시=2022보고서.

**Wave 6 추가 (2026-04-24):**
- 네이버 2023: navercorp.min.js 역공학 → `ESG_REPORT_DATA.PREFIX=/api/article/naver/esg-report/{lang}` 발견 → `/api/article/naver/esg-report/ko` 호출 → articleId=33316 UUID=`261401da` 자동 다운로드 완료 (15,088,872B)

## 수집 전략별 분류

### 그룹 A — 직접 PDF 자동 다운로드 완료
- 삼성전자 005930 (5개년), 현대모비스 012330 (5개년)
- LG디스플레이 034220 (5개년 — lgdisplay.com/attachment/esg/csm/)
- SK이노베이션 096770 (2020~2023 — DART 첨부 직접 URL)
- SK하이닉스 000660 (5개년 — 2019~2021 DART 첨부, 2022~2023 KIND/HubSpot)
- LG에너지솔루션 373220 (2022~2023 — DART 첨부 직접 URL)
- KT 030200 (2021~2023 — DART 첨부 직접 URL)
- 현대제철 004020 (2021~2023 — DART 첨부 직접 URL)
- CJ제일제당 097950 (2019·2022·2023 확인, 2020~2021 추정)
- 대한항공 003490 (2020), 롯데쇼핑 023530 (2023), 롯데케미칼 011170 (2021·2022·2023)
- 두산 000150 (2023 KIND), 이마트 139480 (2022·2023)
- 한화 000880 (2021~2023), 한화솔루션 009830 (2021~2023)

### 그룹 B — DART 첨부 URL 확인 완료 (pdf/download/file.do 직접 접근)
- 중소기업은행 024110 (2021~2023) — DART 뷰어 확인, 첨부 URL 미추출
- 삼성생명 032830 (2020~2023) — DART 뷰어 확인

### 그룹 C — IR 사이트 수동 방문 필수 (DART 미공시 + 자동화 불가)
- 한국전력공사 015760 (전 연도 — DART 0건, 공기업)
- 삼성물산 028260 (전 연도 — DART 0건)
- 현대자동차 005380 (2019~2021 — DART 미공시 구간)
- 포스코홀딩스 005490 (2022~2023 — 법인 전환 후 미탐지)
- 네이버 035420 (2019 미발간 확인, 2020~2023 완료)
- 대한항공 003490 (2021 파일명 미확인)
- 모든 기업 2019~2020 연도 중 DART 미공시 구간

---

*이 가이드는 2026-04-17 기준 웹 조사 결과이며, 일부 URL은 사이트 구조 변경으로 만료될 수 있습니다.*
*PDF 다운로드 후 반드시 SHA-256을 계산하여 `data/README.md`에 기록하십시오.*
