# ForestProof Roadmap

## Status legend

- WORKING: implemented and verified at the stated scope.
- PARTIAL: implemented in part; limitations are named.
- PLANNED: designed but not yet implemented.
- BLOCKED: cannot safely proceed without an external dependency or decision.
- DEFERRED: intentionally outside the current milestone.
- DOCUMENTED_NOT_TESTED: documentation exists; operational behaviour is unverified.

## P0 — smallest complete evidence loop

| Order | Milestone | Status | Completion evidence / remaining work |
| --- | --- | --- | --- |
| 1 | Repository and development environment | PARTIAL | An existing published base version and saved setup/start instructions exist. Publishing the latest saved draft revision 8 failed in the UI. Current-task checks pass with Python 3.12.14, Node 20.20.2, 24 API tests, web typecheck/build, API/web/proxy smoke tests, and read-only GitHub access; the latest draft and fresh-task restoration are not verified. |
| 2 | Architecture and source verification | PARTIAL | Architecture and source manifest exist; a PFMP-derived research envelope is available for non-operational coverage work; authoritative AOI and live-provider validation remain. |
| 3 | PostGIS database and monitored area | PARTIAL | SQL target exists; API still uses SQLite. The provisional Geta envelope is not the official boundary or an operational AOI. |
| 4 | Typed observation schema | PARTIAL | Pydantic geometry and source metadata are present; production persistence and provider contract need extension. |
| 5 | Deterministic DEMO provider | WORKING | Synthetic fixtures are idempotent and explicitly labeled. |
| 6 | One approved live provider | DOCUMENTED_NOT_TESTED | Offline RADD cell identity/row normalization is prepared; the actual response envelope, verified terms/cost, credentials, AOI, bounded request, health, and persistence remain before activation. |
| 7 | Observation map and detail | WORKING (DEMO) | Map/detail UI works against DEMO records; not a live operational map. |
| 8 | Case and review workflow | WORKING (DEMO) | Case state transitions, assignments, and audit history are covered by API tests. |
| 9 | Evidence and integrity | PARTIAL | Local evidence metadata and SHA-256 checks work; production storage, malware scanning, access classes, and retention remain. |
| 10 | Legal context references | PLANNED | No official order/permit corpus or qualified review is configured. |
| 11 | Actions and outcomes | WORKING (DEMO) | Actions, follow-ups, and bounded outcome labels are available; no causal claims. |
| 12 | EvidenceProof dossier | PARTIAL | JSON dossier and hash status exist; PDF output and complete production manifest remain. |
| 13 | Authentication and tenancy | PLANNED | Demo-only boundary fails closed; real identity and isolation are absent. |
| 14 | End-to-end acceptance | PARTIAL | API tests exercise the core workflow; browser-level end-to-end proof is not recorded. |
| 15 | Deployment and external feedback | DEFERRED | Codex Cloud setup comes first; production requires OVH audit/security gates and real-user participation. |

## P1 — only after P0 evidence warrants it

- Multi-sensor corroboration with provenance-aware independence handling.
- Suitable before/after imagery comparison.
- Source-health dashboard and transparent catchment-priority heuristic.
- Improved duplicate/cluster handling and evidence-completeness scoring.
- Field-friendly mobile workflow and follow-up monitoring.

## P2 — only after external validation

- Multi-organization onboarding, billing, subscriptions, API/webhooks, retention plans, and institutional integrations.

## P3 — research and expansion

- Validated predictive prioritization, restoration monitoring, water/catchment analysis, multi-country support, and advanced outcome methods.

No roadmap row is evidence of completion by itself. Update statuses only after implementation and verification.
