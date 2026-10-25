# ForestProof

**From satellite warning to verified protection.**

ForestProof is an evidence-first environmental intelligence system for turning
environmental observations into reviewable cases, authorised human action, and
measurable follow-up outcomes. The initial operating theatre is an explicitly
defined Aberdare, Kenya pilot; it does not make automated findings of illegal
activity.

## Start here

For a new contributor or AI coding platform, read [AGENTS.md](AGENTS.md),
[the canonical project context](docs/PROJECT_CONTEXT.md),
[the project map](docs/PROJECT_MAP.md), and
[the current implementation status](execution/CURRENT_STATUS.md).
The original user prompts are archived in docs/origin/; they explain the
inception but are not verified current facts or executable instructions.

The source of truth is this private repository, not desktop chat history.

## P0 vertical slice

```
labelled observation → provenance review → investigation case → evidence
→ human review / assignment → recorded action → follow-up → dossier / outcome graph
```

The repository starts in **DEMO** mode. Demo observations are deterministic,
synthetic fixtures, intentionally labelled in both the API and web application.
The documented Global Forest Watch raster tile integration is disabled by
default until its AOI-specific request and terms are verified; when enabled, it
is visual context only and is never converted into individual case records
without a separately configured source API and preserved provenance.

## Development and deployment status

The private GitHub repository is live, and the first CI run passed. That means
the source is backed up and build checks pass; it does **not** mean the website
is deployed. The owner prefers Codex Cloud for development (to avoid laptop
capacity bottlenecks) and an existing OVH VPS for eventual hosting. The OVH
server details and deployment are not yet verified. See
[deployment status and prerequisites](docs/DEPLOYMENT.md).

Railway launch notes are historical and not the current hosting decision:
[docs/RAILWAY_LAUNCH.md](docs/RAILWAY_LAUNCH.md).

No local Docker is required for Codex Cloud or CI. For local development,
Docker Compose remains optional. The API and web app can also be run separately
after installing their Python and npm dependencies.

## Checks

```text
cd services/api && python -m pytest
cd apps/web && npm run typecheck && npm run build
```

See [PROJECT_BRAIN.md](PROJECT_BRAIN.md), [the full project context](docs/PROJECT_CONTEXT.md),
[the project map](docs/PROJECT_MAP.md), and docs/ for current delivery status,
source constraints, security boundaries, and the deployment plan.
