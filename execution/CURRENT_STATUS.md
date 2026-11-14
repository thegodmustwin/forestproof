# Current Status

## Private owner workflow rehearsal — 2026-11-14

The synthetic owner identity candidate and the integration rehearsal passed GitHub checks. The rehearsal used a synthetic response, authenticated owner review, action, follow-up and dossier, then recovered both the saved receipt and dossier from separate local SQLite copies. Its link is test-only. The next release still requires a runtime adapter, an authorized source, off-host recovery, and staging. See [the walkthrough](../docs/PRIVATE_RADD_INBOX.md#owner-case-rehearsal).

## NASA scene quality and catalog screen — 2026-11-14

Both downloaded HLS Fmask bands matched their NASA inputs and aligned with the four DIST bands on each tile. Per overlapping grid, 722 of 12,432 centres (5.8%) had a November 3 last-assessed date and 237 (1.9% of all centres) also passed the conservative ForestProof QA screen. These two grids describe one acquisition. Nine synthetic inspector tests previously passed. The bounded 90-day catalog check found 71 entries across 36 acquisition dates, with November 3 the newest listed acquisition. Repeat usable coverage and operational fit remain unknown. See [quality results](../docs/NASA_DIST_SAMPLE_20261112.md#nasa-quality-results-for-november-3).

## Private RADD import and recovery rehearsal — 2026-11-14

The offline inbox can preserve exact RADD shaped response bytes, reject conflicting or out-of-scope cells, deduplicate replays, report stale receipts and observations independently, and export a receipt-linked unverified record. Its separate SQLite copy verifies response hashes and record linkage. Verification uses synthetic input and local restore paths. Actual provider access, case integration and off-host recovery remain open. See [the runbook](../docs/PRIVATE_RADD_INBOX.md).

## Protected Contabo synthetic preview — verified release 2026-11-13

The protected synthetic preview at https://vmi3711898.contaboserver.net/ now serves pinned source commit `38881dc79f04de9d21997fe85dea8712ef78e91d` from `/opt/forestproof-preview-releases/38881dc`. The candidate API and web images were `forestproof_candidate_388-api:latest` and `forestproof_candidate_388-web:latest` under Compose project `forestproof_preview_20261112`. The existing named SQLite volume was retained; the separate Caddy gateway and unrelated services were not restarted. This is a shared-access DEMO preview, not a live or production pilot.

Before the app-only API/web swap, a fresh private SQLite snapshot and a separate restore both passed integrity checks; the existing demo database retained one synthetic case and six events. An isolated loopback staging instance at `127.0.0.1:13002` passed DEMO health and returned three explicitly synthetic, source-labelled observations. Its API denied an evidence upload with HTTP 409. The staging stack was stopped after the release.

After the swap, external HTTPS certificate validation from Windows succeeded with a zero exit code and anonymous access returned HTTP 401. Authenticated host checks returned HTTP 200 for the synthetic home and DEMO health, three synthetic observations with DEMO source provenance, HTTP 403 for gateway-blocked evidence upload and cross-origin mutation, and HTTP 409 for an upload sent directly to the running API. The API has no host-published port; the web listener is on loopback port 13000. SSH, xrdp, MariaDB and PHP-FPM remained active, and RDP remained bound to loopback port 3389.

The deployed site's browser rendering was not visually verified. The private local SQLite snapshot and restore are not an off-host production backup. Person-level owner authentication, separate protected live storage and tested production recovery, source terms/coverage/cost, and a verified live feed remain unfinished. Do not submit personal or real field data or describe the preview's records as live observations.

## Synthetic evidence upload guard — merged and deployed 2026-11-13

The API and storage adapter deny demo evidence uploads by default, with an
explicit opt-in for isolated local `demo` mode only. Shared-preview Compose
explicitly disables the flag; the gateway retains its separate denial. This
change does not provide person-level authentication or authorize LIVE. Its
Contabo deployment is verified in the release entry above. See
`docs/PREVIEW_UPLOAD_GUARD.md`.

## Synthetic owner demo write guard — merged 2026-11-13

The isolated owner demo web proxy requires the exact configured loopback gateway origin for browser POST requests before it forwards its internal service token. GitHub CI passed its proxy, configuration and smoke checks. Person-level owner sign-in remains open. This change is for the separate owner demo candidate. The shared Contabo preview still serves the pinned release above. See [PR #22](https://github.com/thegodmustwin/forestproof/pull/22).

## Synthetic owner identity candidate — 2026-11-14

The isolated synthetic owner workflow now verifies one authenticated gateway subject across Caddy, Next.js and FastAPI, using two distinct server tokens. Its mutations record that subject in the audit trail. The [owner gateway runbook](../infrastructure/deployment/owner-pilot/README.md) covers secret setup, revocation and loopback isolation. The candidate remains undeployed and LIVE remains disabled.

## Direct source review — 2026-11-13

The source evaluation now links the four-band NASA sample and records the product DOI, citation, differing reuse metadata and limits of interpreting vegetation disturbance. The GNW reference documents default key expiry and the domain-based rate tier. Price, numeric quota and project alert access remain unverified. See `docs/DIRECT_SOURCE_EVALUATION.md` and `docs/DATA_SOURCES.md`.

## NASA two-tile research comparison — 2026-11-13

All four matching bands for T37MBV opened and aligned. The two November 3 Landsat 8 tiles fully overlap in the provisional rectangle. Each grid had 722 of 12,432 centres with a November 3 last-assessed date. Native summaries remain separate to avoid counting the same ground twice. See [the comparison](../docs/NASA_DIST_SAMPLE_20261112.md#two-tile-comparison) for verification, local fingerprints, and quality limits. Operational NASA coverage and LIVE ingestion remain unverified.

## Offline NASA research diagnostic — 2026-11-13

A separately invoked NASA DIST-HLS V1 research utility accepts explicitly supplied local layers and a bounded WGS84 rectangle, validates matching grids and reports aggregate dates and status/mask values. Synthetic tests are in a dedicated Python 3.12 workflow; no private rasters or coordinates are committed. This is not a live provider integration, production evidence store, or replacement for the unresolved quality/geography gates.

## Prior protected Contabo preview release — verified 2026-11-13

The synthetic protected preview at https://vmi3711898.contaboserver.net/ was updated to pinned source commit `9bd49bcf92ebbfd14b75e042e3095d23c315eb5b`. The deployment operator reported successful external TLS and anonymous 401, authenticated home and DEMO health, source provenance on three synthetic observations, blocked cross-origin mutation and evidence uploads (403), and preserved database volume (one synthetic case and six events). A private pre-update SQLite snapshot and separate restore passed integrity checks; this is not an off-host or production backup. The operator reported a temporary isolated staging stack was stopped. Actual browser rendering of the deployed host was not independently verified; CI desktop/mobile synthetic renders for the source-context UI were inspected. On 2026-11-13 a separate read-only SSH recheck confirmed the preview web, API and gateway containers running and SSH, xrdp, MariaDB and PHP-FPM active. The web binding was loopback. Tester credentials remain private as in the prior deployment record. No live feed or real-evidence intake was enabled. Future source changes on GitHub may not be deployed; verify exact release.


## Source context in observation detail — 2026-11-12

The monitoring detail displays source-record identity and validated API provenance with explicit missing/unknown values. Older demo servers without the optional provenance object remain supported; malformed or mixed provenance is rejected. This does not enable LIVE or authenticate a provider.


## NASA science sample inspection — 2026-11-12

After the owner privately downloaded one NASA DIST-HLS status TIFF, a local bounded research check found non-nodata status values within the intersection of that tile and a provisional rectangle. Synthetic tool tests passed; other quality layers, event timing, official boundaries and field conditions remain unverified. No live feed was activated and no forest-loss conclusion is established. See `docs/NASA_DIST_SAMPLE_20261112.md`.

## Direct-source evaluation — 2026-11-12

Public NASA metadata and a single whole-tile browse PNG were retrieved; a GLAD-L tile HEAD request returned current file metadata. Neither verifies valid Geta pixels, authorizes live use, or means any GNW alert query was made. See `docs/DIRECT_SOURCE_EVALUATION.md`.

## Independence research — 2026-11-12

`docs/GNW_INDEPENDENCE_RESEARCH.md` records provider-independent architecture options, GNW self-hosting terms and competing workflow capabilities. RADD remains the lead candidate; no production source, live alert request or feed integration has been verified.


**GNW account update (2026-11-11):** The owner supplied a screenshot of the laptop setup reporting successful creation and Windows CurrentUser DPAPI-protected storage of an API key, after successful email/password authentication and a zero-item existing-key check. The reviewed helper is designed to read back and verify its encrypted file before reporting success. A subsequent nonsecret metadata check independently confirmed that the protected file exists and the pending marker is absent; the key itself and live-record access were not independently tested. The protected file is `%LOCALAPPDATA%\ForestProof\gnw-api-key.secure.txt` on that Windows account. It is not automatically available to Codex Cloud or Contabo. Never put the key, its file, passwords or tokens in chat, Git, logs or screenshots. No alert-record query or feed activation was made. API price, quota, applicable terms, attribution, retention, source coverage and real feed access remain unverified; no paid subscription is authorized.

## Synthetic SQLite recovery candidate — 2026-11-11

`app.demo_db_copy` uses SQLite's backup API to create a new, integrity-checked copy in a trusted private directory and refuses to overwrite existing destinations. Its CLI requires an explicit synthetic-only attestation; schema checks do not prove the data is synthetic. It is limited to synthetic demo database files: evidence objects, credentials and PostgreSQL are excluded. The source-independent tests exercise committed WAL data, a separate restore, invalid input and collision handling. This is a candidate pending its PR checks, not verification of the private rescue archive, encryption, production backups, or an actual Contabo restore. See `docs/DEMO_SQLITE_RECOVERY.md`.

**Last updated:** 2026-11-10
**Milestone:** private GitHub source and Codex Cloud development environment established; production gates remain.

**Current hosting update (2026-11-10):** The owner has selected Contabo `vmi3711898` (Ubuntu 24.04.5 LTS verified by read-only SSH) for next-stage hosting. A read-only SSH test using the laptop's existing key and strict host-key checking reached `vmi3711898` on 2026-11-10. This confirms laptop connectivity, not Codex Cloud access or deployment readiness. The owner reports the private ForestProof backup is on the laptop; transfer to Contabo has not been completed or verified. `content-engine-vps` names the old OVH server, not Contabo. A read-only listener check found RDP on loopback; keep it private over the existing SSH tunnel and preserve existing services, projects and recovery access. Do not reinstall the server. Cloud tasks must not assume access to Windows files or SSH keys; arrange a separately configured secure connection if needed. Never put passwords, passphrases or private keys in chat or Git.

Historical OVH information in dated entries below is not evidence of a Contabo installation or current host state.

## Private recovery snapshot

**Owner-provided recovery context (2026-11-10):** Another chat reported a private laptop archive `C:\Users\Owner\Documents\OVH-Rescue-2026-10-30\forestproof-rescue-2026-11-01.tar.gz`, plus an older 2026-10-30 copy in the same folder. The 2026-11-01 archive reportedly contains the old synthetic preview's website/API files, deployment configuration, a SQLite snapshot, and private preview credentials/configuration. At creation the database reportedly passed an integrity check and the transferred archive matched the OVH copy. This is historical reported evidence; this session has not inspected the archive, independently rechecked integrity, or tested a restore. It cannot contain changes made after 2026-11-01. The separate PostgreSQL volume's project ownership is unknown; do not associate it with ForestProof without evidence. The old OVH preview was reported running when checked on 2026-11-01; its present status is unknown. ForestProof has not yet been transferred to Contabo.

Keep the archive and all credentials private and out of GitHub, chat, logs, and shared environments. This is recovery context, not permission to restore, deploy, or replace newer work. The GitHub `main` source and ongoing Cloud development must be preserved: if recovery is later authorized, inventory the archive safely in isolation, compare versions and configuration with current `main`, reconcile only needed data/configuration without overwriting newer code or existing services, then verify a private restore and database integrity before relying on it. Never execute archived scripts or trust old credentials by default; identify the PostgreSQL volume separately before any use. Cloud cannot assume it has the laptop archive or SSH key.

## Truthful snapshot

| Area | Status | Evidence / limitation |
| --- | --- | --- |
| GitHub source control | WORKING | Private main contains the merged synthetic preview and RADD research transport groundwork. Preserve the older, locally modified desktop checkout; do not reset it. |
| GitHub CI | RECORDED PASS; LATEST RUN UNCHECKED | The 2026-11-06 handoff records successful main-branch checks at https://github.com/thegodmustwin/forestproof/actions/runs/41932282052. This Cloud assessment reran the local API/web/build/browser checks at `85dbc77`; it did not independently verify the latest exact-commit GitHub run. |
| DEMO vertical slice | WORKING | Synthetic observation → case → transition/assignment → evidence hash → action/follow-up → JSON dossier/outcome graph is implemented and covered by API checks. |
| Live data | EXPERIMENTAL SCENE CONTEXT; NO ALERT FEED | An optional owner-demo-only Copernicus scene-metadata lookup was tested locally against the public catalog. It is disabled by default and not deployed. GFW alerts, NASA FIRMS, and KFS remain candidates; no validated live forest-alert feed is active. |
| Pilot geography | PROVISIONAL RESEARCH ENVELOPE | `data/areas/geta-pfmp-research-envelope.geojson` converts the PFMP's published location range to a coarse rectangle for research and dry-runs. It is not an authoritative Geta boundary or an activated live filter. The owner accepts a provisional wider-area approach; its assumptions, use and pilot controls must still be verified, and results must not be described as inside the forest. |
| Lead feed engineering target | RADD CANDIDATE | Direct GFW RADD is the first adapter target; GLAD-L remains a comparator. A default-deny standalone bounded research transport, offline normalization and local snapshots are tested with synthetic data; none is connected to live ingestion. Local coverage, deployed query behavior, terms and cost remain unverified. No RADD alert records queried or alert feed activated. |
| Legal context | PLANNED | No verified court order, permit, restriction, or qualified human legal review is loaded. |
| Persistence | PARTIAL | SQLite is the DEMO development adapter. PostGIS SQL exists as a target; production runtime is not connected to it. |
| Authentication and tenancy | PARTIAL / SYNTHETIC ONLY | Experimental owner-demo API verifies an internal web-service token and records one owner actor. The web service requires a separate authenticated gateway and loopback isolation. Person-level identity, production access and multi-tenancy are absent; LIVE remains disabled. |
| Codex Cloud | CURRENT TASK WORKS; PUBLICATION UNCONFIRMED | After a readiness timeout, this task's checkout and Git read recovered on 2026-10-27. Saved draft revision 10 has not been confirmed published. The user captured an approval operation reporting RUNNING while the UI showed a publish error; the server-side cause remains unknown. Fresh-task restoration is not verified. |
| Contabo access | LAPTOP SSH VERIFIED; CLOUD UNKNOWN | Read-only SSH from the owner's laptop reached `vmi3711898` using the existing key with strict host-key checking on 2026-11-10. Ubuntu 24.04.5 and loopback RDP were observed during the read-only check; separate Cloud access, inventory and deployment remain unverified. |
| OVH access | PRIOR ACCESS; CURRENT REACHABILITY UNCONFIRMED | Earlier sessions verified SSH and the synthetic preview. On 2026-11-06, this Cloud runtime's HTTPS check returned proxy HTTP 503 with an upstream connection-timeout message. This does not identify the host-side cause. No current SSH credentials or TCP grants are configured here; backups and production controls remain unverified. |
| Production deployment | HISTORICAL SYNTHETIC PREVIEW ONLY | Project notes record a password-protected shared demo at `https://vps-8071f70a.vps.ovh.net/`, verified during initial deployment. The current service and deployed release remain independently unverified after an unsuccessful HTTPS check. No live-production pilot has been verified. |
| Data-source cost | COPERNICUS FREE-TIER CONTEXT; ALERT COST UNKNOWN | Copernicus documents free worldwide access and a free tier; bounded anonymous catalog metadata queries succeeded without billing. OVH traffic/compute and full legal terms remain unverified. GFW API pricing and quotas remain unknown; no alert query or paid data service has been used. See `docs/COSTS_AND_OPERATING_BUDGET.md`. |

## Disabled-mode storage guard — 2026-11-12

Unsupported API modes no longer create or migrate the configured SQLite file during startup; direct demo storage and seeding calls also reject unsupported modes. Regression tests cover absent and preexisting paths. This does not implement LIVE storage, identity or production backup/restore.

## Constraints and non-claims

1. The Aberdare map area is illustrative, not an official licensed boundary.
2. DEMO observations, cases, dates, coordinates, confidence-like values, and evidence are synthetic; they are not current Kenyan incidents.
3. A remote-sensing signal cannot establish cause, authorization, illegality, or causal conservation impact by itself.
4. The original prompts mention October 2026 court reporting. No operative official order or current legal status is in the application; verify before use.
5. Real field or personal evidence must not enter the current unauthenticated demo system.
6. The old Railway guide is historical; Contabo is the owner's current hosting target and OVH is historical. A password-protected synthetic preview was deployed there; no live production pilot has been deployed.

## Verification evidence

- On 2026-11-06, latest private main `85dbc77` was fetched and fast-forwarded from a clean checkout. The handoff, design skills, data/cost and product documents were reviewed against code. API tests (106), web tests (19), typecheck, production build and the isolated synthetic owner-demo browser workflow passed locally; 1440px/390px dashboard captures were visually inspected. No Caddy binary was supplied in this run, so separate gateway authentication was not exercised. The live API route remains a placeholder, and the API/proxy/UI accept synthetic modes/records only: account completion alone cannot activate live monitoring. See `docs/LAUNCH_STRATEGY.md` for the scoped plan and limitations.
- On 2026-11-06, the three original UI skills were installed and hash-verified in this runtime's user skill directory without replacing existing files; concise UI-scoped guidance was added. Executor catalog discovery and fresh-session persistence are unverified; repository copies remain the fallback. No paid service, live alert request, external outreach or new deployment was performed.
- On 2026-10-30, the owner reported creating an ArcGIS account in connection with MyGFW. At that date, GFW Data API account capabilities, key, alert coverage, quotas and cost were unverified. This historical record is superseded for account/key setup by the 2026-11-11 update above; actual alert access, coverage and cost remain unverified.
- On 2026-10-30, the DEMO dashboard received a clearer first action and introduction, a corrected brand layout, a non-numeric unmeasured outcome, keyboard focus indicators and navigation state. Web tests (19), typecheck and production build passed. A loopback browser check with a temporary synthetic case exercised desktop and mobile layouts, brand bounds, navigation and the monitor link. This is local development only; the OVH preview was not updated or rechecked.
- On 2026-10-29, an optional owner-demo Copernicus scene lookup was added and tested with real public catalog metadata. A bounded three-scene search returned acquisitions including two on 2026-10-29, with scene-wide cloud cover 57.9% and 59.42%. These are scene acquisitions, not disturbance alerts; bounding-box overlap is not proof of full area coverage or an official boundary. The lookup is off by default, restricted to the owner-demo service boundary, and not deployed on OVH. The API suite passed 106 tests, web suite passed 19 tests, TypeScript and build passed, and owner-gateway browser checks passed with the feature off and with an explicitly opted-in live catalog lookup. No imagery, real case records, API keys or paid services were used.
- On 2026-10-29, the demo command center and case queue were connected to the actual saved demo cases. Case links now open the correct source observation, and missing observations are not replaced by unrelated fixtures. The case screen can record synthetic actions and follow-ups; the API rejects action/follow-up states without an action and rejects closing without a follow-up. The full API suite passed 91 tests, the web suite passed 17 tests, the TypeScript check and production web build passed, and an isolated browser test exercised the complete workflow through Caddy, Next.js and FastAPI with synthetic data. This does not activate a live feed or change the existing OVH deployment.
- On 2026-10-29 an experimental synthetic `owner_demo` mode was implemented: the API checks an internal service token, keeps the demo tenant fixed, assigns audit actors server-side, blocks evidence uploads and leaves LIVE closed. The Next proxy only sends its server-side token to an explicit loopback API, rejects redirects, strips browser-supplied internal headers and requires matching API mode. The full API suite passed 89 tests; web tests (15), TypeScript, the production web build, the standard web smoke and an end-to-end Caddy/Next/FastAPI smoke passed locally with synthetic credentials and data. The gateway now requires explicitly chosen ports to avoid silently conflicting with the existing preview. This does not deploy to OVH, verify production security, implement person-level identity, or permit real material. Local host users and the separately authenticated gateway remain inside the trust boundary.
- On 2026-10-29 a standalone, default-deny RADD research transport candidate was added. Tests exercised prerequisite gates, fixed endpoint and header-only key, small request bounds, byte/time limits, duplicate JSON, incomplete responses, error handling, no retry and redirect protection; a real redirect check used only two local mock servers. The full API suite passed 85 tests with the current pinned Python dependencies. No provider credentials or live alert data were used, and no network transport is wired to the application. The candidate's caller attestations are not audited proof or production authorization.
- On 2026-10-29 public GFW `/fields` metadata listed the RADD confidence values 2/3/4 as nominal/high/highest. This is catalog metadata only, not proof that the live response shape, local coverage, service cost or legal terms are verified.
- On 2026-10-29 public RADD release metadata returned `v20261011` for the `latest` alias, while separately listed `v20261018` had a later content date but `is_latest: false`; the reason is unknown. Direct metadata checks for `v20261025` and `v20261026` returned 404. No alert records were requested. Recheck release selection and freshness before activation; see `docs/DATA_SOURCES.md`.
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

- The owner confirms the intended pilot is owner-only, requires a verified live feed, and prefers the existing OVH VPS. They report Ubuntu 24.04 and working remote desktop access. At the start of this work no independent server inventory or verified SSH access was recorded; the subsequent read-only SSH inventory appears below. No production deployment is recorded.
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

The candidate web/API upgrades and optional web container build passed CI at https://github.com/thegodmustwin/forestproof/actions/runs/40621397262. The Python dependency audit found no known vulnerabilities in its resolved requirements at that time; the npm production audit found no known vulnerabilities. Audits do not establish production security.


## 2026-10-28 candidate GFW response envelope

WRI's published API source at commit dd277b245debf8e37a98a8e6238c5ead8aeed115 shows POST query/json returning a Response with status success and data containing a list of row dictionaries: https://github.com/wri/gfw-data-api/blob/dd277b245debf8e37a98a8e6238c5ead8aeed115/app/routes/datasets/queries.py and https://github.com/wri/gfw-data-api/blob/dd277b245debf8e37a98a8e6238c5ead8aeed115/app/models/pydantic/responses.py. This is evidence of the source-code contract, not a verified response from the deployed service or proof of RADD coverage, access, pricing, quota, or retention rights. The standalone offline parser accepts this candidate shape, requires a concrete source release, bounds the parsed JSON and row count, rejects unsuccessful or malformed envelopes, and preserves a copy of parsed source fields. Its tests use synthetic inputs only. An empty result is not a source-health or coverage claim; raw HTTP-byte capture and response-size limits at the network boundary remain future work. LIVE remains disabled.


## 2026-10-28 owner-only gateway candidate

A Caddy configuration under infrastructure/deployment/owner-pilot/ has been tested on an isolated GitHub runner for a loopback-only owner gateway over the existing authenticated SSH tunnel. Its checks for required credentials, authentication, trusted host, Origin, stripped upstream authorization and loopback binding passed in GitHub Actions run 40625015460; this is not an end-to-end VPS test. It is not installed or running on the OVH VPS. It guards all proxied web paths with a hashed owner credential and rejects cross-origin mutations; the API and web upstream must remain separately bound to VPS loopback. It is not suitable as a public HTTP endpoint. Source access, application authentication semantics, protected storage, backups and production operation remain open.


## 2026-10-28 friends-and-family preview preparation

The owner requested a shareable test by approximately 5pm local time today, alongside the longer-term live pilot. An isolated synthetic preview candidate is in `infrastructure/deployment/family-preview/` and `docker-compose.preview.yml`; the web listener binds to loopback and the API has no host port. A separate HTTPS gateway candidate uses a shared test password and blocks evidence uploads. GitHub Actions tests the gateway and the app containers. A server staging folder and isolated demo containers were created on the existing OVH VPS; the candidate has not yet been verified for public HTTPS use, and this is not a live-data deployment. No actual provider records, real case data or personal data should be added. No paid service was created. Existing SSH, remote desktop and unrelated services must remain intact.


## 2026-10-28 protected synthetic preview deployed

The requested friends-and-family preview is running on OVH at https://vps-8071f70a.vps.ovh.net/ behind HTTPS and a shared tester login. External unauthenticated HTTPS returned 401 with a verified certificate; local authenticated checks reached the demo health endpoint and rejected cross-origin mutation and evidence uploads. The direct API port 8000 timed out from outside. API has no host-published port; web binds 127.0.0.1:13000. The preview uses disposable shared synthetic SQLite data and is not production evidence storage; backups and restore are not verified. Do not submit personal or real field data. The HTTPS password is in a server-side owner-only file, never Git/chat. UFW now includes port 80 allow and 443 rate-limit rules alongside the existing SSH rule. SSH and xrdp were verified running after starting the app. RADD, operational AOI, production storage and a true live pilot remain unverified. This deployment must not be described as live forest-loss monitoring.


## 2026-11-05 UI skills and design candidate

Three original user skills were installed on the owner's computer and packaged under .agents/skills/ for repository-based work. The design branch reshapes the command center and shared shell around a field atlas and evidence ledger, retaining synthetic labels, API queue states and existing workflow. CI captures synthetic desktop/mobile images for visual review. Source verification and actual OVH deployment are separate; a prior Nov 5 HTTPS/SSH check timed out, so no new server deployment is claimed. Lower-cost data alternatives and an unvalidated commercial hypothesis are documented in docs/LOW_COST_DATA_AND_VALUE_PLAN.md. MyGFW API price remains unknown; no paid services or live alerts were used.


## 2026-11-06 Cloud continuation and current checks

The user's requested Cloud continuation brief is in `docs/CLOUD_HANDOFF.md`. GitHub main was `48693afb13505df69e3b4863e9f3e1f68be792d2` during preparation and its main-branch CI run https://github.com/thegodmustwin/forestproof/actions/runs/41932282052 succeeded. The desktop checkout remained older with uncommitted/untracked changes; it was not reset. On this date, an SSH check from the Windows laptop timed out and a separate HTTPS check timed out during DNS resolution. This does not establish the VPS's power, firewall or application state. A Windows-local global design guidance file was prepared separately; remote Cloud environments must use repository skills or receive their own user-level setup. The desktop chat-management tools were not available and browser/desktop automation timed out, so direct handoff into a Cloud chat was not verified. No API key, provider alert record, paid service, deployment or external outreach was added by this handoff.

## 2026-11-11 synthetic RADD receipt candidate

A standalone local receipt ledger preserves synthetic fixture response hashes and bounded query metadata, with UNKNOWN completeness and explicit synthetic attestation. It performs no provider calls, does not link to case storage, and does not establish production readiness or live source provenance. See `docs/RADD_FIXTURE_RECEIPTS.md`.

## 2026-11-12 source provenance foundation

The API exposes a versioned, source-neutral provenance projection for identified synthetic observations through list/detail and case/dossier responses. The contract separates derived/fixture/provider identity, source release and time precision, and explicitly marks completeness unknown. Schema validation cannot establish truth, access rights or source health. LIVE remains disabled, and real owner authentication, source authorization, live storage and restore remain unimplemented.

## Protected Contabo synthetic preview — 2026-11-12

The authorized password-protected synthetic preview is running at https://vmi3711898.contaboserver.net/ on Contabo vmi3711898, deployed from commit bf5c827534cd857df5a6c6df0873c689bb9e5b0f (main advanced since). Source archive checksum was verified before extraction under /opt/forestproof-preview-20261112. Compose project forestproof_preview_20261112 keeps API unexposed and web at 127.0.0.1:13000; separate Caddy gateway forestproof-preview-gateway-20261112 uses HTTPS and shared Basic Auth. Tester username is tester; the password is held privately under the Ubuntu user's /home/ubuntu/forestproof-preview-access-20261112/password and must not be pasted into chat, logs, screenshots or Git.

External Windows HTTPS check returned 401 with TLS verification; authenticated host-side checks returned home 200 and health 200 mode DEMO; cross-origin POST and evidence upload returned 403. Direct external API port 8000 timed out from the laptop. SSH, xrdp, MariaDB and PHP-FPM remained active. Existing other projects were not intentionally changed. An authenticated API smoke test created an explicitly named synthetic deployment test case and verified observation, case, action, follow-up and dossier. The test case remains in the shared demo database. Actual browser rendering was not independently verified in this deployment. Preview users share a synthetic demo database; no personal data or real evidence, no live source, no claim of production readiness or tested production backup/restore. HTTPS and services require ongoing monitoring. Host firewall/provider settings unchanged. Caddy data and config are under the dedicated /opt directory; do not use unscoped docker compose down or remove unrelated containers/volumes. The old OVH recovery archive was not restored. Review exact source and current main before any update.


## NASA first-detection-date layer — 2026-11-12

The owner downloaded the matching NASA DIST-HLS V1 first-date band. A bounded, single-tile research check found that 1,477 centres with nonzero provider disturbance status had first-detection dates from 2025-11-03 through 2026-11-03. Dates are algorithm detections, not exact real-world event dates; forest cover, current conditions, causes, legality, full quality/cloud, other tiles and official boundaries remain unverified. The matching last-assessed band gave 2026-10-04 through 2026-11-03 across these centres; this is not proof each was assessed on November 3. Five synthetic tests passed. See `docs/NASA_DIST_SAMPLE_20261112.md`; no raster, private credentials or pixel coordinates were committed, and LIVE remains disabled.
