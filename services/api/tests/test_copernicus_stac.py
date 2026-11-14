from __future__ import annotations

import json
import io
import threading
import time
from dataclasses import replace
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import Settings
from app.providers import copernicus_stac as stac
from app.store import Store


NOW = datetime(2026, 10, 29, 13, tzinfo=UTC)
TOKEN = "A" * 43
FEATURE = {
    "type": "Feature", "id": "S2A_SYNTHETIC_001", "collection": "sentinel-2-l2a",
    "bbox": [36.3, -1.0, 37.2, 0.0],
    "properties": {"datetime": "2026-10-28T07:40:21Z", "platform": "sentinel-2a", "eo:cloud_cover": 57.9},
}


class FakeResponse:
    status = 200

    def __init__(self, payload: object):
        self.body = json.dumps(payload).encode()
        self.stream = io.BytesIO(self.body)
        self.headers = {"Content-Type": "application/json", "Content-Length": str(len(self.body))}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, maximum: int) -> bytes:
        return self.stream.read(maximum)


def fake_catalog(monkeypatch, payload):
    response = FakeResponse(payload)
    observed = {}

    class Opener:
        def open(self, request, timeout):
            observed.update(request=request, timeout=timeout)
            return response

    monkeypatch.setattr(stac, "build_opener", lambda *_args: Opener())
    return observed, response


def test_bounded_scene_lookup_requests_only_metadata_and_preserves_uncertainty(monkeypatch):
    observed, _ = fake_catalog(monkeypatch, {"type": "FeatureCollection", "features": [FEATURE]})
    result = stac.fetch_recent_scenes(now=NOW)
    request = observed["request"]
    parsed = urlsplit(request.full_url)
    query = parse_qs(parsed.query)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == stac.CATALOG_URL
    assert request.get_method() == "GET" and observed["timeout"] == 10
    assert query["collections"] == ["sentinel-2-l2a"]
    assert query["bbox"] == ["36.5,-0.7,36.7,-0.25"] and query["limit"] == ["3"]
    assert "assets" not in query["fields"][0]
    assert result["scenes"] == [{"id": "S2A_SYNTHETIC_001", "acquired_at": "2026-10-28T07:40:21Z",
                                  "platform": "sentinel-2a", "scene_cloud_cover_percent": 57.9}]
    assert "not a forest-loss alert" in result["notice"]
    assert "not an official forest boundary" in result["notice"]
    assert "Copernicus Sentinel data" in result["attribution"]


def test_empty_scene_response_does_not_imply_source_health_or_no_forest_change(monkeypatch):
    fake_catalog(monkeypatch, {"type": "FeatureCollection", "features": []})
    result = stac.fetch_recent_scenes(now=NOW)
    assert result["scenes"] == []
    assert "Results may be incomplete" in result["notice"]


@pytest.mark.parametrize("changes", [
    {"type": "not-a-feature"}, {"collection": "other"}, {"id": "bad/id"},
    {"bbox": [1, 1, 2, 2]}, {"bbox": [36, -1, float("nan"), 0]},
    {"properties": {"datetime": "2026-10-28T07:40:21", "platform": "sentinel-2a"}},
    {"properties": {"datetime": "2026-10-30T07:40:21Z", "platform": "sentinel-2a"}},
    {"properties": {"datetime": "2026-10-28T07:40:21Z", "eo:cloud_cover": 101}},
])
def test_invalid_or_out_of_scope_scene_is_rejected(monkeypatch, changes):
    feature = {**FEATURE, **changes}
    fake_catalog(monkeypatch, {"type": "FeatureCollection", "features": [feature]})
    with pytest.raises(stac.CatalogUnavailable):
        stac.fetch_recent_scenes(now=NOW)


def test_repeated_scene_ids_fail_closed(monkeypatch):
    fake_catalog(monkeypatch, {"type": "FeatureCollection", "features": [FEATURE, FEATURE]})
    with pytest.raises(stac.CatalogUnavailable):
        stac.fetch_recent_scenes(now=NOW)


def test_oversized_truncated_and_wrong_content_type_responses_are_rejected(monkeypatch):
    _, response = fake_catalog(monkeypatch, {"type": "FeatureCollection", "features": []})
    response.headers["Content-Length"] = str(len(response.body) + 1)
    with pytest.raises(stac.CatalogUnavailable):
        stac.fetch_recent_scenes(now=NOW)
    _, response = fake_catalog(monkeypatch, {"type": "FeatureCollection", "features": []})
    response.headers["Content-Type"] = "text/html"
    with pytest.raises(stac.CatalogUnavailable):
        stac.fetch_recent_scenes(now=NOW)
    _, response = fake_catalog(monkeypatch, {"type": "FeatureCollection", "features": []})
    response.headers["Content-Length"] = str(stac.MAX_RESPONSE_BYTES + 1)
    with pytest.raises(stac.CatalogUnavailable):
        stac.fetch_recent_scenes(now=NOW)


def test_success_and_failure_are_rate_limited_without_silent_stale_data():
    clock = [0.0]
    calls = []

    def fetch():
        calls.append(1)
        if len(calls) > 1:
            raise stac.CatalogUnavailable("synthetic failure")
        return {"scenes": [{"id": "synthetic"}]}

    catalog = stac.CopernicusCatalog(fetcher=fetch, clock=lambda: clock[0])
    first = catalog.latest()
    first["scenes"][0]["id"] = "modified locally"
    assert catalog.latest()["scenes"][0]["id"] == "synthetic"
    assert len(calls) == 1
    clock[0] = stac.CACHE_SECONDS
    with pytest.raises(stac.CatalogUnavailable):
        catalog.latest()
    with pytest.raises(stac.CatalogUnavailable):
        catalog.latest()
    assert len(calls) == 2


def test_simultaneous_clicks_share_one_bounded_lookup():
    calls = []
    snapshots = []
    barrier = threading.Barrier(5)

    def fetch():
        calls.append(1)
        time.sleep(0.02)
        return {"scenes": []}

    catalog = stac.CopernicusCatalog(fetcher=fetch, clock=lambda: 100.0)

    def worker():
        barrier.wait()
        snapshots.append(catalog.latest())

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)
    assert len(calls) == 1 and len(snapshots) == 5


def test_route_is_disabled_for_shared_demo_and_requires_owner_service_auth(tmp_path, monkeypatch):
    settings = Settings("demo", tmp_path / "demo.db", tmp_path / "evidence", "http://127.0.0.1", TOKEN, True)
    calls = []

    class Catalog:
        def latest(self):
            calls.append(1)
            return {"scenes": []}

    monkeypatch.setattr(main, "copernicus_catalog", Catalog())
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "store", Store(settings))
    with TestClient(main.app) as client:
        assert client.get("/api/v1/context/copernicus-scenes").status_code == 503
    assert calls == []

    settings = replace(settings, mode="owner_demo", copernicus_catalog_enabled=False, owner_subject="pilot-owner-a")
    owner_headers = {"X-Forestproof-Internal-Token": TOKEN, "X-Forestproof-Owner-Subject": "pilot-owner-a"}
    monkeypatch.setattr(main, "settings", settings)
    monkeypatch.setattr(main, "store", Store(settings))
    with TestClient(main.app) as client:
        assert client.get("/api/v1/context/copernicus-scenes").status_code == 401
        assert client.get("/api/v1/context/copernicus-scenes", headers=owner_headers).status_code == 503
    assert calls == []

    settings = replace(settings, copernicus_catalog_enabled=True)
    monkeypatch.setattr(main, "settings", settings)
    with TestClient(main.app) as client:
        response = client.get("/api/v1/context/copernicus-scenes", headers=owner_headers)
        assert response.status_code == 200 and response.json() == {"scenes": []}
        assert response.headers["cache-control"] == "no-store"
    assert calls == [1]
