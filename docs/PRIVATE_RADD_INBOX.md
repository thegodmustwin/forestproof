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

Before importing any genuine response, confirm the right to retain exact provider bytes, verify the approved area and source configuration, and collect the named review record. The inbox has no HTTP route, owner session, scheduled provider client or connection to the case workflow. Tests cover only synthetic responses and local copies.

## Source qualification

A November 13 diagnostic on UMD's 2001 primary humid tropical forest raster found 422 of 14,400 sampled centres (2.93%) inside the historical class in the provisional rectangle. RADD uses that layer as an input and applies more exclusions, including mapped 2001–2018 loss in Africa and mangroves. Current coverage remains unmeasured. [UMD baseline](https://glad.umd.edu/dataset/primary-forest-humid-tropics) · [WUR RADD method](https://www.wur.nl/en/research/products-services/radd-forest-disturbance-alert)

On November 14, the GNW catalog identified global RADD coverage release `v20240704` and a 10 m EPSG:4326 GeoTIFF asset. The published fields omit class and nodata definitions, and the coverage dataset entry does not specify its license. The separate Africa legacy release `v20210120` describes Congo Basin coverage. [Global coverage catalogue](https://data-api.globalforestwatch.org/dataset/wur_radd_coverage/v20240704) · [Field metadata](https://data-api.globalforestwatch.org/dataset/wur_radd_coverage/v20240704/fields)

GNW's alert catalogue lists GLAD-L under CC BY 4.0 with route-specific credit. UMD's direct download page supplies the dataset citation. Confirm its intended-use and redistribution terms before selecting that route. RADD record access, fees, quotas, attribution and response retention remain open. The existing [unsent provider questions](GFW_ACCESS_REQUEST_DRAFT.md) cover those gaps. [GNW GLAD-L metadata](https://data-api.globalforestwatch.org/dataset/umd_glad_landsat_alerts) · [UMD direct download](https://glad-forest-alert.appspot.com/views/download/download-view.html)
