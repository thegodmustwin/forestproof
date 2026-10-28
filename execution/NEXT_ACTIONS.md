# Next Actions

## Immediate: define a credible first pilot

1. Build the initial release for one authenticated owner. Keep all authorization checks server-side; defer multi-organization onboarding.
2. Use `data/areas/geta-pfmp-research-envelope.geojson` now for engineering dry-runs and coarse coverage research. It is a PFMP-text-derived bounding rectangle, not the Geta forest boundary and not approved for LIVE alert filtering.
3. Extend the offline RADD normalizer and snapshot groundwork to the verified API response envelope after exact terms/cost and a permitted response sample are established. Confirm field/value semantics, source version, and cell provenance; treat any ForestProof grouping as a derived cluster, never a provider alert ID.
4. Follow up on the owner-supplied Global Nature Watch general terms: verify the linked API attribution requirements, dataset-specific conditions, cost, account access, rate limits, local coverage, and retention before making an alert-record query. The legacy terms URL redirects to `globalnaturewatch.org`, which remains blocked from this workspace, though the owner supplied its text. Do not infer $0 from CC BY 4.0. If this provider remains blocked, evaluate a no-new-service Sentinel workflow while preserving the distinction between scenes and validated detections.
5. Obtain the official KFS GIS geometry and reuse conditions when available. Replace the research envelope only after checking CRS, topology, area against the 21,644.37 ha PFMP figure, source/version, and use permission.
6. Keep LIVE disabled and fail closed until source terms/cost, AOI permissions, credentials, response shape, persistence, and health checks pass. Then exercise the owner-only observation-to-case-to-follow-up flow against real source data.

## Before pilot or deployment

- Implement authenticated identity, server-side role/tenant checks, protected object storage, upload scanning, retention, rate limits, monitoring, and tested backup/restore before real evidence.
- Continue development in the working Cloud task while available, preserving work in source control; fresh-task restoration is not verified. The failed environment publication is not an OVH hosting prerequisite.
- The owner can reach the OVH VPS through remote desktop. Audit its SSH access, firewall, backups, DNS/domain/TLS, runtime and operating cost before deployment. Direct access from Cloud and GitHub authentication on the VPS are unverified; do not request passwords or private keys in chat.
- Choose and document a deployment method only after the OVH inventory and production controls are understood. Railway is not the current choice.
- Obtain practitioner feedback and one design partner before expanding billing, enterprise features, or predictive ML.
- Get explicit current approval before recurring paid services, public deployment, external outreach, notifications, or legally consequential communication.


## 2026-10-28 immediate pilot work

1. Obtain a read-only VPS inventory from the existing remote desktop, including listening ports and running services, before selecting deployment ports or changing anything. Keep remote desktop and existing services available.
2. Implement and verify owner-only authentication and a private API boundary, production storage and a restore-tested off-host backup plan. The existing DEMO path is not suitable for real evidence.
3. Verify RADD's actual coverage over a lawfully reusable area, provider account/access, API pricing and quota, exact attribution and retention, then test a bounded response before wiring a live adapter. The provisional rectangle remains research-only.
4. Integrate release comparisons only after the actual response and completeness semantics are established; missing rows alone are not retractions.
5. Keep the existing VPS and recurring costs unchanged until the host audit and any new cost approval are complete. Codex Cloud publishing is not a prerequisite for OVH.

Before exposure, verify the exact supported web release and committed lockfile through CI, review dependency advisories, and exercise the intended owner workflow.

Use a currently supported Node.js runtime for an OVH deployment; Node 20 remains a compatibility check only. A headless browser check covers synthetic markers and stubbed tiles; verify the intended owner's browser and permitted provider tiles before deployment.

The owner supplied a read-only VPS screenshot on 2026-10-28: inspect Docker containers, firewall, backup status, DNS/TLS and authentication before deployment. Preserve SSH and loopback xrdp.


The verified read-only VPS inventory found UFW active with only an SSH rule, no containers listed at that moment, and no Node/npm in PATH. Recheck before installation; preserve SSH, xrdp, Docker and firewall rules. Verify a real backup/restore and domain/TLS before deployment. The API dependency upgrade and audit must pass before any exposure.

Validate the offline GFW envelope parser against a permitted, bounded RADD response only after API pricing, terms, account access and a suitable research area are established. Keep the provider disabled until the remaining pilot gates pass.

Validate the owner-only SSH-tunnel gateway candidate on an isolated runner, then plan host-specific ports, private secrets, API binding and recovery before installing or starting it on OVH.
