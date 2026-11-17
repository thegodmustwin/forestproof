"""Research-only EMSR345 labels on a caller-provided WGS84 raster grid.

Positive geometry is photo-interpreted fire extent.
Analysed coverage is the intersection of the AOI and the post-event SPOT
footprint, minus the provider's explicitly not-analysed areas. Neither the
remaining non-burn area nor the positive extent is a field-verified label.
"""

import hashlib
import io
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import shapefile
from rasterio.features import rasterize

from radar import ROOT

ARCHIVE = ROOT / "EMSR345_01MOUNTKENYA_01DELINEATION_MONIT01_v1_vector.zip"
EXPECTED_SHA256 = "e7aa5d47641e6a7bf5e1494da98cb637c862b04b8c94cc3ba4653414185c10c6"
DATASET_URL = "https://cems-mapping-website.s3.eu-west-1.amazonaws.com/static/activations/EMSR345/EMSR345_01MOUNTKENYA_01DELINEATION_MONIT01_v1_vector.zip"


def _layer(archive, suffix):
    names = archive.namelist()
    shp_names = [n for n in names if n.endswith("_" + suffix + ".shp")]
    if len(shp_names) != 1:
        raise ValueError("Expected exactly one matching CEMS layer")
    stem = shp_names[0][:-4]
    projection = archive.read(stem + ".prj").decode("ascii")
    if 'GCS_WGS_1984' not in projection:
        raise ValueError("CEMS layer does not declare expected WGS84")
    reader = shapefile.Reader(shp=io.BytesIO(archive.read(stem + ".shp")),
                              shx=io.BytesIO(archive.read(stem + ".shx")),
                              dbf=io.BytesIO(archive.read(stem + ".dbf")))
    for sr in reader.iterShapeRecords():
        attrs = sr.record.as_dict()
        geom = sr.shape.__geo_interface__
        if geom.get("type") not in ("Polygon", "MultiPolygon") or not geom.get("coordinates"):
            raise ValueError("Unexpected CEMS geometry")
        yield geom, attrs


def _paint(features, shape, transform):
    if not features:
        raise ValueError("Required CEMS geometry absent")
    return rasterize(((x, 1) for x in features), out_shape=shape, transform=transform,
                     fill=0, all_touched=False, dtype="uint8").astype(bool)


def build_reference(shape, transform):
    """Return (burn, analysed) boolean masks; caller guarantees EPSG:4326.

    Uses pixel-centre rasterization. The burn mask is the full mapped burn
    in the study grid; analysed is separate, so callers can compute the
    unanalysed portion and buffer against the complete mapped footprint.
    Outside coverage and not-analysed pixels are never negatives. Apply
    class-boundary buffers and independent vegetation/controls outside.
    """
    if len(shape) != 2 or any(not isinstance(x, int) or x <= 0 for x in shape):
        raise ValueError("Expected a positive 2D output shape")
    if _archive_hash() != EXPECTED_SHA256:
        raise ValueError("CEMS archive does not match the pinned research copy")
    with zipfile.ZipFile(ARCHIVE) as z:
        aoi = list(_layer(z, "area_of_interest_a"))
        event = list(_layer(z, "observed_event_a"))
        footprints = list(_layer(z, "image_footprint_a"))
    if len(aoi) != 1 or len(event) != 5:
        raise ValueError("Unexpected AOI or event feature count")
    if any(a.get("event_type") != "8-Wildfire" or
           a.get("det_method") != "Photo-interpretation" or
           str(a.get("dmg_src_id")) != "3" for _, a in event):
        raise ValueError("Unexpected CEMS event attributes")
    allowed = {"Image Footprint", "Not Analysed"}
    if any(a.get("obj_type") not in allowed for _, a in footprints):
        raise ValueError("Unexpected CEMS footprint classification")
    source3 = [g for g, a in footprints if a.get("obj_type") == "Image Footprint" and str(a.get("or_src_id")) == "3"]
    excluded = [g for g, a in footprints if a.get("obj_type") == "Not Analysed" and str(a.get("or_src_id")) == "3"]
    if len(source3) != 1 or not excluded:
        raise ValueError("Post-event footprint or exclusion geometry missing")
    aoi_mask = _paint([g for g, _ in aoi], shape, transform)
    coverage = _paint(source3, shape, transform)
    not_analysed = _paint(excluded, shape, transform)
    analysed = aoi_mask & coverage & ~not_analysed
    burn = _paint([g for g, _ in event], shape, transform)
    return burn, analysed


def _archive_hash():
    h = hashlib.sha256()
    with ARCHIVE.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def provenance():
    """Describe the source and file fingerprint without implying validation."""
    digest = _archive_hash()
    if digest != EXPECTED_SHA256:
        raise ValueError("CEMS archive does not match the pinned research copy")
    with zipfile.ZipFile(ARCHIVE) as z:
        natural = list(_layer(z, "natural_land_use_a"))
    return {
        "source": "Copernicus EMS (© 2019 EU), [EMSR345] Mount Kenya: Delineation Map, Monitoring 1",
        "url": DATASET_URL,
        "sha256": digest,
        "post_event_imagery": "SPOT-6-7, 2019-03-06T07:34:00Z; photo-interpretation",
        "natural_land_use_attributes": {str(k): dict(v) for k, v in _attribute_counts(natural).items()},
        "limitations": "Not field truth; unburned is not verified stable or forest; inspect land-use provenance and timing.",
    }


def _attribute_counts(features):
    keys = sorted({key for _, attrs in features for key in attrs})
    return {key: Counter(str(attrs.get(key)) for _, attrs in features) for key in keys}
