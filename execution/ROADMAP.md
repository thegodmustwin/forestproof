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
| 1 | Repository and development environment | PARTIAL | The current Cloud task recovered after a readiness failure and can access the checkout and GitHub. Draft revision 10 publication and fresh-task restoration are not verified. The owner also has an OVH remote desktop; its CLI shell and GitHub authentication need follow-up. |
| 2 | Architecture and source verification | PARTIAL | Architecture and source manifest exist; a PFMP-derived research envelope is available for non-operational coverage work; authoritative AOI and live-provider validation remain. |
| 3 | PostGIS database and monitored area | PARTIAL | SQL target exists; API still uses SQLite. The provisional Geta envelope is not the official boundary or an operational AOI. |
| 4 | Typed observation schema | PARTIAL | Pydantic geometry and source metadata are present; production persistence and provider contract need extension. |
| 5 | Deterministic DEMO provider | WORKING | Synthetic fixtures are idempotent and explicitly labeled. |
| 6 | One approved live provider | DOCUMENTED_NOT_TESTED | Offline RADD identity, row normalization and standalone SQLite snapshot groundwork are tested with synthetic rows. General WRI terms were supplied by the owner; attribution details, dataset conditions, cost, credentials, AOI, response envelope, bounded request, health and production persistence remain before activation. |
| 7 | Observation map and detail | WORKING (DEMO) | Map/detail UI accepts explicitly labelled DEMO records; missing source values are no longer filled from unrelated fixtures. The current display rejects live records and is not a live operational map. |
| 8 | Case and review workflow | WORKING (DEMO) | Case state transitions, assignments, and audit history are covered by API tests. The web case screen rejects mismatched API IDs and does not substitute another demo case for an unknown ID. |
| 9 | Evidence and integrity | PARTIAL | Local evidence metadata and SHA-256 checks work; production storage, malware scanning, access classes, and retention remain. |
| 10 | Legal context references | PLANNED | No official order/permit corpus or qualified review is configured. |
| 11 | Actions and outcomes | WORKING (DEMO) | Actions, follow-ups, and bounded outcome labels are available; no causal claims. |
| 12 | EvidenceProof dossier | PARTIAL | JSON dossier and hash status exist; PDF output and complete production manifest remain. |
| 13 | Authentication and tenancy | PLANNED | Demo-only boundary fails closed; real identity and isolation are absent. |
| 14 | End-to-end acceptance | PARTIAL | API tests exercise the core workflow; browser-level end-to-end proof is not recorded. |
| 15 | Deployment and external feedback | DEFERRED | OVH remote desktop access is confirmed. Publishing a reusable Codex environment is not a hosting prerequisite; production still requires server audit, security gates and real-user participation. |

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


## 2026-10-28 owner-only pilot checkpoint

- WORKING (offline groundwork): immutable synthetic RADD cell/release snapshots and field-level comparison of two saved releases. No missing-row retraction inference.
- PARTIAL / UNVERIFIED: WUR dataset licensing and attribution source documented; local RADD coverage, GFW Data API account access, service cost, quotas, exact attribution mapping, retention, and response shape remain open.
- PLANNED: owner authentication, production storage and tested backups, permitted live ingestion, and a non-disruptive OVH deployment after the host inventory.

- PILOT SECURITY GATE: replace the unsupported Next.js 14 runtime with a supported, tested release before exposure.

- PILOT SECURITY GATE: address the MapLibre and PostCSS advisories, use a supported Node runtime, and verify the map in a browser before exposure.

- PILOT SECURITY GATE: resolve the initial Python dependency audit, separate runtime from test dependencies, and verify the upgraded API and its dependency audit before exposure.

- PARTIAL (offline): bounded candidate GFW response envelope parser based on pinned WRI source and synthetic fixtures; no deployed-service response has been validated.

- PARTIAL: a loopback-only owner gateway over an authenticated SSH tunnel is under CI verification; it is not installed on the VPS and does not satisfy live-feed or production-storage gates.
