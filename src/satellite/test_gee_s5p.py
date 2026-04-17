"""Smoke test: query Sentinel-5P NO2 and SO2 via Google Earth Engine."""

import os, sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

import ee

PROJECT_ID = os.getenv("GEE_PROJECT_ID")
print(f"GEE project: {PROJECT_ID}")

ee.Authenticate()
ee.Initialize(project=PROJECT_ID)

# POSCO Pohang steelworks
lat, lon = 36.0190, 129.3435
poi = ee.Geometry.Point([lon, lat]).buffer(10_000)  # 10 km buffer

start, end = "2023-01-01", "2023-02-01"

# --- NO2 ---
no2_col = (
    ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
    .filterDate(start, end)
    .filterBounds(poi)
    .select("tropospheric_NO2_column_number_density")
)
no2_mean = (
    no2_col.mean()
    .reduceRegion(reducer=ee.Reducer.mean(), geometry=poi, scale=1000)
    .getInfo()
)
print(f"NO2 images in Jan 2023: {no2_col.size().getInfo()}")
print(f"Mean tropospheric NO2: {no2_mean}")

# --- SO2 ---
so2_col = (
    ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_SO2")
    .filterDate(start, end)
    .filterBounds(poi)
    .select("SO2_column_number_density")
)
so2_mean = (
    so2_col.mean()
    .reduceRegion(reducer=ee.Reducer.mean(), geometry=poi, scale=1000)
    .getInfo()
)
print(f"SO2 images in Jan 2023: {so2_col.size().getInfo()}")
print(f"Mean SO2 column density: {so2_mean}")

print("\nGEE pipeline smoke test passed.")
