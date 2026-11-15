# Private rehearsal for public alerts

The preview serves one read-only route on 127.0.0.1. Without a matching private publication policy and report, it returns an unavailable page. Keep the review references and source data outside Git and outside any web root.

```text
python -m tools.alert_publication.preview --output /private/alerts.html
python -m tools.alert_publication.preview --policy /private/policy.json --report /private/report.json --port 18452
```

The second command serves only `/alerts` using GET and HEAD. The policy comes from the authorized publication operator after checking the source, geography, access terms and reuse. Run the test suite to see a synthetic example of both inputs. The policy schema is `forestproof.alert-publication-policy.v1`. It names the source and area, supplies the coarse approved area label, references the decisions on coverage, access, reuse and area approval, and lists explicitly approved records. Each record approval names the source release, the exact receipt SHA-256, its observation date, when publication was approved and the private review reference.

The matching `forestproof.alert-publication-report.v1` report supplies the source release date, last verified check, latest check attempt, failure status and candidate records. A successful check sets both check timestamps to its completion time. On a failed check, preserve the last verified report and advance the attempted timestamp. The reader calculates overdue status on every request. Duplicate IDs, inconsistent timestamps, or an invalid policy or report fail closed. A new release or changed receipt needs its own approval before that record can appear.

The projection exposes the coarse area name, provider credit, release and verification dates, and approved observation and review dates. The underlying report, private review references, identifiers, notes, coordinates and receipt digests stay private. The reference fields link back to already verified decisions. They are not evidence of approval by themselves. Complete the exact source-specific attribution and delivery terms before exposure. No Contabo route or scheduler is installed by this tool.

Run `python -m unittest discover -s tools/alert_publication -v` to check the route, rejection paths, data boundaries, repeated reads and retained snapshots.
