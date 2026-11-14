"""Exercise the synthetic receipt, owner case, dossier and restore as one chain."""

import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.config import Settings
from app.demo_db_copy import copy_demo_database
from app.owner_receipt_rehearsal import FIXTURE, FIXTURE_RELEASE, prepare_rehearsal_inbox
from app.pilot_radd_inbox import copy_inbox, export_observation, list_observations
from app.store import Store


OWNER_SUBJECT = "rehearsal-owner"
OWNER_HEADERS = {
    "X-Forestproof-Internal-Token": "A" * 43,
    "X-Forestproof-Owner-Subject": OWNER_SUBJECT,
    "X-Forestproof-Require-Owner-Demo": "1",
}


def configure_owner_app(monkeypatch, database: Path, inbox: Path | None, *, mode: str = "owner_demo") -> None:
    settings = Settings(
        mode=mode,
        database_path=database,
        evidence_directory=database.parent / "evidence",
        web_origin="http://127.0.0.1:18080",
        internal_api_token=OWNER_HEADERS["X-Forestproof-Internal-Token"],
        owner_subject=OWNER_SUBJECT,
        owner_rehearsal_inbox_path=inbox,
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
    prepare_rehearsal_inbox(inbox)
    records = list_observations(inbox)
    assert len(records) == 1
    key = records[0]["record_key"]
    receipt = export_observation(inbox, record_key=key, release=FIXTURE_RELEASE)
    assert receipt["observed_on"] == FIXTURE["observed_at"][:10]
    expected = {
        "data_mode": "DEMO",
        "record_state": "UNVERIFIED_IMPORT",
        "record_key": key,
        "fixture_release": FIXTURE_RELEASE,
        "observed_on": receipt["observed_on"],
        "receipt": receipt["receipt"],
    }

    configure_owner_app(monkeypatch, case_db, inbox)
    with TestClient(main.app) as client:
        observation_url = f"/api/v1/observations/{FIXTURE['id']}"
        assert client.get(observation_url).status_code == 401
        observation = client.get(observation_url, headers=OWNER_HEADERS)
        assert observation.status_code == 200
        assert observation.json()["source_provenance"]["data_mode"] == "DEMO"
        assert observation.json()["raw_evidence_ref"] == FIXTURE["raw_evidence_ref"]
        assert observation.json()["rehearsal_receipt"] == expected
        assert client.get(observation_url, headers=OWNER_HEADERS).json() == observation.json()
        assert all(
            "rehearsal_receipt" not in record for record in
            client.get("/api/v1/observations", headers=OWNER_HEADERS).json()["items"]
        )
        payload = {
            "observation_id": FIXTURE["id"],
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
        assert client.get(case_url, headers=OWNER_HEADERS).json()["observation"]["rehearsal_receipt"] == expected
        dossier_url = f"{case_url}/dossier"
        assert client.get(dossier_url).status_code == 401
        original = see_dossier(client, dossier_url)
        saved = original["case"]
        assert saved["status"] == "CLOSED"
        assert saved["observation"]["id"] == FIXTURE["id"]
        assert saved["observation"]["rehearsal_receipt"] == expected
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
    assert export_observation(restored / inbox.name, record_key=key, release=FIXTURE_RELEASE) == receipt
    configure_owner_app(monkeypatch, restored / case_db.name, restored / inbox.name)
    with TestClient(main.app) as client:
        assert client.get(dossier_url).status_code == 401
        assert see_dossier(client, dossier_url) == original


def test_receipt_configuration_is_owner_only_optional_and_fails_closed(monkeypatch, tmp_path):
    case_db, inbox = tmp_path / "cases.sqlite", tmp_path / "missing-inbox.sqlite"
    observation_url = f"/api/v1/observations/{FIXTURE['id']}"

    configure_owner_app(monkeypatch, case_db, None)
    with TestClient(main.app) as client:
        response = client.get(observation_url, headers=OWNER_HEADERS)
        assert response.status_code == 200
        assert "rehearsal_receipt" not in response.json()

    configure_owner_app(monkeypatch, case_db, inbox, mode="demo")
    with TestClient(main.app) as client:
        response = client.get(observation_url)
        assert response.status_code == 200
        assert "rehearsal_receipt" not in response.json()

    configure_owner_app(monkeypatch, case_db, inbox, mode="live")
    with TestClient(main.app) as client:
        assert client.get(observation_url, headers=OWNER_HEADERS).status_code == 503

    configure_owner_app(monkeypatch, case_db, inbox)
    with TestClient(main.app) as client:
        assert client.get(observation_url).status_code == 401
        bad_owner = {**OWNER_HEADERS, "X-Forestproof-Owner-Subject": "someone-else"}
        assert client.get(observation_url, headers=bad_owner).status_code == 401
        duplicate = [*OWNER_HEADERS.items(), ("X-Forestproof-Owner-Subject", OWNER_SUBJECT)]
        assert client.get(observation_url, headers=duplicate).status_code == 401
        response = client.get(observation_url, headers=OWNER_HEADERS)
        assert response.status_code == 503
        assert response.json() == {"detail": "Synthetic rehearsal receipt is unavailable"}
        other = client.get("/api/v1/observations/obs_demo_002", headers=OWNER_HEADERS)
        assert other.status_code == 200
        assert "rehearsal_receipt" not in other.json()
        assert client.post("/api/v1/cases", headers=OWNER_HEADERS, json={
            "observation_id": FIXTURE["id"],
            "title": "Unready rehearsal",
            "owner_organization": "Rehearsal team",
        }).status_code == 503
        assert client.get("/api/v1/cases", headers=OWNER_HEADERS).json()["items"] == []
        assert not inbox.exists()

        prepare_rehearsal_inbox(inbox)
        assert client.get(observation_url, headers=OWNER_HEADERS).status_code == 200
        with closing(sqlite3.connect(inbox)) as db, db:
            db.execute("UPDATE receipt SET payload = ?", (b"same record with changed bytes",))
        assert client.get(observation_url, headers=OWNER_HEADERS).status_code == 503
