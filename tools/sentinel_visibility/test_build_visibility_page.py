import copy
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import TestCase

from tools.sentinel_visibility.build_visibility_page import CHECK_MAX_AGE, render
from tools.sentinel_visibility.project_visibility import project


CHECK = datetime(2026, 11, 15, 8, tzinfo=UTC)
ROOT = Path(__file__).resolve().parents[2]


def tile(grid, sampled, visible):
    counts = [0] * 12
    counts[4], counts[8] = visible, sampled - visible
    return {
        "tile": grid,
        "sampled_centres": sampled,
        "surface_classified_visible": visible,
        "vegetation_classified_visible": visible,
        "scl_counts_0_to_11": counts,
        "source_url": "https://example.invalid/private-receipt",
        "item_id": "<script>do-not-publish</script>",
        "etag": "private-source-tag",
    }


def report():
    return {
        "schema": "forestproof.sentinel2_visibility.v1",
        "area": "Provisional Geta research rectangle",
        "bounds_wgs84": [36.60, -0.49, 36.63, -0.46],
        "native_resolution_metres": 20,
        "checked_at": CHECK.isoformat(),
        "acquisitions": [
            {"date": "2026-11-08", "tiles": [tile("36MZE", 27722, 6424), tile("37MBV", 27724, 7675)]},
            {"date": "2026-11-10", "tiles": [tile("37MBV", 27724, 12), tile("36MZE", 27722, 0)]},
        ],
    }


class TestPublication(TestCase):
    def test_projection_sorts_rows_and_retains_only_allowlisted_data(self):
        snapshot = project(report(), now=CHECK)
        latest, earlier = snapshot["acquisitions"]
        self.assertGreater(latest["date"], earlier["date"])
        self.assertEqual(latest["tiles"], [
            {"grid": "T36MZE", "sampled": 27722, "visible": 0, "vegetation": 0},
            {"grid": "T37MBV", "sampled": 27724, "visible": 12, "vegetation": 12},
        ])
        self.assertEqual(set(snapshot), {"checked", "acquisitions"})

    def test_page_distinguishes_zero_small_nonzero_and_unavailable(self):
        page = render(project(report(), now=CHECK), now=CHECK)
        self.assertIn("0 of 27,722 visible", page)
        self.assertIn("12 of 27,724 visible", page)
        self.assertIn("&lt;0.1%", page)
        self.assertIn("Report verified", page)
        self.assertIn("Contains modified Copernicus Sentinel data [2026]", page)
        for text in ("example.invalid", "private-source-tag", "do-not-publish", "36.63", "-0.46"):
            self.assertNotIn(text, page)
        unavailable = render(None, now=CHECK)
        self.assertIn("Visibility report unavailable", unavailable)
        self.assertNotIn("0 of", unavailable)

    def test_overdue_report_keeps_same_scene_and_check_dates(self):
        snapshot = project(report(), now=CHECK)
        now = CHECK + CHECK_MAX_AGE
        page = render(snapshot, now=now)
        self.assertIn("Source check overdue", page)
        self.assertIn("Most recent verified report".lower(), page.lower())
        self.assertIn("10 Nov 2026", page)
        self.assertIn("15 Nov 2026, 11:00 EAT", page)
        self.assertIn("12 of 27,724 visible", page)

    def test_invalid_area_counts_tiles_and_dates_are_rejected(self):
        def bad_count(data):
            data["acquisitions"][0]["tiles"][0]["surface_classified_visible"] = True

        def duplicate_day(data):
            data["acquisitions"][0]["date"] = data["acquisitions"][1]["date"]

        def same_grid(data):
            data["acquisitions"][0]["tiles"][1] = copy.deepcopy(data["acquisitions"][0]["tiles"][0])

        changes = [
            lambda data: data.update(bounds_wgs84=[0, 0, 0.5, 0.5]),
            lambda data: data.update(checked_at=(CHECK + timedelta(seconds=1)).isoformat()),
            lambda data: data.update(checked_at="2026-11-15T08:00:00"),
            bad_count,
            duplicate_day,
            same_grid,
            lambda data: data["acquisitions"][0].update(date="2026-11-16"),
        ]
        for change in changes:
            with self.subTest(change=change):
                invalid = report()
                change(invalid)
                with self.assertRaises(ValueError):
                    project(invalid, now=CHECK)

    def test_invalid_replacement_preserves_last_output(self):
        with tempfile.TemporaryDirectory() as temp:
            report_path = Path(temp) / "input.json"
            page_path = Path(temp) / "page.html"
            report_path.write_text(json.dumps({"schema": "wrong source"}), encoding="utf-8")
            page_path.write_text("previous output", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "tools.sentinel_visibility.build_visibility_page",
                 "--report", str(report_path), "--output", str(page_path)],
                cwd=ROOT, capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(page_path.read_text(encoding="utf-8"), "previous output")
