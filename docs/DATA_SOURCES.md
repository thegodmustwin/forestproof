# Data Sources

## Status and operating rule

Live integrations are DOCUMENTED_NOT_TESTED unless this file is updated with a verification date, successful health check, applicable licence decision, and implementation status. Documentation access is not proof that a feed is operational, commercially reusable, or appropriate for the Aberdare area of interest.

No source below is currently represented as a validated production forest-alert feed. An opt-in, owner-demo-only Copernicus scene-metadata lookup is separate from alert ingestion.

## Current engineering choice (not an activation decision)

Keep **GFW RADD** as a radar candidate for explicitly covered locations and **GLAD-L** as an optical comparison. The provisional Geta rectangle has recent Sentinel-1 acquisition footprints. A bounded map check showed sparse RADD coverage colour, and the native eligibility raster still requires verified data access and a bounded native value check. Local processing, terrain effects, source terms, API fees, quotas and the response shape remain unverified. The mixed **GFW Integrated Alerts** product remains a separate candidate. [Local source checks](DIRECT_SOURCE_EVALUATION.md#radd-baseline-and-radar-acquisitions--2026-11-14)

## Candidate source manifest

### Global Forest Watch / World Resources Institute

- **Official organization:** World Resources Institute (WRI)
- **Official URLs:** https://www.globalforestwatch.org/ ; https://data-api.globalforestwatch.org/openapi.json
- **Tile cache:** https://tiles.globalforestwatch.org/
- **Products to evaluate:** GLAD-S2, RADD, integrated disturbance alerts, forest-change and protected-area context.
- **Known documented access:** GLAD-S2 and RADD dynamic raster tiles are available through the tile cache, such as the GLAD-S2 dynamic tile path umd_glad_sentinel2_alerts/{version}/dynamic/{z}/{x}/{y}.png with documented filters including latest, start_date, end_date, and confirmed_only.
- **Critical limit:** tile-cache overlays are imagery/map context, not per-alert case records. They cannot alone supply an auditable individual-alert feed.
- **Machine-readable queries:** GFW Data API access requires an API key or OAuth according to its OpenAPI description. Source status for API use is AVAILABLE_WITH_CREDENTIALS; it is not yet verified in this project.
- **GLAD-S2 documentation to validate at activation:** Sentinel-2 based, 10 m product, nominal five-day revisit, cited under CC BY 4.0 in GFW materials. Recheck current product terms and attribution before enabling.
- **Known limitations:** alert does not prove cause, authorization, or illegality; latency and coverage vary by product.
- **Operational status:** DOCUMENTED_NOT_TESTED.

**2026-10-21 bounded access check:** the documented `latest` endpoint redirected to a dated version; a single attempted development tile request then returned `404`. This does not prove the provider is unavailable, but it means ForestProof has **not** verified an Aberdare-ready overlay request. The UI therefore treats the layer as optional context and the source remains `DOCUMENTED_NOT_TESTED`.

**2026-10-26 read-only API catalog check:** fetched the official OpenAPI document (version 0.3.0) and public dataset catalog over HTTPS. The catalog listed current daily `geostore__glad__daily_alerts` and `geostore__integrated_alerts__daily_alerts` versions (`v20261025`). Their fields include alert dates, confidence fields, and alert counts/areas. OpenAPI marks the dataset query operation as requiring an API key (`x-api-key`) or OAuth; catalog and schema reads are public. No alert records were queried. The geostore-specific version records did not expose license/cost details. The dataset-level `gfw_integrated_alerts` record below lists CC BY 4.0; the API service terms and any access fees still need review. On 2026-10-26, the owner published the Cloud egress settings for `www.globalforestwatch.org` and `data.globalforestwatch.org`; the catalog/API remain reachable, but the Terms page still fails with an outbound tunnel 403 from this environment.

**2026-10-26 access/cost clarification:** the dataset HTML page links to GFW's Terms of Service at `https://www.globalforestwatch.org/terms`. The published Cloud egress configuration includes this host, but fetching the terms page still returns an outbound tunnel 403. The OpenAPI schema and dataset catalog do not publish query prices or rate limits. OpenAPI also exposes a generic point/zoom `GET .../features` operation without an auth requirement in its schema, but it is not established that this route can provide the integrated alert records, what its limits are, or whether its terms differ. Do not infer that GFW service access is free from the CC BY 4.0 dataset license. No GFW account, key, alert-record query, or paid service has been created or used for ForestProof.

**2026-10-26 product/version comparison:** public metadata lists `wur_radd_alerts` at `v20261018` (Sentinel-1 radar, 10 m, weekly, humid tropical forest areas in sub-Saharan Africa among other regions; Africa coverage from January 2019) and `umd_glad_landsat_alerts` at `v20261025` (Landsat, 30 m, daily updates between 30°N and 30°S). Both list CC BY 4.0. These are direct-source candidates to compare with the daily `gfw_integrated_alerts` product; no local Geta coverage has been tested. The integrated layer upsamples GLAD-L from 30 m to its nominal 10 m grid, and GLAD-S2's documented primary-humid-forest coverage is South America, so do not describe the integrated layer as uniformly native 10 m or assume GLAD-S2 contributes alerts in Geta.

**Observation unit:** public `/fields` metadata for the integrated product (`v20261026`) and direct RADD product (`v20261018`) lists raster pixel values such as `latitude`, `longitude`, `area__ha`, source-specific dates, confidence, and intensity; the 81 listed fields contain no provider event ID. Treat these as source raster-cell observations, not provider-defined event records. A ForestProof grouping would be a separate derived entity with a documented algorithm/version and links back to source cells. Preserve cell locations, source dates, confidence semantics, product/version, and raw response references; do not invent a provider ID or imply a derived cluster is a legal incident.

`services/api/app/providers/raster_identity.py` generates a stable `forestproof:raster-cell:v1:` key from product, rounded WGS84 cell center, and source observation date. `services/api/app/providers/gfw_radd.py` now normalizes one field-shaped RADD row using catalog field names and retains raw fields, release version, date, and uninterpreted confidence values. Its tests use synthetic inputs. The provider HTTP envelope, persistence path, clustering, source terms, and LIVE ingestion remain unverified and disabled.

**2026-10-27 offline progress:** `radd_snapshot_store.py` adds a standalone SQLite prototype for synthetic cell/release snapshots with canonical source fields, a content hash, replay detection and transactional conflict handling. It is not connected to provider requests or production persistence. The GFW terms URL redirects to `globalnaturewatch.org/terms`; that destination is blocked by this workspace's outbound proxy, so applicable terms and API costs remain unknown. No live records were requested.

**2026-10-29 bounded research candidate:** `gfw_radd_research.py` adds a standalone, default-deny HTTP request candidate with explicit caller attestations, a small geometry, limited rows and bytes, header-only key, redirect rejection and no automatic retries. It is not wired to a route or worker, and all tests use synthetic data or loopback-only mocks. Caller attestations are not evidence; actual API cost, account and query behavior remain unverified. Public `/fields` metadata was fetched without querying alerts; it listed RADD confidence values 2/3/4 as nominal/high/highest, while actual source rows and local coverage remain unverified. Do not infer that a small requested area or row limit establishes zero provider cost.

**2026-10-27 owner-supplied terms text:** The owner copied the Global Nature Watch Terms of Service from the redirected page into the conversation. The banner identifies Global Forest Watch as now Global Nature Watch. This is owner-supplied page text rather than a direct retrieval by this workspace; the text did not provide an effective date. The copied text's UTF-8 SHA-256 is `89c17cf4afd159929aea6475ba0d96507a3a999beced920f6792a4738367b3b8`. The original source is https://www.globalforestwatch.org/terms (redirecting to https://globalnaturewatch.org/terms). Recheck the current original when network access allows.

The supplied WRI terms say API requests must include an account API key, API use in products requires attribution under linked requirements, and each dataset carries its own license. They prohibit overburdening the service and allow WRI to change APIs or suspend access. They give separate eligibility conditions for **Global Nature Watch Pro**; those conditions are not evidence that a general Data API account has the same requirements. General submitted content carries a broad service-use license; the text separately describes Forest Watcher/Pro content as confidential under its conditions. Do not submit confidential material without checking the applicable terms and intended submission path.

The copied terms did not state a price, free tier, quota, retention policy, or rate-limit figure. The $100 figure in the text concerns a liability limitation, not a subscription or API price. The linked API attribution requirements at https://resourcewatch.org/api-attribution-requirements were not accessible from this workspace (proxy 403). The public OpenAPI says default API keys are valid for one year and documents header and query key mechanisms; it does not establish the owner has access or specify pricing. Prefer server-side header handling to avoid exposing keys in URLs. Exact attribution, service costs/quotas, retention, account access and local coverage remain unverified. No credential was created, data submitted, alert query made, or feed enabled.

The catalog also exposes the source product `gfw_integrated_alerts`, latest version `v20261026`. Its metadata says daily updates, a nominal 10 m grid, 30°N–30°S coverage, and CC BY 4.0 attribution. It combines GLAD-L, GLAD-S2, and RADD, but their coverage differs: GLAD-L spans the tropics at 30 m and can flag plantation harvesting; RADD is 10 m, weekly, and limited to primary humid forest; GLAD-S2's listed coverage is primary humid forest in South America, so it should not be claimed for Geta. The integrated record exposes source-specific dates and confidence fields. Its own cautions say detections may be fire, storm, disease, or harvesting; alerts are not legal findings or reliable area estimates; recent alerts can be false positives and records may later be revised or removed. Integrated alerts are a strong comparison candidate alongside direct RADD and GLAD-L, not a selected source until actual local coverage, exact API terms/cost, and a bounded query are verified. Preserve each component's actual sensor and resolution rather than presenting all alerts as native 10 m.

The same catalog lists UMD/GLAD/NASA DIST-ALERT as a comparison candidate: global 30 m coverage, CC BY 4.0, with weekly updates in Global Nature Watch (underlying observations every 2–4 days). Its 30% vegetation-reduction threshold reduces noise, but it detects vegetation change in crops and plantations as well as forests, so it is broader and less forest-specific than the integrated tropical alert product.

## Cost and billing guardrail

- A dataset's open license is not proof that its API, hosting, quotas, or redistribution path have no charges. Record the data license separately from API/service fees and rate limits.
- GFW API pricing remains unverified; do not query or activate that alert feed until this is resolved and the owner approves any non-zero or recurring cost. Copernicus describes free worldwide access and a free tier with quotas; bounded anonymous scene-catalog requests have been tested without an account or billing. This does not establish zero cost for every Copernicus service, commercial use, or OVH traffic.
- Prefer existing owner-paid OVH capacity and no-new-service designs while the owner-only pilot is being proven. Do not create paid accounts, subscriptions, overage use, or recurring services without explicit approval.
- Track any verified monthly/annual host cost, source API fee/quota, storage/backup/egress cost, and attribution obligations in `docs/COSTS_AND_OPERATING_BUDGET.md` before production use.

### Copernicus Data Space Ecosystem

- **Official organization:** European Commission / Copernicus
- **Official URLs:** https://dataspace.copernicus.eu/ ; https://documentation.dataspace.copernicus.eu/APIs/STAC.html
- **STAC catalogue endpoint:** https://stac.dataspace.copernicus.eu/v1/
- **Products to evaluate:** Sentinel-1 SAR and Sentinel-2 optical scenes.
- **Purpose:** scene discovery and imagery context, not an off-the-shelf disturbance-alert feed.
- **Access mechanism:** STAC discovery is documented; asset download requires a token.
- **Known limitations:** optical cloud contamination; SAR needs careful interpretation; a scene is not a disturbance finding.
- **Operational status:** EXPERIMENTAL CONTEXT ONLY. An opt-in owner-demo lookup has been tested locally against the public STAC catalog; it is off by default, unavailable in the shared demo, and not deployed or a live forest-alert feed.

**2026-10-29 bounded catalog verification:** `GET /v1/search` with `sentinel-2-l2a`, the provisional Geta-area research rectangle, a 30-day interval, and a limit of three returned recent scene metadata without credentials. The bounded test returned three records; the newest two were acquired on 2026-10-29 and reported 57.9% and 59.42% scene-wide cloud cover. Their bounding boxes overlap the broad rectangle; this does not establish full area coverage, an official boundary, usable local imagery, forest change, or a legal finding. The response is limited and may be incomplete. Only metadata was requested; no imagery was downloaded or alert cases created.

`services/api/app/providers/copernicus_stac.py` implements an on-demand, fixed-host lookup with a small field projection, response-size and time bounds, redirect rejection, input validation, and a 15-minute per-process success/failure cooldown. `GET /api/v1/context/copernicus-scenes` requires the authenticated `owner_demo` service boundary and the explicit `FORESTPROOF_COPERNICUS_CATALOG_ENABLED=true` flag. The `/sources` screen labels acquisitions, provenance, timestamps, cloud-cover limitations and the provisional area; it never turns a scene into an alert. Standard tests and CI do not query the provider; an explicitly opted-in local browser smoke did. This is not production identity, storage, a scheduled live feed, or an OVH deployment.

The provider's official documentation says its data and services are available worldwide under EU policy, describes open/free services and free-tier quotas, and specifies `Copernicus Sentinel data [Year]` attribution: [FAQ source](https://github.com/eu-cdse/documentation/blob/7ba7153f7497b826be1edd4c0d65b095ca065369/FAQ.qmd), [ecosystem](https://github.com/eu-cdse/documentation/blob/7ba7153f7497b826be1edd4c0d65b095ca065369/Ecosystem.qmd), [quotas](https://github.com/eu-cdse/documentation/blob/7ba7153f7497b826be1edd4c0d65b095ca065369/Quotas.qmd), and [STAC documentation](https://github.com/eu-cdse/documentation/blob/7ba7153f7497b826be1edd4c0d65b095ca065369/APIs/STAC.qmd). The full linked legal notice and applicable service terms still require review before production or redistribution. No paid account or subscription was created; existing OVH traffic and compute costs are not established by this check.

### NASA FIRMS

- **Official organization:** NASA
- **Official documentation:** https://firms2.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html
- **Purpose:** fire and thermal-anomaly context only.
- **Sensor/method:** product-specific MODIS and VIIRS; VIIRS data may be 375 m depending on selected product.
- **Access mechanism:** documented API requires a MAP_KEY.
- **Critical limit:** a fire alert must never be represented as evidence of logging.
- **Operational status:** DOCUMENTED_NOT_TESTED.

### Kenya Forest Service / national monitoring information

- **Official organization:** Kenya Forest Service
- **Official URL:** https://www.kenyaforestservice.org/
- **Potential use:** authoritative boundary, management, or publicly documented monitoring context where a specific accessible dataset and terms can be verified.
- **Known limitation:** a public description of a monitoring programme does not establish a public live API or reuse permission.
- **Operational status:** DOCUMENTED_NOT_TESTED.

**2026-10-26 public document check:** the official KFS page [Geta Participatory Forest Management Plan (2026–2031)](https://www.kenyaforestservice.org/download/geta-pfmp/) exposed a 152-page PDF that states the plan is approved for implementation. It describes Geta Forest Station as the whole Kipipiri Forest Reserve plus part of Aberdares Forest, with a stated total of 21,644.37 ha. Its maps are credited to KFS Survey and Mapping, show a January 2025 date, and label the datum ARC 1950 / UTM Zone 37S. The KFS media listing dates the identical PDF to 2026-09-28; SHA-256 of the downloaded file is `1d1332f83c982e2002866cff9f545cbf4f60b262eebbe72916b822bf36ef19b7`. This is a strong candidate reference for scoping the pilot area, but the document does not provide a machine-readable boundary file or reuse terms. Follow-up KFS WordPress media searches on 2026-10-26 returned only the 2026 and 2025 Geta plan PDFs for `Geta`, and zero media results for `shapefile`, `boundary`, or `GeoJSON`; page/post search also did not surface a boundary service. This limited public search is not proof one does not exist. Do not digitize the printed map as an authoritative production polygon without KFS boundary data and confirmation. KFS website pages also returned unrelated third-party promotional links and search results; verify document provenance and reuse through an independent official channel before relying on the site for consequential claims. An unsent boundary/data-use request draft is at `docs/KFS_BOUNDARY_REQUEST_DRAFT.md`.

**2026-10-26 momentum decision:** to avoid blocking engineering on a reply, `data/areas/geta-pfmp-research-envelope.geojson` interprets the PFMP's quote-marked textual location range as degrees-and-minutes (36°30′–36°42′ E, 0°15′–0°42′ S), then converts it to a coarse WGS84 rectangle. The coordinate notation and datum are not fully specified in the text, so both interpretations are recorded as assumptions. This is currently a provisional research envelope for coarse source-coverage research and engineering dry-runs. It is not the forest polygon, it includes surrounding land, and it is not yet activated for LIVE filtering, area estimates, legal scope, or public incident claims. The 21,644.37 ha figure is source context, not the rectangle's area. An owner-only pilot using a clearly labeled wider region can be considered without waiting for an official polygon after geometry assumptions, lawful use, source coverage and the other pilot gates are verified. Authoritative forest-specific filtering and claims require an appropriate verified boundary.

**2026-10-29 public release metadata:** `https://data-api.globalforestwatch.org/dataset/wur_radd_alerts/latest` returned concrete release `v20261011`, marked `is_latest: true` with content date 2026-10-11. The separately listed `v20261018` was marked `is_latest: false` with content date 2026-10-18. The dataset version list included both; direct requests for `v20261025` and `v20261026` returned 404. This catalog discrepancy does not establish why the alias points to the older release or which release is operationally preferred. Recheck and resolve release selection and freshness with documented criteria before activation; do not silently equate the alias with the most recent content date. These were unauthenticated catalog metadata requests, not alert-record queries, and do not establish coverage or service cost.

## Required source record fields

Each enabled source product must record:

    source_name, official_organization, source_url, documentation_url,
    product_name, sensor_or_method, spatial_resolution, temporal_resolution,
    coverage_area, observation_latency, access_mechanism,
    authentication_requirements, rate_limits, license,
    commercial_reuse_permissions, redistribution_restrictions, cost,
    known_limitations, verification_date, operational_status

Allowed status values: VERIFIED_ACTIVE, AVAILABLE_WITH_CREDENTIALS, REQUIRES_APPROVAL, DOCUMENTED_NOT_TESTED, EXPERIMENTAL, DISABLED, UNAVAILABLE.

## Activation checklist

Before changing a provider to VERIFIED_ACTIVE:

1. Record official documentation and access mechanism.
2. Review use, attribution, redistribution, and commercial terms for the exact product.
3. Verify account/credential handling without placing secrets in Git.
4. Test a bounded request covering the approved AOI.
5. Preserve raw source identifiers, timestamps, method/version, and response metadata.
6. Record health, latency, gaps, rate-limit behaviour, and a verification date.
7. Confirm the UI labels a record as an observation—not a legal finding.


## 2026-10-28 RADD and API source verification

- Wageningen University & Research (WUR), the RADD producer, states that its RADD dataset is CC BY 4.0 and may be reused without royalty payment, with attribution: https://www.wur.nl/en/research/products-services/radd-forest-disturbance-alert. The same page provides the dataset reference and credits. Dataset licensing does not establish the cost, quota, or access rights of the GFW Data API service.
- WUR says RADD is limited to its primary humid tropical forest baseline and describes excluded areas and other detection limitations. Regional African coverage is not proof that the provisional Geta research envelope is covered. A source mask or permitted bounded request and local coverage review remain necessary. The envelope is not an official forest boundary.
- The official Global Nature Watch terms say API users must use an account API key and comply with the linked attribution requirements: https://globalnaturewatch.org/terms/. The linked Resource Watch attribution page specifies logo/link treatment for its API: https://resourcewatch.org/api-attribution-requirements. Confirm with the provider how those terms apply to this specific GFW Data API integration and dataset citation; do not assume a logo alone satisfies all requirements.
- The public GFW Data API documentation describes key creation and says keys without listed domains use its lowest rate-limiting tier: https://data-api.globalforestwatch.org/. It does not establish this project's current access, specific quota, API price, local coverage, or the response envelope.
- GFW Pro and its Pro API are announced to retire on 2026-12-31: https://globalnaturewatch.org/help/gfw-pro/guides/global-forest-watch-pro-license-agreement/. This announcement concerns Pro and is not evidence that the separate GFW Data API will retire.
- These are public documentation checks only. No authenticated request, alert-record query, account creation, provider activation, cost commitment, or paid subscription has occurred.

WRI's public API source describes a successful POST query/json envelope as status success with data rows, but the deployed service and a RADD response have not been tested. See the pinned source and offline candidate parser note in docs/SATELLITE_INGESTION.md.

**2026-11-13 key and service terms recheck:** The owner created a GNW key on the laptop on 2026-11-11 and the protected local file was confirmed. The [provider guide](https://globalnaturewatch.org/help/developers/guides/create-and-use-an-api-key/) and [API reference](https://data-api.globalforestwatch.org/) document one-year default expiry and the lowest rate tier for keys without registered domains. The material reviewed did not give a numeric quota or a price. Key creation does not confirm alert-record access. Before activation, verify the actual project tier and cost, allowed usage, required attribution, retention, and bounded record access. No alert-record request was made for this recheck.

**2026-10-28 access guide:** The provider's [API key guide](https://globalnaturewatch.org/help/developers/guides/create-and-use-an-api-key/) describes creating keys through MyGFW and says email/password registration rather than social login may be required; it discusses allowed domains, Origin and rate-limit tiers. Keys can expire and need managed rotation. This guidance does not verify ForestProof's account, access, quota, applicable price or right to retain responses. An unsent provider clarification draft is at `docs/GFW_ACCESS_REQUEST_DRAFT.md`.
