from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from app.providers.raster_identity import raster_cell_identity


def test_raster_cell_identity_is_stable_across_coordinate_formatting_and_release():
    first = raster_cell_identity(
        source_product="wur_radd_alerts",
        longitude=36.1234561,
        latitude=-0.1234561,
        observed_at="2026-10-18",
    )
    same_cell_in_next_release = raster_cell_identity(
        source_product="wur_radd_alerts",
        longitude="36.1234564",
        latitude="-0.1234564",
        observed_at=date(2026, 10, 18),
    )

    assert first == same_cell_in_next_release
    assert first.startswith("forestproof:raster-cell:v1:")


def test_raster_cell_identity_separates_products_cells_and_source_dates():
    common = {
        "source_product": "wur_radd_alerts",
        "longitude": 36.123456,
        "latitude": -0.123456,
        "observed_at": "2026-10-18",
    }
    base = raster_cell_identity(**common)
    assert raster_cell_identity(**{**common, "source_product": "umd_glad_landsat_alerts"}) != base
    assert raster_cell_identity(**{**common, "longitude": 36.123466}) != base
    assert raster_cell_identity(**{**common, "observed_at": "2026-10-19"}) != base


def test_raster_cell_identity_normalizes_aware_datetimes_to_utc():
    utc = raster_cell_identity(
        source_product="wur_radd_alerts",
        longitude=36.1,
        latitude=-0.1,
        observed_at=datetime(2026, 10, 18, 8, 0, tzinfo=timezone.utc),
    )
    offset = raster_cell_identity(
        source_product="wur_radd_alerts",
        longitude=36.1,
        latitude=-0.1,
        observed_at="2026-10-18T11:00:00+03:00",
    )
    assert utc == offset


@pytest.mark.parametrize(
    "overrides",
    [
        {"source_product": " "},
        {"longitude": 181},
        {"latitude": float("nan")},
        {"longitude": True},
        {"observed_at": "2026-10-18T08:00:00"},
        {"observed_at": "2026-02-30"},
    ],
)
def test_raster_cell_identity_rejects_invalid_source_identity(overrides):
    values = {
        "source_product": "wur_radd_alerts",
        "longitude": 36.1,
        "latitude": -0.1,
        "observed_at": "2026-10-18",
    }
    with pytest.raises(ValueError):
        raster_cell_identity(**{**values, **overrides})
