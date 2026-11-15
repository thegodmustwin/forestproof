"""Keep one historical case and its operator review in a separate local ledger."""

from __future__ import annotations

from contextlib import closing
from datetime import UTC, date, datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path, PurePosixPath
import re
import secrets
import sqlite3

from services.api.app.sqlite_copy import copy_checked_database, reserve_database_path


CASE_ID = "FP-RESEARCH-001"
APP_ID = 0x46505257
FILE_LIMIT = 64 * 1024 * 1024
METADATA_LIMIT = 64 * 1024
EAT = timezone(timedelta(hours=3))
DOCUMENTS = ("case.json", "observation.json", "DOSSIER.md", "CHECKSUMS.sha256")
DOIS = {"https://doi.org/10.5067/SNWG/OPERA_L3_DIST-ALERT-HLS_V1.001", "https://doi.org/10.5067/HLS/HLSL30.002"}
DISPOSITIONS = {
    "keep_open": "Open for verification",
    "close_unconfirmed": "Closed without confirmation",
}


class ReviewError(Exception):
    """A private owner review failed verification."""


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read_private_file(path: Path, limit: int) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ReviewError("An expected archive file is missing.")
    with path.open("rb") as stream:
        content = stream.read(limit + 1)
    if not 0 < len(content) <= limit:
        raise ReviewError("An archive metadata file has an unexpected size.")
    return content


def manifest_entries(content: bytes) -> dict[str, str]:
    entries = {}
    for line in content.decode("utf-8").splitlines():
        sha, separator, name = line.partition("  ")
        parts = PurePosixPath(name)
        if (not separator or not re.fullmatch(r"[0-9a-f]{64}", sha) or not name
                or parts.is_absolute() or parts.as_posix() != name or ".." in parts.parts
                or any(mark in name for mark in ("\\", ":", "\x00"))
                or name in entries):
            raise ReviewError("The archive checksum manifest is invalid.")
        entries[name] = sha
    if len(entries) != 16 or not set(DOCUMENTS[:-1]) <= entries.keys():
        raise ReviewError("The expected historical archive is incomplete.")
    if len({name.casefold() for name in entries}) != len(entries):
        raise ReviewError("The manifest references ambiguous filenames.")
    return entries


def validate_documents(documents: dict[str, bytes]) -> tuple[dict, dict]:
    try:
        case = json.loads(documents["case.json"])
        observation = json.loads(documents["observation.json"])
        entries = manifest_entries(documents["CHECKSUMS.sha256"])
        if any(entries[name] != digest(documents[name]) for name in DOCUMENTS[:-1]):
            raise ReviewError("Archive document hashes do not match.")
        acquired = datetime.fromisoformat(observation["acquisition"])
        if (case["case_id"] != CASE_ID or case["mode"] != "PRIVATE_HISTORICAL_RESEARCH"
                or case["state"] != "PENDING_OWNER_REVIEW" or case["observation"] != "observation.json"
                or case["review"]["owner_decision"] is not None
                or acquired.utcoffset() != timedelta(0) or acquired.date().isoformat() != "2026-11-03"
                or observation["first_detection_day"] != "2026-11-03"
                or observation["last_assessed_day"] != "2026-11-03"
                or observation["primary_sample"]["band_values"]["status"] != 1
                or observation["primary_sample"]["band_values"]["mask"] != 1
                or observation["neighbor_sample"]["band_values"]["status"] != 1
                or observation["same_pass_agreement_count"] <= 0
                or {source["doi"] for source in observation["source_products"]} != DOIS):
            raise ReviewError("The documents do not identify the expected historical research case.")
        raster_entries = {Path(name).name: sha for name, sha in entries.items() if name.endswith(".tif")}
        raster_objects = {Path(obj["name"]).name: obj["sha256"] for obj in observation["source_objects"]}
        if len(raster_entries) != 10 or raster_entries != raster_objects:
            raise ReviewError("The archived raster receipts and checksum manifest disagree.")
    except (TypeError, KeyError, ValueError, UnicodeError, RecursionError) as error:
        raise ReviewError("The archived case metadata is invalid.") from error
    return case, observation


def read_archive(directory: Path) -> dict[str, bytes]:
    directory = directory.resolve(strict=True)
    documents = {name: read_private_file(directory / name, METADATA_LIMIT) for name in DOCUMENTS}
    _, observation = validate_documents(documents)
    sizes = {Path(obj["name"]).name: obj["bytes"] for obj in observation["source_objects"]}
    for name, sha in manifest_entries(documents["CHECKSUMS.sha256"]).items():
        path = directory / name
        if not path.resolve(strict=True).is_relative_to(directory) or path.is_symlink() or not path.is_file():
            raise ReviewError("An archive file is outside the trusted evidence directory.")
        size = path.stat().st_size
        if not 0 < size <= FILE_LIMIT or (path.suffix == ".tif" and size != sizes[path.name]):
            raise ReviewError("An archive file has an unexpected size.")
        with path.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != sha:
                raise ReviewError("An archive file failed its checksum verification.")
    return documents


def initialize(path: Path, archive: Path, owner_name: str):
    owner_name = owner_name.strip()
    if not 1 <= len(owner_name) <= 100 or not owner_name.isprintable():
        raise ReviewError("Enter a display name for the owner.")
    documents = read_archive(archive)
    reserve_database_path(path)
    try:
        with closing(sqlite3.connect(path)) as db, db:
            db.executescript(f"""
                PRAGMA application_id = {APP_ID};
                CREATE TABLE owner (
                    id INTEGER PRIMARY KEY CHECK (id = 1), name TEXT NOT NULL,
                    salt BLOB, verifier BLOB
                );
                CREATE TABLE document (
                    name TEXT PRIMARY KEY, content BLOB NOT NULL, sha256 TEXT NOT NULL
                );
                CREATE TABLE review (
                    seq INTEGER PRIMARY KEY, submission TEXT NOT NULL UNIQUE,
                    owner_name TEXT NOT NULL, recorded_at TEXT NOT NULL,
                    disposition TEXT NOT NULL CHECK (disposition IN ('keep_open', 'close_unconfirmed')),
                    follow_up TEXT, note TEXT NOT NULL, receipt_sha256 TEXT NOT NULL
                );
            """)
            db.execute("INSERT INTO owner (id, name) VALUES (1, ?)", (owner_name,))
            db.executemany("INSERT INTO document VALUES (?, ?, ?)",
                           [(name, data, digest(data)) for name, data in documents.items()])
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def connect(path: Path, *, write: bool = False):
    db = sqlite3.connect(path.resolve(strict=True).as_uri() + ("?mode=rw" if write else "?mode=ro"), uri=True)
    db.row_factory = sqlite3.Row
    return db


def account(db):
    if db.execute("PRAGMA application_id").fetchone()[0] != APP_ID:
        raise ReviewError("Expected a historical owner review database.")
    owner = db.execute("SELECT name, salt, verifier FROM owner WHERE id = 1").fetchone()
    if owner is None:
        raise ReviewError("The owner account is missing.")
    return owner


def password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)


def has_password(path: Path) -> bool:
    with closing(connect(path)) as db:
        return account(db)["verifier"] is not None


def set_password(path: Path, password: str):
    if not 12 <= len(password) <= 128 or not password.strip():
        raise ReviewError("Choose a password between 12 and 128 characters.")
    salt = secrets.token_bytes(16)
    with closing(connect(path, write=True)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        if account(db)["verifier"] is not None:
            raise ReviewError("The owner password is already set.")
        db.execute("UPDATE owner SET salt = ?, verifier = ? WHERE id = 1", (salt, password_hash(password, salt)))


def authenticate(path: Path, password: str) -> bool:
    if not 12 <= len(password) <= 128:
        return False
    with closing(connect(path)) as db:
        owner = account(db)
        return owner["verifier"] is not None and hmac.compare_digest(
            owner["verifier"], password_hash(password, owner["salt"])
        )


def stored_documents(db) -> dict[str, bytes]:
    documents = {}
    for record in db.execute("SELECT * FROM document"):
        if digest(record["content"]) != record["sha256"]:
            raise ReviewError("A stored source document failed its checksum.")
        documents[record["name"]] = record["content"]
    if set(documents) != set(DOCUMENTS):
        raise ReviewError("A stored source document is missing.")
    validate_documents(documents)
    return documents


def summarize(db) -> dict:
    owner = account(db)["name"]
    documents = stored_documents(db)
    archived_case, observation = validate_documents(documents)
    receipt_sha = digest(documents["observation.json"])
    reviews = [dict(row) for row in db.execute(
        "SELECT seq, owner_name, recorded_at, disposition, follow_up, note, receipt_sha256 FROM review ORDER BY seq"
    )]
    if any(entry["receipt_sha256"] != receipt_sha or entry["owner_name"] != owner for entry in reviews):
        raise ReviewError("Review history does not match its owner and source receipt.")
    return {
        "case_id": CASE_ID,
        "source_name": "NASA OPERA DIST-ALERT-HLS V1",
        "observation_date": observation["first_detection_day"],
        "observation_summary": (
            "NASA recorded a first, unconfirmed vegetation anomaly in the provisional research area. "
            "The sampled location passed the documented quality checks and the overlapping grid from the same pass agreed. "
            "Ground conditions, cause, and a later confirmation remain unknown."
        ),
        "owner_name": owner,
        "receipt_sha256": receipt_sha,
        "archive_manifest_sha256": digest(documents["CHECKSUMS.sha256"]),
        "archived_case": archived_case,
        "source_receipt": observation,
        "reviews": reviews,
    }


def snapshot(path: Path) -> dict:
    with closing(connect(path)) as db, db:
        db.execute("BEGIN")
        return summarize(db)


def original_receipt(path: Path) -> bytes:
    with closing(connect(path)) as db:
        account(db)
        return stored_documents(db)["observation.json"]


def record_review(path: Path, submission: str, disposition: str, follow_up: str, note: str, *, now: datetime):
    note = note.strip()
    if disposition not in DISPOSITIONS or not 1 <= len(note) <= 2000 or not re.fullmatch(r"[0-9a-f]{32}", submission):
        raise ReviewError("Choose a disposition and enter a note of up to 2,000 characters.")
    if not follow_up and disposition == "keep_open":
        raise ReviewError("Set a follow-up date for an open review.")
    if now.utcoffset() is None:
        raise ReviewError("The review clock is unavailable.")
    if follow_up:
        try:
            next_day = date.fromisoformat(follow_up)
            if next_day.isoformat() != follow_up or next_day < now.astimezone(EAT).date():
                raise ValueError
        except ValueError as error:
            raise ReviewError("Choose a follow-up date on or after today.") from error
    with closing(connect(path, write=True)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        owner = account(db)
        if owner["verifier"] is None:
            raise ReviewError("Set the owner password before recording a review.")
        receipt_sha = digest(stored_documents(db)["observation.json"])
        previous = db.execute(
            "SELECT disposition, follow_up, note FROM review WHERE submission = ?", (submission,),
        ).fetchone()
        fields = (disposition, follow_up or None, note)
        if previous is not None:
            if tuple(previous) != fields:
                raise ReviewError("That submission is already saved. Review the history before trying again.")
            return
        db.execute(
            "INSERT INTO review (submission, owner_name, recorded_at, disposition, follow_up, note, receipt_sha256)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (submission, owner["name"], now.astimezone(UTC).isoformat(), *fields, receipt_sha),
        )


def copy_review(source: Path, destination: Path):
    def verify(db):
        db.row_factory = sqlite3.Row
        summarize(db)
    copy_checked_database(source, destination, validate=verify)
