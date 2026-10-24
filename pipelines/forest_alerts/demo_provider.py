from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


class DeterministicDemoProvider:
    """A repeatable fixture provider. Its data must never be mixed with live records."""

    source_id = "demo-synthetic-v1"
    processing_version = "demo-provider/1.0.0"

    def __init__(self, fixture_path: Path | None = None):
        self.fixture_path = fixture_path

    def discover(self, area: dict[str, Any], time_range: tuple[datetime, datetime]) -> list[dict[str, Any]]:
        # The canonical fixtures are seeded in the API; this method documents the
        # pipeline contract and allows worker tests to inject local fixture content.
        return [{"cursor": "demo://fixtures/aberdare-001", "mode": "DEMO"}]

    def fetch(self, cursor: str) -> dict[str, Any]:
        if not cursor.startswith("demo://"):
            raise ValueError("Demo provider only accepts demo cursors")
        return {"cursor": cursor, "mode": "DEMO", "source_record_id": "DEMO-ABERDARE-001"}

    def normalize(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_record_id": record["source_record_id"],
            "processing_version": self.processing_version,
            "quality_flags": ["DEMO_DATA", "NOT_A_LIVE_DETECTION"],
        }

    def provenance(self, record: dict[str, Any]) -> dict[str, Any]:
        return {"mode": "DEMO", "raw_evidence_ref": record["cursor"], "provider_version": self.processing_version}
