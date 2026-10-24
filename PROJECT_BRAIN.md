# FORESTPROOF Project Brain

## Purpose

ForestProof is an environmental-intelligence and evidence-workflow platform. Its first operating context is the Aberdare water tower in Kenya. The product does not decide whether activity is illegal. It helps authorized people turn a sourced environmental observation into a reviewable case, documented response, and evidence-backed follow-up.

**Tagline:** From satellite warning to verified protection.

## P0 outcome

The first coherent vertical slice is:

1. Ingest a clearly labelled DEMO observation, or a live observation only when an approved provider is configured.
2. Preserve source, geometry, timestamps, method, quality flags, and processing version.
3. Show it on an Aberdare monitoring map and open its provenance.
4. Create a human-owned investigation case.
5. Attach evidence, record assignment, review, and action, and append an audit event.
6. Record a follow-up outcome with uncertainty.
7. Produce an EvidenceProof dossier.

## Non-negotiable evidence rules

- An environmental observation is not an incident, accusation, legal conclusion, or proof of harm.
- Keep observation, publication, ingestion, investigation, and follow-up timestamps separate.
- Show what is observed, derived, inferred, verified, unknown, and disputed separately.
- Preserve original source metadata and uploaded evidence hashes.
- Never present DEMO records as Kenyan incidents or current environmental statistics.
- Legal context is source-grounded, time-aware, and requires qualified human review for consequential conclusions.
- External escalation requires authorized human approval.

## Current implementation truth

| Area | Status | Meaning |
| --- | --- | --- |
| Application vertical slice | WORKING (local) | The API seeds deterministic observations, creates cases, preserves evidence hashes, gates workflow steps, produces dossiers, and serves the map UI; automated verification is recorded in `execution/CURRENT_STATUS.md`. |
| DEMO mode | WORKING | Synthetic records carry explicit DEMO quality flags and are isolated from live-provider code paths. |
| Live forest-alert provider | DOCUMENTED_NOT_TESTED | No provider is represented as operational until credentials, licence, AOI coverage, and ingestion are verified. |
| Legal corpus | PLANNED | No court order or permit is treated as authoritative until an official source and human review are recorded. |
| Outcome Graph | WORKING (P0) | A relational observation → case → action/follow-up graph is exposed; it does not assert environmental causality. |
| Commercial deployment | DEFERRED | No paid service, public deployment, or external notification is authorized by this document. |

## Product boundary

ForestProof coordinates evidence and workflow above upstream observation providers. It does not operate a satellite constellation, replace Kenya Forest Service, make legal findings, or claim that alerts prevented deforestation.

## P0 priorities

1. Reliable, timestamped, source-attributed observation ingestion.
2. Defensible evidence and case records.
3. Closed review/action/follow-up loop.
4. Clear DEMO versus LIVE separation.
5. Tests for integrity, geometry, workflow, and access controls.

## Deferred until evidence warrants it

- Predictive disturbance models and automated prioritization beyond transparent heuristics.
- Multi-sensor corroboration claims.
- Offline field synchronization.
- Billing, public portal, integrations, and global expansion.
- Causal claims about water yield, enforcement, or conservation impact.

## Decision record convention

Material design decisions belong in the relevant document under a dated Decision record entry. Implementation status must use one of: WORKING, PARTIAL, PLANNED, BLOCKED, DEFERRED, or DOCUMENTED_NOT_TESTED.
