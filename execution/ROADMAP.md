# ForestProof Roadmap

## Status legend

- WORKING: implemented and verified at the stated scope.
- PARTIAL: implemented in part; remaining limitations are named.
- PLANNED: designed but not yet implemented.
- BLOCKED: cannot safely proceed without an external dependency or decision.
- DEFERRED: intentionally outside the current milestone.
- DOCUMENTED_NOT_TESTED: documentation exists; operational behaviour is unverified.

## P0 — smallest complete evidence loop

| Order | Milestone | Status | Completion evidence |
| --- | --- | --- | --- |
| 1 | Repository/environment inspection | PARTIAL | Stack, commands, and current state recorded. |
| 2 | Architecture and source verification | PARTIAL | Architecture and source manifest maintained; provider activation pending. |
| 3 | PostGIS database and monitored area | PLANNED | Migrations plus geometry tests. |
| 4 | Typed observation schema | PLANNED | Timestamp/provenance/geometry validation tests. |
| 5 | Deterministic DEMO provider | PLANNED | Repeatable labelled fixture ingestion. |
| 6 | One approved live provider | DOCUMENTED_NOT_TESTED | Source terms, credential, AOI, health, and sample ingest verified. |
| 7 | Observation map and detail | PLANNED | Map click exposes provenance and quality state. |
| 8 | Case and review workflow | PLANNED | Append-only transitions and assignment tests. |
| 9 | Evidence and integrity | PLANNED | Upload validation, SHA-256 metadata, access tests. |
| 10 | Legal context references | PLANNED | Source/time/version references and uncertainty display. |
| 11 | Actions and outcomes | PLANNED | Follow-up and evidence-backed outcome records. |
| 12 | EvidenceProof dossier | PLANNED | Complete report/export test. |
| 13 | Authentication and tenancy | PLANNED | Tenant isolation and access tests. |
| 14 | Primary end-to-end test | PLANNED | Ingest -> map -> case -> evidence -> review -> action -> follow-up -> dossier. |
| 15 | Deployment and external feedback | DEFERRED | Requires explicit approval and partner participation. |

## P1 — only after P0 works

- Multi-sensor corroboration with provenance-aware independence handling.
- Suitable before/after imagery comparison.
- Source-health dashboard and catchment-priority heuristic.
- Improved duplicate/cluster handling and evidence-completeness scoring.
- Field-friendly mobile workflow and follow-up monitoring.

## P2 — only after external validation

- Multi-organization onboarding, billing, subscriptions, API/webhooks, retention plans, and institutional integrations.

## P3 — research and expansion

- Validated predictive prioritization, restoration monitoring, water/catchment analysis, multi-country support, and advanced outcome methods.

No roadmap row is evidence of completion by itself. Update only after implementation and verification.
