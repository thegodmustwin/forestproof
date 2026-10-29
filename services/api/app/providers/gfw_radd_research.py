"""Bounded, disabled-by-default groundwork for a GFW RADD research request.

This module is not connected to any application route or background worker.
It does not activate LIVE ingestion or establish provider access, coverage,
terms, quota, price, query semantics, or response compatibility. The request
shape is a candidate based on WRI's published source and public field catalog.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import math
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .gfw_radd_envelope import MAX_ENVELOPE_BYTES, RaddQueryEnvelope, parse_radd_query_envelope


_API_ORIGIN = "https://data-api.globalforestwatch.org"
_RELEASE = re.compile(r"^v\d{1,8}(?:\.\d{1,3}){0,2}$")
_HOST = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$", re.IGNORECASE)
_MAX_SIDE_DEGREES = 0.01
_MAX_ROWS = 100
_TIMEOUT_SECONDS = 10
_TOTAL_SECONDS = 30


class QueryNotAuthorized(ValueError):
    """An explicitly reviewed research prerequisite is missing."""


class ProviderQueryError(RuntimeError):
    """A provider request or response failed without exposing its contents."""


class ProviderRateLimited(ProviderQueryError):
    """The provider returned HTTP 429; callers must not retry automatically."""


class ResponseIncomplete(ProviderQueryError):
    """The response reached the row cap and must not be treated as complete."""


@dataclass(frozen=True)
class ResearchPrerequisites:
    """Caller attestations, not proof; production needs an audited evidence gate.

    Defaults deliberately deny requests. Every field must be explicitly True
    after review. In particular, the owner has requested no additional paid
    feed service; the fee flag cannot be inferred from a dataset license.
    """

    owner_authorized: bool = False
    service_terms_verified: bool = False
    no_additional_service_fees_verified: bool = False
    attribution_verified: bool = False
    retention_verified: bool = False
    area_use_verified: bool = False
    coverage_verified: bool = False

    def require_approved(self) -> None:
        missing = [name for name in self.__dataclass_fields__ if getattr(self, name) is not True]
        if missing:
            raise QueryNotAuthorized("Unverified research prerequisites: " + ", ".join(missing))


@dataclass(frozen=True)
class ResearchBounds:
    """A small WGS84 rectangle for a bounded research request, not a boundary."""

    west: float
    south: float
    east: float
    north: float

    def polygon(self) -> dict[str, Any]:
        values = (self.west, self.south, self.east, self.north)
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
            raise ValueError("Research bounds must contain finite numeric coordinates")
        if not (-180 <= self.west < self.east <= 180 and -90 <= self.south < self.north <= 90):
            raise ValueError("Research bounds must be an ordered WGS84 rectangle")
        if self.east - self.west > _MAX_SIDE_DEGREES + 1e-12 or self.north - self.south > _MAX_SIDE_DEGREES + 1e-12:
            raise ValueError("Research bounds exceed the small-request limit")
        return {"type": "Polygon", "coordinates": [[[self.west, self.south], [self.east, self.south],
                [self.east, self.north], [self.west, self.north], [self.west, self.south]]]}


@dataclass(frozen=True)
class ResearchQueryResult:
    source_version: str
    received_at: datetime
    raw_sha256: str
    raw_response: bytes = field(repr=False)
    envelope: RaddQueryEnvelope = field(repr=False)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        # Never forward a provider key to a redirected destination.
        return None


def _origin(value: str | None) -> str | None:
    if value is None:
        return None
    if (not isinstance(value, str) or len(value) > 300 or value != value.strip()
            or any(ord(char) <= 32 or ord(char) == 127 for char in value)):
        raise ValueError("Origin must be an HTTPS origin")
    try:
        parsed = urlsplit(value)
        host, port = parsed.hostname, parsed.port
    except ValueError:
        raise ValueError("Origin must be an HTTPS origin") from None
    if (parsed.scheme != "https" or not host or not host.isascii() or not _HOST.fullmatch(host)
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("Origin must be an HTTPS origin")
    return f"https://{host}" + (f":{port}" if port is not None else "")


def _read_limited(response: Any) -> bytes:
    length = response.headers.get("Content-Length")
    if length is not None:
        if (len(str(length)) > 10 or not str(length).isascii() or not str(length).isdigit()
                or int(length) > MAX_ENVELOPE_BYTES):
            raise ProviderQueryError("Provider response exceeds the permitted size or has invalid length")
    encoding = response.headers.get("Content-Encoding", "identity").lower()
    if encoding not in ("", "identity"):
        raise ProviderQueryError("Provider returned an unsupported content encoding")
    media = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if media != "application/json":
        raise ProviderQueryError("Provider response was not JSON")
    deadline = time.monotonic() + _TOTAL_SECONDS
    body = bytearray()
    while True:
        if time.monotonic() > deadline:
            raise ProviderQueryError("Provider response exceeded the total time limit")
        chunk = response.read(min(65_536, MAX_ENVELOPE_BYTES + 1 - len(body)))
        if time.monotonic() > deadline:
            raise ProviderQueryError("Provider response exceeded the total time limit")
        if not isinstance(chunk, bytes):
            raise ProviderQueryError("Provider response was not a byte stream")
        if not chunk:
            break
        body.extend(chunk)
        if len(body) > MAX_ENVELOPE_BYTES:
            raise ProviderQueryError("Provider response exceeds the permitted size")
    if length is not None and len(body) != int(length):
        raise ProviderQueryError("Provider response length did not match its header")
    return bytes(body)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def fetch_radd_research(
    *,
    source_version: str,
    bounds: ResearchBounds,
    api_key: str,
    prerequisites: ResearchPrerequisites,
    max_rows: int = _MAX_ROWS,
    origin: str | None = None,
) -> ResearchQueryResult:
    """Make one bounded request only after explicit review; never auto-retry.

    Uses system TLS and inherited proxy settings. No credential is placed in
    the URL or error messages, redirects are rejected, and no response is
    persisted. Tests replace the opener internally with a synthetic transport.
    """
    if not isinstance(prerequisites, ResearchPrerequisites):
        raise QueryNotAuthorized("Explicit research prerequisites are required")
    prerequisites.require_approved()
    if not isinstance(source_version, str) or not _RELEASE.fullmatch(source_version):
        raise ValueError("A concrete GFW source release is required")
    if not isinstance(bounds, ResearchBounds):
        raise ValueError("Research bounds are required")
    geometry = bounds.polygon()
    if isinstance(max_rows, bool) or not isinstance(max_rows, int) or not 1 <= max_rows <= _MAX_ROWS:
        raise ValueError(f"max_rows must be between 1 and {_MAX_ROWS}")
    if not isinstance(api_key, str) or not 1 <= len(api_key) <= 512 or any(ord(x) < 33 or ord(x) > 126 for x in api_key):
        raise ValueError("A valid server-side API key is required")
    origin_header = _origin(origin)

    # The provider's published source rewrites the FROM table. The exact SQL
    # and date/value semantics still need verification against the service.
    sql = ("SELECT latitude, longitude, area__ha, wur_radd_alerts__date, "
           "wur_radd_alerts__date_conf, wur_radd_alerts__confidence FROM data "
           f"LIMIT {max_rows + 1}")
    payload = json.dumps({"sql": sql, "geometry": geometry}, separators=(",", ":"), allow_nan=False).encode("utf-8")
    request = Request(f"{_API_ORIGIN}/dataset/wur_radd_alerts/{source_version}/query/json", data=payload,
                      headers={"Accept": "application/json", "Accept-Encoding": "identity",
                               "Content-Type": "application/json", "x-api-key": api_key}, method="POST")
    if origin_header is not None:
        request.add_header("Origin", origin_header)
    open_request = build_opener(_NoRedirect()).open
    try:
        with open_request(request, timeout=_TIMEOUT_SECONDS) as response:
            if response.status == 429:
                raise ProviderRateLimited("Provider rate limited the research request")
            if response.status != 200:
                raise ProviderQueryError(f"Provider returned HTTP {response.status}")
            raw = _read_limited(response)
    except HTTPError as error:
        status = error.code
        error.close()
        if status == 429:
            raise ProviderRateLimited("Provider rate limited the research request") from None
        raise ProviderQueryError(f"Provider returned HTTP {status}") from None
    except (URLError, TimeoutError, OSError, http.client.HTTPException):
        raise ProviderQueryError("Provider connection failed or timed out") from None

    try:
        payload_json = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_object)
        if isinstance(payload_json, dict) and isinstance(payload_json.get("data"), list) and len(payload_json["data"]) > max_rows:
            raise ResponseIncomplete("Provider returned more rows than the research limit; narrow the query")
        envelope = parse_radd_query_envelope(payload_json, source_version=source_version)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError):
        raise ProviderQueryError("Provider returned an invalid or unsupported response") from None
    return ResearchQueryResult(source_version=source_version, received_at=datetime.now(timezone.utc),
                               raw_sha256=hashlib.sha256(raw).hexdigest(), raw_response=raw, envelope=envelope)
