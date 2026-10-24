# ForestProof

**From satellite warning to verified protection.**

ForestProof is an evidence-first environmental intelligence system for turning
environmental observations into reviewable cases, authorised human action, and
measurable follow-up outcomes. The initial operating theatre is an explicitly
defined Aberdare, Kenya pilot; it does not make automated findings of illegal
activity.

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

## Launch a hosted beta (no local Docker)

The repository is prepared for a two-service deployment on Railway: a public
Next.js web application and a private FastAPI service with a persistent volume
for the explicitly labelled demo database and synthetic evidence fixtures.
The web application proxies API calls over Railway's private network, so the
mutable demo API does not need a public domain.

Follow [the Railway launch guide](docs/RAILWAY_LAUNCH.md) after pushing this
repository to your personal GitHub account. This produces a real hosted beta,
not a claim that live satellite, legal, or enforcement feeds are active.

## Run locally

1. Copy `.env.example` to `.env` and leave live-source keys empty unless you
   have approved credentials.
2. `docker compose up --build`
3. Open `http://localhost:3000` and `http://localhost:8000/docs`.

The first Compose build needs Docker registry and package-network access. No
paid service is required for local demo mode.

## Checks

```text
cd services/api && python -m pytest
cd apps/web && npm run typecheck && npm run build
```

See [PROJECT_BRAIN.md](PROJECT_BRAIN.md) and `docs/` for current delivery
status, source constraints, security boundaries, and the deployment plan.
