"""Bounded, read-only Sentinel-2 scene context for an opt-in owner demo.

Scenes are acquisitions, not disturbance detections. This module does not
download imagery, create case observations, authenticate to a provider, or
make claims about the official Geta boundary or complete area coverage.
"""

from __future__ import annotations

import copy
import http.client
import json
import math
import re
import threading
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


CATALOG_URL = "https://stac.dataspace.copernicus.eu/v1/search"
COLLECTION = "sentinel-2-l2a"
# PFMP-text-derived research rectangle, not an official forest boundary.
RESEARCH_BOUNDS = (36.5, -0.7, 36.7, -0.25)
SCENE_LIMIT = 3
MAX_RESPONSE_BYTES = 256 * 1024
CACHE_SECONDS = 15 * 60
_ID = re.compile(r"[A-Za-z0-9_.-]{1,200}")


class CatalogUnavailable(RuntimeError):
    """The catalog is unavailable or returned an unsupported response."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _utc_time(value: Any) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError("Invalid scene timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Scene timestamp requires a timezone")
    return parsed.astimezone(UTC)


def _intersects_research_bounds(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError("Invalid scene bounding box")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in value):
        raise ValueError("Invalid scene bounding box")
    west, south, east, north = value
    if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
        raise ValueError("Invalid scene bounding box")
    area_west, area_south, area_east, area_north = RESEARCH_BOUNDS
    return west <= area_east and east >= area_west and south <= area_north and north >= area_south


def fetch_recent_scenes(*, now: datetime | None = None) -> dict[str, Any]:
    """Fetch one small public STAC search; never download imagery or retry.

    The request is fixed to a source, area, 30-day window and three results.
    Only selected metadata fields are requested and returned to the caller.
    """
    current = (now or datetime.now(UTC)).astimezone(UTC)
    start = current - timedelta(days=30)
    params = {
        "collections": COLLECTION,
        "bbox": ",".join(str(value) for value in RESEARCH_BOUNDS),
        "datetime": f"{start.isoformat().replace('+00:00', 'Z')}/{current.isoformat().replace('+00:00', 'Z')}",
        "limit": str(SCENE_LIMIT),
        "sortby": "-properties.datetime",
        "fields": "id,type,collection,bbox,properties.datetime,properties.platform,properties.eo:cloud_cover",
    }
    request = Request(f"{CATALOG_URL}?{urlencode(params)}", headers={
        "Accept": "application/geo+json, application/json", "Accept-Encoding": "identity",
        "User-Agent": "ForestProof-Catalog-Context/1.0",
    })
    try:
        with build_opener(_NoRedirect()).open(request, timeout=10) as response:
            if response.status != 200:
                raise CatalogUnavailable("The satellite catalog returned an error")
            length = response.headers.get("Content-Length")
            if length is not None and (len(str(length)) > 10 or not str(length).isascii() or not str(length).isdigit() or int(length) > MAX_RESPONSE_BYTES):
                raise CatalogUnavailable("The satellite catalog response was too large")
            media = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if media not in {"application/json", "application/geo+json"} or response.headers.get("Content-Encoding", "identity").lower() not in {"", "identity"}:
                raise CatalogUnavailable("The satellite catalog returned an unsupported response")
            deadline = time.monotonic() + 20
            body_buffer = bytearray()
            read_chunk = getattr(response, "read1", response.read)
            while True:
                if time.monotonic() > deadline:
                    raise CatalogUnavailable("The satellite catalog response took too long")
                chunk = read_chunk(min(16_384, MAX_RESPONSE_BYTES + 1 - len(body_buffer)))
                if time.monotonic() > deadline:
                    raise CatalogUnavailable("The satellite catalog response took too long")
                if not isinstance(chunk, bytes):
                    raise CatalogUnavailable("The satellite catalog returned an unsupported response")
                if not chunk:
                    break
                body_buffer.extend(chunk)
                if len(body_buffer) > MAX_RESPONSE_BYTES:
                    raise CatalogUnavailable("The satellite catalog response was too large")
            body = bytes(body_buffer)
            if length is not None and len(body) != int(length):
                raise CatalogUnavailable("The satellite catalog response was too large or incomplete")
    except HTTPError as error:
        error.close()
        raise CatalogUnavailable("The satellite catalog returned an error") from None
    except (URLError, TimeoutError, OSError, http.client.HTTPException):
        raise CatalogUnavailable("The satellite catalog could not be reached") from None

    try:
        payload = json.loads(body.decode("utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
            raise ValueError("Invalid scene collection")
        if len(payload["features"]) > SCENE_LIMIT:
            raise ValueError("Too many scenes")
        scenes = []
        seen: set[str] = set()
        for feature in payload["features"]:
            if not isinstance(feature, dict) or feature.get("type") != "Feature" or feature.get("collection") != COLLECTION:
                raise ValueError("Invalid scene")
            scene_id = feature.get("id")
            if not isinstance(scene_id, str) or not _ID.fullmatch(scene_id) or scene_id in seen:
                raise ValueError("Invalid scene ID")
            seen.add(scene_id)
            if not _intersects_research_bounds(feature.get("bbox")):
                raise ValueError("Scene does not overlap the requested rectangle")
            properties = feature.get("properties")
            if not isinstance(properties, dict):
                raise ValueError("Scene metadata is missing")
            acquired = _utc_time(properties.get("datetime"))
            if not start <= acquired <= current:
                raise ValueError("Scene date is outside the requested window")
            cloud = properties.get("eo:cloud_cover")
            if cloud is not None and (isinstance(cloud, bool) or not isinstance(cloud, (int, float)) or not math.isfinite(cloud) or not 0 <= cloud <= 100):
                raise ValueError("Invalid scene cloud cover")
            platform = properties.get("platform")
            if platform is not None and (not isinstance(platform, str) or not _ID.fullmatch(platform)):
                raise ValueError("Invalid platform")
            scenes.append({"id": scene_id, "acquired_at": acquired.isoformat().replace("+00:00", "Z"),
                           "platform": platform, "scene_cloud_cover_percent": cloud})
        scenes.sort(key=lambda item: item["acquired_at"], reverse=True)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError, OverflowError, RecursionError):
        raise CatalogUnavailable("The satellite catalog returned invalid or unsupported metadata") from None

    return {
        "source": "Copernicus Data Space Ecosystem STAC",
        "collection": COLLECTION,
        "checked_at": current.isoformat().replace("+00:00", "Z"),
        "window_start": start.isoformat().replace("+00:00", "Z"),
        "region_label": "Provisional Geta-area research rectangle",
        "notice": "Scenes were returned for a broad research rectangle, not an official forest boundary. Bounding-box overlap does not prove complete area coverage. A scene is not a forest-loss alert; scene-wide cloud cover is not local cloud cover. Results may be incomplete.",
        "attribution": "Copernicus Sentinel data [year of acquisition]",
        "scenes": scenes,
    }


class CopernicusCatalog:
    """Limit successful and failed lookups to one per 15 minutes per process."""

    def __init__(self, fetcher: Callable[[], dict[str, Any]] = fetch_recent_scenes,
                 clock: Callable[[], float] = time.monotonic):
        self._fetcher = fetcher
        self._clock = clock
        self._lock = threading.Lock()
        self._next_attempt = 0.0
        self._snapshot: dict[str, Any] | None = None

    def latest(self) -> dict[str, Any]:
        with self._lock:
            current = self._clock()
            if current < self._next_attempt:
                if self._snapshot is None:
                    raise CatalogUnavailable("The satellite catalog is temporarily unavailable; try again later")
                return copy.deepcopy(self._snapshot)
            self._next_attempt = current + CACHE_SECONDS
            # A failed refresh must never make a previous result look current.
            self._snapshot = None
            try:
                self._snapshot = self._fetcher()
            except CatalogUnavailable:
                self._snapshot = None
                raise
            return copy.deepcopy(self._snapshot)
