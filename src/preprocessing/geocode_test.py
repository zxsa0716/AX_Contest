"""
VWorld Geocoder API 2.0 smoke test — 주소 → 위경도 변환.

Primary (and only) geocoder: VWorld (국토교통부 공간정보 오픈플랫폼).
  - 무료 40,000 req/day
  - WGS84 (EPSG:4326) 직접 반환
  - 도로명 주소(ROAD) + 지번 주소(PARCEL) 모두 지원
  - 레퍼런스: https://www.vworld.kr/dev/v4dv_geocoderguide2_s001.do

Environment variables (.env):
  VWORLD_API_KEY=<your key>

Usage:
  .venv/Scripts/python.exe src/preprocessing/geocode_test.py

Test addresses (industrial sites for satellite buffer analysis):
  - POSCO 포항제철소      → 경상북도 포항시 남구 동해안로 6261
  - 현대제철 당진제철소   → 충청남도 당진시 송악읍 북부산업로 1480
  - LG화학 여수공장       → 전라남도 여수시 여수산단로 918
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

VWORLD_ENDPOINT = "https://api.vworld.kr/req/address"


@dataclass
class TestCase:
    name: str
    address: str
    addr_type: str  # "ROAD" or "PARCEL"
    expected_lat: float
    expected_lon: float
    tolerance_km: float = 3.0


# Expected coordinates are VWorld-authoritative values (recorded 2026-04-20).
# Tolerance is small — this is a regression test to catch API breakage,
# not a verification of "correct" ground-truth (VWorld IS the ground truth).
TEST_CASES = [
    TestCase(
        name="POSCO 포항제철소",
        address="경상북도 포항시 남구 동해안로 6261",
        addr_type="ROAD",
        expected_lat=35.998261,
        expected_lon=129.382880,
        tolerance_km=0.5,
    ),
    TestCase(
        name="현대제철 당진제철소",
        address="충청남도 당진시 송악읍 북부산업로 1480",
        addr_type="ROAD",
        expected_lat=36.984172,
        expected_lon=126.727520,
        tolerance_km=0.5,
    ),
    TestCase(
        name="LG화학 여수공장",
        address="전라남도 여수시 여수산단로 918",
        addr_type="ROAD",
        expected_lat=34.855321,
        expected_lon=127.711469,
        tolerance_km=0.5,
    ),
]


def geocode_vworld(
    address: str,
    api_key: str,
    addr_type: str = "ROAD",
) -> Optional[tuple[float, float]]:
    """Return (lat, lon) in WGS84 or None if lookup fails.

    Per VWorld API 2.0 spec:
      - request=GetCoord returns result.point.{x,y}
      - When crs=EPSG:4326, x = longitude, y = latitude.
    """
    params = {
        "service": "address",
        "request": "GetCoord",
        "version": "2.0",
        "crs": "EPSG:4326",
        "address": address,
        "format": "json",
        "type": addr_type,
        "key": api_key,
    }
    r = requests.get(VWORLD_ENDPOINT, params=params, timeout=15)
    r.raise_for_status()
    payload = r.json().get("response", {})
    status = payload.get("status")
    if status != "OK":
        err = payload.get("error", {})
        print(f"    VWorld status={status} code={err.get('code')} msg={err.get('text')}")
        return None
    point = payload.get("result", {}).get("point", {})
    lon = float(point["x"])
    lat = float(point["y"])
    return lat, lon


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_earth = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * r_earth * math.asin(math.sqrt(a))


def main() -> int:
    key = os.environ.get("VWORLD_API_KEY")
    if not key:
        print("ERROR: VWORLD_API_KEY not set in .env")
        return 1

    print(f"VWorld key: {key[:8]}...{key[-4:]}")
    print()

    pass_count = 0
    for tc in TEST_CASES:
        print(f"[{tc.name}]")
        print(f"  address : {tc.address}")
        result = geocode_vworld(tc.address, key, tc.addr_type)
        if result is None:
            print(f"  result  : FAILED\n")
            continue
        lat, lon = result
        dist = haversine_km(lat, lon, tc.expected_lat, tc.expected_lon)
        ok = dist < tc.tolerance_km
        status = "PASS" if ok else "FAIL"
        print(f"  result  : lat={lat:.6f}, lon={lon:.6f}")
        print(f"  expected: lat={tc.expected_lat}, lon={tc.expected_lon}")
        print(f"  distance: {dist:.3f} km ({'within' if ok else 'outside'} {tc.tolerance_km} km) [{status}]")
        print()
        if ok:
            pass_count += 1

    print(f"Summary: {pass_count}/{len(TEST_CASES)} passed")
    return 0 if pass_count == len(TEST_CASES) else 2


if __name__ == "__main__":
    raise SystemExit(main())
