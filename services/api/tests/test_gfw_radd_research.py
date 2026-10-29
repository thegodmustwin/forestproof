"""Network-free tests: every provider response and key here is synthetic."""

from __future__ import annotations

import hashlib
import io
import json
import threading
from dataclasses import fields, replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import pytest

from app.providers.gfw_radd_envelope import MAX_ENVELOPE_BYTES
from app.providers.gfw_radd_research import (
    ProviderQueryError,
    ProviderRateLimited,
    QueryNotAuthorized,
    ResearchBounds,
    ResearchPrerequisites,
    ResponseIncomplete,
    _NoRedirect,
    fetch_radd_research,
)


TEST_KEY = "synthetic-not-a-provider-credential"
BOUNDS = ResearchBounds(36.600, -0.480, 36.605, -0.475)
PERMITTED = ResearchPrerequisites(**{item.name: True for item in fields(ResearchPrerequisites)})
ROW = {"longitude": 36.602, "latitude": -0.478, "wur_radd_alerts__date": "2026-10-18",
       "wur_radd_alerts__confidence": 2, "area__ha": 0.01}


class FakeResponse:
    def __init__(self, body: bytes, *, status: int = 200, headers: dict[str, str] | None = None):
        self.status = status
        self.headers = headers if headers is not None else {"Content-Type": "application/json"}
        self.stream = io.BytesIO(body)
        self.closed = False

    def read(self, size: int) -> bytes:
        return self.stream.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True
        self.stream.close()


class FakeOpener:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def __call__(self, request, *, timeout):
        self.calls.append((request, timeout))
        if self.error:
            raise self.error
        return self.response


def request(opener, **kwargs):
    options = {"source_version": "v20261018", "bounds": BOUNDS, "api_key": TEST_KEY,
               "prerequisites": PERMITTED}
    options.update(kwargs)
    with patch("app.providers.gfw_radd_research.build_opener", return_value=SimpleNamespace(open=opener)):
        return fetch_radd_research(**options)


def test_every_unreviewed_prerequisite_blocks_all_network_activity():
    opener = FakeOpener()
    with pytest.raises(QueryNotAuthorized):
        request(opener, prerequisites=ResearchPrerequisites())
    for item in fields(ResearchPrerequisites):
        with pytest.raises(QueryNotAuthorized, match=item.name):
            request(opener, prerequisites=replace(PERMITTED, **{item.name: False}))
        with pytest.raises(QueryNotAuthorized, match=item.name):
            request(opener, prerequisites=replace(PERMITTED, **{item.name: "true"}))
    assert opener.calls == []


def test_synthetic_success_uses_fixed_destination_header_only_key_and_exact_raw_bytes():
    raw = json.dumps({"status": "success", "data": [ROW]}, indent=2).encode()
    response = FakeResponse(raw, headers={"Content-Type": "application/json; charset=utf-8", "Content-Length": str(len(raw))})
    opener = FakeOpener(response)
    result = request(opener, max_rows=2, origin="https://example.org")
    sent, timeout = opener.calls[0]
    assert len(opener.calls) == 1 and timeout == 10
    assert sent.full_url == "https://data-api.globalforestwatch.org/dataset/wur_radd_alerts/v20261018/query/json"
    assert sent.get_method() == "POST" and TEST_KEY not in sent.full_url
    assert sent.get_header("X-api-key") == TEST_KEY
    assert sent.get_header("Origin") == "https://example.org"
    payload = json.loads(sent.data)
    assert payload["geometry"]["type"] == "Polygon"
    assert payload["geometry"]["coordinates"][0][0] == [BOUNDS.west, BOUNDS.south]
    assert payload["geometry"]["coordinates"][0][-1] == [BOUNDS.west, BOUNDS.south]
    assert payload["sql"].endswith("LIMIT 3")
    assert TEST_KEY not in sent.data.decode()
    assert result.raw_response == raw
    assert result.raw_sha256 == hashlib.sha256(raw).hexdigest()
    assert result.envelope.cells[0].raw_fields == ROW
    assert result.received_at.utcoffset().total_seconds() == 0
    assert TEST_KEY not in repr(result) and raw.decode() not in repr(result)
    assert response.closed


@pytest.mark.parametrize("overrides", [
    {"source_version": "latest"},
    {"source_version": "v1/../../secret"},
    {"bounds": ResearchBounds(36.6, -0.5, 37, -0.4)},
    {"bounds": ResearchBounds(181, -0.5, 182, -0.4)},
    {"bounds": ResearchBounds(36.6, -0.5, float("nan"), -0.49)},
    {"bounds": ResearchBounds(True, -0.5, 1.001, -0.49)},
    {"max_rows": 0},
    {"max_rows": True},
    {"max_rows": 101},
    {"api_key": "synthetic\nheader"},
    {"origin": "http://example.org"},
    {"origin": "https://example.org/path?token=secret"},
    {"origin": "https://user:secret@example.org"},
    {"origin": "https://example.\norg"},
])
def test_invalid_inputs_fail_before_network(overrides):
    opener = FakeOpener()
    with pytest.raises(ValueError):
        request(opener, **overrides)
    assert opener.calls == []


@pytest.mark.parametrize("status", [301, 302, 307, 401, 403, 500])
def test_http_errors_and_redirects_never_retry_or_expose_sensitive_body(status):
    error = HTTPError("https://example.invalid/", status, "synthetic-secret", {}, io.BytesIO(b"secret body"))
    opener = FakeOpener(error=error)
    with pytest.raises(ProviderQueryError) as captured:
        request(opener)
    assert f"HTTP {status}" in str(captured.value)
    assert "synthetic-secret" not in str(captured.value) and TEST_KEY not in str(captured.value)
    assert len(opener.calls) == 1


def test_default_redirect_handler_refuses_to_forward_the_request():
    assert _NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.example/") is None


def test_default_transport_does_not_follow_a_redirect_or_send_the_key_to_its_target(monkeypatch):
    # Two local-only mock endpoints exercise urllib's real redirect machinery.
    import app.providers.gfw_radd_research as client

    received = []

    class Target(BaseHTTPRequestHandler):
        def do_GET(self):
            received.append(self.headers.get("x-api-key"))
            self.send_response(200)
            self.end_headers()

        def do_POST(self):
            self.do_GET()

        def log_message(self, *_):
            pass

    target = ThreadingHTTPServer(("127.0.0.1", 0), Target)

    class Redirect(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{target.server_port}/")
            self.end_headers()

        def log_message(self, *_):
            pass

    source = ThreadingHTTPServer(("127.0.0.1", 0), Redirect)
    threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in (target, source)]
    for thread in threads:
        thread.start()
    monkeypatch.setattr(client, "_API_ORIGIN", f"http://127.0.0.1:{source.server_port}")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    try:
        with pytest.raises(ProviderQueryError, match="HTTP 302"):
            fetch_radd_research(source_version="v20261018", bounds=BOUNDS, api_key=TEST_KEY, prerequisites=PERMITTED)
        assert received == []
    finally:
        for server in (source, target):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)


def test_rate_limit_and_connection_failures_do_not_retry_or_leak_details():
    limited = FakeOpener(error=HTTPError("https://example.invalid/", 429, "secret", {}, io.BytesIO()))
    with pytest.raises(ProviderRateLimited):
        request(limited)
    assert len(limited.calls) == 1
    failed = FakeOpener(error=URLError("synthetic confidential detail"))
    with pytest.raises(ProviderQueryError) as captured:
        request(failed)
    assert "confidential" not in str(captured.value) and len(failed.calls) == 1


@pytest.mark.parametrize("response", [
    FakeResponse(b"{}", headers={"Content-Type": "text/html"}),
    FakeResponse(b"{}", headers={"Content-Type": "application/json", "Content-Encoding": "gzip"}),
    FakeResponse(b"{}", headers={"Content-Type": "application/json", "Content-Length": "invalid"}),
    FakeResponse(b"{}", headers={"Content-Type": "application/json", "Content-Length": "²"}),
    FakeResponse(b"{}", headers={"Content-Type": "application/json", "Content-Length": "9" * 5000}),
    FakeResponse(b"{}", headers={"Content-Type": "application/json", "Content-Length": "3"}),
    FakeResponse(b"x" * (MAX_ENVELOPE_BYTES + 1)),
    FakeResponse(b"{bad json}"),
    FakeResponse(b'{"status":"success","data":[],"status":"error"}'),
    FakeResponse(b'{"status":"error","data":[]}'),
])
def test_invalid_or_oversized_provider_responses_are_rejected(response):
    opener = FakeOpener(response)
    with pytest.raises(ProviderQueryError):
        request(opener)
    assert len(opener.calls) == 1 and response.closed


def test_row_limit_is_not_mistaken_for_a_complete_result():
    raw = json.dumps({"status": "success", "data": [ROW, ROW, ROW]}).encode()
    opener = FakeOpener(FakeResponse(raw))
    with pytest.raises(ResponseIncomplete):
        request(opener, max_rows=2)
    assert len(opener.calls) == 1


def test_empty_response_is_not_a_provider_health_or_coverage_claim():
    opener = FakeOpener(FakeResponse(b'{"status":"success","data":[]}'))
    result = request(opener)
    assert result.envelope.cells == ()
    assert not hasattr(result, "source_healthy") and not hasattr(result, "coverage_verified")
