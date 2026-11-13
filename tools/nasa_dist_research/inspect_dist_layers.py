"""Offline research: bounded aggregate NASA DIST-HLS V1 layer cross-check.

No alerts, claims of forest loss or individual pixel locations are produced.
All inputs must belong to the same local granule and the provisional research
rectangle is not an official boundary.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from rasterio.windows import Window, from_bounds
from rasterio.windows import transform as window_transform
def _box_polygon(bounds, segments=32):
    """Densify WGS84 rectangle edges for reprojection; no boundary is implied."""
    try:
        west, south, east, north = (float(x) for x in bounds)
    except (TypeError, ValueError):
        raise ValueError("Four finite WGS84 bounds are required") from None
    if (not all(math.isfinite(x) for x in (west, south, east, north))
            or not (-180 <= west < east <= 180 and -90 <= south < north <= 90)
            or east - west > 1 or north - south > 1):
        raise ValueError("WGS84 bounds must be ordered and no larger than one degree")
    points = []
    for a, b in (((west, south), (east, south)), ((east, south), (east, north)),
                 ((east, north), (west, north)), ((west, north), (west, south))):
        points.extend([(a[0] + (b[0] - a[0]) * i / segments,
                        a[1] + (b[1] - a[1]) * i / segments)
                       for i in range(segments)])
    points.append(points[0])
    return {"type": "Polygon", "coordinates": [points]}

LAYERS = {
    'status': ('VEG-DIST-STATUS', 'uint8', 255),
    'first_date': ('VEG-DIST-DATE', 'int16', -1),
    'last_date': ('VEG-LAST-DATE', 'int16', -1),
    'mask': ('DATA-MASK', 'uint8', 255),
}
EPOCH = date(2020, 12, 31)


def _sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _counts(values):
    keys, counts = np.unique(values, return_counts=True)
    return {str(int(k)): int(v) for k, v in zip(keys, counts)}


def _span(values):
    positive = values[values > 0]
    if not positive.size:
        return None
    return {'earliest': (EPOCH + timedelta(days=int(positive.min()))).isoformat(),
            'latest': (EPOCH + timedelta(days=int(positive.max()))).isoformat(),
            'pixels_with_date': int(positive.size)}


def analyze(paths, bounds):
    paths = {name: Path(paths[name]) for name in LAYERS if paths.get(name) is not None}
    if 'status' not in paths or len(paths) < 2:
        raise ValueError('Status plus at least one additional layer required')
    prefix = None
    for name in paths:
        suffix, _, _ = LAYERS[name]
        expected = '_' + suffix + '.tif'
        path = paths[name]
        if not path.is_file() or not path.name.endswith(expected):
            raise ValueError('Input layer missing or filename suffix invalid')
        this_prefix = path.name[:-len(expected)]
        if prefix is None:
            prefix = this_prefix
        if this_prefix != prefix:
            raise ValueError('Layers do not belong to the same granule')
    match = re.fullmatch(r'OPERA_L3_DIST-ALERT-HLS_T\d{2}[A-Z]{3}_(\d{8})T\d{6}Z_\d{8}T\d{6}Z_(?:L8|L9|S2A|S2B|S2C)_30_v1', prefix)
    if not match:
        raise ValueError('Unexpected OPERA granule name')
    acquisition = date.fromisoformat(f'{match[1][:4]}-{match[1][4:6]}-{match[1][6:8]}')
    max_day = (acquisition - EPOCH).days
    with ExitStack() as stack:
        datasets = {name: stack.enter_context(rasterio.open(path)) for name, path in paths.items()}
        base = datasets['status']
        if base.crs is None or base.transform.b != 0 or base.transform.d != 0:
            raise ValueError('Missing CRS or unsupported rotated raster')
        for name, ds in datasets.items():
            if (ds.count != 1 or ds.dtypes != (LAYERS[name][1],) or ds.crs != base.crs
                    or ds.transform != base.transform or ds.width != base.width or ds.height != base.height):
                raise ValueError('Layer grids or data types do not match')
        geom = transform_geom('EPSG:4326', base.crs, _box_polygon(bounds))
        xs, ys = zip(*geom['coordinates'][0])
        raw = from_bounds(min(xs), min(ys), max(xs), max(ys), base.transform)
        col0, row0 = max(0, math.floor(raw.col_off)), max(0, math.floor(raw.row_off))
        col1 = min(base.width, math.ceil(raw.col_off + raw.width))
        row1 = min(base.height, math.ceil(raw.row_off + raw.height))
        if col1 <= col0 or row1 <= row0:
            raise ValueError('Tile does not intersect the research rectangle')
        if (col1 - col0) * (row1 - row0) > 4_000_000:
            raise ValueError('Research window exceeds the pixel limit')
        window = Window(col0, row0, col1-col0, row1-row0)
        inside = geometry_mask([geom], out_shape=(int(window.height), int(window.width)),
                               transform=window_transform(window, base.transform), invert=True)
        arrays = {name: ds.read(1, window=window, masked=True) for name, ds in datasets.items()}
        if not inside.any():
            raise ValueError('No pixel centres in the intersection')
        values = {name: a.data[inside] for name, a in arrays.items()}
        missing = {name: np.ma.getmaskarray(a)[inside] | (values[name] == LAYERS[name][2])
                   for name, a in arrays.items()}
        for name in ('status', 'mask'):
            if name not in values:
                continue
            legal = set(range(9)) if name == 'status' else {0, 1, 2}
            if any(int(x) not in legal for x in np.unique(values[name][~missing[name]])):
                raise ValueError('Unexpected status or mask code')
        for name in ('first_date', 'last_date'):
            if name not in values:
                continue
            present = values[name][~missing[name]]
            if np.any(present < 0) or np.any(present > max_day) or (name == 'last_date' and np.any(present == 0)):
                raise ValueError('Date value falls outside product specification or acquisition date')
        valid_all = ~np.logical_or.reduce(list(missing.values()))
        result = {
            'granule': prefix, 'acquisition_date': acquisition.isoformat(),
            'file_sha256': {name: _sha(path) for name, path in paths.items()},
            'intersection_pixel_centres': int(inside.sum()),
            'layer_missing_counts': {name: int(mask.sum()) for name, mask in missing.items()},
            'status_counts_all': _counts(values['status'][~missing['status']]),
            'all_supplied_layers_present_count': int(valid_all.sum()),
            'caveats': ['One tile intersection of a user-supplied research rectangle, not an official boundary.',
                'Dates are source detection/last quality-assessed observation dates, not exact event dates.',
                'DATA-MASK is a scene processing mask, not complete cloud quality, forest cover, or historical quality.',
                'Vegetation disturbance status does not prove deforestation, illegality or ground conditions.',
                'Other tile, quality bands and field verification were not checked.'],
        }
        if 'mask' in values:
            paired = ~missing['status'] & ~missing['mask']
            result['land_water_processing_mask_counts'] = _counts(values['mask'][~missing['mask']])
            result['status_by_scene_mask_for_status_and_mask_present'] = {
                str(code): _counts(values['status'][paired & (values['mask'] == code)])
                for code in (0, 1, 2)
            }
            result['status_and_mask_present_count'] = int(paired.sum())
        if 'first_date' in values:
            paired = ~missing['status'] & ~missing['first_date']
            active = paired & (values['status'] > 0)
            result['status_and_first_date_present_count'] = int(paired.sum())
            result['disturbance_status_first_detection_span'] = _span(values['first_date'][active])
            result['first_detection_span_by_status'] = {
                str(code): _span(values['first_date'][active & (values['status'] == code)])
                for code in range(1, 9)
            }
            result['positive_status_with_no_initial_date_count'] = int((active & (values['first_date'] == 0)).sum())
        if 'last_date' in values:
            result['all_valid_last_assessed_span'] = _span(values['last_date'][~missing['last_date']])
        if 'first_date' in values and 'last_date' in values:
            comparable = ~missing['status'] & ~missing['first_date'] & ~missing['last_date']
            result['positive_status_last_before_first_count'] = int((comparable & (values['status'] > 0) & (values['first_date'] > 0) & (values['last_date'] < values['first_date'])).sum())
        return result


def main():
    parser = argparse.ArgumentParser(description='Bounded local synthetic/research-only NASA layer inspection')
    for name in LAYERS:
        parser.add_argument('--' + name.replace('_', '-'), type=Path, required=name == 'status')
    parser.add_argument('--bounds', type=float, nargs=4, required=True,
                        metavar=('WEST', 'SOUTH', 'EAST', 'NORTH'))
    args = parser.parse_args()
    paths = {name: getattr(args, name) for name in LAYERS}
    try:
        print(json.dumps(analyze(paths, args.bounds), indent=2))
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        print('Inspection did not complete:', type(exc).__name__)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

