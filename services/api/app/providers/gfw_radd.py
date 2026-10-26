"""Normalize one documented GFW RADD raster-cell row without making requests.

The public field catalog names are known, but the provider's live response
envelope and field semantics have not been verified. This parser therefore
accepts a single field-to-value mapping, preserves source values, and does not
claim that a cell is an event or legal finding.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Any, Mapping

from .raster_identity import raster_cell_identity


RADD_PRODUCT = "wur_radd_alerts"


@dataclass(frozen=True)
class RaddRasterCell:
    """Normalized reference to one provider raster cell on one observation date."""

    forestproof_id: str
    source_product: str
    source_version: str
    longitude: float
    latitude: float
    observed_on: date
    confidence_value: Any
    date_confidence_value: Any
    source_area_ha: float | None
    raw_fields: dict[str, Any]


def _number(row: Mapping[str, Any], field: str, *, lower: float, upper: float) -> float:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    if not lower <= value <= upper:
        raise ValueError(f"{field} must be between {lower} and {upper}")
    return float(value)


def normalize_radd_pixel_row(row: Mapping[str, Any], *, source_version: str) -> RaddRasterCell:
    """Normalize a single RADD field map; this does not parse an HTTP envelope.

    Confidence and date-confidence are retained without interpretation because
    the catalog response does not define their value semantics. The source
    version is persisted separately from the stable cell/date identity.
    """
    if not isinstance(row, Mapping):
        raise ValueError("RADD pixel row must be a field-to-value mapping")
    if not isinstance(source_version, str) or not source_version.strip() or len(source_version) > 80:
        raise ValueError("source_version must be a non-empty source release identifier")

    longitude = _number(row, "longitude", lower=-180, upper=180)
    latitude = _number(row, "latitude", lower=-90, upper=90)
    raw_date = row.get("wur_radd_alerts__date")
    if not isinstance(raw_date, str):
        raise ValueError("wur_radd_alerts__date must be an ISO calendar date")
    try:
        observed_on = date.fromisoformat(raw_date)
    except ValueError:
        raise ValueError("wur_radd_alerts__date must be a valid ISO calendar date") from None

    raw_area = row.get("area__ha")
    if raw_area is None:
        source_area_ha = None
    elif isinstance(raw_area, bool) or not isinstance(raw_area, (int, float)) or not isfinite(raw_area) or raw_area < 0:
        raise ValueError("area__ha must be a finite non-negative number when present")
    else:
        source_area_ha = float(raw_area)

    return RaddRasterCell(
        forestproof_id=raster_cell_identity(
            source_product=RADD_PRODUCT,
            longitude=longitude,
            latitude=latitude,
            observed_at=observed_on,
        ),
        source_product=RADD_PRODUCT,
        source_version=source_version.strip(),
        longitude=longitude,
        latitude=latitude,
        observed_on=observed_on,
        confidence_value=row.get("wur_radd_alerts__confidence"),
        date_confidence_value=row.get("wur_radd_alerts__date_conf"),
        source_area_ha=source_area_ha,
        raw_fields=dict(row),
    )
