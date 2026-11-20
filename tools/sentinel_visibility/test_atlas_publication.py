from datetime import UTC, datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
from unittest import TestCase

from tools.sentinel_visibility.build_atlas_page import render_atlas
from tools.sentinel_visibility.project_visibility import BOUNDS, project
from tools.sentinel_visibility.preview_fixture import fixture

ASSETS=Path(__file__).with_name("assets")


class TestGeographicPublication(TestCase):
    def test_geography_preserves_canonical_extent_and_image_identity(self):
        geo=json.loads((ASSETS/"geta-geography.json").read_text(encoding="utf-8"))
        image=json.loads((ASSETS/"geta-context.json").read_text(encoding="utf-8"))
        receipt=json.loads((ASSETS/"geography-provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(geo["research_bounds"],BOUNDS)
        self.assertEqual(geo["image_corners"],receipt["image_georeferencing"]["image_corners"])
        self.assertEqual(geo["image_dates"],[item["date"] for item in image["items"]])
        self.assertEqual(geo["image_grid"],"T36MZE")
        self.assertEqual(len(geo["image_corners"]),4)
        for longitude,latitude in geo["image_corners"]:
            self.assertLess(abs(longitude-36.615),.016)
            self.assertLess(abs(latitude+.475),.016)

    def test_published_elevation_and_runtime_bytes_match_receipts(self):
        receipt=json.loads((ASSETS/"geography-provenance.json").read_text(encoding="utf-8"))
        tiles=[item for item in receipt["sources"] if item.get("local_asset")]
        self.assertEqual(len(tiles),4)
        for tile in tiles:
            relative=tile["local_asset"].removeprefix("/assets/")
            data=(ASSETS/relative).read_bytes()
            self.assertEqual(sha256(data).hexdigest(),tile["sha256"])
            self.assertEqual(len(data),tile["bytes"])
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertIn("srtm/",tile["contributing_sources"])
        relief=receipt["terrain"]["relief"]
        self.assertEqual(sha256((ASSETS/relief["file"]).read_bytes()).hexdigest(),relief["sha256"])
        runtime=json.loads((ASSETS/"atlas-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime["maplibre_version"],"6.16.0")
        for item in runtime["runtime_assets"]:
            self.assertEqual(sha256((ASSETS/item["file"]).read_bytes()).hexdigest(),item["sha256"])
        self.assertLess(sum(p.stat().st_size for p in ASSETS.rglob("*") if p.is_file()),5_000_000)

    def test_atlas_keeps_dated_evidence_when_rendering_is_unavailable(self):
        now=datetime.now(UTC)
        data=fixture()["report"]
        now=datetime.fromisoformat(data["checked_at"])+timedelta(seconds=1)
        # A raw private receipt must never enter the public geographic projection.
        data["private_evidence_path"]="DO-NOT-PUBLISH-PRIVATE-RECEIPT"
        page=render_atlas(project(data,now=now),now=now)
        self.assertIn("6,424",page)
        self.assertIn("6,346",page)
        self.assertIn("13 Nov 2026",page)
        self.assertIn('src="/assets/atlas.js"',page)
        self.assertIn('type="module"',page)
        self.assertNotIn("DO-NOT-PUBLISH",page)
        missing=render_atlas(None,now=now)
        self.assertIn("Observation report unavailable",missing)
        self.assertNotIn("6,424",missing)
        stale=render_atlas(project(data,now=now),now=now+timedelta(hours=37))
        self.assertIn("Source check overdue",stale)
