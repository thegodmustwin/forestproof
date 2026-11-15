"""Refresh and serve the independent Geta visibility page."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from http.client import HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tools.sentinel_visibility.build_visibility_page import render
from tools.sentinel_visibility.project_visibility import project
from tools.source_status.build_source_status import read_report, write_page


PUBLIC_PATH = "/visibility"
ERRORS = (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError, AttributeError, HTTPException)


def read_state(path, now):
    state = read_report(path)
    if not isinstance(state, dict) or set(state) != {"attempted_at", "failed", "report"}:
        raise ValueError("Unexpected visibility state")
    attempted = datetime.fromisoformat(state["attempted_at"])
    failed = state["failed"]
    if attempted.utcoffset() != timedelta(0) or attempted > now or type(failed) is not bool:
        raise ValueError("Inconsistent check state")
    report = state["report"]
    snapshot = project(report, now=now) if report is not None else None
    if (snapshot and snapshot["checked"] > attempted) or (snapshot is None and not failed):
        raise ValueError("Inconsistent report state")
    return state, snapshot


def fetch(previous, now):
    # Raster packages are used only by the one-shot refresh.
    from tools.sentinel_visibility.inspect_visibility import inspect_recent
    return inspect_recent(previous, now)


def refresh(path, *, clock=lambda: datetime.now(UTC), inspect=fetch):
    try:
        state, _ = read_state(path, clock())
        previous = state["report"]
    except ERRORS:
        previous = None
    try:
        from rasterio.errors import RasterioError
    except ImportError:
        RasterioError = OSError
    start = clock()
    report = previous
    try:
        candidate = inspect(previous, start)
        finished = clock()
        snapshot = project(candidate, now=finished)
        if snapshot["checked"] < start:
            raise ValueError("Candidate report predates this check")
        report, failed = candidate, False
    except (*ERRORS, RasterioError, ImportError):
        finished = clock()
        failed = True
    write_page(path, json.dumps({"attempted_at": finished.isoformat(), "failed": failed, "report": report}))
    return failed


def response_for(path, *, now):
    try:
        state, snapshot = read_state(path, now)
    except ERRORS:
        state, snapshot = None, None
    failed_at = datetime.fromisoformat(state["attempted_at"]) if state and state["failed"] else None
    body = render(snapshot, now=now, public=True, failed_at=failed_at)
    return (200 if snapshot else 503), body.encode("utf-8")


def serve(path, port, hostname):
    allowed_hosts = {hostname, f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self._page()

        def do_HEAD(self):
            self._page()

        def _page(self):
            if self.headers.get("Host") not in allowed_hosts:
                self.send_error(400)
                return
            if self.path.partition("?")[0] != PUBLIC_PATH:
                self.send_error(404)
                return
            try:
                status, body = response_for(path, now=datetime.now(UTC))
            except ERRORS:
                self.send_error(503)
                return
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.end_headers()
            if self.command == "GET":
                self.wfile.write(body)

        def log_request(self, code="-", size="-"):
            pass

    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("refresh")
    listener = commands.add_parser("serve")
    listener.add_argument("--port", required=True, type=int)
    listener.add_argument("--hostname", required=True)
    args = parser.parse_args()

    try:
        if args.command == "refresh":
            failed = refresh(args.state)
            print("Visibility refresh failed. Last valid data retained." if failed else "Visibility report verified.")
            return int(failed)
        if not 1024 <= args.port <= 65535:
            parser.error("Choose an unprivileged listener port")
        serve(args.state, args.port, args.hostname)
    except ERRORS:
        parser.exit(1, "Visibility service failed. Check its state path or listener.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
