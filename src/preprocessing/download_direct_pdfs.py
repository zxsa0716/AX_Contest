"""Download directly-accessible sustainability report PDFs from gold24_ir_download_guide.md.

Strategy: parse markdown tables from the guide, download each row with requests.
Saves to data/raw/sustainability_reports/{stock_code}/{YYYY}.pdf with SHA-256 logging.

Only downloads URLs that end with .pdf (direct links). Skip companies that require
Selenium/JS rendering (SK이노베이션, 롯데쇼핑, etc.).
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

import requests
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "report" / "gold24_ir_download_guide.md"
OUT_ROOT = ROOT / "data" / "raw" / "sustainability_reports"
LOG = OUT_ROOT / "_download_log.jsonl"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def parse_guide() -> list[dict]:
    """Parse markdown for [company section, year, URL] tuples."""
    text = GUIDE.read_text(encoding="utf-8")
    records = []
    sections = re.split(r"^## \d+\. ", text, flags=re.M)[1:]

    for sec in sections:
        name_match = re.match(r"(.+?) \((\d+)\)", sec)
        if not name_match:
            continue
        corp_name, stock_code = name_match.group(1).strip(), name_match.group(2)

        # Find URLs ending in .pdf with a year context
        for line in sec.splitlines():
            url_match = re.search(r"(https?://\S+?\.pdf)", line)
            if not url_match:
                continue
            url = url_match.group(1).rstrip(")")
            year_match = re.search(r"\b(2019|2020|2021|2022|2023)\b", line)
            if not year_match:
                continue
            year = int(year_match.group(1))
            records.append({
                "corp_name": corp_name,
                "stock_code": stock_code,
                "year": year,
                "url": url,
            })
    return records


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def download(rec: dict) -> dict:
    out_dir = OUT_ROOT / rec["stock_code"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{rec['year']}.pdf"
    if out.exists():
        return {**rec, "status": "cached", "path": str(out),
                "sha256": sha256(out.read_bytes()), "size": out.stat().st_size}
    try:
        r = requests.get(rec["url"], headers={"User-Agent": UA}, timeout=60,
                         allow_redirects=True, stream=True)
        r.raise_for_status()
        content = r.content
        if not content.startswith(b"%PDF") or len(content) < 10_000:
            return {**rec, "status": "not_pdf", "size": len(content)}
        out.write_bytes(content)
        return {**rec, "status": "ok", "path": str(out),
                "sha256": sha256(content), "size": len(content)}
    except Exception as e:
        return {**rec, "status": "error", "error": f"{type(e).__name__}: {str(e)[:200]}"}


def main() -> int:
    recs = parse_guide()
    # dedupe by (stock_code, year, url)
    seen = set()
    uniq = []
    for r in recs:
        key = (r["stock_code"], r["year"], r["url"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    print(f"Found {len(uniq)} unique direct PDF URLs")

    results = []
    for rec in tqdm(uniq, desc="download", ncols=100):
        res = download(rec)
        results.append(res)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
        if res["status"] == "ok":
            time.sleep(0.5)

    # summary
    from collections import Counter
    c = Counter(r["status"] for r in results)
    print(f"\nSummary: {dict(c)}")
    for r in results:
        icon = {"ok": "✓", "cached": "⊙", "not_pdf": "✗", "error": "✗"}.get(r["status"], "?")
        size = f"{r.get('size',0)//1024}KB" if "size" in r else ""
        print(f"  {icon} {r['stock_code']} {r['year']}: {r['status']} {size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
