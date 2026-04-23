"""Download sustainability report PDFs for the tech/manufacturing group.

Covers 6 companies with missing years:
- SK이노베이션 (096770): 2020, 2021, 2022, 2023
- LG디스플레이 (034220): 2019, 2020, 2021, 2022, 2023
- SK하이닉스 (000660): 2019, 2020, 2021
- LG에너지솔루션 (373220): 2022, 2023
- KT (030200): 2021, 2022, 2023
- 현대제철 (004020): 2021, 2022, 2023

Sources:
- LGD: lgdisplay.com direct PDF (attachment/esg/csm/)
- SK Innovation: DART attachment (file.do endpoint)
- SK Hynix: DART attachment (file.do endpoint)
- LG Energy Solution: DART attachment (file.do endpoint)
- KT: DART attachment (file.do endpoint)
- Hyundai Steel: DART attachment (file.do endpoint)

DART attachment URL pattern:
https://dart.fss.or.kr/pdf/download/file.do?rcp_no={rcpNo}&dcm_id=99998&dcm_seq={seq}&fl_nm={encoded_filename}

Note on year mapping (DART filings are submitted the year AFTER the report year):
- SK이노베이션 rcpNo=20230714800506 → report year 2022 ESG
- SK이노베이션 rcpNo=20220729800368 → report year 2021 ESG
- SK이노베이션 rcpNo=20210726800456 → report year 2020 ESG
- SK이노베이션 rcpNo=20200611800141 → report year 2019 (not needed, 2019 not in scope)
  For 2023 SK이노베이션 report: not yet in DART as of 2026-04-17.
  Source is DART attachment confirmed only up to report year 2022.

CRITICAL: SK이노베이션 2023 ESG report (Sustainability Report)
File: 'sk이노베이션SR23_0830_v81.pdf' exists on skinnovation.com but requires browser session.
Fallback: manual download from https://www.skinnovation.com/esg/Sustainability_Report
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import requests
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "data" / "raw" / "sustainability_reports"
LOG = OUT_ROOT / "_download_log.jsonl"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

DART_BASE = "https://dart.fss.or.kr/pdf/download/file.do"


def dart_url(rcp_no: str, dcm_seq: str, fl_nm: str) -> str:
    """Build DART file download URL."""
    import urllib.parse
    encoded = urllib.parse.quote(fl_nm, safe="")
    return f"{DART_BASE}?rcp_no={rcp_no}&dcm_id=99998&dcm_seq={dcm_seq}&fl_nm={encoded}"


# Direct download records: (stock_code, report_year, url, label)
# DART attachment URLs confirmed as real PDFs via %PDF magic byte check.
# LGD direct PDF URLs confirmed 200 application/pdf.

RECORDS: list[tuple[str, int, str, str]] = [
    # -------------------------------------------------------------------
    # LG디스플레이 (034220) — lgdisplay.com direct PDF
    # -------------------------------------------------------------------
    ("034220", 2023, "https://www.lgdisplay.com/attachment/esg/csm/LGD_ESG_report_2023_kor.pdf", "LGD ESG 2023 KOR"),
    ("034220", 2022, "https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2022_kor.pdf", "LGD CSR 2022 KOR"),
    ("034220", 2021, "https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2021_kor.pdf", "LGD CSR 2021 KOR"),
    ("034220", 2020, "https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2020_kor.pdf", "LGD CSR 2020 KOR"),
    ("034220", 2019, "https://www.lgdisplay.com/attachment/esg/csm/LGD_CSR_report_2019_kor.pdf", "LGD CSR 2019 KOR"),

    # -------------------------------------------------------------------
    # SK이노베이션 (096770) — DART attachments
    # rcpNo=20230714800506 contains the 2022 ESG Report (filed 2023)
    # rcpNo=20220729800368 contains the 2021 ESG Report (filed 2022)
    # rcpNo=20210726800456 contains the 2020 ESG Report (filed 2021)
    # 2023 SK이노베이션 Sustainability Report: NO confirmed direct URL.
    # Requires manual download from skinnovation.com (JS-session-gated).
    # -------------------------------------------------------------------
    ("096770", 2022, dart_url("20230714800506", "695", "2022 SK이노베이션 ESG_Report.pdf"), "SKI 2022 ESG (DART)"),
    ("096770", 2021, dart_url("20220729800368", "409", "SK이노베이션 2021 ESG Report_국문.pdf"), "SKI 2021 ESG (DART)"),
    ("096770", 2020, dart_url("20210726800456", "883", "SK이노베이션 2020 ESG Report_KOR.pdf"), "SKI 2020 ESG (DART)"),
    # 2023: DART rcpNo=20240621800170 (filed 2024.06.21) — add separately below

    # -------------------------------------------------------------------
    # SK하이닉스 (000660) — DART attachments for 2019, 2020, 2021
    # (2022 and 2023 were already downloaded in prior run)
    # -------------------------------------------------------------------
    ("000660", 2019, dart_url("20191105800202", "947", "2019 SK hynix SR_kor_web(3).pdf"), "SKH 2019 SR (DART)"),
    ("000660", 2020, dart_url("20200723800341", "452", "2020 SK hynix SR_Kor_web F.pdf"), "SKH 2020 SR (DART)"),
    ("000660", 2021, dart_url("20210706800538", "815", "SK hynix 2021 Sustainability Report.pdf"), "SKH 2021 SR (DART)"),

    # -------------------------------------------------------------------
    # LG에너지솔루션 (373220) — DART attachments
    # rcpNo=20230801800047 contains 2022 ESG Report (filed 2023)
    # rcpNo=20220803800009 contains 2021 LGES ESG Report — but LGES only existed from 2022
    # Note: The 2022 filing (rcpNo=20220803800009) contains "2021 LGES ESG Report"
    #       This is the inaugural report covering 2021 activity; report year = 2021 (pre-listing)
    #       For our study, we use report years 2022 and 2023 only (post-listing).
    #       rcpNo=20230801800047 → report_year=2022 (covers 2022 GHG data)
    #       There is no 2023 report year filing yet visible in DART as of 2026-04.
    #       The 2024 DART filing would contain the 2023 ESG report.
    # -------------------------------------------------------------------
    ("373220", 2022, dart_url("20230801800047", "062", "LG에너지솔루션_2022 ESG Report_(KOR).pdf"), "LGES 2022 ESG (DART)"),
    # 2023 LGES: DART rcpNo=20240627800741 (filed 2024.06.27) — add separately below

    # -------------------------------------------------------------------
    # KT (030200) — DART attachments
    # rcpNo=20230721800640 (amended) contains KT 2023 ESG report
    # rcpNo=20220725800116 contains 2022 ESG report
    # rcpNo=20210729800582 contains 2021 ESG report
    # -------------------------------------------------------------------
    ("030200", 2023, dart_url("20230721800640", "551", "KT 2023 ESG보고서_230717.pdf"), "KT 2023 ESG (DART)"),
    ("030200", 2022, dart_url("20220725800116", "504", "2022년 KT ESG보고서_업로드용.pdf"), "KT 2022 ESG (DART)"),
    ("030200", 2021, dart_url("20210729800582", "428", "KT ESG보고서 2021.pdf"), "KT 2021 ESG (DART)"),

    # -------------------------------------------------------------------
    # 현대제철 (004020) — DART attachments
    # rcpNo=20230720800548 contains 2023 Integrated Report
    # rcpNo=20220705800176 contains 2022 Integrated Report
    # rcpNo=20210625800504 contains 2021 Integrated Report
    # -------------------------------------------------------------------
    ("004020", 2023, dart_url("20230720800548", "335", "2023_HyundaiSteel_IntegratedReport_kor.pdf"), "HDS 2023 IR (DART)"),
    ("004020", 2022, dart_url("20220705800176", "857", "2022_hyundaiSteel_kor.pdf"), "HDS 2022 IR (DART)"),
    ("004020", 2021, dart_url("20210625800504", "722", "2021년 현대제철 통합보고서.pdf"), "HDS 2021 IR (DART)"),

    # SK이노베이션 2023: DART rcpNo=20240621800170, dcm_seq=534 (filed 2024.06.21)
    ("096770", 2023, dart_url("20240621800170", "534",
        "SK이노베이션_지속가능경영보고서 2023.pdf"), "SKI 2023 SR (DART 2024.06.21)"),

    # LG에너지솔루션 2023: DART rcpNo=20240627800741, dcm_seq=158 (filed 2024.06.27)
    ("373220", 2023, dart_url("20240627800741", "158",
        "LG에너지솔루션_2023 ESG Report_KOR.pdf"), "LGES 2023 ESG (DART 2024.06.27)"),
]

MANUAL_NOTES: dict = {}  # All items now have confirmed DART URLs


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_record(rec: tuple[str, int, str, str]) -> dict:
    stock_code, year, url, label = rec
    out_dir = OUT_ROOT / stock_code
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{year}.pdf"

    if out.exists():
        data = out.read_bytes()
        return {
            "stock_code": stock_code, "year": year, "label": label,
            "url": url, "status": "cached",
            "path": str(out), "sha256": sha256(data), "size": len(data),
        }

    headers = {"User-Agent": UA}
    # DART requests benefit from Accept header
    if "dart.fss.or.kr" in url:
        headers["Accept"] = "application/pdf,application/octet-stream,*/*"
        headers["Referer"] = "https://dart.fss.or.kr/"

    try:
        r = requests.get(url, headers=headers, timeout=120, allow_redirects=True)
        r.raise_for_status()
        content = r.content

        if not content.startswith(b"%PDF"):
            snippet = content[:200].decode("utf-8", errors="replace")
            return {
                "stock_code": stock_code, "year": year, "label": label,
                "url": url, "status": "not_pdf",
                "size": len(content), "snippet": snippet[:100],
            }

        if len(content) < 500_000:  # < 500 KB is suspicious for a sustainability report
            return {
                "stock_code": stock_code, "year": year, "label": label,
                "url": url, "status": "too_small",
                "size": len(content),
            }

        out.write_bytes(content)
        return {
            "stock_code": stock_code, "year": year, "label": label,
            "url": url, "status": "ok",
            "path": str(out), "sha256": sha256(content), "size": len(content),
        }

    except Exception as exc:
        return {
            "stock_code": stock_code, "year": year, "label": label,
            "url": url, "status": "error",
            "error": f"{type(exc).__name__}: {str(exc)[:250]}",
        }


def main() -> int:
    print(f"Tech-group download: {len(RECORDS)} records to process")
    print(f"Manual-only (no URL): {len(MANUAL_NOTES)} records\n")

    results = []
    for rec in tqdm(RECORDS, desc="downloading", ncols=100):
        res = download_record(rec)
        results.append(res)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")

        icon = {"ok": "OK", "cached": "CACHED", "not_pdf": "NOT_PDF", "error": "ERROR", "too_small": "TOO_SMALL"}.get(
            res["status"], "?"
        )
        size_kb = res.get("size", 0) // 1024
        print(f"  [{icon}] {res['stock_code']} {res['year']} {res['label']} — {size_kb}KB")

        if res["status"] in ("ok",):
            time.sleep(1.0)

    # Summary
    from collections import Counter
    c = Counter(r["status"] for r in results)
    total_ok = c.get("ok", 0) + c.get("cached", 0)
    print(f"\n=== Summary ===")
    print(f"  Success (ok+cached): {total_ok}/{len(results)}")
    print(f"  Status breakdown: {dict(c)}")

    if MANUAL_NOTES:
        print(f"\n=== Manual download required ({len(MANUAL_NOTES)} items) ===")
        for (sc, yr), note in MANUAL_NOTES.items():
            print(f"  {sc} {yr}: {note}")

    return 0 if c.get("error", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
