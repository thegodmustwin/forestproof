# Deployment

## Living Atlas hosting — 19 November 2026

The existing Contabo host serves the public homepage and aggregate pass explorer through the dedicated loopback visibility service. The protected Next.js web container has the Living Atlas interface and continues using the existing demo API and volume. See [current release verification](../execution/CURRENT_STATUS.md#living-atlas-release--19-november-2026) for exact running pins and checks, and the [visibility runbook](../infrastructure/deployment/sentinel-visibility/README.md) for service operation and root-context web builds. Those records supersede the older dated deployment descriptions below. The synthetic preview retains shared tester access; genuine alerts and production owner access remain unfinished.

## Current status and owner preference

**Public Sentinel-2 visibility (2026-11-15):** [`/visibility`](https://vmi3711898.contaboserver.net/visibility) serves the owner-approved aggregate view of the provisional Geta research area. The dedicated loopback origin and twice-daily check are separate from the password-protected Contabo tester app. The verified release and rollback procedure are recorded in the [visibility runbook](../infrastructure/deployment/sentinel-visibility/README.md) and [current status](../execution/CURRENT_STATUS.md#public-geta-satellite-visibility--2026-11-15).

**Verified Contabo synthetic preview release (2026-11-13):** The protected preview at https://vmi3711898.contaboserver.net/ serves pinned source `38881dc79f04de9d21997fe85dea8712ef78e91d` through the existing HTTPS gateway. The API/web update kept the named demo SQLite volume and gateway; a private local SQLite snapshot and separate restore passed integrity checks. External TLS, anonymous denial, authenticated DEMO health/source labels, gateway upload/cross-origin denial and direct API upload denial were verified. SSH, xrdp, MariaDB and PHP-FPM remained active; RDP remained on loopback. See [the exact release record](../execution/CURRENT_STATUS.md). This is synthetic-only shared tester access, not person-level owner authentication, a live feed, off-host production recovery or a public live launch. The deployed browser was not visually inspected. Do not submit real evidence or personal data.

**Earlier hosting update (2026-11-10):** The owner has selected Contabo `vmi3711898` (Ubuntu 24.04.5 LTS verified by read-only SSH) for next-stage hosting. A read-only SSH test using the laptop's existing key and strict host-key checking reached `vmi3711898` on 2026-11-10. This confirms laptop connectivity, not Codex Cloud access or deployment readiness. The owner reports the private ForestProof backup is on the laptop; transfer to Contabo has not been completed or verified. `content-engine-vps` names the old OVH server, not Contabo. A read-only listener check found RDP on loopback; keep it private over the existing SSH tunnel and preserve existing services, projects and recovery access. Do not reinstall the server. Cloud tasks must not assume access to Windows files or SSH keys; arrange a separately configured secure connection if needed. Never put passwords, passphrases or private keys in chat or Git.

The remaining dated OVH inventory and deployment records are historical. They do not establish Contabo's ports, software, firewall or backup state. The verified Contabo preview release is recorded above.

**Historical OVH preview:** A password-protected synthetic preview was deployed and verified on 2026-10-28; its current availability is unconfirmed. No live-production pilot has been verified. The later dated deployment record below describes the historical preview. The latest design is in private GitHub main and has not been verified on OVH. See [the launch assessment](LAUNCH_STRATEGY.md) for the current release sequence.

Historically, the owner preferred an existing OVH VPS for hosting and does not want local Docker to be required for development. The temporary hostname recorded in prior project discussion is vps-8071f70a.vps.ovh.net. The owner reports Ubuntu 24.04 and working remote desktop access; earlier owner-supplied terminal output recorded Ubuntu 24.04.4 LTS and hardware capacity. The current public IP, SSH readiness, firewall, DNS/domain, TLS, backup configuration, existing services, and deployment path still require independent inspection.

Railway was an earlier deployment proposal. It is superseded by the owner's current Contabo preference; RAILWAY_LAUNCH.md is retained only as historical context and is not the current deployment plan. Do not create a Railway project or deploy there unless the owner changes the decision.

## Development without local Docker

Codex Cloud is the preferred development environment. It should use the same checks as GitHub Actions:

    Python 3.12
    Node 20
    python -m pip install -r services/api/requirements-dev.txt
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


### Read-only SSH inventory, 2026-10-28

The agent verified the ED25519 host fingerprint against the owner's VPS terminal screenshot and connected as ubuntu using existing local SSH credentials; no password or key was shared. Ubuntu reported Python 3.12.3 and Git 2.43.0. Root filesystem had approximately 90 GB available. The UFW status reported active, default deny incoming, with a rate-limited SSH rule; the screenshot showed xrdp listening on loopback. Docker and containerd were running, and sudo docker ps -a returned no containers at that moment. Node, npm, GitHub CLI, Caddy, nginx and Apache were not found on the account's PATH. No application backup was verified by the timer inventory; other backup mechanisms and OVH snapshots remain unknown. Firewall reachability, ports, running services and containers can change and must be rechecked before changes. This was read-only; no service, firewall or VPS software was changed.

Use a supported Node.js LTS runtime, such as Node 24, for any eventual production runtime. Installing a runtime, opening firewall ports, enabling a reverse proxy, or creating a backup requires a host-specific plan and verification first. The optional development web container uses Node 24 and is not a production deployment by itself.


## 2026-10-28 owner-only gateway candidate

A Caddy configuration under infrastructure/deployment/owner-pilot/ is being tested for a loopback-only owner gateway over the existing authenticated SSH tunnel. It is not installed or running on the OVH VPS. It guards all proxied web paths with a hashed owner credential and rejects cross-origin mutations; the API and web upstream must remain separately bound to VPS loopback. It is not suitable as a public HTTP endpoint. Source access, application authentication semantics, protected storage, backups and production operation remain open.


## 2026-10-28 password-protected synthetic friends-and-family preview

The synthetic preview was initially verified at https://vps-8071f70a.vps.ovh.net/ on 2026-10-28; its current availability is unconfirmed. Its recorded configuration uses a Caddy HTTPS gateway with a shared tester credential, the web app on 127.0.0.1:13000, and an API with no host-published port. The demo database is shared, not private per tester, and is not suitable for personal data or real evidence. The gateway blocks evidence uploads. The owner can retrieve the password directly on the VPS from /home/ubuntu/forestproof-preview-20261028/private/preview-password; it must not be pasted into chat or committed. User name: tester. No live provider records or official Geta boundary are configured.

The host has dedicated preview containers and volumes, a UFW allow rule for TCP 80 for certificates and limit rule for TCP 443, while prior SSH/xrdp services remain in place. Do not stop or remove unrelated containers or alter SSH/xrdp. TLS, unauthenticated 401, authenticated demo health and cross-origin/upload blocks passed at initial deployment; direct API port 8000 timed out from an external check. The source is the family-preview branch/PR; deployment is not evidence that it is a production live system. Testers share the same demo state; production backups, restore, audit attribution and per-user isolation remain unverified.
