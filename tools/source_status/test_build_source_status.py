import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from build_source_status import SOURCE_URL, project, render


NOW = datetime(2026, 11, 15, tzinfo=UTC)
REPORT = {
    "source": "UMD GLAD-L observation date",
    "bounds_wgs84": [36.60, -0.49, 36.63, -0.46],
    "source_generation": "123",
    "source_url": f"{SOURCE_URL}?generation=123",
    "source_last_modified": "Sat, 14 Nov 2026 19:05:36 GMT",
    "checked_at": "2026-11-14T20:13:13+00:00",
    "as_of": "2026-11-14",
    "latest_cloud_free_observation_day": "2026-11-03",
    "sampled_centres": 14_400,
    "masked_centres": 0,
    "no_clear_observation_this_year_centres": 7,
    "observed_this_year_centres": 14_393,
    "centres_observed_within_days": {"7": 0, "14": 2128, "30": 2495, "60": 8646},
}


class PublicationTest(unittest.TestCase):
    def test_report_displays_three_distinct_clocks_and_no_unapproved_fields(self):
        report = {**REPORT, "private_case": "must-never-render"}
        html = render(project(report, now=NOW))
        for value in ("03 Nov 2026", "22:05 EAT", "23:13 EAT", "14.8%", "0.0%"):
            self.assertIn(value, html)
        for value in ("must-never-render", "36.60", "-0.49", "?generation=123"):
            self.assertNotIn(value, html)

    def test_zero_observations_and_missing_report_have_distinct_states(self):
        report = {**REPORT, "latest_cloud_free_observation_day": None,
                  "observed_this_year_centres": 0, "no_clear_observation_this_year_centres": 14_400,
                  "centres_observed_within_days": {str(d): 0 for d in (7, 14, 30, 60)}}
        self.assertIn('class="date">Unknown', render(project(report, now=NOW)))
        self.assertIn("Source report unavailable", render(None))
        self.assertNotIn("0.0%", render(None))

    def test_rejects_misattributed_future_and_inconsistent_reports(self):
        for overrides in (
            {"bounds_wgs84": [36, -0.49, 36.63, -0.46]},
            {"source_url": "https://example.invalid"},
            {"checked_at": "2026-11-14T18:00:00+00:00"},
            {"checked_at": "2026-11-14T20:00:00"},
            {"checked_at": "2026-11-16T00:00:00+00:00"},
            {"latest_cloud_free_observation_day": "2026-11-15"},
            {"masked_centres": True},
            {"masked_centres": 1},
            {"centres_observed_within_days": {"7": 1, "14": 5, "30": 4, "60": 9}},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                project({**REPORT, **overrides}, now=NOW)

    def test_bad_input_keeps_existing_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report, output = root / "report.json", root / "status.html"
            bad = copy.deepcopy(REPORT)
            bad["sampled_centres"] = "private error content"
            report.write_text(json.dumps(bad), encoding="utf-8")
            output.write_text("previous page", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("build_source_status.py")),
                 "--report", str(report), "--output", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("private error content", result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "previous page")


if __name__ == "__main__":
    unittest.main()
