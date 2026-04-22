"""
detect_dart_esg_filings.py
--------------------------
For the 24 Gold-sample firms, query DART disclosure list API
for sustainability / ESG related filings 2019-2023.

Produces: data/interim/dart_esg_filings_gold24.csv

Columns:
    corp_code, corp_name, stock_code, year, rcept_no,
    report_nm, flr_nm, rcept_dt, dart_viewer_url,
    has_direct_pdf (bool), direct_pdf_url (str or "")
"""

import os
import time
import logging
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
DART_API_KEY: str = os.environ["DART_API_KEY"]

GOLD_CORPS_CSV = Path(__file__).resolve().parents[2] / "data/interim/gold_corps.csv"
OUTPUT_CSV = (
    Path(__file__).resolve().parents[2] / "data/interim/dart_esg_filings_gold24.csv"
)
FAILURES_CSV = (
    Path(__file__).resolve().parents[2]
    / "data/interim/failures_dart_esg_filings.csv"
)

DART_LIST_URL = "https://opendart.fss.or.kr/api/list.json"
DART_ATTACH_URL = "https://opendart.fss.or.kr/api/attach/doc.json"
DART_VIEWER_BASE = "https://dart.fss.or.kr/dsaf001/main.do"

# Keywords to match sustainability-related filings (case-insensitive)
ESG_KEYWORDS = [
    "지속가능",
    "sustainability",
    "esg",
    "환경",
    "온실가스",
    "탄소",
    "기후",
]

BGN_DE = "20190101"
END_DE = "20231231"

# Disclosure type codes that can carry sustainability reports as attachments
# "A" = 정기공시, "B" = 주요사항보고, "C" = 발행공시, "D" = 지분공시,
# "E" = 기타공시, "F" = 외부감사, "G" = 펀드공시, "H" = 자산유동화,
# "I" = 거래소공시, "J" = 공정위공시
# Sustainability reports are typically filed as "E" (기타공시) or "A"
PBLNTF_TY_TARGETS = ["A", "E"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _is_esg_report(report_nm: str) -> bool:
    """Return True if report name contains any ESG/sustainability keyword."""
    nm_lower = report_nm.lower()
    return any(kw in nm_lower for kw in ESG_KEYWORDS)


def fetch_dart_list(corp_code: str) -> list[dict]:
    """
    Fetch ALL disclosure list entries for corp_code over 2019-2023.
    Iterates pages until exhausted. Returns list of raw filing dicts.
    """
    results: list[dict] = []
    page_no = 1
    page_count = 1  # will be updated after first call

    while page_no <= page_count:
        params = {
            "crtfc_key": DART_API_KEY,
            "corp_code": corp_code,
            "bgn_de": BGN_DE,
            "end_de": END_DE,
            "page_no": str(page_no),
            "page_count": "100",
        }
        try:
            resp = requests.get(DART_LIST_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.warning("DART list API error corp_code=%s page=%d: %s", corp_code, page_no, exc)
            break

        status = data.get("status", "")
        if status == "013":
            # No data
            break
        if status != "000":
            log.warning(
                "DART list API non-zero status corp_code=%s status=%s msg=%s",
                corp_code,
                status,
                data.get("message", ""),
            )
            break

        page_count = int(data.get("total_page", 1))
        filings = data.get("list", [])
        results.extend(filings)
        log.debug(
            "corp_code=%s page=%d/%d filings_so_far=%d",
            corp_code,
            page_no,
            page_count,
            len(results),
        )
        page_no += 1
        if page_no <= page_count:
            time.sleep(0.3)  # polite rate limit

    return results


def fetch_attach_pdf(rcept_no: str) -> str:
    """
    Query DART attach doc list for rcept_no and return the first PDF URL.
    Returns "" if none found or on error.
    """
    params = {"crtfc_key": DART_API_KEY, "rcept_no": rcept_no}
    try:
        resp = requests.get(DART_ATTACH_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        log.debug("attach API error rcept_no=%s: %s", rcept_no, exc)
        return ""

    if data.get("status") != "000":
        return ""

    for doc in data.get("list", []):
        # dcm_nm contains the document description; url field is direct link
        # Typical field: "url": "https://dart.fss.or.kr/pdf/download/..."
        url = doc.get("url", "")
        if url.lower().endswith(".pdf") or "pdf" in url.lower():
            return url
        # Also accept doc_url or file_url keys if present
        for key in ("doc_url", "file_url", "dc_url"):
            alt = doc.get(key, "")
            if alt:
                return alt

    return ""


# ── Main ───────────────────────────────────────────────────────────────────────


def main() -> None:
    # 1. Load Gold corps — deduplicate on corp_code (LGD appears twice)
    gold_df = pd.read_csv(GOLD_CORPS_CSV, dtype=str)
    gold_df = gold_df.drop_duplicates(subset=["corp_code"]).reset_index(drop=True)
    log.info("Gold firms loaded: %d unique corp_codes", len(gold_df))

    rows: list[dict] = []
    failures: list[dict] = []

    for _, firm in gold_df.iterrows():
        corp_code: str = firm["corp_code"]
        corp_name: str = firm["corp_name"]
        stock_code: str = firm["stock_code"]

        log.info("Processing %s (%s)", corp_name, corp_code)
        raw_filings = fetch_dart_list(corp_code)
        log.info("  -> %d total filings fetched", len(raw_filings))

        # Filter to ESG-related
        esg_filings = [f for f in raw_filings if _is_esg_report(f.get("report_nm", ""))]
        log.info("  -> %d ESG filings matched", len(esg_filings))

        if not esg_filings and not raw_filings:
            failures.append(
                {
                    "corp_code": corp_code,
                    "corp_name": corp_name,
                    "stock_code": stock_code,
                    "reason": "DART API returned no filings",
                }
            )

        for filing in esg_filings:
            rcept_no: str = filing.get("rcept_no", "")
            rcept_dt: str = filing.get("rcept_dt", "")
            report_nm: str = filing.get("report_nm", "")
            flr_nm: str = filing.get("flr_nm", "")

            # Derive year from rcept_dt (YYYYMMDD)
            year = rcept_dt[:4] if rcept_dt else ""

            dart_viewer_url = f"{DART_VIEWER_BASE}?rcpNo={rcept_no}" if rcept_no else ""

            # Try to get direct PDF
            direct_pdf_url = ""
            has_direct_pdf = False
            if rcept_no:
                direct_pdf_url = fetch_attach_pdf(rcept_no)
                has_direct_pdf = bool(direct_pdf_url)
                time.sleep(0.2)

            rows.append(
                {
                    "corp_code": corp_code,
                    "corp_name": corp_name,
                    "stock_code": stock_code,
                    "year": year,
                    "rcept_no": rcept_no,
                    "report_nm": report_nm,
                    "flr_nm": flr_nm,
                    "rcept_dt": rcept_dt,
                    "dart_viewer_url": dart_viewer_url,
                    "has_direct_pdf": has_direct_pdf,
                    "direct_pdf_url": direct_pdf_url,
                }
            )

        time.sleep(0.5)  # between firms

    # 2. Save results
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    log.info("Saved %d ESG filing rows -> %s", len(out_df), OUTPUT_CSV)

    if failures:
        fail_df = pd.DataFrame(failures)
        fail_df.to_csv(FAILURES_CSV, index=False, encoding="utf-8-sig")
        log.info("Saved %d failure records -> %s", len(failures), FAILURES_CSV)

    # 3. Print summary
    print("\n" + "=" * 60)
    print("DART ESG FILING DETECTION SUMMARY")
    print("=" * 60)
    print(f"Total ESG filings found : {len(out_df)}")
    if not out_df.empty:
        print(f"Firms with >=1 filing   : {out_df['corp_code'].nunique()}")
        direct_firms = out_df[out_df["has_direct_pdf"]]["corp_code"].nunique()
        print(f"Firms with direct PDF   : {direct_firms}")

        print("\nPer-firm filing counts:")
        counts = (
            out_df.groupby(["corp_name", "corp_code"])
            .size()
            .sort_values(ascending=False)
        )
        for (name, code), cnt in counts.items():
            pdf_cnt = out_df[
                (out_df["corp_code"] == code) & out_df["has_direct_pdf"]
            ].shape[0]
            print(f"  {name} ({code}): {cnt} filings, {pdf_cnt} with direct PDF")

    # Firms with zero ESG filings
    all_codes = set(gold_df["corp_code"])
    found_codes = set(out_df["corp_code"]) if not out_df.empty else set()
    zero_firms = gold_df[gold_df["corp_code"].isin(all_codes - found_codes)][
        ["corp_name", "corp_code", "stock_code"]
    ]
    if not zero_firms.empty:
        print("\nFirms with 0 DART ESG filings (IR-only path):")
        for _, row in zero_firms.iterrows():
            print(f"  {row['corp_name']} ({row['stock_code']})")
    print("=" * 60)


if __name__ == "__main__":
    main()
