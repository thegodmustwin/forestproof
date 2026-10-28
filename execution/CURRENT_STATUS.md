# Current Status

**Last updated:** 2026-10-28
**Milestone:** private GitHub source and Codex Cloud development environment established; production gates remain.

## Truthful snapshot

| Area | Status | Evidence / limitation |
| --- | --- | --- |
| GitHub source control | WORKING | Private repo thegodmustwin/forestproof, default branch main. The provisional research envelope and offline RADD normalization are in commit `c6377249b5b5dc587f289e55d9ba7794685503f3`; a status correction followed in `8bf1f02`. The app still does not ingest or display live records. |
| GitHub CI | WORKING | Main commit `6d552d29b5d3337a56b434010fa41a2f836aa373` passed API and web checks: https://github.com/thegodmustwin/forestproof/actions/runs/40609084867. |
| DEMO vertical slice | WORKING | Synthetic observation → case → transition/assignment → evidence hash → action/follow-up → JSON dossier/outcome graph is implemented and covered by API checks. |
| Live data | DOCUMENTED_NOT_TESTED | GFW, Copernicus, NASA FIRMS, and KFS remain candidates. No record-level live feed is active or represented as validated. |
| Pilot geography | PROVISIONAL RESEARCH ENVELOPE | `data/areas/geta-pfmp-research-envelope.geojson` converts the PFMP's published location range to a coarse rectangle for research and dry-runs. It is not an authoritative Geta boundary and is not approved for live alert filtering. |
| Lead feed engineering target | RADD CANDIDATE | Direct GFW RADD is the first adapter target; GLAD-L remains a comparator. Offline normalization and local snapshot persistence accept synthetic rows only in tests. Local coverage, terrain performance, exact response shape, service terms, and cost remain unverified. No live records queried or feed activated. |
| Legal context | PLANNED | No verified court order, permit, restriction, or qualified human legal review is loaded. |
| Persistence | PARTIAL | SQLite is the DEMO development adapter. PostGIS SQL exists as a target; production runtime is not connected to it. |
| Authentication and tenancy | PLANNED | DEMO is constrained to one seeded organization. Non-demo requests fail closed. No real identity or multi-tenant operation. |
| Codex Cloud | CURRENT TASK WORKS; PUBLICATION UNCONFIRMED | After a readiness timeout, this task's checkout and Git read recovered on 2026-10-27. Saved draft revision 10 has not been confirmed published. The user captured an approval operation reporting RUNNING while the UI showed a publish error; the server-side cause remains unknown. Fresh-task restoration is not verified. |
| OVH access | REMOTE DESKTOP WORKS; DEPLOYMENT PATH UNVERIFIED | The owner supplied terminal output from `vps-8071f70a`: Ubuntu 24.04.4 LTS, 6 CPUs, 11 GiB RAM and 90 GB root-disk free at that time. Codex CLI is installed, but the owner's HTTPS Git read could not authenticate. Direct access from this Cloud task, firewall, backups, TLS and deployment readiness remain unverified. |
| Production deployment | NOT DEPLOYED | No public website or service has been deployed. The existing OVH account is paid according to the owner, but the VPS has not been accessed or audited. |
| Data-source cost | UNKNOWN / NO FEED ACTIVE | GFW dataset metadata reports CC BY 4.0. The owner supplied general Global Nature Watch terms requiring account keys and attribution, but API pricing, quotas, exact attribution requirements and dataset-specific conditions remain unverified. No authenticated alert query or paid data service has been used. See `docs/COSTS_AND_OPERATING_BUDGET.md`. |

## Constraints and non-claims

1. The Aberdare map area is illustrative, not an official licensed boundary.
2. DEMO observations, cases, dates, coordinates, confidence-like values, and evidence are synthetic; they are not current Kenyan incidents.
3. A remote-sensing signal cannot establish cause, authorization, illegality, or causal conservation impact by itself.
4. The original prompts mention October 2026 court reporting. No operative official order or current legal status is in the application; verify before use.
5. Real field or personal evidence must not enter the current unauthenticated demo system.
6. The old Railway guide is historical; OVH is the owner's stated preference. No website has been deployed.

## Verification evidence

- On 2026-10-28 the demo case screen was changed to wait for the requested API case or an exact matching local fixture. Missing cases no longer fall back to a different demonstration case; API responses with missing or mismatched case IDs are rejected. Seven web tests, TypeScript and the production web build passed locally. This is a demo correctness fix, not owner authentication or production deployment.
- On 2026-10-27 the owner supplied copied Global Nature Watch Terms of Service text from the redirected legacy GFW terms page. It requires account API keys and attribution and refers to dataset-specific licenses. It contains separate Pro eligibility criteria, no API price/quota, and a $100 liability cap that is not a price. The owner-supplied text and its hash are documented in `docs/DATA_SOURCES.md`; the linked attribution requirements could not be fetched through this workspace. No account or API key was created and no live alert records were queried.
- On 2026-10-27 a standalone RADD snapshot store was added and verified against synthetic rows. It preserves canonical source fields, a hash, cell/date identity, source release and receipt time; handles identical replays; keeps releases separate; and rolls back a batch when an existing cell/release has conflicting fields. The full API suite passes 28 tests. The store is not wired to live ingestion or production storage.
- On 2026-10-27 the public GFW OpenAPI was retrieved again. The legacy terms URL returned HTTP 301 to `https://globalnaturewatch.org/terms`, whose host is blocked by the current workspace proxy. This explains the observed redirect failure but not the terms or API cost. No alert records were requested.
- On 2026-10-27 the web client was changed to reject records without an explicit DEMO_DATA flag, refuse records without their own valid point and ID, and represent absent source fields and scores as unavailable rather than borrowing synthetic fixtures. Case-event timestamps no longer fall back to the observation ingestion time. Four new web checks, TypeScript, and the production web build passed locally. This does not add live display, production authentication, or deployment.
- On 2026-10-27 the owner's OVH remote desktop terminal reported the server inventory above, Git 2.43.0 and Codex CLI 0.163.0; Node and npm were absent from its PATH. An HTTPS Git read without interactive authentication failed. This is user-provided terminal evidence, not proof of a deployment or direct agent access.
- Local API tests: 8 passed with Python 3.13 on 2026-10-21.
- Local web typecheck: passed on 2026-10-21.
- Local web production build: passed and generated nine routes on 2026-10-21.
- Hosted-proxy topology check: web proxy returned HTTP 200 for API health and observations on loopback on 2026-10-21; this was not a public deployment.
- GitHub Actions for initial app commit `71af70f81318ea98e4d1ab20bd52739aa97012c1`: API and web jobs passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40185388840.
- GitHub Actions for context/onboarding commit `be4402f4f4c44f2f1ca52dc694af185164c3263e`: API tests and web checks passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40216435071.
- GitHub Actions for follow-up context-verification commit `107e31f0b39067e19a47d40496a47282b35c04c5`: API tests and web checks passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40216705267.
- GitHub Actions for status/map update commit `0078e91f0ce2211863aac2fb393f7b5c5cbc0ada`: API tests and web checks passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40217015885.
- GitHub Actions for handoff commit `1df38e714fdfbae14294318e0326eadbaeb26af4`: API and web checks passed according to the owner; https://github.com/thegodmustwin/forestproof/actions/runs/40217118596.
- Cloud setup validation on 2026-10-25 at app commit `71af70f81318ea98e4d1ab20bd52739aa97012c1` (project context at `1df38e714fdfbae14294318e0326eadbaeb26af4`): 8 API tests passed; web typecheck and production build passed; API health/observations, web home page, and same-origin API proxy smoke checks passed. No application files changed during setup.
- Cloud environment investigation on 2026-10-26: the owner screenshot shows “Couldn't publish environment”; config read confirms a saved revision 8 draft based on an existing published version. No publish diagnostics are available through the connected tools. In the current task, Python 3.12.14 and pinned Node 20.20.2 are present; 24 API tests, web typecheck/build, API health/observations, web home, and same-origin proxy pass. Read-only GitHub `ls-remote origin HEAD` succeeds. DNS lookups fail for github.com, GFW, and OVH via the container's direct resolver; the saved custom egress list has no OVH host, and no SSH identity is available.
- On 2026-10-26, the research envelope, RADD normalizer, tests, and related status/source documentation were committed as `c6377249b5b5dc587f289e55d9ba7794685503f3` and pushed to private `main`. This preserves the work separately from the unpublished Cloud environment draft. GitHub Actions for this commit have not yet been checked.
- On 2026-10-26, Cloud environment draft revision 9 was saved with only the OVH VPS hostname added to the existing custom egress hosts. The tool confirmed `requires_publish: true`; this does not apply the change. The current running task still cannot reach OVH through the proxy, and raw SSH support remains unverified.
- Public read-only checks on 2026-10-26 succeeded for the GFW API catalog/OpenAPI, Copernicus STAC catalog, and KFS public Geta plan. GFW integrated alerts are the strongest current feed candidate: the catalog lists daily v20261026 and CC BY 4.0 metadata, with API query requiring API key/OAuth; the owner is unsure whether project access exists. Component coverage differs (GLAD-L and RADD may cover Geta; GLAD-S2 is listed for South America only). No alert records were queried; exact local coverage, API terms/cost, AOI geometry, and production access remain unverified. KFS exposes the 2026–2031 Geta plan as a PDF, but no machine-readable boundary surfaced in limited public page/media/API searches. The owner published the GFW source-host egress settings; the Terms page still fails with an outbound tunnel 403.
- Additional GFW review on 2026-10-26: the official product page links to GFW Terms of Service. OpenAPI/catalog do not state API fees or rate limits; the CC BY 4.0 data label does not settle service costs. A generic point/zoom features route appears unauthenticated in the API schema, but its usefulness and terms for integrated alert records have not been verified. No records were queried. Cost stays UNKNOWN until provider terms/quotas are confirmed.
- Additional product-schema review on 2026-10-26: public metadata lists RADD (`v20261018`, Sentinel-1, 10 m, weekly, humid tropical forest coverage in sub-Saharan Africa) and GLAD-L (`v20261025`, Landsat, 30 m, daily updates across the tropics) alongside integrated alerts. Their Geta coverage remains unverified. Public raster field catalogs list cell coordinates/date/confidence but no provider event ID; any grouped observation must be represented as a versioned ForestProof-derived cluster linked to source cells, not as a native event record. No alert records queried.
- Raster-cell identity and offline RADD row normalization are implemented at `services/api/app/providers/raster_identity.py` and `services/api/app/providers/gfw_radd.py`. Tests cover stable keys, release separation, source date and field preservation, and invalid inputs. API suite passes 24 tests. The parser accepts one field map only; the live response envelope, persistence, and LIVE ingestion are not implemented.
- Momentum work on 2026-10-26: reviewed the official KFS PFMP's stated location extent and added a provisional research-only GeoJSON envelope. It is intentionally broader than the forest station and uses an explicit WGS84 assumption because the text does not state a datum. This supports engineering and coarse coverage research while the official GIS boundary and reuse terms remain pending; it is not used by the DEMO map or LIVE ingestion.
- Engineering direction on 2026-10-26: prioritize a direct RADD adapter, with GLAD-L as a later comparison and GFW Integrated Alerts deferred. This is a candidate selection, not evidence of Geta coverage or free API access. No alert records were queried.

## Next checkpoint

The owner has selected an owner-only first pilot and requires a live provider feed. Continue provider/query engineering and coarse source-coverage research using the provisional envelope, while obtaining/validating a machine-readable Geta AOI and its reuse terms before operational filtering. Confirm the exact source terms and cost before any alert-record query. Implement owner authentication, production database/storage, and restore controls before real case material. Audit the OVH host and costs before any deployment.


## 2026-10-28: pilot preparation and verified source notes

- The owner confirms the intended pilot is owner-only, requires a verified live feed, and prefers the existing OVH VPS. They report Ubuntu 24.04 and working remote desktop access. No independent server inventory, production deployment, or verified SSH access is recorded.
- The laptop checkout is at 71af70f with uncommitted documentation changes. GitHub main was 6d552d29b5d3337a56b434010fa41a2f836aa373 when this work began; its API and web CI passed in run 40609084867. Preserve local changes; do not reset that checkout.
- The offline RADD snapshot store compares two explicitly stored releases of the same derived cell/date identity. It reports source field differences and cannot infer retractions from a missing row; there is no live ingestion or owner authentication.
- WUR documents CC BY 4.0 reuse of the RADD dataset without royalty payment and identifies its primary humid tropical forest baseline. Local Geta coverage and GFW Data API access, cost, quota, exact integration attribution, response shape, and retention remain unverified. The PFMP-derived envelope is provisional and not an approved live filter.
- Official Global Nature Watch terms and the linked Resource Watch attribution page were read; GFW Pro retirement on 2026-12-31 concerns Pro and does not itself establish a retirement of the separate Data API. See docs/DATA_SOURCES.md and docs/COSTS_AND_OPERATING_BUDGET.md.


## 2026-10-28 supported web runtime

The repository's locked Next.js 14.2.35 is outside the supported release lines. A change in this pilot-preparation branch upgrades to Next.js 16.4.3 and React 19.2.8, migrates asynchronous route parameters, and adds a loopback production proxy/page smoke check and a production dependency audit. The candidate passed a generated-lock CI run and now has a committed lockfile; the exact release must also pass CI. It does not implement owner authentication or enable LIVE. Next.js support policy: https://nextjs.org/support-policy. Relevant current advisory: https://github.com/vercel/next.js/security/advisories/GHSA-p3m5-59mp-jv5r.


The first upgrade candidate passed API tests, web tests, typecheck, build and loopback smoke checks on 2026-10-28, but npm's production dependency audit reported MapLibre and PostCSS advisories. The revised candidate passed API tests, web tests, typecheck, build, loopback proxy and case-page smoke checks on Node 20 and 24, and a headless synthetic map interaction on Node 24, in https://github.com/thegodmustwin/forestproof/actions/runs/40617936251. The production dependency audit reported zero known vulnerabilities at that time; CI on the committed lockfile must also pass. Node 20 is end-of-life and must not be the proposed production runtime.


### Owner-provided OVH terminal screenshot, 2026-10-28

The owner showed a terminal on host vps-8071f70a reporting Ubuntu 24.04.4 LTS. The screenshot's TCP listener list shows port 22 on IPv4/IPv6 wildcard addresses, port 3389 bound to 127.0.0.1, and port 3350 bound to IPv6 loopback. SSH, xrdp, xrdp-sesman, Docker and containerd services were running. Ports 80 and 443 were not shown as TCP listeners in that snapshot. This does not establish firewall reachability, TLS, UDP listeners, container inventory, backup state, SSH authentication, service ownership, or future port availability. Preserve the existing remote desktop, SSH and container services.

The optional development Compose configuration binds its host ports to 127.0.0.1 and is checked in CI. It remains an unauthenticated synthetic demo and is not an approved production deployment.


### Read-only SSH inventory, 2026-10-28

The agent verified the ED25519 host fingerprint against the owner's VPS terminal screenshot and connected as ubuntu using existing local SSH credentials; no password or key was shared. Ubuntu reported Python 3.12.3 and Git 2.43.0. Root filesystem had approximately 90 GB available. The UFW status reported active, default deny incoming, with a rate-limited SSH rule; the screenshot showed xrdp listening on loopback. Docker and containerd were running, and sudo docker ps -a returned no containers at that moment. Node, npm, GitHub CLI, Caddy, nginx and Apache were not found on the account's PATH. No application backup was verified by the timer inventory; other backup mechanisms and OVH snapshots remain unknown. Firewall reachability, ports, running services and containers can change and must be rechecked before changes. This was read-only; no service, firewall or VPS software was changed.


The initial Python dependency audit reported advisories in Starlette, python-multipart and pytest. The candidate separates test dependencies, removes the unused multipart parser, upgrades the affected packages and adds pip-audit to CI. Verification must pass on the exact branch commit; no API authentication or live feed is claimed. The web container template now uses supported Node 24 instead of end-of-life Node 20.
