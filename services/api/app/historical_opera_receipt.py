"""Offline recovery rehearsal for a synthetic historical OPERA receipt."""

from argparse import ArgumentParser
from contextlib import closing
from datetime import UTC, date, datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from .sqlite_copy import RecoveryError, copy_checked_database, reserve_database_path


APPLICATION_ID = 0x46504F52
SCHEMA_VERSION = 1
MANIFEST_LIMIT = 32 * 1024
LAYER_LIMIT = 64
MODE = "SYNTHETIC_HISTORICAL_REHEARSAL"
ROLES = ("status", "first_date", "last_date", "mask", "fmask")
GRANULE_PATTERN = (
    r"^OPERA_L3_DIST-ALERT-HLS_T00AAA_\d{8}T\d{6}Z_"
    r"\d{8}T\d{6}Z_(L8|L9|S2A|S2B|S2C)_30_v1$"
)


class ReceiptError(Exception):
    """The historical rehearsal could not be verified."""


class Layer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    filename: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_\-.]{0,199}\.tif$")
    byte_count: int = Field(gt=0, le=LAYER_LIMIT)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal[1]
    mode: Literal["SYNTHETIC_HISTORICAL_REHEARSAL"]
    granule: str = Field(pattern=GRANULE_PATTERN)
    row: int = Field(ge=0, lt=4000)
    column: int = Field(ge=0, lt=4000)
    observed_on: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    assessed_on: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    layers: dict[str, Layer]

    @property
    def record_id(self) -> str:
        return f"{self.granule}:{self.row}:{self.column}"


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError("Manifest contains a duplicate JSON field.")
        result[key] = value
    return result


def _parse_manifest(content: bytes) -> Manifest:
    if not content or len(content) > MANIFEST_LIMIT:
        raise ReceiptError("Manifest size is invalid.")
    try:
        raw = json.loads(content, object_pairs_hook=_unique_object)
        manifest = Manifest.model_validate(raw)
        sensed_at, created_at = (
            datetime.strptime(value, "%Y%m%dT%H%M%SZ")
            for value in manifest.granule.split("_")[4:6]
        )
        observed = date.fromisoformat(manifest.observed_on)
        assessed = date.fromisoformat(manifest.assessed_on)
    except (ValueError, RecursionError) as exc:
        raise ReceiptError("Manifest schema, granule or dates are invalid.") from exc
    if not observed <= assessed <= sensed_at.date() or created_at < sensed_at:
        raise ReceiptError("Manifest dates are out of order.")
    if set(manifest.layers) != set(ROLES):
        raise ReceiptError("Exactly five known layer roles are required.")
    if len({layer.filename.casefold() for layer in manifest.layers.values()}) != len(ROLES):
        raise ReceiptError("Layer files must be distinct.")
    return manifest


def _read_bounded(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ReceiptError("Receipt input must be a regular file.")
    with path.open("rb") as reader:
        content = reader.read(limit + 1)
    if len(content) > limit:
        raise ReceiptError("Receipt input exceeds its size limit.")
    return content


def _verify_layer(role: str, layer: Layer, content: bytes) -> None:
    if len(content) != layer.byte_count or _sha256(content) != layer.sha256:
        raise ReceiptError("Layer size or digest does not match the manifest.")
    prefix = b"SYNTHETIC PLACEHOLDER " + role.encode("ascii")
    if re.fullmatch(prefix + rb"( [a-z0-9]{1,24})?", content) is None:
        raise ReceiptError("Layer must be a synthetic placeholder for its role.")


def initialize(database: Path) -> None:
    reserve_database_path(database)
    try:
        with closing(sqlite3.connect(database)) as db, db:
            db.executescript(f"""
                PRAGMA application_id = {APPLICATION_ID};
                PRAGMA user_version = {SCHEMA_VERSION};
                CREATE TABLE receipt (
                    record_id TEXT PRIMARY KEY, manifest BLOB NOT NULL,
                    manifest_sha256 TEXT NOT NULL, received_at TEXT NOT NULL,
                    status BLOB NOT NULL, first_date BLOB NOT NULL,
                    last_date BLOB NOT NULL, mask BLOB NOT NULL, fmask BLOB NOT NULL
                );
            """)
    except BaseException:
        database.unlink(missing_ok=True)
        raise


def _verify_db(db: sqlite3.Connection) -> None:
    application_id = db.execute("PRAGMA application_id").fetchone()[0]
    schema_version = db.execute("PRAGMA user_version").fetchone()[0]
    if (application_id, schema_version) != (APPLICATION_ID, SCHEMA_VERSION):
        raise ReceiptError("Expected an OPERA rehearsal database.")


def _open(database: Path, *, read_only: bool) -> sqlite3.Connection:
    mode = "ro" if read_only else "rw"
    db = sqlite3.connect(database.resolve(strict=True).as_uri() + f"?mode={mode}", uri=True)
    db.row_factory = sqlite3.Row
    return db


def _checked_manifest(row: sqlite3.Row) -> Manifest:
    manifest = _parse_manifest(row["manifest"])
    if manifest.record_id != row["record_id"] or _sha256(row["manifest"]) != row["manifest_sha256"]:
        raise ReceiptError("Stored receipt identity or manifest digest does not match.")
    for role in ROLES:
        _verify_layer(role, manifest.layers[role], row[role])
    return manifest


def ingest(database: Path, manifest_path: Path) -> tuple[str, str]:
    content = _read_bounded(manifest_path, MANIFEST_LIMIT)
    manifest = _parse_manifest(content)
    assets = []
    for role in ROLES:
        layer = manifest.layers[role]
        layer_bytes = _read_bounded(manifest_path.parent / layer.filename, layer.byte_count)
        _verify_layer(role, layer, layer_bytes)
        assets.append(layer_bytes)

    with closing(_open(database, read_only=False)) as db, db:
        _verify_db(db)
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute(
            "SELECT * FROM receipt WHERE record_id = ?", (manifest.record_id,),
        ).fetchone()
        if previous is not None:
            _checked_manifest(previous)
            if previous["manifest"] != content or any(
                previous[role] != asset for role, asset in zip(ROLES, assets, strict=True)
            ):
                raise ReceiptError("An immutable receipt with different content already exists.")
            return manifest.record_id, "replayed"
        db.execute(
            "INSERT INTO receipt (record_id, manifest, manifest_sha256, received_at, "
            "status, first_date, last_date, mask, fmask) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (manifest.record_id, content, _sha256(content), datetime.now(UTC).isoformat(), *assets),
        )
    return manifest.record_id, "imported"


def dossier(database: Path, record_id: str) -> dict[str, object]:
    with closing(_open(database, read_only=True)) as db:
        _verify_db(db)
        row = db.execute("SELECT * FROM receipt WHERE record_id = ?", (record_id,)).fetchone()
        if row is None:
            raise ReceiptError("Receipt was not found.")
        manifest = _checked_manifest(row)
    return {
        "record_id": record_id,
        "receipt": {
            "manifest": manifest.model_dump(),
            "manifest_sha256": row["manifest_sha256"],
            "received_at": row["received_at"],
        },
        "owner_review": "pending",
    }


def copy_database(database: Path, new_database: Path) -> None:
    def validate(db: sqlite3.Connection) -> None:
        _verify_db(db)
        db.row_factory = sqlite3.Row
        for row in db.execute("SELECT * FROM receipt"):
            _checked_manifest(row)

    copy_checked_database(database, new_database, validate=validate)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("ingest").add_argument("manifest", type=Path)
    commands.add_parser("dossier").add_argument("record_id")
    commands.add_parser("copy").add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        match args.command:
            case "init":
                initialize(args.database)
            case "ingest":
                record_id, result = ingest(args.database, args.manifest)
                print(json.dumps({"record_id": record_id, "result": result}))
            case "dossier":
                print(json.dumps(dossier(args.database, args.record_id), sort_keys=True))
            case "copy":
                copy_database(args.database, args.destination)
    except (ReceiptError, RecoveryError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f"OPERA rehearsal failed ({type(exc).__name__}).\n")


if __name__ == "__main__":
    main()