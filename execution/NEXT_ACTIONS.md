# Next Actions

## Immediate: define a credible first pilot

1. Build the initial release for one authenticated owner. Keep all authorization checks server-side; defer multi-organization onboarding.
2. Use `data/areas/geta-pfmp-research-envelope.geojson` now for engineering dry-runs and coarse coverage research. It is a PFMP-text-derived bounding rectangle, not the Geta forest boundary and not approved for LIVE alert filtering.
3. Extend the offline RADD normalizer from one catalog-shaped field map to the verified API response envelope after exact terms/cost and a permitted response sample are established. Confirm field/value semantics, source version, and cell provenance; treat any ForestProof grouping as a derived cluster, never a provider alert ID.
4. Verify GFW's terms, cost, account access, rate limits, local coverage, and retention before making an alert-record query. The Terms page currently returns an outbound tunnel 403 from this environment. Do not infer $0 from CC BY 4.0. If this provider remains blocked, evaluate a no-new-service Sentinel workflow while preserving the distinction between scenes and validated detections.
5. Obtain the official KFS GIS geometry and reuse conditions when available. Replace the research envelope only after checking CRS, topology, area against the 21,644.37 ha PFMP figure, source/version, and use permission.
6. Keep LIVE disabled and fail closed until source terms/cost, AOI permissions, credentials, response shape, persistence, and health checks pass. Then exercise the owner-only observation-to-case-to-follow-up flow against real source data.

## Before pilot or deployment

- Implement authenticated identity, server-side role/tenant checks, protected object storage, upload scanning, retention, rate limits, monitoring, and tested backup/restore before real evidence.
- To test an OVH connection from Cloud, publish saved environment draft revision 9 first; it adds only `vps-8071f70a.vps.ovh.net` to the custom egress list. Then retry reachability. This opens an HTTPS host route only if publication succeeds; it does not supply SSH credentials or prove port 22 is supported. If Cloud cannot use SSH, use OVH Manager's web/KVM console to inspect the server and establish the owner-controlled access method.
- Audit the OVH VPS from the owner account: IP, OS/version, SSH readiness, firewall, backups, DNS/domain/TLS, capacity, and operating cost. Do not ask for passwords or private keys in chat.
- Choose and document a deployment method only after the OVH inventory and production controls are understood. Railway is not the current choice.
- Obtain practitioner feedback and one design partner before expanding billing, enterprise features, or predictive ML.
- Get explicit current approval before recurring paid services, public deployment, external outreach, notifications, or legally consequential communication.
