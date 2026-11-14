"""Synthetic owner-demo service-boundary tests; no real credential is used."""

from dataclasses import replace

from fastapi.testclient import TestClient

from app import main
from app.config import Settings
from app.store import Store


TEST_TOKEN = "A" * 43
WRONG_TOKEN = "B" * 43
SUBJECT = "pilot-owner-a"
OWNER_HEADERS = {"X-Forestproof-Internal-Token": TEST_TOKEN, "X-Forestproof-Owner-Subject": SUBJECT}


def configure(monkeypatch, tmp_path, *, mode="owner_demo", token=TEST_TOKEN, subject=SUBJECT):
    settings = Settings(mode, tmp_path / "owner-demo.db", tmp_path / "evidence", "http://127.0.0.1:18080", token,
                        owner_subject=subject)
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "store", Store(settings))
    return settings


def test_owner_demo_requires_configured_internal_token_even_with_forged_tenant(monkeypatch, tmp_path):
    settings = configure(monkeypatch, tmp_path)
    assert TEST_TOKEN not in repr(settings)
    with TestClient(main.app) as client:
        assert client.get("/api/v1/observations").status_code == 401
        assert client.get("/api/v1/observations", headers={"X-Organization-ID": "org_demo_aberdare"}).status_code == 401
        assert client.get("/api/v1/observations", headers={"X-Forestproof-Internal-Token": WRONG_TOKEN}).status_code == 401
        assert client.get("/api/v1/observations", headers={"X-Forestproof-Internal-Token": "short"}).status_code == 401
        assert client.get("/api/v1/observations", headers={"X-Forestproof-Internal-Token": TEST_TOKEN}).status_code == 401
        assert client.get("/api/v1/observations", headers={**OWNER_HEADERS, "X-Forestproof-Owner-Subject": "other"}).status_code == 401
        assert client.get("/api/v1/observations", headers=[*OWNER_HEADERS.items(), ("X-Forestproof-Owner-Subject", SUBJECT)]).status_code == 401
        assert client.get("/api/v1/observations", headers=[*OWNER_HEADERS.items(), ("X-Forestproof-Internal-Token", TEST_TOKEN)]).status_code == 401
        assert client.get("/api/v1/observations", headers={**OWNER_HEADERS, "X-Organization-ID": "other"}).status_code == 403
        result = client.get("/api/v1/observations", headers=OWNER_HEADERS)
        assert result.status_code == 200
        assert all("DEMO_DATA" in row["quality_flags"] for row in result.json()["items"])


def test_missing_or_invalid_configuration_fails_closed_and_never_echoes_the_token(monkeypatch, tmp_path):
    settings = configure(monkeypatch, tmp_path, token=None)
    with TestClient(main.app) as client:
        response = client.get("/api/v1/observations", headers=OWNER_HEADERS)
        assert response.status_code == 503 and TEST_TOKEN not in response.text
    monkeypatch.setattr(main, "settings", replace(settings, internal_api_token="not-strong-enough"))
    with TestClient(main.app) as client:
        response = client.get("/api/v1/observations", headers=OWNER_HEADERS)
        assert response.status_code == 503 and "not-strong-enough" not in response.text
    for invalid_subject in (None, "contains spaces", "linebreak\n"):
        configure(monkeypatch, tmp_path, subject=invalid_subject)
        with TestClient(main.app) as client:
            assert client.get("/api/v1/observations", headers=OWNER_HEADERS).status_code == 503


def test_owner_demo_attributes_mutations_to_owner_and_disables_evidence_uploads(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    with TestClient(main.app) as client:
        observation = client.get("/api/v1/observations", headers=OWNER_HEADERS).json()["items"][0]
        created = client.post("/api/v1/cases", headers=OWNER_HEADERS, json={
            "observation_id": observation["id"], "title": "Synthetic review case",
            "owner_organization": "Demo team", "reviewer": "Reviewer label",
        })
        assert created.status_code == 201
        case_id = created.json()["id"]
        assert client.get(f"/api/v1/cases/{case_id}").status_code == 401
        assert client.get(f"/api/v1/cases/{case_id}", headers=OWNER_HEADERS).json()["events"][0]["actor"] == SUBJECT

        def transition(target):
            return client.post(f"/api/v1/cases/{case_id}/transitions", headers=OWNER_HEADERS,
                               json={"to_status": target, "actor": "spoofed actor", "note": "Synthetic review"})

        assert transition("UNDER_REVIEW").status_code == 200
        assignment = client.post(f"/api/v1/cases/{case_id}/assignments", headers=OWNER_HEADERS,
                                 json={"assignee": "Demo reviewer", "role": "reviewer", "actor": "spoofed actor"})
        assert assignment.status_code == 201 and assignment.json()["assigned_by"] == SUBJECT
        assert transition("FIELD_VERIFICATION").status_code == 200
        action = client.post(f"/api/v1/cases/{case_id}/actions", headers=OWNER_HEADERS,
                             json={"action_type": "SYNTHETIC", "summary": "Demo action", "actor": "spoofed actor"})
        assert action.status_code == 201 and action.json()["recorded_by"] == SUBJECT
        assert transition("ACTION_RECORDED").status_code == 200
        followup = client.post(f"/api/v1/cases/{case_id}/follow-ups", headers=OWNER_HEADERS,
                               json={"assessment": "UNRESOLVED", "summary": "Demo follow-up", "actor": "spoofed actor"})
        assert followup.status_code == 201 and followup.json()["recorded_by"] == SUBJECT
        evidence = client.post(f"/api/v1/cases/{case_id}/evidence", headers=OWNER_HEADERS, json={
            "file_name": "demo.txt", "content_base64": "dGVzdA==", "source_description": "Synthetic", "actor": "spoofed actor",
        })
        assert evidence.status_code == 409
        events = client.get(f"/api/v1/cases/{case_id}", headers=OWNER_HEADERS).json()["events"]
        assert all(event["actor"] == SUBJECT for event in events)


def test_owner_proxy_mode_guard_rejects_misconfigured_demo_api_and_live_stays_closed(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path, mode="demo")
    with TestClient(main.app) as client:
        assert client.get("/api/v1/observations").status_code == 200
        assert client.get("/api/v1/observations", headers={"X-Forestproof-Require-Owner-Demo": "1"}).status_code == 503
    configure(monkeypatch, tmp_path, mode="live")
    with TestClient(main.app) as client:
        assert client.get("/api/v1/observations", headers=OWNER_HEADERS).status_code == 503
        assert client.post("/api/v1/ingestion/live/gfw", headers=OWNER_HEADERS).status_code == 503
