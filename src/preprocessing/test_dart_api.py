"""Smoke test: DART API corpCode download."""

import io
import zipfile
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("DART_API_KEY")
assert API_KEY, "DART_API_KEY not found in .env"

url = "https://opendart.fss.or.kr/api/corpCode.xml"
resp = requests.get(url, params={"crtfc_key": API_KEY}, timeout=30)
resp.raise_for_status()

with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
    xml_bytes = zf.read(zf.namelist()[0])

root = ET.fromstring(xml_bytes)
corps = root.findall("list")
listed = [c for c in corps if (c.findtext("stock_code") or "").strip()]

print(f"Total companies : {len(corps)}")
print(f"Listed (w/ stock_code): {len(listed)}")
