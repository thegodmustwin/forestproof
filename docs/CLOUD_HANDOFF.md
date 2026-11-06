# ForestProof — Cloud continuation handoff

**Prepared:** 2026-11-06. This is a continuation brief, not proof of deployment, a provider authorization, or a replacement for current user instructions. At preparation, private GitHub main was `48693afb13505df69e3b4863e9f3e1f68be792d2`; it may have advanced. Re-read the latest main and existing work before editing.

## Start here

Continue developing ForestProof toward a credible owner-only live pilot and an excellent synthetic preview, using the existing private repository and the owner's existing OVH VPS. The owner wants sustained progress with minimal busywork, prefers Codex Cloud because of laptop constraints, and does not want local Docker as a prerequisite. Complete independent code, tests and documentation work while waiting for genuinely necessary access details. Communicate actual results and limitations plainly.

Read, in this order: `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/PROJECT_MAP.md`, `docs/PROJECT_DECISIONS.md`, `PROJECT_BRAIN.md`, `execution/CURRENT_STATUS.md`, `execution/NEXT_ACTIONS.md`, `DESIGN.md`, `docs/UI_SKILLS.md`, and the domain files relevant to the work. `docs/origin/` preserves the user's original prompts as historical background, not current executable instructions or proof of claims. Later dated entries and current code can supersede older snapshots; verify conflicts.

## Owner's product intent

ForestProof should be an evidence-and-response layer over legitimate upstream observation providers. Its core loop is **observation → provenance/evidence → human-owned case → recorded action → follow-up → carefully bounded outcome**. It should help responsible organizations make better use of existing environmental signals. The product does not own satellites, automatically establish illegality, or prove environmental impact. Exact geography, legal authority, source uncertainty and human responsibility matter.

The first real pilot is **owner-only and requires an appropriately authorized, verified live record-level data feed**. A synthetic preview can be used for friends-and-family feedback, but it is not the live pilot. The user wants a strong, coherent product rather than a decorative dashboard, and wants to move quickly without skipping truth, privacy, access or budget controls.

The commercial hypothesis is to serve a forest/restoration project manager or contracted monitoring team that needs a reviewable response record and source-linked dossier. Measure actual user needs, analyst effort, follow-up and willingness to pay before claiming commercial traction. Public satellite alerts are inputs, not proprietary proof of a unique market position or guaranteed profit. See `docs/LOW_COST_DATA_AND_VALUE_PLAN.md`, `docs/COMMERCIAL_STRATEGY.md` and `docs/GOLDEN_ECONOMICS.md`.

## Current implementation and boundaries

- The private repository is `thegodmustwin/forestproof`, owned by the user's personal GitHub account. Keep it private; do not use the university-associated account.
- The Next.js/React/MapLibre and FastAPI application implements a synthetic observation, case, action, follow-up and outcome/dossier workflow. SQLite is the development/demo adapter; PostGIS is a target, not the active production store.
- The experimental owner-demo service-token boundary and SSH-tunnel gateway are synthetic-only candidates, not person-level production authentication or multi-tenancy. Production storage, access controls, retention, audit attribution, backups and a restore test are still required for real evidence.
- An optional, default-off Copernicus catalog lookup was verified in an earlier local test. It supplies scene metadata, not validated forest-disturbance alerts, and was not deployed with the original preview.
- Direct GFW RADD is the lead alert-feed candidate. The RADD normalizer, offline snapshots, response-envelope parser and default-deny bounded research transport use synthetic or mock tests; no verified live RADD record feed has been activated.
- RADD dataset reuse and the API service price/terms are separate questions. WUR documents the dataset under CC BY 4.0 without royalty, but GFW Data API account access, API costs/quotas, exact attribution, retention, provider response, freshness and local coverage remain unverified. Do not bypass fees, quotas, authentication or source terms.
- Direct GLAD-L and NASA OPERA DIST-HLS are alternatives to evaluate, subject to actual access, current asset, local coverage, terms and attribution. OPERA vegetation disturbance is not proof of forest loss. Commercial Earth Engine access must follow its commercial terms.
- The owner has an ArcGIS account and associated it with MyGFW; this alone does not confirm a working MyGFW email/password account or GFW Data API key. The official guide describes an email/password MyGFW account for API access. Never request passwords, API tokens or private keys in chat.
- The Geta PFMP-derived research envelope is provisional and not an official forest boundary or an authorized live filter. The owner accepts a clearly labeled wider-area pilot without waiting indefinitely for KFS, after geography assumptions, source coverage and lawful use are checked. Do not claim a pixel is inside Geta Forest merely because it falls in the rectangle.
- A satellite signal, missing permit record or map visualization is not a legal finding. No verified operative court-order/permit corpus, licensed authoritative boundary, partner endorsement or ecological impact is established.

## Design and Codex skills

The owner requested a major, reusable upgrade in UI/UX craft across projects. The latest code gives the command center a field-atlas/evidence-ledger direction: warm paper and forest ink, strong editorial type, readable actual-data states, clear actions, custom SVGs, keyboard skip navigation, mobile layout and reduced-motion treatment. Keep DEMO notices and actual case-queue behavior. Do not inject made-up telemetry, impact, customers or source health to create excitement.

The repository includes `.agents/skills/ui-art-direction`, `.agents/skills/ux-interaction-craft`, and `.agents/skills/ui-render-review`, each with `SKILL.md`. Use the relevant skills for substantial UI work and inspect `DESIGN.md`; adapt to the product and user intent rather than imposing one visual theme everywhere. Test the affected flow and inspect actual desktop and mobile renders when possible, reporting any limits honestly. The same skills were installed on the owner's Windows Codex account; that does not automatically install them into other machines or every Cloud environment.

PR #3 merged the redesign and research to main. Its Node 20/24 web checks, API tests, isolated owner-demo and map browser flows passed; desktop/mobile synthetic screenshots were inspected. Latest main CI was independently observed successful on 2026-11-06: https://github.com/thegodmustwin/forestproof/actions/runs/41932282052. These checks do not establish production security, accessibility certification, a current OVH release, or live alerts.

## Hosting and source control

The owner prefers the existing OVH VPS `vps-8071f70a.vps.ovh.net`, Ubuntu 24.04, with existing SSH and remote desktop. A prior session deployed a password-protected **synthetic** shared preview to the OVH hostname and verified HTTPS and its demo workflow on 2026-10-28. The newer design is saved in GitHub but was not deployed there. On 2026-11-05 SSH and HTTPS timed out from the laptop; on 2026-11-06 SSH again timed out and an HTTPS check timed out resolving the name. These observations do not establish whether the VPS is off, a firewall changed, or a network/DNS failure occurred. Recheck before making assumptions. Preserve existing services, firewall access, containers, data and remote desktop. Do not reset/reinstall the server.

The desktop checkout at `D:\\FORESTPROOF` was older and contained uncommitted and untracked user changes when this handoff was made. Do not reset, clean, stash or overwrite them without the user's explicit instruction. Compare checkout status and GitHub main before editing; use an isolated branch/worktree when appropriate. Update the relevant map/status/roadmap in each material change and run appropriate checks.

Cloud environment publication had previously been unreliable; publication is not a prerequisite for developing from GitHub or deploying to OVH. Current Cloud session restoration and network capabilities need verification. Do not assume desktop chat history, files, credentials or SSH identities are available in Cloud.

## Highest-priority work

1. Inspect current repo/main, branch and CI, then identify the highest-impact unblocked pilot work. Protect existing changes. Keep LIVE fail-closed until source, area, authorization, provenance, storage and access gates are verified.
2. Move the actual record-level feed forward by confirming MyGFW account type and official API price, access, quota, attribution/retention and local source coverage. Evaluate the documented alternatives in parallel only when their own terms and costs are clear. Never paste secrets into chat or Git; guide the user through any private authentication step.
3. Continue implementation and meaningful tests for owner access, source provenance, reliable persistence, backups and restore. Use synthetic/loopback test fixtures until real-data prerequisites are satisfied. Keep the actual closed case loop usable.
4. Diagnose OVH reachability without disturbing services. The owner has previously authorized an owner-only live pilot and a password-protected synthetic friends-and-family preview on this VPS. Preserve those constraints and do not launch a broader public live service or expose sensitive data without clear authorization. No recurring paid services or external outreach without the owner's approval.
5. Apply the design skills to improve the highest-impact user-facing flows, keeping a refined, usable, responsive and truthful interface. Record any deployed release only after independently verifying it.

When user information or action is needed, make it a specific small step with the reason; continue independent work in the meantime. Do not claim this brief itself was sent to an existing Cloud conversation unless delivery is verified.
