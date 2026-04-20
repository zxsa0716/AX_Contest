"""
scrape_kcgs.py
==============
Wave 1 / Part D — Scrape KCGS (한국ESG기준원, formerly 한국기업지배구조원)
ESG ratings 2019-2023 for all listed companies.

Note on data availability
--------------------------
- KCGS discloses ESG grades on its website at cgs.or.kr/business/esg_tab04.jsp
- The page is server-side rendered (JSP) but the grade data table is populated
  ONLY AFTER a user-type selection + consent click that is enforced via
  JavaScript (alert: "등급조회 사용자 유형을 선택해 주세요").
- A plain POST to esg_tab04.jsp returns the page shell but an empty data table.
  This was confirmed by live testing on 2026-04-17.
- CONCLUSION: Selenium with headless Chrome is REQUIRED to automate this source.
  The script below implements the POST approach (which will always hit the JS wall)
  and provides a complete Selenium fallback instruction.

CONFIRMED BLOCKER (2026-04-17): Plain POST returns HTML with empty <tbody>.
  The table contains only the header row and an "등급조회" placeholder cell.
  Grade data is injected by JavaScript after user consent.

IMPORTANT: KCGS terms of service prohibit commercial redistribution.
  This script collects data for non-commercial academic research only.
  Per KCGS usage policy, attribution is required:
  "출처: 한국ESG기준원(KCGS), [year]년 ESG 평가 결과"

Institutional note: KCGS was branded "한국기업지배구조원" until renamed in 2022.
  The acronym KCGS was retained; data continuity is unbroken.

Strategy
--------
1. Attempt paginated POST scraping of esg_tab04.jsp for years 2019-2023.
2. If the response is not parseable (JavaScript-rendered content or CAPTCHA
   detected), fall back to a fully-documented manual-download instruction.
3. Log every attempt to data/raw/download_log.json.
4. NEVER raise on per-record failure — log to data/interim/failures_kcgs.csv.

Output
------
data/interim/kcgs_esg_grades.csv
  Columns: year, corp_name, stock_code, overall_grade, E_grade, S_grade, G_grade

Usage
-----
    python src/preprocessing/scrape_kcgs.py [--years 2019 2020 2021 2022 2023]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
LOG_PATH = PROJECT_ROOT / "data" / "raw" / "download_log.json"
FAILURES_PATH = INTERIM_DIR / "failures_kcgs.csv"

# ---------------------------------------------------------------------------
# KCGS endpoints
# ---------------------------------------------------------------------------
KCGS_BASE = "https://www.cgs.or.kr"
KCGS_GRADE_URL = f"{KCGS_BASE}/business/esg_tab04.jsp"
KCGS_AJAX_URL = f"{KCGS_BASE}/business/esg_tab04.jsp"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": KCGS_GRADE_URL,
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}

# Grade scale: S > A+ > A > B+ > B > C > D
VALID_GRADES = {"S", "A+", "A", "B+", "B", "C", "D"}

# Number of results per page (KCGS default is typically 15 or 20)
PAGE_SIZE = 100  # request maximum to reduce round-trips


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_log() -> list:
    if LOG_PATH.exists():
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(entries: list) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def append_failure(record: dict) -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    write_header = not FAILURES_PATH.exists()
    with open(FAILURES_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(record)


def detect_js_wall(html: str) -> bool:
    """
    Return True if the response looks like a JavaScript-only page rather than
    actual table data. Heuristic: no <table> or <tr> with grade content.
    """
    lower = html.lower()
    return "<table" not in lower or "등급" not in lower


def parse_grade_table(html: str, year: int) -> list[dict]:
    """
    Parse the KCGS grade inquiry HTML table into a list of record dicts.

    KCGS table structure (as of 2024):
      <table>
        <thead><tr> 기업명 | 종목코드 | ESG등급 | E등급 | S등급 | G등급 | ... </tr></thead>
        <tbody><tr>...</tr> × N </tbody>
      </table>

    Returns list of dicts with keys:
      year, corp_name, stock_code, overall_grade, E_grade, S_grade, G_grade

    Returns empty list if table not found or parse fails.
    """
    try:
        # Use a minimal HTML parser to avoid BeautifulSoup dependency.
        # If BeautifulSoup is available, use it; otherwise fall back to regex.
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            tables = soup.find_all("table")
            if not tables:
                return []
            # Take the first table that contains grade-like data
            target_table = None
            for tbl in tables:
                text = tbl.get_text()
                if any(g in text for g in ("A+", "B+", "등급")):
                    target_table = tbl
                    break
            if not target_table:
                return []

            rows = target_table.find_all("tr")
            if len(rows) < 2:
                return []

            # Determine header column positions
            header_cells = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]

            # Map column names to indices
            col_map: dict[str, Optional[int]] = {
                "corp_name": None,
                "stock_code": None,
                "overall_grade": None,
                "E_grade": None,
                "S_grade": None,
                "G_grade": None,
            }
            for i, h in enumerate(header_cells):
                h_clean = h.replace(" ", "")
                if "기업명" in h_clean or "회사명" in h_clean:
                    col_map["corp_name"] = i
                elif "종목코드" in h_clean or "코드" in h_clean:
                    col_map["stock_code"] = i
                elif "ESG" in h_clean and "등급" in h_clean:
                    col_map["overall_grade"] = i
                elif h_clean.startswith("E") and "등급" in h_clean:
                    col_map["E_grade"] = i
                elif h_clean.startswith("S") and "등급" in h_clean:
                    col_map["S_grade"] = i
                elif h_clean.startswith("G") and "등급" in h_clean:
                    col_map["G_grade"] = i

            records = []
            for row in rows[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 3:
                    continue
                rec = {"year": year}
                for field, idx in col_map.items():
                    rec[field] = cells[idx] if idx is not None and idx < len(cells) else ""
                records.append(rec)
            return records

        except ImportError:
            # Fallback: no BeautifulSoup
            import re
            pattern = re.compile(
                r"<tr[^>]*>(.*?)</tr>", re.DOTALL | re.IGNORECASE
            )
            cell_pat = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL | re.IGNORECASE)
            tag_pat = re.compile(r"<[^>]+>")

            records = []
            rows_found = pattern.findall(html)
            for row_html in rows_found:
                cells = [
                    tag_pat.sub("", c).strip()
                    for c in cell_pat.findall(row_html)
                ]
                if len(cells) >= 4 and any(g in cells for g in VALID_GRADES):
                    rec = {
                        "year": year,
                        "corp_name": cells[0] if len(cells) > 0 else "",
                        "stock_code": cells[1] if len(cells) > 1 else "",
                        "overall_grade": cells[2] if len(cells) > 2 else "",
                        "E_grade": cells[3] if len(cells) > 3 else "",
                        "S_grade": cells[4] if len(cells) > 4 else "",
                        "G_grade": cells[5] if len(cells) > 5 else "",
                    }
                    records.append(rec)
            return records

    except Exception as exc:
        print(f"  [PARSE ERROR] year={year}: {exc}")
        return []


def scrape_year(
    session: requests.Session,
    year: int,
) -> tuple[list[dict], str]:
    """
    Scrape all ESG grades for a given year by paginating through the KCGS table.

    Returns (records, status) where status is "success" | "js_wall" | "failed".
    """
    all_records: list[dict] = []
    page = 1

    while True:
        post_data = {
            "searchYear": str(year),
            "searchGubun": "1",   # 1 = full ESG, 2 = E, 3 = S, 4 = G
            "searchGrade": "",    # blank = all grades
            "searchCorpNm": "",   # blank = all companies
            "pageIndex": str(page),
            "pageUnit": str(PAGE_SIZE),
        }

        try:
            resp = session.post(
                KCGS_AJAX_URL,
                data=post_data,
                timeout=30,
            )
            resp.raise_for_status()
            html = resp.text

        except requests.exceptions.RequestException as exc:
            print(f"  [HTTP ERROR] year={year} page={page}: {exc}")
            return all_records, "failed"

        if detect_js_wall(html):
            print(
                f"  [JS WALL] year={year} page={page}: "
                "Response does not contain expected table HTML. "
                "The page likely requires JavaScript rendering (Selenium needed)."
            )
            return all_records, "js_wall"

        page_records = parse_grade_table(html, year)

        if not page_records:
            # Empty page = end of pagination
            break

        all_records.extend(page_records)

        # If we got fewer records than PAGE_SIZE, this is the last page
        if len(page_records) < PAGE_SIZE:
            break

        page += 1
        time.sleep(0.5)  # respectful crawl delay

    return all_records, "success"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(years: list[int]) -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    log_entries = load_log()
    all_records: list[dict] = []
    js_wall_years: list[int] = []

    # First, load the home page to establish session cookies
    try:
        session.get(KCGS_GRADE_URL, timeout=15)
        time.sleep(0.5)
    except Exception as exc:
        print(f"[WARN] Could not load KCGS home page: {exc}")

    print("Scraping KCGS ESG grades...")
    for year in tqdm(years, desc="KCGS years"):
        records, status = scrape_year(session, year)

        if status == "js_wall":
            js_wall_years.append(year)
            log_entries.append({
                "dataset_id": "kcgs_esg",
                "name": f"KCGS ESG grades {year}",
                "target_path": str(INTERIM_DIR / "kcgs_esg_grades.csv"),
                "url": KCGS_GRADE_URL,
                "status": "manual_required",
                "sha256": None,
                "error": "JS wall detected — Selenium required for full scrape",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
            append_failure({
                "year": year,
                "reason": "js_wall",
                "url": KCGS_GRADE_URL,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
        elif status == "failed":
            js_wall_years.append(year)
            log_entries.append({
                "dataset_id": "kcgs_esg",
                "name": f"KCGS ESG grades {year}",
                "target_path": str(INTERIM_DIR / "kcgs_esg_grades.csv"),
                "url": KCGS_GRADE_URL,
                "status": "failed",
                "sha256": None,
                "error": "HTTP request failed",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
            append_failure({
                "year": year,
                "reason": "http_failed",
                "url": KCGS_GRADE_URL,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })
        else:
            all_records.extend(records)
            print(f"  [OK] {year}: {len(records)} records")
            log_entries.append({
                "dataset_id": "kcgs_esg",
                "name": f"KCGS ESG grades {year}",
                "target_path": str(INTERIM_DIR / "kcgs_esg_grades.csv"),
                "url": KCGS_GRADE_URL,
                "status": "success" if records else "empty",
                "sha256": None,
                "error": None if records else "Parsed 0 records — possible schema change",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })

        time.sleep(1)

    # Save whatever we collected
    if all_records:
        import pandas as pd
        df = pd.DataFrame(all_records)

        # Ensure all required columns exist
        for col in ["year", "corp_name", "stock_code", "overall_grade",
                    "E_grade", "S_grade", "G_grade"]:
            if col not in df.columns:
                df[col] = ""

        # Standardize grade values
        for col in ["overall_grade", "E_grade", "S_grade", "G_grade"]:
            df[col] = df[col].str.strip()

        out_path = INTERIM_DIR / "kcgs_esg_grades.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
        print(
            f"\n[SAVED] {out_path}  rows={len(df)}  "
            f"years={sorted(df['year'].unique().tolist())}  "
            f"sha256={sha[:16]}…"
        )
    else:
        print("\n[WARN] No KCGS records collected.")

    save_log(log_entries)
    print(f"Log saved: {LOG_PATH}")
    if FAILURES_PATH.exists():
        print(f"Failures log: {FAILURES_PATH}")

    if js_wall_years:
        print(
            f"\nMANUAL DOWNLOAD REQUIRED for years: {js_wall_years}\n"
            "\nBackground:\n"
            "  The KCGS grade inquiry page at https://www.cgs.or.kr/business/esg_tab04.jsp\n"
            "  renders its data table via JavaScript (JSP + AJAX). A plain POST request\n"
            "  returns the page shell without table data. Selenium with a headless Chrome\n"
            "  driver is required to execute the JavaScript and extract the rendered table.\n"
            "\nOption A — Selenium (recommended):\n"
            "  pip install selenium webdriver-manager\n"
            "  from selenium import webdriver\n"
            "  from selenium.webdriver.chrome.service import Service\n"
            "  from webdriver_manager.chrome import ChromeDriverManager\n"
            "  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))\n"
            "  driver.get('https://www.cgs.or.kr/business/esg_tab04.jsp')\n"
            "  # Then interact with the year dropdown and paginate.\n"
            "\nOption B — KCGS press releases (available on website):\n"
            "  KCGS publishes annual ESG evaluation result press releases (보도자료) at\n"
            "  https://www.cgs.or.kr/news/press_list.jsp\n"
            "  These PDFs contain the full grade tables for each evaluation year.\n"
            "  PDF parsing with pdfplumber is feasible for this format.\n"
            "\nOption C — Manual CSV export:\n"
            "  On the grade inquiry page, use the Excel/CSV export button (if present).\n"
            "  Save to: data/interim/kcgs_esg_grades_YYYY.csv per year.\n"
            "  Then merge: pd.concat([pd.read_csv(f) for f in ...]).to_csv(...)\n"
            "\nIf KCGS data remains unavailable via Options A-C, consider:\n"
            "  - Korea Stock Exchange (KRX ESG 통합공시) for overlapping E/S/G fields.\n"
            "  - DART 사업보고서 내 ESG 등급 언급 (ad hoc, lower coverage)."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape KCGS ESG grades")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2019, 2020, 2021, 2022, 2023],
        help="Years to scrape (default: 2019-2023)",
    )
    args = parser.parse_args()
    main(years=args.years)
