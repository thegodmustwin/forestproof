"""Offline receipt provenance for synthetic RADD research fixtures.

This metadata ledger performs no requests, stores no raw payload, and is not
connected to ingestion or production storage. It does not establish coverage,
completeness, provider health, authorization, or real-data provenance.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from .gfw_radd_envelope import MAX_ENVELOPE_BYTES, parse_radd_query_envelope
from .gfw_radd_research import ResearchBounds

_SCHEMA = """
CREATE TABLE IF NOT EXISTS radd_fixture_receipts (
    receipt_id TEXT PRIMARY KEY,
    source_version TEXT NOT NULL,
    bounds_json TEXT NOT NULL,
    received_at TEXT NOT NULL,
    response_sha256 TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    completeness TEXT NOT NULL CHECK (completeness = 'UNKNOWN')
)
"""


class ReceiptConflict(ValueError):
    """The receipt identity is already associated with different metadata."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


class RaddFixtureReceiptStore:
    """Preserve metadata about explicitly synthetic offline response fixtures."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute(_SCHEMA)

    def record(
        self, *, receipt_id: str, source_version: str, bounds: ResearchBounds,
        received_at: datetime, raw_response: bytes, synthetic_fixture: bool = False,
    ) -> str:
        """Record an immutable synthetic receipt; return 'inserted' or 'unchanged'.

        The hash covers the exact fixture bytes, not reconstructed JSON. It does
        not authenticate the response or prove completeness. A replay with the
        same receipt ID and metadata is a no-op; mismatched replays fail.
        """
        if synthetic_fixture is not True:
            raise ValueError("Explicit synthetic fixture attestation is required")
        try:
            if not isinstance(receipt_id, str):
                raise ValueError
            canonical_id = str(UUID(receipt_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("A UUID receipt identity is required") from None
        if not isinstance(bounds, ResearchBounds):
            raise ValueError("Bounded research coordinates are required")
        bounds.polygon()
        bounds_json = json.dumps(
            [float(bounds.west), float(bounds.south), float(bounds.east), float(bounds.north)],
            separators=(",", ":"), allow_nan=False,
        )
        if (not isinstance(received_at, datetime) or received_at.tzinfo is None
                or received_at.utcoffset() is None):
            raise ValueError("A timezone-aware receipt time is required")
        utc_time = received_at.astimezone(timezone.utc).isoformat()
        if not isinstance(raw_response, bytes) or not 0 < len(raw_response) <= MAX_ENVELOPE_BYTES:
            raise ValueError("A bounded fixture response is required")
        try:
            payload = json.loads(raw_response.decode("utf-8"), object_pairs_hook=_unique_object)
            envelope = parse_radd_query_envelope(payload, source_version=source_version)
        except (UnicodeDecodeError, ValueError, RecursionError):
            raise ValueError("Fixture response is invalid or unsupported") from None

        values = (source_version, bounds_json, utc_time, hashlib.sha256(raw_response).hexdigest(),
                  len(envelope.cells), "UNKNOWN")
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute(
                "SELECT source_version, bounds_json, received_at, response_sha256, "
                "row_count, completeness FROM radd_fixture_receipts WHERE receipt_id = ?",
                (canonical_id,),
            ).fetchone()
            if previous is not None:
                if previous != values:
                    raise ReceiptConflict("Receipt identity is associated with different metadata")
                return "unchanged"
            connection.execute(
                "INSERT INTO radd_fixture_receipts "
                "(receipt_id, source_version, bounds_json, received_at, response_sha256, row_count, completeness) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (canonical_id, *values),
            )
        return "inserted"

    def get(self, receipt_id: str) -> dict[str, Any] | None:
        """Read receipt metadata; it contains neither a credential nor raw rows."""
        try:
            if not isinstance(receipt_id, str):
                raise ValueError
            canonical_id = str(UUID(receipt_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("A UUID receipt identity is required") from None
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM radd_fixture_receipts WHERE receipt_id = ?", (canonical_id,)
            ).fetchone()
        return dict(row) if row is not None else None
