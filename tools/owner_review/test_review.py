import base64
from datetime import datetime, timedelta, timezone
from http.client import HTTPConnection
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from threading import Thread
from unittest import TestCase
from urllib.parse import urlencode

from tools.owner_review import store, web


FAKE_OWNER = "Rehearsal operator"
TEST_PASSWORD = "test-only-password"
EAT = timezone(timedelta(hours=3))


def fixture(directory: Path):
    directory.mkdir()
    (directory / "source").mkdir()
    archive_case = {
        "case_id": store.CASE_ID, "mode": "PRIVATE_HISTORICAL_RESEARCH",
        "state": "PENDING_OWNER_REVIEW", "observation": "observation.json",
        "review": {"owner_decision": None}, "test_fixture": True,
    }
    objects = []
    for index in range(10):
        name = f"fixture-{index}.tif"
        data = f"synthetic archive asset {index}".encode()
        (directory / "source" / name).write_bytes(data)
        objects.append({"name": name, "bytes": len(data), "sha256": store.digest(data)})
    observation = {
        "acquisition": "2026-11-03T07:42:55Z", "first_detection_day": "2026-11-03",
        "last_assessed_day": "2026-11-03", "source_objects": objects,
        "primary_sample": {"band_values": {"status": 1, "mask": 1}},
        "neighbor_sample": {"band_values": {"status": 1}}, "same_pass_agreement_count": 1,
        "source_products": [{"doi": doi} for doi in sorted(store.DOIS)],
    }
    (directory / "case.json").write_text(json.dumps(archive_case), encoding="utf-8")
    (directory / "observation.json").write_text(json.dumps(observation, indent=2), encoding="utf-8")
    (directory / "DOSSIER.md").write_text("Synthetic rehearsal dossier", encoding="utf-8")
    for name in ("reproduce.py", "inspect_dist_layers.py", "raster-requirements.txt"):
        (directory / name).write_text("synthetic fixture", encoding="utf-8")
    lines = [
        f"{store.digest(path.read_bytes())}  {path.relative_to(directory).as_posix()}"
        for path in sorted(directory.rglob("*")) if path.is_file()
    ]
    (directory / "CHECKSUMS.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestOwnerReview(TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.private_dir = Path(temporary.name)
        self.archive = self.private_dir / "archive"
        self.database = self.private_dir / "owner-review.sqlite3"
        fixture(self.archive)

    def start(self):
        store.initialize(self.database, self.archive, FAKE_OWNER)
        store.set_password(self.database, TEST_PASSWORD)
        server = web.ReviewServer(self.database, 0)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        self.addCleanup(server.server_close)
        self.addCleanup(worker.join)
        self.addCleanup(server.shutdown)
        self.server = server

    def request(self, method, path, *, password=TEST_PASSWORD, extra=None, body=None):
        headers = extra.copy() if extra else {}
        if password is not None:
            encoded = base64.b64encode(f"owner:{password}".encode()).decode("ascii")
            headers["Authorization"] = f"Basic {encoded}"
        link = HTTPConnection("127.0.0.1", self.server.server_port, timeout=45)
        try:
            link.request(method, path, body=body, headers=headers)
            result = link.getresponse()
            return result.status, result.read(), dict(result.getheaders())
        finally:
            link.close()

    def test_owner_auth_review_receipt_and_restore(self):
        self.start()
        for path in ("/", "/receipt", "/dossier"):
            status, anonymous, _ = self.request("GET", path, password=None)
            self.assertEqual(status, 401)
            self.assertNotIn(store.CASE_ID.encode(), anonymous)
        self.assertEqual(self.request("GET", "/", password="wrong-password")[0], 401)
        self.assertEqual(self.request("GET", "/", extra={"Host": "example.invalid"})[0], 400)
        self.assertEqual(self.request("GET", "/archive/source/fixture-0.tif")[0], 404)
        status, page, page_headers = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertEqual(page_headers["Referrer-Policy"], "same-origin")
        self.assertIn(b"Owner review pending", page)
        match = re.search(rb'<input\b(?=[^>]*\bname="csrf")[^>]*\bvalue="([^"]+)"', page)
        self.assertIsNotNone(match)
        receipt = (self.archive / "observation.json").read_bytes()
        status, body, headers = self.request("GET", "/receipt")
        self.assertEqual((status, body), (200, receipt))
        self.assertIn("attachment", headers["Content-Disposition"])

        form = {
            "csrf": match[1].decode(), "disposition": "keep_open",
            "follow_up": (datetime.now(EAT).date() + timedelta(days=2)).isoformat(),
            "note": "Synthetic rehearsal review. Follow up on the next quality-assessed pass.",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Origin": self.server.origin}
        self.assertEqual(self.request("POST", "/review", extra={**headers, "Origin": "http://invalid.local"},
                                      body=urlencode(form))[0], 403)
        bad = {**form, "csrf": form["csrf"][:-1]}
        self.assertEqual(self.request("POST", "/review", extra=headers, body=urlencode(bad))[0], 400)
        bad = {**form, "follow_up": ""}
        status, error, _ = self.request("POST", "/review", extra=headers, body=urlencode(bad))
        self.assertEqual(status, 400)
        self.assertIn(b"Synthetic rehearsal review", error)
        self.assertIn(b"Set a follow-up date", error)
        self.assertEqual(store.snapshot(self.database)["reviews"], [])

        for _ in range(2):
            status, _, response = self.request("POST", "/review", extra=headers, body=urlencode(form))
            self.assertEqual((status, response["Location"]), (303, "/?saved=1"))
        conflict = {**form, "note": "Conflicting note."}
        self.assertEqual(self.request("POST", "/review", extra=headers, body=urlencode(conflict))[0], 400)
        dossier = json.loads(self.request("GET", "/dossier")[1])
        self.assertEqual(len(dossier["reviews"]), 1)
        entry = dossier["reviews"][0]
        self.assertEqual(entry["owner_name"], FAKE_OWNER)
        self.assertEqual(entry["receipt_sha256"], store.digest(receipt))
        self.assertEqual(entry["follow_up"], form["follow_up"])
        self.assertEqual(dossier["archived_case"]["review"]["owner_decision"], None)

        backup = self.private_dir / "backup.sqlite3"
        restored = self.private_dir / "restored.sqlite3"
        store.copy_review(self.database, backup)
        self.archive.rename(self.private_dir / "archive-offline")
        store.copy_review(backup, restored)
        self.assertEqual(store.snapshot(restored), dossier)
        self.assertEqual(store.original_receipt(restored), receipt)
        self.assertTrue(store.authenticate(restored, TEST_PASSWORD))

    def test_bad_source_blocks_import_without_replacing_existing_file(self):
        path = self.archive / "source" / "fixture-0.tif"
        path.write_bytes(b"x" * path.stat().st_size)
        with self.assertRaisesRegex(store.ReviewError, "checksum"):
            store.initialize(self.database, self.archive, FAKE_OWNER)
        self.assertFalse(self.database.exists())
