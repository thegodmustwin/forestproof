from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from stage_source_status import page_for, read_state, refresh
from test_build_source_status import REPORT


NOW = datetime(2026, 11, 14, 20, 13, 13, tzinfo=UTC)


class TestStagedStatus(TestCase):
    def test_refresh_replay_failure_and_staleness(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            self.assertIn("Source report unavailable", page_for(read_state(path, NOW), now=NOW))
            self.assertEqual(refresh(path, clock=lambda: NOW, fetch=lambda _, __: REPORT), "updated")
            initial = read_state(path, NOW)
            self.assertIn("Snapshot updated", page_for(initial, now=NOW))
            stale_time = NOW + timedelta(hours=37)
            stale = page_for(initial, now=stale_time)
            self.assertIn("Source check overdue", stale)
            self.assertIn("03 Nov 2026", stale)
            self.assertIn("14.8%", stale)

            next_check = NOW + timedelta(hours=1)
            self.assertEqual(refresh(path, clock=lambda: next_check, fetch=lambda _, __: None), "unchanged")
            same_generation = read_state(path, next_check)
            self.assertEqual(initial["report"], same_generation["report"])
            self.assertIn("No newer file", page_for(same_generation, now=next_check))

            def network_failure(_, __):
                raise TimeoutError("private exception")

            self.assertEqual(refresh(path, clock=lambda: next_check, fetch=network_failure), "failed")
            failed = read_state(path, next_check)
            page = page_for(failed, now=next_check)
            self.assertIn("Latest source check failed", page)
            self.assertIn("03 Nov 2026", page)
            self.assertNotIn("private exception", page)
            self.assertEqual(initial["report"], failed["report"])

    def test_invalid_new_report_preserves_last_good_generation(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            self.assertEqual(refresh(path, clock=lambda: NOW, fetch=lambda _, __: REPORT), "updated")
            self.assertEqual(refresh(path, clock=lambda: NOW, fetch=lambda _, __: {**REPORT, "source_url": "invalid"}), "failed")
            self.assertEqual(read_state(path, NOW)["report"], REPORT)
