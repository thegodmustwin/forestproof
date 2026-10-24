# Next Actions

## Immediate engineering actions

1. Inspect the actual repository stack and preserve unrelated user changes.
2. Add the smallest PostGIS-backed schema for monitored areas, sources, observations, cases, evidence, actions, outcomes, and audit events.
3. Create a deterministic DEMO fixture with an obvious DEMO marker and separate it from LIVE records.
4. Implement validation for geometry, timestamps, source provenance, and idempotency.
5. Implement the first case state transitions and evidence integrity metadata.
6. Build a map/detail view that exposes source, timestamp, resolution, quality flags, and uncertainty.
7. Exercise the complete DEMO workflow with one end-to-end test.

## Live-source gating actions

1. Select one source product that can provide individual observations, not only tiles.
2. Confirm current access, terms, attribution, commercial reuse, rate limits, and AOI coverage from official documentation.
3. Obtain credentials through environment configuration if required; never paste secrets into chat or Git.
4. Run a bounded sample request, persist original identifiers/metadata, and record health/latency.
5. Change status only after validation; label any gaps in the interface.

## Before any pilot or deployment

- Complete tenant boundaries, upload validation, object-access protections, audit logging, backups, and restoration checks.
- Obtain explicit approval before recurring paid services, public deployment, external outreach, notifications, or legally consequential communication.
- Ensure the DEMO does not claim real incidents, legal conclusions, or conservation impact.
