# GLAD-L observation recency

This operator-run diagnostic reads a versioned, public UMD GLAD-L observation-date tile for eastern Africa. It uses HTTPS byte ranges with an 8 MiB response-body budget, verifies the cloud object generation and ETag, and reads at most a 0.05-degree rectangle per axis. Output includes aggregate dates, the sample fingerprint, and the provider modification time. This layer records the latest cloud-free observation so far this year. It does not establish alert eligibility, forest cover or current conditions.

Install the existing raster research dependencies in an isolated Python environment.

```text
cd tools/glad_l_research
python -m pip install -r ../nasa_dist_research/requirements.txt
python -m unittest -v
python inspect_glad_observation_dates.py --generation GENERATION --as-of YYYY-MM-DD --bounds WEST SOUTH EAST NORTH
```

Use the observation-date asset's `x-goog-generation` from a HEAD request to the [linked public tile](https://storage.googleapis.com/earthenginepartners-hansen/GLADalert/C2/current/obsDate_030E_10S_040E_00N.tif). The reporting date must be in the same calendar year and on or after the tile was published. Keep each generation, date and result together. The mutable `current` object may overwrite older generations. A replacement or inaccessible generation requires a new report with its own identity. The window hash covers little-endian UInt16 values in native row order followed by the raster mask bytes.

The date bins count centres at most 7, 14, 30 and 60 calendar days old, inclusive. Documented zero means the source has no cloud-free observation for that centre in the current year. The tool reports raster-masked centres separately. The underlying bytes come from the producer's direct publication route. No provider credentials, alert raster requests, automatic polling or application routes are involved.

Cite UMD GLAD and Hansen et al. (2016) for any use of the dataset. See [product guidance](https://glad.umd.edu/dataset/glad-forest-alerts), [download and layer definitions](https://glad-forest-alert.appspot.com/views/download/download-view.html) and [method reference](https://doi.org/10.1088/1748-9326/11/3/034008).

## Paired alert archive inspection

Inspect one explicitly dated archive in the provisional Geta research rectangle. Supply the generation of each file independently. This command uses the same pinned range reader and 8 MiB per-object ceiling as the observation-date diagnostic.

```text
python tools/glad_l_research/inspect_glad_alert_pair.py 2026-11-13 --status-generation 1794578188389979 --detection-generation 1794578211527205 --observation-generation 1794579516954440
python tools/glad_l_research/inspect_glad_alert_pair.py 2026-11-14 --status-generation 1794681529413083 --detection-generation 1794681567386287 --observation-generation 1794682860805108
```

The report verifies the native transforms, uses the same 14,400 cell centres for all three files and keeps release, detection and clear-observation dates distinct. Status 2 is probable and status 3 is confirmed by the provider's algorithm. The producer's status, date and observation layers do not establish the complete native eligibility mask for this pilot. Counts describe cells, not a set of distinct incidents or an area estimate. [Layer definitions](https://glad-forest-alert.appspot.com/views/download/download-view.html)

For a private review candidate, pass `--private-receipt` with a new file in an owner-protected directory outside Git. It selects the most recent cell with status 3 and records the source identifiers, native grid location and date fields. It assigns no field verification, owner decision or publication approval. The normal stdout report contains aggregate results only.
