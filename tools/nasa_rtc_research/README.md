# Geta RTC-S1 seasonal research

The reviewed `geta_batch.json` pins 21 original ASF GeoTIFFs by catalog concept, acquisition date, size and MD5. It selects two Sentinel-1C target captures and five same-burst 2025 reference captures. The existing provisional Geta rectangle defines the research sample. An operational pilot requires separate area and source qualification.

Use Python 3.12. The download helper uses the standard library. Install the existing raster dependencies for the offline comparison in an isolated environment.

```text
python -m pip install -r tools/nasa_dist_research/requirements.txt
python tools/nasa_rtc_research/download.py --manifest tools/nasa_rtc_research/geta_batch.json --output-dir PRIVATE_DATA --check-only
python tools/nasa_rtc_research/download.py --manifest tools/nasa_rtc_research/geta_batch.json --output-dir PRIVATE_DATA
python tools/nasa_rtc_research/compare.py --manifest tools/nasa_rtc_research/geta_batch.json --input-dir PRIVATE_DATA
```

Use an existing owner-controlled directory outside Git for `PRIVATE_DATA`. The downloader checks existing files before prompting and keeps the reviewed, matching files in place. The program uses a masked interactive Earthdata Login and an in-memory session limited to NASA and ASF endpoints. Subsequent runs verify the retained files and fetch the remainder. New files are staged and released to their final filenames after size and checksum verification. The Earthdata account may require the standard ASF browser authorization first. [NASA Python access flow](https://urs.earthdata.nasa.gov/documentation/for_users/data_access/python) · [ASF account setup](https://docs.asf.alaska.edu/api/basics/)

The comparison uses aligned native 30 m cells and validates the three input grids per date. A common cell needs a positive finite VV and VH value and a code-0 acquisition mask on every date. It summarizes each target's dB difference from the per-cell reference median. It also holds out each historical date and compares it with the remaining dates to describe the reference spread. These dependent reference summaries measure backscatter variability. Disturbance detection, land cover, cause and estimated error need independent evidence. [ASF validity masks](https://hyp3-docs.asf.alaska.edu/guides/opera_rtc_product_guide/#validity-mask)

The output is a local aggregate report. Keep source TIFFs, credentials, detailed locations and local outputs out of the repository. The full OPERA detector and its runtime requirements are a separate research step.

## Historical fire backtest

Place the three public ZIPs in an existing source directory using these names. The script checks the archived SHA-256 hashes before opening the required TIFF members in memory.

- `jpl-dist-s1.zip` from the [JPL radar prototype](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_L3_DIST-ALERT-S1_T11SLT_20250121T015030Z_20250819T130204Z_S1_30_v0.1.zip)
- `baer-eaton.zip` from the [USDA Forest Service Eaton reference](https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/baer/eaton_ca3419211810520250108_sbs.zip)
- `baer-palisades.zip` from the [USDA Forest Service Palisades reference](https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/baer/palisades_ca3406811855120250107_sbs.zip)

```text
python tools/nasa_rtc_research/backtest_fire_reference.py --input-dir SOURCE_DIRECTORY
python -m unittest discover -s tools/nasa_rtc_research -p 'test_backtest_fire_reference.py' -v
```

The output separates each reference class, missing radar and first flags for four neighbourhood sizes. It uses the delivered acquisition outcome from the pinned JPL prototype. [Interpretation and results](../../docs/DIRECT_SOURCE_EVALUATION.md#california-radar-prototype-backtest---2026-11-16)
