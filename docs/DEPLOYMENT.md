# Deployment

## Current status and owner preference

**No public deployment exists.** The code is in the private GitHub repo and CI passes, but the public website has not been launched.

The owner prefers an existing OVH VPS for eventual hosting and does not want local Docker to be required for development. The temporary hostname recorded in prior project discussion is vps-8071f70a.vps.ovh.net. The following are not yet verified here: current public IP, OS/version, SSH readiness, firewall, DNS/domain, TLS, backup configuration, server capacity, and deployed software.

Railway was an earlier deployment proposal. It is superseded by the owner's OVH preference; RAILWAY_LAUNCH.md is retained only as historical context and is not the current deployment plan. Do not create a Railway project or deploy there unless the owner changes the decision.

## Development without local Docker

Codex Cloud is the preferred development environment. It should use the same checks as GitHub Actions:

    Python 3.12
    Node 20
    python -m pip install -r services/api/requirements.txt
    cd services/api && python -m pytest
    cd apps/web && npm ci && npm run typecheck && npm run build

Docker Compose remains available for optional local/service experiments. It is not required for Cloud setup or the current CI checks.

## OVH pre-deployment audit

Before choosing a server runtime or changing the VPS, establish:

1. Exact OVH service/product, current public IP, region, CPU/RAM/disk, and operating-system release.
2. Whether SSH is enabled, the correct account/user, key-based access readiness, and firewall rules. Do not place private keys or passwords in Git or chat.
3. Domain ownership and DNS plan, TLS certificate path, ingress ports, and whether the API will remain private behind the web app.
4. Backup scope, schedule, retention, restore test, logs/monitoring, update process, and incident access.
5. Runtime choice and cost. Docker on the VPS is not decided by the fact that Dockerfiles exist in the repository.
6. Whether the intended public launch is a DEMO-only preview or a real institutional service. The current application has no real authentication, live source feed, or production evidence controls.

Record the verified inventory and chosen architecture in a dated decision/status entry before deployment.

## Production gates

Before real users or real case material:

- Replace or productionize the SQLite adapter; test PostgreSQL/PostGIS migrations and backup/restore.
- Implement identity, roles, authorization, tenant isolation, rate limits, protected evidence storage, upload scanning, retention, and audit controls.
- Enable only sources whose licensing, attribution, access, AOI coverage, metadata, and operational health are verified.
- Keep synthetic records visibly distinct from genuine records; never silently fall back from a failed live source to invented observations.
- Verify health, HTTPS, API exposure, secrets, backups, restore, and the actual user workflow after deployment.

## Deployment evidence

Before marking deployment WORKING, record the host/runtime, release/commit, migration result, backup/restore test, source health, authenticated user-journey test, known limitations, responsible operator, date, and public URL if applicable. A passing local proxy check or GitHub CI run is not production deployment evidence.
