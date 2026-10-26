"""Deterministic identities for upstream raster-cell observations.

Some alert products expose pixel values rather than provider-defined event IDs.
This module creates an explicitly ForestProof-generated identity for one source
cell/date. It must not be presented as a provider event identifier.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


_COORDINATE_QUANTUM = Decimal("0.000001")
_DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _coordinate(value: float | int | Decimal | str, *, axis: str) -> str:
    if isinstance(value, bool):
        raise ValueError(f"{axis} must be a finite WGS84 coordinate")
    raw = str(value)
    if len(raw) > 64:
        raise ValueError(f"{axis} must be a finite WGS84 coordinate")
    try:
        coordinate = Decimal(raw)
    except (InvalidOperation, ValueError):
        raise ValueError(f"{axis} must be a finite WGS84 coordinate") from None
    limit = Decimal("180") if axis == "longitude" else Decimal("90")
    if not coordinate.is_finite() or abs(coordinate) > limit:
        raise ValueError(f"{axis} must be a finite WGS84 coordinate")

    normalized = coordinate.quantize(_COORDINATE_QUANTUM, rounding=ROUND_HALF_UP)
    if normalized == 0:
        normalized = abs(normalized)  # Avoid distinct negative-zero identities.
    return format(normalized, "f")


def _observation_time(value: date | datetime | str) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("A datetime cell observation must include a timezone")
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        raise ValueError("Cell observation time must be an ISO date or timezone-aware datetime")

    text = value.strip()
    if _DATE_ONLY.fullmatch(text):
        try:
            return date.fromisoformat(text).isoformat()
        except ValueError:
            raise ValueError("Cell observation date must be a valid ISO date") from None

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Cell observation time must be an ISO date or timezone-aware datetime") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("A datetime cell observation must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def raster_cell_identity(
    *,
    source_product: str,
    longitude: float | int | Decimal | str,
    latitude: float | int | Decimal | str,
    observed_at: date | datetime | str,
) -> str:
    """Return a stable ForestProof key for one source product/cell/date.

    The source product and observation date are included; the source release
    version is intentionally stored separately as processing provenance. This
    lets callers compare the same cell across releases while preserving each
    release independently. The key is not a provider-issued event ID.
    """
    product = source_product.strip() if isinstance(source_product, str) else ""
    if not product or len(product) > 200:
        raise ValueError("source_product must be a non-empty identifier of at most 200 characters")

    identity = {
        "identity_schema": "raster-cell-v1",
        "source_product": product,
        "longitude": _coordinate(longitude, axis="longitude"),
        "latitude": _coordinate(latitude, axis="latitude"),
        "observed_at": _observation_time(observed_at),
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"forestproof:raster-cell:v1:{digest}"
