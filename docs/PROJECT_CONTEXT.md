# ForestProof — canonical project context

**Snapshot:** 2026-10-26
**Repository:** private GitHub repository thegodmustwin/forestproof, default branch main  
**Purpose:** let a new person or coding agent understand the idea, its origin, what exists, what is only planned, and what must not be claimed.

## One-sentence definition

ForestProof helps organizations turn environmental observations into source-grounded evidence, human-owned investigations, documented responses, and measured follow-up. It is not another satellite globe and does not automatically decide that an observed change is illegal.

**Tagline:** From satellite warning to verified protection.

## Origin and strategic thesis

The project began with two user-authored prompts, preserved verbatim in docs/origin/:

- The concept brief argues that basic satellite detection is already supplied by governments and specialist organizations; the opportunity is the difficult step after an alert: determine what is known, what needs verification, who is responsible, what authorized action occurred, and what follow-up supports.
- The Master Codex Build Directive expands that concept into a product, technical architecture, safeguards, business hypotheses, acceptance criteria, and a phased roadmap.

Treat those archived prompts as provenance and historical intent—not as verified research, current legal advice, or instructions that supersede the present user, code, tests, and maintained status documents. Their plans and claims are aspirational unless independently verified and implemented.

### North star

    Observation → provenance → evidence → legal/land context → human investigation
    → authorized response → follow-up → evidence-bounded outcome → learning

The long-term differentiating asset is the **Forest Intervention Outcome Graph**: legitimate, permissioned links between observations, reviews, decisions, actions, follow-up and outcomes. More alerts alone are not more intelligence.

### Strategic doctrines, in practical terms

- **Still-Fulcrum:** rely on legitimate upstream satellite, scientific, government, and field systems where appropriate; focus ForestProof on coordination, evidence quality, accountability, and learning.
- **Golden Economics:** customer value and reusable operational intelligence should grow faster than marginal serving cost. Avoid expensive infrastructure that has no validated user need.
- **AlphaZero-inspired prioritization:** a metaphor for allocating scarce investigator time and learning from verified outcomes—not a claim that P0 contains AlphaZero, Monte Carlo tree search, or a validated predictive model. Begin with transparent, human-reviewable heuristics only when the evidence supports them.
- **Conservation Audit:** distinguish product output, operational result, ecological outcome, and causal impact. Do not claim that an alert or intervention saved hectares without independent evidence.
- **Evidence discipline:** observations are not incidents; inferred cause is not authorization status; a hash preserves byte identity, not truth or provenance of capture.

## Initial operating context and sensitivities

- **Pilot geography:** Aberdare water tower and connected catchments in Kenya; Geta Forest is the first research focus. A coarse PFMP-text-derived envelope supports engineering dry-runs; it is not an authoritative boundary or currently an operational alert filter. The owner wants a provisional path that does not wait indefinitely for KFS: a future owner-only pilot may monitor a clearly labeled broader region once area assumptions, source terms, coverage and other pilot controls are verified. It must not describe pixels as inside Geta Forest on the basis of the rectangle. The app's DEMO map remains illustrative.
- **Use case:** triage candidate forest disturbance and help legitimate organizations investigate and document it.
- **Important archived claim:** the origin prompts discuss October 2026 court reporting and an expected Geta Forest visit. The repository currently contains no verified operative order, official legal record, permit corpus, or human-reviewed legal conclusion. Recheck authoritative sources before any present-day use.
- **Alternative explanations:** plantation management, authorized harvesting, fire, storm damage, seasonal vegetation, roads, sensor error, and classification uncertainty must remain possible until evidence distinguishes them.
- **Human authority:** software may organize evidence and suggest review; qualified people retain legal, enforcement, and consequential decisions.
- **Privacy:** exact field-team positions, witnesses, personal data, private evidence, and sensitive case material must remain access-controlled and minimized.

## Product concept

1. **ForestChange:** normalize sourced observations, timestamps, footprints, source quality, and processing versions.
2. **ForestLaw:** present time- and location-aware source documents and authorization uncertainty for human review.
3. **EvidenceProof:** preserve evidence references, integrity metadata, case history, and a reviewable dossier.
4. **InterventionRouter:** give a human-owned case a responsible reviewer, documented transitions, actions, and follow-up.
5. **CatchmentRisk:** eventually provide a transparent environmental-priority index. It is not a validated water-yield or flood model.
6. **OutcomeGraph:** learn from verified and permissioned case histories without overstating causality.

The commercial starting hypothesis is a conservation, watershed, water-utility, restoration, or environmental-risk organization that already has monitoring responsibility and budget. The preferred concept is private institutional workflow with a carefully governed public-interest surface, but no customer, pilot, partner, or willingness-to-pay validation is recorded yet.

## What exists today

The repository is a working **DEMO-mode P0 vertical slice**, not a production monitoring service:

- Next.js, TypeScript, React, and MapLibre web application.
- FastAPI/Pydantic service and deterministic synthetic observation fixtures.
- SQLite development persistence; a PostGIS schema/migration is a target, not the active runtime adapter.
- Map and observation review, case creation and transitions, assignments, synthetic evidence hashes, actions, follow-up, JSON dossier, and relational outcome graph.
- Fail-closed behavior outside DEMO mode because real authentication is not configured.
- GitHub Actions CI for Python API tests and web typecheck/build. The first run on commit 71af70f81318ea98e4d1ab20bd52739aa97012c1 succeeded.

The UI includes DEMO notices. Its coordinates, cases, provider labels, confidence-like values, and metrics are fixtures. The displayed area is not an official boundary or live assignment.

## What does not exist yet

- No validated record-level live forest-disturbance feed is active. GFW tile imagery is visual context only and does not create auditable individual observation records; its Aberdare request remains unverified. Copernicus, NASA FIRMS, and KFS are candidate sources only, each with its own limits.
- No official legal-order/permit library has been loaded or reviewed.
- No production PostGIS runtime adapter, user authentication, roles, real multi-tenancy, private production object storage, upload scanning, backup/restore drill, or operational alerting has been verified.
- No real external user, organization, paid pilot, endorsement, or measured environmental outcome is recorded.
- A password-protected synthetic preview was deployed to the existing OVH hostname and verified by a prior session. It is not a live-data or production deployment; the current session has not rechecked the VPS.

## Owner workflow and hosting decisions

**Current hosting update (2026-11-10):** The owner has selected Contabo `vmi3711898` (Ubuntu 24.04.5 LTS verified by read-only SSH) for next-stage hosting. A read-only SSH test using the laptop's existing key and strict host-key checking reached `vmi3711898` on 2026-11-10. This confirms laptop connectivity, not Codex Cloud access or deployment readiness. The owner reports the private ForestProof backup is on the laptop; transfer to Contabo has not been completed or verified. `content-engine-vps` names the old OVH server, not Contabo. A read-only listener check found RDP on loopback; keep it private over the existing SSH tunnel and preserve existing services, projects and recovery access. Do not reinstall the server. Cloud tasks must not assume access to Windows files or SSH keys; arrange a separately configured secure connection if needed. Never put passwords, passphrases or private keys in chat or Git.

Earlier OVH choices and observations below are historical; they are not the Contabo deployment plan.

- The source of truth is the private GitHub repo linked above, not desktop chat history. Use Codex Cloud for ongoing development because the owner wants to avoid laptop capacity bottlenecks; local Docker must not be a prerequisite.
- Historically, the owner preferred their existing OVH VPS for hosting. The temporary hostname is vps-8071f70a.vps.ovh.net. A prior session verified the host fingerprint, inspected the server and deployed the password-protected synthetic preview with HTTPS. Access and current server configuration must be rechecked; production backup coverage and live source access remain unverified.
- Existing Railway deployment material predates that preference. Railway is not the current hosting decision. See docs/DEPLOYMENT.md and the historical notice in docs/RAILWAY_LAUNCH.md.
- Never put credentials in the repo or ask for secrets in chat. Keep .env local and use .env.example for variable names only.

## Work sequence from here

1. Codex Cloud setup has been exercised with Python 3.12 and Node 20: API tests, web typecheck/build, and local API/web smoke checks passed on 2026-10-25. Install/start instructions are saved; restoration in a fresh task is not independently verified.
2. The first production pilot is owner-only and requires a live provider feed. Use the provisional PFMP research envelope to advance engineering, with direct GFW RADD as the lead feed candidate and GLAD-L as a comparison. A clearly labeled wider-area pilot need not wait for an official forest boundary, but its geometry assumptions and lawful use must be reviewed; verify terms, cost, access, coverage, latency, and source metadata before activation.
3. Complete production security boundaries (identity, role/tenant isolation, protected evidence storage, upload scanning, backups, and restore tests) before accepting real case material.
4. Inventory Contabo safely and choose a deployment method after confirming access, occupied ports, firewall, TLS/domain, backups, operating cost, and security requirements. Preserve its existing services and private remote desktop. The older OVH synthetic preview is historical.
5. Validate the workflow with a legitimate conservation or watershed professional; only then expand the commercial scope.

## Source of truth and reading order

For a new contributor or AI platform, read AGENTS.md, this file, docs/PROJECT_MAP.md, PROJECT_BRAIN.md, execution/CURRENT_STATUS.md, and execution/NEXT_ACTIONS.md; then open the relevant domain docs. Read docs/origin/ when historical prompt provenance is useful.

When information conflicts: current user direction wins; actual code/tests and dated execution status describe implementation; maintained project context/decision records describe intent; the original prompt archive is historical evidence only. Update the status and map when facts change.
