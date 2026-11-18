import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import urllib.request

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.windows import from_bounds as window_from_bounds


ROOT = Path(os.environ["FORESTPROOF_KENYA_RESEARCH_DIR"]).resolve()
BOUNDS = (37.20, -0.34, 37.54, -0.02)
STEP = 0.0002
SHAPE = (1600, 1700)
GRID = from_bounds(*BOUNDS, SHAPE[1], SHAPE[0])
BUCKET = "https://deafrica-sentinel-1.s3.af-south-1.amazonaws.com/s1_rtc/S01E037"
RASTER_OPTIONS = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_HTTP_TIMEOUT": "120",
    "GDAL_HTTP_MAX_RETRY": "2",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
    "CPL_VSIL_CURL_CHUNK_SIZE": "262144",
    "GDAL_INGESTED_BYTES_AT_OPEN": "32768",
}


def asset_url(date, take, suffix):
    date_path = date.replace("-", "/")
    name_date = date.replace("-", "_")
    name = f"s1_rtc_{take}_S01E037_{name_date}"
    return f"{BUCKET}/{date_path}/{take}/{name}_{suffix}"


def capture_metadata(date, take):
    path = ROOT / f"radar_{date}_{take}_metadata.json"
    if not path.exists():
        request = urllib.request.Request(asset_url(date, take, "metadata.json"))
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError("Metadata response exceeded probe limit")
        path.write_bytes(raw)
    metadata = json.loads(path.read_bytes())
    props = metadata["properties"]
    identity = (
        str(props["platform"]).lower(),
        str(props["sat:orbit_state"]).lower(),
        int(props["sat:relative_orbit"]),
        sorted(map(str.lower, props["sar:polarizations"])),
    )
    if identity != ("sentinel-1a", "ascending", 57, ["vh", "vv"]):
        raise ValueError(f"Unexpected same-track identity for {date}: {identity}")
    if props["datetime"][:10] != date:
        raise ValueError(f"Unexpected metadata time for {date}")
    return metadata


def read_band(date, take, band):
    path = ROOT / f"radar_{date}_{take}_{band}.npy"
    if path.exists():
        values = np.load(path, allow_pickle=False)
        if values.shape != SHAPE:
            raise ValueError(f"Unexpected cached radar window shape {values.shape}")
        return values
    url = asset_url(date, take, f"{band}.tif")
    with rasterio.Env(**RASTER_OPTIONS):
        with rasterio.open(f"/vsicurl/{url}") as dataset:
            if dataset.crs.to_epsg() != 4326:
                raise ValueError(f"Unexpected radar CRS on {date} {band}")
            window = window_from_bounds(*BOUNDS, transform=dataset.transform)
            window = window.round_offsets(op="round").round_lengths()
            if not dataset.window_transform(window).almost_equals(GRID, precision=1e-8):
                raise ValueError(f"Grid mismatch on {date} {band}")
            values = dataset.read(1, window=window)
    if values.shape != SHAPE:
        raise ValueError(f"Unexpected radar window shape {values.shape}")
    np.save(path, values, allow_pickle=False)
    print(f"Radar window verified {date} {band} {values.shape}", flush=True)
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("date")
    parser.add_argument("take")
    parser.add_argument("--bands", nargs="+", choices=["VV", "VH", "MASK", "ANGLE"], default=["VV", "VH", "MASK"])
    args = parser.parse_args()
    metadata = capture_metadata(args.date, args.take)
    print(f"Radar acquisition verified {metadata['properties']['datetime']}", flush=True)
    with ThreadPoolExecutor(max_workers=min(3, len(args.bands))) as pool:
        list(pool.map(lambda band: read_band(args.date, args.take, band), args.bands))


if __name__ == "__main__":
    main()
