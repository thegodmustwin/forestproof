# ForestProof — decision and context ledger

This is the compact record of durable owner choices and important unresolved facts. Keep it current; do not use it to imply an implementation is complete.

## Confirmed owner choices

| Date | Decision | Consequence |
| --- | --- | --- |
| 2026-11-10 | Use the existing Contabo VPS `vmi3711898` as the target for future ForestProof hosting; OVH is the previous host. | Laptop read-only strict-host-key SSH reached that hostname. Preserve existing projects, services and private RDP tunnel; do not use `content-engine-vps` (the old OVH alias). Backup transfer and Cloud access are unverified. |
| 2026-10-29 | Keep moving without waiting indefinitely for an official Geta GIS boundary; the owner accepts a provisional approach. | A future owner-only pilot may monitor an explicitly labeled broader region after the area assumptions, permitted data use, coverage and pilot controls are verified. Do not represent the coarse rectangle as a forest boundary or claim that a pixel lies inside Geta Forest. The current research envelope is not yet activated for LIVE use. |
| 2026-10-26 | Keep momentum while KFS boundary and provider access questions are pending by using the PFMP's published coordinate extent as a provisional Geta research envelope. | Use only for source-coverage research and engineering dry-runs. It is not a forest boundary, not approved for live filtering, and does not settle data reuse, API cost, legal scope, or alert validity. Replace it when authoritative GIS geometry and terms are verified. |
| 2026-10-26 | Use GFW RADD as the lead provider candidate for the first feed adapter; keep GLAD-L as a comparison and defer GFW Integrated Alerts. | This is an engineering priority based on RADD's Sentinel-1 radar, 10 m weekly product, and documented humid-tropical-forest/Africa scope. Validate local coverage, terrain limits, terms, and service cost before any record query or LIVE use; new paid access requires owner approval. |
| 2026-10-25 | Use the owner's personal GitHub account thegodmustwin and private repository thegodmustwin/forestproof; default branch is main. | Keep source private; don't publish or transfer to the university account. |
| 2026-10-25 | Continue development in Codex Cloud to reduce laptop capacity pressure. | Prepare a repository-backed Cloud environment; preserve context in GitHub because desktop chat history is not the project source of truth. |
| 2026-10-25 | Do not make local Docker a prerequisite for the owner's workflow. | Prefer Cloud setup and CI-equivalent Python/npm checks. Docker Compose may remain for optional use. |
| 2026-10-25 | The first production pilot is owner-only and requires a live provider feed. | Build for one authenticated owner first; do not treat a manual-only observation workflow as satisfying the pilot requirement. Verify an appropriate record-level feed before enabling LIVE. |
| 2026-10-25 | Prefer the existing OVH VPS for eventual hosting; its hostname is temporary. | Audit the server before choosing deployment steps. No OVH deployment or SSH readiness is verified. |
| 2026-10-25 | Railway is not the owner's current hosting preference. | Railway guide is historical; do not follow it unless the owner changes the decision. |

## Product decisions and hypotheses

- Build an evidence-and-accountability layer that uses existing observation infrastructure rather than competing first on global satellite coverage.
- Start with the Aberdare water tower / Geta context, while treating the map boundary and any individual disturbance as unverified until a lawful source supports them.
- Prefer a private institutional workflow with a carefully governed public-interest surface. Initial customer hypothesis: an organization already responsible for a forest, watershed, restoration programme, or environmental compliance. This is not validated customer demand.
- The core workflow is observation → evidence/context → human-owned case → authorized action → follow-up → evidence-bounded outcome.
- DEMO-first development is acceptable only when every synthetic item is unmistakably labeled; live providers must never silently fall back to fabricated observations.
- Use a relational/PostGIS architecture when justified; do not adopt a graph database merely because the long-term product asset is called an outcome graph.
- No recurring paid service, public deployment, external outreach, or consequential legal/enforcement communication is authorized merely by inclusion in a roadmap.

## Historical claims requiring fresh verification

The original prompts mention October 2026 court reporting, a reported logging restriction, and an expected Geta Forest visit. They are preserved in docs/origin/ as historical prompt content. No official order, case number, operative text, current scope, amendment, or qualified legal review is present in the current implementation. Do not display or apply the reported restriction as current law without independent authoritative verification.

The prompts also discuss candidate providers, grants, customer types, and market scores. These are research hypotheses from the source prompts, not validated feed access, grant eligibility, partnership, pricing, or commercial traction. See the current evidence in the respective domain docs.

## Operational facts still to establish

- Contabo `vmi3711898`: on 2026-11-10 a read-only SSH test from the owner's laptop succeeded with its existing key and strict host-key checking; the host reported Ubuntu 24.04.5 LTS and RDP was listening on loopback. Cloud access, current service/port inventory, firewall, deployment, and transfer and restore verification of the owner's reported laptop backup remain open. The desktop uses `ubuntu` and an SSH tunnel according to the owner; keep RDP private, preserve other services, and never use `content-engine-vps` for Contabo.

- OVH service details: a prior session inspected the server and verified HTTPS for the deployed synthetic preview. Current access, server state, backup/restore and the production deployment path remain to be established.
- Codex Cloud: environment setup and CI-equivalent checks completed in the onboarding task; saved install/start instructions are present. Fresh-task restoration is not independently verified, and a narrow egress allowlist for public source documentation awaits review/publication.
- Data: a lawfully usable and accurately labeled area, one suitable record-level source, product license and attribution, latency/coverage, successful bounded request and provenance. A PFMP-derived provisional envelope supports non-operational research today; a wider-area pilot can be considered without asserting an official forest boundary once its remaining gates pass.
- GFW access: the owner is unsure whether an approved project API account exists. Do not request or store a key until terms and cost are reviewed; if required, use environment settings rather than chat.
- Product validation: first legitimate practitioner interview, design partner, pilot criteria, and willingness to pay.
- Production security: authentication, role boundaries, tenant isolation, object-store access, retention, backup and restore, monitoring, incident handling.

Do not put server passwords, SSH private keys, personal evidence, or access tokens in this ledger or in Git.

## Decision entry template

    Date:
    Decision:
    Reason / evidence:
    Alternatives:
    Consequences:
    Revisit when:



## 2026-10-28 owner direction

Historical direction, superseded on 2026-11-10 by the Contabo target: continue toward an owner-only pilot with a verified live feed. The owner reports Ubuntu 24.04 and working remote desktop access. Preserve existing VPS services and remote desktop; inventory the host before proposing changes. Codex Cloud environment publishing is not a prerequisite for OVH. Check any new paid service cost with the owner, and never request passwords, API keys, or private keys in chat. This direction authorizes pilot preparation; the source, authentication, backup, and host-readiness gates still require evidence.


### Owner-provided OVH terminal screenshot, 2026-10-28

The owner showed a terminal on host vps-8071f70a reporting Ubuntu 24.04.4 LTS. The screenshot's TCP listener list shows port 22 on IPv4/IPv6 wildcard addresses, port 3389 bound to 127.0.0.1, and port 3350 bound to IPv6 loopback. SSH, xrdp, xrdp-sesman, Docker and containerd services were running. Ports 80 and 443 were not shown as TCP listeners in that snapshot. This does not establish firewall reachability, TLS, UDP listeners, container inventory, backup state, SSH authentication, service ownership, or future port availability. Preserve the existing remote desktop, SSH and container services.


### Read-only SSH inventory, 2026-10-28

The agent verified the ED25519 host fingerprint against the owner's VPS terminal screenshot and connected as ubuntu using existing local SSH credentials; no password or key was shared. Ubuntu reported Python 3.12.3 and Git 2.43.0. Root filesystem had approximately 90 GB available. The UFW status reported active, default deny incoming, with a rate-limited SSH rule; the screenshot showed xrdp listening on loopback. Docker and containerd were running, and sudo docker ps -a returned no containers at that moment. Node, npm, GitHub CLI, Caddy, nginx and Apache were not found on the account's PATH. No application backup was verified by the timer inventory; other backup mechanisms and OVH snapshots remain unknown. Firewall reachability, ports, running services and containers can change and must be rechecked before changes. This was read-only; no service, firewall or VPS software was changed.


## 2026-10-28 time-sensitive shared synthetic preview

The owner requested a shareable friends-and-family test today. A password-protected synthetic preview was deployed to the existing OVH hostname to support feedback while the live feed, authorized AOI, production storage, backups and identity controls remain open. This does not change the decision that an owner-only live pilot requires verified data and protected production operation, and it is not a claim of production readiness. No paid service or provider activation was added.
