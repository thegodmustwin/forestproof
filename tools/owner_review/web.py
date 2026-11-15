"""Serve the archived owner review over local loopback."""

from __future__ import annotations

import base64
import binascii
from datetime import UTC, datetime, timedelta, timezone
import hashlib
import hmac
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import sqlite3
from string import Template
from time import time
from urllib.parse import parse_qs
import webbrowser

from tools.owner_review import store


PAGE = Path(__file__).with_name("review_page.html")
EAT = timezone(timedelta(hours=3))
PORT = 18451
FORM_LIMIT = 32 * 1024
CSRF_AGE = 7200
ROUTES = {"/", "/?saved=1", "/receipt", "/dossier"}
STORAGE_ERRORS = (OSError, sqlite3.Error, store.ReviewError)


def history_html(reviews: list[dict]) -> str:
    if not reviews:
        return "<p>No owner decision has been recorded yet.</p>"
    rows = []
    for entry in reversed(reviews):
        status = store.DISPOSITIONS[entry["disposition"]]
        happened = datetime.fromisoformat(entry["recorded_at"]).astimezone(EAT).strftime("%d %b %Y, %H:%M EAT")
        note = escape(entry["note"]).replace("\n", "<br>")
        follow_up = escape(entry["follow_up"] or "Unscheduled")
        rows.append(
            f"<li><strong>{status}</strong><p>{escape(entry['owner_name'])} · {happened}</p>"
            f"<p>{note}</p><p>Follow-up {follow_up}</p></li>"
        )
    return "<ol>" + "".join(rows) + "</ol>"


def render(snapshot: dict, csrf: str, *, notice: str = "", error: bool = False, values: dict | None = None) -> bytes:
    values = values or {}
    reviews = snapshot["reviews"]
    status = store.DISPOSITIONS[reviews[-1]["disposition"]] if reviews else "Owner review pending"
    feedback = ""
    if notice:
        role = "alert" if error else "status"
        feedback = f'<p class="feedback" role="{role}">{escape(notice)}</p>'
    selected = values.get("disposition")
    return Template(PAGE.read_text(encoding="utf-8")).substitute(
        case_id=escape(snapshot["case_id"]),
        source_name=escape(snapshot["source_name"]),
        observation_date=escape(snapshot["observation_date"]),
        observation_summary=escape(snapshot["observation_summary"]),
        owner_name=escape(snapshot["owner_name"]),
        status=escape(status),
        feedback=feedback,
        review_history=history_html(reviews),
        csrf=escape(csrf),
        minimum_date=datetime.now(EAT).date().isoformat(),
        keep_checked="checked" if selected == "keep_open" else "",
        close_checked="checked" if selected == "close_unconfirmed" else "",
        follow_up_value=escape(values.get("follow_up", "")),
        note_value=escape(values.get("note", "")),
    ).encode("utf-8")


class ReviewServer(ThreadingHTTPServer):
    def __init__(self, database: Path, port: int):
        super().__init__(("127.0.0.1", port), ReviewHandler)
        self.database = database
        self.host_header = f"127.0.0.1:{self.server_port}"
        self.origin = f"http://{self.host_header}"
        self.csrf_key = secrets.token_bytes(32)

    def sign(self, message: str) -> str:
        return hmac.new(self.csrf_key, message.encode("ascii"), hashlib.sha256).hexdigest()

    def new_csrf(self) -> str:
        message = f"{int(time()):x}.{secrets.token_hex(16)}"
        return f"{message}.{self.sign(message)}"

    def validate_csrf(self, token: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{1,12}\.[0-9a-f]{32}\.[0-9a-f]{64}", token):
            raise store.ReviewError("Reload the review page before submitting.")
        message, signature = token.rsplit(".", 1)
        timestamp, nonce = message.split(".")
        if not 0 <= time() - int(timestamp, 16) <= CSRF_AGE or not hmac.compare_digest(signature, self.sign(message)):
            raise store.ReviewError("Reload the review page before submitting.")
        return nonce


class ReviewHandler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(30)

    def log_message(self, format, *args):
        pass

    def respond(self, status, body=b"", *, content_type="text/plain; charset=utf-8", headers=()):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        # Retain Origin on the local form POST without sending a referrer off site.
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; form-action 'self'; base-uri 'none'")
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        try:
            if not self.allowed(ROUTES):
                return
            database = self.server.database
            if self.path == "/receipt":
                self.download(store.original_receipt(database), "observation-receipt.json")
            elif self.path == "/dossier":
                dossier = json.dumps(store.snapshot(database), sort_keys=True, indent=2).encode("utf-8")
                self.download(dossier, "owner-dossier.json")
            else:
                notice = "Owner review saved." if self.path == "/?saved=1" else ""
                self.page(200, notice=notice)
        except STORAGE_ERRORS:
            self.respond(503, b"The private review is unavailable.")

    def download(self, body, filename):
        self.respond(200, body, content_type="application/json", headers=(
            ("Content-Disposition", f'attachment; filename="{filename}"'),
        ))

    def allowed(self, paths):
        if self.headers.get("Host") != self.server.host_header:
            self.respond(400)
            return False
        if self.path not in paths:
            self.respond(404)
            return False
        scheme, _, encoded = self.headers.get("Authorization", "").partition(" ")
        if scheme.lower() == "basic" and len(encoded) <= 1800:
            try:
                user, colon, password = base64.b64decode(encoded, validate=True).decode("utf-8").partition(":")
            except (UnicodeError, binascii.Error):
                user, colon, password = "", "", ""
            if user == "owner" and colon and store.authenticate(self.server.database, password):
                return True
        self.respond(401, b"Sign in to view this private owner review.", headers=(
            ("WWW-Authenticate", 'Basic realm="ForestProof owner review", charset="UTF-8"'),
        ))
        return False

    def form(self):
        size = self.headers.get("Content-Length", "")
        if (self.headers.get("Transfer-Encoding") or not re.fullmatch(r"[0-9]{1,8}", size)
                or not 0 < int(size) <= FORM_LIMIT):
            raise store.ReviewError("The review submission is incomplete or too large.")
        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            raise store.ReviewError("Submit through the owner review form.")
        data = self.rfile.read(int(size))
        if len(data) != int(size):
            raise store.ReviewError("The review submission was interrupted.")
        parsed = parse_qs(data.decode("utf-8"), keep_blank_values=True, strict_parsing=True,
                          errors="strict", max_num_fields=4)
        if set(parsed) != {"csrf", "disposition", "follow_up", "note"} or any(len(v) != 1 for v in parsed.values()):
            raise store.ReviewError("Choose a disposition and complete the review form.")
        return {key: value[0] for key, value in parsed.items()}

    def page(self, status, *, notice="", values=None):
        snapshot = store.snapshot(self.server.database)
        if notice == "Owner review saved." and not snapshot["reviews"]:
            notice = ""
        body = render(snapshot, self.server.new_csrf(), notice=notice, error=status >= 400, values=values)
        self.respond(status, body, content_type="text/html; charset=utf-8")

    def do_POST(self):
        try:
            if not self.allowed({"/review"}):
                return
            if self.headers.get("Origin") != self.server.origin:
                self.respond(403)
                return
            values = {}
            try:
                values = self.form()
                submission = self.server.validate_csrf(values["csrf"])
                store.record_review(self.server.database, submission, values["disposition"],
                                    values["follow_up"], values["note"], now=datetime.now(UTC))
            except store.ReviewError as error:
                self.page(400, notice=str(error), values=values)
                return
            except (UnicodeError, ValueError):
                self.page(400, notice="The form could not be read. Reload and try again.")
                return
            self.respond(303, headers=(("Location", "/?saved=1"),))
        except STORAGE_ERRORS:
            self.respond(503, b"The review could not be saved.")


def run(database: Path, port: int = PORT, *, open_browser: bool = False):
    if not store.has_password(database):
        raise store.ReviewError("Set the local owner password before opening the review.")
    with ReviewServer(database, port) as server:
        print(f"Private owner review at {server.origin}", flush=True)
        if open_browser:
            webbrowser.open(server.origin)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
