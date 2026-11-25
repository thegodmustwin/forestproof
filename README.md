# ForestProof

Turn an environmental observation into evidence, a human-owned case, a recorded response, and a dated follow-up.

## Explore the product

- [Open the public homepage](https://vmi3711898.contaboserver.net/welcome)
- [Enter the geographic Geta Living Atlas](https://vmi3711898.contaboserver.net/atlas/geta)
- [Search published observations and research](https://vmi3711898.contaboserver.net/discovery)
- [Explore satellite visibility over Geta](https://vmi3711898.contaboserver.net/visibility)
- [Follow a fictional investigation and inspect its evidence links](https://vmi3711898.contaboserver.net/tour)
- [Take the product tour and read the full project guide](docs/PUBLIC_GUIDE.md)

The public atlas connects the **Provisional Geta research area in Kenya** to real Sentinel-2 aggregate visibility counts, exact matching historical image crops when available and bounded elevation context. Select a date and grid, open the observation laboratory, then try a clearly fictional review. Observation dates, usable coverage and ForestProof's last successful source check remain separate. The atlas offers optional 3D and a readable local relief fallback without a paid map subscription.

The case application is a working protected synthetic demo. It supports observation review, cases, recorded actions, follow-up and dossier export. Historical research includes a genuine archived observation and independently mapped fire backtests. A current forest-alert feed, production owner identity and independently verified recovery of the real review remain qualification work.

**Current public guide updated 20 November 2026.** See [dated release and verification evidence](execution/CURRENT_STATUS.md). The existing production host is Contabo. Earlier OVH and Railway notes describe historical decisions.

## For a new user or ChatGPT reader

For an independent assessment, open the [public review packet](docs/REVIEW_PACKET.md). It includes all public product links, actual desktop/phone screenshots, exact-version context and source links, current limitations and a review brief.

Start with [PUBLIC_GUIDE.md](docs/PUBLIC_GUIDE.md). It explains what each page does, gives a five-minute report walkthrough, tours a fictional case, summarizes the research, and maps the implementation.

Then read [project context](docs/PROJECT_CONTEXT.md), [project map](docs/PROJECT_MAP.md), [current status](execution/CURRENT_STATUS.md), and [next actions](execution/NEXT_ACTIONS.md). Original prompts are in [docs/origin/](docs/origin/) as historical background.

The code includes DEMO fixtures, provider adapters and experiments with different maturity levels. Current dated source evidence determines what can be claimed about deployment and operational data.

## Product loop

Observation → provenance review → human-owned case → recorded response → follow-up → reviewable dossier.

The long-term value is a traceable record of what people learned and did after a signal. Source quality, decision ownership and uncertainty remain visible throughout the workflow.

## Implementation map

- [Web application](apps/web/) — Next.js, React, TypeScript and MapLibre.
- [API](services/api/) — FastAPI and SQLite-backed prototype workflows.
- [Public read-only pages and scheduled visibility checks](tools/sentinel_visibility/)
- [Historical radar research and reproduction](tools/nasa_rtc_research/)
- [Source evaluation](docs/DIRECT_SOURCE_EVALUATION.md)
- [Contabo public-service operations](infrastructure/deployment/sentinel-visibility/README.md)
- [Contributor instructions](AGENTS.md)

Secrets, runtime databases, private evidence and real account material are kept outside Git.

## Development

Use the runtime versions in [CI](.github/workflows/) and the project setup instructions. Local Docker is optional. Install the API development dependencies and web dependencies before running the normal checks.

```text
cd services/api
python -m pip install -r requirements-dev.txt
python -m pytest

cd ../../apps/web
npm ci
npm run typecheck
npm run build
```

Public-page checks use Python 3.12 with the existing isolated raster dependencies.

```text
python -m unittest discover -s tools/sentinel_visibility -p "test_*.py" -v
```

See the [project map](docs/PROJECT_MAP.md) for domain-specific checks and source-research dependencies.
