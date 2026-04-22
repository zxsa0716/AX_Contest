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

## 03. SK이노베이션(주) (096770)

- **IR 사이트**: https://www.skinnovation.com/esg/Sustainability_Report
- **DART 공시 수**: 4건 (2020, 2021, 2022, 2023 — 2019 공시 미탐지)
- **다운로드 링크**: 사이트 내 연도별 다운로드 버튼 존재; 직접 PDF URL은 JS 렌더링으로 추출 불가

| 연도 | 비고 |
|------|------|
| 2023 | Sustainability Report KOR/ENG, Taxonomy Report KOR |
| 2022 | ESG Report KOR/ENG, Net Zero Special Report |
| 2021 | ESG Report KOR/ENG, ESG Performance Report, Net Zero Special Report |
| 2020 | ESG Report KOR/ENG, ESG Performance Report |
| 2019 | Sustainability Report + ESG Performance Report |

- **수동 수집 방법**: IR 사이트 직접 방문 → 연도별 다운로드 버튼 클릭
- **비고**: GRI Standards, 제3자 검증. 2023년부터 "Taxonomy Report" 별도 발간.
- **저장 경로**: `data/raw/sustainability_reports/096770/YYYY.pdf`

---

## 04. 포스코홀딩스(주) (005490)

- **IR 사이트 (2022~현재)**: http://www.posco-inc.com/poscoinc/v4/kor/esg/s91e4000400c.jsp
- **구 POSCO 사이트 (2019~2021)**: https://sustainability.posco.co.kr/S91/S91F10/kor/UI-PK_W027.do
- **DART 공시 수**: 4건 (2019, 2020×2, 2021 — 2022·2023 미탐지, 포스코홀딩스 출범 후 공시명 변경 가능성)

| 연도 | 비고 |
|------|------|
| 2023 | 포스코홀딩스 공식 사이트 (posco-inc.com) |
| 2022 | 포스코홀딩스 첫 발간 연도 |
| 2021 | 구 포스코 사이트 (posco.co.kr 또는 sustainability.posco.co.kr) |
| 2020 | 구 포스코 사이트 |
| 2019 | 구 포스코 사이트 |

- **주의**: 2022년 포스코홀딩스 출범으로 법인 전환. 2019~2021 보고서는 "포스코(POSCO)" 명의. GIR에서는 동일 사업자번호로 연속 확인 필요.
- **비고**: GRI Standards + ISAE 3000 제3자 검증. 한/영 제공.
- **저장 경로**: `data/raw/sustainability_reports/005490/YYYY.pdf`

---

## 05. LG에너지솔루션(주) (373220)

- **IR 사이트**: https://www.lgensol.com/kr/esg-sustainability
- **DART 공시 수**: 2건 (2022, 2023 — 2022년 1월 상장이므로 2019~2021은 해당 없음)

| 연도 | 비고 |
|------|------|
| 2023 | ESG 보고서 다운로드 (lgensol.com) |
| 2022 | ESG 보고서 다운로드 (lgensol.com) — 첫 발간 |
| 2019~2021 | 해당 없음 (2022.01 상장, 이전에는 LG화학 자회사로 별도 보고서 없음) |

- **비고**: GRI Standards Core 기반. 분석 시 2019~2021 Scope 1은 GIR 데이터만 사용 가능.
- **저장 경로**: `data/raw/sustainability_reports/373220/YYYY.pdf`

---

## 06. LG디스플레이(주) (034220)

- **IR 사이트**: https://www.lgdisplay.com/kor/esg/csm/csm-report
- **추가 페이지**: https://www.lgdisplay.com/kor/esg/board/report-and-databook
- **DART 공시 수**: 9건 (2019, 2020, 2021×2, 2022×2, 2023×3 — ESG위원회 개최결과 포함)

| 연도 | 비고 |
|------|------|
| 2023 | 지속가능경영보고서 (한/영/중/베트남어) |
| 2022 | 지속가능경영보고서 |
| 2021 | 지속가능경영보고서 |
| 2020 | 지속가능경영보고서 |
| 2019 | 지속가능경영보고서 |

- **수동 수집 방법**: IR 사이트 방문 → "ESG Report & Data book" 섹션 → 연도별 PDF 다운로드
- **비고**: GRI Standards. 5개년 전부 발간 확인. 한/영/중 다국어 제공. DART 공시 중 ESG위원회 결과 공시는 보고서가 아니므로 수집 제외.
- **저장 경로**: `data/raw/sustainability_reports/034220/YYYY.pdf`

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
- **다운로드 링크** (KIND 직접 PDF):

| 연도 | URL |
|------|-----|
| 2023 | https://kind.krx.co.kr/external/2023/08/04/000103/20230803000340/SK%ED%95%98%EC%9D%B4%EB%8B%89%EC%8A%A4%20%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C%202023.pdf |
| 2022 | https://20028749.fs1.hubspotusercontent-na1.net/hubfs/20028749/A_Medialibrary/10_Newsroom%20Upload/2022/7%EC%9B%94/ESG_%ED%94%84%EB%A6%AC%EC%A6%98/SK%ED%95%98%EC%9D%B4%EB%8B%89%EC%8A%A4_%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EA%B2%BD%EC%98%81%EB%B3%B4%EA%B3%A0%EC%84%9C_2022.pdf |
| 2021 | IR 사이트 아카이브 확인 필요 |
| 2020 | IR 사이트 아카이브 확인 필요 |
| 2019 | IR 사이트 아카이브 확인 필요 |

- **비고**: GRI Standards. DART 첨부정정은 내용 수정본이므로 최신 정정본을 수집.
- **저장 경로**: `data/raw/sustainability_reports/000660/YYYY.pdf`

---

## 09. 한국전력공사(주) (015760)

- **IR 사이트**: https://home.kepco.co.kr/kepco/SM/A/htmlView/SMAAHP000.do
- **DART 공시 수**: 0건 (자율공시 미제출 — 공공기관 특성상 자체 발간)

| 연도 | 비고 |
|------|------|
| 2023 | 한전 공식 지속가능경영 페이지 직접 수집 필요 |
| 2022 | 상동 |
| 2021 | 상동 |
| 2020 | 공공기관연구원(maip.kr) 아카이브에 2020년 보고서 확인 |
| 2019 | 한전 공식 사이트 또는 공공데이터포털 탐색 필요 |

- **대체 경로**: https://bsfesg.com/ — 2024년 한국전력 지속가능경영보고서 아카이브 확인됨
- **수동 수집 방법**: 한전 공식 사이트 지속가능경영 메뉴 → 연도별 PDF 직접 다운로드
- **비고**: 공공기관이므로 GRI Standards + 환경부 가이드라인 병행. DART 자율공시 전략 없음.
- **저장 경로**: `data/raw/sustainability_reports/015760/YYYY.pdf`

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

## 11. 삼성물산(주) (028260)

- **IR 사이트**: https://www.samsungcnt.com/esg/resource/report/sustainability.do
- **DART 공시 수**: 0건 (자율공시 미제출)

| 연도 | 비고 |
|------|------|
| 2023 | 삼성물산 ESG Resource Center 다운로드 (2017~2023 전 연도 제공) |
| 2022 | 상동 |
| 2021 | 상동 |
| 2020 | 상동 |
| 2019 | 상동 |

- **수동 수집 방법**: IR 사이트 방문 → 지속가능경영보고서 섹션 → 연도별 PDF 다운로드
- **비고**: GRI Standards. 2017년부터 발간. DART 0건이므로 IR 사이트 전용.
- **저장 경로**: `data/raw/sustainability_reports/028260/YYYY.pdf`

---

## 12. 삼성생명보험(주) (032830)

- **IR 사이트**: https://www.samsunglife.com/ (ESG/지속가능경영 섹션)
- **DART 공시 수**: 4건 (2020, 2021, 2022, 2023)
- **KIND 직접 PDF**:

| 연도 | KIND PDF URL |
|------|-------------|
| 2023 | https://kind.krx.co.kr/external/2023/06/29/000477/20230629000569/%EC%82%BC%EC%84%B1%EC%83%9D%EB%AA%85%202023%20ESG%20%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220714800376 |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210709800346 |
| 2020 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200608800432 |
| 2019 | 미탐지 — 삼성생명 IR 사이트 직접 확인 필요 |

- **비고**: 통합보고서(Integrated Report) 형태로 발간. GRI Standards.
- **저장 경로**: `data/raw/sustainability_reports/032830/YYYY.pdf`

---

## 13. 네이버(주) (035420)

- **IR 사이트**: https://www.navercorp.com/esg/esgReports
- **DART 공시 수**: 4건 (2021, 2022×2, 2023)
- **다운로드 링크** (직접 PDF):

| 연도 | 한국어 PDF URL |
|------|---------------|
| 2023 | IR 사이트 확인 필요 (Integrated Report 발간) |
| 2022 | https://www.navercorp.com/navercorp_/ir/sustainabilityReport/NAVER_2022_ESG_KOR.pdf (추정) |
| 2021 | IR 사이트 확인 필요 |
| 2020 | https://www.navercorp.com/navercorp_/ir/sustainabilityReport/NAVER_2020_ESG_KOR_V2.pdf |
| 2019 | IR 사이트 확인 필요 (발간 여부 불확실) |

- **비고**: 2022년부터 통합보고서(Integrated Report) 형태로 전환. GRI Standards. 2019년 보고서 발간 여부 별도 확인 필요.
- **저장 경로**: `data/raw/sustainability_reports/035420/YYYY.pdf`

---

## 14. (주)대한항공 (003490)

- **IR 사이트**: https://www.koreanair.com/kr/ko/footer/about-us/sustainable-management/report
- **DART 공시 수**: 3건 (2022×2, 2023)
- **다운로드 링크** (직접 PDF):

| 연도 | URL |
|------|-----|
| 2023 | 공식 사이트 다운로드 (2023 ESG Report) |
| 2022 | 공식 사이트 다운로드 |
| 2021 | 공식 사이트 아카이브 |
| 2020 | https://kr.img.news.koreanair.com/wp-content/uploads/2021/04/2020-%EB%8C%80%ED%95%9C%ED%95%AD%EA%B3%B5-%EC%A7%80%EC%86%8D%EA%B0%80%EB%8A%A5%EC%84%B1-%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf |
| 2019 | 공식 사이트 아카이브 또는 뉴스룸 확인 |

- **비고**: 2021년부터 보고서명 "ESG 보고서"로 변경. GRI Standards + Korea Management Registrar 제3자 검증. 문의: KAL_ESG@koreanair.com
- **저장 경로**: `data/raw/sustainability_reports/003490/YYYY.pdf`

---

## 15. (주)두산 (000150)

- **IR 사이트**: https://www.doosan.com/en/ir/report/ (영문) / https://www.doosan.com/ko/csr/about-csr/
- **DART 공시 수**: 5건 (2019, 2020, 2021, 2022, 2023 — 5개년 완전)
- **KIND 직접 PDF**:

| 연도 | URL |
|------|-----|
| 2023 | https://kind.krx.co.kr/external/2024/06/28/000682/20240628000875/2023%EB%85%84%20(%EC%A3%BC)%EB%91%90%EC%82%B0_ESG%EB%B3%B4%EA%B3%A0%EC%84%9C_%EA%B5%AD%EB%AC%B8.pdf |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220718800067 |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210714800318 |
| 2020 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20200722800404 |
| 2019 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20190812800373 |

- **비고**: 2020년부터 보고서명 "ESG 보고서"로 변경. GRI Standards. Interactive PDF 제공(2023).
- **저장 경로**: `data/raw/sustainability_reports/000150/YYYY.pdf`

---

## 16. 롯데쇼핑(주) (023530)

- **IR 사이트**: https://www.lotteshoppingir.com/esg/esg_06.jsp
- **추가**: https://www.lotteshopping.com/esgSystem/report
- **DART 공시 수**: 3건 (2022×2, 2023)
- **다운로드 링크**:

| 연도 | URL |
|------|-----|
| 2023 | https://www.lotte.co.kr/upload/report/shopping/lotteshopping_SR_kor_2023.pdf |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220706800069 |
| 2021 | IR 사이트 아카이브 확인 필요 |
| 2020 | IR 사이트 아카이브 확인 필요 |
| 2019 | IR 사이트 아카이브 확인 필요 |

- **비고**: GRI Standards. 2019~2021은 DART 미공시 — IR 사이트 수집 필요.
- **저장 경로**: `data/raw/sustainability_reports/023530/YYYY.pdf`

---

## 17. 롯데케미칼(주) (011170)

- **IR 사이트**: https://www.lottechem.com/ko/esg/management_report.do
- **DART 공시 수**: 3건 (2021, 2022, 2023)
- **다운로드 링크**:

| 연도 | URL |
|------|-----|
| 2023 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230714800023 |
| 2022 | https://www.lotte.co.kr/upload/report/chemical/HPC_2022_kor.pdf |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210702800064 |
| 2020 | IR 사이트 아카이브 (2007년부터 매년 발간) |
| 2019 | IR 사이트 아카이브 |

- **비고**: GRI Standards 2021 + TCFD + SASB 준거(2022~). 2022 보고서명 "ESG Report"로 변경.
- **저장 경로**: `data/raw/sustainability_reports/011170/YYYY.pdf`

---

## 18. (주)케이티 (030200)

- **IR 사이트**: https://corp.kt.com/html/sustain/possibility/reports.html
- **DART 공시 수**: 4건 (2021, 2022, 2023×2)
- **다운로드 링크**:

| 연도 | URL |
|------|-----|
| 2023 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230713800287 (정정: 20230721800640) |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220725800116 |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210729800582 |
| 2020 | IR 사이트 아카이브 (2006년부터 발간, 18회차) |
| 2019 | IR 사이트 아카이브 |

- **비고**: 통합보고서(ESG Report) 형태. GRI Standards. 2006년부터 CSR 백서 → 통합보고서 전환. 2019~2020은 DART 미공시 — IR 사이트 수집 필요.
- **저장 경로**: `data/raw/sustainability_reports/030200/YYYY.pdf`

---

## 19. (주)한화 (000880)

- **IR 사이트**: https://www.hanwhacorp.co.kr/hanwha/sustainability/introduction.jsp
- **DART 공시 수**: 5건 (2021×2, 2022×2, 2023)
- **다운로드 링크**:

| 연도 | URL |
|------|-----|
| 2023 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230630801017 |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220711800543 (정정: 20220713800272) |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20211015800382 (정정: 20211112800648) |
| 2020 | IR 사이트 아카이브 확인 필요 |
| 2019 | IR 사이트 아카이브 확인 필요 |

- **직접 PDF**: https://www.hanwha.co.kr/upload/news/press/2024/06/28/1719540216296_04.pdf (2024년 참고용)
- **비고**: GRI Standards. 2019~2020은 DART 미공시.
- **저장 경로**: `data/raw/sustainability_reports/000880/YYYY.pdf`

---

## 20. 한화솔루션(주) (009830)

- **IR 사이트**: https://www.hanwhasolutions.com/ko/sustainability/sustainable-report/
- **DART 공시 수**: 5건 (2021×2, 2022, 2023×2)
- **다운로드 링크**:

| 연도 | URL |
|------|-----|
| 2023 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230530800639 (정정: 20230623800383) |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220629800111 |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20211102800095 (정정: 20211102800152) |
| 2020 | IR 사이트 아카이브 확인 필요 |
| 2019 | IR 사이트 아카이브 확인 필요 |

- **직접 PDF 참고**: https://www.hanwha.co.kr/assets/data/philosophy/Hanwha_Solutions_Sustainability_Report_2025.pdf (2025년 참고용)
- **비고**: GRI Standards. 한/영 제공. 케미칼 부문 별도 보고서(hcc.hanwha.co.kr) 존재 — Scope 1 합산 여부 확인 필요.
- **저장 경로**: `data/raw/sustainability_reports/009830/YYYY.pdf`

---

## 21. 현대제철(주) (004020)

- **IR 사이트**: https://www.hyundai-steel.com/kr/sustainability/esg
- **추가 (통합보고서 웹)**: https://esg.hyundai-steel.com/
- **DART 공시 수**: 4건 (2021, 2022, 2023×2)

| 연도 | URL |
|------|-----|
| 2023 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230720800548 (정정: 20230811800898) |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220705800176 |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210625800504 |
| 2020 | IR 사이트 아카이브 (esg.hyundai-steel.com 웹 리포트) |
| 2019 | IR 사이트 아카이브 |

- **비고**: 2021년부터 디지털 기반 웹 리포트 + PDF 병행. GRI Standards. 2016년부터 통합보고서 발간.
- **저장 경로**: `data/raw/sustainability_reports/004020/YYYY.pdf`

---

## 22. (주)이마트 (139480)

- **IR 사이트**: https://company.emart.com/ko/ethic/sustainability_report.do
- **DART 공시 수**: 2건 (2022, 2023)

| 연도 | URL |
|------|-----|
| 2023 | https://kind.krx.co.kr/external/2024/07/31/000214/20240731000452/emart%202023%20Sustainability%20Report.pdf |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220714800163 |
| 2021 | IR 사이트 아카이브 확인 필요 |
| 2020 | IR 사이트 아카이브 확인 필요 |
| 2019 | IR 사이트 아카이브 확인 필요 (발간 여부 불확실) |

- **비고**: GRI Standards. 2019~2021은 DART 미공시. 2019년 보고서 발간 여부 별도 확인 필요.
- **저장 경로**: `data/raw/sustainability_reports/139480/YYYY.pdf`

---

## 23. 중소기업은행 (024110)

- **IR 사이트**: https://www.ibk.co.kr/common/navigation.ibk?linkUrl=/intro/contrib/contribute_report.jsp&pageId=IR06060000
- **DART 공시 수**: 3건 (2021, 2022, 2023)

| 연도 | URL |
|------|-----|
| 2023 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230727800775 |
| 2022 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220718800509 |
| 2021 | DART 뷰어: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210805800431 |
| 2020 | IR 사이트 아카이브 (2019, 2021, 2022, 2023 국문/영문 다운로드 확인) |
| 2019 | IR 사이트 아카이브 |

- **비고**: GRI Standards + ISSB IFRS S 공개초안 준수(2023). 국/영문 제공. 공기업이지만 자율공시 3건 확인.
- **저장 경로**: `data/raw/sustainability_reports/024110/YYYY.pdf`

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
| 4 | 포스코홀딩스 | 005490 | 4건 | 사이트 방문 필요 | 2022년 법인 전환 주의 |
| 5 | LG에너지솔루션 | 373220 | 2건 | 2022~2023 | 2019~2021 해당 없음 (상장 전) |
| 6 | LG디스플레이 | 034220 | 9건 | IR 사이트 방문 | 5개년 전부 발간 확인 |
| 7 | 현대모비스 | 012330 | 3건 | 5개년 직접 PDF | mobis.com 직접 링크 확인 완료 |
| 8 | SK하이닉스 | 000660 | 7건 | 2022~2023 KIND | 2019~2021 IR 아카이브 필요 |
| 9 | 한국전력공사 | 015760 | 0건 | IR 사이트 수동 | DART 자율공시 없음 |
| 10 | CJ제일제당 | 097950 | 0건 | 2019·2022·2023 직접 PDF | DART 0건, cj.co.kr 직접 링크 |
| 11 | 삼성물산 | 028260 | 0건 | IR 사이트 방문 | DART 0건, samsungcnt.com |
| 12 | 삼성생명 | 032830 | 4건 | 2023 KIND | 2019 미공시 — IR 수동 |
| 13 | 네이버 | 035420 | 4건 | 2020 직접 PDF | 2019·2021·2023 아카이브 확인 필요 |
| 14 | 대한항공 | 003490 | 3건 | 2020 직접 PDF | 2022·2023 DART 뷰어 |
| 15 | 두산 | 000150 | 5건 | 2023 KIND | 5개년 전부 DART 공시 |
| 16 | 롯데쇼핑 | 023530 | 3건 | 2023 직접 PDF | 2019~2021 IR 아카이브 |
| 17 | 롯데케미칼 | 011170 | 3건 | 2022 직접 PDF | 2019~2020 IR 아카이브 |
| 18 | KT | 030200 | 4건 | IR 사이트 방문 | 2019~2020 IR 아카이브 |
| 19 | 한화 | 000880 | 5건 | DART 뷰어 3건 | 2019~2020 IR 아카이브 |
| 20 | 한화솔루션 | 009830 | 5건 | DART 뷰어 3건 | 2019~2020 IR 아카이브 |
| 21 | 현대제철 | 004020 | 4건 | DART 뷰어 3건 | 2019~2020 IR 아카이브 |
| 22 | 이마트 | 139480 | 2건 | 2023 KIND | 2019~2021 IR 아카이브 |
| 23 | 중소기업은행 | 024110 | 3건 | DART 뷰어 3건 | 2019~2020 IR 아카이브 |

## 수집 전략별 분류

### 그룹 A — 직접 PDF 다운로드 가능 (스크립트 wget/requests 자동화 가능)
- 삼성전자 (5개년 완전)
- 현대모비스 (5개년 완전)
- CJ제일제당 (2019·2022·2023 확인, 2020~2021 URL 패턴 추정)
- 대한항공 2020년 1개
- 롯데쇼핑 2023년 1개
- 롯데케미칼 2022년 1개
- 두산 2023년 KIND PDF
- SK하이닉스 2022~2023 KIND/HubSpot PDF
- 이마트 2023 KIND PDF

### 그룹 B — DART 뷰어 URL 있음 (브라우저 수동 열기 + 첨부파일 저장)
- 20개사 합계 81건 뷰어 URL — 뷰어 내 PDF 링크 클릭하여 저장

### 그룹 C — IR 사이트 수동 방문 필수 (DART 0건 또는 뷰어만 존재하는 연도)
- 한국전력공사 (전 연도), 삼성물산 (전 연도), SK이노베이션 (JS 렌더링)
- 2019~2020 연도의 모든 기업 DART 미공시 구간

---

*이 가이드는 2026-04-17 기준 웹 조사 결과이며, 일부 URL은 사이트 구조 변경으로 만료될 수 있습니다.*
*PDF 다운로드 후 반드시 SHA-256을 계산하여 `data/README.md`에 기록하십시오.*
