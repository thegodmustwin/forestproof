"""Offline SQLite groundwork for preserving RADD cell snapshots.

This module makes no provider requests and is not wired to LIVE ingestion. It
is a development persistence primitive, not the production PostGIS adapter.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .gfw_radd import RADD_PRODUCT, RaddRasterCell, normalize_radd_pixel_row


MAX_BATCH_ROWS = 1_000
MAX_ROW_BYTES = 65_536

_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS radd_cell_snapshots (
    source_product TEXT NOT NULL,
    forestproof_id TEXT NOT NULL,
    source_version TEXT NOT NULL,
    longitude REAL NOT NULL,
    latitude REAL NOT NULL,
    observed_on TEXT NOT NULL,
    raw_fields_json TEXT NOT NULL,
    raw_fields_sha256 TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    PRIMARY KEY (source_product, forestproof_id, source_version)
)
"""


class SnapshotConflict(ValueError):
    """A cell/release identity was already saved with different source fields."""


@dataclass(frozen=True)
class SnapshotBatchResult:
    inserted: int
    unchanged: int


def _canonical_fields(row: Mapping[str, Any]) -> tuple[str, str]:
    if any(not isinstance(key, str) for key in row):
        raise ValueError("RADD field names must be strings")
    try:
        raw = json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        encoded = raw.encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError):
        raise ValueError("RADD source fields must be valid UTF-8 JSON") from None
    if len(encoded) > MAX_ROW_BYTES:
        raise ValueError("RADD source row exceeds the offline size limit")
    return raw, hashlib.sha256(encoded).hexdigest()


class RaddSnapshotStore:
    """Save immutable-by-application cell/release snapshots in a local database."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute(_CREATE_SCHEMA)

    def save_batch(self, rows: Sequence[Mapping[str, Any]], *, source_version: str) -> SnapshotBatchResult:
        """Save a bounded batch atomically; conflicting snapshots roll it all back.

        A replay with the same canonical raw fields is a no-op. The same cell
        and release with changed fields is reported, never silently overwritten.
        """
        if not isinstance(rows, (list, tuple)) or not rows or len(rows) > MAX_BATCH_ROWS:
            raise ValueError(f"Provide between 1 and {MAX_BATCH_ROWS} RADD rows")
        prepared: list[tuple[RaddRasterCell, str, str]] = []
        for row in rows:
            cell = normalize_radd_pixel_row(row, source_version=source_version)
            raw, digest = _canonical_fields(row)
            prepared.append((cell, raw, digest))

        inserted = unchanged = 0
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            for cell, raw, digest in prepared:
                key = (cell.source_product, cell.forestproof_id, cell.source_version)
                previous = connection.execute(
                    "SELECT raw_fields_json, raw_fields_sha256 FROM radd_cell_snapshots "
                    "WHERE source_product = ? AND forestproof_id = ? AND source_version = ?",
                    key,
                ).fetchone()
                if previous:
                    if previous != (raw, digest):
                        raise SnapshotConflict("Source fields changed for an existing cell and release")
                    unchanged += 1
                    continue
                connection.execute(
                    "INSERT INTO radd_cell_snapshots "
                    "(source_product, forestproof_id, source_version, longitude, latitude, observed_on, "
                    "raw_fields_json, raw_fields_sha256, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (*key, cell.longitude, cell.latitude, cell.observed_on.isoformat(), raw, digest,
                     datetime.now(timezone.utc).isoformat()),
                )
                inserted += 1
        return SnapshotBatchResult(inserted=inserted, unchanged=unchanged)

    def get_snapshot(self, *, forestproof_id: str, source_version: str) -> dict[str, Any] | None:
        """Return preserved source fields, identity, release and receipt time."""
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            result = connection.execute(
                "SELECT * FROM radd_cell_snapshots "
                "WHERE source_product = ? AND forestproof_id = ? AND source_version = ?",
                (RADD_PRODUCT, forestproof_id, source_version),
            ).fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        result_dict["raw_fields"] = json.loads(result_dict.pop("raw_fields_json"))
        return result_dict


    def compare_releases(
        self, *, forestproof_id: str, from_version: str, to_version: str
    ) -> dict[str, Any]:
        """Compare two saved cell snapshots without inferring absent alerts.

        The caller supplies the same ForestProof cell/date identity and both
        explicitly saved releases. This is an offline raw-field comparison,
        not a provider event, a retraction, or a live-ingestion result.
        Release ordering and meaning must be verified separately.
        """
        if not isinstance(forestproof_id, str) or not forestproof_id.strip():
            raise ValueError("A ForestProof cell identity is required")
        if not isinstance(from_version, str) or not isinstance(to_version, str):
            raise ValueError("Two distinct source release identifiers are required")
        from_version, to_version = from_version.strip(), to_version.strip()
        if not from_version or not to_version or from_version == to_version:
            raise ValueError("Two distinct source release identifiers are required")

        before = self.get_snapshot(forestproof_id=forestproof_id, source_version=from_version)
        after = self.get_snapshot(forestproof_id=forestproof_id, source_version=to_version)
        if before is None or after is None:
            raise ValueError(
                "Both snapshots must exist; an absent row does not establish a retraction"
            )

        old_fields = before["raw_fields"]
        new_fields = after["raw_fields"]

        def canonical(value: Any) -> str:
            return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

        changed_fields = [
            key
            for key in sorted(old_fields.keys() | new_fields.keys())
            if key not in old_fields or key not in new_fields or canonical(old_fields[key]) != canonical(new_fields[key])
        ]
        return {
            "forestproof_id": forestproof_id,
            "source_product": RADD_PRODUCT,
            "from_version": from_version,
            "to_version": to_version,
            "change": "SOURCE_FIELDS_CHANGED" if changed_fields else "UNCHANGED",
            "changed_fields": changed_fields,
        }
