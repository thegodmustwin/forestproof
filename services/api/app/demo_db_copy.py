"""Offline SQLite copy primitive for the synthetic demo only.

This is not an evidence backup, production backup policy, encryption, or an
automatic restore. Both paths must be under private, trusted directories.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

if __package__:
    from .sqlite_copy import RecoveryError, copy_checked_database
else:
    from sqlite_copy import RecoveryError, copy_checked_database


_REQUIRED_TABLES = {"observations", "investigation_cases", "case_events"}


def _check_database(connection: sqlite3.Connection) -> None:
    tables = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    if not _REQUIRED_TABLES.issubset(tables):
        raise RecoveryError("Not a recognized ForestProof database schema.")


def copy_demo_database(source: Path, destination: Path) -> None:
    """Copy the demo database to a new path in a private, trusted directory."""
    copy_checked_database(source, destination, validate=_check_database)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy a synthetic ForestProof SQLite database to a new private file."
    )
    parser.add_argument(
        "--synthetic-only", action="store_true", required=True,
        help="Attest that this database contains synthetic demo data only.",
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
