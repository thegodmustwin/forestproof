"""Unsupported modes must leave configured storage untouched."""
from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import Settings
from app.store import Store


@pytest.mark.parametrize("mode", ["live", "production", "unknown"])
def test_disabled_modes_do_not_create_database_or_parent(tmp_path, monkeypatch, mode):
    database = tmp_path / "not-created" / "data.db"
    settings = Settings(mode, database, tmp_path / "evidence", "http://localhost:3000")
    store = Store(settings)
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "store", store)

    with TestClient(main.app) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/observations").status_code == 503
        assert client.post("/api/v1/ingestion/live/gfw").status_code == 503

    assert not database.parent.exists()
    with pytest.raises(RuntimeError, match="Storage is disabled"):
        store.list_observations("org_demo_aberdare")
    assert not database.parent.exists()


@pytest.mark.parametrize("mode", ["live", "production", "unknown"])
def test_disabled_modes_do_not_migrate_or_seed_existing_database(tmp_path, monkeypatch, mode):
    database = tmp_path / "existing.db"
    # Represent a prior unknown database, not actual or live records.
    with sqlite3.connect(database) as conn:
        conn.execute("CREATE TABLE sentinel (note TEXT)")
        conn.execute("INSERT INTO sentinel VALUES ('leave untouched')")
    original = database.read_bytes()

    settings = Settings(mode, database, tmp_path / "evidence", "http://localhost:3000")
    store = Store(settings)
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "store", store)
    with TestClient(main.app) as client:
        assert client.get("/api/v1/observations").status_code == 503

    assert database.read_bytes() == original
    with sqlite3.connect(database) as conn:
        with pytest.raises(RuntimeError, match="Demo seeding is disabled"):
            store.seed_demo_observations(conn)
        assert conn.execute("SELECT note FROM sentinel").fetchall() == [("leave untouched",)]
        assert conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall() == [("sentinel",)]
    assert database.read_bytes() == original


@pytest.mark.parametrize("mode", ["demo", "owner_demo"])
def test_supported_synthetic_modes_still_initialize_and_seed(tmp_path, mode):
    database = tmp_path / "demo.db"
    settings = Settings(mode, database, tmp_path / "evidence", "http://localhost:3000")
    store = Store(settings)
    store.prepare()
    assert database.is_file()
    assert store.list_observations("org_demo_aberdare")
