# Private RADD import and recovery rehearsal

Use this command-line tool to rehearse one part of the private pilot with a synthetic response. It stores the original bytes, exact release, receipt time, and a digest, then links each normalized cell to the receipt that first supplied it for that release. An export carries the stated source credit and scope review reference. All exports have state `UNVERIFIED_IMPORT` because the operator supplies the input.

From `services/api`, use the existing Python environment. Put the database, input files and outputs in private directories outside Git. The scope file is JSON. Example coordinates below are synthetic.

```json
{
  "scope_id": "offline-rehearsal",
  "review_ref": "local synthetic fixture",
  "attribution": "Synthetic RADD-shaped fixture",
  "bounds": [0.0, 0.0, 0.01, 0.01],
  "max_observation_age_days": 7,
  "max_receipt_gap_hours": 24
}
```

Save this synthetic response as `response.json` for the rehearsal:

```json
{"status":"success","data":[{"longitude":0.002,"latitude":0.003,"wur_radd_alerts__date":"2026-11-10","wur_radd_alerts__confidence":3}]}
```

```text
python -m app.pilot_radd_inbox /private/inbox.sqlite init /private/scope.json
python -m app.pilot_radd_inbox /private/inbox.sqlite import /private/response.json --release v20261110 --received-at 2026-11-13T12:00:00Z
python -m app.pilot_radd_inbox /private/inbox.sqlite status
python -m app.pilot_radd_inbox /private/inbox.sqlite list
python -m app.pilot_radd_inbox /private/inbox.sqlite copy /private/backups/inbox.sqlite
python -m app.pilot_radd_inbox /private/backups/inbox.sqlite copy /private/drill/restored.sqlite
python -m app.pilot_radd_inbox /private/drill/restored.sqlite export /private/drill/record.json --record-key CELL_KEY --release v20261110
```

Create the private backup and drill directories before running the copy commands. Use the record key and release shown by `list` for the export.

The importer rejects malformed responses, cells outside the scope, future observation dates relative to receipt, and conflicting source fields for the same cell and release. Replaying the exact bytes leaves both the records and latest unique receipt time as they were. An empty successful response can advance receipt status while coverage and observation freshness remain unknown in an empty inbox. The tool shows receipt age and observation age independently. It does not observe actual requests or outages.

The copy uses SQLite's online backup API, validates the copied database and receipt links, and rechecks saved response bytes and corresponding rows. The restore drill uses a separate database path. The operator must provision private directory permissions, protect the backup in transit and at rest, and test a restore on the off-host target.

Before importing any genuine response, confirm the right to retain exact provider bytes, verify the approved area and source configuration, and collect the named review record. The inbox has no HTTP route, owner session, scheduled provider client or connection to the case workflow. Tests cover only synthetic requests and local copies.
