"""Prepare and resolve a receipt for one built-in owner-demo observation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .demo_data import DEMO_OBSERVATIONS
from .pilot_radd_inbox import InboxError, PilotScope, create_inbox, export_observation, import_receipt
from .providers.gfw_radd import normalize_radd_pixel_row
from .sqlite_copy import RecoveryError


FIXTURE = next(observation for observation in DEMO_OBSERVATIONS if observation["id"] == "obs_demo_001")
FIXTURE_RELEASE = "v1"
RECEIVED_AT = datetime.fromisoformat(FIXTURE["ingested_at"])
_LON, _LAT = FIXTURE["geometry"]["coordinates"]
_SOURCE_ROW = {
    "longitude": _LON,
    "latitude": _LAT,
    "wur_radd_alerts__date": FIXTURE["observed_at"][:10],
}
_SCOPE = PilotScope(
    scope_id="forestproof-owner-rehearsal-v1",
    review_ref="ForestProof repository fixture",
    attribution="ForestProof synthetic RADD-shaped fixture",
    bounds=(_LON - 0.004, _LAT - 0.004, _LON + 0.004, _LAT + 0.004),
    max_observation_age_days=7,
    max_receipt_gap_hours=24,
)
_FIXTURE_BYTES = json.dumps(
    {"fixture": _SCOPE.scope_id, "status": "success", "data": [_SOURCE_ROW]},
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
_RECORD_KEY = normalize_radd_pixel_row(_SOURCE_ROW, source_version=FIXTURE_RELEASE).forestproof_id
_DIGEST = hashlib.sha256(_FIXTURE_BYTES).hexdigest()


def prepare_rehearsal_inbox(path: Path) -> None:
    """Create a new private inbox with the built-in synthetic response."""
    create_inbox(path, _SCOPE)
    try:
        import_receipt(path, _FIXTURE_BYTES, release=FIXTURE_RELEASE, received_at=RECEIVED_AT)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def resolve_rehearsal_receipt(path: Path, observation: dict) -> dict | None:
    """Resolve the exact built-in receipt, independently from other inbox records."""
    if observation["id"] != FIXTURE["id"]:
        return None
    if any(
        observation.get(field) != FIXTURE[field]
        for field in (
            "organization_id", "source_id", "source_product", "source_record_id",
            "processing_version", "geometry", "observed_at", "ingested_at",
        )
    ):
        raise InboxError("Observation does not match the receipt rehearsal fixture")

    record = export_observation(path, record_key=_RECORD_KEY, release=FIXTURE_RELEASE)
    receipt = record["receipt"]
    if (
        record["scope_id"] != _SCOPE.scope_id or record["review_ref"] != _SCOPE.review_ref
        or record["attribution"] != _SCOPE.attribution or record["source_row"] != _SOURCE_ROW
        or receipt["sha256"] != _DIGEST or receipt["byte_count"] != len(_FIXTURE_BYTES)
        or datetime.fromisoformat(receipt["received_at"]) != RECEIVED_AT
    ):
        raise InboxError("Stored receipt does not match the rehearsal fixture")
    return {
        "data_mode": "DEMO",
        "record_state": record["record_state"],
        "record_key": _RECORD_KEY,
        "fixture_release": FIXTURE_RELEASE,
        "observed_on": record["observed_on"],
        "receipt": receipt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a private synthetic owner-rehearsal inbox at a new path.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        prepare_rehearsal_inbox(args.path)
    except (OSError, ValueError, sqlite3.Error, RecoveryError):
        print("Could not prepare the rehearsal inbox. Check write access and use a new path.")
        return 1
    print("Synthetic owner rehearsal inbox created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
