"""Refresh and serve the standalone GLAD-L observation-status staging page."""

from __future__ import annotations

import argparse
import http.client
import json
import re
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import HTTPRedirectHandler, Request, build_opener

from build_source_status import BOUNDS, SOURCE_URL, project, read_report, render, time_label, utc_time, write_page

CHECK_MAX_AGE = timedelta(hours=36)
STATE_ERRORS = (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_report(previous, now):
    """HEAD detects new objects; only a new generation needs a raster window read."""
    with build_opener(NoRedirect()).open(Request(SOURCE_URL, method="HEAD"), timeout=12) as response:
        generation = response.headers.get("x-goog-generation", "")
        if response.status != 200 or not re.fullmatch(r"[0-9]{1,20}", generation):
            raise ValueError("Source object identity is unavailable")
        etag = response.headers.get("ETag")
        modified = response.headers.get("Last-Modified")
        if not etag or not modified:
            raise ValueError("Source object identity is incomplete")
    if previous and previous["source_generation"] == generation:
        if etag != previous.get("source_etag") or modified != previous["source_last_modified"]:
            raise ValueError("Source object identity changed without a new generation")
        return None

    # Raster dependencies are required by the refresh worker only.
    from inspect_glad_observation_dates import inspect
    return inspect(generation, tuple(BOUNDS), now.date())


def read_state(path, now):
    try:
        state = read_report(path)
    except FileNotFoundError:
        return None
    if not isinstance(state, dict) or set(state) != {"result", "attempted_at", "report"}:
        raise ValueError("Unexpected source status state")
    result = state["result"]
    if result not in ("updated", "unchanged", "failed"):
        raise ValueError("Unexpected refresh result")
    attempted = utc_time(datetime.fromisoformat(state["attempted_at"]))
    if attempted > now or (state["report"] is None and result != "failed"):
        raise ValueError("Inconsistent refresh state")
    if state["report"] is not None:
        snapshot = project(state["report"], now=now)
        if snapshot["checked"] > attempted:
            raise ValueError("Snapshot is newer than its refresh")
    return state


def refresh(path, *, clock=lambda: datetime.now(UTC), fetch=fetch_report):
    previous = read_state(path, clock())
    report = previous["report"] if previous else None
    started = clock()
    try:
        updated = fetch(report, started)
        finished = clock()
        if updated is not None:
            next_snapshot = project(updated, now=finished)
            if next_snapshot["checked"] < started:
                raise ValueError("New raster report predates its refresh")
            if report is not None:
                current = project(report, now=finished)
                if (next_snapshot["modified"] < current["modified"]
                        or int(updated["source_generation"]) <= int(report["source_generation"])):
                    raise ValueError("The source generation did not advance")
            report = updated
            result = "updated"
        elif report is not None:
            result = "unchanged"
        else:
            raise ValueError("No initial observation report")
    except (*STATE_ERRORS, http.client.HTTPException, ImportError):
        finished = clock()
        result = "failed"
    write_page(path, json.dumps({"result": result, "attempted_at": finished.isoformat(), "report": report}))
    return result


def page_for(state, *, now, max_age=CHECK_MAX_AGE):
    if not state or state["report"] is None:
        return render(None)
    snapshot = project(state["report"], now=now)
    attempted = utc_time(datetime.fromisoformat(state["attempted_at"]))
    if state["result"] == "failed":
        notice = "Latest source check failed. Showing the last verified snapshot."
    elif now - attempted >= max_age:
        notice = "Source check overdue. Showing the last verified snapshot."
    elif state["result"] == "unchanged":
        notice = "Source checked. No newer file was available."
    else:
        notice = "Source checked. Snapshot updated."
    banner = f'<p class="check-status"><strong>{notice}</strong> Last attempt {time_label(attempted)}.</p>'
    return render(snapshot, status=banner)


def serve(path, port, max_age):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self._page()

        def do_HEAD(self):
            self._page()

        def do_POST(self):
            self.send_response(405)
            self.send_header("Allow", "GET, HEAD")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _page(self):
            if self.headers.get("Host") not in (f"127.0.0.1:{port}", f"localhost:{port}"):
                self.send_error(400)
                return
            if self.path != "/":
                self.send_error(404)
                return
            now = datetime.now(UTC)
            try:
                body = page_for(read_state(path, now), now=now, max_age=max_age)
            except STATE_ERRORS:
                body = render(None)
            content = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            if self.command == "GET":
                self.wfile.write(content)

    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("refresh")
    serving = commands.add_parser("serve")
    serving.add_argument("--port", required=True, type=int)
    serving.add_argument("--max-check-age-seconds", type=int, default=int(CHECK_MAX_AGE.total_seconds()))
    args = parser.parse_args()
    try:
        if args.command == "refresh":
            result = refresh(args.state)
            print(result)
            return 1 if result == "failed" else 0
        if not 1024 <= args.port <= 65535 or args.max_check_age_seconds <= 0:
            parser.error("Supply a nonprivileged port and a positive check age")
        serve(args.state, args.port, timedelta(seconds=args.max_check_age_seconds))
    except STATE_ERRORS:
        parser.exit(1, "Source status could not run. Check state file or listener settings.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
