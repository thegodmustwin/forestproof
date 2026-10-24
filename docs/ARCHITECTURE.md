# Architecture

## Status

**P0 local vertical slice — PARTIAL.** The DEMO workflow is executable; live providers, authentication, and the production PostGIS repository adapter are intentionally not deployed.

## Design objective

ForestProof is a low-cost coordination and evidence layer on top of legitimate Earth-observation sources. The architecture favors bounded scheduled work, shared data products, provenance, and human review over expensive always-on processing.

## P0 logical flow

    Provider or DEMO fixture
        -> normalization and validation
        -> SQLite development observation record (PostGIS target schema supplied)
        -> map/detail experience
        -> human-created investigation case
        -> evidence/actions/audit history
        -> outcome assessment
        -> EvidenceProof dossier

## Intended components

### Web application

- Next.js, TypeScript, React, and component-scoped global CSS.
- MapLibre GL JS for a 2D operational map.
- Lightweight charts for workflow and outcome metrics.
- Expected routes: Aberdare monitor, case detail, dossier, operations, legal library, outcomes, and source health.

### API

- Python/FastAPI with Pydantic validation.
- A small SQLite development repository with a PostGIS-aligned schema target.
- A fixed single-organization DEMO boundary; non-demo requests fail closed until authenticated identity and role enforcement are implemented.
- API returns explicit evidence level and DEMO/LIVE provenance.

### Data and storage

- PostgreSQL with PostGIS is the target primary store for structured and spatial data; the provided SQL target is not wired into the P0 API yet.
- Object storage uses an S3-compatible interface in production and a local adapter in development.
- Original evidence and transformed previews have separate records and hashes.

### Ingestion

- A provider interface supports discovery, fetch, normalization, provenance, health reporting, and retry/backoff.
- P0 begins with a deterministic DEMO provider.
- A real provider is enabled only after terms, access, AOI coverage, and requests are verified.

### Background work

- P0 exposes bounded on-demand demo ingestion and verifies hashes during dossier preparation.
- Bounded scheduled workers will run ingestion, integrity verification, dossier preparation, and source-health checks after a real source is activated.
- A queue is deferred until demonstrated reliability or concurrency needs justify it.

## Trust boundaries

1. External provider payloads are untrusted until schema, geometry, timestamp, and source validation succeeds.
2. File uploads are untrusted until type, size, access controls, and hashing succeed.
3. Browser clients never decide authorization or legal applicability.
4. The API accepts only the seeded demo organization and rejects non-demo operation until authentication is available.
5. Dossiers contain source references and uncertainty; they are not legal opinions.

## Development and deployment

Docker Compose is sufficient for local P0 services. Kubernetes, Kafka, global imagery mirrors, GPUs, and custom ML infrastructure are explicitly out of scope for the initial slice.

See DEPLOYMENT.md for the intended low-cost path and SECURITY_AND_PRIVACY.md for safeguards.
