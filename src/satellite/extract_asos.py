"""KMA ASOS daily ground observations -> monthly aggregate per site.

API: http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList
Auth: serviceKey (use DECODED form; requests url-encodes).
"""
from __future__ import annotations

import os
import sys
import time
import math
import argparse
from pathlib import Path
from calendar import monthrange

import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

KEY_DECODED = os.getenv("KMA_API_KEY_DECODED")
if not KEY_DECODED:
    sys.exit("KMA_API_KEY_DECODED not set in .env")

BASE = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"
INTERIM = Path(__file__).resolve().parents[2] / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

# ASOS 지점 목록 (한국 주요 산업지 포함). KMA 공식 지점번호.
ASOS_STATIONS = pd.DataFrame([
    {"stnId": 108, "stnNm": "서울",   "lat": 37.5714, "lon": 126.9658},
    {"stnId": 112, "stnNm": "인천",   "lat": 37.4777, "lon": 126.6249},
    {"stnId": 119, "stnNm": "수원",   "lat": 37.2723, "lon": 126.9857},
    {"stnId": 129, "stnNm": "서산",   "lat": 36.7766, "lon": 126.4939},
    {"stnId": 131, "stnNm": "청주",   "lat": 36.6392, "lon": 127.4407},
    {"stnId": 133, "stnNm": "대전",   "lat": 36.3722, "lon": 127.3735},
    {"stnId": 135, "stnNm": "추풍령", "lat": 36.2203, "lon": 128.0038},
    {"stnId": 138, "stnNm": "포항",   "lat": 36.0328, "lon": 129.3799},
    {"stnId": 140, "stnNm": "군산",   "lat": 36.0053, "lon": 126.7614},
    {"stnId": 143, "stnNm": "대구",   "lat": 35.8782, "lon": 128.6528},
    {"stnId": 146, "stnNm": "전주",   "lat": 35.8408, "lon": 127.1193},
    {"stnId": 152, "stnNm": "울산",   "lat": 35.5822, "lon": 129.3249},
    {"stnId": 156, "stnNm": "광주",   "lat": 35.1729, "lon": 126.8916},
    {"stnId": 159, "stnNm": "부산",   "lat": 35.1047, "lon": 128.9019},
    {"stnId": 162, "stnNm": "통영",   "lat": 34.8454, "lon": 128.4362},
    {"stnId": 165, "stnNm": "목포",   "lat": 34.8172, "lon": 126.3814},
    {"stnId": 168, "stnNm": "여수",   "lat": 34.7392, "lon": 127.7406},
    {"stnId": 174, "stnNm": "순천",   "lat": 34.9405, "lon": 127.5015},
    {"stnId": 184, "stnNm": "제주",   "lat": 33.5141, "lon": 126.5297},
    {"stnId": 192, "stnNm": "진주",   "lat": 35.1636, "lon": 128.0400},
    {"stnId": 232, "stnNm": "천안",   "lat": 36.7765, "lon": 127.1214},
    {"stnId": 235, "stnNm": "보령",   "lat": 36.3271, "lon": 126.5576},
    {"stnId": 236, "stnNm": "부여",   "lat": 36.2729, "lon": 126.9209},
    {"stnId": 238, "stnNm": "금산",   "lat": 36.1048, "lon": 127.4815},
    {"stnId": 247, "stnNm": "남원",   "lat": 35.4213, "lon": 127.3968},
    {"stnId": 260, "stnNm": "장흥",   "lat": 34.6886, "lon": 126.9194},
    {"stnId": 266, "stnNm": "광양",   "lat": 34.9407, "lon": 127.6941},
    {"stnId": 278, "stnNm": "의성",   "lat": 36.3560, "lon": 128.6886},
    {"stnId": 279, "stnNm": "구미",   "lat": 36.1306, "lon": 128.3222},
    {"stnId": 283, "stnNm": "경주",   "lat": 35.7883, "lon": 129.5708},
    {"stnId": 285, "stnNm": "청송",   "lat": 36.4354, "lon": 129.0577},
])


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    r1, r2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(r1)*math.cos(r2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def nearest_station(lat: float, lon: float) -> pd.Series:
    d = ASOS_STATIONS.copy()
    d["dist_km"] = [haversine_km(lat, lon, r.lat, r.lon)
                    for r in d.itertuples(index=False)]
    return d.sort_values("dist_km").iloc[0]


def fetch_daily(stn_id: int, start_yyyymmdd: str, end_yyyymmdd: str,
                num_rows: int = 999, max_retries: int = 3) -> pd.DataFrame:
    rows: list[dict] = []
    page = 1
    while True:
        params = {
            "serviceKey": KEY_DECODED,
            "numOfRows":  num_rows,
            "pageNo":     page,
            "dataType":   "JSON",
            "dataCd":     "ASOS",
            "dateCd":     "DAY",
            "startDt":    start_yyyymmdd,
            "endDt":      end_yyyymmdd,
            "stnIds":     stn_id,
        }
        for attempt in range(max_retries):
            try:
                r = requests.get(BASE, params=params, timeout=30)
                r.raise_for_status()
                j = r.json()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

        body = (j.get("response", {}).get("body") or {})
        items = ((body.get("items") or {}).get("item")) or []
        if isinstance(items, dict):
            items = [items]
        rows.extend(items)

        total = int(body.get("totalCount") or 0)
        fetched = page * num_rows
        if fetched >= total or not items:
            break
        page += 1
        time.sleep(0.2)

    return pd.DataFrame(rows)


def monthly_aggregate(daily: pd.DataFrame) -> pd.DataFrame:
    if daily.empty:
        return daily
    d = daily.copy()
    d["tm"] = pd.to_datetime(d["tm"])
    d["stnId"] = pd.to_numeric(d["stnId"], errors="coerce").astype("Int64").astype(int)
    for c in ("avgTa", "avgWs", "sumRn", "maxWs", "avgRhm", "sumSsHr"):
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d["year"]  = d["tm"].dt.year
    d["month"] = d["tm"].dt.month

    agg = (d.groupby(["stnId", "stnNm", "year", "month"], as_index=False)
             .agg(asos_avgTa  = ("avgTa",  "mean"),
                  asos_avgWs  = ("avgWs",  "mean"),
                  asos_sumRn  = ("sumRn",  "sum"),
                  asos_maxWs  = ("maxWs",  "max"),
                  asos_avgRhm = ("avgRhm", "mean"),
                  asos_sumSsHr= ("sumSsHr", "sum"),
                  asos_ndays  = ("tm",     "count")))
    return agg


def build_asos_panel(sites_csv: str, start: str = "2019-01-01",
                     end: str = "2023-12-31",
                     out_csv: str | None = None) -> pd.DataFrame:
    sites = pd.read_csv(sites_csv)
    req = {"company_id", "site_id", "lat", "lon"}
    if not req.issubset(sites.columns):
        raise ValueError(f"sites_csv missing: {req - set(sites.columns)}")

    picks = []
    for _, s in sites.iterrows():
        ns = nearest_station(float(s["lat"]), float(s["lon"]))
        picks.append({
            "company_id":  s["company_id"],
            "site_id":     s["site_id"],
            "lat":         s["lat"],
            "lon":         s["lon"],
            "stnId":       int(ns["stnId"]),
            "stnNm":       ns["stnNm"],
            "dist_km":     round(float(ns["dist_km"]), 2),
        })
    site_stn = pd.DataFrame(picks)

    sd = start.replace("-", "")
    ed = end.replace("-", "")
    unique_stn = sorted(site_stn["stnId"].unique().tolist())
    print(f"[asos] {len(unique_stn)} unique stations, period {sd}~{ed}")

    daily_frames = []
    for stn in tqdm(unique_stn, desc="ASOS daily", ncols=80):
        try:
            df = fetch_daily(stn, sd, ed)
            if not df.empty:
                daily_frames.append(df)
        except Exception as e:
            print(f"  [error] stn={stn}: {e}")
            time.sleep(1.0)

    if not daily_frames:
        sys.exit("[asos] no data fetched.")

    all_daily = pd.concat(daily_frames, ignore_index=True)
    raw_path = INTERIM / "asos_daily_raw.csv"
    all_daily.to_csv(raw_path, index=False, encoding="utf-8")
    print(f"[asos] wrote raw daily rows={len(all_daily)} -> {raw_path}")

    monthly = monthly_aggregate(all_daily)
    panel = site_stn.rename(columns={"stnId": "nearest_stn_id",
                                     "stnNm": "nearest_stn_nm"})\
                   .merge(monthly.rename(columns={"stnId": "nearest_stn_id"}),
                          on="nearest_stn_id", how="left")

    if out_csv is None:
        out_csv = str(INTERIM / "asos_panel.csv")
    panel.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[asos] wrote site-monthly panel rows={len(panel)} -> {out_csv}")
    return panel


def test_one_station(stn_id: int = 138, ym: str = "2023-01") -> None:
    y, m = map(int, ym.split("-"))
    last = monthrange(y, m)[1]
    sd = f"{y:04d}{m:02d}01"
    ed = f"{y:04d}{m:02d}{last:02d}"
    print(f"[test] stn={stn_id}  {sd}..{ed}")
    df = fetch_daily(stn_id, sd, ed)
    print(f"[test] rows returned: {len(df)}")
    if not df.empty:
        print("[test] columns:", list(df.columns))
        print(df[["tm", "stnId", "stnNm", "avgTa", "avgWs",
                  "sumRn", "maxWs"]].head(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites")
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end",   default="2023-12-31")
    ap.add_argument("--test-one", action="store_true")
    args = ap.parse_args()

    if args.test_one:
        test_one_station()
        sys.exit(0)

    if not args.sites:
        sys.exit("--sites required unless --test-one")

    build_asos_panel(args.sites, args.start, args.end)
