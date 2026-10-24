# Current Status

**Last updated:** 2026-10-21  
**Milestone:** P0 hosted-beta launch package.

## Truthful snapshot

- Documentation: PARTIAL. Core architecture, source, evidence, workflow, security, economics, and pilot records are defined; live-source activation and deployment runbooks remain incomplete by design.
- DEMO flow: WORKING. Automated tests seed deterministic observations; exercise case creation, assignment, review-state gates, evidence hashing, action, follow-up, dossier generation, and an outcome graph.
- Live data: DOCUMENTED_NOT_TESTED. Candidate GFW, Copernicus, NASA FIRMS, and Kenya Forest Service contexts are recorded; none is declared operational in the project until activation evidence is captured.
- Legal context: PLANNED. No authoritative order, permit, or restriction has been entered or applied.
- Database and application workflow: WORKING locally. The P0 API uses a SQLite development adapter with a PostGIS-aligned target schema supplied for the next adapter milestone. The PostGIS runtime adapter is not implemented.
- Deployment: READY_FOR_PROVIDER_CONNECTION. Production Docker commands, a private API proxy, a persistent-volume configuration guide, and GitHub Actions checks are prepared. No public URL exists yet: the remaining external steps are authentication to the owner's personal GitHub account and Railway account connection.

## Current known constraints

1. Exact Aberdare monitoring-area boundaries must come from an appropriate authoritative or licensed source.
2. A live disturbance feed needs product-specific terms, credentials where required, bounded AOI testing, and provider-health validation.
3. No remote observation can establish illegality or causal conservation impact on its own.
4. Sensitive field/case information needs access controls before handling real material.

## Verification recorded

- API tests: `8 passed` using Python 3.13 on 2026-10-21.
- Web typecheck: passed.
- Web production build: passed (nine routes generated).
- Local API and web readiness: both returned HTTP 200 on loopback.
- Hosted-proxy check: the production Next.js web server proxied `/health` and `/observations` to a private FastAPI endpoint successfully on loopback (HTTP 200 each).
- Browser automation: BLOCKED by a local sandbox helper error; no visual-interaction claim is made from this check.

## Next verification checkpoint

Push the verified P0 package to the owner's personal GitHub account, connect it to Railway, attach the API volume, and record the resulting public web URL. Independently verify a legally usable live source before representing a live monitoring capability.
