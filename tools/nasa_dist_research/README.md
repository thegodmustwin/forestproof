# Offline NASA DIST-HLS V1 layer check

This is a **research-only**, local-file diagnostic for one user-supplied NASA
OPERA DIST-ALERT-HLS V1 granule. It makes no network requests and is not a
live-feed adapter, evidence store, land-cover map or an official boundary.

Use an isolated Python 3.12 environment and install `requirements.txt` there.
Never put NASA credentials, downloaded rasters, precise location results or
private information into Git, chat or shared logs.

```text
python -m pip install -r requirements.txt
python -m unittest -v test_inspect_dist_layers
python inspect_dist_layers.py --status PATH --first-date PATH --last-date PATH --mask PATH --bounds WEST SOUTH EAST NORTH
```

`--status` and at least one of the other bands are required. Supply a small
WGS84 rectangle as four explicit values; there is no default project geography.
It cannot exceed one degree in either axis or four million selected window
pixels. The rectangle is not an official boundary or approval for LIVE use.
Inputs must be local files from the same granule, with matching grids, CRS,
dimensions, band count, and data type. Only the single tile's intersection is
examined; no other tile, attribution or upstream checksum is verified. Hashes
are locally calculated identifiers, not authentication.

The utility reports aggregate statuses, date spans, mask codes and the number
of pixel centres in each denominator; it does not export pixel locations.
First detection is an algorithm observation, not necessarily the date of a
ground event. Last assessed is a source-defined observation date, not proof of
current conditions. DATA-MASK is a current-scene processing mask rather than
complete cloud quality or a forest mask. NASA V1's specification labels mask
0 as “not land”; the observed sample TIFF described it as “no data or masked”.
Do not infer the cause or permanent land cover. No alert, deforestation,
illegality, loss-area or coverage-completeness claim follows from these counts.

The tool does not enable LIVE operation. Verify source rights, quality, date,
area, source accuracy, identity and protected storage before any real pilot.
The observed sample and limitations are documented in
`docs/NASA_DIST_SAMPLE_20261112.md`.
