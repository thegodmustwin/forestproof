from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class GfwGladS2Overlay:
    """Public real-data visual context, intentionally not a case-ingestion source.

    Source: Global Forest Watch Tile Cache API. Dynamic alert PNG tiles lack the
    record-level metadata needed to create defensible individual observations.
    """

    source_id: str = "gfw-glad-s2-overlay"
    version: str = "latest"
    base_url: str = "https://tiles.globalforestwatch.org/umd_glad_sentinel2_alerts"

    @property
    def tile_template(self) -> str:
        return f"{self.base_url}/{self.version}/dynamic/{{z}}/{{x}}/{{y}}.png"

    def tile_url(self, start_date: str | None = None, end_date: str | None = None, confirmed_only: bool = False) -> str:
        query = []
        if start_date:
            query.append(f"start_date={start_date}")
        if end_date:
            query.append(f"end_date={end_date}")
        if confirmed_only:
            query.append("confirmed_only=true")
        return self.tile_template + ("?" + "&".join(query) if query else "")

    def discover(self, area: dict[str, Any], time_range: tuple[datetime, datetime]) -> list[dict[str, Any]]:
        return [{
            "kind": "RASTER_CONTEXT_LAYER",
            "source_id": self.source_id,
            "tile_template": self.tile_url(time_range[0].date().isoformat(), time_range[1].date().isoformat()),
            "notice": "Use for visual review only; do not construct individual observation records from tile pixels.",
        }]

    def fetch(self, cursor: str) -> dict[str, Any]:
        raise NotImplementedError("Tile images are displayed by MapLibre; the worker does not infer alerts from pixels.")

    def normalize(self, record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Raster context is not a record-level environmental observation.")

    def provenance(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "source": "Global Forest Watch Tile Cache API",
            "accessed_at": datetime.now(UTC).isoformat(),
            "mode": "LIVE_CONTEXT_ONLY",
            "limitations": "No per-alert source record is retained from a rendered tile.",
        }
