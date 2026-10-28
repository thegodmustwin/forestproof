import copy
import hashlib
import json

import pytest

from app.providers.gfw_radd import normalize_radd_pixel_row
from app.providers.radd_snapshot_store import RaddSnapshotStore, SnapshotConflict


@pytest.fixture
def sample_row():
    # Entirely synthetic data; no live source was queried.
    return {
        "longitude": 36.61,
        "latitude": -0.48,
        "wur_radd_alerts__date": "2026-10-18",
        "wur_radd_alerts__confidence": 2,
        "wur_radd_alerts__date_conf": "uninterpreted",
        "area__ha": 0.01,
    }


@pytest.fixture
def snapshot_store(tmp_path):
    store = RaddSnapshotStore(tmp_path / "snapshots.sqlite")
    store.initialize()
    return store


def test_preserves_raw_fields_release_identity_and_utc_receipt_time(snapshot_store, sample_row):
    original = copy.deepcopy(sample_row)
    result = snapshot_store.save_batch([sample_row], source_version="v20261018")
    cell = normalize_radd_pixel_row(sample_row, source_version="v20261018")
    sample_row["wur_radd_alerts__confidence"] = 99
    saved = snapshot_store.get_snapshot(forestproof_id=cell.forestproof_id, source_version="v20261018")
    assert (result.inserted, result.unchanged) == (1, 0)
    assert saved["raw_fields"] == original
    canonical = json.dumps(original, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    assert saved["raw_fields_sha256"] == hashlib.sha256(canonical.encode()).hexdigest()
    assert saved["source_version"] == "v20261018"
    assert saved["observed_on"] == "2026-10-18"
    assert saved["recorded_at"].endswith("+00:00")


def test_same_snapshot_replay_is_idempotent_but_new_release_is_preserved(snapshot_store, sample_row):
    first = snapshot_store.save_batch([sample_row], source_version="v20261018")
    replay = snapshot_store.save_batch([dict(reversed(list(sample_row.items())))], source_version="v20261018")
    release = snapshot_store.save_batch([sample_row], source_version="v20261025")
    cell = normalize_radd_pixel_row(sample_row, source_version="v20261018")
    assert (first.inserted, replay.unchanged, release.inserted) == (1, 1, 1)
    assert snapshot_store.get_snapshot(forestproof_id=cell.forestproof_id, source_version="v20261025") is not None


def test_changed_same_release_is_rejected_and_batch_rolls_back(snapshot_store, sample_row):
    snapshot_store.save_batch([sample_row], source_version="v20261018")
    new = {**sample_row, "longitude": 36.62}
    conflict = {**sample_row, "wur_radd_alerts__confidence": 3}
    with pytest.raises(SnapshotConflict):
        snapshot_store.save_batch([new, conflict], source_version="v20261018")
    new_id = normalize_radd_pixel_row(new, source_version="v20261018").forestproof_id
    assert snapshot_store.get_snapshot(forestproof_id=new_id, source_version="v20261018") is None
    old_id = normalize_radd_pixel_row(sample_row, source_version="v20261018").forestproof_id
    assert snapshot_store.get_snapshot(forestproof_id=old_id, source_version="v20261018")["raw_fields"] == sample_row


def test_invalid_or_unbounded_batches_are_rejected_without_partial_writes(snapshot_store, sample_row):
    with pytest.raises(ValueError):
        snapshot_store.save_batch([], source_version="v20261018")
    with pytest.raises(ValueError):
        snapshot_store.save_batch([sample_row] * 1001, source_version="v20261018")
    with pytest.raises(ValueError):
        snapshot_store.save_batch([sample_row, {**sample_row, "latitude": 100}], source_version="v20261018")
    with pytest.raises(ValueError):
        snapshot_store.save_batch([{**sample_row, "unexpected": float("nan")}], source_version="v20261018")
    with pytest.raises(ValueError):
        snapshot_store.save_batch([{**sample_row, "unexpected": "x" * 70_000}], source_version="v20261018")
    cell = normalize_radd_pixel_row(sample_row, source_version="v20261018")
    assert snapshot_store.get_snapshot(forestproof_id=cell.forestproof_id, source_version="v20261018") is None



def test_compare_releases_reports_source_field_changes_without_interpreting_them(snapshot_store, sample_row):
    updated = {**sample_row, "wur_radd_alerts__confidence": 3, "new_source_field": None}
    snapshot_store.save_batch([sample_row], source_version="v20261018")
    snapshot_store.save_batch([updated], source_version="v20261025")
    cell = normalize_radd_pixel_row(sample_row, source_version="v20261018")

    compared = snapshot_store.compare_releases(
        forestproof_id=cell.forestproof_id, from_version="v20261018", to_version="v20261025"
    )

    assert compared == {
        "forestproof_id": cell.forestproof_id,
        "source_product": "wur_radd_alerts",
        "from_version": "v20261018",
        "to_version": "v20261025",
        "change": "SOURCE_FIELDS_CHANGED",
        "changed_fields": ["new_source_field", "wur_radd_alerts__confidence"],
    }
    assert snapshot_store.get_snapshot(
        forestproof_id=cell.forestproof_id, source_version="v20261018"
    )["raw_fields"] == sample_row


def test_compare_releases_is_independent_of_json_key_order(snapshot_store, sample_row):
    first = {**sample_row, "metadata": {"a": 1, "b": [2, 3]}}
    second = {**sample_row, "metadata": {"b": [2, 3], "a": 1}}
    snapshot_store.save_batch([first], source_version="v1")
    snapshot_store.save_batch([second], source_version="v2")
    cell = normalize_radd_pixel_row(first, source_version="v1")

    result = snapshot_store.compare_releases(
        forestproof_id=cell.forestproof_id, from_version="v1", to_version="v2"
    )
    assert result["change"] == "UNCHANGED"
    assert result["changed_fields"] == []


def test_compare_releases_distinguishes_json_types(snapshot_store, sample_row):
    snapshot_store.save_batch([{**sample_row, "metadata": {"flag": True}}], source_version="v1")
    snapshot_store.save_batch([{**sample_row, "metadata": {"flag": 1}}], source_version="v2")
    cell = normalize_radd_pixel_row(sample_row, source_version="v1")

    result = snapshot_store.compare_releases(
        forestproof_id=cell.forestproof_id, from_version="v1", to_version="v2"
    )
    assert result["changed_fields"] == ["metadata"]


def test_compare_releases_requires_both_snapshots_and_distinct_versions(snapshot_store, sample_row):
    snapshot_store.save_batch([sample_row], source_version="v1")
    cell = normalize_radd_pixel_row(sample_row, source_version="v1")
    with pytest.raises(ValueError, match="absent row does not establish a retraction"):
        snapshot_store.compare_releases(
            forestproof_id=cell.forestproof_id, from_version="v1", to_version="v2"
        )
    with pytest.raises(ValueError, match="distinct"):
        snapshot_store.compare_releases(
            forestproof_id=cell.forestproof_id, from_version="v1", to_version="v1"
        )
    with pytest.raises(ValueError, match="identity"):
        snapshot_store.compare_releases(forestproof_id="", from_version="v1", to_version="v2")
