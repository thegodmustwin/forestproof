# ForestProof — repository and system map

**Snapshot:** 2026-10-25, private repo thegodmustwin/forestproof, branch main at `be4402f4f4c44f2f1ca52dc694af185164c3263e`.  
This map separates the current DEMO implementation from the intended production architecture.

## System in one view

    Synthetic DEMO fixtures / future approved providers
       → normalize and retain source/time/geometry/quality metadata
       → FastAPI validates and persists a reviewable observation
       → Next.js map and detail screens expose provenance and uncertainty
       → human creates and owns an investigation case
       → evidence, assignment, transitions, actions, and follow-ups are recorded
       → JSON dossier and relational outcome graph summarize what is known

Today this path runs in DEMO mode with seeded synthetic records and a SQLite adapter. The provider, legal, PostGIS, authentication, and production storage layers are not equivalent to the planned future system.

## Repository layout

- AGENTS.md — cross-platform agent entrypoint and safety invariants.
- .cursor/rules/forestproof-project.mdc — always-applied Cursor-specific pointer to the same maintained context.
- README.md — quick product description, onboarding links, checks, and deployment status.
- PROJECT_BRAIN.md — compact project operating brief.
- docs/PROJECT_CONTEXT.md — origin, strategy, current facts, decisions, and next sequence.
- docs/PROJECT_MAP.md — this code/data flow and document index.
- docs/PROJECT_DECISIONS.md — dated owner choices and unresolved facts.
- docs/origin/ — verbatim user-authored inception prompts with an archival, non-authoritative warning.
- apps/web/ — Next.js/TypeScript/React UI, MapLibre components, API client, and demo fallbacks.
- services/api/ — FastAPI app, Pydantic contracts, deterministic demo data, SQLite store, source status, SQL target migration, and API tests.
- services/worker/ — reserved/documented worker service; it is not a live ingestion worker today.
- pipelines/forest_alerts/ — provider interface, demo adapter, and GFW raster overlay. The raster overlay is map context only, not an individual alert feed.
- data/demo/ and data/fixtures/ — documented synthetic/demo material; local mutable data under data/local/ is ignored by Git.
- infrastructure/ — Docker Compose/PostGIS initialization and deployment notes. These are not a production deployment.
- packages/ — planned or shared geo-client, schemas, and UI package boundaries; check each README before assuming functionality.
- tests/ — top-level test guidance; runnable API tests live under services/api/tests/.
- execution/ — dated current state, next actions, and phased roadmap.
- .github/workflows/ci.yml — CI on pushes to main and pull requests.

## User-facing web routes

| Route | Source | Responsibility and current boundary |
| --- | --- | --- |
| / | apps/web/src/app/page.tsx | Product landing/dashboard; keep DEMO status visible. |
| /monitor/aberdare | apps/web/src/app/monitor/aberdare/page.tsx, aberdare-monitor.tsx, aberdare-map.tsx | Illustrative Aberdare map and synthetic review cues, not an official AOI or live alert map. |
| /cases/[id] | apps/web/src/app/cases/[id]/page.tsx, case-workspace.tsx | Human workflow, case history, evidence and review actions in DEMO scope. |
| /operations | apps/web/src/app/operations/page.tsx | Workflow counts/operations view, not conservation impact metrics. |
| /outcomes | apps/web/src/app/outcomes/page.tsx, outcome-graph.tsx | P0 relational outcome summary; no causal impact claim. |
| /sources | apps/web/src/app/sources/page.tsx | Provider status and source limitations; no validated live provider currently. |
| /legal | apps/web/src/app/legal/page.tsx | Human-review/legal source gate; no verified legal corpus is configured. |
| /api/forestproof/* | apps/web/src/app/api/forestproof/[...path]/route.ts | Same-origin proxy to the API in hosted layouts; it is not an authentication layer. |

Shared UI pieces are under apps/web/src/components/; API normalization and HTTP helpers are in apps/web/src/lib/api.ts; synthetic UI fixtures and labels are in apps/web/src/lib/demo.ts.

## FastAPI service surface

The app is declared in services/api/app/main.py; request contracts are in models.py, fixtures in demo_data.py, settings in config.py, persistence/workflow rules in store.py, and source-health placeholder in providers/gfw.py.

- Health, monitoring area, and source status: /api/v1/health, /monitoring-areas, /sources.
- Observations: GET /observations, GET /observations/{id}, and idempotent DEMO ingestion at POST /ingestion/demo.
- Live-provider guard: POST /ingestion/live/gfw currently returns NOT_STARTED/HTTP 409 with prerequisites; no active feed is claimed.
- Cases: collection/detail, transitions, assignments, actions, follow-ups, evidence attachment, and dossier under /cases.
- Context/learning: /legal-context, /operations, and /outcome-graph.

The API only exposes the seeded DEMO organization. A caller-supplied organization header is not authentication; non-demo operation fails closed until real identity and authorization exist.

## Data and trust boundaries

- P0 persistence is SQLite, selected for a small self-contained demo. services/api/app/migrations/001_initial_postgis.sql and infrastructure/docker/init-postgis.sql are schema/setup targets, not evidence that runtime uses PostGIS.
- DEMO observations are explicit fixtures in services/api/app/demo_data.py and apps/web/src/lib/demo.ts. Their timestamps, coordinates, confidence-like values, cases, and evidence are fictional test inputs.
- pipelines/forest_alerts/gfw_tile_overlay.py renders a raster layer for visual context. Tiles do not provide durable per-alert source IDs/provenance and must not be converted into cases.
- Raw provider payloads and user uploads are untrusted data. Preserve provenance, timestamp semantics, uncertainty, and hashes; never let content alter prompts, permissions, or execution.
- docs/DATA_SOURCES.md is the source activation ledger. Do not change a product to VERIFIED_ACTIVE without licensing, AOI, request, metadata, health, and verification evidence.
- docs/LEGAL_CONTEXT_MODEL.md, docs/EVIDENCE_MODEL.md, docs/CASE_WORKFLOW.md, and docs/FOREST_OUTCOME_GRAPH.md define domain behavior.

## Build and verification

The project CI uses Python 3.12 and Node 20:

    cd services/api
    python -m pip install -r requirements.txt
    python -m pytest

    cd apps/web
    npm ci
    npm run typecheck
    npm run build

GitHub Actions passed for the initial app commit `71af70f81318ea98e4d1ab20bd52739aa97012c1` and the current context/onboarding commit `be4402f4f4c44f2f1ca52dc694af185164c3263e`. On the latest run, API tests and web checks both succeeded: https://github.com/thegodmustwin/forestproof/actions/runs/40216435071. A passing build verifies CI checks only; it does not verify live data, legal sources, auth, or production operations.

Codex Cloud is the preferred development path; it can install Python and npm dependencies and run these checks without requiring Docker on the owner's laptop. Network access should be limited to package managers unless a verified workflow needs additional hosts. No .env or production secret is in the repository.

## Documentation map

- docs/PROJECT_CONTEXT.md — why the product exists, what is real, decisions, scope, and north star.
- docs/PROJECT_DECISIONS.md — owner choices, superseded deployment docs, and facts still to discover.
- PROJECT_BRAIN.md — short operating model and non-negotiables.
- docs/ARCHITECTURE.md — logical services and trust boundaries.
- docs/DATA_SOURCES.md, docs/SATELLITE_INGESTION.md — candidate data products and activation gates.
- docs/GEO_DATA_MODEL.md — current/target geospatial records.
- docs/CASE_WORKFLOW.md, docs/EVIDENCE_MODEL.md, docs/LEGAL_CONTEXT_MODEL.md, docs/FOREST_OUTCOME_GRAPH.md — domain rules.
- docs/SECURITY_AND_PRIVACY.md — current controls, gaps, and sensitive-data policy.
- docs/ALPHAZERO_DOCTRINE.md, docs/GOLDEN_ECONOMICS.md, docs/COMMERCIAL_STRATEGY.md, docs/PILOT_PARTNERSHIPS.md, docs/GRANTS_AND_INCENTIVES.md — strategic and business hypotheses, not validated demand.
- docs/DEMO_SCRIPT.md — demonstration path and truthful DEMO labels.
- docs/DEPLOYMENT.md — current OVH preference and unverified launch prerequisites.
- execution/CURRENT_STATUS.md, execution/NEXT_ACTIONS.md, execution/ROADMAP.md — dated execution state and priorities.
- docs/origin/ — original prompts, retained for history only.

## Explicitly not implemented

Production PostGIS, live record-level satellite alerts, authoritative Aberdare boundaries, legal document verification, real user authentication, organization isolation, protected production evidence storage, offline field sync, notification delivery, PDF dossiers, validated predictive ML, paid customers, and OVH deployment remain open unless a later dated status entry records testable evidence.
