from __future__ import annotations

import sqlite3

import pytest

from app.config import Settings
from app.demo_data import DEMO_ORGANIZATION_ID
from app.demo_db_copy import RecoveryError, copy_demo_database, main
from app.store import Store


def _demo_store(path, evidence):
    store = Store(Settings("demo", path, evidence, "http://localhost:3000"))
    store.prepare()
    return store


def test_backup_and_test_restore_preserve_committed_work_and_wal(tmp_path):
    source = tmp_path / "working.db"
    store = _demo_store(source, tmp_path / "evidence")
    observation = store.list_observations(DEMO_ORGANIZATION_ID)[0]
    case = store.create_case(
        DEMO_ORGANIZATION_ID, observation["id"], "Synthetic recovery",
        "Demo organization", "Reviewer"
    )
    # Keep the connection open so committed changes remain in the WAL during
    # the snapshot; a simple filesystem copy of the DB would miss them.
    writer = sqlite3.connect(source)
    try:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
        writer.execute(
            "UPDATE investigation_cases SET title = ? WHERE id = ?",
            ("Committed in WAL", case["id"]),
        )
        writer.commit()
        backup = tmp_path / "backup.db"
        restored = tmp_path / "restored.db"
        copy_demo_database(source, backup)
        copy_demo_database(backup, restored)
        with sqlite3.connect(restored) as recovered:
            assert recovered.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
            assert recovered.execute(
                "SELECT title FROM investigation_cases WHERE id = ?", (case["id"],)
            ).fetchone() == ("Committed in WAL",)
    finally:
        writer.close()


def test_copy_refuses_overwrite_and_preserves_existing_file(tmp_path):
    source = tmp_path / "working.db"
    _demo_store(source, tmp_path / "evidence")
    existing = tmp_path / "existing.db"
    existing.write_bytes(b"keep this content")

    with pytest.raises(FileExistsError):
        copy_demo_database(source, existing)
    assert existing.read_bytes() == b"keep this content"


def test_missing_invalid_and_wrong_database_never_leave_backup(tmp_path):
    destination = tmp_path / "backup.db"
    with pytest.raises(FileNotFoundError):
        copy_demo_database(tmp_path / "missing.db", destination)
    assert not destination.exists()

    invalid = tmp_path / "invalid.db"
    invalid.write_bytes(b"not a SQLite database")
    with pytest.raises(sqlite3.DatabaseError):
        copy_demo_database(invalid, destination)
    assert not destination.exists()

    other = tmp_path / "other.db"
    with sqlite3.connect(other) as conn:
        conn.execute("CREATE TABLE unrelated (id INTEGER)")
    with pytest.raises(RecoveryError):
        copy_demo_database(other, destination)
    assert not destination.exists()


def test_existing_destination_sidecar_is_never_touched(tmp_path):
    source = tmp_path / "working.db"
    _demo_store(source, tmp_path / "evidence")
    destination = tmp_path / "backup.db"
    sidecar = tmp_path / "backup.db-wal"
    sidecar.write_bytes(b"preserve")

    with pytest.raises(RecoveryError):
        copy_demo_database(source, destination)
    assert not destination.exists()
    assert sidecar.read_bytes() == b"preserve"


def test_cli_requires_synthetic_attestation_before_creating_a_copy(tmp_path, monkeypatch):
    source = tmp_path / "working.db"
    _demo_store(source, tmp_path / "evidence")
    destination = tmp_path / "backup.db"
    monkeypatch.setattr("sys.argv", ["demo_db_copy", str(source), str(destination)])
    with pytest.raises(SystemExit):
        main()
    assert not destination.exists()

    monkeypatch.setattr(
        "sys.argv", ["demo_db_copy", "--synthetic-only", str(source), str(destination)]
    )
    assert main() == 0
    assert destination.is_file()
