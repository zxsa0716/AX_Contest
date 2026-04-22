"""
sustainability_report_parser.py — GRI 305-1 and ESG Scope Extractor from PDF Reports

Parses downloaded Korean sustainability reports (PDF format) for:
  1. GRI 305-1 Scope 1 emissions (tCO₂eq)
  2. GRI 305-2 Scope 2 (location vs market-based)
  3. GRI 305-3 Scope 3 (categories listed)
  4. Organizational boundary type (operational/financial/equity)
  5. Third-party assurance: present, provider, standard, level
  6. Reporting standard (GRI/IFRS S2/TCFD/KSSB)

Confidence flags:
  HIGH   — table extraction + unit match in same cell/row
  MEDIUM — regex extraction + unit found nearby (within 2 lines)
  LOW    — text search only, value found but no unit confirmation

Output: data/interim/esg_reports_parsed.csv
  One row per (corp_code, year, report_file)

Usage:
  python src/preprocessing/sustainability_report_parser.py \\
    --reports-dir data/raw/sustainability_reports \\
    --out data/interim/esg_reports_parsed.csv

  # Parse single file:
  python src/preprocessing/sustainability_report_parser.py \\
    --single path/to/report.pdf --corp-code 00126380 --year 2022
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import pdfplumber
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ─── Unit normalization ────────────────────────────────────────────────────────

UNIT_MULTIPLIERS = {
    # tCO2eq variants → tCO2eq (multiplier = 1)
    "tco2eq": 1.0,
    "tco2e": 1.0,
    "t-co2eq": 1.0,
    "t co2eq": 1.0,
    "톤co2": 1.0,
    "톤co2eq": 1.0,
    # 천tCO2eq → ×1,000
    "천tco2eq": 1_000.0,
    "천t-co2eq": 1_000.0,
    "천톤": 1_000.0,
    "ktco2eq": 1_000.0,
    "ktco2e": 1_000.0,
    # MtCO2eq → ×1,000,000
    "mtco2eq": 1_000_000.0,
    "mtco2e": 1_000_000.0,
    "백만톤": 1_000_000.0,
}

UNIT_RE = re.compile(
    r"(?:천\s*)?(?:[Mm]t|t|T|kt|KT)\s*-?\s*CO2\s*(?:eq|e|당량|eq\.|e\.)?",
    re.IGNORECASE,
)


def normalize_unit(raw_unit: str) -> tuple[float, str]:
    """Return (multiplier, canonical_unit_string) for a raw unit string."""
    key = raw_unit.lower().replace(" ", "").replace("₂", "2").replace("²", "2")
    for k, mult in UNIT_MULTIPLIERS.items():
        if k in key:
            return mult, "tCO2eq"
    return 1.0, raw_unit


def parse_number(s: str) -> Optional[float]:
    """Parse numeric string with Korean number formatting (commas, spaces)."""
    s = s.strip().replace(",", "").replace(" ", "").replace("\u2019", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


# ─── GRI 305-1 extraction ─────────────────────────────────────────────────────

# Scope 1 label patterns (Korean + English)
SCOPE1_LABELS = [
    r"scope\s*1",
    r"스코프\s*1",
    r"직접\s*배출[량]?",
    r"gri\s*305-1",
    r"gri\s*305\.1",
    r"scope\s*i\b",
]
SCOPE1_LABEL_RE = re.compile(
    "|".join(SCOPE1_LABELS),
    re.IGNORECASE,
)

# Number pattern: handles 1,234,567 or 1234567 or 1,234.56
NUMBER_RE = re.compile(r"[\d]{1,3}(?:[,\s]\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?")

# Exclusion patterns (avoid false positives like year numbers)
EXCLUDE_RE = re.compile(r"^(19|20)\d{2}$")


def extract_scope1_from_table(page) -> list[dict]:
    """Extract Scope 1 from pdfplumber table cells.

    Returns list of candidate dicts with value, unit, confidence.
    """
    candidates = []
    tables = page.extract_tables()
    for table in tables:
        if not table:
            continue
        for r_idx, row in enumerate(table):
            if not row:
                continue
            row_str = [str(c).strip() if c else "" for c in row]
            row_flat = " ".join(row_str)

            # Check if this row contains Scope 1 label
            if not SCOPE1_LABEL_RE.search(row_flat):
                continue

            # Search for numeric value in row and adjacent rows
            search_rows = [row_str]
            if r_idx + 1 < len(table) and table[r_idx + 1]:
                search_rows.append([str(c).strip() if c else "" for c in table[r_idx + 1]])

            for search_row in search_rows:
                for cell in search_row:
                    nums = NUMBER_RE.findall(cell.replace(",", ""))
                    unit_m = UNIT_RE.search(cell)
                    for num_str in nums:
                        if EXCLUDE_RE.match(num_str.replace(",", "")):
                            continue
                        val = parse_number(num_str)
                        if val is None or val <= 0:
                            continue
                        unit_raw = unit_m.group() if unit_m else ""
                        mult, unit_norm = normalize_unit(unit_raw)
                        confidence = "HIGH" if unit_m else "MEDIUM"
                        candidates.append({
                            "value_raw": val,
                            "unit_raw": unit_raw,
                            "unit_normalized": unit_norm,
                            "value_tco2eq": val * mult,
                            "confidence": confidence,
                            "extraction_method": "table",
                        })
    return candidates


def extract_scope1_from_text(text: str) -> list[dict]:
    """Extract Scope 1 from raw text using regex.

    Returns list of candidate dicts with value, unit, confidence.
    """
    candidates = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        if not SCOPE1_LABEL_RE.search(line):
            continue

        # Search for numbers in current line and next 3 lines
        window = "\n".join(lines[i : i + 4])
        unit_m = UNIT_RE.search(window)

        nums = NUMBER_RE.findall(window.replace(",", ""))
        for num_str in nums:
            if EXCLUDE_RE.match(num_str):
                continue
            val = parse_number(num_str)
            if val is None or val <= 0 or val > 1e11:
                continue
            unit_raw = unit_m.group() if unit_m else ""
            mult, unit_norm = normalize_unit(unit_raw)
            # Confidence: HIGH if unit in same line, MEDIUM if in window, LOW if absent
            if unit_m and UNIT_RE.search(line):
                confidence = "MEDIUM"  # text (not table) even with unit = MEDIUM
            elif unit_m:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            candidates.append({
                "value_raw": val,
                "unit_raw": unit_raw,
                "unit_normalized": unit_norm,
                "value_tco2eq": val * mult,
                "confidence": confidence,
                "extraction_method": "text_regex",
            })

    return candidates


def select_best_candidate(candidates: list[dict]) -> Optional[dict]:
    """Select the most likely correct Scope 1 value from candidates.

    Priority: HIGH > MEDIUM > LOW, then table > text.
    Among equal confidence, prefer values in plausible range (1,000–50,000,000 tCO2eq).
    """
    if not candidates:
        return None

    priority = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    method_priority = {"table": 0, "text_regex": 1}

    plausible = [
        c for c in candidates
        if 100 <= c["value_tco2eq"] <= 5e8  # 100 t to 500 Mt
    ]
    pool = plausible if plausible else candidates

    pool.sort(key=lambda c: (priority[c["confidence"]], method_priority.get(c["extraction_method"], 2)))
    return pool[0]


# ─── Scope 2 extraction ────────────────────────────────────────────────────────

SCOPE2_LABEL_RE = re.compile(r"scope\s*2|스코프\s*2|간접\s*배출|gri\s*305-?2", re.IGNORECASE)
LOCATION_RE = re.compile(r"location[\s-]*based|위치\s*기반|입지\s*기반", re.IGNORECASE)
MARKET_RE = re.compile(r"market[\s-]*based|시장\s*기반", re.IGNORECASE)


def extract_scope2(text: str, pages) -> dict:
    """Extract Scope 2 (location-based and market-based) values."""
    result = {
        "scope2_location_tco2eq": None,
        "scope2_market_tco2eq": None,
        "scope2_confidence": "LOW",
    }

    # Search text for location/market-based values
    for i, line in enumerate(text.split("\n")):
        if not SCOPE2_LABEL_RE.search(line):
            continue
        window = text.split("\n")[i : i + 4]
        window_text = "\n".join(window)

        nums = NUMBER_RE.findall(window_text.replace(",", ""))
        unit_m = UNIT_RE.search(window_text)
        unit_raw = unit_m.group() if unit_m else ""
        mult, _ = normalize_unit(unit_raw)

        # Check for location vs market based
        if LOCATION_RE.search(window_text):
            for num_str in nums:
                val = parse_number(num_str)
                if val and 0 < val < 5e8:
                    result["scope2_location_tco2eq"] = val * mult
                    result["scope2_confidence"] = "MEDIUM" if unit_m else "LOW"
                    break
        elif MARKET_RE.search(window_text):
            for num_str in nums:
                val = parse_number(num_str)
                if val and 0 < val < 5e8:
                    result["scope2_market_tco2eq"] = val * mult
                    result["scope2_confidence"] = "MEDIUM" if unit_m else "LOW"
                    break

    return result


# ─── Assurance extraction ─────────────────────────────────────────────────────

ASSURANCE_STD_RE = re.compile(
    r"isae\s*3410|isae\s*3000|aa1000as|aa1000|asae\s*3000",
    re.IGNORECASE,
)
REASONABLE_RE = re.compile(r"reasonable|합리적\s*확신|높은\s*수준", re.IGNORECASE)
LIMITED_RE = re.compile(r"limited|제한적\s*확신|낮은\s*수준", re.IGNORECASE)
ASSURANCE_PROVIDER_RE = re.compile(
    r"(?:검증|인증|assurance|verification)\s*기관\s*[:：]\s*([\w가-힣\(\)\s]+)",
    re.IGNORECASE,
)


def extract_assurance(text: str) -> dict:
    """Extract third-party assurance metadata."""
    result = {
        "third_party_assurance": False,
        "assurance_standard": "none",
        "assurance_level": "none",
        "assurance_provider": "none",
    }

    has_assurance = bool(ASSURANCE_STD_RE.search(text) or
                         re.search(r"검증\s*의견|assurance\s*statement|verification\s*statement", text, re.IGNORECASE))

    if not has_assurance:
        return result

    result["third_party_assurance"] = True

    std_m = ASSURANCE_STD_RE.search(text)
    if std_m:
        result["assurance_standard"] = std_m.group().upper().replace(" ", "")

    if REASONABLE_RE.search(text):
        result["assurance_level"] = "reasonable"
    elif LIMITED_RE.search(text):
        result["assurance_level"] = "limited"

    prov_m = ASSURANCE_PROVIDER_RE.search(text)
    if prov_m:
        result["assurance_provider"] = prov_m.group(1).strip()

    return result


# ─── Boundary extraction ──────────────────────────────────────────────────────

ORG_BOUNDARY_PATTERNS = {
    "operational_control": re.compile(r"operational\s*control|운영\s*통제", re.IGNORECASE),
    "financial_control": re.compile(r"financial\s*control|재무\s*통제", re.IGNORECASE),
    "equity_share": re.compile(r"equity\s*share|지분\s*비율", re.IGNORECASE),
}


def extract_boundary(text: str) -> str:
    for boundary_type, pattern in ORG_BOUNDARY_PATTERNS.items():
        if pattern.search(text):
            return boundary_type
    return "unspecified"


# ─── Reporting standard extraction ────────────────────────────────────────────

STANDARD_PATTERNS = {
    "GRI": re.compile(r"\bGRI\s*(?:Standards?|표준|준수)", re.IGNORECASE),
    "IFRS_S2": re.compile(r"IFRS\s*S2|KSSB\s*제2호", re.IGNORECASE),
    "TCFD": re.compile(r"\bTCFD\b", re.IGNORECASE),
    "KSSB": re.compile(r"KSSB|지속가능성\s*공시기준", re.IGNORECASE),
}


def extract_reporting_standard(text: str) -> str:
    found = []
    for std, pattern in STANDARD_PATTERNS.items():
        if pattern.search(text):
            found.append(std)
    if not found:
        return "none"
    if len(found) == 1:
        return found[0]
    return ",".join(found)


# ─── Main PDF parser ──────────────────────────────────────────────────────────

def parse_single_pdf(
    pdf_path: Path,
    corp_code: str,
    year: int,
) -> dict:
    """Parse one sustainability report PDF.

    Returns a dict with all extracted fields.
    """
    result = {
        "corp_code": corp_code,
        "year": year,
        "source_file": pdf_path.name,
        "n_pages": 0,
        # Scope 1
        "scope1_tco2eq": None,
        "scope1_unit_raw": None,
        "scope1_confidence": "LOW",
        # Scope 2
        "scope2_location_tco2eq": None,
        "scope2_market_tco2eq": None,
        "scope2_confidence": "LOW",
        # Scope 3
        "scope3_present": False,
        "scope3_categories_raw": None,
        # Boundary
        "organizational_boundary": "unspecified",
        # Standard
        "reporting_standard": "none",
        # Assurance
        "third_party_assurance": False,
        "assurance_standard": "none",
        "assurance_level": "none",
        "assurance_provider": "none",
        # Meta
        "parse_success": False,
        "parse_notes": "",
    }

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            result["n_pages"] = len(pdf.pages)
            full_text_parts = []
            scope1_candidates = []

            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                full_text_parts.append(page_text)

                # Table extraction (page by page for better precision)
                table_candidates = extract_scope1_from_table(page)
                scope1_candidates.extend(table_candidates)

                # Text regex extraction
                text_candidates = extract_scope1_from_text(page_text)
                scope1_candidates.extend(text_candidates)

            full_text = "\n".join(full_text_parts)

            # Select best Scope 1
            best = select_best_candidate(scope1_candidates)
            if best:
                result["scope1_tco2eq"] = best["value_tco2eq"]
                result["scope1_unit_raw"] = best["unit_raw"]
                result["scope1_confidence"] = best["confidence"]
                result["parse_success"] = True
            else:
                result["parse_notes"] = "scope1_not_found"

            # Scope 2
            scope2 = extract_scope2(full_text, pdf.pages)
            result.update(scope2)

            # Scope 3
            scope3_present = bool(re.search(r"scope\s*3|스코프\s*3|gri\s*305-?3", full_text, re.IGNORECASE))
            result["scope3_present"] = scope3_present
            if scope3_present:
                # Try to capture listed categories
                cats_m = re.findall(r"(?:category|카테고리|범주)\s*(\d+)", full_text, re.IGNORECASE)
                result["scope3_categories_raw"] = ",".join(sorted(set(cats_m))) if cats_m else "present_no_detail"

            # Boundary
            result["organizational_boundary"] = extract_boundary(full_text)

            # Reporting standard
            result["reporting_standard"] = extract_reporting_standard(full_text)

            # Assurance
            assurance = extract_assurance(full_text)
            result.update(assurance)

    except Exception as exc:
        log.error("Failed to parse %s: %s", pdf_path.name, exc)
        result["parse_notes"] = f"exception: {exc}"

    return result


# ─── Batch runner ─────────────────────────────────────────────────────────────

def run_batch(
    reports_dir: str,
    out_csv: str,
) -> pd.DataFrame:
    """Parse all PDFs under reports_dir/{stock_code}/{year}*.pdf.

    Directory structure expected:
        reports_dir/
          {stock_code}/
            {year}_{report_type}.pdf
    """
    base = Path(reports_dir)
    rows = []

    # Discover files
    pdf_files = list(base.rglob("*.pdf"))
    log.info("Found %d PDF files under %s", len(pdf_files), reports_dir)

    for pdf_path in tqdm(pdf_files, desc="Parsing reports"):
        # Try to infer corp_code/year from path
        parts = pdf_path.parts
        # Expected: .../{stock_code}/{year}_{type}.pdf
        stock_code_dir = pdf_path.parent.name if len(parts) > 1 else "unknown"
        year_match = re.search(r"(201[5-9]|202[0-9])", pdf_path.stem)
        year = int(year_match.group(1)) if year_match else 0

        log.info("Parsing: %s (corp=%s year=%d)", pdf_path.name, stock_code_dir, year)
        rec = parse_single_pdf(pdf_path, corp_code=stock_code_dir, year=year)
        rows.append(rec)

    df = pd.DataFrame(rows)
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    log.info("Saved: %s (%d rows)", out_path, len(df))

    # Print summary
    if len(df) > 0:
        success = df["parse_success"].sum()
        print(f"\n=== Parsing Summary ===")
        print(f"Files parsed: {len(df)}")
        print(f"Scope 1 extracted: {success} ({success/len(df):.0%})")
        conf_dist = df["scope1_confidence"].value_counts().to_dict()
        print(f"Confidence distribution: {conf_dist}")

    return df


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Parse sustainability report PDFs for GRI 305-1")
    p.add_argument(
        "--reports-dir",
        default="data/raw/sustainability_reports",
        help="Directory containing downloaded PDFs",
    )
    p.add_argument(
        "--out",
        default="data/interim/esg_reports_parsed.csv",
        help="Output CSV path",
    )
    p.add_argument("--single", help="Parse a single PDF file (for testing)")
    p.add_argument("--corp-code", default="unknown", help="Corp code for single file mode")
    p.add_argument("--year", type=int, default=0, help="Year for single file mode")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.single:
        pdf_path = Path(args.single)
        if not pdf_path.exists():
            print(f"File not found: {pdf_path}")
            sys.exit(1)
        rec = parse_single_pdf(pdf_path, args.corp_code, args.year)
        print("\n=== Parsed Result ===")
        for k, v in rec.items():
            print(f"  {k}: {v}")
    else:
        run_batch(args.reports_dir, args.out)
