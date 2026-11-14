from datetime import date
from io import BytesIO
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.coords import BoundingBox
from rasterio.transform import from_origin
from rasterio.windows import Window

from inspect_glad_observation_dates import ObservationDateTile, TILE, select_window, summarize_dates


class Response(BytesIO):
    def __init__(self, payload, status, headers):
        super().__init__(payload)
        self.status = status
        self.headers = headers


class TestPinnedRanges(unittest.TestCase):
    def _opener(self, *, payload=b"abcdefghijkl", range_status=206, wrong_generation=False):
        open_requests = []

        def open_request(request, *, timeout):
            open_requests.append((request.get_method(), request.get_header("Range")))
            self.assertIn("?generation=123", request.full_url)
            headers = {"x-goog-generation": "123", "ETag": '"fixed"', "Last-Modified": "Fri, 13 Nov 2026 14:23:06 GMT"}
            if request.get_method() == "HEAD":
                return Response(b"", 200, {**headers, "Content-Length": str(len(payload))})
            start, end = map(int, request.get_header("Range").removeprefix("bytes=").split("-"))
            if wrong_generation:
                headers["x-goog-generation"] = "124"
            return Response(payload[start:end + 1], range_status, {**headers, "Content-Range": f"bytes {start}-{end}/{len(payload)}"})

        return SimpleNamespace(open=open_request), open_requests

    @patch("inspect_glad_observation_dates.BLOCK_SIZE", 4)
    def test_reads_pinned_blocks_and_reuses_them(self):
        opener, requests = self._opener()
        remote = ObservationDateTile("123", opener=opener)
        with remote.open(TILE) as tile:
            self.assertEqual(tile.read(3), b"abc")
            self.assertEqual(tile.read(3), b"def")
            tile.seek(0)
            self.assertEqual(tile.read(6), b"abcdef")
            self.assertEqual(remote.transfer_bytes, 8)
        self.assertEqual(requests, [("HEAD", None), ("GET", "bytes=0-3"), ("GET", "bytes=4-7")])

    @patch("inspect_glad_observation_dates.BLOCK_SIZE", 4)
    @patch("inspect_glad_observation_dates.TRANSFER_LIMIT", 7)
    def test_enforces_transfer_ceiling_before_later_block(self):
        opener, requests = self._opener()
        remote = ObservationDateTile("123", opener=opener)
        with remote.open(TILE) as tile:
            self.assertEqual(tile.read(4), b"abcd")
            with self.assertRaisesRegex(ValueError, "transfer budget"):
                tile.read(1)
        self.assertEqual(len(requests), 2)

    def test_fails_when_server_ignores_range_or_changes_generation(self):
        for kwargs in ({"range_status": 200}, {"wrong_generation": True}):
            with self.subTest(kwargs=kwargs):
                opener, _ = self._opener(**kwargs)
                remote = ObservationDateTile("123", opener=opener)
                with remote.open(TILE) as tile:
                    with self.assertRaisesRegex(ValueError, "pinned byte range"):
                        tile.read(1)

    def test_rasterio_can_stat_and_read_via_separate_handles(self):
        pixels = np.array([[307, 306], [0, 291]], dtype="uint16")
        with MemoryFile() as memory:
            with memory.open(driver="GTiff", height=2, width=2, count=1, dtype="uint16",
                             crs="EPSG:4326", transform=from_origin(30, 0, 0.00025, 0.00025)) as output:
                output.write(pixels, 1)
            opener, requests = self._opener(payload=memory.read())
        remote = ObservationDateTile("123", opener=opener)
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
            with rasterio.open(TILE, opener=remote.open) as dataset:
                np.testing.assert_array_equal(dataset.read(1), pixels)
        self.assertIsNone(remote.read_error)
        self.assertEqual([method for method, _ in requests], ["HEAD", "GET"])


class TestDateRecency(unittest.TestCase):
    def test_counts_age_bins_and_separates_zero_from_masked(self):
        data = np.ma.array([0, 300, 306, 307, 312, 318, 65535], mask=[0, 0, 0, 0, 0, 0, 1], dtype="uint16")
        result = summarize_dates(data, as_of=date(2026, 11, 14))
        self.assertEqual(result["sampled_centres"], 7)
        self.assertEqual(result["no_clear_observation_this_year_centres"], 1)
        self.assertEqual(result["masked_centres"], 1)
        self.assertEqual(result["observed_this_year_centres"], 5)
        self.assertEqual(result["latest_cloud_free_observation_day"], "2026-11-14")
        self.assertEqual(result["centres_observed_within_days"], {"7": 2, "14": 4, "30": 5, "60": 5})

    def test_future_date_fails_and_all_zeros_stay_unknown(self):
        as_of = date(2026, 11, 14)
        with self.assertRaisesRegex(ValueError, "later than"):
            summarize_dates(np.ma.array([319], dtype="uint16"), as_of=as_of)
        result = summarize_dates(np.ma.array([0, 0], dtype="uint16"), as_of=as_of)
        self.assertIsNone(result["latest_cloud_free_observation_day"])

    def test_native_window_limits_bounds(self):
        dataset = SimpleNamespace(bounds=BoundingBox(30, -10, 40, 0), transform=from_origin(30, 0, 0.00025, 0.00025))
        self.assertEqual(select_window(dataset, (36.60, -0.49, 36.63, -0.46)), Window(26400, 1840, 120, 120))
        with self.assertRaisesRegex(ValueError, "0.05 degrees"):
            select_window(dataset, (36.60, -0.49, 36.66, -0.46))


if __name__ == "__main__":
    unittest.main()