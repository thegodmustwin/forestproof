# Public observatory assets

## Earth image

earth-east.jpg is the NASA Blue Marble eastern-hemisphere composite from 2002. It provides historical geographic orientation on the public homepage.

Source file:
https://assets.science.nasa.gov/content/dam/science/esd/eo/content-feature/bluemarble/images/globe_east_2048.jpg

Source description and credit:
https://science.nasa.gov/earth/earth-observatory/the-blue-marble-true-color-global-imagery-at-1km-resolution/

NASA media guidance:
https://www.nasa.gov/nasa-brand-center/images-and-media/

Downloaded size 536,295 bytes. SHA-256 3b47b77b49ccd18ecf0aa58610a2047cc68a2e06a1de2e224295a1346aa2dc95.

The original JPEG bytes are retained. Homepage lighting is applied in CSS. The composite has its own date and credit independent of current satellite reports.

## Pass interaction

visibility.js progressively enhances the server-projected grid, date and aggregate counts. The complete observation archive remains available when JavaScript is disabled.

## Geta context comparison - 19 November 2026

The two `geta-context-2026-11-08.png` and `geta-context-2026-11-13.png` files are unchanged uint8 true-colour visualization pixels cropped from the same 335 by 333 native 10 m source window in T36MZE. They show static historical context around the already-published provisional research rectangle. They are not selected-pass live imagery, a forest boundary, or a derived forest-change map. No generated or enhanced content was added.

`geta-context.json` records the exact STAC scene, acquisition timestamp, original TCI URL, source ETag, projected window, output dimensions and SHA-256. `prepare_context_images.py` is the manual bounded preparation script. Regeneration is not part of serving or refresh. The original visualizations were read through anonymous range access from Earth Search / Element 84 public COGs.

Contains modified Copernicus Sentinel data [2026]. Accessed 19 November 2026 from the [AWS Sentinel-2 COG archive](https://registry.opendata.aws/sentinel-2-l2a-cogs/). The public guide explains the image dates and interpretation inside the product.

The public observation explorer may show these same crops only for the exact manifest-matched grid and date. It displays image context unavailable for any other selection. Source images are independent of any forest-change classification. The archived Earth composite is no longer used as the current homepage's main visual.

## Bounded atlas geography — 20 November 2026

`geta-geography.json` retains the canonical research bounds and exact WGS84 outer corners of the published UTM source window. `geography-provenance.json` records four original z10 Terrarium PNGs from the AWS Mapzen Terrain Tiles archive, their hashes and contributing USGS SRTM/GMTED2010 headers. Their 2×2 mosaic provides a 512×512 derived colour/shaded relief image. Colours represent historical elevation; source spacing is approximately153 m at the regional centre. This is geographic context, not a vegetation or disturbance layer. Attribution and primary rights references are retained in the manifest. The original encoded tiles are unchanged.

`world-context.geojson` retains Natural Earth 1:110m country geometry with reduced properties. A generalized Kenya outline is used in the homepage locator. Natural Earth maps are public domain; these are orientation boundaries, not official forest/cadastral geometry. The homepage Earth photograph remains NASA's historical 2002 composite.

MapLibre6.16.0 browser modules/CSS are pinned copies of the existing installed runtime. BSD-3-Clause and third-party notices are retained in `maplibre-LICENSE.txt`; `atlas-runtime.json` records exact hashes. These assets are served locally. Serving or refreshing observations never downloads new geography, packages or terrain.
