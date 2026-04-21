"""Extract monthly Sentinel-5P (NO2, SO2, CO, HCHO) + ERA5-Land + MERRA-2 per site.

Output long-format CSV: data/interim/satellite_panel_{yyyymm}_{yyyymm}.csv

qa filtering:
  - NO2:  qa_value >= 0.75 (standard)
  - SO2:  qa_value >= 0.50 (higher noise)
  - CO:   no qa band in L3 OFFL (pre-filtered at L2->L3 QA>50%)
  - HCHO: no qa band in L3 OFFL (pre-filtered at L2->L3 QA>50%)

ERA5 BLH: fetched from ECMWF/ERA5/HOURLY (ERA5-Land lacks BLH).
"""
from __future__ import annotations

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from calendar import monthrange

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

import ee  # noqa: E402

PROJECT_ID = os.getenv("GEE_PROJECT_ID")
if not PROJECT_ID:
    sys.exit("GEE_PROJECT_ID not set in .env")

SLEEP_SEC = 0.3

# S5P L3 OFFL products do NOT expose qa_value band (qa filtering is applied
# upstream at L2->L3 compositing). All 4 species use no qa_band filter.
S5P_COLLECTIONS = {
    "no2": {
        "id": "COPERNICUS/S5P/OFFL/L3_NO2",
        "band": "tropospheric_NO2_column_number_density",
        "qa_band": None, "qa_min": None, "scale": 1113,
    },
    "so2": {
        "id": "COPERNICUS/S5P/OFFL/L3_SO2",
        "band": "SO2_column_number_density",
        "qa_band": None, "qa_min": None, "scale": 1113,
    },
    "co": {
        "id": "COPERNICUS/S5P/OFFL/L3_CO",
        "band": "CO_column_number_density",
        "qa_band": None, "qa_min": None, "scale": 1113,
    },
    "hcho": {
        "id": "COPERNICUS/S5P/OFFL/L3_HCHO",
        "band": "tropospheric_HCHO_column_number_density",
        "qa_band": None, "qa_min": None, "scale": 1113,
    },
}

ERA5_LAND_ID = "ECMWF/ERA5_LAND/HOURLY"
ERA5_LAND_BANDS = {
    "era5_u10": "u_component_of_wind_10m",
    "era5_v10": "v_component_of_wind_10m",
    "era5_t2m": "temperature_2m",
    "era5_tp": "total_precipitation_hourly",
}
ERA5_ID = "ECMWF/ERA5/HOURLY"
ERA5_BANDS = {"era5_blh": "boundary_layer_height"}

# MERRA-2 SLV (instantaneous single-level) in GEE uses different band naming.
# Key diagnostics available: QV10M (specific humidity 10m), QV2M, PBLTOP,
# PS (surface pressure), DISPH (displacement height). Surface wind U/V and T2M
# are NOT present in this subset — deferred to sensitivity analysis later.
# Keep PBLTOP as independent PBL height check vs ERA5 BLH.
MERRA2_ID = "NASA/GSFC/MERRA/slv/2"
MERRA2_BANDS = {
    "merra2_pbltop": "PBLTOP",
    "merra2_ps":     "PS",
    "merra2_disph":  "DISPH",
    "merra2_qv2m":   "QV2M",
}


def month_bounds(year: int, month: int) -> tuple[str, str]:
    last_day = monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def _qa_mask(img: ee.Image, qa_band: str, qa_min: float, value_band: str) -> ee.Image:
    mask = img.select(qa_band).gte(qa_min)
    return img.select(value_band).updateMask(mask)


def extract_s5p_monthly(geom: ee.Geometry, start: str, end: str,
                        collection_key: str) -> dict | None:
    spec = S5P_COLLECTIONS[collection_key]
    col = (ee.ImageCollection(spec["id"])
           .filterDate(start, end)
           .filterBounds(geom))

    if spec["qa_band"] is not None:
        col = col.map(lambda img: _qa_mask(img, spec["qa_band"],
                                           spec["qa_min"], spec["band"]))
    else:
        col = col.select(spec["band"])

    img = col.mean()
    try:
        out = (img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geom,
                scale=spec["scale"],
                maxPixels=1e9,
                bestEffort=True)
               .getInfo())
        n = col.size().getInfo()
    except Exception as e:
        return {"value": None, "n_images": None, "error": str(e)[:200]}
    time.sleep(SLEEP_SEC)
    val = out.get(spec["band"]) if out else None
    return {"value": val, "n_images": n, "error": None}


def extract_era5_land(geom: ee.Geometry, start: str, end: str) -> dict:
    col = (ee.ImageCollection(ERA5_LAND_ID)
           .filterDate(start, end)
           .filterBounds(geom)
           .select(list(ERA5_LAND_BANDS.values())))
    img = col.mean()
    try:
        out = (img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geom,
                scale=11132,
                maxPixels=1e9,
                bestEffort=True)
               .getInfo()) or {}
    except Exception as e:
        out = {"_error": str(e)[:200]}
    time.sleep(SLEEP_SEC)
    result = {}
    for out_key, band in ERA5_LAND_BANDS.items():
        result[out_key] = out.get(band)
    u, v = result.get("era5_u10"), result.get("era5_v10")
    result["era5_ws10"] = (u**2 + v**2) ** 0.5 if (u is not None and v is not None) else None
    return result


def extract_era5_blh(geom: ee.Geometry, start: str, end: str) -> dict:
    col = (ee.ImageCollection(ERA5_ID)
           .filterDate(start, end)
           .filterBounds(geom)
           .select(list(ERA5_BANDS.values())))
    img = col.mean()
    try:
        out = (img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geom,
                scale=27830,
                maxPixels=1e9,
                bestEffort=True)
               .getInfo()) or {}
    except Exception as e:
        out = {"_error": str(e)[:200]}
    time.sleep(SLEEP_SEC)
    return {k: out.get(v) for k, v in ERA5_BANDS.items()}


def extract_merra2(geom: ee.Geometry, start: str, end: str) -> dict:
    col = (ee.ImageCollection(MERRA2_ID)
           .filterDate(start, end)
           .filterBounds(geom)
           .select(list(MERRA2_BANDS.values())))
    img = col.mean()
    try:
        out = (img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geom,
                scale=55660,
                maxPixels=1e9,
                bestEffort=True)
               .getInfo()) or {}
    except Exception as e:
        out = {"_error": str(e)[:200]}
    time.sleep(SLEEP_SEC)
    result = {k: out.get(v) for k, v in MERRA2_BANDS.items()}
    return result


def extract_satellite_panel(sites_csv: str, start: str, end: str,
                            buffer_m: int = 10_000,
                            out_csv: str | None = None,
                            checkpoint_every: int = 25) -> pd.DataFrame:
    ee.Initialize(project=PROJECT_ID)

    sites = pd.read_csv(sites_csv)
    required = {"company_id", "site_id", "lat", "lon", "industry"}
    missing = required - set(sites.columns)
    if missing:
        raise ValueError(f"sites_csv missing columns: {missing}")

    months: list[tuple[int, int]] = []
    d = datetime.fromisoformat(start).replace(day=1)
    end_dt = datetime.fromisoformat(end)
    while d <= end_dt:
        months.append((d.year, d.month))
        if d.month == 12:
            d = d.replace(year=d.year + 1, month=1)
        else:
            d = d.replace(month=d.month + 1)

    if out_csv is None:
        yyyymm_s = f"{months[0][0]:04d}{months[0][1]:02d}"
        yyyymm_e = f"{months[-1][0]:04d}{months[-1][1]:02d}"
        interim = Path(__file__).resolve().parents[2] / "data" / "interim"
        interim.mkdir(parents=True, exist_ok=True)
        out_csv = str(interim / f"satellite_panel_{yyyymm_s}_{yyyymm_e}.csv")

    print(f"[satellite_panel] sites={len(sites)}  months={len(months)}  "
          f"total_iters={len(sites)*len(months)}  out={out_csv}")

    done = set()
    if Path(out_csv).exists():
        try:
            prev = pd.read_csv(out_csv)
            done = set(zip(prev["site_id"].astype(str),
                           prev["year"].astype(int),
                           prev["month"].astype(int)))
            print(f"[satellite_panel] resuming — {len(done)} rows already done")
        except Exception:
            done = set()

    header_written = Path(out_csv).exists() and len(done) > 0
    buffer_rows: list[dict] = []

    total = len(sites) * len(months)
    with tqdm(total=total, desc="sat+met", ncols=100) as pbar:
        for _, s in sites.iterrows():
            geom = (ee.Geometry.Point([float(s["lon"]), float(s["lat"])])
                    .buffer(buffer_m))
            for (yr, mo) in months:
                key = (str(s["site_id"]), int(yr), int(mo))
                if key in done:
                    pbar.update(1)
                    continue
                t0 = time.time()
                m_start, m_end = month_bounds(yr, mo)
                row: dict = {
                    "company_id": s["company_id"],
                    "site_id": s["site_id"],
                    "industry": s["industry"],
                    "lat": float(s["lat"]),
                    "lon": float(s["lon"]),
                    "year": yr,
                    "month": mo,
                    "buffer_m": buffer_m,
                }
                for key_s in ("no2", "so2", "co", "hcho"):
                    res = extract_s5p_monthly(geom, m_start, m_end, key_s)
                    row[f"{key_s}_mean"] = res["value"]
                    row[f"{key_s}_n_images"] = res["n_images"]
                    if res["error"]:
                        row[f"{key_s}_error"] = res["error"]
                row.update(extract_era5_land(geom, m_start, m_end))
                row.update(extract_era5_blh(geom, m_start, m_end))
                row.update(extract_merra2(geom, m_start, m_end))

                row["elapsed_s"] = round(time.time() - t0, 2)
                buffer_rows.append(row)
                pbar.update(1)

                if len(buffer_rows) >= checkpoint_every:
                    _flush(buffer_rows, out_csv, header_written)
                    header_written = True
                    buffer_rows.clear()

    if buffer_rows:
        _flush(buffer_rows, out_csv, header_written)

    return pd.read_csv(out_csv)


def _flush(rows: list[dict], path: str, header_written: bool) -> None:
    mode = "a" if header_written else "w"
    pd.DataFrame(rows).to_csv(path, index=False, mode=mode,
                              header=not header_written, encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", required=True)
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end",   default="2023-12-31")
    ap.add_argument("--buffer", type=int, default=10_000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    df = extract_satellite_panel(
        sites_csv=args.sites, start=args.start, end=args.end,
        buffer_m=args.buffer, out_csv=args.out,
    )
    print(df.tail())
    print(f"[done] rows={len(df)}  non-null NO2={df['no2_mean'].notna().sum()}")
