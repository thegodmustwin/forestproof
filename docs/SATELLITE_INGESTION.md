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
