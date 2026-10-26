from datetime import date

import pytest

from app.providers.gfw_radd import normalize_radd_pixel_row


def sample_radd_pixel_row():
    # Synthetic field-shaped input; not a real GFW record.
    return {
        "longitude": 36.61,
        "latitude": -0.48,
        "area__ha": 0.01,
        "wur_radd_alerts__date": "2026-10-18",
        "wur_radd_alerts__date_conf": "synthetic-date-confidence",
        "wur_radd_alerts__confidence": "synthetic-confidence",
    }


def test_normalize_radd_cell_preserves_source_fields_and_derived_identity():
    row = sample_radd_pixel_row()

    result = normalize_radd_pixel_row(row, source_version="v20261018")

    assert result.source_product == "wur_radd_alerts"
    assert result.source_version == "v20261018"
    assert result.observed_on == date(2026, 10, 18)
    assert result.confidence_value == "synthetic-confidence"
    assert result.date_confidence_value == "synthetic-date-confidence"
    assert result.raw_fields == row
    assert result.forestproof_id.startswith("forestproof:raster-cell:v1:")
    assert "provider" not in result.forestproof_id


def test_source_release_is_separate_from_stable_cell_date_identity():
    row = sample_radd_pixel_row()

    first = normalize_radd_pixel_row(row, source_version="v20261018")
    updated_release = normalize_radd_pixel_row(row, source_version="v20261025")

    assert first.forestproof_id == updated_release.forestproof_id
    assert first.source_version != updated_release.source_version


@pytest.mark.parametrize(
    "row, version",
    [
        ({"latitude": -0.48, "wur_radd_alerts__date": "2026-10-18"}, "v1"),
        ({"longitude": 36.61, "latitude": -0.48, "wur_radd_alerts__date": "2026-02-30"}, "v1"),
        ({"longitude": 181, "latitude": -0.48, "wur_radd_alerts__date": "2026-10-18"}, "v1"),
        ({"longitude": 36.61, "latitude": -0.48, "wur_radd_alerts__date": "2026-10-18", "area__ha": -1}, "v1"),
        (sample_radd_pixel_row(), " "),
    ],
)
def test_normalize_radd_rejects_invalid_or_incomplete_pixel_rows(row, version):
    with pytest.raises(ValueError):
        normalize_radd_pixel_row(row, source_version=version)
