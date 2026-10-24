# Data Sources

## Status and operating rule

Live integrations are DOCUMENTED_NOT_TESTED unless this file is updated with a verification date, successful health check, applicable licence decision, and implementation status. Documentation access is not proof that a feed is operational, commercially reusable, or appropriate for the Aberdare area of interest.

No source below is currently represented by this document as a live ForestProof feed.

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

### Copernicus Data Space Ecosystem

- **Official organization:** European Commission / Copernicus
- **Official URLs:** https://dataspace.copernicus.eu/ ; https://documentation.dataspace.copernicus.eu/APIs/STAC.html
- **STAC catalogue endpoint:** https://stac.dataspace.copernicus.eu/v1/
- **Products to evaluate:** Sentinel-1 SAR and Sentinel-2 optical scenes.
- **Purpose:** scene discovery and imagery context, not an off-the-shelf disturbance-alert feed.
- **Access mechanism:** STAC discovery is documented; asset download requires a token.
- **Known limitations:** optical cloud contamination; SAR needs careful interpretation; a scene is not a disturbance finding.
- **Operational status:** DOCUMENTED_NOT_TESTED.

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
