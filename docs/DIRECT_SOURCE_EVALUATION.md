# Direct-source evaluation: NASA DIST-HLS and GLAD-L

**Research date:** 2026-11-12 UTC. This is an experimental access assessment, not evidence of a functioning live feed, official Geta boundary, land-cover change, a legal finding, or production readiness. The provisional research box (36.60, -0.49, 36.63, -0.46) is not an authorized operational filter.

## Summary

- NASA OPERA DIST-HLS V1 catalog metadata and one low-resolution public browse PNG were accessed without credentials. The corresponding science TIFF URLs are marked protected; official documentation requires a free Earthdata Login for download. Usable science pixels within the research area remain unverified.
- GLAD-L's own download page exposes current Google Cloud Storage GeoTIFF paths without using the GNW Data API or running Earth Engine. One 10-degree tile containing the research box responded to an unauthenticated HTTP HEAD request. We did not download this GLAD alert TIFF or query GNW alert records. Current source-specific commercial reuse/retention terms and actual usable pixels remain unverified.
- Neither source is integrated into ForestProof; no LIVE data or change claims were produced.

## NASA OPERA DIST-HLS V1

The public NASA CMR [bounded metadata query](https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C2746980408-LPCLOUD&bounding_box=36.60%2C-0.49%2C36.63%2C-0.46&page_size=2&sort_key=-start_date) on 2026-11-12 returned footprint-intersecting product entries for Landsat 8 tiles T36MZE and T37MBV. Both have an observation timestamp of 2026-11-03 07:42:55 UTC; the filenames carry production times on 2026-11-07, approximately four days later. This is a point-in-time result, not a latency guarantee. Footprint intersection does not prove valid, cloud-free pixels or detection in the box.

For T36MZE, CMR lists a public `VEG-DIST-STATUS.png` browse visualization. One anonymous bounded GET returned HTTP 200, `image/png`, 357,237 bytes, 1024 × 1024 pixels. It was inspected in memory for format and dimensions only; it is a whole-tile browse image, not georeferenced science data and was not used to infer conditions in the research box. No scene raster or alert records were downloaded.

The same CMR granule metadata points to `lp-prod-protected` GeoTIFF assets. [NASA's OPERA software documentation](https://nasa-opera.github.io/docs/products/) states that downloads require a valid Earthdata Login; [Earthdata](https://urs.earthdata.nasa.gov/documentation/what_do_i_need_to_know) says searches do not require registration and DAAC data downloads do. Confirm the owner's account privately; never put credentials in chat, logs or Git. [NASA’s Earthdata Login documentation](https://urs.earthdata.nasa.gov/documentation/for_users) describes registration as free. The [product DOI](https://doi.org/10.5067/SNWG/OPERA_L3_DIST-ALERT-HLS_V1.001) and [product specification](https://lpdaac.usgs.gov/documents/1766/OPERA_DIST_HLS_Product_Specification_V1.pdf) are source references.

The collection's public CMR metadata describes access constraints as `None` and points its use constraints to [NASA's data-use policy](https://www.earthdata.nasa.gov/learn/use-data/data-use-policy); this reflects legal/access metadata and does not negate the technical login requirement. [LP DAAC staff describe LP DAAC products as public domain with reuse and sale permitted](https://forum.earthdata.nasa.gov/viewtopic.php?t=5421). Verify the latest exact collection policy, citation and Copernicus/NASA source-credit requirements before external commercial use; do not treat metadata alone as a complete legal review.

[DIST-HLS](https://glad.umd.edu/dataset/DIST-ALERT) reports vegetation loss or spectral disturbance relative to a prior baseline, not inherently forest loss. Assess valid/masked pixels and interpret confidence, observation time and quality before making any real-data claim.

## GLAD-L direct route

The [UMD GLAD-L product page](https://glad.umd.edu/dataset/glad-forest-alerts) links to the [GLAD-maintained direct download interface](https://glad-forest-alert.appspot.com/views/download/download-view.html). Its application generates 10-degree tile names. The provisional box falls in `030E_10S_040E_00N`; this is a broad grid tile, not a validated forest boundary. The page describes alert status 0/2/3 as no loss/probable/confirmed and a separate day-of-year file; preserve actual product semantics. It also specifies a scientific citation and warns that observation cadence depends on usable cloud-free imagery.

On 2026-11-12 UTC, an unauthenticated HTTP HEAD request to [the 2026 alert-status tile](https://storage.googleapis.com/earthenginepartners-hansen/GLADalert/C2/current/alert26_030E_10S_040E_00N.tif) returned status 200, content type `image/tiff`, 13,645,212 bytes, `Last-Modified: Wed, 11 Nov 2026 14:28:46 GMT` and `Accept-Ranges: bytes`. HEAD only establishes file metadata: no alert data was downloaded and no valid pixels were checked. The [provider's regional update marker](https://storage.googleapis.com/earthenginepartners-hansen/GLADalert/C2/current/0_GLADalert_update_date.txt) reported `Africa 11_11`, uploaded 2026-11-11 09:57:54; regional freshness does not establish imagery availability in Geta.

The product page provides a citation but the specific GLAD-L alert dataset's machine-readable licence, downstream retention, commercial-use terms, update guarantee and a usable clip remain unverified. The no-charge/CC-BY statement on [GLAD Landsat ARD](https://glad.geog.umd.edu/ard/home) refers to a different reflectance product and must not be silently transferred to GLAD-L alerts. The UMD alert page says these alerts are early event indicators, not reliable loss-area estimates.

## Bounded cost model and next checks

One GLAD-L status file was ~13.0 MiB at this check. As a simple planning calculation, downloading that same size once on each of 30 days would transfer ~390 MiB per month and retain ~390 MiB if every daily copy were kept, before the separately required date/quality layers, compression differences, retries, backups or cloud charges. This is traffic/storage arithmetic, **not a provider fee quotation**. `Accept-Ranges` does not prove the TIFF is cloud-optimized or that a particular small-area read is efficient. Confirm current network, provider terms and actual measured bytes before estimating expenses; no paid account or subscription was created.

Once access and relevant terms are clear, next validate the intersecting NASA science pixels and quality flags in isolation, and separately verify GLAD-L's exact licence and bounded machine-readable pixel access. Record source/product version, acquisition and receipt times, bytes and freshness/unknown states. Keep demo and LIVE stores separate and require owner authentication plus tested recovery before a real pilot. Do not claim no disturbance from missing or masked pixels.
