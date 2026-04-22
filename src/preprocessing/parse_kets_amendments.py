"""
parse_kets_amendments.py — Parse K-ETS 할당계획 변경공고 documents

Handles three file types:
  .hwpx  — Unzip (XML), read Contents/section0.xml, extract text from <hp:t> elements
  .hwp   — Binary OLE format, read PrvText stream via olefile
  .pdf   — pdfplumber

Context on file contents
------------------------
These are mostly 유상할당 (paid allocation) auction plan announcements —
NOT firm-level allocation tables. The firm-level allocation data is already
captured in data/interim/kets_allocation_panel.parquet (from 사전할당 CSVs).

The HWP/HWPX/PDF files here provide:
  - 공고번호 (announcement number)
  - 계획기간 (planning period Phase 1-4)
  - 공고 날짜 (announcement date)
  - 변경사유 텍스트 (amendment rationale)
  - Occasionally: 업체별 조정 tables (rare — most are aggregate policy changes)

Outputs
-------
  data/interim/kets_amendments_index.csv
      Columns: file, 공고번호, 날짜, 계획기간, type, parse_method, parse_success,
               has_firm_table, fulltext_len
  data/interim/kets_firm_adjustments.csv
      Columns: corp_name, 공고번호, year, original_allocation, adjusted_allocation,
               reason, source_file
      (Populated only if firm-level tables found in documents)
  data/interim/kets_amendments_fulltext/
      One .txt per document for full-text search

Usage
-----
  python src/preprocessing/parse_kets_amendments.py [--input-dir "data/할당계획 변경공고"]
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
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

# Regex patterns
GONGGO_NO_RE = re.compile(
    r"(?:공고\s*제?|환경부공고|기후에너지환경부공고)\s*(20\d{2}-\d+호?)"
)
DATE_RE = re.compile(r"(20\d{2})년\s*(\d{1,2})월\s*(\d{1,2})일")
PHASE_RE = re.compile(r"제([1-4])차\s*계획기간")
YEAR_RE = re.compile(r"(20\d{2})년도?")

# Pattern for firm-level allocation tables (업체별 할당량)
# Typical format: 업체명 | 기존 | 변경 | 사유
FIRM_TABLE_RE = re.compile(
    r"([\w가-힣()\s]+?)\s+"
    r"([\d,]+(?:\.\d+)?)\s*(?:톤|tCO2|tCO₂)?\s+"
    r"([\d,]+(?:\.\d+)?)\s*(?:톤|tCO2|tCO₂)?"
)


# ─── HWPX parsing ────────────────────────────────────────────────────────────

def _extract_hwpx_namespaces(xml_content: bytes) -> dict:
    """Extract namespace map from HWPX XML."""
    ns = {}
    for match in re.finditer(r'xmlns:(\w+)="([^"]+)"', xml_content.decode("utf-8", errors="replace")):
        ns[match.group(1)] = match.group(2)
    return ns


def parse_hwpx(hwpx_path: Path) -> str:
    """Extract plain text from HWPX file (zip of XML files).

    Strategy:
      1. Read Preview/PrvText.txt (fastest, plain text preview)
      2. Fallback: parse Contents/section0.xml extracting <hp:t> text elements
    """
    try:
        with zipfile.ZipFile(str(hwpx_path)) as z:
            # Strategy 1: PrvText
            if "Preview/PrvText.txt" in z.namelist():
                with z.open("Preview/PrvText.txt") as f:
                    raw = f.read()
                    try:
                        return raw.decode("utf-8", errors="replace")
                    except Exception:
                        return raw.decode("utf-16-le", errors="replace")

            # Strategy 2: Parse section0.xml
            if "Contents/section0.xml" in z.namelist():
                with z.open("Contents/section0.xml") as f:
                    xml_bytes = f.read()

                # Parse XML with namespace handling
                # HWPX uses hp: namespace for paragraph/text elements
                xml_str = xml_bytes.decode("utf-8", errors="replace")

                # Remove namespace declarations for simpler parsing
                xml_clean = re.sub(r'\s+xmlns(?::\w+)?="[^"]+"', "", xml_str)
                xml_clean = re.sub(r"<(\w+):", "<", xml_clean)
                xml_clean = re.sub(r"</(\w+):", "</", xml_clean)

                root = ET.fromstring(xml_clean)
                texts = []
                for elem in root.iter():
                    if elem.tag in ("t", "p"):
                        if elem.text:
                            texts.append(elem.text)
                return "\n".join(texts)

    except zipfile.BadZipFile as exc:
        log.error("Bad zip file %s: %s", hwpx_path.name, exc)
    except ET.ParseError as exc:
        log.error("XML parse error %s: %s", hwpx_path.name, exc)
    except Exception as exc:
        log.error("HWPX parse error %s: %s", hwpx_path.name, exc)

    return ""


# ─── HWP parsing ─────────────────────────────────────────────────────────────

def parse_hwp(hwp_path: Path) -> str:
    """Extract plain text from HWP binary OLE file via PrvText stream."""
    if not OLEFILE_AVAILABLE:
        log.warning("olefile not available — skipping %s (requires manual transcription)", hwp_path.name)
        return ""

    try:
        if not olefile.isOleFile(str(hwp_path)):
            log.warning("%s is not a valid OLE file", hwp_path.name)
            return ""

        ole = olefile.OleFileIO(str(hwp_path))
        entries = ole.listdir()
        entry_names = ["/".join(e) for e in entries]

        # PrvText is the plain text preview — sufficient for metadata extraction
        if any("PrvText" in e for e in entry_names):
            raw = ole.openstream("PrvText").read()
            try:
                return raw.decode("utf-16-le", errors="replace")
            except Exception:
                return raw.decode("utf-8", errors="replace")

    except Exception as exc:
        log.error("HWP parse error %s: %s", hwp_path.name, exc)

    return ""


# ─── PDF parsing ──────────────────────────────────────────────────────────────

def parse_pdf(pdf_path: Path) -> str:
    """Extract full text from PDF using pdfplumber."""
    texts = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
    except Exception as exc:
        log.error("PDF parse error %s: %s", pdf_path.name, exc)
    return "\n".join(texts)


# ─── Metadata extraction ──────────────────────────────────────────────────────

def extract_metadata(text: str, fname: str) -> dict:
    """Extract 공고번호, date, planning phase from document text."""
    # 공고번호
    gonggo_no = ""
    m = GONGGO_NO_RE.search(text)
    if m:
        gonggo_no = m.group(1).strip()
    # also check filename
    if not gonggo_no:
        m2 = re.search(r"(20\d{2}-\d+호?)", fname)
        if m2:
            gonggo_no = m2.group(1)

    # Date
    date_str = ""
    m = DATE_RE.search(text)
    if m:
        date_str = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    # Planning phase
    phase = ""
    m = PHASE_RE.search(text)
    if m:
        phase = f"제{m.group(1)}차"

    # Year from filename or text
    year = None
    m = YEAR_RE.search(fname)
    if m:
        year = int(m.group(1))
    if year is None:
        m = YEAR_RE.search(text)
        if m:
            year = int(m.group(1))

    # Document type
    if "유상할당" in text or "경매" in text:
        doc_type = "유상할당"
    elif "변경" in text:
        doc_type = "할당계획변경"
    elif "공표" in text:
        doc_type = "할당계획공표"
    else:
        doc_type = "기타"

    return {
        "공고번호": gonggo_no,
        "날짜": date_str,
        "계획기간": phase,
        "year": year,
        "type": doc_type,
    }


def try_extract_firm_adjustments(text: str, gonggo_no: str, source_file: str) -> list[dict]:
    """Attempt to extract firm-level allocation adjustment records from text.

    These are extremely rare in the documents we have (which are mostly aggregate
    policy changes or auction parameters). Returns [] if none found.

    Looks for:
      - Tables with firm name + numeric allocation values
      - Text patterns like "A사: 기존 X톤 → 변경 Y톤"
    """
    rows = []

    # Pattern 1: Arrow notation "업체명 X톤 → Y톤"
    arrow_re = re.compile(
        r"([\w가-힣()\s]{2,20})\s*:\s*([\d,]+)\s*(?:톤|tCO2|tCO₂)\s*→\s*([\d,]+)"
    )
    for m in arrow_re.finditer(text):
        corp = m.group(1).strip()
        orig = float(m.group(2).replace(",", ""))
        adj = float(m.group(3).replace(",", ""))
        if corp and orig > 0:
            rows.append({
                "corp_name": corp,
                "공고번호": gonggo_no,
                "year": None,
                "original_allocation": orig,
                "adjusted_allocation": adj,
                "reason": "",
                "source_file": source_file,
            })

    # Pattern 2: Table rows with firm name + two allocation columns
    # This is a heuristic — only triggers if "업체별" appears in document
    if "업체별" in text or "업체명" in text:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            m = FIRM_TABLE_RE.search(line)
            if m:
                corp = m.group(1).strip()
                # Filter out obvious non-company strings
                if len(corp) < 2 or len(corp) > 30:
                    continue
                if any(kw in corp for kw in ["계획기간", "업체명", "할당량", "변경", "기존"]):
                    continue
                try:
                    orig = float(m.group(2).replace(",", ""))
                    adj = float(m.group(3).replace(",", ""))
                    rows.append({
                        "corp_name": corp,
                        "공고번호": gonggo_no,
                        "year": None,
                        "original_allocation": orig,
                        "adjusted_allocation": adj,
                        "reason": "",
                        "source_file": source_file,
                    })
                except ValueError:
                    pass

    return rows


# ─── Main ─────────────────────────────────────────────────────────────────────

def run(input_dir: str, out_dir: str) -> None:
    in_path = Path(input_dir)
    out_path = Path(out_dir)
    fulltext_dir = out_path / "kets_amendments_fulltext"
    fulltext_dir.mkdir(parents=True, exist_ok=True)

    index_rows: list[dict] = []
    firm_adj_rows: list[dict] = []

    files = sorted(in_path.iterdir())
    supported = {".hwpx", ".hwp", ".pdf"}

    for fpath in tqdm(files, desc="Parsing K-ETS amendments"):
        if fpath.suffix.lower() not in supported:
            continue

        log.info("Processing: %s", fpath.name)
        text = ""
        parse_method = "unknown"
        parse_success = False

        try:
            if fpath.suffix.lower() == ".hwpx":
                text = parse_hwpx(fpath)
                parse_method = "hwpx_prvtext"
                parse_success = len(text) > 50
            elif fpath.suffix.lower() == ".hwp":
                text = parse_hwp(fpath)
                parse_method = "hwp_olefile_prvtext"
                parse_success = len(text) > 50
                if not parse_success:
                    log.warning(
                        "%s: olefile PrvText failed or empty — requires manual transcription",
                        fpath.name,
                    )
            elif fpath.suffix.lower() == ".pdf":
                text = parse_pdf(fpath)
                parse_method = "pdfplumber"
                parse_success = len(text) > 50
        except Exception as exc:
            log.error("Fatal error parsing %s: %s", fpath.name, exc)
            text = ""

        # Save full text
        if text:
            txt_out = fulltext_dir / (fpath.stem + ".txt")
            txt_out.write_text(text, encoding="utf-8", errors="replace")

        # Extract metadata
        meta = extract_metadata(text, fpath.name) if text else {}

        # Try to extract firm-level adjustments
        firm_rows = []
        has_firm_table = False
        if text and parse_success:
            firm_rows = try_extract_firm_adjustments(
                text, meta.get("공고번호", ""), fpath.name
            )
            has_firm_table = len(firm_rows) > 0
            if has_firm_table:
                log.info("  -> Found %d firm adjustment records!", len(firm_rows))
                firm_adj_rows.extend(firm_rows)

        index_rows.append({
            "file": fpath.name,
            "공고번호": meta.get("공고번호", ""),
            "날짜": meta.get("날짜", ""),
            "계획기간": meta.get("계획기간", ""),
            "type": meta.get("type", ""),
            "parse_method": parse_method,
            "parse_success": parse_success,
            "has_firm_table": has_firm_table,
            "fulltext_len": len(text),
        })

        log.info(
            "  Method=%s success=%s len=%d gonggo=%s date=%s",
            parse_method, parse_success, len(text),
            meta.get("공고번호", "-"), meta.get("날짜", "-"),
        )

    # Save outputs
    index_df = pd.DataFrame(index_rows)
    index_out = out_path / "kets_amendments_index.csv"
    index_df.to_csv(index_out, index=False, encoding="utf-8")
    log.info("Saved index: %s (%d rows)", index_out, len(index_df))

    if firm_adj_rows:
        firm_df = pd.DataFrame(firm_adj_rows)
        firm_out = out_path / "kets_firm_adjustments.csv"
        firm_df.to_csv(firm_out, index=False, encoding="utf-8")
        log.info("Saved firm adjustments: %s (%d rows)", firm_out, len(firm_df))
        print("\n=== Firm-Level Adjustment Records (Supervised Labels) ===")
        print(firm_df.to_string(index=False))
    else:
        # Write empty with schema
        pd.DataFrame(columns=[
            "corp_name", "공고번호", "year", "original_allocation",
            "adjusted_allocation", "reason", "source_file",
        ]).to_csv(out_path / "kets_firm_adjustments.csv", index=False, encoding="utf-8")
        log.info(
            "No firm-level adjustment tables found. "
            "Documents are aggregate policy changes (유상할당 auction parameters). "
            "Firm-level GIR corrections → use data/interim/kets_allocation_panel.parquet "
            "from 사전할당 CSV files instead."
        )

    # Print summary
    print("\n=== K-ETS Amendment Parsing Summary ===")
    print(index_df[["file", "공고번호", "날짜", "계획기간", "type",
                     "parse_method", "parse_success", "fulltext_len"]].to_string(index=False))
    success_rate = index_df["parse_success"].mean() if len(index_df) > 0 else 0
    print(f"\nSuccess rate: {success_rate:.0%} ({index_df['parse_success'].sum()}/{len(index_df)})")
    print(f"Fulltext files saved to: {fulltext_dir}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Parse K-ETS 할당계획 변경공고 files")
    p.add_argument(
        "--input-dir",
        default="data/할당계획 변경공고",
        help="Directory with HWP/HWPX/PDF files",
    )
    p.add_argument("--out-dir", default="data/interim", help="Output directory")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input_dir, args.out_dir)
