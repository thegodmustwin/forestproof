# Sentinel-2 visibility inspection

Inspect the two native 20 m Scene Classification Layer grids that overlap the provisional Geta research rectangle. Use this to distinguish satellite acquisitions with an observable surface from acquisitions obscured by clouds, shadow, or other unclassified pixels.

Activate an isolated Python 3.12 environment from the repository root.

```text
python -m pip install -r tools/nasa_dist_research/requirements.txt
python -m unittest discover -s tools/sentinel_visibility -v
python tools/sentinel_visibility/inspect_visibility.py 2026-11-08 2026-11-10 2026-11-13
```

Supply one to three distinct UTC scene dates. The command checks that the Earth Search catalog identifies both grids from the same datatake. It accepts only the expected public SCL asset path for each item. An anonymous HEAD and ETag-conditional byte range read verify each object's identity and length. Each band download is capped at 8 MiB. The JSON receipt records the item and datatake IDs, the source URL, object modification time, ETag and SHA-256. Save successful output outside the checkout. The inspector keeps the rasters in memory. An offline reproduction would need a separate copy of the original bytes. The command uses no token or paid API.

Each grid is measured separately in its native projection, using pixel centres inside the rectangle. Codes 4, 5 and 6 are the provider's vegetation, nonvegetated and water classes. Their combined count is a visibility indicator. Cloud, shadow, unclassified and no-data centres remain in the denominator. The output distinguishes visible vegetation from all visible surface. A missing tile or ambiguous acquisition fails the run with a diagnostic. The two grids overlap and cannot be summed to produce an area percentage. Use this classification for visibility checks.

Use the per-acquisition Copernicus attribution when reproducing aggregate results, and credit the delivery service and access date. This bounded research tool has no alert records, publishing endpoint, approved operational geography, or service guarantee. [Sentinel-2 classification documentation](https://sentiwiki.copernicus.eu/web/s2-processing#S2Processing-ClassificationMaskGeneration) · [Copernicus data terms](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice) · [Public COG delivery](https://registry.opendata.aws/sentinel-2-l2a-cogs/)

## Private visibility page

From the repository root, render the JSON from the current inspector into a standalone HTML preview. Keep the input and output outside Git.

```text
python -m tools.sentinel_visibility.build_visibility_page --report /private/sentinel-report.json --output /private/visibility.html
```

The builder verifies the fixed research extent, both grids, and the class totals before it replaces any page. The HTML contains the acquisition days, check time, denominators, visible and vegetation counts, the method, and Copernicus credit. The private report retains the precise bounds and source receipts. An omitted report generates an unavailable state. A check at least 36 hours old renders an overdue banner and keeps the last measured counts. The freshness banner is evaluated when the page is built. An operational release needs a periodic rebuild and a monitored refresh.

Keep the test listener on loopback with only the generated HTML in its served directory. The preview is independent of the case API and storage.

## Recurring public visibility

The owner approved aggregate publication under the label **Provisional Geta research area**. The [published page](https://vmi3711898.contaboserver.net/visibility) uses the timer, loopback web process and exact HTTPS route in the [Contabo release runbook](../../infrastructure/deployment/sentinel-visibility/README.md). The service evaluates stale and failed-check status independently of the static preview.
