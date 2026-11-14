"""Non-overwriting SQLite copy shared by the demo and private import tooling."""
from collections.abc import Callable
from contextlib import closing
import os
from pathlib import Path
import sqlite3


class RecoveryError(Exception):
    """A SQLite copy or integrity check failed."""


def reserve_database_path(path: Path) -> None:
    """Reserve a new file in an existing, trusted directory."""
    if not path.parent.is_dir():
        raise RecoveryError("Destination directory does not exist.")
    for suffix in ("-wal", "-shm", "-journal"):
        if os.path.lexists(Path(str(path) + suffix)):
            raise RecoveryError("Destination sidecar already exists.")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)


def copy_checked_database(
    source: Path, destination: Path, *, validate: Callable[[sqlite3.Connection], None],
) -> None:
    """Copy read-only source data and verify the new copy before reporting success.

    Paths must be in trusted directories. Callers provision private filesystem
    permissions, transfer the copy off-host, and test recovery on the target.
    """
    source = Path(source).resolve(strict=True)
    destination = Path(destination).absolute()
    if not source.is_file() or source.stat().st_size == 0:
        raise RecoveryError("Source must be a nonempty regular file.")
    reserve_database_path(destination)
    try:
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as reader:
            reader.execute("PRAGMA query_only = ON")
            with closing(sqlite3.connect(destination)) as writer:
                reader.backup(writer)
                if writer.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                    raise RecoveryError("Database integrity check failed.")
                validate(writer)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
