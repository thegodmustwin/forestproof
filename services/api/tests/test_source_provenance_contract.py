"""API contract tests use synthetic fixtures; no live provider access occurs."""
from datetime import date, datetime, timezone
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import main
from app.config import Settings
from app.source_provenance import SourceProvenance
from app.store import Store


@pytest.fixture
def demo_client(tmp_path, monkeypatch):
    config = Settings("demo", tmp_path / "demo.db", tmp_path / "evidence", "http://localhost:3000")
    monkeypatch.setattr(main, "settings", config)
    monkeypatch.setattr(main, "store", Store(config))
    with TestClient(main.app) as client:
        yield client, config


def test_provenance_is_available_through_the_observation_to_dossier_workflow(demo_client):
    client, _ = demo_client
    response = client.get("/api/v1/observations")
    assert response.status_code == 200
    item = response.json()["items"][0]
    provenance = item["source_provenance"]
    assert provenance["contract_version"] == "1"
    assert provenance["data_mode"] == "DEMO"
    assert provenance["record_key"] == item["source_record_id"]
    assert provenance["record_key_kind"] == "SYNTHETIC_FIXTURE"
    assert provenance["source_release"] is None
    assert provenance["attribution"] is None
    assert provenance["completeness"] == "UNKNOWN"

    detail = client.get(f"/api/v1/observations/{item['id']}")
    assert detail.status_code == 200
    assert detail.json()["source_provenance"] == provenance

    created = client.post("/api/v1/cases", json={
        "observation_id": item["id"], "title": "Synthetic source record",
        "owner_organization": "Fixture group", "reviewer": "Reviewer",
    })
    assert created.status_code == 201
    case_id = created.json()["id"]
    case = client.get(f"/api/v1/cases/{case_id}").json()
    dossier = client.get(f"/api/v1/cases/{case_id}/dossier").json()
    assert case["observation"]["source_provenance"] == provenance
    assert dossier["case"]["observation"]["source_provenance"] == provenance


def test_unlabeled_or_foreign_rows_fail_closed_instead_of_being_relabelled(demo_client):
    client, config = demo_client
    items = client.get("/api/v1/observations").json()["items"]
    record_id = items[0]["id"]
    with sqlite3.connect(config.database_path) as db:
        db.execute(
            "UPDATE observations SET source_id = ?, quality_flags_json = ? WHERE id = ?",
            ("other-source", json.dumps(["DEMO_DATA", "NOT_A_LIVE_DETECTION"]), record_id),
        )
    detail = client.get(f"/api/v1/observations/{record_id}")
    assert detail.status_code == 503
    assert detail.json()["detail"] == "Observation source provenance is unavailable"
    assert client.get("/api/v1/observations").status_code == 503


def test_provider_neutral_contract_preserves_date_precision_and_rejects_demo_mixing():
    # Synthetic test values describe the contract only, not an actual source.
    fields = dict(
        data_mode="LIVE", source_id="example-provider", product="example-product",
        source_release="v20261112", processing_version="adapter-1",
        record_key="cell-123", record_key_kind="DERIVED_CELL",
        observed_on=date(2026, 11, 10), received_at=datetime(2026, 11, 12, tzinfo=timezone.utc),
        quality_flags=[], completeness="UNKNOWN",
    )
    record = SourceProvenance(**fields)
    assert record.observed_at is None
    assert record.observed_on == date(2026, 11, 10)
    assert record.completeness == "UNKNOWN"
    for invalid in (
        {"quality_flags": ["DEMO_DATA"]},
        {"quality_flags": [" demo_data "]},
        {"source_id": "demo-synthetic-v1"},
        {"record_key_kind": "SYNTHETIC_FIXTURE"},
        {"source_release": None},
        {"source_release": "latest"},
        {"source_release": " LATEST "},
        {"observed_at": datetime(2026, 11, 10, tzinfo=timezone.utc)},
        {"received_at": datetime(2026, 11, 12)},
    ):
        with pytest.raises(ValidationError):
            SourceProvenance(**{**fields, **invalid})


def test_non_demo_mode_and_owner_demo_without_token_remain_closed(tmp_path, monkeypatch):
    for mode in ("live", "owner_demo"):
        config = Settings(mode, tmp_path / f"{mode}.db", tmp_path / "evidence", "http://localhost:3000")
        monkeypatch.setattr(main, "settings", config)
        monkeypatch.setattr(main, "store", Store(config))
        with TestClient(main.app) as client:
            response = client.get("/api/v1/observations")
            assert response.status_code == 503
            assert client.post("/api/v1/ingestion/live/gfw").status_code == 503
