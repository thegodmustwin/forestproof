from __future__ import annotations

from datetime import UTC, datetime


DEMO_ORGANIZATION_ID = "org_demo_aberdare"
DEMO_AREA = {
    "id": "area_aberdare_demo",
    "name": "Aberdare pilot area — DEMO boundary",
    "mode": "DEMO",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[36.738, -0.418], [36.796, -0.418], [36.796, -0.363], [36.738, -0.363], [36.738, -0.418]]],
    },
    "boundary_notice": "Illustrative development boundary only. It is not an official forest, legal, or management boundary.",
}

DEMO_SOURCES = [
    {
        "id": "demo-synthetic-v1",
        "name": "ForestProof deterministic demo provider",
        "official_organization": "ForestProof development fixture",
        "product_name": "Synthetic disturbance observations",
        "operational_status": "VERIFIED_ACTIVE",
        "mode": "DEMO",
        "license": "CC0 test data",
        "source_url": None,
        "limitations": "Synthetic fixtures. They represent no actual event, person, forest boundary, permit, or legal condition.",
    },
    {
        "id": "gfw-glad-s2-overlay",
        "name": "Global Forest Watch GLAD-S2 raster overlay",
        "official_organization": "Global Forest Watch / University of Maryland GLAD",
        "product_name": "GLAD-S2 alerts",
        "operational_status": "DOCUMENTED_NOT_TESTED",
        "mode": "LIVE_CONTEXT_ONLY",
        "license": "See source terms and dataset metadata before redistribution",
        "source_url": "https://tiles.globalforestwatch.org/",
        "limitations": "Map context only. Raster tiles do not produce a provenance-preserving individual observation or legal conclusion.",
    },
    {
        "id": "gfw-data-api",
        "name": "Global Forest Watch Data API",
        "official_organization": "Global Forest Watch",
        "product_name": "Machine-readable forest data",
        "operational_status": "AVAILABLE_WITH_CREDENTIALS",
        "mode": "LIVE",
        "license": "Dataset-specific; verify before operational or commercial use",
        "source_url": "https://data-api.globalforestwatch.org/openapi.json",
        "limitations": "Disabled until approved server-side credentials, data terms, AOI definition, and source-version preservation are configured.",
    },
]

DEMO_OBSERVATIONS = [
    {
        "id": "obs_demo_001",
        "organization_id": DEMO_ORGANIZATION_ID,
        "source_id": "demo-synthetic-v1",
        "source_product": "SYNTHETIC_DISTURBANCE_V1",
        "source_record_id": "DEMO-ABERDARE-001",
        "observation_type": "FOREST_DISTURBANCE",
        "classification": "REQUIRES_HUMAN_REVIEW",
        "confidence_value": 0.74,
        "confidence_meaning": "Synthetic score for interface testing—not a scientific confidence estimate.",
        "spatial_resolution_meters": 10,
        "observed_at": "2026-10-12T09:15:00Z",
        "published_at": "2026-10-14T08:00:00Z",
        "ingested_at": "2026-10-14T08:05:12Z",
        "processing_version": "demo-provider/1.0.0",
        "forest_classification": "UNKNOWN_PENDING_VERIFICATION",
        "quality_flags": ["DEMO_DATA", "NOT_A_LIVE_DETECTION", "AUTHORIZATION_UNKNOWN"],
        "geometry": {"type": "Point", "coordinates": [36.7654, -0.3876]},
        "raw_evidence_ref": "demo://fixtures/aberdare-001",
    },
    {
        "id": "obs_demo_002",
        "organization_id": DEMO_ORGANIZATION_ID,
        "source_id": "demo-synthetic-v1",
        "source_product": "SYNTHETIC_RADAR_CHANGE_V1",
        "source_record_id": "DEMO-ABERDARE-002",
        "observation_type": "RADAR_CHANGE",
        "classification": "PLANTATION_MANAGEMENT_POSSIBLE",
        "confidence_value": 0.61,
        "confidence_meaning": "Synthetic score for interface testing—not a scientific confidence estimate.",
        "spatial_resolution_meters": 20,
        "observed_at": "2026-10-09T06:10:00Z",
        "published_at": "2026-10-11T12:00:00Z",
        "ingested_at": "2026-10-11T12:02:40Z",
        "processing_version": "demo-provider/1.0.0",
        "forest_classification": "UNVERIFIED_LAND_CLASS",
        "quality_flags": ["DEMO_DATA", "NOT_A_LIVE_DETECTION", "AUTHORIZATION_UNKNOWN"],
        "geometry": {"type": "Point", "coordinates": [36.7821, -0.3992]},
        "raw_evidence_ref": "demo://fixtures/aberdare-002",
    },
    {
        "id": "obs_demo_003",
        "organization_id": DEMO_ORGANIZATION_ID,
        "source_id": "demo-synthetic-v1",
        "source_product": "SYNTHETIC_FIRE_CONTEXT_V1",
        "source_record_id": "DEMO-ABERDARE-003",
        "observation_type": "FIRE_ANOMALY",
        "classification": "POSSIBLE_FIRE_DAMAGE",
        "confidence_value": 0.38,
        "confidence_meaning": "Synthetic score for interface testing—not a scientific confidence estimate.",
        "spatial_resolution_meters": 375,
        "observed_at": "2026-10-07T11:30:00Z",
        "published_at": "2026-10-07T14:08:00Z",
        "ingested_at": "2026-10-07T14:11:10Z",
        "processing_version": "demo-provider/1.0.0",
        "forest_classification": "UNKNOWN_PENDING_VERIFICATION",
        "quality_flags": ["DEMO_DATA", "NOT_A_LIVE_DETECTION", "FIRE_CONTEXT_NOT_LOGGING_EVIDENCE"],
        "geometry": {"type": "Point", "coordinates": [36.7503, -0.3718]},
        "raw_evidence_ref": "demo://fixtures/aberdare-003",
    },
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
