"""Auto-classify root sustainability_reports PDFs by peeking first 2 pages.

Strategy:
1. For each root-level PDF, read first 2 pages of text
2. Match against company identification keywords (by stock_code)
3. Extract year from filename + text content (heuristic)
4. Move to correct folder

Handles ambiguous names like '지속가능경영보고서.pdf', 'Report_ko.pdf', UUIDs.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "sustainability_reports"
LOG = ROOT / "_download_log.jsonl"

# Company identification: regex patterns in PDF text → stock_code
COMPANY_PATTERNS = [
    # Strong signals (unique company names)
    (r"POSCO\s*HOLDINGS|포스코\s*홀딩스|POSCOHOLDINGS", "005490"),
    (r"POSCO\b(?!\s*HOLDINGS)(?!필바라)", "005490"),  # legacy POSCO → POSCO Holdings
    (r"Samsung\s*Electronics|삼성전자\b", "005930"),
    (r"Samsung\s*C\s*&\s*T|삼성물산", "028260"),
    (r"Samsung\s*Life|삼성생명", "032830"),
    (r"SK\s*hynix|SK하이닉스|에스케이하이닉스", "000660"),
    (r"SK\s*Innovation|SK이노베이션", "096770"),
    (r"LG\s*Display|LGD|엘지디스플레이", "034220"),
    (r"LG\s*Energy\s*Solution|LG엔솔|엘지에너지솔루션", "373220"),
    (r"Hyundai\s*Motor\b|현대자동차", "005380"),
    (r"Hyundai\s*Mobis|현대모비스", "012330"),
    (r"Hyundai\s*Steel|현대제철|HyundaiSteel", "004020"),
    (r"Korean\s*Air|대한항공", "003490"),
    (r"Doosan\s*Corporation|두산\b", "000150"),
    (r"Lotte\s*Shopping|롯데쇼핑|LOTTE\s*SHOPPING", "023530"),
    (r"Lotte\s*Chemical|롯데케미칼|LOTTE\s*CHEMICAL", "011170"),
    (r"KT\s*Corporation|주식회사\s*케이티|\(주\)\s*케이티|KT\b.*ESG", "030200"),
    (r"CJ\s*CheilJedang|CJ제일제당", "097950"),
    (r"KEPCO|한국전력공사|Korea\s*Electric\s*Power", "015760"),
    (r"NAVER\b|네이버\s*(주)?", "035420"),
    (r"IBK|중소기업은행|Industrial\s*Bank\s*of\s*Korea", "024110"),
    (r"Hanwha\s*Corporation|\(주\)한화|㈜한화|^한화\s", "000880"),
    (r"Hanwha\s*Solutions|한화솔루션|HPC\b|Hanwha\s*Chemical|한화케미칼", "009830"),
    (r"Emart|이마트|emart", "139480"),
]


def peek(pdf_path: Path, n_pages: int = 2) -> str:
    """Read first n_pages text."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join((pdf.pages[i].extract_text() or "") for i in range(min(n_pages, len(pdf.pages))))
    except Exception as e:
        return ""


def detect_company(text: str, filename: str) -> str | None:
    """Return stock_code or None."""
    combined = f"{filename}\n{text}"
    for pat, code in COMPANY_PATTERNS:
        if re.search(pat, combined, re.IGNORECASE):
            return code
    return None


def detect_year(text: str, filename: str) -> int | None:
    """Year from filename (preferred) or first-page title."""
    # Filename YYYY
    m = re.search(r"(?<!\d)(20\d{2})(?!\d)", filename)
    if m:
        year = int(m.group(1))
        if 2015 <= year <= 2026:
            return year
    # Text search — first "20XX" in title-like area
    head = text[:2000]
    years = re.findall(r"(?<!\d)(20\d{2})(?!\d)", head)
    years = [int(y) for y in years if 2015 <= int(y) <= 2026]
    if years:
        from collections import Counter
        # Most common year in header (reporting year)
        return Counter(years).most_common(1)[0][0]
    return None


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    root_pdfs = [f for f in ROOT.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
    print(f"Root PDFs to classify: {len(root_pdfs)}\n")

    moved = []
    skipped_dup = []
    unknown = []

    for src in root_pdfs:
        text = peek(src, 2)
        code = detect_company(text, src.name)
        year = detect_year(text, src.name)

        if code is None or year is None:
            unknown.append((src.name, code, year))
            print(f"  [?] {src.name}: code={code}, year={year}")
            continue

        target = ROOT / code / f"{year}.pdf"
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            tgt_sz = target.stat().st_size
            src_sz = src.stat().st_size
            if tgt_sz >= src_sz:
                skipped_dup.append(f"{src.name} → {code}/{year}.pdf (existing {tgt_sz:,} ≥ new {src_sz:,})")
                src.unlink()
                continue
            target.unlink()  # replace with larger

        shutil.move(str(src), str(target))
        sha = sha256(target)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "stock_code": code, "year": year, "source_file": src.name,
                "path": str(target), "sha256": sha, "size": target.stat().st_size,
                "status": "auto_classified"
            }, ensure_ascii=False) + "\n")
        moved.append(f"{src.name[:60]:60} → {code}/{year}.pdf ({target.stat().st_size // 1024} KB)")

    print(f"\n=== MOVED ({len(moved)}) ===")
    for m in moved:
        print(f"  {m}")
    print(f"\n=== SKIPPED DUPLICATE ({len(skipped_dup)}) ===")
    for s in skipped_dup:
        print(f"  {s}")
    if unknown:
        print(f"\n=== UNCLASSIFIED ({len(unknown)}) — manual review ===")
        for name, code, year in unknown:
            print(f"  {name}  (code={code}, year={year})")


if __name__ == "__main__":
    main()
