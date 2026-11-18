"""Bounded Sentinel-2 optical comparison for the private 2019 Kenya backtest.

Research only: provider scene classifications are not independent field truth.
Returns prefire NBR and pre-minus-post delta NBR; NaN means unavailable.

"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import math
import numpy as np
import rasterio
from rasterio.errors import WindowError
from rasterio.warp import transform_bounds, reproject, Resampling
from rasterio.windows import Window, from_bounds, transform as window_transform

SCENES = {
    "pre": {
        "T37MBV": "S2A_37MBV_20190218_0_L2A",
        "T37MCV": "S2A_37MCV_20190218_0_L2A",
    },
    "post": {
        "T37MBV": "S2A_37MBV_20190310_0_L2A",
        "T37MCV": "S2A_37MCV_20190310_0_L2A",
    },
}
SCENE_CLOUD_PERCENT = {
    "S2A_37MBV_20190218_0_L2A": 0.124064,
    "S2A_37MCV_20190218_0_L2A": 2.435539,
    "S2A_37MBV_20190310_0_L2A": 1.196642,
    "S2A_37MCV_20190310_0_L2A": 1.131264,
}
# Grid-wide metadata are not a local cloud assessment; SCL screens every cell.
SOURCES = {
    period: {
        tile: {
            band: (
                "https://sentinel-cogs.s3.us-west-2.amazonaws.com/"
                f"sentinel-s2-l2a-cogs/37/M/{tile[-2:]}/2019/{month}/{scene}/{band}.tif"
            )
            for band in ("B8A", "B12", "SCL")
        }
        for tile, scene in tiles.items()
    }
    for period, tiles, month in (
        ("pre", SCENES["pre"], 2), ("post", SCENES["post"], 3)
    )
}


def _window_to_grid(url, shape, transform):
    """Read only the source window intersecting the target EPSG:4326 grid."""
    output = np.zeros(shape, dtype=np.uint16)
    height, width = shape
    west, south, east, north = rasterio.transform.array_bounds(height, width, transform)
    with rasterio.open(url) as src:
        if src.crs is None or src.count != 1:
            raise ValueError("Optical source lacks CRS or has an unexpected band count")
        target_bounds = transform_bounds("EPSG:4326", src.crs, west, south, east, north, densify_pts=21)
        try:
            w = from_bounds(*target_bounds, transform=src.transform).intersection(
                Window(0, 0, src.width, src.height)
            )
        except WindowError:
            return output
        col0 = max(0, math.floor(w.col_off))
        row0 = max(0, math.floor(w.row_off))
        col1 = min(src.width, math.ceil(w.col_off + w.width))
        row1 = min(src.height, math.ceil(w.row_off + w.height))
        if col1 <= col0 or row1 <= row0:
            return output
        window = Window(col0, row0, col1-col0, row1-row0)
        pixels = src.read(1, window=window, masked=True).filled(0)
        reproject(
            source=pixels, destination=output,
            src_transform=window_transform(window, src.transform), src_crs=src.crs,
            src_nodata=0, dst_transform=transform, dst_crs="EPSG:4326",
            dst_nodata=0, resampling=Resampling.nearest,
        )
    return output


def _period(period, shape, transform):
    """Mosaic same-date bands; select SCL vegetation before bare soil."""
    scl_out = np.zeros(shape, dtype=np.uint16)
    nir_out = np.zeros(shape, dtype=np.uint16)
    swir_out = np.zeros(shape, dtype=np.uint16)
    for tile in ("T37MBV", "T37MCV"):
        urls = SOURCES[period][tile]
        print(f"Optical {period} {tile}: reading SCL, B8A and B12 windows", flush=True)
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(_window_to_grid, urls[band], shape, transform)
                       for band in ("SCL", "B8A", "B12")]
            scl, nir, swir = [future.result() for future in futures]
        print(f"Optical {period} {tile}: windows complete", flush=True)
        usable = np.isin(scl, (4, 5)) & (nir > 0) & (swir > 0)
        choose = usable & ((scl_out == 0) | ((scl_out != 4) & (scl == 4)))
        scl_out[choose] = scl[choose]
        nir_out[choose] = nir[choose]
        swir_out[choose] = swir[choose]
    return scl_out, nir_out, swir_out


def _nbr(nir, swir, valid):
    nir = nir.astype(np.float32)
    swir = swir.astype(np.float32)
    denominator = nir + swir
    result = np.full(nir.shape, np.nan, dtype=np.float32)
    np.divide(nir - swir, denominator, out=result, where=valid & (denominator > 0))
    return result


def read_optical(shape, transform):
    """Return prefire NBR, pre-minus-post NBR, and both-date vegetation mask.

    Input grid is a north-up EPSG:4326 rasterio Affine. Outputs use the same
    shape. Prefire NBR requires prefire SCL=4 independent of postfire SCL.
    Delta additionally needs postfire SCL=4 or 5 and both usable bands.
    vegetation_mask requires SCL=4 and valid bands at both dates.
    Unknown/cloud/shadow/water/no-data or absent coverage is excluded, not zero.
    """
    if (not isinstance(shape, tuple) or len(shape) != 2
            or any(not isinstance(n, int) or n <= 0 for n in shape)
            or shape[0] * shape[1] > 5_000_000):
        raise ValueError("A positive bounded (height, width) shape is required")
    if (transform.b != 0 or transform.d != 0 or transform.a <= 0 or transform.e >= 0):
        raise ValueError("Expected a north-up EPSG:4326 affine transform")
    west, south, east, north = rasterio.transform.array_bounds(*shape, transform)
    if not (36.0 <= west < east <= 39.0 and -2.0 <= south < north <= 1.0):
        raise ValueError("Research target is outside the bounded Kenya region")
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="2"):
        pre_scl, pre_nir, pre_swir = _period("pre", shape, transform)
        post_scl, post_nir, post_swir = _period("post", shape, transform)
    pre_valid = (pre_scl == 4) & (pre_nir > 0) & (pre_swir > 0)
    post_valid = np.isin(post_scl, (4, 5)) & (post_nir > 0) & (post_swir > 0)
    pre = _nbr(pre_nir, pre_swir, pre_valid)
    post = _nbr(post_nir, post_swir, post_valid)
    delta = np.full(shape, np.nan, dtype=np.float32)
    both = np.isfinite(pre) & np.isfinite(post)
    np.subtract(pre, post, out=delta, where=both)
    vegetation_mask = pre_valid & (post_scl == 4) & post_valid
    return pre, delta, vegetation_mask
