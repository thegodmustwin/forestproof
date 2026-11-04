# Lower-cost data and commercial focus

Research date: 2026-11-05. These are documented candidates and a commercial hypothesis, not activated integrations or validated demand.

## Decision
Keep ForestProof's review-to-response workflow independent of a single observation provider. Do not assume MyGFW/Data API is costly: its exact service price and quota remain unverified. Do not bypass credentials, quotas or reuse conditions to avoid fees.

## Source options and limits

**RADD via the existing lead route.** WUR says the RADD dataset is CC BY 4.0 and can be reused without royalty payment. This does not settle GFW Data API service pricing, account access, retention conditions, rate limits or local coverage. RADD's primary humid tropical forest baseline must be checked for the chosen area. Source: https://www.wur.nl/en/research/products-services/radd-forest-disturbance-alert

**Direct GLAD-L downloads.** UMD documents a Landsat-based alert product, 30 m observations across the tropics and direct access through its maintained pages. This is a promising alternate distribution path; verify the exact current files, license/attribution, access, extraction method and local data before using it. Optical cloud gaps and the distinction between a tree-cover alert and a forest/legal finding must remain visible. GLAD-S2's Amazon coverage does not make it a Kenya substitute. Source: https://glad.umd.edu/dataset/glad-forest-alerts

**NASA OPERA DIST-ALERT-HLS V1.** An established 30 m vegetation-disturbance product worth a bounded evaluation. Earthdata Login enables free data access and the NASA-managed registry lists CC BY 4.0, but assets/granules, access method, attribution and local coverage still need verification. It detects vegetation disturbance; ForestProof must not relabel it as deforestation. Free data does not eliminate OVH compute, storage, backup or operations costs. Sources: https://nasa-opera.github.io/docs/products/ ; https://registry.opendata.aws/nasa-snwg-opera/ ; https://urs.earthdata.nasa.gov/documentation/for_users/welcome

**Google Earth Engine.** WUR documents RADD access there, but Google requires commercial configurations for commercial/private-company use. Do not classify a commercial product as noncommercial to obtain a cheaper tier. Pricing and eligibility would need explicit review before commitment. Source: https://developers.google.com/earth-engine/guides/transition_to_commercial

DIST-S1 radar is a later evaluation candidate, not an established Geta feed in this project. Verify actual product assets and validation rather than relying on a product schedule: https://www.jpl.nasa.gov/go/opera/products/dist-product-suite/

## Lowest-cost implementation to evaluate

- Use one reviewed region and bounded date window with a hard query/download budget.
- Fetch on a schedule consistent with actual provider updates; do not query upstream on every page view or map movement.
- Save permitted raw release snapshots with product/version, source/observation/receipt time, license/attribution, hash and query scope. Reuse them across UI sessions.
- Where permitted, extract small raster windows from official assets rather than mirroring global archives.
- Preserve source-specific resolution, mask, confidence, revision and absence semantics. A provider swap is a new validation, not merely a renamed field.
- Cache only within confirmed retention/redistribution rights. Record failures and freshness; never substitute demo observations for a failed live source.
- Keep all existing activation/security/storage gates. No new paid service, data account, alert query or source activation is included in this plan.

## Commercial focus to test

Initial buyer hypothesis: a forest/restoration project manager or contracted monitoring/review team responsible for one project area and recurring reporting. The offer is a traceable case cycle: observation → named reviewer → verification record → documented response → follow-up → source-linked dossier.

The scarce value is a completed, reviewable workflow and the team's permissioned record of decisions. Public satellite data is an input, not exclusive intellectual property. Proposed differentiation needs evidence from actual use; no customer, demand or defensibility claim has been verified.

Test one pilot offer against the buyer's current process: measure actual analyst time, time to assign/review, incomplete cases, reporting turnaround and repeat use. Compare a per-project subscription with explicit limits and optional human-reviewed reporting. Do not set a binding price or build billing before willingness to pay is demonstrated.

Unit economics to record: collected revenue minus source/API cost, serving compute/storage/backup, support and human-review cost. Count field verification and interpretation as real costs. Paid conversion, retention and measured savings are the test; guaranteed profits or conservation impact are not claims.

Next source action: complete/confirm the appropriate MyGFW account, clarify API price/quota/terms, then compare a permitted bounded RADD result with a legally accessible alternate product on the same clearly described research region. Do not state that the provisional Geta envelope establishes forest membership.
