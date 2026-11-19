# FORESTPROOF Project Brain

## Living Atlas — 19 November 2026

Contabo serves the public Living Atlas homepage and dated Geta pass explorer. The protected demo uses the same design language for its command center, case desk, evidence review and saved-case lineage. Desktop/mobile public rendering and the actual saved synthetic case have been inspected. Read [the current release verification](execution/CURRENT_STATUS.md#living-atlas-release--19-november-2026) for exact source pins and map checks. That entry supersedes older deployment and rendering claims below.

The public coverage counts remain distinct from the protected synthetic case workflow. An operational record-level alert feed, actual owner identity and independently recoverable live storage remain separate launch requirements. The original Windows checkout and private research evidence are preserved.

## Public product guide — 18 November 2026

Read [the public guide](docs/PUBLIC_GUIDE.md) for the visitor journey and current hosted capabilities. The source repository and historical context have public read access at the owner’s request. Runtime credentials and private research evidence remain in protected storage.

New contributors and AI platforms: begin with [AGENTS.md](AGENTS.md),
[PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md), and
[PROJECT_MAP.md](docs/PROJECT_MAP.md). Original inception prompts are archived
under docs/origin/ as historical material, not verified current facts.

**Current hosting and preview (verified 2026-11-13):** Contabo `vmi3711898` serves the protected synthetic preview at pinned source `38881dc79f04de9d21997fe85dea8712ef78e91d`. Its shared tester gate, DEMO API, upload denial, TLS and local SQLite snapshot/restore were checked; the deployed browser rendering and off-host production recovery were not. This is not a live or owner-authenticated production pilot. Keep RDP private and preserve other projects. The old OVH alias `content-engine-vps` is historical. See [deployment context](docs/DEPLOYMENT.md) and [release checks](execution/CURRENT_STATUS.md).

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
| Deployment | WORKING (PROTECTED SYNTHETIC PREVIEW ONLY) | Contabo serves pinned release `38881dc` behind HTTPS and shared tester access. Gateway and API upload denial, DEMO health/source labels and a local SQLite restore passed. The deployed browser was not visually inspected. Person-level owner identity, off-host production recovery and a live pilot remain unfinished. OVH and Railway deployment notes are historical. See execution/CURRENT_STATUS.md. |

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
