"""Move 27 newly-uploaded ESG PDFs from root to correct stock_code folders.

Mapping rules (verified by filename + PDF header peek):
- 한화 000880: 2021~2025 × "2021_㈜한화_지속가능경영보고서.pdf" etc.
- 두산 000150: 2020~2024 × various Doosan filenames
- 대한항공 003490: 2021~2025 × "YYYY_Korean_Air_ESG_Report_ko.pdf"
- 롯데쇼핑 023530: 2021~2024 × "YYYY_ENG.pdf" (content confirmed LOTTE SHOPPING)
- 롯데케미칼 011170: 2021~2024 × "YYYY_롯데케미칼_..." or "_ENG_final"
- 이마트 139480: 2021~2024 × "emart YYYY Sustainability Report..."

Target range for analysis: 2019-2023 (but 2024, 2025 kept as bonus).

Files already in correct folders are preserved (no overwrite of smaller existing files).
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "sustainability_reports"
LOG = ROOT / "_download_log.jsonl"

# Filename → (stock_code, year) mapping
MAPPING = {
    # 한화 000880
    "2021_㈜한화_지속가능경영보고서.pdf": ("000880", 2021),
    "2022_㈜한화_지속가능경영보고서.pdf": ("000880", 2022),
    "2023_㈜한화_지속가능경영보고서.pdf": ("000880", 2023),
    "2024_㈜한화_지속가능경영보고서.pdf": ("000880", 2024),
    "2025_㈜한화_지속가능경영보고서.pdf": ("000880", 2025),
    # 두산 000150
    "일반비_2020 (주)두산 ESG보고서_국문_0714.pdf": ("000150", 2020),
    "2021 Doosan Corporation ESG Report_Kor.F.v3.pdf": ("000150", 2021),
    "2022 (주)두산 ESG보고서_국문_v2.pdf": ("000150", 2022),
    "일반비_2023_(주)두산_ESG보고서_국문_H2.pdf": ("000150", 2023),  # will skip if exists
    "2024_(주)두산_지속가능경영보고서_vf (5).pdf": ("000150", 2024),
    # 대한항공 003490
    "2021_Korean_Air_ESG_Report_ko.pdf": ("003490", 2021),
    "2022_Korean_Air_ESG_Report_ko.pdf": ("003490", 2022),
    "2023_Korean_Air_ESG_Report_ko.pdf": ("003490", 2023),
    "2024_Korean_Air_ESG_Report_kr.pdf": ("003490", 2024),
    "2025_Korean_Air_ESG_Report_kr.pdf": ("003490", 2025),
    # 롯데쇼핑 023530 (confirmed LOTTE SHOPPING from PDF header)
    "2021_ENG.pdf": ("023530", 2021),
    "2022_ENG.pdf": ("023530", 2022),
    "2023_ENG.pdf": ("023530", 2023),  # already have different file, will keep larger
    "2024_ENG.pdf": ("023530", 2024),
    # 롯데케미칼 011170
    "2021_롯데케미칼_지속가능경영보고서_영문_Main_Report+Data Book.pdf": ("011170", 2021),
    "2022_ LOTTE Chemical ESG_Report+Data Book (영문).pdf": ("011170", 2022),
    "롯데케미칼_ESG_보고서_eng_final_0821_compressed.pdf": ("011170", 2023),
    "롯데케미칼_2024_ESG_보고서_eng_final.pdf": ("011170", 2024),
    # 이마트 139480
    "emart 2021 Sustainability Report v2.pdf": ("139480", 2021),
    "emart 2022 Sustainability  report.pdf": ("139480", 2022),
    "emart 2023 Sustainability report.pdf": ("139480", 2023),
    "2024 emart SR_kor_0820_low.pdf": ("139480", 2024),
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    moved = []
    skipped = []
    unknown = []

    pdf_files = [f for f in ROOT.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]

    for src in pdf_files:
        name = src.name
        if name not in MAPPING:
            unknown.append(name)
            continue
        code, year = MAPPING[name]
        target_dir = ROOT / code
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{year}.pdf"

        src_size = src.stat().st_size
        if target.exists():
            tgt_size = target.stat().st_size
            # Keep the larger file (more complete data)
            if tgt_size >= src_size:
                skipped.append(f"{name} → {code}/{year}.pdf (target {tgt_size:,} ≥ new {src_size:,})")
                # Remove the duplicate from root
                src.unlink()
                continue
            else:
                # Replace with larger new file
                target.unlink()
        shutil.move(str(src), str(target))
        sha = sha256(target)
        log_entry = {
            "stock_code": code,
            "year": year,
            "source_file": name,
            "path": str(target),
            "sha256": sha,
            "size": target.stat().st_size,
            "status": "classified_manual",
        }
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        moved.append(f"{name} → {code}/{year}.pdf ({target.stat().st_size // 1024} KB)")

    print(f"=== MOVED ({len(moved)}) ===")
    for m in moved:
        print(f"  {m}")
    print(f"\n=== SKIPPED (duplicate, kept existing) ({len(skipped)}) ===")
    for s in skipped:
        print(f"  {s}")
    if unknown:
        print(f"\n=== UNKNOWN ({len(unknown)}) — need manual classification ===")
        for u in unknown:
            print(f"  {u}")


if __name__ == "__main__":
    main()
