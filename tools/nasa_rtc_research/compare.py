"""Offline, bounded dual-polarization RTC-S1 research diagnostic.

Inputs are local files and a caller-provided manifest. No network, credentials,
individual pixel locations, alert classifications or ground-truth claims.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import date
import hashlib
import hmac
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from rasterio.windows import Window, from_bounds
from rasterio.windows import transform as window_transform


class InputError(ValueError):
    """Static, non-sensitive reason for rejecting an input."""


_NAME = re.compile(
    r"(?P<stem>OPERA_L2_RTC-S1_(?P<burst>T\d{3}-\d{6}-IW[123])_"
    r"(?P<day>\d{8})T\d{6}Z_\d{8}T\d{6}Z_"
    r"(?P<sensor>S1[A-D])_30_(?P<version>v\d+\.\d+))_"
    r"(?P<band>VV|VH|mask)\.tif"
)
_MD5 = re.compile(r"[0-9a-f]{32}")
_CONCEPT = re.compile(r"G[0-9]+-ASF")
_MAX_WINDOW_PIXELS = 500_000
_GRID_TOLERANCE = 1e-6


def _box_polygon(bounds: tuple[float, float, float, float]) -> dict:
    """Densify the WGS84 rectangle before projection."""
    west, south, east, north = bounds
    points = []
    for start, end in (
        ((west, south), (east, south)),
        ((east, south), (east, north)),
        ((east, north), (west, north)),
        ((west, north), (west, south)),
    ):
        points.extend(
            (start[0] + (end[0] - start[0]) * i / 32,
             start[1] + (end[1] - start[1]) * i / 32)
            for i in range(32)
        )
    points.append(points[0])
    return {"type": "Polygon", "coordinates": [points]}


def _bounds(raw: object) -> tuple[float, float, float, float]:
    if not isinstance(raw, list) or len(raw) != 4:
        raise InputError("A bounded WGS84 rectangle is required.")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in raw):
        raise InputError("Rectangle coordinates must be finite numbers.")
    box = tuple(float(v) for v in raw)
    west, south, east, north = box
    if (not all(math.isfinite(v) for v in box) or not -180 <= west < east <= 180
            or not -90 <= south < north <= 90 or east - west > 1 or north - south > 1):
        raise InputError("The research rectangle is invalid or too large.")
    return box


def _load_manifest(path: Path, input_dir: Path) -> tuple[tuple, dict]:
    """Validate caller metadata and authenticate each local file to its manifest.

    Checksums match the caller-supplied manifest, not an independent catalog
    unless that manifest itself has been verified separately.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise InputError("The manifest could not be read.") from exc
    if not isinstance(raw, dict) or set(raw) != {"bounds_wgs84", "assets"}:
        raise InputError("Unexpected manifest fields.")
    box = _bounds(raw["bounds_wgs84"])
    assets = raw["assets"]
    if not isinstance(assets, list) or not 9 <= len(assets) <= 90:
        raise InputError("Provide a bounded set of local acquisition assets.")
    try:
        root = input_dir.resolve(strict=True)
    except OSError as exc:
        raise InputError("The local input directory is unavailable.") from exc
    if not root.is_dir():
        raise InputError("The local input directory is unavailable.")

    days: dict[str, dict] = {}
    common_identity = None
    expected = {"day", "role", "band", "filename", "concept_id", "size_bytes", "md5", "url"}
    for item in assets:
        if not isinstance(item, dict) or set(item) != expected:
            raise InputError("Unexpected asset metadata.")
        day, role, band = item["day"], item["role"], item["band"]
        try:
            parsed_day = date.fromisoformat(day)
        except (TypeError, ValueError) as exc:
            raise InputError("An acquisition date is invalid.") from exc
        if (parsed_day.isoformat() != day or not isinstance(role, str) or not isinstance(band, str)
                or role not in {"reference", "target"} or band not in {"VV", "VH", "mask"}):
            raise InputError("An acquisition role, date or band is invalid.")
        name, concept, size, digest, url = (item[k] for k in ("filename", "concept_id", "size_bytes", "md5", "url"))
        if not isinstance(name, str) or "/" in name or "\\" in name or Path(name).name != name:
            raise InputError("Asset filenames must be local basenames.")
        match = _NAME.fullmatch(name)
        if (match is None or match["band"] != band
                or match["day"] != day.replace("-", "")
                or not isinstance(concept, str) or not _CONCEPT.fullmatch(concept)
                or isinstance(size, bool) or not isinstance(size, int) or size <= 0
                or not isinstance(digest, str) or not _MD5.fullmatch(digest)
                or not isinstance(url, str)):
            raise InputError("An asset's metadata is invalid.")
        parsed_url = urlsplit(url)
        if (parsed_url.scheme != "https" or parsed_url.netloc != "cumulus.asf.earthdatacloud.nasa.gov"
                or parsed_url.query or parsed_url.fragment or parsed_url.path.rsplit("/", 1)[-1] != name):
            raise InputError("The asset source URL is invalid.")
        identity = (match["burst"], match["sensor"], match["version"])
        if common_identity is None:
            common_identity = identity
        elif identity != common_identity:
            raise InputError("Inputs must share a burst, sensor and product version.")
        group = days.setdefault(day, {"role": role, "stem": match["stem"], "concept_id": concept, "assets": {}})
        if group["role"] != role or group["stem"] != match["stem"] or group["concept_id"] != concept or band in group["assets"]:
            raise InputError("An acquisition has conflicting or duplicate assets.")
        try:
            candidate = (root / name).resolve(strict=True)
            if candidate.parent != root or not candidate.is_file() or candidate.stat().st_size != size:
                raise InputError("An asset is missing or does not match the manifest.")
            actual = hashlib.md5(usedforsecurity=False)
            with candidate.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    actual.update(block)
            if not hmac.compare_digest(actual.hexdigest(), digest):
                raise InputError("An asset checksum does not match the manifest.")
        except OSError as exc:
            raise InputError("An asset is unavailable.") from exc
        group["assets"][band] = candidate

    if any(set(group["assets"]) != {"VV", "VH", "mask"} for group in days.values()):
        raise InputError("Every acquisition needs VV, VH and its own mask.")
    references = sorted(day for day, group in days.items() if group["role"] == "reference")
    targets = sorted(day for day, group in days.items() if group["role"] == "target")
    if len(references) < 2 or not targets or references[-1] >= targets[0]:
        raise InputError("At least two earlier reference acquisitions and one target are required.")
    return box, days


def _quantiles(values: np.ndarray) -> dict:
    """Fixed descriptive quantiles; one observation per eligible pixel."""
    names = ("min", "p05", "p25", "median", "p75", "p95", "max")
    percentiles = np.percentile(values, [0, 5, 25, 50, 75, 95, 100])
    return {name: round(float(value), 6) for name, value in zip(names, percentiles)}


def analyze(manifest_path: Path, input_dir: Path) -> dict:
    """Compare signed per-pixel dB deviations on a common conservative mask."""
    box, days = _load_manifest(Path(manifest_path), Path(input_dir))
    references = sorted(day for day in days if days[day]["role"] == "reference")
    targets = sorted(day for day in days if days[day]["role"] == "target")

    with ExitStack() as stack:
        datasets = {
            (day, band): stack.enter_context(rasterio.open(path))
            for day, group in days.items() for band, path in group["assets"].items()
        }
        anchor = datasets[(references[0], "VV")]
        affine = anchor.transform
        if (anchor.crs is None or not anchor.crs.is_projected
                or anchor.crs.linear_units != "metre"
                or abs(affine.a - 30) > _GRID_TOLERANCE
                or abs(affine.e + 30) > _GRID_TOLERANCE
                or abs(affine.b) > _GRID_TOLERANCE or abs(affine.d) > _GRID_TOLERANCE):
            raise InputError("An unsupported reference grid was supplied.")
        offsets = {}
        for key, ds in datasets.items():
            if (ds.driver != "GTiff" or ds.count != 1 or ds.crs != anchor.crs
                    or abs(ds.transform.a - affine.a) > _GRID_TOLERANCE
                    or abs(ds.transform.e - affine.e) > _GRID_TOLERANCE
                    or abs(ds.transform.b) > _GRID_TOLERANCE or abs(ds.transform.d) > _GRID_TOLERANCE):
                raise InputError("Raster coordinate systems or pixel sizes differ.")
            if ds.dtypes[0] != ("uint8" if key[1] == "mask" else "float32"):
                raise InputError("A raster band has an unexpected data type.")
            col_shift = (ds.transform.c - affine.c) / affine.a
            row_shift = (ds.transform.f - affine.f) / affine.e
            if (abs(col_shift - round(col_shift)) > _GRID_TOLERANCE
                    or abs(row_shift - round(row_shift)) > _GRID_TOLERANCE):
                raise InputError("Raster grids are not aligned to whole pixels.")
            offsets[key] = (int(round(col_shift)), int(round(row_shift)))

        # All three assets of one acquisition are declared to be the same
        # granule; a different extent within it is suspicious, even when its
        # origin happens to land on an integer pixel of the global grid.
        for day in days:
            day_grid = datasets[(day, "VV")]
            for band in ("VH", "mask"):
                other = datasets[(day, band)]
                if (other.transform != day_grid.transform or other.width != day_grid.width
                        or other.height != day_grid.height):
                    raise InputError("Bands within an acquisition have different grids.")

        geom = transform_geom("EPSG:4326", anchor.crs, _box_polygon(box))
        xs, ys = zip(*geom["coordinates"][0])
        requested = from_bounds(min(xs), min(ys), max(xs), max(ys), affine)
        anchor_col0, anchor_row0 = max(0, math.floor(requested.col_off)), max(0, math.floor(requested.row_off))
        anchor_col1 = min(anchor.width, math.ceil(requested.col_off + requested.width))
        anchor_row1 = min(anchor.height, math.ceil(requested.row_off + requested.height))
        if anchor_col1 <= anchor_col0 or anchor_row1 <= anchor_row0:
            raise InputError("The reference raster does not intersect the research box.")
        if (anchor_col1 - anchor_col0) * (anchor_row1 - anchor_row0) > _MAX_WINDOW_PIXELS:
            raise InputError("The requested processing window is too large.")
        anchor_window = Window(anchor_col0, anchor_row0, anchor_col1 - anchor_col0, anchor_row1 - anchor_row0)
        anchor_inside = geometry_mask(
            [geom], out_shape=(int(anchor_window.height), int(anchor_window.width)),
            transform=window_transform(anchor_window, affine), invert=True, all_touched=False,
        )
        col0, row0, col1, row1 = anchor_col0, anchor_row0, anchor_col1, anchor_row1
        for key, ds in datasets.items():
            dc, dr = offsets[key]
            col0, row0 = max(col0, dc), max(row0, dr)
            col1, row1 = min(col1, dc + ds.width), min(row1, dr + ds.height)
        if col1 <= col0 or row1 <= row0:
            raise InputError("The rasters have no common research-box coverage.")
        if (col1 - col0) * (row1 - row0) > _MAX_WINDOW_PIXELS:
            raise InputError("The requested processing window is too large.")
        base_window = Window(col0, row0, col1 - col0, row1 - row0)
        inside = geometry_mask(
            [geom], out_shape=(int(base_window.height), int(base_window.width)),
            transform=window_transform(base_window, affine), invert=True, all_touched=False,
        )
        if not inside.any():
            raise InputError("No common pixel centres fall inside the research box.")

        raw = {}
        for key, ds in datasets.items():
            dc, dr = offsets[key]
            window = Window(col0 - dc, row0 - dr, col1 - col0, row1 - row0)
            raw[key] = ds.read(1, window=window, masked=True)

    # Each image must be reliable for both polarizations and its own geometry
    # mask; use the same common pixels across every target and reference.
    eligible = inside.copy()
    per_acquisition = []
    for day in sorted(days):
        mask = raw[(day, "mask")]
        available_mask = inside & ~np.ma.getmaskarray(mask)
        mask_values = mask.data[available_mask]
        if not np.isin(mask_values, [0, 1, 2, 3, 255]).all():
            raise InputError("An acquisition contains unsupported mask codes.")
        day_valid = available_mask & (mask.data == 0)
        mask_counts = {
            str(code): int((available_mask & (mask.data == code)).sum())
            for code in (0, 1, 2, 3, 255)
        }
        missing_mask = int((inside & ~available_mask).sum())
        per_band = {}
        for band in ("VV", "VH"):
            arr = raw[(day, band)]
            valid = ~np.ma.getmaskarray(arr) & np.isfinite(arr.data) & (arr.data > 0)
            per_band[band] = {
                "finite_positive_inside": int((inside & valid).sum()),
                "missing_nonfinite_or_nonpositive_inside": int((inside & ~valid).sum()),
            }
            day_valid &= valid
        per_acquisition.append({
            "day": day, "role": days[day]["role"], "concept_id": days[day]["concept_id"],
            "mask_codes_inside": mask_counts, "missing_mask_inside": missing_mask,
            "bands": per_band, "both_bands_and_mask0_inside": int(day_valid.sum()),
        })
        eligible &= day_valid

    common_count = int(eligible.sum())
    result = {
        "scope": "offline_research_only",
        "method": "10*log10(gamma0 power); per-pixel median of reference dB; target minus median",
        "checksum_note": "MD5 and sizes matched supplied manifest; manifest authenticity is not established by this tool.",
        "anchor_box_pixel_centres": int(anchor_inside.sum()),
        "intersection_pixel_centres": int(inside.sum()),
        "anchor_box_centres_outside_common_extent": int(anchor_inside.sum() - inside.sum()),
        "common_all_acquisitions_pixel_centres": common_count,
        "reference_count": len(references),
        "reference_days": references,
        "target_days": targets,
        "acquisitions": per_acquisition,
        "polarizations": {},
        "caveats": [
            "The caller-supplied rectangle is research geography and is not an official boundary.",
            "Results cover only aligned common pixel centres; coverage outside the intersection is unknown.",
            "Mask code 0 excludes layover and shadow but does not prove forest, ground truth or stable moisture.",
            "Backscatter deviation is not an alert, cause, deforestation, illegality or an area-loss estimate.",
            "Leave-one-out references overlap and are dependent; their quantiles are not confidence intervals or independent validation.",
            "No network request, provider authentication or operational live feed was used.",
        ],
    }
    if common_count == 0:
        result["outcome"] = "NO_COMMON_VALID_PIXELS"
        return result
    for band in ("VV", "VH"):
        refs = np.stack([10.0 * np.log10(raw[(day, band)].data[eligible].astype(np.float64))
                         for day in references])
        baseline = np.median(refs, axis=0)
        target_stats = {}
        for day in targets:
            target = 10.0 * np.log10(raw[(day, band)].data[eligible].astype(np.float64))
            target_stats[day] = _quantiles(target - baseline)
        loo_stats = {}
        for index, day in enumerate(references):
            other_median = np.median(np.delete(refs, index, axis=0), axis=0)
            loo_stats[day] = _quantiles(refs[index] - other_median)
        result["polarizations"][band] = {
            "units": "dB",
            "eligible_pixel_centres": common_count,
            "target_minus_reference_median": target_stats,
            "leave_one_reference_out_minus_other_reference_median": loo_stats,
        }
    result["outcome"] = "DESCRIPTIVE_COMPARISON_ONLY"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(analyze(args.manifest, args.input_dir), indent=2, allow_nan=False))
    except InputError as exc:
        print(f"Inspection did not complete: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("Inspection did not complete; check inputs privately.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
