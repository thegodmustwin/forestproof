"""Score the published JPL v0.1 radar sample against two BAER reference maps."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
import math
from pathlib import Path
import sys
from zipfile import ZipFile

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import Resampling, reproject, transform_bounds
from rasterio.windows import Window, from_bounds

RADAR_MEMBER = (
    "OPERA_L3_DIST-ALERT-S1_T11SLT_20250121T015030Z_20250819T130204Z_S1_30_v0.1"
    "_GEN-DIST-STATUS-ACQ.tif"
)
RADAR_ARCHIVE = "jpl-dist-s1.zip"
REFERENCE_MEMBERS = {
    "Eaton": ("baer-eaton.zip", "eaton_ca3419211810520250108_sbs.tif"),
    "Palisades": ("baer-palisades.zip", "palisades_ca3406811855120250107_sbs.tif"),
}
HASHES = {
    RADAR_ARCHIVE: "9ffac080d09ac6975577496165c9e2507de330366d328062d1095dfa627f7c63",
    "baer-eaton.zip": "fbdd1a4a9a109b1823b792c404c1e9512fd1d2a240ceacc6edcd579ec1f8e358",
    "baer-palisades.zip": "397f3bec3b620e67c26b9b8798aa7f031988d10b3094ab84aefe6ae708a8197e",
}
RADIUS_CELLS = (0, 1, 2, 3)
PRIMARY_RADIUS_CELLS = 2


def open_member(stack, root, archive_name, member_name):
    path = root / archive_name
    with path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != HASHES[archive_name]:
            raise ValueError(f"Unexpected archive identity for {archive_name}.")
    with ZipFile(path) as archive:
        member = archive.getinfo(member_name)
        if member.file_size > 2_000_000:
            raise ValueError("Unexpected analysis-band size.")
        raster = stack.enter_context(MemoryFile(archive.read(member)))
    return stack.enter_context(raster.open())


def aligned_reference_window(reference, radar):
    """Rasterize the small reference extent on the original 30 m radar grid."""
    if reference.count != 1 or reference.dtypes != ("uint8",) or reference.crs.to_epsg() != 26911:
        raise ValueError("Unexpected BAER classification raster.")
    bounds = transform_bounds(reference.crs, radar.crs, *reference.bounds)
    fractional = from_bounds(*bounds, transform=radar.transform)
    left = math.floor(fractional.col_off)
    top = math.floor(fractional.row_off)
    right = math.ceil(fractional.col_off + fractional.width)
    bottom = math.ceil(fractional.row_off + fractional.height)
    if not 0 < (right - left) * (bottom - top) <= 1_000_000:
        raise ValueError("BAER assessment window exceeds the bounded analysis.")
    requested = Window(left, top, right - left, bottom - top)
    classes = np.zeros((bottom - top, right - left), dtype="uint8")
    reproject(
        source=rasterio.band(reference, 1),
        destination=classes,
        dst_transform=radar.window_transform(requested),
        dst_crs=radar.crs,
        # Unclassified reference cells must stay out of the control class.
        src_nodata=0,
        dst_nodata=0,
        resampling=Resampling.nearest,
    )
    if not np.isin(classes, [0, 1, 2, 3, 4]).all():
        raise ValueError("Unexpected BAER class code.")

    # Preserve the reference denominator for any centres outside the radar tile.
    status = np.full(classes.shape, 255, dtype="uint8")
    col0, row0 = max(left, 0), max(top, 0)
    col1, row1 = min(right, radar.width), min(bottom, radar.height)
    if col0 < col1 and row0 < row1:
        values = radar.read(1, window=Window(col0, row0, col1 - col0, row1 - row0), masked=True)
        status[row0 - top:row1 - top, col0 - left:col1 - left] = values.filled(255)
    if not np.isin(status, [0, 1, 4, 255]).all():
        raise ValueError("Unexpected prototype flag for the pinned software version.")
    return classes, status


def interior(mask, radius):
    if radius == 0:
        return mask
    padded = np.pad(mask, radius, constant_values=False)
    diameter = 2 * radius + 1
    neighbourhoods = np.lib.stride_tricks.sliding_window_view(padded, (diameter, diameter))
    return neighbourhoods.all(axis=(-2, -1))


def counts(group, status):
    by_code = {str(code): int(np.count_nonzero(group & (status == code))) for code in (0, 1, 4, 255)}
    assessed = by_code["0"] + by_code["1"] + by_code["4"]
    flagged = by_code["1"] + by_code["4"]
    return {
        "reference_centres": int(np.count_nonzero(group)),
        "radar_assessed": assessed,
        "radar_unavailable": by_code["255"],
        "no_flag": by_code["0"],
        "first_low_confidence": by_code["1"],
        "first_high_confidence": by_code["4"],
        "any_flag_pct_of_assessed": round(100 * flagged / assessed, 4) if assessed else None,
        "high_confidence_pct_of_assessed": round(100 * by_code["4"] / assessed, 4) if assessed else None,
    }


def analyze(root):
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with ExitStack() as stack:
            radar = open_member(stack, root, RADAR_ARCHIVE, RADAR_MEMBER)
            version = radar.tags().get("version")
            if (
                radar.crs.to_epsg() != 32611 or radar.res != (30, 30) or radar.count != 1
                or radar.dtypes != ("uint8",) or radar.nodata != 255
                or version != "0.0.4.dev448+g363460431"
            ):
                raise ValueError("Unexpected JPL prototype version or analysis grid.")
            events = {}
            for event, (archive, member) in REFERENCE_MEMBERS.items():
                reference = open_member(stack, root, archive, member)
                classes, status = aligned_reference_window(reference, radar)
                events[event] = {
                    str(radius): {
                        "high_soil_severity": counts(interior(classes == 4, radius), status),
                        "unburned_or_very_low_proxy": counts(interior(classes == 1, radius), status),
                    }
                    for radius in RADIUS_CELLS
                }
            return {
                "status_member": RADAR_MEMBER,
                "software_version": version,
                "archive_sha256": HASHES,
                "analysis_grid_metres": 30,
                "primary_square_interiors_radius_cells": PRIMARY_RADIUS_CELLS,
                "events": events,
            }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = analyze(args.input_dir)
    except (OSError, KeyError, ValueError, rasterio.errors.RasterioError) as error:
        parser.exit(1, f"Backtest did not complete: {error}\n")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
