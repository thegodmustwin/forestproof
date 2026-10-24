from __future__ import annotations

import base64
import hashlib

import pytest
from fastapi import HTTPException

from app.config import Settings
from app.demo_data import DEMO_ORGANIZATION_ID
from app.store import Store


@pytest.fixture()
def store(tmp_path):
    instance = Store(Settings("demo", tmp_path / "forestproof.db", tmp_path / "evidence", "http://localhost:3000"))
    instance.prepare()
    return instance


def test_demo_ingestion_is_idempotent_and_keeps_distinct_timestamps(store):
    observations = store.list_observations(DEMO_ORGANIZATION_ID)
    assert len(observations) == 3
    assert store.seed_demo_observations() == 0
    first = observations[0]
    assert first["observed_at"] != first["published_at"]
    assert first["published_at"] != first["ingested_at"]
    assert "DEMO_DATA" in first["quality_flags"]


def test_evidence_to_outcome_vertical_slice(store):
    observation = store.list_observations(DEMO_ORGANIZATION_ID)[0]
    case = store.create_case(DEMO_ORGANIZATION_ID, observation["id"], "Review synthetic observation", "Demo Conservation Team", "A. Reviewer")
    same_case = store.create_case(DEMO_ORGANIZATION_ID, observation["id"], "Ignored repeat", "Demo Conservation Team", "A. Reviewer")
    assert same_case["id"] == case["id"]

    store.transition_case(case["id"], "UNDER_REVIEW", "A. Reviewer", "Source provenance reviewed.")
    store.assign_case(case["id"], "Field reviewer", "Verifier", "A. Reviewer")
    store.transition_case(case["id"], "FIELD_VERIFICATION", "A. Reviewer", "Field verification requested.")
    payload = b"field note: synthetic test evidence"
    evidence = store.attach_evidence(
        case["id"], "field-note.txt", "text/plain", base64.b64encode(payload).decode(),
        "Synthetic upload for integrity test", "Field reviewer", None,
    )
    assert evidence["sha256"] == hashlib.sha256(payload).hexdigest()
    store.record_action(case["id"], "REQUESTED_REVIEW", "Requested an authorised review.", "Field reviewer", None)
    store.transition_case(case["id"], "ACTION_RECORDED", "Field reviewer", "Response recorded.")
    store.transition_case(case["id"], "FOLLOW_UP", "Field reviewer", "Follow-up is due.")
    store.record_follow_up(case["id"], "INSUFFICIENT_EVIDENCE", "Synthetic fixture has no real-world conclusion.", "Field reviewer", None)
    store.transition_case(case["id"], "CLOSED", "Field reviewer", "Case closed without legal finding.")

    dossier = store.dossier(case["id"])
    assert dossier["case"]["status"] == "CLOSED"
    assert dossier["completeness"]["provenance_present"]
    assert dossier["completeness"]["evidence_asset_count"] == 1
    assert dossier["completeness"]["verified_evidence_asset_count"] == 1
    assert dossier["case"]["evidence"][0]["dossier_integrity_status"] == "HASH_VERIFIED"
    assert "does not make a legal finding" in dossier["verification_notice"]


def test_invalid_state_transitions_and_tenant_boundaries_are_rejected(store):
    observation = store.list_observations(DEMO_ORGANIZATION_ID)[0]
    case = store.create_case(DEMO_ORGANIZATION_ID, observation["id"], "Boundary test", "Demo Conservation Team", None)
    with pytest.raises(HTTPException) as invalid_transition:
        store.transition_case(case["id"], "CLOSED", "Reviewer", "Skipping review.")
    assert invalid_transition.value.status_code == 409
    with pytest.raises(HTTPException) as premature_action:
        store.record_action(case["id"], "REQUESTED_REVIEW", "Too early.", "Reviewer", None)
    assert premature_action.value.status_code == 409
    with pytest.raises(HTTPException) as tenant_error:
        store.assert_case_access(case["id"], "org_other")
    assert tenant_error.value.status_code == 404
