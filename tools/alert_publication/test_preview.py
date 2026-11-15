from datetime import UTC, datetime, timedelta
from http.client import HTTPConnection
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from unittest import TestCase

from tools.alert_publication.preview import AlertPreviewServer, project, render, response


NOW = datetime(2026, 11, 15, 10, tzinfo=UTC)


def fixtures():
    policy = {
        "schema": "forestproof.alert-publication-policy.v1",
        "provider": "glad_l", "area_id": "test-scope", "area_label": "Synthetic test area",
        "coverage_reference": "test native qualification", "area_approval_reference": "test scope decision",
        "access_reference": "test access and costs", "reuse_reference": "test intended use",
        "approved_records": [{
            "record_id": "private-fixture-1", "observed_on": "2026-11-02",
            "reviewed_on": "2026-11-15", "review_reference": "private-test-decision",
            "release": "test-20261114", "receipt_sha256": "c" * 64,
            "reviewer": "hidden example person",
        }],
    }
    report = {
        "schema": "forestproof.alert-publication-report.v1",
        "provider": "glad_l", "area_id": "test-scope",
        "release": "test-20261114", "release_date": "2026-11-14",
        "checked_at": NOW.isoformat(), "attempted_at": NOW.isoformat(),
        "check_failed": False,
        "records": [
            {"record_id": "private-fixture-1", "observed_on": "2026-11-02", "receipt": "secret-receipt",
             "receipt_sha256": "c" * 64,
             "coordinates": [112.9846, 44.3331]},
            {"record_id": "private-fixture-2", "observed_on": "2026-11-09", "note": "secret draft"},
        ],
    }
    return policy, report


class TestAlertPublication(TestCase):
    def test_missing_policy_never_falls_back_to_candidate_records(self):
        self.assertEqual(response(None, None, now=NOW)[0], 503)
        self.assertIn(b"Alerts unavailable", response(None, None, now=NOW)[1])

    def test_exact_approval_and_separate_dates(self):
        policy, candidate = fixtures()
        page = render(project(policy, candidate, now=NOW), now=NOW)
        for label in ("Source release", "Last verified check",
                      "14 Nov 2026", "02 Nov 2026", "Approved for publication"):
            self.assertIn(label, page)
        for field in ("private-fixture", "private-test-decision", "hidden example person",
                      "secret-receipt", "09 Nov 2026", "112.9846", "secret draft", "c" * 64):
            self.assertNotIn(field, page)
        candidate["records"][0]["observed_on"] = "2026-11-01"
        result = project(policy, candidate, now=NOW)
        self.assertFalse(result["approved"])
        self.assertIn("No approved alerts in this report", render(result, now=NOW))

    def test_changed_scope_duplicate_ids_and_missing_rights_fail(self):
        policy, report = fixtures()
        wrong_scope = {**report, "area_id": "another-scope"}
        with self.assertRaises(ValueError):
            project(policy, wrong_scope, now=NOW)
        with self.assertRaises(ValueError):
            project(policy, {**report, "records": [report["records"][0]] * 2}, now=NOW)
        with self.assertRaises(ValueError):
            project({**policy, "reuse_reference": ""}, report, now=NOW)
        with self.assertRaises(ValueError):
            project(policy, {**report, "checked_at": (NOW - timedelta(minutes=1)).isoformat()}, now=NOW)

    def test_new_release_or_record_revision_requires_its_own_approval(self):
        policy, candidate = fixtures()
        self.assertFalse(project(policy, {**candidate, "release": "test-20261115"}, now=NOW)["approved"])
        candidate["records"][0]["receipt_sha256"] = "d" * 64
        self.assertFalse(project(policy, candidate, now=NOW)["approved"])

    def test_failed_and_overdue_checks_keep_approved_rows(self):
        policy, report = fixtures()
        report["check_failed"] = True
        report["checked_at"] = (NOW - timedelta(hours=1)).isoformat()
        snapshot = project(policy, report, now=NOW)
        failure = render(snapshot, now=NOW)
        overdue = render(snapshot, now=NOW + timedelta(hours=36))
        self.assertIn("Latest source check failed", failure)
        self.assertIn("Last attempted check", failure)
        self.assertIn("Source check overdue", overdue)
        for html in (failure, overdue):
            self.assertIn("02 Nov 2026", html)

    def test_loopback_serves_only_read_projection(self):
        with TemporaryDirectory() as tmp:
            policy, report = fixtures()
            paths = [Path(tmp) / filename for filename in ("policy.json", "report.json")]
            for path, data in zip(paths, (policy, report), strict=True):
                path.write_text(json.dumps(data), encoding="utf-8")
            with AlertPreviewServer(*paths, 0) as server:
                thread = Thread(target=server.serve_forever, daemon=True)
                thread.start()

                def request(method, path):
                    client = HTTPConnection("127.0.0.1", server.server_port, timeout=45)
                    try:
                        client.request(method, path)
                        result = client.getresponse()
                        return result.status, result.read(), result.getheader("Cache-Control")
                    finally:
                        client.close()

                try:
                    code, first, cache = request("GET", "/alerts")
                    self.assertEqual((code, cache), (200, "no-store"))
                    self.assertIn(b"Synthetic test area", first)
                    self.assertEqual(request("HEAD", "/alerts"), (200, b"", "no-store"))
                    self.assertEqual(request("GET", "/alerts")[1], first)
                    self.assertEqual(request("GET", "/api/forestproof/cases")[0], 404)
                    self.assertEqual(request("GET", "/report.json")[0], 404)
                    self.assertEqual(request("GET", "/policy.json")[0], 404)
                    self.assertEqual(request("POST", "/alerts")[0], 405)
                    paths[0].unlink()
                    self.assertEqual(request("GET", "/alerts")[0], 503)
                finally:
                    server.shutdown()
                    thread.join()
