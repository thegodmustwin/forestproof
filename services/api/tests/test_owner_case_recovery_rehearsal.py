"""Exercise the synthetic receipt, owner case, dossier and restore as one chain."""

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.config import Settings
from app.demo_db_copy import copy_demo_database
from app.demo_data import DEMO_OBSERVATIONS
from app.pilot_radd_inbox import (
    PilotScope,
    copy_inbox,
    create_inbox,
    export_observation,
    import_receipt,
    list_observations,
)
from app.store import Store


RELEASE = "v20261014"
RECEIVED = datetime(2026, 10, 14, 8, 5, 12, tzinfo=timezone.utc)
OWNER_SUBJECT = "rehearsal-owner"
OWNER_HEADERS = {
    "X-Forestproof-Internal-Token": "A" * 43,
    "X-Forestproof-Owner-Subject": OWNER_SUBJECT,
    "X-Forestproof-Require-Owner-Demo": "1",
}


def configure_owner_app(monkeypatch, database: Path) -> None:
    settings = Settings(
        mode="owner_demo",
        database_path=database,
        evidence_directory=database.parent / "evidence",
        web_origin="http://127.0.0.1:18080",
        internal_api_token=OWNER_HEADERS["X-Forestproof-Internal-Token"],
        owner_subject=OWNER_SUBJECT,
    )
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "store", Store(settings))


def see_dossier(client, path):
    response = client.get(path, headers=OWNER_HEADERS)
    assert response.status_code == 200
    dossier = response.json()
    del dossier["generated_at"]
    return dossier


def test_synthetic_receipt_is_traceable_from_owner_case_after_both_stores_restore(monkeypatch, tmp_path):
    inbox, case_db = tmp_path / "inbox.sqlite", tmp_path / "cases.sqlite"
    fixture = DEMO_OBSERVATIONS[0]
    longitude, latitude = fixture["geometry"]["coordinates"]
    source_day = fixture["observed_at"][:10]
    raw = json.dumps({
        "status": "success",
        "data": [{"longitude": longitude, "latitude": latitude, "wur_radd_alerts__date": source_day}],
    }).encode()
    create_inbox(inbox, PilotScope(
        scope_id="synthetic-owner-rehearsal",
        review_ref="repository demo fixture",
        attribution="ForestProof synthetic RADD-shaped fixture",
        bounds=(longitude - 0.004, latitude - 0.004, longitude + 0.004, latitude + 0.004),
        max_observation_age_days=7,
        max_receipt_gap_hours=24,
    ))
    assert import_receipt(inbox, raw, release=RELEASE, received_at=RECEIVED)["inserted"] == 1
    replay = import_receipt(inbox, raw, release=RELEASE, received_at=RECEIVED)
    assert replay["inserted"] == 0 and replay["replay"]
    records = list_observations(inbox)
    assert len(records) == 1
    receipt = export_observation(inbox, record_key=records[0]["record_key"], release=RELEASE)
    assert receipt["record_state"] == "UNVERIFIED_IMPORT"
    assert receipt["observed_on"] == source_day
    assert receipt["receipt"]["sha256"] == hashlib.sha256(raw).hexdigest()
    receipt_ref = f"demo://rehearsal/radd/{RELEASE}/{receipt['receipt']['sha256']}"

    configure_owner_app(monkeypatch, case_db)
    with TestClient(main.app) as client:
        # The rehearsal links one known repository fixture in its isolated database.
        # There is no API or runtime adapter for promoting inbox records.
        with closing(sqlite3.connect(case_db)) as connection, connection:
            assert connection.execute(
                "UPDATE observations SET raw_evidence_ref = ? WHERE id = ? AND source_id = ?",
                (receipt_ref, fixture["id"], fixture["source_id"]),
            ).rowcount == 1
        observation_url = f"/api/v1/observations/{fixture['id']}"
        assert client.get(observation_url).status_code == 401
        observation = client.get(observation_url, headers=OWNER_HEADERS).json()
        assert observation["source_provenance"]["data_mode"] == "DEMO"
        assert observation["raw_evidence_ref"] == receipt_ref
        payload = {
            "observation_id": fixture["id"],
            "title": "Synthetic receipt review",
            "owner_organization": "Rehearsal team",
            "reviewer": "Display label",
        }
        created = client.post("/api/v1/cases", headers=OWNER_HEADERS, json=payload)
        assert created.status_code == 201
        case_id = created.json()["id"]
        repeated = client.post("/api/v1/cases", headers=OWNER_HEADERS, json=payload)
        assert repeated.status_code == 201 and repeated.json()["id"] == case_id
        assert len(client.get("/api/v1/cases", headers=OWNER_HEADERS).json()["items"]) == 1
        case_url = f"/api/v1/cases/{case_id}"

        def post(suffix, **fields):
            return client.post(f"{case_url}/{suffix}", headers=OWNER_HEADERS, json={
                "actor": "Untrusted request label", **fields,
            })

        def transition(status):
            return post("transitions", to_status=status, note="Synthetic owner rehearsal")

        assert transition("UNDER_REVIEW").status_code == 200
        assert transition("FIELD_VERIFICATION").status_code == 200
        assert transition("ACTION_RECORDED").status_code == 409
        action = post("actions", action_type="DESK_REVIEW", summary="Checked synthetic receipt context.")
        assert action.status_code == 201 and action.json()["recorded_by"] == OWNER_SUBJECT
        assert transition("ACTION_RECORDED").status_code == 200
        assert transition("FOLLOW_UP").status_code == 200
        assert transition("CLOSED").status_code == 409
        follow_up = post("follow-ups", assessment="INSUFFICIENT_EVIDENCE", summary="No field finding in this rehearsal.")
        assert follow_up.status_code == 201 and follow_up.json()["recorded_by"] == OWNER_SUBJECT
        assert transition("CLOSED").status_code == 200
        assert post("evidence", file_name="fixture.txt", content_base64="dGVzdA==",
                    source_description="Synthetic").status_code == 409
        dossier_url = f"{case_url}/dossier"
        assert client.get(dossier_url).status_code == 401
        original = see_dossier(client, dossier_url)
        saved = original["case"]
        assert saved["status"] == "CLOSED"
        assert saved["observation"]["id"] == fixture["id"]
        assert saved["observation"]["raw_evidence_ref"] == receipt_ref
        assert saved["observation"]["source_provenance"]["data_mode"] == "DEMO"
        assert {event["actor"] for event in saved["events"]} == {OWNER_SUBJECT}
        assert original["completeness"]["action_recorded"]
        assert original["completeness"]["follow_up_recorded"]

    backup = tmp_path / "backup"
    restored = tmp_path / "restored"
    backup.mkdir()
    restored.mkdir()
    copy_inbox(inbox, backup / inbox.name)
    copy_demo_database(case_db, backup / case_db.name)
    copy_inbox(backup / inbox.name, restored / inbox.name)
    copy_demo_database(backup / case_db.name, restored / case_db.name)
    assert export_observation(restored / inbox.name, record_key=records[0]["record_key"], release=RELEASE) == receipt
    configure_owner_app(monkeypatch, restored / case_db.name)
    with TestClient(main.app) as client:
        assert client.get(dossier_url).status_code == 401
        assert see_dossier(client, dossier_url) == original
