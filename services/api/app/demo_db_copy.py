"""Offline SQLite copy primitive for the synthetic demo only.

This is not an evidence backup, production backup policy, encryption, or an
automatic restore. Both paths must be under private, trusted directories.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
from contextlib import closing
from pathlib import Path


class RecoveryError(Exception):
    """The demo database could not be copied safely."""


_REQUIRED_TABLES = {"observations", "investigation_cases", "case_events"}


def _check_database(connection: sqlite3.Connection) -> None:
    integrity = connection.execute("PRAGMA integrity_check").fetchall()
    if integrity != [("ok",)]:
        raise RecoveryError("Database integrity check failed.")
    tables = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    if not _REQUIRED_TABLES.issubset(tables):
        raise RecoveryError("Not a recognized ForestProof demo database.")


def copy_demo_database(source: Path, destination: Path) -> None:
    """Copy to a new SQLite file via the online backup API.

    The source is opened read-only. The destination must not exist and its
    parent must be a private, trusted directory; this function does not secure
    directory ACLs. The same operation can create a backup or a separate test
    restore. It deliberately never overwrites an existing database.
    """
    source = Path(source).resolve(strict=True)
    destination = Path(destination).absolute()
    if not source.is_file():
        raise RecoveryError("The source must be a regular file.")
    if source.stat().st_size == 0:
        raise RecoveryError("The source is empty.")
    if not destination.parent.is_dir():
        raise RecoveryError("Destination directory does not exist.")
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(str(destination) + suffix)
        if os.path.lexists(sidecar):
            raise RecoveryError("Destination sidecar already exists.")

    # Exclusive creation refuses existing files and dangling symlinks.
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        source_uri = source.as_uri() + "?mode=ro"
        with closing(sqlite3.connect(source_uri, uri=True)) as reader:
            reader.execute("PRAGMA query_only = ON")
            with closing(sqlite3.connect(destination)) as writer:
                reader.backup(writer)
                _check_database(writer)
    except BaseException:
        # Only the file exclusively created above is removed. The parent must
        # not be writable by an untrusted user; see module documentation.
        destination.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy a synthetic ForestProof SQLite database to a new private file."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        copy_demo_database(args.source, args.destination)
    except (OSError, sqlite3.Error, RecoveryError):
        # Paths and DB contents can be sensitive; never echo exception details.
        print("Database copy failed. Check source, destination and access privately.")
        return 1
    print("Database copy and integrity check completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
