import copy

import pytest

from app.providers.gfw_radd_envelope import (
    MAX_ENVELOPE_BYTES,
    MAX_ENVELOPE_ROWS,
    parse_radd_query_envelope,
)


@pytest.fixture
def row():
    # Synthetic fields only, never a provider observation.
    return {
        "longitude": 36.61,
        "latitude": -0.48,
        "wur_radd_alerts__date": "2026-10-18",
        "wur_radd_alerts__confidence": "uninterpreted",
        "area__ha": 0.01,
    }


def test_parses_documented_candidate_envelope_and_copies_raw_data(row):
    payload = {"status": "success", "data": [row], "extra": {"provenance": "synthetic"}}
    before = copy.deepcopy(payload)
    result = parse_radd_query_envelope(payload, source_version="v20261018")
    payload["data"][0]["longitude"] = 1
    payload["extra"]["provenance"] = "changed"
    assert result.source_version == "v20261018"
    assert len(result.cells) == 1
    assert result.cells[0].longitude == 36.61
    assert result.cells[0].source_product == "wur_radd_alerts"
    assert result.cells[0].forestproof_id.startswith("forestproof:raster-cell:v1:")
    assert result.raw_envelope == before


def test_empty_query_is_preserved_without_creating_records_or_a_health_claim():
    payload = {"status": "success", "data": []}
    result = parse_radd_query_envelope(payload, source_version="v20261018")
    assert result.cells == ()
    assert result.raw_envelope == payload


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {"data": []},
        {"status": "error", "data": []},
        {"status": "success"},
        {"status": "success", "data": {}},
        {"status": "success", "data": [None]},
        {"status": "success", "data": [{"latitude": 100}]},
    ],
)
def test_rejects_unsuccessful_or_malformed_envelopes(payload):
    with pytest.raises(ValueError):
        parse_radd_query_envelope(payload, source_version="v20261018")


@pytest.mark.parametrize("version", ["latest", "", "v 1", "v123456789", None])
def test_requires_concrete_source_version_even_for_empty_data(version):
    with pytest.raises(ValueError, match="concrete"):
        parse_radd_query_envelope({"status": "success", "data": []}, source_version=version)


def test_rejects_oversized_or_non_json_input(row):
    with pytest.raises(ValueError, match="row limit"):
        parse_radd_query_envelope(
            {"status": "success", "data": [row] * (MAX_ENVELOPE_ROWS + 1)},
            source_version="v1",
        )
    with pytest.raises(ValueError, match="size limit"):
        parse_radd_query_envelope(
            {"status": "success", "data": [], "padding": "x" * MAX_ENVELOPE_BYTES},
            source_version="v1",
        )
    with pytest.raises(ValueError, match="valid UTF-8 JSON"):
        parse_radd_query_envelope(
            {"status": "success", "data": [], "extra": {1: "not a JSON key"}},
            source_version="v1",
        )
    with pytest.raises(ValueError, match="valid UTF-8 JSON"):
        parse_radd_query_envelope(
            {"status": "success", "data": [], "value": float("nan")},
            source_version="v1",
        )
