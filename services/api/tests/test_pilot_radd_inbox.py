import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone

import pytest

from app.pilot_radd_inbox import (
    InboxError,
    PilotScope,
    copy_inbox,
    create_inbox,
    export_observation,
    import_receipt,
    inbox_status,
)
from app.providers.gfw_radd_envelope import parse_radd_query_envelope


RECEIVED = datetime(2026, 11, 13, 12, tzinfo=timezone.utc)
RELEASE = "v20261110"


def row(**overrides):
    return {
        "longitude": 0.002,
        "latitude": 0.003,
        "wur_radd_alerts__date": "2026-11-10",
        "wur_radd_alerts__confidence": 3,
        **overrides,
    }


def response(*rows):
    return json.dumps({"status": "success", "data": rows}).encode()


def make_scope():
    return PilotScope(
        scope_id="synthetic-test",
        review_ref="synthetic operator policy fixture",
        attribution="Synthetic attribution fixture",
        bounds=(0.0, 0.0, 0.01, 0.01),
        max_observation_age_days=7,
        max_receipt_gap_hours=24,
    )


def record_key(raw):
    return parse_radd_query_envelope(json.loads(raw), source_version=RELEASE).cells[0].forestproof_id


def save(path, raw, *, release=RELEASE, received_at=RECEIVED):
    return import_receipt(path, raw, release=release, received_at=received_at)


def test_replay_preserves_exact_bytes_and_cannot_refresh_stale_data(tmp_path):
    db = tmp_path / "pilot.sqlite"
    create_inbox(db, make_scope())
    assert inbox_status(db, now=RECEIVED)["receipt_freshness"] == "UNKNOWN"
    raw = response(row()) + b"\n"
    assert save(db, raw)["inserted"] == 1
    assert save(db, raw, received_at=RECEIVED + timedelta(days=8))["replay"]
    # Different bytes containing the same row can add a receipt but not a record.
    assert save(db, raw.strip())["inserted"] == 0
    status = inbox_status(db, now=RECEIVED + timedelta(days=8))
    assert status["receipt_freshness"] == status["freshness"] == "STALE"
    assert status["coverage"] == "UNKNOWN"
    record = export_observation(db, record_key=record_key(raw), release=RELEASE)
    assert record["record_state"] == "UNVERIFIED_IMPORT"
    assert record["receipt"]["sha256"] == hashlib.sha256(raw).hexdigest()
    with closing(sqlite3.connect(db)) as conn:
        assert conn.execute("SELECT payload FROM receipt WHERE sha256 = ?", (record["receipt"]["sha256"],)).fetchone()[0] == raw
        assert conn.execute("SELECT count(*) FROM observation").fetchone()[0] == 1


def test_conflicts_and_out_of_scope_batches_leave_no_partial_rows_or_receipt(tmp_path):
    db = tmp_path / "pilot.sqlite"
    create_inbox(db, make_scope())
    save(db, response(row()))
    with pytest.raises(InboxError, match="changed"):
        save(db, response(row(longitude=0.004), row(wur_radd_alerts__confidence=4)))
    with pytest.raises(InboxError, match="outside"):
        save(db, response(row(longitude=1.0)))
    with pytest.raises(InboxError, match="after receipt"):
        save(db, response(row(wur_radd_alerts__date="2026-11-14")))
    with pytest.raises(InboxError, match="envelope"):
        save(db, b'{"status":"success","status":"success","data":[]}')
    with closing(sqlite3.connect(db)) as conn:
        assert conn.execute("SELECT count(*) FROM receipt").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM observation").fetchone()[0] == 1


def test_empty_success_tracks_receipt_without_inventing_coverage_or_observations(tmp_path):
    db = tmp_path / "pilot.sqlite"
    create_inbox(db, make_scope())
    assert save(db, response())["inserted"] == 0
    status = inbox_status(db, now=RECEIVED)
    assert status["receipt_freshness"] == "WITHIN_GAP_LIMIT"
    assert status["freshness"] == status["coverage"] == "UNKNOWN"


def test_separate_restore_preserves_attributed_export_and_rejects_wrong_databases(tmp_path):
    db = tmp_path / "pilot.sqlite"
    backup = tmp_path / "backup.sqlite"
    restored = tmp_path / "restored.sqlite"
    other = tmp_path / "other.sqlite"
    create_inbox(db, make_scope())
    raw = response(row())
    save(db, raw)
    save(db, response(row(wur_radd_alerts__confidence=4)), release="v20261111")
    copy_inbox(db, backup)
    copy_inbox(backup, restored)
    original = export_observation(db, record_key=record_key(raw), release=RELEASE)
    assert original == export_observation(restored, record_key=record_key(raw), release=RELEASE)
    assert original["record_state"] == "UNVERIFIED_IMPORT"
    assert original["attribution"] == "Synthetic attribution fixture"
    with closing(sqlite3.connect(other)) as conn, conn:
        conn.execute("CREATE TABLE unrelated (id INTEGER)")
    with pytest.raises(InboxError, match="not a supported"):
        save(other, raw)
    with pytest.raises(FileExistsError):
        copy_inbox(db, restored)
    with closing(sqlite3.connect(restored)) as conn, conn:
        conn.execute("UPDATE observation SET source_row = '{}'")
    failed_row = tmp_path / "failed-row.sqlite"
    with pytest.raises(InboxError, match="observations failed"):
        copy_inbox(restored, failed_row)
    assert not failed_row.exists()
    with closing(sqlite3.connect(backup)) as conn, conn:
        conn.execute("UPDATE receipt SET payload = ?", (b"corrupted",))
    failed = tmp_path / "failed.sqlite"
    with pytest.raises(InboxError, match="bytes failed"):
        copy_inbox(backup, failed)
    assert not failed.exists()
