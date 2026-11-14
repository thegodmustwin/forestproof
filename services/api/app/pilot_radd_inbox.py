"""Private, offline RADD inbox for the first pilot integration.

The operator supplies bytes from a reviewed source and records that review.
This module has no network client or application route.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from contextlib import closing, contextmanager
from datetime import date, datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .providers.gfw_radd import RADD_PRODUCT
from .providers.gfw_radd_envelope import (
    MAX_ENVELOPE_BYTES,
    RaddQueryEnvelope,
    decode_radd_response,
    parse_radd_query_envelope,
)
from .providers.gfw_radd_research import ResearchBounds
from .sqlite_copy import RecoveryError, copy_checked_database, reserve_database_path


_APP_ID = 0x46505249
_SCHEMA_VERSION = 1
_SCHEMA = """
CREATE TABLE scope (id INTEGER PRIMARY KEY CHECK(id = 1), config TEXT NOT NULL);
CREATE TABLE receipt (
    release TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    received_at TEXT NOT NULL,
    payload BLOB NOT NULL,
    row_count INTEGER NOT NULL,
    PRIMARY KEY (release, sha256)
);
CREATE TABLE observation (
    record_key TEXT NOT NULL,
    release TEXT NOT NULL,
    receipt_sha256 TEXT NOT NULL,
    observed_on TEXT NOT NULL,
    source_row TEXT NOT NULL,
    PRIMARY KEY (record_key, release),
    FOREIGN KEY (release, receipt_sha256) REFERENCES receipt(release, sha256)
);
"""


class InboxError(ValueError):
    """An inbox operation could not be completed safely."""


class PilotScope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True, strict=True)

    scope_id: str = Field(min_length=1, max_length=128)
    review_ref: str = Field(min_length=1, max_length=500)
    attribution: str = Field(min_length=1, max_length=500)
    bounds: tuple[float, float, float, float]
    max_observation_age_days: int = Field(ge=1, le=90)
    max_receipt_gap_hours: int = Field(ge=1, le=2160)

    @model_validator(mode="after")
    def valid_bounds(self) -> PilotScope:
        ResearchBounds(*self.bounds).polygon()
        return self


def _source_row_json(fields: dict) -> str:
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _parse_response(raw: bytes, release: str) -> RaddQueryEnvelope:
    try:
        return parse_radd_query_envelope(decode_radd_response(raw), source_version=release)
    except (ValueError, RecursionError):
        raise InboxError("Response failed the RADD envelope or row checks") from None


def _utc(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise InboxError("An explicit timezone is required")
    return value.astimezone(timezone.utc)


def _open(path: Path, *, write: bool = False) -> sqlite3.Connection:
    mode = "rw" if write else "ro"
    db = sqlite3.connect(path.absolute().as_uri() + f"?mode={mode}", uri=True)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def _scope(db: sqlite3.Connection) -> PilotScope:
    if (db.execute("PRAGMA application_id").fetchone()[0] != _APP_ID
            or db.execute("PRAGMA user_version").fetchone()[0] != _SCHEMA_VERSION):
        raise InboxError("Database is not a supported private RADD inbox")
    entry = db.execute("SELECT config FROM scope WHERE id = 1").fetchone()
    if entry is None:
        raise InboxError("Private inbox scope is missing")
    return PilotScope.model_validate_json(entry["config"])


@contextmanager
def _connection(path: Path, *, write: bool = False):
    with closing(_open(path, write=write)) as db, db:
        if write:
            db.execute("BEGIN IMMEDIATE")
        yield db, _scope(db)


def create_inbox(path: Path, scope: PilotScope) -> None:
    """Create a new inbox inside an operator-protected directory."""
    reserve_database_path(path)
    try:
        with closing(_open(path, write=True)) as db, db:
            db.executescript("BEGIN IMMEDIATE;\n" + _SCHEMA)
            db.execute("INSERT INTO scope (id, config) VALUES (1, ?)", (scope.model_dump_json(),))
            db.execute(f"PRAGMA application_id = {_APP_ID}")
            db.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def import_receipt(
    path: Path, raw: bytes, *, release: str, received_at: datetime,
) -> dict:
    """Atomically save exact bytes and source rows, with immutable release identity."""
    received = _utc(received_at)
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_ENVELOPE_BYTES:
        raise InboxError("Response bytes exceed the permitted input size or are empty")
    parsed = _parse_response(raw, release)
    digest = hashlib.sha256(raw).hexdigest()

    with _connection(path, write=True) as (db, scope):
        west, south, east, north = scope.bounds
        for cell in parsed.cells:
            if not (west <= cell.longitude <= east and south <= cell.latitude <= north):
                raise InboxError("Source cell lies outside the recorded scope")
            if cell.observed_on > received.date():
                raise InboxError("Source observation is dated after receipt")

        existing = db.execute(
            "SELECT 1 FROM receipt WHERE release = ? AND sha256 = ?", (release, digest)
        ).fetchone()
        if existing:
            return {"sha256": digest, "inserted": 0, "replay": True}

        db.execute(
            "INSERT INTO receipt VALUES (?, ?, ?, ?, ?)",
            (release, digest, received.isoformat(timespec="microseconds"), raw, len(parsed.cells)),
        )
        inserted = 0
        for cell in parsed.cells:
            key = (cell.forestproof_id, release)
            canonical = _source_row_json(cell.raw_fields)
            previous = db.execute(
                "SELECT source_row FROM observation WHERE record_key = ? AND release = ?", key,
            ).fetchone()
            if previous:
                if previous["source_row"] != canonical:
                    raise InboxError("Source fields changed for an existing cell and release")
                continue
            db.execute(
                "INSERT INTO observation VALUES (?, ?, ?, ?, ?)",
                (*key, digest, cell.observed_on.isoformat(), canonical),
            )
            inserted += 1
        return {"sha256": digest, "inserted": inserted, "replay": False}


def inbox_status(path: Path, *, now: datetime) -> dict:
    """Show receipt and observation dates separately, without a coverage claim."""
    now = _utc(now)
    with _connection(path) as (db, scope):
        last_accepted = db.execute("SELECT MAX(received_at) FROM receipt").fetchone()[0]
        gap = (now - datetime.fromisoformat(last_accepted)).total_seconds() / 3600 if last_accepted else None
        observed = db.execute("SELECT MAX(observed_on) FROM observation").fetchone()[0]
        age = (now.date() - date.fromisoformat(observed)).days if observed else None
        return {
            "scope_id": scope.scope_id,
            "last_unique_receipt_at": last_accepted,
            "receipt_freshness": "UNKNOWN" if gap is None or gap < 0 else (
                "STALE" if gap > scope.max_receipt_gap_hours else "WITHIN_GAP_LIMIT"
            ),
            "latest_observed_on": observed,
            "observation_age_days": age,
            "freshness": "UNKNOWN" if age is None or age < 0 else (
                "STALE" if age > scope.max_observation_age_days else "WITHIN_AGE_LIMIT"
            ),
            "coverage": "UNKNOWN",
        }


def export_observation(path: Path, *, record_key: str, release: str) -> dict:
    """Return one private, source-linked review input for a future case."""
    with _connection(path) as (db, scope):
        row = db.execute(
            "SELECT observation.*, receipt.received_at, length(receipt.payload) AS byte_count "
            "FROM observation JOIN receipt ON receipt.release = observation.release "
            "AND receipt.sha256 = observation.receipt_sha256 WHERE record_key = ? AND observation.release = ?",
            (record_key, release),
        ).fetchone()
        if row is None:
            raise InboxError("Observation and release were not found")
        return {
            "record_state": "UNVERIFIED_IMPORT",
            "scope_id": scope.scope_id,
            "review_ref": scope.review_ref,
            "source_product": RADD_PRODUCT,
            "source_record_key": record_key,
            "release": release,
            "observed_on": row["observed_on"],
            "attribution": scope.attribution,
            "source_row": json.loads(row["source_row"]),
            "receipt": {
                "sha256": row["receipt_sha256"], "byte_count": row["byte_count"], "received_at": row["received_at"],
            },
        }


def list_observations(path: Path) -> list[dict]:
    """List up to 100 recent record and release keys for an operator export."""
    with _connection(path) as (db, _):
        return [dict(row) for row in db.execute(
            "SELECT record_key, release, observed_on FROM observation "
            "ORDER BY observed_on DESC, release, record_key LIMIT 100"
        )]


def _validate_inbox_copy(db: sqlite3.Connection) -> None:
    db.row_factory = sqlite3.Row
    _scope(db)
    if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise InboxError("Inbox receipt links failed the recovery check")
    for release, digest, payload, row_count in db.execute(
        "SELECT release, sha256, payload, row_count FROM receipt"
    ):
        if hashlib.sha256(payload).hexdigest() != digest:
            raise InboxError("Inbox receipt bytes failed the recovery check")
        cells = _parse_response(payload, release).cells
        if len(cells) != row_count:
            raise InboxError("Inbox receipt row count failed the recovery check")
        source_rows = {
            (cell.forestproof_id, cell.observed_on.isoformat(), _source_row_json(cell.raw_fields))
            for cell in cells
        }
        saved_rows = db.execute(
            "SELECT record_key, observed_on, source_row FROM observation "
            "WHERE release = ? AND receipt_sha256 = ?", (release, digest),
        )
        if any(tuple(row) not in source_rows for row in saved_rows):
            raise InboxError("Inbox observations failed the receipt recovery check")


def copy_inbox(source: Path, destination: Path) -> None:
    copy_checked_database(source, destination, validate=_validate_inbox_copy)


def main() -> int:
    parser = argparse.ArgumentParser(description="Private, offline ForestProof RADD inbox")
    parser.add_argument("database", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init").add_argument("scope", type=Path)
    ingest = commands.add_parser("import")
    ingest.add_argument("response", type=Path)
    ingest.add_argument("--release", required=True)
    ingest.add_argument("--received-at", type=datetime.fromisoformat, required=True)
    commands.add_parser("status")
    commands.add_parser("list")
    export = commands.add_parser("export")
    export.add_argument("output", type=Path)
    export.add_argument("--record-key", required=True)
    export.add_argument("--release", required=True)
    commands.add_parser("copy").add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            with args.scope.open("rb") as stream:
                raw_scope = stream.read(8193)
            if len(raw_scope) > 8192:
                raise InboxError("Scope exceeds the permitted input size")
            scope = PilotScope.model_validate_json(raw_scope)
            create_inbox(args.database, scope)
        elif args.command == "import":
            with args.response.open("rb") as stream:
                raw = stream.read(MAX_ENVELOPE_BYTES + 1)
            print(json.dumps(import_receipt(args.database, raw, release=args.release, received_at=args.received_at)))
            return 0
        elif args.command == "status":
            print(json.dumps(inbox_status(args.database, now=datetime.now(timezone.utc))))
            return 0
        elif args.command == "list":
            print(json.dumps(list_observations(args.database)))
            return 0
        elif args.command == "export":
            record = export_observation(args.database, record_key=args.record_key, release=args.release)
            encoded = json.dumps(record, ensure_ascii=False).encode("utf-8")
            with os.fdopen(os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
                stream.write(encoded)
        else:
            copy_inbox(args.database, args.destination)
    except InboxError as error:
        print(f"Inbox operation refused: {error}.")
        return 1
    except (OSError, sqlite3.Error, ValidationError, RecoveryError):
        print("Inbox operation failed. Check private files, schema and scope.")
        return 1
    print("Inbox operation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
