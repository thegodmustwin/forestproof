# Satellite and Alert Ingestion

## Status

**P0 design — PARTIAL/PLANNED.** DEMO ingestion may be used during development. Live ingestion is disabled by default until a specific provider passes the activation checklist in DATA_SOURCES.md.

## Provider contract

Each provider implements the equivalent of:

    discover(area, time_range)
    fetch(cursor)
    normalize(record)
    provenance(record)

It also exposes health information and a stable provider/product identifier.

## Normalized observation contract

An environmental observation retains:

    id
    source_id
    source_product
    source_record_id
    observed_at
    published_at (optional)
    ingested_at
    geometry
    observation_type
    confidence_value and confidence_meaning (optional)
    spatial_resolution_meters (optional)
    forest_classification (optional)
    processing_version
    raw_evidence_ref
    quality_flags
    record_mode (DEMO or LIVE)

Observed, published, and ingested timestamps are distinct. Missing timestamps are surfaced as quality issues rather than silently substituted.

## Raster-cell products and derived events

Some alert products expose raster-cell values rather than provider-defined event records. In the GFW Integrated Alerts (`v20261026`) and RADD (`v20261018`) field catalogs checked on 2026-10-26, the published fields included cell coordinates, source-specific dates, confidence, and intensity, but no provider event ID. Before ingesting such a product, distinguish a provider-native record ID (when one exists) from a deterministic raster-cell identity derived from product, grid/cell location, observation date, and source version. Store the processing/source version separately so an updated release can be compared with the prior snapshot.

If ForestProof groups adjacent cells into a reviewable candidate, persist it as a derived cluster with the clustering method/version, parameters, and references to its contributing source cells. Keep source pixels and derived geometry distinct. A cluster is an analytical convenience, not a provider alert, confirmed event, allegation, or legal conclusion. Do not enable the live path until a bounded response confirms the exact response shape and terms allow the required retention.

`services/api/app/providers/raster_identity.py` implements the deterministic cell/date key primitive. `services/api/app/providers/gfw_radd.py` now normalizes one RADD field map using documented catalog field names and preserves the raw row, release version, observation date, and uninterpreted confidence values. Tests use synthetic field-shaped input. This parser does not parse a verified HTTP response envelope, persist cell snapshots, cluster cells, or query the live provider; all remain future work.

An additional standalone development primitive, `services/api/app/providers/radd_snapshot_store.py`, can persist bounded synthetic row batches in SQLite. It records the derived cell key, source release, source date, canonical raw JSON, SHA-256 and UTC receipt time. Replaying identical fields is idempotent; conflicting fields for the same cell/release abort the entire batch rather than overwrite evidence. Separate releases are retained separately. This module makes no network requests and is not wired to the API or a production database. Retention and use of actual provider data still depend on verified provider terms, and a hash is not proof of origin or truth.

**Request-contract check, 2026-10-27:** the public GFW OpenAPI describes authenticated `POST /dataset/{dataset}/{version}/query/json` requests with an SQL string and optional inline geometry. The route documentation says raster-only datasets require geometry or a geostore; the POST schema exposes inline geometry. The response schema is insufficient to establish the real response envelope. No alert query was made, and no SQL, geometry or response behavior has been operationally verified.

## Required protections

- Filter through an approved monitored area of interest.
- Validate GeoJSON type, coordinate order/range, geometry validity, and spatial overlap.
- Validate timestamp syntax and reject impossible time ordering when provider semantics require it.
- Preserve raw metadata or a durable reference when permitted by source terms.
- Use provider/source-record idempotency keys.
- Detect duplicates and related overlaps without erasing provenance.
- Bound retries with backoff; record failures, cursor state, and rate-limit responses.
- Never transform a provider alert into illegal logging.

## DEMO versus LIVE

DEMO fixtures are deterministic and contain no asserted real incident. Their geometry, content, evidence, and metrics must carry a visible DEMO label. LIVE data uses only configured provider credentials and persists original source metadata. Demo and live fixtures must not be mixed in production metrics by default.

## Source health states

Use distinct states for:

- NO_NEW_ALERTS
- SOURCE_NOT_UPDATED
- PROVIDER_UNAVAILABLE
- INGESTION_FAILED
- RATE_LIMITED
- DEGRADED
- HEALTHY

Absence of alerts is not evidence of system health.

## P0 verification

Test idempotency, invalid geometry, out-of-order timestamps, retry/backoff, source attribution, DEMO/LIVE separation, missing-data detection, and provider failures before representing ingestion as working.


## 2026-10-28: offline release comparison

The local RADD snapshot store now compares raw fields for two explicitly saved versions of the same ForestProof cell/date identity. It reports which top-level source fields differ, without interpreting confidence, declaring an alert retracted, or asserting that the releases are complete. It rejects missing snapshots and identical release identifiers. An alert date change yields a different identity and is not automatically linked. Tests use synthetic data only. This remains standalone SQLite groundwork: no live response has been fetched, parsed or ingested.
