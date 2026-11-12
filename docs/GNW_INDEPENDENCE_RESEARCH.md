# GNW independence and ForestProof differentiation research

**Research date:** 2026-11-12. This is a source-backed strategy brief, not evidence of an implemented live feed, legal advice, a public deployment, verified costs, or commercial demand.

## Decision in plain language

ForestProof can own its application, monitoring workflow, database, deployment, and integration contracts while using appropriately licensed observation products. Eliminating one API dependency is different from independently producing alerts from satellites. The source, source-processing service, data host, software licence, and operating infrastructure are separate dependencies; a self-hosted analysis can still depend on a WRI-hosted S3 bucket. Use a provider-neutral contract with source-specific adapters, source/version/receipt provenance, explicit uncertainty and independent source-health states. Never silently replace unavailable LIVE records with DEMO fixtures.

A sensible near-term experiment is to compare one lawfully usable primary feed against a second direct-source option over a small, clearly described area using separately verified access, costs, retention rights, and coverage. Keep the GNW API key as an option; creating a key does not confirm alert access, API price, quota, or source terms. A direct source is an alternative, not a promise of free operations or independence from all providers.

## What GNW already provides

GNW/GFW aggregates forest-change and context datasets, versioned assets, spatial and tabular APIs, and map/analysis interfaces. Its public [Data API documentation](https://data-api.globalforestwatch.org/docs) describes dataset versions, source files, multiple assets, queries, downloads, and analysis. The [open data portal](https://data.globalforestwatch.org/) provides dataset discovery and describes public API/developer tools. These operational capabilities (integrating many datasets, refresh, coverage, traceable data, infrastructure, user trust and distribution) are potential advantages; the relative strength and cost of each are hypotheses, not a verified valuation of WRI's position.

Crucially, GNW already offers more than a map: [Forest Watcher](https://forestwatcher.globalnaturewatch.org/) describes offline access, investigations, reports, areas of interest and contextual data; its [team-management guide](https://globalnaturewatch.org/help/forest-watcher/guides/manage-teams-forest-watcher-web/) describes teams, assignment, report templates, review and downloads. Do not claim that field reporting, assignments or an observation-to-action workflow alone are unprecedented. Comparing the current products and a target user's unmet needs remains an empirical task.

## Concrete reusable public assets and restrictions

- WRI's [GNW Self-Hosted Monitoring repository](https://github.com/wri/gnw-self-hosted-monitoring) is Apache-2.0 licensed. Its README describes scripts for geometry-based post-2020 deforestation risk/disturbance-alert analyses and direct land-use-change emissions factors. Its default analysis reads GNW S3 buckets, and an alternative is to download the relevant datasets locally for reliability, scalability and lower access costs. This is a useful evaluation candidate, not a proven replacement for a live alert feed, not independent satellite detection, and not proof of free S3 use, applicable commercial rights, coverage, or compatibility with ForestProof. The linked detailed documentation was not machine-readable in this research session; inspect it and each data manifest before relying on claims beyond the README.
- WRI's [GFW frontend repository and MIT licence](https://github.com/wri/gfw/blob/develop/LICENSE) permit code reuse subject to the licence's notice conditions. Code licensing does not grant rights to every dataset, visual brand, external dependency, hosted endpoint or trademark.
- WRI's [GFW Data API repository](https://github.com/wri/gfw-data-api) is public, but no repository-level licence was identified in the inspected repository listing. Visibility and source availability alone do not establish permission to reuse its code commercially. Verify an applicable licence or receive permission before copying code; independently implementing concepts is a separate question.
- [GNW terms](https://globalnaturewatch.org/terms/) state that API use in products requires API attribution and that each dataset has its own licence and restrictions. Data use, source API usage, licensing of code, and use of names/logos are distinct. Respect authentication, rate limits and service terms; do not bypass them or copy private customer data or credentials.
- The [Wageningen University RADD page](https://www.wur.nl/en/research/products-services/radd-forest-disturbance-alert) states the RADD dataset is royalty-free under CC BY 4.0 with attribution. That is not evidence that the GNW Data API has no fees or that a particular direct-host workflow is free. Commercial rights, geographic coverage, distribution method, update frequency, exact attribution, product access, and onward-retention conditions must be checked for each chosen pathway.

## Direct provider candidates (research only)

- **GLAD-L**: [University of Maryland's GLAD forest-alert product](https://glad.umd.edu/dataset/glad-forest-alerts) offers direct download of Landsat-based pantropical alert data, approximately 30 m. Current Kenya tiles, update latency, access, licence and commercial suitability remain to be verified. Do not assume GLAD-S2 covers Kenya: the researched GLAD-S2 release is Amazon-focused.
- **NASA/UMD OPERA DIST-HLS**: [NASA JPL's DIST product suite](https://www.jpl.nasa.gov/go/opera/products/dist-product-suite/) describes 30 m DIST products and validated HLS products available through LP DAAC / Earthdata. [UMD explains](https://glad.umd.edu/dataset/DIST-ALERT) that DIST covers vegetation loss and generic spectral disturbance. Do not call all such alerts deforestation. Verify a current bounded Kenya tile, product availability and freshness, direct access and relevant licence/attribution and actual storage/transfer costs.
- **RADD**: Wageningen's published CC BY 4.0 terms support investigation, but a suitable current direct distribution route, update timing, Kenya pilot coverage and downstream terms are not yet verified. The Geta research envelope is not an official mask.

All are research candidates, not activated feeds; the lead RADD decision remains in force unless explicitly revised. No provider alert-record query or feed integration was performed here.

### Self-hosted monitoring special terms

WRI's [August 2026 GNW Self-Hosted Monitoring terms](https://www.wri.org/about/legal/gnw-shm-tos) are in addition to relevant general/Horizon terms. They describe default code/data licences with dataset-specific exceptions and approvals, require prescribed attribution, prohibit implying endorsement, and make the user responsible for third-party cloud compute, storage, and data-transfer costs. They also disclose access logs that may indicate approximate areas being analyzed when querying WRI-hosted objects; copying a suitable dataset to one's own environment may mitigate that particular exposure, subject to access and terms. The terms describe broad treatment of feedback, so avoid submitting proprietary or sensitive material. This summary is not legal advice.

## A defendable product hypothesis

ForestProof's possible differentiation is the accountable review and follow-up workflow for a clearly defined customer with a real operational duty: provenance and uncertainty; source and boundary version; assigned human decision; documented action; follow-up; access-controlled, exportable evidence; and verified recovery. Possible defensibility could grow from a lawful, consented history of completed workflows, a product adapted to a specific institutional process, reliable integrations, trusted local context and user relationships. These are hypotheses: current project documents establish no customer, entitlement to official boundaries, institutional partnership, measurable environmental impact, exclusive data, proven legal finding, or validated willingness to pay.

Validate against the free Forest Watcher baseline before claiming an advantage. With explicit owner authorization, observe a real practitioner completing an alert-to-response task and compare completion time, quality of evidence, missing follow-ups, audit requirements, and willingness to pay. Permissions and security must be designed before collecting personal or sensitive field information. A satellite signal or a missing online permit is not proof of illegal activity.

## Evaluation and operational cost

For each candidate (GNW API, WRI self-hosted analysis, a direct licensed source), record:

1. A precise data product/version, producer and supported source URL; real update and historical-coverage evidence for the intended Kenya pilot geography.
2. Licence, attribution, redistribution/retention and commercial-use restrictions, including applicable third-party boundary and basemap terms.
3. Any account, authorization, network, rate-limit and access prerequisite; no key, token, private field data or credentials in chat, logs or Git.
4. Expected time-to-availability, observable freshness, missing-data and error semantics; differences between vegetation disturbance and deforestation.
5. End-to-end operating costs: compute, disk, bandwidth/egress, backups, monitoring and human operations. Do not treat royalty-free data as zero infrastructure cost.
6. A small bounded, explicitly authorized test, provenance record, recovery exercise, and a synthetic-first integration path. No RADD record query has yet been performed in this project.

Treat the Geta research envelope as provisional, not an official forest boundary or approved operational filter. Obtain official/source-linked geography and terms when available; a wider, accurately described area still needs verification before use. Keep RADD candidate details and alternatives separate until actual product semantics are verified.

## Next actions

- Compare Forest Watcher's documented baseline with one proposed high-value institutional workflow. Do not contact potential users or providers without owner authorization.
- Inspect the GNW self-hosted monitoring manifests, dataset availability, network access, licences and costs read-only; do not deploy or copy code until the relevant licence is reviewed.
- Resolve Data API price/quota and exact source attribution/retention and independently verify candidate feed coverage before activation. The 2026-12-31 retirement of [GFW Pro and its Pro API](https://pro-news.globalforestwatch.org/news-events/gfw-pro-is-consolidating-into-global-nature-watch) does not establish that the separate Data API retires.
- Continue a separately protected synthetic preview and independent owner-access, persistence, restore, and source-neutral contract work. Do not expose real evidence until security and restore gates are verified.
