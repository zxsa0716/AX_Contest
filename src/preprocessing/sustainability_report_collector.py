"""
sustainability_report_collector.py — Multi-source Korean Sustainability Report Downloader

Collects PDFs of 지속가능경영보고서 (sustainability/ESG reports) for a target list of
Korean listed companies over years 2019-2023.

Sources (with fallback):
  1. DART Open API — search '지속가능경영보고서등관련사항' filings → get attachment URLs
  2. KRX ESG Portal (esg.krx.co.kr) — scrape 지속가능경영보고서 download list
     (requires Selenium for JS-rendered pages)
  3. Company IR pages — future manual extension (logged as "ir_manual" source)

Download pipeline:
  - requests + 3x exponential retry
  - 1 req/sec rate limiting (configurable)
  - SHA-256 hash on download, deduplication check before download
  - Save to: data/raw/sustainability_reports/{stock_code}/{year}_{report_type}.pdf
  - Log to: data/raw/sustainability_reports/_download_log.jsonl
  - 5 concurrent threads max
  - Resume-safe: skip existing files by SHA-256 check

Note on DART "자율공시" structure:
  Many Korean companies file a 지속가능경영보고서 as a "자율공시" on DART where
  the actual PDF is attached as a supplementary file or hosted on the company website.
  DART's OpenAPI returns the main HTML document (a form disclosure) — the PDF must
  be found either in attach_doc_list OR by following links in the disclosure HTML.
  If no direct PDF is found, the URL field is populated with the DART viewer URL
  for manual download.

Usage:
  python src/preprocessing/sustainability_report_collector.py \\
    --targets data/interim/gold_corps.csv \\
    --years 2019-2023 \\
    --sources dart,krx,ir

  # Demo with single company:
  python src/preprocessing/sustainability_report_collector.py \\
    --corp-codes 00126380 \\
    --years 2022-2023 \\
    --sources dart
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

DART_API_KEY = os.environ.get("DART_API_KEY", "")
DART_BASE = "https://opendart.fss.or.kr/api"

SUSTAINABILITY_KEYWORDS = [
    "지속가능경영보고서",
    "지속가능성보고서",
    "ESG보고서",
    "사회책임경영보고서",
    "sustainability report",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AX-ESG-Research/1.0"
}


# ─── Utilities ────────────────────────────────────────────────────────────────

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_download_log(log_path: Path) -> dict[str, dict]:
    """Load existing download log as {sha256: record}."""
    records: dict[str, dict] = {}
    if log_path.exists():
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                        if rec.get("sha256"):
                            records[rec["sha256"]] = rec
                    except json.JSONDecodeError:
                        pass
    return records


def append_to_log(log_path: Path, record: dict) -> None:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def rate_limited_get(
    url: str,
    session: requests.Session,
    retries: int = 3,
    backoff: float = 2.0,
    timeout: int = 30,
    **kwargs,
) -> Optional[requests.Response]:
    """GET with exponential backoff retry."""
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=timeout, **kwargs)
            if r.status_code == 200:
                return r
            log.debug("HTTP %d for %s (attempt %d)", r.status_code, url, attempt + 1)
        except requests.RequestException as exc:
            log.debug("Request error %s: %s (attempt %d)", url, exc, attempt + 1)
        time.sleep(backoff * (2 ** attempt))
    return None


# ─── DART source ──────────────────────────────────────────────────────────────

def dart_find_sustainability_filings(
    corp_code: str,
    year: int,
    session: requests.Session,
) -> list[dict]:
    """Find DART filings related to sustainability reports for a given corp and year.

    Returns list of {rcept_no, report_nm, rcept_dt, dart_viewer_url}.
    """
    results = []
    # Search window: July of target year to June of following year
    # (companies typically publish ~6 months after fiscal year end)
    start_de = f"{year}0101"
    end_de = f"{year + 1}0630"

    url = f"{DART_BASE}/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": corp_code,
        "bgn_de": start_de,
        "end_de": end_de,
        "page_no": 1,
        "page_count": 100,
    }

    r = rate_limited_get(url, session, params=params)
    if not r:
        return results

    try:
        data = r.json()
    except Exception:
        return results

    if data.get("status") != "000":
        return results

    for item in data.get("list", []):
        nm = item.get("report_nm", "")
        if any(kw in nm for kw in SUSTAINABILITY_KEYWORDS):
            rcept_no = item.get("rcept_no", "")
            results.append({
                "rcept_no": rcept_no,
                "report_nm": nm,
                "rcept_dt": item.get("rcept_dt", ""),
                "dart_viewer_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
            })

    return results


def dart_get_attachment_url(
    rcept_no: str,
    dart_reader,
    session: requests.Session,
) -> Optional[str]:
    """Try to get direct PDF download URL from DART disclosure attachments.

    DART 자율공시 for sustainability reports often links to the company website,
    not a downloadable PDF on DART servers. We capture the link from the HTML.
    """
    try:
        doc_list = dart_reader.attach_doc_list(rcept_no)
        if doc_list is not None and len(doc_list) > 0:
            first_url = doc_list.iloc[0]["url"] if "url" in doc_list.columns else None
            if first_url and "dart.fss.or.kr" in str(first_url):
                # Try to get actual file URLs from the attachment page
                r = rate_limited_get(str(first_url), session)
                if r:
                    # Search for PDF link in response
                    pdf_links = re.findall(
                        r'https?://[^\s"\'<>]+\.pdf(?:\?[^\s"\'<>]+)?',
                        r.text,
                        re.IGNORECASE,
                    )
                    if pdf_links:
                        return pdf_links[0]
    except Exception as exc:
        log.debug("attach_doc_list error for %s: %s", rcept_no, exc)

    return None


def dart_download_disclosure_pdf(
    corp_code: str,
    stock_code: str,
    corp_name: str,
    year: int,
    out_base: Path,
    dart_reader,
    session: requests.Session,
    existing_sha256s: set,
    log_path: Path,
) -> Optional[dict]:
    """Download sustainability report PDF via DART for one corp+year.

    Returns log record dict or None if nothing found.
    """
    filings = dart_find_sustainability_filings(corp_code, year, session)
    if not filings:
        return None

    # Take most recent filing for this year
    filing = filings[0]
    rcept_no = filing["rcept_no"]

    # Try to get direct PDF URL
    pdf_url = dart_get_attachment_url(rcept_no, dart_reader, session)

    out_dir = out_base / (stock_code or corp_code)
    out_dir.mkdir(parents=True, exist_ok=True)

    if pdf_url:
        r = rate_limited_get(pdf_url, session, timeout=60)
        if r and r.headers.get("content-type", "").startswith("application/pdf"):
            content = r.content
            sha = sha256_bytes(content)
            if sha in existing_sha256s:
                log.info("Duplicate (sha256 match) — skipping: %s %d", corp_name, year)
                return None
            fname = out_dir / f"{year}_sustainability.pdf"
            fname.write_bytes(content)
            existing_sha256s.add(sha)
            record = {
                "corp_code": corp_code,
                "stock_code": stock_code,
                "corp_name": corp_name,
                "year": year,
                "rcept_no": rcept_no,
                "url": pdf_url,
                "local_path": str(fname),
                "sha256": sha,
                "size_bytes": len(content),
                "status": "downloaded",
                "source": "dart_attachment",
            }
            append_to_log(log_path, record)
            log.info("Downloaded: %s %d -> %s", corp_name, year, fname.name)
            return record

    # No direct PDF — record DART viewer URL for manual download
    record = {
        "corp_code": corp_code,
        "stock_code": stock_code,
        "corp_name": corp_name,
        "year": year,
        "rcept_no": rcept_no,
        "url": filing["dart_viewer_url"],
        "local_path": None,
        "sha256": None,
        "size_bytes": None,
        "status": "url_found_no_direct_pdf",
        "source": "dart_viewer",
        "report_nm": filing["report_nm"],
        "note": (
            "DART 자율공시 — PDF is on company IR site, not DART server. "
            "Visit dart_viewer_url to download manually."
        ),
    }
    append_to_log(log_path, record)
    log.info("DART filing found (no direct PDF): %s %d — %s", corp_name, year, filing["dart_viewer_url"])
    return record


# ─── KRX ESG source (Selenium) ────────────────────────────────────────────────

def krx_check_selenium_available() -> bool:
    """Check if Selenium + ChromeDriver are available."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=opts)
        driver.quit()
        return True
    except Exception as exc:
        log.debug("Selenium not available: %s", exc)
        return False


def krx_search_esg_reports(
    corp_name: str,
    years: list[int],
    session: requests.Session,
) -> list[dict]:
    """Search KRX ESG portal for sustainability report PDFs.

    KRX ESG portal: https://esg.krx.co.kr/
    The "지속가능경영보고서" section requires JS. We attempt both:
      1. Direct API endpoint (undocumented)
      2. Selenium scraping as fallback

    Returns list of {corp_name, year, pdf_url, source}.
    """
    results = []

    # Attempt 1: Undocumented KRX ESG API endpoint
    # Based on network inspection of esg.krx.co.kr
    api_url = "https://esg.krx.co.kr/contents/02/02010000/ESG02010000.jspx"
    params = {"searchText": corp_name, "pageNo": "1", "pageSize": "20"}
    try:
        r = rate_limited_get(api_url, session, params=params, timeout=10)
        if r and r.status_code == 200:
            # Parse response for PDF links
            pdf_links = re.findall(
                r'https?://[^\s"\'<>]+\.pdf(?:\?[^\s"\'<>]+)?',
                r.text,
                re.IGNORECASE,
            )
            for link in pdf_links:
                # Try to extract year from URL or filename
                y_match = re.search(r"(201[5-9]|202[0-9])", link)
                link_year = int(y_match.group(1)) if y_match else None
                if link_year in years or link_year is None:
                    results.append({
                        "corp_name": corp_name,
                        "year": link_year,
                        "pdf_url": link,
                        "source": "krx_api",
                    })
    except Exception as exc:
        log.debug("KRX API attempt failed for %s: %s", corp_name, exc)

    # Attempt 2: Selenium (if API failed and Selenium available)
    if not results:
        log.info("KRX API returned no results for %s. Selenium fallback would be needed.", corp_name)
        # Selenium implementation placeholder — requires manual ChromeDriver setup
        # See data/README.md for KRX ESG scraping setup instructions
        results.append({
            "corp_name": corp_name,
            "year": None,
            "pdf_url": f"https://esg.krx.co.kr/ (search: {corp_name})",
            "source": "krx_manual_required",
        })

    return results


# ─── Main collector ───────────────────────────────────────────────────────────

def _download_task(task: dict) -> dict:
    """Worker function for thread pool. Returns status dict."""
    import OpenDartReader as odr
    session = requests.Session()
    session.headers.update(HEADERS)
    dart_reader = odr(DART_API_KEY)

    corp_code = task["corp_code"]
    stock_code = task.get("stock_code", corp_code)
    corp_name = task.get("corp_name", corp_code)
    year = task["year"]
    out_base = task["out_base"]
    log_path = task["log_path"]
    existing_sha256s = task["existing_sha256s"]
    sources = task["sources"]

    result = {"corp_code": corp_code, "year": year, "status": "not_found"}

    time.sleep(1.0)  # rate limiting

    if "dart" in sources:
        rec = dart_download_disclosure_pdf(
            corp_code=corp_code,
            stock_code=stock_code,
            corp_name=corp_name,
            year=year,
            out_base=out_base,
            dart_reader=dart_reader,
            session=session,
            existing_sha256s=existing_sha256s,
            log_path=log_path,
        )
        if rec:
            result = rec
            result["source"] = "dart"
            return result

    if "krx" in sources:
        krx_results = krx_search_esg_reports(corp_name, [year], session)
        for kr in krx_results:
            if kr.get("pdf_url") and "manual_required" not in kr.get("source", ""):
                # Attempt download
                r = rate_limited_get(kr["pdf_url"], session, timeout=60)
                if r and "pdf" in r.headers.get("content-type", "").lower():
                    content = r.content
                    sha = sha256_bytes(content)
                    if sha not in existing_sha256s:
                        out_dir = out_base / stock_code
                        out_dir.mkdir(parents=True, exist_ok=True)
                        fname = out_dir / f"{year}_sustainability_krx.pdf"
                        fname.write_bytes(content)
                        existing_sha256s.add(sha)
                        rec = {
                            "corp_code": corp_code,
                            "stock_code": stock_code,
                            "corp_name": corp_name,
                            "year": year,
                            "url": kr["pdf_url"],
                            "local_path": str(fname),
                            "sha256": sha,
                            "size_bytes": len(content),
                            "status": "downloaded",
                            "source": "krx",
                        }
                        append_to_log(log_path, rec)
                        result = rec
                        return result

    return result


def run(
    corp_list: list[dict],
    years: list[int],
    sources: list[str],
    out_base_dir: str,
    max_workers: int = 5,
) -> pd.DataFrame:
    """Main collection runner.

    Args:
        corp_list: list of {corp_code, stock_code, corp_name}
        years: list of int years to collect
        sources: ['dart', 'krx', 'ir']
        out_base_dir: base directory for downloads
        max_workers: max concurrent downloads

    Returns:
        DataFrame of download log records
    """
    out_base = Path(out_base_dir)
    out_base.mkdir(parents=True, exist_ok=True)
    log_path = out_base / "_download_log.jsonl"

    # Load existing downloads
    existing_log = load_download_log(log_path)
    existing_sha256s: set[str] = set(existing_log.keys())
    log.info(
        "Starting collector: %d corps x %d years, sources=%s",
        len(corp_list), len(years), sources,
    )
    log.info("Existing downloads: %d", len(existing_sha256s))

    tasks = []
    for corp in corp_list:
        for year in years:
            # Check if already downloaded
            already_done = any(
                rec.get("corp_code") == corp.get("corp_code")
                and rec.get("year") == year
                and rec.get("status") == "downloaded"
                for rec in existing_log.values()
            )
            if already_done:
                log.info("Skip (already downloaded): %s %d", corp.get("corp_name"), year)
                continue

            tasks.append({
                "corp_code": corp["corp_code"],
                "stock_code": corp.get("stock_code", ""),
                "corp_name": corp.get("corp_name", ""),
                "year": year,
                "out_base": out_base,
                "log_path": log_path,
                "existing_sha256s": existing_sha256s,
                "sources": sources,
            })

    log.info("Tasks to execute: %d", len(tasks))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_download_task, t): t for t in tasks}
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc="Downloading reports",
        ):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                task = futures[future]
                log.error("Task failed %s %d: %s", task["corp_name"], task["year"], exc)
                results.append({
                    "corp_code": task["corp_code"],
                    "year": task["year"],
                    "status": "error",
                    "error": str(exc),
                })

    df = pd.DataFrame(results)
    log.info("\n=== Collection Summary ===")
    if len(df) > 0:
        print(df.groupby("status").size().to_string())
    return df


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Collect Korean sustainability reports from DART, KRX ESG, IR pages"
    )
    p.add_argument(
        "--targets",
        help="CSV with corp_code, stock_code, corp_name columns",
    )
    p.add_argument(
        "--corp-codes",
        help="Comma-separated corp_codes (alternative to --targets)",
    )
    p.add_argument("--years", default="2019-2023", help="Year range e.g. 2019-2023")
    p.add_argument(
        "--sources",
        default="dart,krx",
        help="Comma-separated sources: dart,krx,ir",
    )
    p.add_argument(
        "--out-dir",
        default="data/raw/sustainability_reports",
        help="Base output directory",
    )
    p.add_argument("--max-workers", type=int, default=5)
    return p.parse_args()


def parse_year_range(s: str) -> list[int]:
    s = s.strip()
    if "-" in s and "," not in s:
        parts = s.split("-")
        return list(range(int(parts[0]), int(parts[1]) + 1))
    return [int(y.strip()) for y in s.split(",")]


if __name__ == "__main__":
    args = parse_args()
    years = parse_year_range(args.years)
    sources = [s.strip() for s in args.sources.split(",")]

    corp_list: list[dict] = []

    if args.targets:
        df = pd.read_csv(args.targets)
        corp_list = df[["corp_code", "stock_code", "corp_name"]].to_dict("records")
    elif args.corp_codes:
        import OpenDartReader as odr
        dart = odr(DART_API_KEY)
        for cc in args.corp_codes.split(","):
            cc = cc.strip()
            try:
                info = dart.company(cc)
                corp_list.append({
                    "corp_code": cc,
                    "stock_code": info.get("stock_code", ""),
                    "corp_name": info.get("corp_name", cc),
                })
            except Exception:
                corp_list.append({"corp_code": cc, "stock_code": "", "corp_name": cc})
    else:
        print("Error: provide --targets or --corp-codes")
        sys.exit(1)

    if not DART_API_KEY:
        print("Error: DART_API_KEY not set in .env")
        sys.exit(1)

    df_result = run(
        corp_list=corp_list,
        years=years,
        sources=sources,
        out_base_dir=args.out_dir,
        max_workers=args.max_workers,
    )
    print(df_result.to_string(index=False) if len(df_result) > 0 else "No results.")
