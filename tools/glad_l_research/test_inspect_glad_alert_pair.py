from datetime import date
from unittest import TestCase

import numpy as np
from rasterio.transform import from_origin
from rasterio.windows import Window

from inspect_glad_alert_pair import candidate_receipt, summarize_alerts


class TestArchivePair(TestCase):
    def test_counts_only_published_codes_and_preserves_mask(self):
        status = np.ma.array([2, 3, 0, 0], mask=[False, False, False, True])
        detection = np.ma.array([307, 311, 0, 0], mask=[False, False, True, True])
        result = summarize_alerts(status, detection, release=date(2026, 11, 14))
        self.assertEqual(result["probable_centres"], 1)
        self.assertEqual(result["confirmed_centres"], 1)
        self.assertEqual(result["masked_status_centres"], 1)
        self.assertEqual(result["latest_first_detection"], "2026-11-07")

    def test_flagged_cell_requires_plausible_date(self):
        with self.assertRaisesRegex(ValueError, "detection"):
            summarize_alerts(np.ma.array([3]), np.ma.array([0]), release=date(2026, 11, 14))

    def test_private_receipt_selects_latest_confirmed_cell(self):
        report = {
            "source": "synthetic source", "scope": "synthetic scope", "release_folder_day": "2026-11-14",
            "checked_at": "2026-11-15T10:00:00+00:00", "assets": {},
        }
        receipt = candidate_receipt(
            report, from_origin(50, 10, 0.00025, 0.00025), Window(10, 20, 2, 2),
            np.ma.array([[2, 3], [3, 0]]), np.ma.array([[315, 311], [302, 0]]),
            np.ma.array([[310, 316], [311, 0]]),
        )
        self.assertEqual(receipt["provider_status_code"], 3)
        self.assertEqual(receipt["first_detection_day"], "2026-11-07")
        self.assertEqual(receipt["native_grid"], {"crs": "EPSG:4326", "row": 20, "column": 11})
