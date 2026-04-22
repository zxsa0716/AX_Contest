"""ODIAC v2024 bulk download-and-clip wrapper (download-only phase).

Downloads all 60 monthly GeoTIFFs for 2019-01 to 2023-12 and clips each to
the Korea bounding box. Does NOT compute zonal statistics — that step runs
separately after gold_sites.csv is ready (takes ~10 min with cached rasters).

URL pattern:
  https://db.cger.nies.go.jp/nies_data/10.17595/20170411.001/
  odiac2024/1km_tiff/{YYYY}/odiac2024_1km_excl_intl_{YYMM}.tif.gz

Disk estimate: ~15 GB raw .tif + ~1 GB clipped KR .tif
Expected wall time: ~60 min at NIES throttle (~60 s/file including gunzip+clip)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Allow importing from parent package without installing
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.satellite.extract_odiac import download_month, clip_to_korea, _months, RAW_DIR, CACHE_DIR

START = "2019-01-01"
END   = "2023-12-31"


def main() -> int:
    months = _months(START, END)
    print(f"[odiac_bulk] Downloading {len(months)} months ({START} to {END})")
    print(f"[odiac_bulk] RAW_DIR  : {RAW_DIR}")
    print(f"[odiac_bulk] CACHE_DIR: {CACHE_DIR}")
    print()

    ok = 0
    skip = 0
    fail = 0

    for yr, mo in months:
        yymm = f"{yr % 100:02d}{mo:02d}"
        clip_path = CACHE_DIR / f"odiac2024_1km_excl_intl_{yymm}_KR.tif"

        if clip_path.exists():
            print(f"[skip] {yr}-{mo:02d} already clipped: {clip_path.name}")
            skip += 1
            continue

        try:
            print(f"[download] {yr}-{mo:02d} ...", flush=True)
            tif = download_month(yr, mo)
            print(f"[clip]     {yr}-{mo:02d} ...", flush=True)
            clipped = clip_to_korea(tif)
            print(f"[done]     {yr}-{mo:02d} -> {clipped.name}")
            ok += 1
            # NIES server is polite-crawl sensitive — 2 s cooldown between files
            time.sleep(2)
        except Exception as exc:
            print(f"[ERROR]    {yr}-{mo:02d}: {exc}", flush=True)
            fail += 1
            # back off on error
            time.sleep(10)

    print()
    print(f"[odiac_bulk] done — ok={ok}, skipped={skip}, failed={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
