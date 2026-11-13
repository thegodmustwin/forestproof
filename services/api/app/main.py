from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .demo_data import DEMO_AREA, DEMO_ORGANIZATION_ID, DEMO_SOURCES
from .models import ActionCreate, AssignmentCreate, CaseCreate, EvidenceCreate, FollowUpCreate, StatusTransition
from .owner_access import InternalAccessNotConfigured, valid_internal_token
from .providers.copernicus_stac import CatalogUnavailable, CopernicusCatalog
from .providers.gfw import status as gfw_status
from .source_provenance import demo_source_provenance
from .store import Store


settings = get_settings()
store = Store(settings)
copernicus_catalog = CopernicusCatalog()


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.prepare()
    yield


app = FastAPI(
    title="ForestProof API",
    version="0.1.0",
    description=(
        "Evidence-first environmental case workflow. Observations are not legal conclusions; "
        "enforcement and authorisation decisions stay with authorised human reviewers."
    ),
    lifespan=lifespan,
)
allowed_origins = [settings.web_origin]
if settings.mode == "demo":
    # Both names are normal loopback origins during local testing; production
    # does not inherit this convenience allowlist.
    allowed_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(set(allowed_origins)),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Organization-ID"],
)


def organization_id(
    x_organization_id: Annotated[str | None, Header()] = None,
    x_forestproof_internal_token: Annotated[str | None, Header()] = None,
    x_forestproof_require_owner_demo: Annotated[str | None, Header()] = None,
) -> str:
    """Constrain P0 to the synthetic demo tenant; LIVE remains disabled.

    A caller-supplied tenant header is never an authentication mechanism. Rather
    than pretending the header provides multi-tenant security, non-demo mode is
    fail-closed and demo mode only exposes the seeded demo organization.
    """
    if x_forestproof_require_owner_demo is not None and (
        x_forestproof_require_owner_demo != "1" or settings.mode != "owner_demo"
    ):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Owner demo API mode is not active")
    if settings.mode == "owner_demo":
        try:
            authorized = valid_internal_token(settings.internal_api_token, x_forestproof_internal_token)
        except InternalAccessNotConfigured:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Owner demo internal access is not configured") from None
        if not authorized:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Internal service authentication required")
    elif settings.mode != "demo":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured. Live or multi-organization operation is disabled.",
        )
    if x_organization_id and x_organization_id != DEMO_ORGANIZATION_ID:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the seeded demo organization is available in demo mode")
    return DEMO_ORGANIZATION_ID


Org = Annotated[str, Depends(organization_id)]


def recorded_actor(provided: str) -> str:
    """The owner-demo gateway represents one owner, not caller-supplied actors."""
    return "owner" if settings.mode == "owner_demo" else provided


def ensure_case_access(case_id: str, organization: str) -> None:
    store.assert_case_access(case_id, organization)


def with_source_provenance(observation: dict[str, Any]) -> dict[str, Any]:
    """Expose provenance only when this record is an identified demo fixture."""
    try:
        provenance = demo_source_provenance(observation)
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Observation source provenance is unavailable") from None
    return {**observation, "source_provenance": provenance}


def as_iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


@app.get("/api/v1/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": settings.mode.upper(),
        "database": "sqlite-development-adapter",
        "production_database_target": "PostgreSQL + PostGIS",
        "notice": "Demo mode contains deterministic synthetic data only.",
    }


@app.get("/api/v1/monitoring-areas")
def monitoring_areas(_: Org) -> list[dict[str, Any]]:
    return [DEMO_AREA]


@app.get("/api/v1/sources")
def sources(_: Org) -> dict[str, Any]:
    live = gfw_status()
    return {
        "sources": DEMO_SOURCES,
        "provider_health": [
            {
                "provider": live.provider,
                "operational_status": live.operational_status,
                "configured": live.configured,
                "tile_template": live.tile_template,
                "notice": live.notice,
            }
        ],
    }


@app.get("/api/v1/context/copernicus-scenes")
def copernicus_scenes(response: Response, _: Org) -> dict[str, Any]:
    """Opt-in, owner-demo-only scene context; not live forest alerts."""
    response.headers["Cache-Control"] = "no-store"
    if settings.mode != "owner_demo" or not settings.copernicus_catalog_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Satellite scene lookup is not enabled")
    try:
        return copernicus_catalog.latest()
    except CatalogUnavailable:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Satellite scene lookup is temporarily unavailable") from None


@app.get("/api/v1/observations")
def observations(organization: Org, source_id: str | None = None) -> dict[str, Any]:
    return {
        "items": [with_source_provenance(item) for item in store.list_observations(organization, source_id)],
        "mode": settings.mode.upper(),
        "disclaimer": "An observation is not an incident finding, permit determination, or allegation of wrongdoing.",
    }


@app.get("/api/v1/observations/{observation_id}")
def observation(observation_id: str, organization: Org) -> dict[str, Any]:
    return with_source_provenance(store.get_observation(organization, observation_id))


@app.post("/api/v1/ingestion/demo", status_code=status.HTTP_201_CREATED)
def ingest_demo(_: Org) -> dict[str, Any]:
    if settings.mode not in {"demo", "owner_demo"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Demo ingestion is disabled outside DEMO mode")
    return {"inserted": store.seed_demo_observations(), "mode": "DEMO", "notice": "Fixtures are idempotent synthetic observations."}


@app.post("/api/v1/ingestion/live/gfw", status_code=status.HTTP_409_CONFLICT)
def ingest_live_gfw(_: Org) -> dict[str, Any]:
    live = gfw_status()
    return {
        "status": "NOT_STARTED",
        "provider": live.provider,
        "reason": live.notice,
        "required_before_activation": [
            "Approved server-side credential", "Documented licensed area of interest", "Dataset/version selection",
            "Retention and attribution policy", "Integration test with preserved original metadata",
        ],
    }


@app.post("/api/v1/cases", status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, organization: Org) -> dict[str, Any]:
    return store.create_case(organization, payload.observation_id, payload.title, payload.owner_organization,
                             payload.reviewer, actor="owner" if settings.mode == "owner_demo" else None)


@app.get("/api/v1/cases")
def cases(organization: Org) -> dict[str, Any]:
    return {"items": store.list_cases(organization)}


@app.get("/api/v1/cases/{case_id}")
def case(case_id: str, organization: Org) -> dict[str, Any]:
    ensure_case_access(case_id, organization)
    result = store.get_case(case_id)
    result["observation"] = with_source_provenance(result["observation"])
    return result


@app.post("/api/v1/cases/{case_id}/transitions")
def transition_case(case_id: str, payload: StatusTransition, organization: Org) -> dict[str, Any]:
    ensure_case_access(case_id, organization)
    return store.transition_case(case_id, payload.to_status, recorded_actor(payload.actor), payload.note)


@app.post("/api/v1/cases/{case_id}/assignments", status_code=status.HTTP_201_CREATED)
def assign_case(case_id: str, payload: AssignmentCreate, organization: Org) -> dict[str, Any]:
    ensure_case_access(case_id, organization)
    return store.assign_case(case_id, payload.assignee, payload.role, recorded_actor(payload.actor))


@app.post("/api/v1/cases/{case_id}/actions", status_code=status.HTTP_201_CREATED)
def record_action(case_id: str, payload: ActionCreate, organization: Org) -> dict[str, Any]:
    ensure_case_access(case_id, organization)
    return store.record_action(case_id, payload.action_type, payload.summary, recorded_actor(payload.actor), as_iso(payload.occurred_at))


@app.post("/api/v1/cases/{case_id}/follow-ups", status_code=status.HTTP_201_CREATED)
def record_follow_up(case_id: str, payload: FollowUpCreate, organization: Org) -> dict[str, Any]:
    ensure_case_access(case_id, organization)
    return store.record_follow_up(case_id, payload.assessment, payload.summary, recorded_actor(payload.actor), as_iso(payload.observed_at))


@app.post("/api/v1/cases/{case_id}/evidence", status_code=status.HTTP_201_CREATED)
def attach_evidence(case_id: str, payload: EvidenceCreate, organization: Org) -> dict[str, Any]:
    ensure_case_access(case_id, organization)
    if settings.mode != "demo" or not settings.demo_evidence_uploads_enabled:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Evidence uploads are disabled")
    return store.attach_evidence(case_id, payload.file_name, payload.media_type, payload.content_base64,
                                 payload.source_description, payload.actor, as_iso(payload.observed_at))


@app.get("/api/v1/cases/{case_id}/dossier")
def dossier(case_id: str, organization: Org) -> dict[str, Any]:
    ensure_case_access(case_id, organization)
    result = store.dossier(case_id)
    result["case"]["observation"] = with_source_provenance(result["case"]["observation"])
    return result


@app.get("/api/v1/outcome-graph")
def outcome_graph(organization: Org) -> dict[str, Any]:
    return store.outcome_graph(organization)


@app.get("/api/v1/legal-context")
def legal_context(_: Org) -> dict[str, Any]:
    return {
        "items": [
            {
                "id": "legal-demo-review-gate",
                "status": "NO_VERIFIED_LEGAL_SOURCE_CONFIGURED",
                "title": "Human legal-review gate",
                "notice": "No court order, permit, restriction, or legal conclusion is loaded in the P0 demo. Add only source-linked, versioned documents reviewed by an authorised human.",
            }
        ],
        "rule": "A press report or unverified upload must not be surfaced as controlling law.",
    }


@app.get("/api/v1/operations")
def operations(organization: Org) -> dict[str, Any]:
    case_items = store.list_cases(organization)
    return {
        "case_counts": {state: sum(item["status"] == state for item in case_items) for state in [
            "NEW", "UNDER_REVIEW", "FIELD_VERIFICATION", "ACTION_RECORDED", "FOLLOW_UP", "CLOSED", "REOPENED"
        ]},
        "open_case_count": sum(item["status"] != "CLOSED" for item in case_items),
        "provider_health": [gfw_status().__dict__],
        "notice": "Operational metrics describe workflow records, not evidence of environmental impact.",
    }
