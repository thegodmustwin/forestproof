# ForestProof — repository and system map

## Matched radar research

[`tools/nasa_rtc_research/`](../tools/nasa_rtc_research/README.md) verifies the pinned OPERA RTC-S1 batch and compares paired VV and VH against same-season reference captures on the common quality mask. Its inputs and aggregate results remain outside the live application. [Repeat-pass evidence](DIRECT_SOURCE_EVALUATION.md#geta-repeat-pass-radar-research---2026-11-16)

The [historical fire backtest](../tools/nasa_rtc_research/README.md#historical-fire-backtest) scores the published JPL prototype against independent BAER severity maps, preserving missing data and separate sample counts for each matched class.

## Alert publication rehearsal

The [loopback alert preview](../tools/alert_publication/README.md) projects only explicitly approved fields tied to an exact source release and receipt. The [GLAD-L paired archive inspection](../tools/glad_l_research/README.md#paired-alert-archive-inspection) checks provider status, detection and observation dates independently of the public view.

## Sentinel-2 scene visibility

[`tools/sentinel_visibility/`](../tools/sentinel_visibility/README.md) checks one to three Sentinel-2 Level-2A acquisitions against the provisional Geta rectangle. The private JSON report preserves two separate native grid counts and pins each SCL input by ETag and SHA-256. It sits outside alert ingestion, case storage and public routing.

The [visibility preview builder](../tools/sentinel_visibility/README.md#private-visibility-page) projects a verified report into static HTML with a distinct zero, unavailable, and overdue experience. The page excludes the precise bounds and source receipt fields.

[`visibility_service.py`](../tools/sentinel_visibility/visibility_service.py) refreshes and serves the authorized visibility report independently of the app. The [Contabo runbook](../infrastructure/deployment/sentinel-visibility/README.md) defines the timer and exact HTTPS route.

## Source-status publication preview
The separate `tools/source_status/stage_source_status.py` command refreshes one observation source into its own atomic state file and serves a loopback-only read view. It does not route to the demo API or case storage. See [the staged workflow](../tools/source_status/README.md#isolated-staging).

`tools/source_status/` validates the fixed provisional GLAD-L report and generates a standalone read-only HTML page. The page displays the provider file update, ForestProof check, reporting day and local observation day as separate facts. See [local build and limits](../tools/source_status/README.md).

## GLAD-L observation-date diagnostic

`tools/glad_l_research/` uses budgeted read-only byte ranges for one generation of the producer's observation-date raster. It produces a bounded recency summary and plumbs no data into the app. See [the documented check](DIRECT_SOURCE_EVALUATION.md#measured-local-observation-recency--2026-11-14).


## Private historical research case

The November 3 NASA files support one private, reproducible research case, FP-RESEARCH-001. The existing `tools/nasa_dist_research/` grid validation and source diagnostics supplied the basis for the private case script. The dossier, native pixel selectors, original source files, and recovery materials are held outside Git. See [the research checkpoint](../execution/CURRENT_STATUS.md#first-genuine-research-case-and-restore--2026-11-14).

The [local owner review](../tools/owner_review/README.md) admits the verified archive to a separate database and allows an authenticated owner to record disposition and follow-up. The review exports and backup preserve the historical receipt linkage.

[The offline OPERA receipt rehearsal](../services/api/app/historical_opera_receipt.py) tests exact manifest and attachment retention with synthetic placeholders. It uses the shared checked SQLite copy helper and never reads the private archive through the application. From `services/api`, run `python -m pytest tests/test_historical_opera_receipt.py` to exercise import, byte-identical replay, conflict rejection and a restored dossier without the source files. The CLI has `init`, `ingest`, `dossier` and `copy` commands. The rehearsal accepts only the fictional `T00AAA` tile and short role-specific placeholder bytes. Raster interpretation remains in the NASA research tools.

## Private RADD import rehearsal

`services/api/app/pilot_radd_inbox.py` imports explicitly supplied response bytes into a separate SQLite inbox, records source and receipt identity, reports freshness, exports an unverified record and supports a checked copy. See [the operator runbook](PRIVATE_RADD_INBOX.md). Opt-in `services/api/app/owner_receipt_rehearsal.py` creates a private built-in fixture inbox. The authenticated owner-demo API resolves that exact receipt in observation, case and dossier details. Regular DEMO is unaffected. Source-cleared ingestion and live case storage are pending.

## Owner-demo browser mutation guard — 2026-11-13

`apps/web/src/lib/internal-api-config.ts` requires an explicit HTTP IPv4 loopback gateway origin in synthetic `owner_demo` mode. The Next.js proxy rejects missing or mismatched `Origin` on POST before forwarding its internal service token, alongside the separate owner gateway check. The isolated smoke and proxy tests exercise this boundary. This is a CSRF defense for the uninstalled owner-demo candidate, not human authentication, protection for an exposed web listener, or LIVE authorization.

`docs/PREVIEW_UPLOAD_GUARD.md` records the default-off synthetic evidence
upload guard at both API and storage boundaries; it is not owner identity.

## Reproducible NASA research tool — 2026-11-13

`tools/nasa_dist_research/` contains an offline, explicitly bounded single-granule multi-layer diagnostic with synthetic tests and separate optional dependencies. It does not download data, enable LIVE, establish an official boundary, or make forest-loss claims.

## Source context in observation detail — 2026-11-12

`apps/web/src/lib/observation-normalization.ts` validates the optional versioned demo provenance contract and `observation-detail.tsx` shows source record, processing version, release, completeness and attribution without guessing missing values. This remains synthetic-only and is not live-source activation.


## NASA sample inspection — 2026-11-12

`docs/NASA_DIST_SAMPLE_20261112.md` records the local four-band checks and comparison of both overlapping November 3 NASA DIST-HLS tiles. It preserves native-grid counts, the current-scene and historical-date distinction, and the provisional geography.

## Direct-source evaluation — 2026-11-12

`docs/DIRECT_SOURCE_EVALUATION.md` records the direct NASA metadata/browse and GLAD-L file-metadata tests, access and licence caveats.

## Research update — 2026-11-12

`docs/GNW_INDEPENDENCE_RESEARCH.md` compares GNW capabilities, self-hosted options, direct-source candidates, licensing and defensibility hypotheses. It does not change the lead feed or claim a live integration.


## Recovery candidate — 2026-11-11

`services/api/app/demo_db_copy.py` and its tests implement a synthetic-only, non-overwriting SQLite copy/restore drill; usage and limits are in `docs/DEMO_SQLITE_RECOVERY.md`. It does not back up evidence objects or establish production recovery readiness.

**Snapshot:** 2026-10-25, private repo thegodmustwin/forestproof, branch `main`; application code is at `71af70f81318ea98e4d1ab20bd52739aa97012c1` and subsequent commits maintain the context package.  
This map separates the current DEMO implementation from the intended production architecture.

## Disabled-mode storage guard — 2026-11-12

`services/api/app/store.py` prevents unsupported modes from opening or migrating the configured SQLite path. See `docs/DISABLED_MODE_STORAGE_GUARD.md`. This is not a LIVE store or backup.

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
- docs/LAUNCH_STRATEGY.md — 2026-11-06 code-verified readiness, minimum account needs, separate preview/live acceptance criteria and UI review sequence.
- docs/origin/ — verbatim user-authored inception prompts with an archival, non-authoritative warning.
- apps/web/ — Next.js/TypeScript/React UI, MapLibre components, API client, and demo fallbacks.
- apps/web/src/lib/observation-normalization.ts — demo-only API observation validation; missing provenance is displayed as missing and records without a valid ID, point, or DEMO_DATA flag are rejected. It does not implement live display.
- `infrastructure/deployment/owner-pilot/`, `apps/web/src/lib/internal-api-config.ts` and `services/api/app/owner_access.py` — uninstalled synthetic owner identity candidate. Caddy asserts the authenticated owner subject to the web process, which independently verifies the gateway token and uses a distinct API token for its loopback request. The API records the verified subject as the audit actor. LIVE remains disabled.
- services/api/ — FastAPI app, Pydantic contracts, deterministic demo data, SQLite store, source status, SQL target migration, and API tests.
- services/worker/ — reserved/documented worker service; it is not a live ingestion worker today.
- pipelines/forest_alerts/ — provider interface, demo adapter, and GFW raster overlay. The raster overlay is map context only, not an individual alert feed. `services/api/app/providers/raster_identity.py` and `gfw_radd.py` contain tested identity/normalization primitives; neither makes live requests or persists alerts.
- services/api/app/providers/radd_snapshot_store.py — standalone local SQLite groundwork for retaining synthetic RADD cell/release snapshots, replay detection and conflict rollback. It is not connected to the API, a live feed, or the production PostGIS target.
- services/api/app/providers/gfw_radd_research.py — default-deny, standalone bounded research transport candidate. Its tests use synthetic and loopback-only mocks; it is not wired to the API or a worker and has not queried live alerts.
- services/api/app/providers/copernicus_stac.py and apps/web/src/components/copernicus-context.tsx — optional owner-demo-only, bounded live scene-metadata context. It is off by default, has a 15-minute per-process cooldown, and does not create observations, download imagery or enable alerts.
- data/demo/ and data/fixtures/ — documented synthetic/demo material; local mutable data under data/local/ is ignored by Git.
- data/areas/ — provisional, clearly non-authoritative research geography; not an operational forest boundary or LIVE alert filter.
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
| /cases/[id] | apps/web/src/app/cases/[id]/page.tsx, case-workspace.tsx | Human workflow, case history, evidence and review actions in DEMO scope. A missing case does not substitute an unrelated demo case, and an API response must match the requested case ID. |
| /operations | apps/web/src/app/operations/page.tsx | Workflow counts/operations view, not conservation impact metrics. |
| /outcomes | apps/web/src/app/outcomes/page.tsx, outcome-graph.tsx | P0 relational outcome summary; no causal impact claim. |
| /sources | apps/web/src/app/sources/page.tsx | Provider status and an optional owner-demo Copernicus scene lookup; no validated live alert feed. |
| /legal | apps/web/src/app/legal/page.tsx | Human-review/legal source gate; no verified legal corpus is configured. |
| /api/forestproof/* | apps/web/src/app/api/forestproof/[...path]/route.ts | Same-origin proxy to the API in hosted layouts; it is not an authentication layer. |

The command center provides explicit demo observation and case entry points and shows unmeasured environmental outcomes without inventing a count. It and `/operations` load saved synthetic cases through `apps/web/src/lib/use-case-queue.ts` and `api.ts`; an empty or unavailable API does not fall back to unrelated static cases. `/cases/[id]` can record synthetic action and follow-up text before the API allows the corresponding state transitions, and links back to the exact source observation. `apps/web/scripts/smoke-owner.mjs` exercises this browser flow on loopback with synthetic data when a local Chrome/Chromium executable is supplied.

The optional `owner_demo` configuration relies on Caddy's owner authentication and trusted loopback listeners. The web proxy checks the gateway assertion before accessing the API, and the API verifies the distinct service token and expected owner subject. The mode is synthetic only and blocks evidence uploads. LIVE is still disabled.

Shared UI pieces are under apps/web/src/components/; API normalization and HTTP helpers are in apps/web/src/lib/api.ts; synthetic UI fixtures and labels are in apps/web/src/lib/demo.ts.

## FastAPI service surface

The app is declared in services/api/app/main.py; request contracts are in models.py, fixtures in demo_data.py, settings in config.py, persistence/workflow rules in store.py, and source-health placeholder in providers/gfw.py.

- Health, monitoring area, and source status: /api/v1/health, /monitoring-areas, /sources.
- Optional scene context: GET /api/v1/context/copernicus-scenes; only available with owner-demo service authentication and an explicit enable flag, never a forest-alert endpoint.
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
- GFW RADD and integrated alert metadata expose raster-cell fields without provider event IDs; future ingestion must distinguish source cells from ForestProof-derived clusters. See `docs/SATELLITE_INGESTION.md`.
- `data/areas/geta-pfmp-research-envelope.geojson` is a coarse rectangle derived from the KFS PFMP's printed coordinate range. It supports source-coverage research only and is not approved for live alert filtering.
- docs/DATA_SOURCES.md is the source activation ledger. Do not change a product to VERIFIED_ACTIVE without licensing, AOI, request, metadata, health, and verification evidence.
- The owner supplied Global Nature Watch's general terms text on 2026-10-27; API key and attribution requirements are recorded in docs/DATA_SOURCES.md. Service cost, quota and specific attribution details remain unverified.
- docs/LEGAL_CONTEXT_MODEL.md, docs/EVIDENCE_MODEL.md, docs/CASE_WORKFLOW.md, and docs/FOREST_OUTCOME_GRAPH.md define domain behavior.

## Build and verification

The project CI uses Python 3.12 and tests the web with Node 20 for compatibility and supported Node 24:

    cd services/api
    python -m pip install -r requirements-dev.txt
    python -m pytest

    cd apps/web
    npm ci
    npm test
    npm run typecheck
    npm run build

GitHub Actions passed for application commit `71af70f81318ea98e4d1ab20bd52739aa97012c1`, context/onboarding commit `be4402f4f4c44f2f1ca52dc694af185164c3263e`, follow-up context-verification commit `107e31f0b39067e19a47d40496a47282b35c04c5`, and status/map update commit `0078e91f0ce2211863aac2fb393f7b5c5cbc0ada`. The status/map update run also passed both API and web checks: https://github.com/thegodmustwin/forestproof/actions/runs/40217015885. A passing build verifies CI checks only; it does not verify live data, legal sources, auth, or production operations.

The owner reports that the handoff documentation commit `1df38e714fdfbae14294318e0326eadbaeb26af4` also passed API and web checks: https://github.com/thegodmustwin/forestproof/actions/runs/40217118596. Cloud-local setup validation is recorded in `execution/CURRENT_STATUS.md`.

Commit `c6377249b5b5dc587f289e55d9ba7794685503f3` adds the provisional Geta research envelope and offline RADD cell normalization groundwork. It has been pushed to private `main`; its GitHub Actions result is pending verification.

Codex Cloud is the preferred development path; it can install Python and npm dependencies and run these checks without requiring Docker on the owner's laptop. Network access should be limited to package managers unless a verified workflow needs additional hosts. No .env or production secret is in the repository.

On 2026-10-26, the owner reported that publishing the latest saved Cloud environment draft failed. The configuration read shows draft revision 8 based on an existing published version; no publish diagnostics are exposed by the connected tools. The current task still has the checkout, Python 3.12, pinned Node 20, passing API/web checks, local smoke access, and read-only GitHub access. The latest draft and fresh-task restoration are not verified.

On 2026-10-26, draft revision 9 was saved to add only `vps-8071f70a.vps.ovh.net` to custom egress. It requires publication and has not changed the active environment. The shell's HTTPS proxy previously returned 403 CONNECT denied for the host; raw SSH support remains unverified.

## Documentation map

- docs/PROJECT_CONTEXT.md — why the product exists, what is real, decisions, scope, and north star.
- docs/PROJECT_DECISIONS.md — owner choices, superseded deployment docs, and facts still to discover.
- PROJECT_BRAIN.md — short operating model and non-negotiables.
- docs/ARCHITECTURE.md — logical services and trust boundaries.
- docs/DATA_SOURCES.md, docs/SATELLITE_INGESTION.md — candidate data products and activation gates.
- docs/COSTS_AND_OPERATING_BUDGET.md — verified spend, unknown source fees, and approval gates.
- docs/KFS_BOUNDARY_REQUEST_DRAFT.md — unsent request for the official Geta boundary and reuse conditions.
- docs/GEO_DATA_MODEL.md — current/target geospatial records.
- docs/CASE_WORKFLOW.md, docs/EVIDENCE_MODEL.md, docs/LEGAL_CONTEXT_MODEL.md, docs/FOREST_OUTCOME_GRAPH.md — domain rules.
- docs/SECURITY_AND_PRIVACY.md — current controls, gaps, and sensitive-data policy.
- docs/ALPHAZERO_DOCTRINE.md, docs/GOLDEN_ECONOMICS.md, docs/COMMERCIAL_STRATEGY.md, docs/PILOT_PARTNERSHIPS.md, docs/GRANTS_AND_INCENTIVES.md — strategic and business hypotheses, not validated demand.
- docs/DEMO_SCRIPT.md — demonstration path and truthful DEMO labels.
- docs/DEPLOYMENT.md — current Contabo hosting handoff, historical synthetic OVH preview, and unverified live-pilot prerequisites.
- docs/CLOUD_HANDOFF.md and execution/CURRENT_STATUS.md — reported private November 1 OVH rescue archive, recovery limitations and reconciliation guardrails; the archive itself stays off GitHub.
- execution/CURRENT_STATUS.md, execution/NEXT_ACTIONS.md, execution/ROADMAP.md — dated execution state and priorities.
- docs/origin/ — original prompts, retained for history only.

## Explicitly not implemented

Production PostGIS, live record-level satellite alerts, authoritative Aberdare boundaries, legal document verification, real user authentication, organization isolation, protected production evidence storage, offline field sync, notification delivery, PDF dossiers, validated predictive ML, paid customers, and live-pilot deployment remain open. A prior session deployed and verified a synthetic OVH preview; see `execution/CURRENT_STATUS.md` for its limitations.


## 2026-10-28 pilot preparation update

The RADD snapshot store includes an offline comparison of two explicitly saved versions for the same derived cell/date identity. It reports raw source-field differences only; missing rows do not establish retraction, and changed alert dates are not automatically matched. The implementation and tests do not call a provider or enable LIVE. See the dated source and ingestion notes. GitHub main commit 6d552d29b5d3337a56b434010fa41a2f836aa373 passed its API and web CI checks at https://github.com/thegodmustwin/forestproof/actions/runs/40609084867.


## 2026-10-28 supported web runtime

The earlier Next.js 14.2.35 lockfile was outside the supported release lines. The current lockfile uses Next.js 16.4.3 and React 19.2.8, with asynchronous route parameters, a loopback proxy/page smoke check and a dependency audit. The candidate passed CI as recorded in `execution/CURRENT_STATUS.md`; a framework upgrade does not implement owner authentication or enable LIVE. Next.js support policy: https://nextjs.org/support-policy. Relevant advisory: https://github.com/vercel/next.js/security/advisories/GHSA-p3m5-59mp-jv5r.

The web upgrade uses MapLibre GL JS 6.16.0 and tests Node 20 for compatibility and supported Node 24. Run https://github.com/thegodmustwin/forestproof/actions/runs/40617936251 passed API tests, web checks, production dependency audit, and a headless browser map interaction with synthetic fixtures and stubbed tiles. A synthetic preview was deployed later; live production and real provider tiles remain unverified.

The owner-provided OVH screenshot is summarized in docs/DEPLOYMENT.md; it is a point-in-time inventory and not a deployment or firewall verification.

Optional demo Compose host ports are restricted to loopback and checked in CI. Loopback is not owner authentication and Compose remains unsuitable for real evidence or production deployment.

The API separates runtime dependencies in services/api/requirements.txt from test dependencies in services/api/requirements-dev.txt. CI audits the resolved development and runtime requirements; pinned direct dependencies do not constitute a fully pinned transitive production lockfile.

services/api/app/providers/gfw_radd_envelope.py provides a bounded offline candidate parser for WRI's published success envelope; services/api/tests/test_gfw_radd_envelope.py uses synthetic inputs. The deployed API envelope, actual provider data and LIVE ingestion remain unverified.


## 2026-10-28 owner-only gateway candidate

A Caddy configuration under infrastructure/deployment/owner-pilot/ is being tested for a loopback-only owner gateway over the existing authenticated SSH tunnel. It is not installed or running on the OVH VPS. It guards all proxied web paths with a hashed owner credential and rejects cross-origin mutations; the API and web upstream must remain separately bound to VPS loopback. It is not suitable as a public HTTP endpoint. Source access, application authentication semantics, protected storage, backups and production operation remain open.

- `docs/GFW_ACCESS_REQUEST_DRAFT.md` — unsent questions about API access, pricing, attribution, local coverage and retention; no provider has been contacted.

- `docker-compose.preview.yml` and `infrastructure/deployment/family-preview/` — synthetic friends-and-family preview; shared test account, HTTPS gateway, no real evidence or live source.

## 2026-10-29 pilot area and release selection

The owner accepts a provisional wider-region path without waiting indefinitely for an official KFS boundary. The current envelope is still research-only until its assumptions and use are reviewed; it cannot establish that observations are inside Geta Forest. Public RADD metadata also showed an older content date behind the `latest` alias than another listed release. See `docs/DATA_SOURCES.md` and `execution/NEXT_ACTIONS.md` before choosing a source version or enabling any live request.


## 2026-11-05 design and operating-value work

- DESIGN.md defines the field-atlas / evidence-ledger visual direction.
- .agents/skills/ and docs/UI_SKILLS.md provide portable original art-direction, UX interaction and rendered-review skills. Local user-skill copies are installed separately; Cloud uses repository discovery/installation.
- docs/LOW_COST_DATA_AND_VALUE_PLAN.md records lower-cost licensed source candidates and a commercial workflow hypothesis; no feed or paid service is activated.


## 2026-11-06 Cloud handoff

- `docs/CLOUD_HANDOFF.md` is a concise continuation brief covering the project's origin, current limitations, Contabo and GitHub state, historical OVH deployment, design skills, data-cost research and next priorities. Recheck current main and facts before acting.

## 2026-11-11 synthetic RADD receipt ledger

`services/api/app/providers/radd_fixture_receipts.py` stores bounded synthetic fixture receipt metadata and exact-byte hashes, not raw rows, provenance proof, production data, or a live feed. See `docs/RADD_FIXTURE_RECEIPTS.md`.

## Source provenance contract foundation — 2026-11-12

`services/api/app/source_provenance.py` defines a versioned source-neutral contract. Existing observation and case/dossier API responses expose only an identified synthetic fixture projection; mismatched rows fail closed. See `docs/OBSERVATION_PROVENANCE_CONTRACT.md`. This is not live ingestion or owner authentication.


**NASA date follow-up (2026-11-12):** The bounded status/first-detection-date comparison and limitations are recorded in `docs/NASA_DIST_SAMPLE_20261112.md`. It is a research check, not a live feed or official geography.
