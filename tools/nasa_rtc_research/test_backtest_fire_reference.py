import unittest

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from backtest_fire_reference import aligned_reference_window, counts, interior


class FireReferenceTest(unittest.TestCase):
    def test_unclassified_values_stay_out_of_the_control(self):
        transform = from_origin(400000, 3790000, 30, 30)
        source_values = np.zeros((5, 5), dtype="uint8")
        source_values[2, 2] = 1
        source_values[3, 3] = 4
        options = dict(driver="GTiff", height=5, width=5, count=1, dtype="uint8", transform=transform)
        with MemoryFile() as reference_file, MemoryFile() as radar_file:
            with reference_file.open(crs="EPSG:26911", **options) as reference:
                reference.write(source_values, 1)
            with radar_file.open(crs="EPSG:32611", nodata=255, **options) as radar:
                radar.write(np.zeros_like(source_values), 1)
            with reference_file.open() as reference, radar_file.open() as radar:
                labels, _ = aligned_reference_window(reference, radar)
        self.assertEqual(int((labels == 1).sum()), 1)
        self.assertEqual(int((labels == 4).sum()), 1)

    def test_missing_radar_is_separate_from_unflagged(self):
        status = np.array([[0, 1, 4, 255]], dtype="uint8")
        result = counts(np.ones(status.shape, dtype=bool), status)
        self.assertEqual(result["reference_centres"], 4)
        self.assertEqual(result["radar_assessed"], 3)
        self.assertEqual(result["no_flag"], 1)
        self.assertEqual(result["radar_unavailable"], 1)
        self.assertEqual(result["any_flag_pct_of_assessed"], 66.6667)

    def test_interior_uses_the_entire_neighbourhood(self):
        group = np.ones((5, 5), dtype=bool)
        self.assertEqual(int(interior(group, 2).sum()), 1)
        group[0, 0] = False
        self.assertEqual(int(interior(group, 2).sum()), 0)


if __name__ == "__main__":
    unittest.main()
