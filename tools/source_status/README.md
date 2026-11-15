# Source-status publication preview

Build a standalone HTML preview from the GLAD-L research diagnostic. This tool has no app database access, credentials, external fetches, or JavaScript. It only accepts the known observation-date source and the provisional Geta research rectangle. The output contains an aggregate snapshot, four independent dates, and a clearly marked unavailable state. It exposes no input coordinates, identifiers or arbitrary text.

From this directory, using Python 3.12:

```text
python -m unittest -v
python build_source_status.py --report /private/glad-report.json --output /private/status.html
python build_source_status.py --output /private/unavailable.html
```

Generate a new report using the [observation-date diagnostic](../glad_l_research/README.md). Keep the report and generated page outside the checkout. Open the generated HTML directly. Invalid input exits with an error and preserves any existing output. A valid snapshot remains dated as of its report even when reopened later.

The preview is for local review. It reads cloud-free observation timing from the source report. Alert eligibility, ground conditions, monitoring completeness and current radar coverage are outside its scope. Before publishing, verify permissions for this source and geography, deploy the page independently of private case routes, and verify recurring refresh, stale handling, and public transport on the target host.