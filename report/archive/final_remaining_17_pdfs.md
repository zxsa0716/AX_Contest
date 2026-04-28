# 🎯 마지막 남은 17개 PDF — Final Coverage Gap

**2026-04-24 기준**  
**현재**: 119 PDFs (98 in 2019-2023 range = **85.2%**)  
**완전 5년 기업**: 14/23 (61%)  
**잔여**: 17 PDFs

---

## 🟡 수집 가능 (11개)

| 기업 | 종목 | 필요 연도 | 참고 |
|---|---|---|---|
| 네이버 | 035420 | 2019 | [navercorp.com](https://www.navercorp.com/value/reportLibrary?menu=sustainabilityReport) |
| 삼성생명 | 032830 | 2019 | 2018/2020-2025 보유, 2019만 gap |
| 롯데쇼핑 | 023530 | 2019, 2020 | [lotteshopping.com/sustain/reportlist](https://www.lotteshopping.com/sustain/reportlist) |
| 이마트 | 139480 | 2019, 2020 | [company.emart.com/investor/esgReport.do](https://company.emart.com/investor/esgReport.do) |
| 중소기업은행 | 024110 | 2020 | [ibk.co.kr/esg/sustainability-report](https://www.ibk.co.kr/esg/sustainability-report.do) |
| 한화 | 000880 | 2019, 2020 | 단독 보고서 부재 가능. 한화그룹 통합 CSR 대체 가능 |
| 한화솔루션 | 009830 | 2019, 2020 | 2020.1 합병 신설 — 2019는 한화케미칼 전신 (HPC_2019 있음) ✅ 확인 |

## 🔴 구조적 미발행 (6개)

| 기업 | 종목 | 필요 연도 | 사유 |
|---|---|---|---|
| LG에너지솔루션 | 373220 | 2019, 2020, 2021 | 2022.1 상장, 이전은 LG화학 보고서 |
| 현대자동차 | 005380 | 2019, 2020, 2021 | 2022부터 standalone, 이전은 Hyundai Motor Group 통합 Annual Report |

---

## 🎯 100% 달성 시나리오

**11개 더 받으면**: 85.2% → **94.8%** (비구조적 100%)  
**대체자료 6개 포함**: → **100%** (이론적 최대)

### 한화솔루션 2019 해결책 발견
사용자가 업로드한 `HPC_2019_eng.pdf`는 **한화케미칼(Hanwha Petrochemical Corporation)** 2019 보고서. 한화솔루션 전신사이므로 **009830/2019.pdf로 사용 가능**. → 현재 이미 분류됨.

---

## 💾 저장 규칙

```
data/raw/sustainability_reports/{stock_code}/{YYYY}.pdf
```

## 📝 남은 작업 체크리스트

**우선순위 높음** (11개):
- [ ] 네이버 2019
- [ ] 삼성생명 2019
- [ ] 롯데쇼핑 2019
- [ ] 롯데쇼핑 2020
- [ ] 이마트 2019
- [ ] 이마트 2020
- [ ] 중소기업은행 2020
- [ ] 한화 2019
- [ ] 한화 2020
- [ ] 한화솔루션 2020
- [ ] (한화솔루션 2019 = HPC_2019_eng.pdf ✅ 이미 분류)

**옵션** (6개, 대체자료):
- [ ] LG에너지솔루션 2019-2021 → LG화학 보고서로 대체 (parent_company_proxy)
- [ ] 현대자동차 2019-2021 → Hyundai Motor Group Annual Report로 대체
