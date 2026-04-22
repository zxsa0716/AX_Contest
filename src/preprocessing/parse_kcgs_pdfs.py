"""
parse_kcgs_pdfs.py — Parse KCGS (한국ESG기준원) ESG Grade PDFs and HWP files

Input directory: data/KCGS ESG 등급/
  - PDFs: annual announcement press releases (2017-2025)
  - HWP: 2022 announcement (binary old format)

Outputs
-------
  data/interim/kcgs_aggregate_distribution.csv
      Columns: year, category (통합/환경/사회/지배구조), grade, count
  data/interim/kcgs_company_grades.csv
      Columns: year, corp_name, overall_grade, E_grade, S_grade, G_grade,
               adjustment_reason, source_file
      Note: Individual company grades only available in quarterly adjustment releases.
  data/interim/kcgs_quarterly_adjustments.csv
      Columns: year, quarter, corp_name, E_before, E_after, S_before, S_after,
               G_before, G_after, overall_before, overall_after, reason, source_file

Usage
-----
  python src/preprocessing/parse_kcgs_pdfs.py [--input-dir data/KCGS\ ESG\ 등급]
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import pdfplumber
from tqdm import tqdm

try:
    import olefile
    OLEFILE_AVAILABLE = True
except ImportError:
    OLEFILE_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

GRADE_ORDER = ["S", "A+", "A", "B+", "B", "C", "D"]

# Patterns to extract year from filename or text
YEAR_FILENAME_RE = re.compile(r"(201[5-9]|202[0-9])")

# Regex for aggregate distribution tables in annual press releases
# e.g. "A+ 8사 (1.1%)"
GRADE_COUNT_RE = re.compile(
    r"([SABCDsabcd][+＋]?)\s+(\d+)사?\s*(?:\([\d.]+%\))?",
    re.UNICODE,
)

# Pattern for quarterly adjustment table rows
# e.g. "1 한화 B+ B+ A+ B+ B+ B+ A B+"
QUARTERLY_ROW_RE = re.compile(
    r"(\d+)\s+([\w가-힣\(\)（）.]+(?:\s+[\w가-힣]+)*)\s+"
    r"([SABCDsabcd][+＋]?)\s+([SABCDsabcd][+＋]?)\s+"
    r"([SABCDsabcd][+＋]?)\s+([SABCDsabcd][+＋]?)\s+"
    r"([SABCDsabcd][+＋]?)\s+([SABCDsabcd][+＋]?)\s+"
    r"([SABCDsabcd][+＋]?)\s+([SABCDsabcd][+＋]?)"
)


def extract_year_from_filename(fname: str) -> Optional[int]:
    m = YEAR_FILENAME_RE.search(fname)
    if m:
        return int(m.group(1))
    return None


def extract_year_from_text(text: str) -> Optional[int]:
    # Look for patterns like "2019년 ESG" or "2021년도"
    m = re.search(r"(201[5-9]|202[0-9])년", text)
    if m:
        return int(m.group(1))
    return None


def is_quarterly_adjustment(fname: str) -> bool:
    return "등급조정" in fname or "분기" in fname


def parse_aggregate_table(text: str, year: int, category: str) -> list[dict]:
    """Extract grade counts from aggregate distribution table text."""
    rows = []
    for m in GRADE_COUNT_RE.finditer(text):
        grade_raw = m.group(1).replace("＋", "+")
        count_str = m.group(2)
        grade = grade_raw.upper()
        if grade not in GRADE_ORDER:
            continue
        try:
            rows.append({
                "year": year,
                "category": category,
                "grade": grade,
                "count": int(count_str),
            })
        except ValueError:
            pass
    return rows


def parse_annual_pdf(pdf_path: Path, year: int) -> tuple[list[dict], list[dict]]:
    """Parse annual ESG grade announcement PDF.

    Returns (aggregate_rows, company_rows).
    Annual PDFs typically contain only aggregate distribution, not individual grades.
    """
    aggregate_rows: list[dict] = []
    company_rows: list[dict] = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""

                # Determine section context
                if "통합등급" in text or "ESG 통합" in text:
                    agg = parse_aggregate_table(text, year, "통합")
                    aggregate_rows.extend(agg)

                if "환경" in text and ("사회" in text or "지배구조" in text):
                    # Multi-category table — try to parse section by section
                    # Look for "환경", "사회", "지배구조" column headers
                    for cat_kr, cat_col in [("환경", "E"), ("사회", "S"), ("지배구조", "G"), ("금융 지배구조", "G_fin")]:
                        if cat_kr in text:
                            # Extract counts that appear after the category keyword
                            section = text[text.find(cat_kr):]
                            agg = parse_aggregate_table(section[:300], year, cat_col)
                            # Deduplicate by grade
                            existing_grades = {r["grade"] for r in aggregate_rows if r["category"] == cat_col}
                            for r in agg:
                                if r["grade"] not in existing_grades:
                                    aggregate_rows.append(r)

                # Try table extraction
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 3:
                        continue
                    # Check if this looks like an aggregate distribution table
                    header = [str(c).strip() if c else "" for c in table[0]]
                    if any(g in str(table) for g in ["A+", "B+", "S"]):
                        for row in table[1:]:
                            if not row or all(c is None or str(c).strip() == "" for c in row):
                                continue
                            row_str = [str(c).strip() if c else "" for c in row]
                            # Check for grade in first col
                            first = row_str[0] if row_str else ""
                            grade = first.replace("＋", "+").upper()
                            if grade in GRADE_ORDER:
                                # Try to parse counts from remaining cols
                                for i, val in enumerate(row_str[1:], 1):
                                    if re.match(r"^\d+$", val):
                                        cat_label = header[i] if i < len(header) else f"col_{i}"
                                        aggregate_rows.append({
                                            "year": year,
                                            "category": cat_label,
                                            "grade": grade,
                                            "count": int(val),
                                        })

    except Exception as exc:
        log.error("Failed to parse %s: %s", pdf_path.name, exc)

    # Deduplicate aggregate rows
    agg_df = pd.DataFrame(aggregate_rows) if aggregate_rows else pd.DataFrame()
    if not agg_df.empty:
        agg_df = agg_df.drop_duplicates(subset=["year", "category", "grade"])
        aggregate_rows = agg_df.to_dict("records")

    return aggregate_rows, company_rows


def parse_quarterly_pdf(pdf_path: Path, year: int) -> tuple[list[dict], list[dict]]:
    """Parse quarterly grade adjustment PDF.

    These contain individual company grade tables (before/after for E/S/G/통합).
    """
    aggregate_rows: list[dict] = []
    company_rows: list[dict] = []

    # Determine quarter from filename
    quarter = None
    q_match = re.search(r"([1-4])분기", pdf_path.name)
    if q_match:
        quarter = int(q_match.group(1))

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""

                # Try regex on raw text for table rows
                lines = text.split("\n")
                for line in lines:
                    # Pattern: "N 회사명 E_before E_after S_before S_after G_before G_after 통합_before 통합_after"
                    m = QUARTERLY_ROW_RE.match(line.strip())
                    if m:
                        company_rows.append({
                            "year": year,
                            "quarter": quarter,
                            "corp_name": m.group(2).strip(),
                            "E_before": m.group(3).replace("＋", "+"),
                            "E_after": m.group(4).replace("＋", "+"),
                            "S_before": m.group(5).replace("＋", "+"),
                            "S_after": m.group(6).replace("＋", "+"),
                            "G_before": m.group(7).replace("＋", "+"),
                            "G_after": m.group(8).replace("＋", "+"),
                            "overall_before": m.group(9).replace("＋", "+"),
                            "overall_after": m.group(10).replace("＋", "+"),
                            "reason": "",
                            "source_file": pdf_path.name,
                        })

                # Also try pdfplumber table extraction
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table[0] or []) < 8:
                        continue
                    for row in table:
                        if not row:
                            continue
                        row_clean = [str(c).strip().replace("＋", "+") if c else "" for c in row]
                        # Check: row has corp name + multiple grade columns
                        # Heuristic: at least 6 non-empty cells, some are valid grades
                        non_empty = [c for c in row_clean if c]
                        grade_cells = [c for c in row_clean if c in GRADE_ORDER]
                        if len(non_empty) >= 6 and len(grade_cells) >= 4:
                            # Try to extract: find corp name (not a grade, not a number)
                            corp_name_candidate = ""
                            grade_vals = []
                            for cell in row_clean:
                                if cell in GRADE_ORDER:
                                    grade_vals.append(cell)
                                elif cell and not cell.isdigit() and len(cell) > 1:
                                    if not corp_name_candidate:
                                        corp_name_candidate = cell
                            if corp_name_candidate and len(grade_vals) >= 4:
                                # Already captured by regex? dedup later
                                company_rows.append({
                                    "year": year,
                                    "quarter": quarter,
                                    "corp_name": corp_name_candidate,
                                    "E_before": grade_vals[0] if len(grade_vals) > 0 else "",
                                    "E_after": grade_vals[1] if len(grade_vals) > 1 else "",
                                    "S_before": grade_vals[2] if len(grade_vals) > 2 else "",
                                    "S_after": grade_vals[3] if len(grade_vals) > 3 else "",
                                    "G_before": grade_vals[4] if len(grade_vals) > 4 else "",
                                    "G_after": grade_vals[5] if len(grade_vals) > 5 else "",
                                    "overall_before": grade_vals[6] if len(grade_vals) > 6 else "",
                                    "overall_after": grade_vals[7] if len(grade_vals) > 7 else "",
                                    "reason": "",
                                    "source_file": pdf_path.name,
                                })

        # Add reason text via another pass
        if company_rows:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    full_text = " ".join(p.extract_text() or "" for p in pdf.pages)
                # For each company, find adjacent reason text
                for rec in company_rows:
                    corp = rec["corp_name"]
                    idx = full_text.find(corp)
                    if idx >= 0:
                        # Extract the portion after the company name (up to 300 chars)
                        snippet = full_text[idx : idx + 300]
                        reason_m = re.search(r"(?:쟁점사안|조정사유)[）\)]\s*([^\n]+)", snippet)
                        if reason_m:
                            rec["reason"] = reason_m.group(1).strip()
            except Exception:
                pass

    except Exception as exc:
        log.error("Failed to parse quarterly %s: %s", pdf_path.name, exc)

    # Deduplicate by (year, quarter, corp_name)
    if company_rows:
        df = pd.DataFrame(company_rows)
        df = df.drop_duplicates(subset=["year", "quarter", "corp_name", "overall_after"])
        company_rows = df.to_dict("records")

    return aggregate_rows, company_rows


def parse_hwp_file(hwp_path: Path, year: int) -> tuple[list[dict], list[dict]]:
    """Parse HWP binary format using olefile PrvText stream.

    HWP files here are annual announcement press releases.
    PrvText gives plain text preview — sufficient for aggregate distribution counts.
    """
    aggregate_rows: list[dict] = []
    company_rows: list[dict] = []

    if not OLEFILE_AVAILABLE:
        log.warning("olefile not installed — cannot parse %s", hwp_path.name)
        return aggregate_rows, company_rows

    try:
        if not olefile.isOleFile(str(hwp_path)):
            log.warning("%s is not a valid OLE file", hwp_path.name)
            return aggregate_rows, company_rows

        ole = olefile.OleFileIO(str(hwp_path))
        raw = ole.openstream("PrvText").read()
        # HWP PrvText uses UTF-16-LE
        try:
            text = raw.decode("utf-16-le", errors="replace")
        except Exception:
            text = raw.decode("utf-8", errors="replace")

        # Extract year from text if not known
        if year == 0:
            y = extract_year_from_text(text)
            if y:
                year = y

        # Parse aggregate (same logic as annual PDF)
        agg_rows, _ = parse_annual_pdf.__wrapped__(text, year) if hasattr(parse_annual_pdf, "__wrapped__") else ([], [])
        # Use direct text parsing
        agg = parse_aggregate_table(text, year, "통합")
        aggregate_rows.extend(agg)

    except Exception as exc:
        log.error("Failed to parse HWP %s: %s", hwp_path.name, exc)

    return aggregate_rows, company_rows


def run(input_dir: str, out_dir: str) -> None:
    """Main runner."""
    in_path = Path(input_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    all_aggregate: list[dict] = []
    all_company: list[dict] = []
    all_quarterly: list[dict] = []

    parse_log: list[dict] = []

    files = sorted(in_path.iterdir())
    for fpath in tqdm(files, desc="Parsing KCGS files"):
        if fpath.suffix.lower() not in (".pdf", ".hwp"):
            continue

        year = extract_year_from_filename(fpath.name) or 0
        is_quarterly = is_quarterly_adjustment(fpath.name)
        success = False

        log.info("Processing: %s (year=%s, quarterly=%s)", fpath.name, year, is_quarterly)

        try:
            if fpath.suffix.lower() == ".pdf":
                if is_quarterly:
                    agg, comp = parse_quarterly_pdf(fpath, year)
                    all_aggregate.extend(agg)
                    all_quarterly.extend(comp)
                    log.info("  -> %d company grade records extracted", len(comp))
                else:
                    agg, comp = parse_annual_pdf(fpath, year)
                    all_aggregate.extend(agg)
                    all_company.extend(comp)
                    log.info("  -> %d aggregate rows extracted", len(agg))
                success = True

            elif fpath.suffix.lower() == ".hwp":
                agg, comp = parse_hwp_file(fpath, year)
                all_aggregate.extend(agg)
                all_company.extend(comp)
                log.info("  -> %d aggregate rows from HWP", len(agg))
                success = len(agg) > 0 or len(comp) > 0

        except Exception as exc:
            log.error("Unhandled error for %s: %s", fpath.name, exc)

        parse_log.append({
            "file": fpath.name,
            "year": year,
            "is_quarterly": is_quarterly,
            "success": success,
        })

    # Save outputs
    # 1. Aggregate distribution
    if all_aggregate:
        agg_df = pd.DataFrame(all_aggregate)
        agg_df = agg_df.drop_duplicates(subset=["year", "category", "grade"])
        agg_df = agg_df.sort_values(["year", "category", "grade"])
        agg_out = out_path / "kcgs_aggregate_distribution.csv"
        agg_df.to_csv(agg_out, index=False, encoding="utf-8")
        log.info("Saved aggregate: %s (%d rows)", agg_out, len(agg_df))
    else:
        log.warning("No aggregate distribution rows extracted")

    # 2. Individual company grades (annual — usually empty from press releases)
    if all_company:
        comp_df = pd.DataFrame(all_company)
        comp_out = out_path / "kcgs_company_grades.csv"
        comp_df.to_csv(comp_out, index=False, encoding="utf-8")
        log.info("Saved company grades: %s (%d rows)", comp_out, len(comp_df))
    else:
        log.info("No individual company grades from annual PDFs (expected — check quarterly files)")
        # Write empty with schema
        pd.DataFrame(columns=["year", "corp_name", "overall_grade", "E_grade",
                               "S_grade", "G_grade", "adjustment_reason", "source_file"
                               ]).to_csv(out_path / "kcgs_company_grades.csv", index=False, encoding="utf-8")

    # 3. Quarterly adjustments
    if all_quarterly:
        q_df = pd.DataFrame(all_quarterly)
        q_out = out_path / "kcgs_quarterly_adjustments.csv"
        q_df.to_csv(q_out, index=False, encoding="utf-8")
        log.info("Saved quarterly adjustments: %s (%d rows)", q_out, len(q_df))
        print("\n=== Quarterly Adjustment Records ===")
        print(q_df[["year", "quarter", "corp_name", "overall_before",
                     "overall_after", "reason"]].to_string(index=False))
    else:
        log.warning("No quarterly adjustment records extracted")
        pd.DataFrame(columns=["year", "quarter", "corp_name", "E_before", "E_after",
                               "S_before", "S_after", "G_before", "G_after",
                               "overall_before", "overall_after", "reason", "source_file"
                               ]).to_csv(out_path / "kcgs_quarterly_adjustments.csv", index=False, encoding="utf-8")

    # Parse log summary
    log_df = pd.DataFrame(parse_log)
    print("\n=== Parsing Summary ===")
    print(log_df.to_string(index=False))
    success_rate = log_df["success"].mean() if len(log_df) > 0 else 0
    print(f"\nOverall success rate: {success_rate:.0%} ({log_df['success'].sum()}/{len(log_df)} files)")

    print(f"\nNote: Individual company grades are only in quarterly adjustment PDFs.")
    print("Annual press releases contain aggregate distributions only (no firm-level data).")
    print("HWP 2022 file: parsed via olefile PrvText stream.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Parse KCGS ESG grade PDFs")
    p.add_argument(
        "--input-dir",
        default="data/KCGS ESG 등급",
        help="Directory containing KCGS PDF/HWP files",
    )
    p.add_argument("--out-dir", default="data/interim", help="Output directory")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input_dir, args.out_dir)
