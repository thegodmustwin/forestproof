# ForestProof — verified readiness and launch strategy

**Assessed:** 2026-11-06 (Africa/Nairobi). Code inspected and exercised: private main `85dbc77` (handoff merge). This assessment is a plan and dated verification record, not a production release or provider authorization.

## Product and first customer

ForestProof turns a sourced environmental observation into an accountable review, documented response, follow-up and source-linked dossier. Its first commercial hypothesis is a forest/restoration project manager or contracted monitoring team with a real review/reporting duty. Public alerts are an input; the useful product is completing and retaining that review trail. No paying customer, practitioner validation, measured savings or ecological impact is established.

The first live release remains one authenticated owner, one explicitly described provisional region and one verified record-level source. A wider Geta research region can support this without claiming an official forest boundary. Do not expand into multi-organization onboarding, billing, legal determinations, public accusations or automated enforcement for this milestone.

## What is ready and what is not

| Area | Verified state | Remaining launch work |
| --- | --- | --- |
| Source and design | Latest GitHub main fetched into a clean Cloud checkout. The command center/shared shell have the field-atlas/evidence-ledger redesign. | Extend the same craft to the monitoring and case work surfaces through actual task reviews. |
| Case workflow | Synthetic observations, saved cases, required actions/follow-ups, closure and dossiers work. | Support genuine provider records through a separately authorized, non-demo path. |
| Live backend | RADD normalization, snapshots, parser and bounded transport are standalone groundwork. | API rejects unsupported modes; `/ingestion/live/gfw` still returns `NOT_STARTED`. Implement ingestion, storage integration, scheduling, health and real record access. |
| Live frontend | DEMO identity and source safeguards work. | Observation and case parsing explicitly reject non-DEMO_DATA records. Implement a real-data contract/UI without weakening demo protections or mixing databases. |
| Identity and storage | Isolated synthetic owner-demo service-token boundary exists. SQLite/local evidence are demo adapters. | Identify/authenticate the actual owner, enforce private API access and audit attribution, productionize persistence and demonstrate backup/restore. |
| Hosting | A prior session verified a protected synthetic preview on OVH on 2026-10-28. | Current host state and deployed version unconfirmed. A 2026-11-06 Cloud HTTPS request received proxy HTTP 503, with an upstream connection-timeout message. No SSH credentials or TCP grants are configured in this runtime. This does not diagnose the VPS power, DNS, firewall or app. |
| Source access and price | Owner reports an ArcGIS account. RADD dataset reuse is documented separately from GFW API service terms. | Confirm actual MyGFW/API-key capability, service cost/quota, attribution, retention, release freshness, local baseline coverage and a permitted bounded response. |

**Account completion alone cannot enable live monitoring.** The backend and frontend still require implementation. A key must not simply be dropped into the existing demo.

## Accounts: the minimum useful set

- **Existing personal GitHub:** already usable for private source; keep the university account separate.
- **Existing OVH:** recover/verify current access and service health; do not order another host by default.
- **MyGFW / GFW Data API:** needed if the RADD route is selected. The recorded official guide describes an email/password account and API-key capability. An ArcGIS or social-login account does not establish that capability. Keep passwords/keys out of chat and Git; use private server/environment secret handling after access and terms are reviewed.
- **ArcGIS:** no current application SDK/integration or established technical requirement. Do not buy credits or an upgrade for ForestProof without a demonstrated need and approval.
- **NASA Earthdata:** only if the OPERA alternative is selected and validated. Do not create it alongside MyGFW merely for completeness.
- **Copernicus account:** not required for the implemented anonymous, bounded scene-catalog lookup; scenes are context, not the requested alert feed.
- **Earth Engine, hosted auth/database/storage, email and billing accounts:** no blanket requirement for this owner-only milestone. Select only after a specific operational need, terms and cost are known.

## Delivery sequence and acceptance

### 1. Restore the feedback surface

Determine OVH's current service state/address through an authorized console or existing trusted access. Recheck DNS, ingress and containers without resetting the server or disrupting SSH/remote desktop. Once access is available, deploy the latest synthetic preview to the already authorized protected preview boundary. Verify HTTPS, denied anonymous access, upload restrictions and the full synthetic browser flow. This milestone produces a feedback link; it does not satisfy the live-pilot requirement.

### 2. Build the private real-data path while source access is resolved

Implement a separate owner-live mode, authenticated identity, source/record/version contracts, read APIs and UI validation. Keep DEMO databases and labels isolated. Build meaningful tests using explicitly synthetic provider contract fixtures, not falsely labeled genuine observations. Define fresh/stale/unavailable/empty states and prevent a failed source from becoming demo data. Choose an explicit storage design and add consistent backups, retention and a restore drill.

For the smallest pilot, **propose keeping field/personal uploads disabled** and using permitted provider records plus owner review notes and source-linked dossiers. This reduces scope without dropping the core review loop. The restriction and treatment of notes must be explicit. Productionized SQLite may be evaluated for one owner if concurrency, integrity, recovery and operational limits are demonstrated; PostGIS remains the documented target where the geospatial workload justifies it. Neither a migration nor a managed database account substitutes for restore evidence.

### 3. Validate one source and connect it

Finish the private account/access check and source ledger. Validate price/quota, exact product use/attribution/retention, a reviewed area description, local baseline coverage, release selection and provenance. Only then perform a small permitted request, preserve allowed raw/source version metadata and verify its meaning before wiring scheduled bounded ingestion. Do not query upstream for every page view. A missing observation or an empty result is not proof of no disturbance.

RADD remains the lead candidate. If access, cost or local coverage is unsuitable, evaluate direct GLAD-L first, then NASA OPERA DIST-HLS against the same explicit product criteria. These are unimplemented alternatives with their own verification work, not instant switches. OPERA vegetation disturbance must not be relabeled as confirmed forest loss.

### 4. Complete one real owner journey and release

Accept the pilot only after the owner can authenticate, inspect a genuine attributed observation, create a case, record review/action/follow-up, export its source-linked dossier and recover the database from a tested backup. Verify TLS, private API boundaries, credentials, rate limits, logging/health and the exact deployed release. Record source freshness/limitations and the deployment result. No broader public live access or personal/field uploads are implied.

### 5. Validate value before expanding

Use the synthetic preview for selected feedback while the live pilot is completed. With the owner's explicit outreach instruction, invite a few actual practitioners to complete a task, then seek one structured design-partner pilot. Measure time to review/assign, missing follow-up, report preparation and repeat use. Do not describe hypothetical pricing, demand or conservation impact as achieved.

## UI review session

Use actual rendered behavior and one continuous task. Prioritize the monitoring screen and source detail, then the case workspace, action/follow-up, dossier, queue/dashboard and source-health page. Ask at each point: what is known, what is uncertain, what can the user do next, and what proves it was saved? Check a narrow phone view, keyboard navigation and an empty/error state alongside the normal flow.

The redesigned opening provides a strong identity. For repeated operational use, assess whether its large introduction delays the saved-case queue, especially on mobile. Do not spend the next iteration only restyling the already redesigned homepage. The useful first experience is reviewing one observation and reaching a clear next step.

## Cost and user involvement

No new paid data, hosting or other recurring service was ordered in this assessment. The RADD dataset is documented royalty-free; the GFW API fee/quota remain unknown, not assumed paid or free. Existing OVH, backup entitlement, Codex usage and GitHub Actions allowance/billing are not inspected. Display an actual budget before any paid commitment.

The two useful owner checks are (1) whether the actual MyGFW account offers API-key creation and any shown price/limit, and (2) whether OVH Manager reports the VPS running at the expected address. Screens or text used for these checks must omit secrets. A domain purchase, ArcGIS upgrade, new database subscription or additional Cloud publication attempt is not a prerequisite to continuing code and design work.

## Verification in this assessment

- Python 3.12 API suite: 106 tests passed; one Starlette/httpx deprecation warning.
- Node 24 web suite: 19 tests passed; typecheck and production build passed.
- Isolated owner-demo browser flow: saved case, action, follow-up, closure, exact observation navigation and error/empty states passed with synthetic data. No separate Caddy gateway binary was supplied, so gateway authentication was not exercised in this run.
- Actual dashboard captures at 1440px desktop and 390px mobile were visually inspected; automated overflow and brand-bound checks passed. No WCAG certification is claimed.
- No current OVH deployment, live alert request, provider terms refresh, latest exact-commit CI status or new dependency audit was verified by these local checks. The handoff records an earlier successful GitHub run.
- Three original design skill folders were copied into this runtime's `/home/agent/.codex/skills/` and hash-verified, with concise UI-scoped user guidance. No existing skill/instruction was replaced. Repository copies remain available. The executor skill catalog still returned no entries; automatic discovery and persistence after runtime replacement/fresh-session startup are unverified. This is not account-wide sync and no reusable environment configuration was published.
