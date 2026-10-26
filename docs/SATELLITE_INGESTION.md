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
