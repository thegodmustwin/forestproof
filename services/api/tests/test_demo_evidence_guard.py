"""Synthetic evidence is explicit opt-in; hosted and owner demos fail closed."""
from __future__ import annotations

import base64

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main
from app.config import Settings, get_settings
from app.store import Store


TOKEN = "a" * 43  # Synthetic test value; not a real credential.
PAYLOAD = {
    "file_name": "fixture.txt",
    "media_type": "text/plain",
    "content_base64": base64.b64encode(b"synthetic fixture").decode(),
    "source_description": "Synthetic evidence fixture",
    "actor": "Demo reviewer",
}


@pytest.mark.parametrize("value,enabled", [
    (None, False), ("false", False), ("yes", False), ("1", False),
    (" true ", False), ("true", True), ("TRUE", True),
])
def test_only_explicit_true_enables_flag(monkeypatch, value, enabled):
    if value is None:
        monkeypatch.delenv("FORESTPROOF_DEMO_EVIDENCE_UPLOADS_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FORESTPROOF_DEMO_EVIDENCE_UPLOADS_ENABLED", value)
    assert get_settings().demo_evidence_uploads_enabled is enabled


@pytest.mark.parametrize("mode,enabled,expected", [
    ("demo", False, 409), ("demo", True, 201),
    ("owner_demo", False, 409), ("owner_demo", True, 409),
])
def test_api_and_store_enforce_synthetic_only_opt_in(tmp_path, monkeypatch, mode, enabled, expected):
    settings = Settings(
        mode, tmp_path / "demo.db", tmp_path / "evidence", "http://127.0.0.1",
        internal_api_token=TOKEN, demo_evidence_uploads_enabled=enabled, owner_subject="pilot-owner-a",
    )
    store = Store(settings)
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "store", store)
    headers = {"X-Forestproof-Internal-Token": TOKEN, "X-Forestproof-Owner-Subject": "pilot-owner-a"} if mode == "owner_demo" else {}
    with TestClient(main.app) as client:
        observation = client.get("/api/v1/observations", headers=headers).json()["items"][0]
        created = client.post("/api/v1/cases", headers=headers, json={
            "observation_id": observation["id"], "title": "Synthetic upload guard",
            "owner_organization": "Demo", "reviewer": "Reviewer",
        })
        assert created.status_code == 201
        case_id = created.json()["id"]
        response = client.post(f"/api/v1/cases/{case_id}/evidence", headers=headers, json=PAYLOAD)
        assert response.status_code == expected
        if expected == 409:
            # Even a future caller that bypasses the HTTP endpoint cannot write.
            with pytest.raises(HTTPException) as error:
                store.attach_evidence(case_id, "fixture.txt", "text/plain",
                                      PAYLOAD["content_base64"], "Synthetic fixture", "Reviewer", None)
            assert error.value.status_code == 409
            assert not settings.evidence_directory.exists()
            assert client.get(f"/api/v1/cases/{case_id}", headers=headers).json()["evidence"] == []
        else:
            assert response.json()["file_name"] == "fixture.txt"
