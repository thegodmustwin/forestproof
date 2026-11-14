import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds, from_origin
from rasterio.warp import transform_bounds
from inspect_dist_layers import analyze

PREFIX = 'OPERA_L3_DIST-ALERT-HLS_T00AAA_20261103T074255Z_20261107T181429Z_L8_30_v1'
SUFFIX = {'status': 'VEG-DIST-STATUS', 'first_date': 'VEG-DIST-DATE',
          'last_date': 'VEG-LAST-DATE', 'mask': 'DATA-MASK'}
BOX = (0.10, 0.10, 0.13, 0.13)


class TestLayers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.paths = {key: Path(self.tmp.name) / f'{PREFIX}_{name}.tif' for key, name in SUFFIX.items()}
        self.values = {
            'status': np.array([[0,1,3],[255,7,8],[0,0,6]], dtype='uint8'),
            'first_date': np.array([[0,2100,2101],[-1,2102,2103],[0,0,2104]], dtype='int16'),
            'last_date': np.array([[2130,2130,2130],[-1,2130,2130],[2130,2130,2130]], dtype='int16'),
            'mask': np.array([[1,1,1],[0,1,1],[2,1,1]], dtype='uint8'),
        }
        self.write_all()

    def tearDown(self):
        self.tmp.cleanup()

    def write_all(self, mismatch=None):
        for name, array in self.values.items():
            transform = from_origin(0.10, 0.13, .01 if mismatch != name else .02, .01)
            with rasterio.open(self.paths[name], 'w', driver='GTiff', width=3, height=3,
                               count=1, dtype=array.dtype.name, crs='EPSG:4326', transform=transform,
                               nodata=(-1 if name in ('first_date','last_date') else 255)) as ds:
                ds.write(array, 1)

    def test_status_dates_missing_and_mask_count(self):
        result = analyze(self.paths, BOX)
        self.assertEqual(result['intersection_pixel_centres'], 9)
        self.assertEqual(result['layer_missing_counts']['status'], 1)
        self.assertEqual(result['land_water_processing_mask_counts'], {'0':1,'1':7,'2':1})
        self.assertEqual(result['disturbance_status_first_detection_span']['pixels_with_date'], 5)
        self.assertEqual(result['positive_status_with_no_initial_date_count'], 0)
        self.assertEqual(result['first_detection_span_by_status']['1']['pixels_with_date'], 1)
        self.assertEqual(result['status_by_scene_mask_for_status_and_mask_present']['1']['7'], 1)

    def test_optional_layers_and_pairwise_denominators(self):
        self.values['first_date'][0,1] = -1
        self.write_all()
        result = analyze(self.paths, BOX)
        self.assertEqual(result['all_supplied_layers_present_count'], 7)
        self.assertEqual(result['status_and_mask_present_count'], 8)
        self.assertEqual(result['status_by_scene_mask_for_status_and_mask_present']['1']['1'], 1)
        self.assertIsNone(result['first_detection_span_by_status']['1'])
        first_only = analyze({'status': self.paths['status'], 'first_date': self.paths['first_date']}, BOX)
        self.assertEqual(first_only['status_and_first_date_present_count'], 7)
        self.assertNotIn('land_water_processing_mask_counts', first_only)

    def test_mismatched_grid_rejected(self):
        self.write_all(mismatch='mask')
        with self.assertRaisesRegex(ValueError, 'grids'):
            analyze(self.paths, BOX)

    def test_matching_fmask_keeps_fill_separate_from_overlapping_quality_flags(self):
        fmask = Path(self.tmp.name) / 'HLS.L30.T00AAA.2026307T074255.v2.0.Fmask.tif'
        qa = np.array([[0, 2, 10], [255, 4, 32], [192, 16, 128]], dtype='uint8')
        with rasterio.open(fmask, 'w', driver='GTiff', width=3, height=3, count=1,
                           dtype='uint8', crs='EPSG:4326', transform=from_origin(0.10, 0.13, .01, .01),
                           nodata=255) as dataset:
            dataset.write(qa, 1)
        result = analyze({**self.paths, 'fmask': fmask}, BOX)['hls_fmask']
        self.assertEqual(result['present_count'], 8)
        self.assertEqual(result['flag_counts_nonexclusive']['cloud'], 2)
        self.assertEqual(result['flag_counts_nonexclusive']['cloud_shadow'], 1)
        self.assertEqual(result['aerosol_level_counts'], {'0': 6, '2': 1, '3': 1})
        self.assertEqual(result['passes_conservative_hls_screen_count'], 2)
        self.assertEqual(result['screen_pass_by_dist_mask_code'], {'1': 2})

    def test_rejects_fmask_from_another_acquisition(self):
        fmask = Path(self.tmp.name) / 'HLS.L30.T00AAA.2026306T074255.v2.0.Fmask.tif'
        fmask.touch()
        with self.assertRaisesRegex(ValueError, 'Fmask filename'):
            analyze({**self.paths, 'fmask': fmask}, BOX)

    def test_unknown_status_and_future_dates_rejected(self):
        self.values['status'][0,0] = 42
        self.write_all()
        with self.assertRaisesRegex(ValueError, 'Unexpected status'):
            analyze(self.paths, BOX)
        self.values['status'][0,0] = 0
        self.values['last_date'][0,0] = 3000
        self.write_all()
        with self.assertRaisesRegex(ValueError, 'Date value'):
            analyze(self.paths, BOX)

    def test_projected_utm_grids_use_wgs84_research_bounds(self):
        utm_bounds = transform_bounds('EPSG:4326', 'EPSG:32631', *BOX, densify_pts=21)
        transform = from_bounds(*utm_bounds, 3, 3)
        status = np.ones((3, 3), dtype='uint8')
        dates = np.full((3, 3), 2100, dtype='int16')
        for name, array, nodata in (('status', status, 255), ('first_date', dates, -1)):
            with rasterio.open(self.paths[name], 'w', driver='GTiff', width=3, height=3,
                               count=1, dtype=array.dtype.name, crs='EPSG:32631',
                               transform=transform, nodata=nodata) as dataset:
                dataset.write(array, 1)
        result = analyze({'status': self.paths['status'], 'first_date': self.paths['first_date']}, BOX)
        self.assertGreater(result['intersection_pixel_centres'], 0)
        self.assertEqual(result['status_counts_all']['1'], result['intersection_pixel_centres'])
        self.assertEqual(result['disturbance_status_first_detection_span']['pixels_with_date'],
                         result['intersection_pixel_centres'])

    def test_invalid_bounds_rejected(self):
        for bounds in ((0, 0, 2, 2), (1, 0, 0, 1), (0, 0, float("nan"), 1)):
            with self.assertRaises(ValueError):
                analyze(self.paths, bounds)

    def test_disjoint_rectangle_rejected(self):
        with self.assertRaisesRegex(ValueError, 'intersect'):
            analyze(self.paths, (30,0,31,1))


if __name__ == '__main__':
    unittest.main()

