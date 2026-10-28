# Deployment

## Current status and owner preference

**No public deployment exists.** The code is in the private GitHub repo and CI passes, but the public website has not been launched.

The owner prefers an existing OVH VPS for eventual hosting and does not want local Docker to be required for development. The temporary hostname recorded in prior project discussion is vps-8071f70a.vps.ovh.net. The owner reports Ubuntu 24.04 and working remote desktop access; earlier owner-supplied terminal output recorded Ubuntu 24.04.4 LTS and hardware capacity. The current public IP, SSH readiness, firewall, DNS/domain, TLS, backup configuration, existing services, and deployment path still require independent inspection.

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


## Read-only OVH inventory for an owner-only pilot

Inspect the VPS before selecting ports or installing anything. From the owner's existing remote desktop terminal, the following commands show the hostname, OS, root disk space, listening TCP ports, and running system services:

    hostname
    cat /etc/os-release
    df -h /
    ss -lnt
    systemctl list-units --type=service --state=running --no-pager --no-legend

These commands are read-only and do not display passwords, API keys, or private keys. Service names and addresses may still be operationally sensitive; review output before sharing. Record occupied ports and services, remote-desktop and SSH recovery paths, host-level firewall and backups before proposing a release. Do not change firewall rules, ports, existing services or remote-desktop access during this inventory.


### Owner-provided OVH terminal screenshot, 2026-10-28

The owner showed a terminal on host vps-8071f70a reporting Ubuntu 24.04.4 LTS. The screenshot's TCP listener list shows port 22 on IPv4/IPv6 wildcard addresses, port 3389 bound to 127.0.0.1, and port 3350 bound to IPv6 loopback. SSH, xrdp, xrdp-sesman, Docker and containerd services were running. Ports 80 and 443 were not shown as TCP listeners in that snapshot. This does not establish firewall reachability, TLS, UDP listeners, container inventory, backup state, SSH authentication, service ownership, or future port availability. Preserve the existing remote desktop, SSH and container services.

The optional Compose file is development-only. Its published ports are restricted to loopback, but the DEMO API still has no owner authentication; this is not a production deployment recipe.
