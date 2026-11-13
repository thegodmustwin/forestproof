# Next Actions

Review `docs/PREVIEW_UPLOAD_GUARD.md` and its tests before deploying. Keep
both API and gateway denial for shared synthetic previews; implement real owner
identity, protected storage and recovery separately before accepting evidence.

## Source context follow-up — 2026-11-12

The demo observation detail exposes validated optional provenance. Future live adapters must independently implement and verify source-specific semantics, access and storage before enabling any real-data path; do not promote fixture metadata into live evidence.


## NASA science sample follow-up — 2026-11-12

Review the bounded status-layer findings in `docs/NASA_DIST_SAMPLE_20261112.md`; verify additional overlapping tiles, quality/cloud and date semantics, source terms and an authorized geography before considering integration. Keep LIVE disabled and demo/real storage separate until identity, storage, recovery and source gates are met.

## Direct-source evaluation — 2026-11-12

Review `docs/DIRECT_SOURCE_EVALUATION.md`, verify GLAD-L product-specific reuse conditions and build on the owner-downloaded Earthdata sample and verify further science pixels. Keep LIVE disabled until source, area, owner auth, storage and recovery gates are met.

## Data-source independence research — 2026-11-12

Review `docs/GNW_INDEPENDENCE_RESEARCH.md` and compare a bounded direct-source candidate with the GNW route after access, rights, costs, coverage and geography are verified. Keep source decisions and LIVE disabled until the existing gates are met.


**GNW account update (2026-11-11):** The owner supplied a screenshot of the laptop setup reporting successful creation and Windows CurrentUser DPAPI-protected storage of an API key, after successful email/password authentication and a zero-item existing-key check. The reviewed helper is designed to read back and verify its encrypted file before reporting success. A subsequent nonsecret metadata check independently confirmed that the protected file exists and the pending marker is absent; the key itself and live-record access were not independently tested. The protected file is `%LOCALAPPDATA%\ForestProof\gnw-api-key.secure.txt` on that Windows account. It is not automatically available to Codex Cloud or Contabo. Never put the key, its file, passwords or tokens in chat, Git, logs or screenshots. No alert-record query or feed activation was made. API price, quota, applicable terms, attribution, retention, source coverage and real feed access remain unverified; no paid subscription is authorized.

## Demo recovery candidate — 2026-11-11

Review `docs/DEMO_SQLITE_RECOVERY.md` and the synthetic test results. Before depending on recovery for a real pilot, separately design and test encrypted off-host database and evidence backup, retention, access controls, integrity, operational restores and reconciliation with the private OVH archive. No private archive was accessed by this candidate.

Start with the code-verified [launch strategy](../docs/LAUNCH_STRATEGY.md), assessed on 2026-11-06. Prioritize the real-data backend/UI and private persistence/restore while source access is resolved; a key alone cannot activate the current synthetic implementation. Inventory the new Contabo host and verify any backup transfer before planning a preview update. For UI review, begin with monitoring/source detail and the case workspace rather than another homepage redesign.

## Private recovery context — 2026-11-10

**Owner-provided recovery context (2026-11-10):** Another chat reported a private laptop archive `C:\Users\Owner\Documents\OVH-Rescue-2026-10-30\forestproof-rescue-2026-11-01.tar.gz`, plus an older 2026-10-30 copy in the same folder. The 2026-11-01 archive reportedly contains the old synthetic preview's website/API files, deployment configuration, a SQLite snapshot, and private preview credentials/configuration. At creation the database reportedly passed an integrity check and the transferred archive matched the OVH copy. This is historical reported evidence; this session has not inspected the archive, independently rechecked integrity, or tested a restore. It cannot contain changes made after 2026-11-01. The separate PostgreSQL volume's project ownership is unknown; do not associate it with ForestProof without evidence. The old OVH preview was reported running when checked on 2026-11-01; its present status is unknown. ForestProof has not yet been transferred to Contabo.

Keep the archive and all credentials private and out of GitHub, chat, logs, and shared environments. This is recovery context, not permission to restore, deploy, or replace newer work. The GitHub `main` source and ongoing Cloud development must be preserved: if recovery is later authorized, inventory the archive safely in isolation, compare versions and configuration with current `main`, reconcile only needed data/configuration without overwriting newer code or existing services, then verify a private restore and database integrity before relying on it. Never execute archived scripts or trust old credentials by default; identify the PostgreSQL volume separately before any use. Cloud cannot assume it has the laptop archive or SSH key.

## Current host handoff — 2026-11-10

**Current hosting update (2026-11-10):** The owner has selected Contabo `vmi3711898` (Ubuntu 24.04.5 LTS verified by read-only SSH) for next-stage hosting. A read-only SSH test using the laptop's existing key and strict host-key checking reached `vmi3711898` on 2026-11-10. This confirms laptop connectivity, not Codex Cloud access or deployment readiness. The owner reports the private ForestProof backup is on the laptop; transfer to Contabo has not been completed or verified. `content-engine-vps` names the old OVH server, not Contabo. A read-only listener check found RDP on loopback; keep it private over the existing SSH tunnel and preserve existing services, projects and recovery access. Do not reinstall the server. Cloud tasks must not assume access to Windows files or SSH keys; arrange a separately configured secure connection if needed. Never put passwords, passphrases or private keys in chat or Git.

1. On the laptop only, read `D:\content-engine\docs\CONTABO_AGENT_HANDOFF.md` and use its verified connection approach. In Cloud, request a separately configured secure connection only if access is needed; never request credentials in chat.
2. Inspect host identity, occupied ports, running services, firewall, storage and existing project ownership read-only before choosing paths or making changes. Keep SSH and tunnel-only RDP usable; do not reinstall or stop other projects.
3. Identify the private laptop backup without exposing its contents or credentials, then plan a safe, conflict-free transfer and a restore verification before claiming Contabo has the project or recoverable data.
4. Continue live-feed, access-control, storage and UI work independently; do not claim a live service or deployment without verification.

Older OVH-specific tasks below are historical unless explicitly updated.

## Immediate: define a credible first pilot

The owner authenticated to My GNW and the laptop setup helper reported protected API key creation on 2026-11-11. Verify applicable real-feed access, quota, price and terms without collecting credentials in chat. Continue a screen-by-screen review of the synthetic preview while the live pilot gates below are completed.

1. Complete the initial release for one authenticated owner. The synthetic `owner_demo` candidate now authenticates the web service to the API and uses server-derived owner audit labels, but it still relies on the separate owner gateway for human authentication. Verify deployment topology, credentials, rate limiting, person-level identity and storage before real use; defer multi-organization onboarding.
   The synthetic web case queue, action and follow-up workflow now uses persisted API records and has a browser-level test; continue from this implementation rather than assuming the demo fixtures are saved cases.
2. Use `data/areas/geta-pfmp-research-envelope.geojson` now for engineering dry-runs and coarse coverage research. It is a PFMP-text-derived bounding rectangle, not the Geta forest boundary and not approved for LIVE alert filtering.
3. After exact terms/cost, area use, attribution, retention, account and coverage are established, verify a permitted bounded response against the standalone default-deny RADD research transport and parser. Its SQL, HTTP behavior and caller attestations are candidates, not evidence of operational authorization. Preserve cell provenance; treat any ForestProof grouping as a derived cluster, never a provider alert ID.
4. Follow up on the owner-supplied Global Nature Watch general terms: verify the linked API attribution requirements, dataset-specific conditions, cost, account access, rate limits, local coverage, and retention before making an alert-record query. The original terms page and linked attribution requirements were subsequently read on 2026-10-28; applicability to this exact API integration still needs clarification. Do not infer $0 from CC BY 4.0. A bounded, opt-in Copernicus Sentinel scene lookup now works locally without a paid account, but scenes are context rather than validated detections and do not satisfy the live-alert pilot requirement.
5. Obtain the official KFS GIS geometry and reuse conditions when available, without making a response a prerequisite for an honestly labeled wider-area owner pilot. Before any provisional pilot use, verify the region's assumptions, lawful use and source coverage; never claim its rectangle establishes Geta Forest membership. Check official replacement geometry for CRS, topology, area against the 21,644.37 ha PFMP figure, source/version, and use permission.
6. Keep LIVE disabled and fail closed until source terms/cost, AOI permissions, credentials, response shape, persistence, and health checks pass. Then exercise the owner-only observation-to-case-to-follow-up flow against real source data.

## Storage isolation follow-up — 2026-11-12

See `docs/DISABLED_MODE_STORAGE_GUARD.md`. Design a separately configured LIVE store, real identity controls, migrations, private off-host backups and an operational restore test before enabling LIVE. This disabled-mode guard does not classify or secure data in an explicitly configured DEMO database.

## Before pilot or deployment

- Implement authenticated identity, server-side role/tenant checks, protected object storage, upload scanning, retention, rate limits, monitoring, and tested backup/restore before real evidence.
- Continue development in the working Cloud task while available, preserving work in source control; fresh-task restoration is not verified. The failed environment publication is not a Contabo hosting prerequisite.
- On Contabo, audit occupied ports and services, firewall, backups, DNS/domain/TLS, runtime and operating cost before deployment. Direct access from Cloud and GitHub authentication on the VPS are unverified; do not request passwords or private keys in chat.
- Choose and document a deployment method only after the Contabo inventory and production controls are understood. Railway is not the current choice.
- Obtain practitioner feedback and one design partner before expanding billing, enterprise features, or predictive ML.
- Get explicit current approval before recurring paid services, public deployment, external outreach, notifications, or legally consequential communication.


## Historical 2026-10-28 immediate pilot work — OVH

The section below preserves the original plan and OVH inventory as history. It is not authorization or an instruction to deploy on OVH; see the Contabo handoff above. Apply any still-relevant general security or live-feed gates independently to Contabo after verifying its current conditions.

1. Recheck the read-only VPS inventory immediately before deployment; SSH access and the initial listener, firewall and container inventory were verified on 2026-10-28. Keep remote desktop and existing services available.
2. Implement and verify owner-only authentication and a private API boundary, production storage and a restore-tested off-host backup plan. The existing DEMO path is not suitable for real evidence.
3. Verify RADD's actual coverage over a lawfully reusable area, provider account/access, API pricing and quota, exact attribution and retention, then test a bounded response before wiring a live adapter. The provisional rectangle remains research-only.
   Public catalog metadata on 2026-10-29 returned an older content date for the `latest` alias than for another listed release; recheck and resolve freshness and version choice instead of assuming the alias is newest.
4. Integrate release comparisons only after the actual response and completeness semantics are established; missing rows alone are not retractions.
5. Keep the existing VPS and recurring costs unchanged until the host audit and any new cost approval are complete. Codex Cloud publishing is not a prerequisite for OVH.

Before exposure, verify the exact supported web release and committed lockfile through CI, review dependency advisories, and exercise the intended owner workflow.

Use a currently supported Node.js runtime for an OVH deployment; Node 20 remains a compatibility check only. A headless browser check covers synthetic markers and stubbed tiles; verify the intended owner's browser and permitted provider tiles before deployment.

The owner supplied a read-only VPS screenshot on 2026-10-28: inspect Docker containers, firewall, backup status, DNS/TLS and authentication before deployment. Preserve SSH and loopback xrdp.


The verified read-only VPS inventory found UFW active with only an SSH rule, no containers listed at that moment, and no Node/npm in PATH. Recheck before installation; preserve SSH, xrdp, Docker and firewall rules. Verify a real backup/restore and domain/TLS before deployment. The API dependency upgrade and audit must pass before any exposure.

Validate the offline GFW envelope parser against a permitted, bounded RADD response only after API pricing, terms, account access and a suitable research area are established. Keep the provider disabled until the remaining pilot gates pass.

The owner-only SSH-tunnel gateway candidate passed isolated runner checks in run 40625015460. Before installing or starting it on OVH, plan host-specific ports, private secrets, API binding and recovery, and test the full owner workflow.


## Historical 2026-10-28 friends-and-family test — OVH

This was the original OVH preview plan, retained as history. Do not perform its host-specific instructions on OVH or assume the preview exists on Contabo.

Verify the synthetic preview's localhost health and full user flow, then configure and verify password-protected HTTPS on the OVH hostname without changing existing SSH or remote desktop. Clearly distinguish it from the requested live pilot. Record the actual deployment result, URL, limitations and recovery instructions if and only if verified. Confirm feed access, terms, price and area coverage separately; do not represent the Geta research envelope as an official boundary.


## Historical deployed preview follow-up — OVH

This follow-up concerned the earlier OVH preview. Its password location and deployment state must not be assumed to apply to Contabo.

Ask the owner to privately retrieve the test password from the VPS and share it only with intended testers. Confirm their browser map and navigation; never collect real evidence or personal data in this shared synthetic database. Continue verified live-source access, cost and coverage work, authorized boundary, production storage and backups, identity and audit controls; do not claim the preview satisfies those gates. Preserve the existing VPS services and document any subsequent firewall or service changes.


## Historical 2026-11-05 design and source-cost follow-up

The OVH-specific instruction below is historical; use the Contabo host handoff above. The design and source-verification principles remain useful.

Use the portable UI skills and DESIGN.md for subsequent interface work. Inspect the synthetic desktop/mobile captures, test keyboard/focus and the primary workflow, and re-establish OVH access before deploying a new UI release. Verify the exact MyGFW Data API terms, price and quota before any alert query; evaluate direct GLAD-L and NASA OPERA only after their specific assets, reuse conditions, local coverage and semantics are checked. Test the narrow project-manager offer through authorized practitioner feedback; do not contact anyone without the owner's instruction.


## Historical 2026-11-06 Cloud continuation

The OVH availability instruction below is historical and superseded by the Contabo host handoff above.

Begin with `docs/CLOUD_HANDOFF.md`, then inspect the current code, main and execution status. Verify the MyGFW account type and applicable source costs/terms before any alert-record query. Continue source-independent implementation, identity/storage/backup preparation and meaningful tests while access is resolved. Recheck OVH availability without disturbing existing services. Apply the repository design skills to appropriate UI tasks and preserve the current DEMO/LIVE distinction.

## 2026-11-11 receipt provenance follow-up

The synthetic-only receipt ledger is groundwork, not an ingestion path. Before real data, establish source and retention terms, protected storage and recovery, provenance verification, authorized geography, and identity controls. Do not treat fixture hashes or empty responses as provider proof.

## Source-neutral provenance follow-up — 2026-11-12

Review `docs/OBSERVATION_PROVENANCE_CONTRACT.md`. Define provider-specific mappings and actual verified source semantics before connecting live records. Build real owner authentication, source verification, isolated storage and restore controls; do not enable LIVE merely because the contract exists.


## NASA date/quality follow-up — 2026-11-12

The owner supplied a first-detection-date band; its bounded status comparison is documented in `docs/NASA_DIST_SAMPLE_20261112.md`. The matching last-assessed-date and current-scene-mask bands have also been examined. Resolve the mask's code-0 terminology against authoritative metadata; separately evaluate relevant quality/cloud layers and overlapping tiles before making current-coverage claims. Keep provider detection dates separate from actual event dates and do not infer an official boundary or legal finding. Continue source-neutral integration, owner authentication, separate storage and recovery; LIVE remains disabled.
