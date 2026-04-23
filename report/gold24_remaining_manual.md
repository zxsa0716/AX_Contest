# Gold 24 지속가능경영보고서 — 최종 수동 수집 필요 목록

**현황 (2026-04-23)**: 70 PDFs 자동 다운로드 완료 (Gold 23개사 중 17개사 100%, 6개사 부분)

## 🔴 수동 수집 필요 10개 PDF (6개사)

DART에 URL만 있고 PDF 첨부가 없으며, IR 자동 다운로드 패턴 미발견. 각 IR 사이트에서 직접 다운로드 필요.

### 1. (주)한화 (000880) — **3개 전부 필요**
- **IR 사이트**: https://www.hanwhacorp.co.kr/hanwha/sustainability/introduction.jsp
- **수동 절차**:
  1. 사이트 접속 후 "지속가능경영보고서" 섹션 찾기 (좌측 메뉴 또는 스크롤)
  2. 2021, 2022, 2023 각 연도 PDF 다운로드 버튼 클릭
  3. 파일 저장:
     - `data/raw/sustainability_reports/000880/2021.pdf`
     - `data/raw/sustainability_reports/000880/2022.pdf`
     - `data/raw/sustainability_reports/000880/2023.pdf`
- **대안**: DART 뷰어에서 각 공시 첨부 확인
  - 2021: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20211015800382
  - 2022: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220711800543
  - 2023: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230630801017

### 2. (주)두산 (000150) — **4개 필요** (2023 확보)
- **IR 사이트**: https://www.doosan.com/kr/sustainability/sustainability-report
- **수동 절차**:
  1. 사이트 접속, 연도 드롭다운에서 2019~2022 각각 선택
  2. "다운로드" 또는 PDF 아이콘 클릭
  3. 저장 경로: `data/raw/sustainability_reports/000150/{YYYY}.pdf`
- **DART 대체**:
  - 2019: rcpNo=20190812800373
  - 2020: rcpNo=20200722800404
  - 2021: rcpNo=20210714800318
  - 2022: rcpNo=20220718800067

### 3. (주)대한항공 (003490) — **2개 필요** (2020 확보)
- **IR 사이트**: https://www.koreanair.com/about/social-responsibility/sustainability-report 
- **뉴스룸 아카이브**: https://news.koreanair.com/category/esg/지속가능경영/
- **수동 절차**:
  1. 뉴스룸에서 "2022 ESG 보고서" "2023 ESG 보고서" 게시물 검색
  2. 본문 하단 PDF 다운로드
  3. 저장: `data/raw/sustainability_reports/003490/{2022|2023}.pdf`
- **DART 대체**:
  - 2022: rcpNo=20220804800317
  - 2023: rcpNo=20230630800457

### 4. 롯데케미칼 (011170) — **2개 필요** (2022 확보)
- **IR 사이트**: https://www.lottechem.com/kr/sustainability/report
- **수동 절차**:
  1. "보고서" 또는 "Archive" 섹션에서 2021년, 2023년 보고서 선택
  2. 사이트가 PDF 썸네일 대신 PDF 뷰어로 여는 경우: 뷰어 오른쪽 상단 "다운로드" 버튼
  3. 저장: `data/raw/sustainability_reports/011170/{2021|2023}.pdf`
- **DART 대체**:
  - 2021: rcpNo=20210702800064
  - 2023: rcpNo=20230714800023

### 5. 롯데쇼핑 (023530) — **1개 필요** (2023 확보)
- **IR 사이트**: https://www.lotteshopping.com/sustain/reportlist
- **수동 절차**:
  1. 2022년 ESG 보고서 카드 클릭
  2. PDF 다운로드
  3. 저장: `data/raw/sustainability_reports/023530/2022.pdf`
- **DART 대체**: rcpNo=20220707800496

### 6. 이마트 (139480) — **1개 필요** (2023 확보)
- **IR 사이트**: https://company.emart.com/investor/esgReport.do
- **수동 절차**:
  1. 2022년 지속가능경영보고서 게시물 클릭
  2. 첨부 PDF 다운로드
  3. 저장: `data/raw/sustainability_reports/139480/2022.pdf`
- **DART 대체**: rcpNo=20220714800163

---

## 📊 다운로드 완료 후 파서 재실행

모든 PDF 수집 후:
```bash
.venv/Scripts/python.exe src/preprocessing/sustainability_report_parser.py \
  --reports-dir data/raw/sustainability_reports \
  --out data/interim/esg_reports_parsed.csv
```

예상 시간: ~10분. 결과: GRI 305-1 Scope 1, 305-2, 305-3, 조직경계, 검증 정보 전체 추출.

---

## ✅ 완료된 17개사 (참고)

삼성전자, 삼성물산, 삼성생명, SK하이닉스, SK이노베이션, LG디스플레이, LG에너지솔루션, 현대차, 현대모비스, 현대제철, 포스코홀딩스, KT, 한국전력공사, 한화솔루션, CJ제일제당, 네이버, 중소기업은행
