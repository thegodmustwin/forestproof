from __future__ import annotations

from fastapi.testclient import TestClient

from app import main
from app.config import Settings
from app.store import Store


def test_api_walks_observation_to_dossier(tmp_path, monkeypatch):
    test_settings = Settings("demo", tmp_path / "api.db", tmp_path / "evidence", "http://localhost:3000")
    monkeypatch.setattr(main, "settings", test_settings)
    monkeypatch.setattr(main, "store", Store(test_settings))
    with TestClient(main.app) as client:
        cors = client.options("/api/v1/observations", headers={
            "Origin": "http://127.0.0.1:3000", "Access-Control-Request-Method": "GET"
        })
        assert cors.status_code == 200
        assert cors.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
        observation_response = client.get("/api/v1/observations")
        assert observation_response.status_code == 200
        assert client.get("/api/v1/observations", headers={"X-Organization-ID": "org_other"}).status_code == 403
        observation = observation_response.json()["items"][0]
        assert "DEMO_DATA" in observation["quality_flags"]

        created = client.post("/api/v1/cases", json={
            "observation_id": observation["id"], "title": "API workflow test", "owner_organization": "Demo team", "reviewer": "Analyst"
        })
        assert created.status_code == 201
        case_id = created.json()["id"]

        transition = client.post(f"/api/v1/cases/{case_id}/transitions", json={
            "to_status": "UNDER_REVIEW", "actor": "Analyst", "note": "Opened for review."
        })
        assert transition.status_code == 200
        dossier = client.get(f"/api/v1/cases/{case_id}/dossier")
        assert dossier.status_code == 200
        assert dossier.json()["case"]["observation"]["source_record_id"].startswith("DEMO-")
