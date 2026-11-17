from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from inspect_visibility import inspect_pairs, recent_pairs
from test_build_visibility_page import report
from tools.sentinel_visibility.visibility_service import read_state, refresh, response_for


NOW = datetime(2026, 11, 15, 9, tzinfo=UTC)


class TestVisibilityService(TestCase):
    def test_welcome_links_to_report_when_source_is_unavailable(self):
        with TemporaryDirectory() as tmp:
            state = Path(tmp) / "source.json"
            status, page = response_for(state, now=NOW, route="/welcome")
            self.assertEqual(status, 200)
            self.assertIn(b"Report unavailable", page)
            self.assertIn(b'href="/visibility"', page)
            self.assertNotIn(b"Latest sampled pass", page)
            candidate = report()
            candidate["checked_at"] = NOW.isoformat()
            self.assertFalse(refresh(state, clock=lambda: NOW, inspect=lambda *_: candidate))
            later = NOW + timedelta(hours=36)
            _, page = response_for(state, now=later, route="/welcome")
            self.assertIn(b"Latest sampled pass", page)
            self.assertIn(b"Source check overdue.", page)

    def test_refresh_retains_report_during_failure_and_expiry(self):
        def check(prior, started):
            self.assertIsNone(prior)
            candidate = report()
            candidate["checked_at"] = started.isoformat()
            return candidate

        def provider_timeout(prior, started):
            self.assertEqual(prior["checked_at"], NOW.isoformat())
            raise TimeoutError

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.json"
            code, missing = response_for(path, now=NOW)
            self.assertEqual(code, 503)
            self.assertIn(b"Visibility report unavailable", missing)
            self.assertFalse(refresh(path, clock=lambda: NOW, inspect=check))
            verified = read_state(path, NOW)[0]["report"]
            later = NOW + timedelta(hours=2)
            self.assertTrue(refresh(path, clock=lambda: later, inspect=provider_timeout))
            self.assertEqual(read_state(path, later)[0]["report"], verified)
            status, failed = response_for(path, now=later)
            self.assertEqual(status, 200)
            self.assertIn(b"Latest source check failed", failed)
            self.assertIn(b"12 of 27,724 visible", failed)
            self.assertNotIn(b"noindex", failed)
            self.assertNotIn(b"private-tag", failed)
            self.assertIn(b"Source check overdue", response_for(path, now=NOW + timedelta(hours=36))[1])

    def test_success_becomes_overdue_without_a_new_worker_run(self):
        def check(prior, started):
            candidate = report()
            candidate["checked_at"] = started.isoformat()
            return candidate

        with TemporaryDirectory() as tmp:
            state = Path(tmp) / "source.json"
            refresh(state, clock=lambda: NOW, inspect=check)
            self.assertIn(b"Report verified", response_for(state, now=NOW)[1])
            self.assertIn(b"Source check overdue", response_for(state, now=NOW + timedelta(hours=36))[1])

    def test_recent_catalog_rejects_incomplete_newer_pair(self):
        def item(day, tile):
            sensing = day.strftime("%Y%m%d")
            item_id = f"S2B_{tile}_{sensing}_0_L2A"
            return {
                "id": item_id, "collection": "sentinel-2-l2a",
                "properties": {"grid:code": f"MGRS-{tile}", "datetime": f"{day}T07:41:21Z",
                               "s2:datatake_id": f"GS2B_{sensing}T074121_010000_N05.13"},
                "assets": {"scl": {"href": (
                    "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/"
                    f"{tile[:2]}/{tile[2]}/{tile[3:]}/{day:%Y/%m}/{item_id}/SCL.tif"
                )}},
            }

        days = [date(2026, 11, day) for day in (3, 8, 10, 13)]
        complete = [item(day, grid) for day in days for grid in ("36MZE", "37MBV")]
        with patch("inspect_visibility.catalog_items", return_value=complete):
            self.assertEqual([day for day, _ in recent_pairs(None, NOW)], days[-1:-4:-1])
        with patch("inspect_visibility.catalog_items", return_value=complete[:-1]):
            with self.assertRaisesRegex(ValueError, "both catalog tile records"):
                recent_pairs(None, NOW)

    def test_unchanged_asset_retains_measurement_after_head_check(self):
        day = date(2026, 11, 10)
        old = report()
        prior = old["acquisitions"][-1]["tiles"][0]
        prior["source_url"] = "https://example.invalid/single-scl"
        identity = {"etag": '"etag"', "source_modified": "unchanged", "bytes": 100}
        prior.update(identity, sha256="a" * 64, measured_at=NOW.isoformat())
        tile = {"tile": prior["tile"], "source_url": prior["source_url"]}
        checked = NOW + timedelta(hours=12)
        with patch("inspect_visibility.asset_identity", return_value=identity) as head, \
                patch("inspect_visibility.read_pinned_asset") as get:
            candidate = inspect_pairs([(day, [tile])], None, previous=old, clock=lambda: checked)
        head.assert_called_once()
        get.assert_not_called()
        self.assertEqual(tile["measured_at"], NOW.isoformat())
        self.assertEqual(candidate["checked_at"], checked.isoformat())
