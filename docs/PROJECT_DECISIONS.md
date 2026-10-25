# ForestProof — decision and context ledger

This is the compact record of durable owner choices and important unresolved facts. Keep it current; do not use it to imply an implementation is complete.

## Confirmed owner choices

| Date | Decision | Consequence |
| --- | --- | --- |
| 2026-10-25 | Use the owner's personal GitHub account thegodmustwin and private repository thegodmustwin/forestproof; default branch is main. | Keep source private; don't publish or transfer to the university account. |
| 2026-10-25 | Continue development in Codex Cloud to reduce laptop capacity pressure. | Prepare a repository-backed Cloud environment; preserve context in GitHub because desktop chat history is not the project source of truth. |
| 2026-10-25 | Do not make local Docker a prerequisite for the owner's workflow. | Prefer Cloud setup and CI-equivalent Python/npm checks. Docker Compose may remain for optional use. |
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

- OVH service details: current public IP, OS/version, SSH access and key arrangement, firewall, backups, DNS/domain, TLS, runtime and deployment path.
- Codex Cloud: GitHub connection, selected repository, environment setup/publish result, actual test run from Cloud.
- Data: authoritative/lawfully reusable Aberdare AOI, one suitable record-level source, product license and attribution, latency/coverage, successful bounded request and provenance.
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

