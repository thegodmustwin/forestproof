"""Measure native Sentinel-2 scene-classification visibility in the Geta research rectangle."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

import numpy as np
from rasterio.errors import RasterioError
from rasterio.io import MemoryFile
from rasterio.warp import transform, transform_bounds
from rasterio.windows import Window, from_bounds


BOUNDS = (36.60, -0.49, 36.63, -0.46)
TILES = {"36MZE": 32736, "37MBV": 32737}
COLLECTION = "sentinel-2-l2a"
CATALOG = "https://earth-search.aws.element84.com/v1/search"
ASSETS = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs"
MAX_CATALOG_BYTES = 512 * 1024
MAX_TILE_BYTES = 8 * 1024 * 1024
MAX_WINDOW_CELLS = 250_000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(opener, url, *, method="GET", headers=None):
    return opener.open(Request(url, method=method, headers={
        "User-Agent": "ForestProof-Sentinel-Visibility/1.0",
        "Accept-Encoding": "identity",
        **(headers or {}),
    }), timeout=20)


def scene_pair(opener, day):
    url = f"{CATALOG}?{urlencode({
        'collections': COLLECTION,
        'bbox': ','.join(map(str, BOUNDS)),
        'datetime': f'{day}T00:00:00Z/{day + timedelta(days=1)}T00:00:00Z',
        'limit': 20,
    })}"
    with request(opener, url) as response:
        if response.status != 200:
            raise ValueError("Unexpected catalog response")
        raw = response.read(MAX_CATALOG_BYTES + 1)
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError("Catalog result exceeds the transfer limit")
    result = json.loads(raw)
    features = result["features"]
    # Earth Search also emits a next link when the response already has every match.
    context = result.get("context")
    if context is not None:
        complete = context.get("matched") == context.get("returned") == len(features)
    else:
        complete = not any(link.get("rel") == "next" for link in result["links"])
    if not complete:
        raise ValueError("Catalog window cannot be inspected in one page")

    tiles = {}
    for item in features:
        properties = item["properties"]
        tile = properties.get("grid:code", "").removeprefix("MGRS-")
        acquired = datetime.fromisoformat(properties["datetime"]).astimezone(UTC)
        if tile not in TILES or acquired.date() != day:
            continue

        item_id = item["id"]
        match = re.fullmatch(rf"(S2[ABC])_{tile}_{day:%Y%m%d}_[0-9]+_L2A", item_id)
        if not match or item["collection"] != COLLECTION:
            raise ValueError("Unexpected catalog item identity")
        datatake = properties["s2:datatake_id"]
        if not datatake.startswith(f"G{match[1]}_{day:%Y%m%d}T"):
            raise ValueError("Unexpected Sentinel-2 datatake identity")
        asset_url = f"{ASSETS}/{tile[:2]}/{tile[2]}/{tile[3:]}/{day:%Y/%m}/{item_id}/SCL.tif"
        if item["assets"]["scl"]["href"] != asset_url or tile in tiles:
            raise ValueError("Ambiguous or unrecognized SCL asset")
        tiles[tile] = {
            "tile": tile, "item_id": item_id, "datatake": datatake,
            "tile_time": acquired.isoformat(), "source_url": asset_url,
        }

    if tiles.keys() != TILES.keys():
        raise ValueError(f"{day} does not have both catalog tile records")
    if len({tile["datatake"] for tile in tiles.values()}) != 1:
        raise ValueError("The two grids belong to different acquisitions")
    return [tiles[tile] for tile in TILES]


def read_pinned_asset(opener, url):
    with request(opener, url, method="HEAD") as response:
        length = response.headers.get("Content-Length", "")
        etag = response.headers.get("ETag", "")
        modified = response.headers.get("Last-Modified")
        if (response.status != 200 or not re.fullmatch(r"[0-9]{1,8}", length)
                or not re.fullmatch(r'"[0-9a-f]{32}(?:-[0-9]+)?"', etag) or not modified):
            raise ValueError("SCL object identity is incomplete")
        size = int(length)
    if not 0 < size <= MAX_TILE_BYTES:
        raise ValueError("SCL asset is outside the transfer budget")
    with request(opener, url, headers={"Range": f"bytes=0-{size - 1}", "If-Match": etag}) as response:
        if (response.status != 206 or response.headers.get("ETag") != etag
                or response.headers.get("Content-Range") != f"bytes 0-{size - 1}/{size}"
                or response.headers.get("Content-Encoding", "identity") != "identity"):
            raise ValueError("SCL response did not match the pinned range")
        data = response.read(size + 1)
    if len(data) != size:
        raise ValueError("SCL response was incomplete")
    return data, {"etag": etag, "source_modified": modified, "bytes": size, "sha256": sha256(data).hexdigest()}


def classify(values):
    if not values.size or (values > 11).any():
        raise ValueError("Window contained no centres or an unknown SCL code")
    counts = np.bincount(values, minlength=12).tolist()
    return {
        "sampled_centres": int(values.size),
        "surface_classified_visible": sum(counts[4:7]),
        "vegetation_classified_visible": counts[4],
        "scl_counts_0_to_11": counts,
    }


def measure(data, epsg):
    with MemoryFile(data) as memory:
        with memory.open() as raster:
            if (raster.driver != "GTiff" or raster.count != 1 or raster.dtypes != ("uint8",)
                    or raster.crs is None or raster.crs.to_epsg() != epsg
                    or (raster.transform.a, raster.transform.b, raster.transform.d, raster.transform.e)
                    != (20, 0, 0, -20)):
                raise ValueError("Expected a native north-up 20 m Sentinel-2 classification grid")

            projected = transform_bounds("EPSG:4326", raster.crs, *BOUNDS)
            loose = from_bounds(*projected, transform=raster.transform)
            window = Window.from_slices(
                (max(0, int(np.floor(loose.row_off))), min(raster.height, int(np.ceil(loose.row_off + loose.height)))),
                (max(0, int(np.floor(loose.col_off))), min(raster.width, int(np.ceil(loose.col_off + loose.width)))),
            )
            if not 0 < window.width * window.height <= MAX_WINDOW_CELLS:
                raise ValueError("SCL sample window is empty or oversized")
            values = raster.read(1, window=window)
            rows, cols = np.indices(values.shape)
            grid = raster.window_transform(window)
            x = grid.c + grid.a * (cols.ravel() + 0.5)
            y = grid.f + grid.e * (rows.ravel() + 0.5)
            lon, lat = map(np.asarray, transform(raster.crs, "EPSG:4326", x, y))
            west, south, east, north = BOUNDS
            inside = (west <= lon) & (lon < east) & (south <= lat) & (lat < north)
            return classify(values.ravel()[inside])


def inspect(days, opener):
    acquisitions = []
    for day in days:
        tiles = scene_pair(opener, day)
        for tile in tiles:
            data, receipt = read_pinned_asset(opener, tile["source_url"])
            tile.update(receipt)
            tile.update(measure(data, TILES[tile["tile"]]))
        acquisitions.append({
            "date": day.isoformat(),
            "attribution": f"Contains modified Copernicus Sentinel data [{day.year}]",
            "tiles": tiles,
        })

    return {
        "schema": "forestproof.sentinel2_visibility.v1",
        "area": "Provisional Geta research rectangle",
        "checked_at": datetime.now(UTC).isoformat(),
        "native_resolution_metres": 20,
        "note": "Overlapping grids are reported separately. Scene visibility does not measure disturbance.",
        "acquisitions": acquisitions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("day", nargs="+", type=date.fromisoformat, help="Acquisition date in UTC (YYYY-MM-DD)")
    args = parser.parse_args()
    days = sorted(set(args.day))
    if len(args.day) != len(days) or len(days) > 3:
        parser.error("Supply one to three distinct acquisition dates")
    try:
        report = inspect(days, build_opener(NoRedirect()))
    except (OSError, ValueError, RasterioError, KeyError, TypeError) as error:
        parser.exit(1, f"Visibility inspection unavailable: {error}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
