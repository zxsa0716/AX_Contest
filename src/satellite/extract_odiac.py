"""ODIAC v2024 CO2 monthly 1 km fossil-fuel emissions extraction for site buffers.

Flow:
  1. Download monthly GeoTIFF .tif.gz from NIES for 2019-01..2023-12 (60 files).
  2. Decompress, clip to Korea bbox [124, 33, 132, 39], cache locally.
  3. For each site x month, buffer 10 km, compute sum / mean / max tC/month.

URL pattern (verified 2026-04):
  https://db.cger.nies.go.jp/nies_data/10.17595/20170411.001/odiac2024/1km_tiff/{YYYY}/odiac2024_1km_excl_intl_{YYMM}.tif.gz

Units: native = tC per 1km grid cell per month.
"""
from __future__ import annotations

import os
import sys
import gzip
import shutil
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

import rasterio
from rasterio.windows import from_bounds
from rasterio.mask import mask as rio_mask
from shapely.geometry import Point, mapping, Polygon
from pyproj import Transformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR      = PROJECT_ROOT / "data" / "raw" / "odiac2024"
CACHE_DIR    = PROJECT_ROOT / "data" / "interim" / "odiac_clip_kr"
INTERIM_DIR  = PROJECT_ROOT / "data" / "interim"
for p in (RAW_DIR, CACHE_DIR, INTERIM_DIR):
    p.mkdir(parents=True, exist_ok=True)

BASE_URL = ("https://db.cger.nies.go.jp/nies_data/10.17595/20170411.001/"
            "odiac2024/1km_tiff/{year}/odiac2024_1km_excl_intl_{yymm}.tif.gz")
KR_BBOX  = (124.0, 33.0, 132.0, 39.0)
UA       = "Mozilla/5.0 (compatible; AX-contest-research/1.0; +mailto:zxsa0716@kookmin.ac.kr)"
HEADERS  = {"User-Agent": UA}


def _months(start: str, end: str) -> list[tuple[int, int]]:
    out = []
    d = datetime.fromisoformat(start).replace(day=1)
    e = datetime.fromisoformat(end)
    while d <= e:
        out.append((d.year, d.month))
        d = d.replace(year=d.year + (1 if d.month == 12 else 0),
                      month=1 if d.month == 12 else d.month + 1)
    return out


def download_month(year: int, month: int, force: bool = False) -> Path:
    yymm = f"{year % 100:02d}{month:02d}"
    url  = BASE_URL.format(year=year, yymm=yymm)
    gz_path = RAW_DIR / f"odiac2024_1km_excl_intl_{yymm}.tif.gz"
    tif_path = RAW_DIR / f"odiac2024_1km_excl_intl_{yymm}.tif"

    if tif_path.exists() and not force:
        return tif_path

    if not gz_path.exists() or force:
        print(f"[download] {url}")
        r = requests.get(url, headers=HEADERS, stream=True, timeout=120)
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(gz_path, "wb") as f, tqdm(
                total=total, unit="B", unit_scale=True,
                desc=f"{yymm}", ncols=80) as bar:
            for chunk in r.iter_content(chunk_size=1 << 16):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

    print(f"[gunzip] {gz_path.name}")
    with gzip.open(gz_path, "rb") as gi, open(tif_path, "wb") as fo:
        shutil.copyfileobj(gi, fo)
    return tif_path


def clip_to_korea(tif_path: Path, overwrite: bool = False) -> Path:
    out = CACHE_DIR / f"{tif_path.stem}_KR.tif"
    if out.exists() and not overwrite:
        return out
    with rasterio.open(tif_path) as src:
        window = from_bounds(*KR_BBOX, transform=src.transform)
        data = src.read(1, window=window)
        transform = src.window_transform(window)
        profile = src.profile.copy()
        profile.update(height=data.shape[0], width=data.shape[1],
                       transform=transform, compress="deflate")
        with rasterio.open(out, "w", **profile) as dst:
            dst.write(data, 1)
    return out


def _buffer_geom_deg(lat: float, lon: float, buffer_m: int) -> dict:
    fwd = Transformer.from_crs(4326, 3857, always_xy=True).transform
    inv = Transformer.from_crs(3857, 4326, always_xy=True).transform
    x, y = fwd(lon, lat)
    buf = Point(x, y).buffer(buffer_m)
    coords = [inv(xc, yc) for xc, yc in buf.exterior.coords]
    poly = Polygon(coords)
    return mapping(poly)


def stats_in_buffer(tif_path: Path, lat: float, lon: float,
                    buffer_m: int) -> dict:
    geom = _buffer_geom_deg(lat, lon, buffer_m)
    try:
        with rasterio.open(tif_path) as src:
            arr, _ = rio_mask(src, [geom], crop=True, filled=True,
                              nodata=np.nan)
            a = arr[0].astype("float64")
            a = a[np.isfinite(a)]
            if a.size == 0:
                return {"odiac_sum_tC": 0.0,
                        "odiac_mean_tC_per_km2": 0.0,
                        "odiac_max_tC": 0.0,
                        "odiac_n_cells": 0}
            return {
                "odiac_sum_tC":          float(a.sum()),
                "odiac_mean_tC_per_km2": float(a.mean()),
                "odiac_max_tC":          float(a.max()),
                "odiac_n_cells":         int(a.size),
            }
    except Exception as e:
        return {"odiac_sum_tC": None, "odiac_mean_tC_per_km2": None,
                "odiac_max_tC": None, "odiac_n_cells": None,
                "odiac_error": str(e)[:200]}


def build_odiac_panel(sites_csv: str, start: str = "2019-01-01",
                      end: str = "2023-12-31", buffer_m: int = 10_000,
                      download: bool = True,
                      out_csv: str | None = None) -> pd.DataFrame:
    sites = pd.read_csv(sites_csv)
    req = {"company_id", "site_id", "lat", "lon"}
    if not req.issubset(sites.columns):
        raise ValueError(f"sites_csv missing columns: {req - set(sites.columns)}")

    months = _months(start, end)
    if out_csv is None:
        out_csv = str(INTERIM_DIR / "odiac_panel.csv")

    clipped: dict[tuple[int, int], Path] = {}
    print(f"[odiac] preparing {len(months)} monthly rasters...")
    for (yr, mo) in tqdm(months, desc="download+clip", ncols=80):
        try:
            if download:
                tif = download_month(yr, mo)
            else:
                yymm = f"{yr % 100:02d}{mo:02d}"
                tif = RAW_DIR / f"odiac2024_1km_excl_intl_{yymm}.tif"
                if not tif.exists():
                    print(f"  [skip] {tif.name} missing and download=False")
                    continue
            clipped[(yr, mo)] = clip_to_korea(tif)
        except Exception as e:
            print(f"  [error] {yr}-{mo}: {e}")

    if not clipped:
        sys.exit("No ODIAC rasters available.")

    rows = []
    for (yr, mo), tif in tqdm(clipped.items(), desc="zonal-stats", ncols=80):
        for _, s in sites.iterrows():
            r = stats_in_buffer(tif, float(s["lat"]), float(s["lon"]), buffer_m)
            r.update({
                "company_id": s["company_id"],
                "site_id":   s["site_id"],
                "year":      yr,
                "month":     mo,
                "buffer_m":  buffer_m,
            })
            rows.append(r)

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[odiac] wrote {len(df)} rows -> {out_csv}")
    return df


def print_bulk_urls(start: str = "2019-01-01", end: str = "2023-12-31") -> None:
    for (yr, mo) in _months(start, end):
        yymm = f"{yr % 100:02d}{mo:02d}"
        print(BASE_URL.format(year=yr, yymm=yymm))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites")
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end",   default="2023-12-31")
    ap.add_argument("--buffer", type=int, default=10_000)
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--print-urls", action="store_true")
    ap.add_argument("--test-one", action="store_true")
    args = ap.parse_args()

    if args.print_urls:
        print_bulk_urls(args.start, args.end)
        sys.exit(0)

    if args.test_one:
        p = download_month(2023, 5)
        q = clip_to_korea(p)
        print(f"[test] downloaded: {p}")
        print(f"[test] KR-clipped: {q}")
        with rasterio.open(q) as src:
            print(f"       shape={src.shape}  crs={src.crs}  sum={src.read(1).sum():.1f} tC")
        sys.exit(0)

    if not args.sites:
        sys.exit("--sites required unless --print-urls or --test-one")

    build_odiac_panel(args.sites, args.start, args.end,
                      buffer_m=args.buffer,
                      download=not args.no_download)
