# Forest-alert providers

Providers have four deliberate stages:

1. `discover(area, time_range)` locates source records without asserting an incident.
2. `fetch(cursor)` obtains the original available record or artifact.
3. `normalize(record)` produces a typed observation while retaining source timestamps.
4. `provenance(record)` emits source/version/access metadata used in the evidence packet.

`demo_provider.py` is deterministic test data. `gfw_tile_overlay.py` provides a
real public GLAD-S2 raster layer for map context, but intentionally cannot
manufacture individual evidence records from raster pixels. The separately
credentialed Data API adapter is deferred until its response contract is tested
against an approved account and licence terms.
