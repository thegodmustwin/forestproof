from datetime import date
from io import BytesIO
from unittest import TestCase

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from rasterio.warp import transform

from inspect_visibility import classify, measure, read_pinned_asset, scene_pair


class Response(BytesIO):
    def __init__(self, status, headers, data=b""):
        super().__init__(data)
        self.status = status
        self.headers = headers


class OfflineProvider:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        return next(self.responses)


class TestVisibility(TestCase):
    def test_visibility_preserves_cloud_and_zero_denominators(self):
        result = classify(np.array([0, 1, 4, 5, 6, 7, 8, 9, 10, 11], dtype="uint8"))
        self.assertEqual(result["sampled_centres"], 10)
        self.assertEqual(result["surface_classified_visible"], 3)
        self.assertEqual(result["vegetation_classified_visible"], 1)
        self.assertEqual(classify(np.array([0, 9], dtype="uint8"))["surface_classified_visible"], 0)
        with self.assertRaisesRegex(ValueError, "unknown SCL code"):
            classify(np.array([12], dtype="uint8"))

    def test_measure_on_preserved_grid(self):
        (x,), (y,) = transform("EPSG:4326", "EPSG:32736", [36.615], [-0.475])
        with MemoryFile() as memory:
            with memory.open(
                driver="GTiff", count=1, width=3, height=2, dtype="uint8",
                crs="EPSG:32736", transform=from_origin(x - 30, y + 20, 20, 20),
            ) as raster:
                raster.write(np.array([[4, 5, 6], [9, 0, 3]], dtype="uint8"), 1)
            data = memory.read()
        result = measure(data, 32736)
        self.assertEqual(result["sampled_centres"], 6)
        self.assertEqual(result["surface_classified_visible"], 3)
        with self.assertRaisesRegex(ValueError, "native"):
            measure(data, 32737)

    def test_range_is_required_to_match_identity_and_size(self):
        url = "https://example.invalid/fixture.tif"
        etag = '"' + "a" * 32 + '"'
        headers = {
            "Content-Length": "3", "ETag": etag,
            "Last-Modified": "Tue, 10 Nov 2026 12:00:00 GMT",
        }
        provider = OfflineProvider(
            Response(200, headers),
            Response(206, {"Content-Range": "bytes 0-2/3", "ETag": etag}, b"abc"),
        )
        contents, receipt = read_pinned_asset(provider, url)
        self.assertEqual(contents, b"abc")
        self.assertEqual(receipt["bytes"], 3)
        self.assertEqual(provider.requests[1].get_header("If-match"), etag)
        self.assertEqual(provider.requests[1].get_header("Range"), "bytes=0-2")

        for range_header, response_etag, data in (
            ("bytes 0-1/3", etag, b"abc"),
            ("bytes 0-2/3", '"' + "b" * 32 + '"', b"abc"),
            ("bytes 0-2/3", etag, b"ab"),
        ):
            with self.subTest(range_header=range_header, response_etag=response_etag, data=data):
                provider = OfflineProvider(
                    Response(200, headers),
                    Response(206, {"Content-Range": range_header, "ETag": response_etag}, data),
                )
                with self.assertRaises(ValueError):
                    read_pinned_asset(provider, url)

    def test_missing_catalog_pair_is_not_zero_visibility(self):
        provider = OfflineProvider(Response(200, {}, b'{"features":[],"links":[]}'))
        with self.assertRaisesRegex(ValueError, "does not have both catalog tile records"):
            scene_pair(provider, date(2026, 11, 10))
