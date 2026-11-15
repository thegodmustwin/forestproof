# Source-status publication preview

Build a standalone HTML preview from the GLAD-L research diagnostic. The static builder has no app database access, credentials, external fetches, or JavaScript. It only accepts the known observation-date source and the provisional Geta research rectangle. The output contains an aggregate snapshot, four independent dates, and a clearly marked unavailable state. It exposes no input coordinates, identifiers or arbitrary text.

From this directory, using Python 3.12:

```text
python -m unittest -v
python build_source_status.py --report /private/glad-report.json --output /private/status.html
python build_source_status.py --output /private/unavailable.html
```

Generate a new report using the [observation-date diagnostic](../glad_l_research/README.md). Keep the report and generated page outside the checkout. Open the generated HTML directly. Invalid input exits with an error and preserves any existing output. A valid snapshot remains dated as of its report even when reopened later.

The preview is for local review. It reads cloud-free observation timing from the source report. Alert eligibility, ground conditions, monitoring completeness and current radar coverage are outside its scope. Before publishing, verify permissions for this source and geography, deploy the page independently of private case routes, and verify recurring refresh, stale handling, and public transport on the target host.

## Isolated staging

Use the separate loopback-only service for testing. From this directory in Python 3.12, install the existing raster dependencies in an isolated environment, then set the raster module path for the refresh process.

```sh
python -m pip install -r ../nasa_dist_research/requirements.txt
PYTHONPATH=../glad_l_research python stage_source_status.py --state /private/status.json refresh
python stage_source_status.py --state /private/status.json serve --port 18447
```

Keep the state file private and run refreshes serially as one operator. The shared report stores the last successful pinned aggregate snapshot. The one-shot refresh uses a single HEAD check before reading a raster window for a new generation. An unchanged generation updates the attempt timestamp and preserves the snapshot. Failed validation or access preserves the last good report and displays a failed-check notice. Unavailable or malformed state displays the unavailable view. The default overdue threshold is 36 hours since the last refresh attempt. It is separate from the age of the latest local observation.

The loopback listener serves only GET and HEAD on `/`. Open it through an SSH forward with the same port on the laptop and remote loopback. Set up no public route for this staging candidate. It serves solely the aggregate report and never serves the state file or connects to the private case application. `--max-check-age-seconds` can be set lower in a separate isolated process to exercise the overdue view. Add a recurring operator-owned refresh only during the approved deployment.
