"""Stage a read-only public-alert projection without opening a public route."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from string import Template

from tools.source_status.build_source_status import day_label, read_date, read_report, time_label, utc_time, write_page


TEMPLATE = Path(__file__).with_name("alert_preview.html")
PUBLIC_PATH = "/alerts"
CHECK_MAX_AGE = timedelta(hours=36)
INPUT_ERRORS = (OSError, TypeError, ValueError, KeyError, OverflowError, RecursionError)
PROVIDERS = {
    "radd": ("Wageningen University · RADD forest disturbance alerts",
             "https://www.wur.nl/en/research/products-services/radd-forest-disturbance-alert"),
    "glad_l": ("University of Maryland GLAD · Landsat forest alerts · Hansen et al. (2016)",
               "https://glad.umd.edu/dataset/glad-forest-alerts"),
    "opera_dist_hls": ("NASA OPERA · DIST-ALERT-HLS V1",
                       "https://doi.org/10.5067/SNWG/OPERA_L3_DIST-ALERT-HLS_V1.001"),
}


def text_value(value, maximum=120):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or not value.isprintable():
        raise ValueError("Expected a bounded text value")
    return value


def index_records(rows):
    if not isinstance(rows, list):
        raise ValueError("Expected a record list")
    indexed = {}
    for row in rows:
        record_id = text_value(row["record_id"])
        if record_id in indexed:
            raise ValueError("Duplicate alert identity")
        indexed[record_id] = row
    return indexed


def project(policy, report, *, now):
    if not isinstance(policy, dict) or policy.get("schema") != "forestproof.alert-publication-policy.v1":
        raise ValueError("Missing publication policy")
    provider = policy["provider"]
    if provider not in PROVIDERS:
        raise ValueError("Unrecognized alert source")
    area = text_value(policy["area_id"])
    label = text_value(policy["area_label"], 100)
    for field in ("coverage_reference", "access_reference", "reuse_reference", "area_approval_reference"):
        text_value(policy[field], 240)
    if (not isinstance(report, dict) or report.get("schema") != "forestproof.alert-publication-report.v1"
            or report.get("provider") != provider or report.get("area_id") != area):
        raise ValueError("The report does not match the approved source and area")
    release = report["release"]
    if not isinstance(release, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}", release):
        raise ValueError("Invalid release identifier")
    released = read_date(report["release_date"])
    checked = utc_time(datetime.fromisoformat(report["checked_at"]))
    attempted = utc_time(datetime.fromisoformat(report["attempted_at"]))
    failed = report["check_failed"]
    if (type(failed) is not bool or not released <= checked.date() or not checked <= attempted <= now
            or failed != (attempted > checked)):
        raise ValueError("Inconsistent release and check times")

    records = index_records(report["records"])
    approvals = index_records(policy["approved_records"])
    approved = []
    for identifier, approval in approvals.items():
        text_value(approval["review_reference"], 240)
        receipt = approval["receipt_sha256"]
        if not isinstance(receipt, str) or not re.fullmatch(r"[0-9a-f]{64}", receipt):
            raise ValueError("Expected an approved receipt digest")
        if (identifier not in records or approval["release"] != release
                or records[identifier].get("receipt_sha256") != receipt):
            continue
        day = read_date(records[identifier]["observed_on"])
        if day != read_date(approval["observed_on"]):
            continue
        reviewed = read_date(approval["reviewed_on"])
        if not day <= released or not day <= reviewed <= now.date():
            raise ValueError("Inconsistent observation and review dates")
        approved.append((day, reviewed))
    return {
        "area_label": label, "provider": provider, "release": release,
        "released": released, "checked": checked, "attempted": attempted,
        "failed": failed, "approved": sorted(approved, reverse=True),
    }


def render(snapshot, *, now):
    layout = Template(TEMPLATE.read_text(encoding="utf-8"))
    if snapshot is None:
        return layout.substitute(
            scope="ForestProof alert publication",
            status="Alerts unavailable",
            detail="Source qualification and publication approval are pending.",
            content="",
            attribution="",
        )
    if now - snapshot["checked"] >= CHECK_MAX_AGE:
        status = "Source check overdue"
        detail = "Showing the last approved report. The latest check also failed." if snapshot["failed"] else "Showing the last approved report."
    elif snapshot["failed"]:
        status = "Latest source check failed"
        detail = "Showing the last approved report."
    elif not snapshot["approved"]:
        status = "No approved alerts in this report"
        detail = "Only observations cleared for publication appear here."
    else:
        status = "Approved alerts"
        detail = "Each observation shown here has a recorded publication review."

    release = escape(snapshot["release"])
    latest_attempt = (
        f'<div><dt>Last attempted check</dt><dd>{time_label(snapshot["attempted"])}</dd></div>'
        if snapshot["failed"] else ""
    )
    facts = (
        '<dl class="dates">'
        f'<div><dt>Source release</dt><dd>{release} · {day_label(snapshot["released"])}</dd></div>'
        f'<div><dt>Last verified check</dt><dd>{time_label(snapshot["checked"])}</dd></div>'
        f"{latest_attempt}</dl>"
    )
    if snapshot["approved"]:
        rows = "".join(
            f"<li>{day_label(day)}<p>Approved for publication {day_label(reviewed)}</p></li>"
            for day, reviewed in snapshot["approved"]
        )
        facts += '<h2>Observation dates</h2><ol class="alerts" role="list">' + rows + "</ol>"
    credit, source = PROVIDERS[snapshot["provider"]]
    return layout.substitute(
        scope=escape(snapshot["area_label"]),
        status=escape(status),
        detail=escape(detail),
        content=facts,
        attribution=f'<a href="{source}" rel="noreferrer">{escape(credit)}</a>',
    )


def response(policy_path, report_path, *, now):
    snapshot = None
    if policy_path and report_path:
        try:
            snapshot = project(read_report(policy_path), read_report(report_path), now=now)
        except INPUT_ERRORS:
            pass
    return (200 if snapshot else 503), render(snapshot, now=now).encode("utf-8")


class AlertPreviewServer(ThreadingHTTPServer):
    def __init__(self, policy_path, report_path, port):
        super().__init__(("127.0.0.1", port), AlertPreviewHandler)
        self.policy_path = policy_path
        self.report_path = report_path
        self.host = f"127.0.0.1:{self.server_port}"


class AlertPreviewHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.headers.get("Host") != self.server.host:
            self.send_error(400)
            return
        if self.path != PUBLIC_PATH:
            self.send_error(404)
            return
        status, body = response(self.server.policy_path, self.server.report_path, now=datetime.now(UTC))
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        if self.command == "GET":
            self.wfile.write(body)

    def do_POST(self):
        self.send_response(405)
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Content-Length", "0")
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--report", type=Path)
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--output", type=Path)
    output.add_argument("--port", type=int)
    args = parser.parse_args()

    if args.output:
        if args.output.suffix.lower() != ".html" or any(
            source and source.resolve() == args.output.resolve() for source in (args.policy, args.report)
        ):
            parser.error("Choose a distinct HTML output")
        _, body = response(args.policy, args.report, now=datetime.now(UTC))
        write_page(args.output, body.decode("utf-8"))
    else:
        if not 1024 <= args.port <= 65535:
            parser.error("Choose an unprivileged loopback port")
        with AlertPreviewServer(args.policy, args.report, args.port) as server:
            print(f"Local alert preview at http://{server.host}{PUBLIC_PATH}", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
