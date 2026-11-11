"""All provider envelopes in these tests are synthetic fixtures."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.providers.gfw_radd_research import ResearchBounds
from app.providers.radd_fixture_receipts import RaddFixtureReceiptStore, ReceiptConflict


@pytest.fixture
def store(tmp_path):
    ledger = RaddFixtureReceiptStore(tmp_path / "receipts.sqlite")
    ledger.initialize()
    return ledger


@pytest.fixture
def fixture_request():
    return {
        "receipt_id": str(uuid4()),
        "source_version": "v20261018",
        "bounds": ResearchBounds(36.61, -0.48, 36.62, -0.47),
        "received_at": datetime(2026, 10, 20, 12, tzinfo=timezone.utc),
        "raw_response": json.dumps({"status": "success", "data": [{
            "longitude": 36.61,
            "latitude": -0.48,
            "wur_radd_alerts__date": "2026-10-18",
            "wur_radd_alerts__confidence": 2,
            "wur_radd_alerts__date_conf": "synthetic",
            "area__ha": 0.01,
        }]}).encode("utf-8"),
        "synthetic_fixture": True,
    }


def test_receipt_persists_exact_fixture_hash_and_metadata_only(store, fixture_request):
    assert store.record(**fixture_request) == "inserted"
    result = store.get(fixture_request["receipt_id"])
    assert result["response_sha256"] == hashlib.sha256(fixture_request["raw_response"]).hexdigest()
    assert result["source_version"] == "v20261018"
    assert result["received_at"] == "2026-10-20T12:00:00+00:00"
    assert result["row_count"] == 1
    assert result["completeness"] == "UNKNOWN"
    assert "raw_response" not in result
    assert "data" not in result


def test_replay_is_idempotent_and_changed_receipt_is_rejected(store, fixture_request):
    assert store.record(**fixture_request) == "inserted"
    assert store.record(**fixture_request) == "unchanged"
    before = store.get(fixture_request["receipt_id"])
    # A byte-level change produces a different digest even when JSON is equivalent.
    changed = {**fixture_request, "raw_response": fixture_request["raw_response"] + b" "}
    with pytest.raises(ReceiptConflict):
        store.record(**changed)
    assert store.get(fixture_request["receipt_id"]) == before


def test_empty_result_does_not_imply_complete_coverage(store, fixture_request):
    fixture_request["raw_response"] = b'{"status":"success","data":[]}'
    store.record(**fixture_request)
    result = store.get(fixture_request["receipt_id"])
    assert result["row_count"] == 0
    assert result["completeness"] == "UNKNOWN"


@pytest.mark.parametrize("change", [
    {"synthetic_fixture": False},
    {"synthetic_fixture": 1},
    {"receipt_id": "not-an-id"},
    {"source_version": "latest"},
    {"received_at": datetime(2026, 1, 1)},
    {"bounds": ResearchBounds(36, -1, 38, 1)},
    {"raw_response": b'{"status":"success","data":[],"data":[]}'},
    {"raw_response": b'{"status":"error","data":[]}'},
    {"raw_response": b"\xff"},
    {"raw_response": b"x" * 2_000_001},
])
def test_invalid_input_fails_before_any_write(store, fixture_request, change):
    with pytest.raises(ValueError):
        store.record(**{**fixture_request, **change})
    with sqlite3.connect(store.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM radd_fixture_receipts").fetchone()[0] == 0


def test_different_receipt_ids_do_not_imply_a_retraction(store, fixture_request):
    store.record(**fixture_request)
    second = {**fixture_request, "receipt_id": str(uuid4()),
              "raw_response": b'{"status":"success","data":[]}'}
    store.record(**second)
    assert store.get(fixture_request["receipt_id"])["row_count"] == 1
    assert store.get(second["receipt_id"])["row_count"] == 0
    assert store.get(second["receipt_id"])["completeness"] == "UNKNOWN"
