from datetime import UTC, date, datetime, timedelta
import unittest

from tools.sentinel_visibility.build_discovery_page import render_discovery


class PublicDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 20, 10, tzinfo=UTC)
        self.snapshot = {
            'checked': self.now,
            'private_receipt': 'SENTINEL_SECRET_MUST_NOT_APPEAR',
            'acquisitions': [
                {'date': date(2026, 11, d), 'tiles': [
                    {'grid': grid, 'sampled': 100, 'visible': visible, 'vegetation': visible}
                    for grid, visible in [('T36MZE', 23), ('T37MBV', 3)]
                ]} for d in (13, 10, 8)
            ],
        }

    def test_public_projection_and_exact_destinations(self):
        page = render_discovery(self.snapshot, now=self.now)
        self.assertEqual(page.count('data-kind="observation"'), 6)
        self.assertIn('/atlas/geta?grid=T36MZE&amp;date=2026-11-08', page)
        self.assertIn('/atlas/geta?grid=T37MBV&amp;date=2026-11-13', page)
        self.assertIn('23 of 100 sampled centres visible (23.0%)', page)
        self.assertNotIn('SENTINEL_SECRET_MUST_NOT_APPEAR', page)
        self.assertIn('not a forest-loss alert', page)

    def test_stale_failure_and_missing_states(self):
        self.assertIn('Source check overdue', render_discovery(self.snapshot, now=self.now + timedelta(days=2)))
        self.assertIn('Latest source check failed', render_discovery(self.snapshot, now=self.now, failed_at=self.now))
        page = render_discovery(None, now=self.now)
        self.assertIn('Observation report unavailable', page)
        self.assertNotIn('data-kind="observation"', page)
        self.assertIn('data-kind="place"', page)

    def test_imagery_context_is_strictly_matched(self):
        page = render_discovery(self.snapshot, now=self.now)
        self.assertEqual(page.count('Published image context available.'), 2)
        self.assertEqual(page.count('Matching image context unavailable.'), 4)


if __name__ == '__main__':
    unittest.main()
