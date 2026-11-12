# NASA DIST-HLS sample: bounded research inspection

**Date checked:** 2026-11-12. The owner downloaded one NASA OPERA DIST-ALERT-HLS V1 VEG-DIST-STATUS GeoTIFF through their Earthdata account. This is a local research check, not a live feed, operational incident, field verification, or official Geta Forest boundary.

## Product and local provenance

- NASA collection: OPERA DIST-ALERT-HLS V1, [dataset DOI](https://doi.org/10.5067/SNWG/OPERA_L3_DIST-ALERT-HLS_V1.001); catalog granule G4404844353-LPCLOUD.
- Filename: `OPERA_L3_DIST-ALERT-HLS_T36MZE_20261103T074255Z_20261107T181429Z_L8_30_v1_VEG-DIST-STATUS.tif`. Its name indicates acquisition on 2026-11-03 and production on 2026-11-07; the internal metadata lists update time 2026-11-03T07:42:55.724310Z–07:43:19.649238Z and references a 2026-11-02 prior input granule.
- File size 3,408,170 bytes; locally computed SHA-256 `cc0129ee110f20c86980b2d2dce915fa78f9fe6610842424baf170c14009afdf`. This is a local fingerprint, not comparison with an independently verified NASA checksum.
- The actual file is a 3,660 × 3,660 single-band UInt8 GeoTIFF, 30 m pixels, EPSG:32636, nodata value 255. Its embedded flag descriptions match the [NASA V1 product specification](https://lpdaac.usgs.gov/documents/1766/OPERA_DIST_HLS_Product_Specification_V1.pdf).

## Method and result

A locally installed rasterio tool projected a densified, provisional WGS84 research rectangle (36.60, -0.49, 36.63, -0.46) into the raster CRS, clipped to the tile intersection, selected pixel centres inside the rectangle and counted status categories. This is not an official boundary or approved operational filter. No individual pixel locations were exported.

In this *one tile's intersection* there were 12,432 pixel centres, of which 0 were marked nodata or masked in this status layer. The counts were:

| Source code | NASA meaning | Pixel centres |
| --- | --- | ---: |
| 0 | No disturbance status detected | 10,955 |
| 1 | First detection, <50% | 146 |
| 2 | Provisional, <50% | 74 |
| 3 | Confirmed, <50% | 369 |
| 4 | First detection, ≥50% | 3 |
| 5 | Provisional, ≥50% | 2 |
| 6 | Confirmed, ≥50% | 172 |
| 7 | Confirmed, <50%, finished | 498 |
| 8 | Confirmed, ≥50%, finished | 213 |

NASA's categories describe vegetation-cover disturbance relative to the product baseline. A first/provisional/confirmed status does not prove deforestation, a particular cause, illegality, an action on the ground, or conditions today. Finished statuses may describe earlier disturbances; an acquisition timestamp does not date every prior detection. Zero is a product status, not proof no disturbance occurred.

## Verification and limits

The inspection was performed locally, with no account credentials read, no science data transferred into GitHub, and no GNW query or live ingestion. The tool first passed three synthetic tests: known nodata/category counts; rejection of invalid status and nonintersecting input; and a projected-UTM intersection. Dependencies were installed only into a temporary virtual environment.

Only the selected VEG-DIST-STATUS layer and tile intersection were checked. Other overlapping tiles and separate quality/cloud, date, duration, forest-mask and contextual layers were not examined. A nodata count of zero in this band is not a full quality assessment. No exact boundary, per-pixel validation, NASA-provided checksum, scientific accuracy assessment, official land-cover classification or field verification was established. Do not infer cleared forest area, product coverage outside the tile, or legal conclusions.

Before product use, verify source and attribution/retention terms, current source freshness and quality semantics, define a lawful area, integrate identity/provenance and protected separate storage, and demonstrate backup/restore. This work does not change the lead-feed decision or make ForestProof's live endpoint operational.
