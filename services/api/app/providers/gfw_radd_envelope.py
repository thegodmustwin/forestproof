"""Offline candidate parser for GFW RADD query responses.

This implements the success envelope described by WRI's public API source at
commit dd277b245debf8e37a98a8e6238c5ead8aeed115. It does not make a network
request, verify the deployed service, activate LIVE, or infer provider health.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .gfw_radd import RaddRasterCell, normalize_radd_pixel_row


MAX_ENVELOPE_ROWS = 1_000
MAX_ENVELOPE_BYTES = 2_000_000
_CONCRETE_RELEASE = re.compile(r"^v\d{1,8}(?:\.\d{1,3}){0,2}$")


@dataclass(frozen=True)
class RaddQueryEnvelope:
    source_version: str
    cells: tuple[RaddRasterCell, ...]
    raw_envelope: dict[str, Any]


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def decode_radd_response(raw: bytes) -> Any:
    """Decode one bounded UTF-8 response without discarding duplicate fields."""
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_ENVELOPE_BYTES:
        raise ValueError("Invalid GFW response size")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_object)
    except (ValueError, RecursionError):
        raise ValueError("Invalid GFW response JSON") from None


def _check_json_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            _check_json_keys(child)
    elif isinstance(value, list):
        for child in value:
            _check_json_keys(child)


def parse_radd_query_envelope(payload: Any, *, source_version: str) -> RaddQueryEnvelope:
    """Parse a bounded, successful cell query response using synthetic inputs.

    A concrete release is required; an alias such as 'latest' is not stable
    provenance. Empty data means only that this query returned no rows. It does
    not establish coverage, completeness, source health, or absence of alerts.
    The parsed envelope is copied, not the original HTTP response bytes.
    """
    if not isinstance(source_version, str) or not _CONCRETE_RELEASE.fullmatch(source_version):
        raise ValueError("A concrete GFW source release is required")
    if not isinstance(payload, dict) or payload.get("status") != "success":
        raise ValueError("A successful GFW response envelope is required")
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ValueError("GFW response data must be an array of cell rows")
    if len(rows) > MAX_ENVELOPE_ROWS:
        raise ValueError("GFW response exceeds the offline row limit")

    try:
        _check_json_keys(payload)
        encoded = json.dumps(
            payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError):
        raise ValueError("GFW response must be valid UTF-8 JSON") from None
    if len(encoded) > MAX_ENVELOPE_BYTES:
        raise ValueError("GFW response exceeds the offline size limit")

    copied = json.loads(encoded)
    cells = tuple(
        normalize_radd_pixel_row(row, source_version=source_version)
        for row in copied["data"]
    )
    return RaddQueryEnvelope(source_version=source_version, cells=cells, raw_envelope=copied)
