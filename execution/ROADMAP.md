# ForestProof Roadmap

**Hosting update, 2026-11-10:** Contabo `vmi3711898` is now the target. The laptop reached it via a read-only strict-host-key SSH test. Cloud access, backup transfer and ForestProof deployment are unverified. Preserve other projects and keep RDP private over its existing SSH tunnel. Older OVH entries below are historical.

## Status legend
The [source-status staging path](../tools/source_status/README.md#isolated-staging) now tracks separate check, report, and underlying observation dates. Public publication and recurring release work still depend on area and source rights. The owner case workflow still needs a qualified record-level feed.

The [source-status publication preview](../tools/source_status/README.md) is a local static candidate. Production publication still requires a source and geography decision, rights review, recurring updates, and stale handling. The owner workflow, approved alert feed, and public release remain separate milestones.

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
| 2 | Architecture and source verification | PARTIAL | Architecture and source manifest exist; a PFMP-derived envelope is available for non-operational coverage work. A clearly labeled wider-area pilot may be considered after geometry assumptions, lawful use and live-provider validation; it cannot establish an official forest boundary. |
| 3 | PostGIS database and monitored area | PARTIAL | SQL target exists; API still uses SQLite. The provisional Geta envelope is not the official boundary or an operational AOI. |
| 4 | Typed observation schema | PARTIAL | Pydantic geometry and source metadata are present; production persistence and provider contract need extension. |
| 5 | Deterministic DEMO provider | WORKING | Synthetic fixtures are idempotent and explicitly labeled. |
| 6 | One approved live provider | DOCUMENTED_NOT_TESTED (ALERTS) | Direct GLAD-L recency and RADD display coverage have been measured over the research rectangle. Sentinel-1 footprint metadata confirms acquisition opportunities. Native alert eligibility, usable cadence, approved operating area, source access and terms, and protected runtime storage remain before activation. [Source checks](../docs/DIRECT_SOURCE_EVALUATION.md#radd-baseline-and-radar-acquisitions--2026-11-14) |
| 7 | Observation map and detail | WORKING (DEMO) | Map/detail UI accepts explicitly labelled DEMO records; missing source values are no longer filled from unrelated fixtures. The current display rejects live records and is not a live operational map. |
| 8 | Case and review workflow | WORKING (DEMO) | Dashboard and queue show saved API cases; the web flow records synthetic actions and follow-ups, preserves the correct observation link, and checks that required records exist before advancing. API and browser tests passed locally. |
| 9 | Evidence and integrity | PARTIAL | Local evidence metadata and SHA-256 checks work; production storage, malware scanning, access classes, and retention remain. |
| 10 | Legal context references | PLANNED | No official order/permit corpus or qualified review is configured. |
| 11 | Actions and outcomes | WORKING (DEMO) | Actions, follow-ups, and bounded outcome labels are available; no causal claims. |
| 12 | EvidenceProof dossier | PARTIAL | JSON dossier and hash status exist; PDF output and complete production manifest remain. |
| 13 | Authentication and tenancy | PARTIAL (SYNTHETIC ONLY) | The isolated candidate links one authenticated gateway subject to the review audit trail, with separate service secrets and browser Origin checks. Verify credential lifecycle and isolation on the eventual private live deployment. |
| 14 | End-to-end acceptance | PARTIAL (DEMO) | An isolated browser test exercised observation → case → saved action → saved follow-up → closure through the owner gateway, web app and API. A real-data, protected-storage and deployed-owner acceptance test remains open. |
| 15 | Deployment and external feedback | WORKING (PROTECTED SYNTHETIC PREVIEW) | Contabo serves verified preview release `38881dc` behind HTTPS with shared tester access. The owner-only live pilot still needs person-level identity, a verified feed, separate protected storage and tested off-host recovery. See execution/CURRENT_STATUS.md. |

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

## 2026-11-06 verified launch scope

See `docs/LAUNCH_STRATEGY.md`. Latest main's synthetic workflow and desktop/mobile command center were exercised locally; live mode, live UI contracts, source ingestion and production recovery still require implementation. Account setup is a parallel dependency, not the entire remaining task. The minimum proposed pilot is one owner/region/source and a source-linked review/action/follow-up/dossier loop, with field/personal uploads disabled initially and a tested private storage/restore design. Current OVH reachability is unconfirmed; no new deployment is recorded. Repository skills were copied into this runtime's user directory; automatic discovery and fresh-session persistence remain unverified.


## 2026-10-28 owner-only pilot checkpoint

- WORKING (offline groundwork): immutable synthetic RADD cell/release snapshots and field-level comparison of two saved releases. No missing-row retraction inference.
- PARTIAL / UNVERIFIED: WUR dataset licensing and attribution source documented; local RADD coverage, GFW Data API account access, service cost, quotas, exact attribution mapping, retention, and response shape remain open.
- PLANNED: owner authentication, production storage and tested backups, permitted live ingestion, and a non-disruptive Contabo deployment after the host inventory.

- COMPLETED DEPENDENCY WORK: the lockfile was upgraded from Next.js 14 to Next.js 16.4.3; a local Node 24 build passed and prior candidate CI passed. A framework upgrade does not establish production security.

- PILOT SECURITY GATE: recheck current dependency advisories and the intended owner's browser/map for the production release. Prior candidate CI and dependency audits passed; verify a supported Node runtime on the eventual production host.

- COMPLETED DEPENDENCY WORK: the initial Python dependency audit was addressed, runtime/test dependencies were separated, and candidate CI/audit passed. Recheck advisories for the production release.

- PARTIAL (offline): bounded candidate GFW response envelope parser based on pinned WRI source and synthetic fixtures; no deployed-service response has been validated.

- PARTIAL: a loopback-only owner gateway over an authenticated SSH tunnel is under CI verification; it is not installed on the VPS and does not satisfy live-feed or production-storage gates.


## 2026-11-05 design quality and economic resilience

- PARTIAL: original UI skill set installed locally and packaged in the repository; visual upgrade candidate and rendered desktop/mobile checks added. Test evidence describes the branch, not an OVH release.
- DOCUMENTED_NOT_TESTED: direct GLAD-L and NASA OPERA as alternative alert/vegetation products; no activation or paid dependency. MyGFW API costs remain unverified.
- PLANNED / HYPOTHESIS: validate a one-project review-to-dossier workflow offer with actual practitioners, measured analyst/reporting effort and willingness to pay before billing expansion.
