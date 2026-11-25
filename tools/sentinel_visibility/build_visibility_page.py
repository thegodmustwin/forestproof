"""Render the visibility page from a reviewed Sentinel-2 report."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path
from string import Template

from tools.sentinel_visibility.project_visibility import project
from tools.source_status.build_source_status import day_label, read_report, time_label, write_page


TEMPLATE = Path(__file__).with_name("visibility.html")
ATLAS_STYLES = Path(__file__).resolve().parents[2] / "packages" / "ui" / "living-atlas.css"
CHECK_MAX_AGE = timedelta(hours=36)
READING_GUIDE = """
<section class="reading-guide" aria-labelledby="reading-guide-title">
<h2 id="reading-guide-title">How to read this report</h2>
<div>
<p><strong>Start with the visible share.</strong> It counts the sampled centres classified as surface on that pass. Cloud, shadow, unclassified and missing centres remain unassessed. The vegetation count applies to the visible centres.</p>
<p><strong>Compare one grid across dates.</strong> The grids overlap and have separate denominators. A pass date records the satellite observation. The report verification time records ForestProof's latest successful source check.</p>
</div>
</section>
"""


TIME_MACHINE = r'''
<section class="time-machine" id="compare-observations" aria-labelledby="time-title">
 <div class="time-intro"><div><p class="eyebrow">One place · two historical views</p><h2 id="time-title">Look through time.</h2></div><p>Compare the same published Sentinel-2 window on two dates. The images show what the sensor captured; the coverage figures describe what could be assessed.</p></div>
 <div class="time-workbench"><header class="time-head"><strong>Geta research window · T36MZE</strong><span>Historical true colour · 10 m pixels</span></header>
  <div class="time-layout"><div>
   <div class="time-viewport" tabindex="0" aria-label="Historical comparison image viewport. At higher magnification, scroll or use arrow keys to move around the same view." data-time-viewport>
    <div class="time-canvas" data-time-canvas>
     <figure class="time-frame"><img src="/assets/geta-context-2026-11-08.png" width="335" height="333" loading="lazy" alt="8 November 2026: patches of green land between bright clouds and shadows." data-time-image="2026-11-08"><figcaption>08 NOV 2026 · S2C</figcaption></figure>
     <figure class="time-frame"><img src="/assets/geta-context-2026-11-13.png" width="335" height="333" loading="lazy" alt="13 November 2026: the same source window is almost entirely white with little usable ground view." data-time-image="2026-11-13"><figcaption>13 NOV 2026 · S2B</figcaption></figure>
    </div>
   </div>
   <div class="time-controls" data-time-controls hidden><label>Compare the two views <input data-time-reveal type="range" min="0" max="100" value="50" aria-label="Compare image dates: left is 8 November, right is 13 November"></label><label>Magnification <input data-time-zoom type="range" min="100" max="300" step="25" value="100" aria-label="Magnify both dates together"></label></div>
   <p class="time-help" data-time-help>Two published crops share the same source window and grid. Their dates and source images remain distinct.</p>
   <p class="time-failure" role="status" data-time-failure hidden></p>
  </div><div class="time-evidence"><p class="eyebrow">Read the evidence</p><h3>What can we actually see?</h3><dl>
    <div><dt>08 November 2026 · T36MZE</dt><dd data-time-coverage="2026-11-08">See the dated report above for coverage.</dd></div>
    <div><dt>13 November 2026 · T36MZE</dt><dd data-time-coverage="2026-11-13">See the dated report above for coverage.</dd></div>
   </dl><p class="time-limit"><strong>Visibility is not forest loss.</strong> Clouds and other unassessed areas limit comparison. Different appearances alone do not establish change, its cause or legality.</p>
   <p class="time-source">Same 335 × 333 pixel source window, UTM grid and 10 m image resolution; coverage is sampled at 20 m. <a href="/assets/geta-context.json">View published source identities and provenance</a> · <a href="/guide#satellite-imagery">How to interpret imagery</a>.</p>
  </div></div>
 </div>
</section>
'''


def percent_label(visible: int, sampled: int) -> str:
    percent = 100 * visible / sampled
    if visible == 0:
        return "0%"
    if percent < 0.1:
        return "&lt;0.1%"
    return f"{percent:.1f}%"


def grid_row(tile: dict) -> str:
    visible, sampled = tile["visible"], tile["sampled"]
    percent = 100 * visible / sampled
    display = percent_label(visible, sampled)
    return f"""
<li class="grid-row" data-grid="{tile["grid"]}" data-visible="{visible}"
    data-sampled="{sampled}" data-vegetation="{tile["vegetation"]}">
  <span class="grid-name">{tile["grid"]}</span>
  <div class="track" aria-hidden="true"><span style="width:{percent:.6f}%"></span></div>
  <span class="reading"><strong>{display}</strong><span>{visible:,} of {sampled:,} visible</span></span>
  <span class="vegetation">{tile["vegetation"]:,} classified as vegetation</span>
</li>"""


def scene(day: dict, *, latest: bool = False) -> str:
    date = day["date"]
    pass_time = f'<time datetime="{date.isoformat()}">{day_label(date)}</time>'
    caption = '<p class="eyebrow">Latest pass in this report</p>' if latest else ""
    rows = "\n".join(grid_row(tile) for tile in day["tiles"])
    return f"""
<article class="pass{' latest' if latest else ''}" data-observation-date="{date.isoformat()}">
  <header>{caption}<h2>{pass_time}</h2></header>
  <ul class="grids" aria-label="Visibility by tile">{rows}</ul>
</article>"""


def explorer(acquisitions: list) -> str:
    latest = acquisitions[0]
    grid_buttons = "\n".join(
        f'<button class="grid-choice" type="button" data-select-grid="{tile["grid"]}" '
        f'aria-pressed="{"true" if index == 0 else "false"}">{tile["grid"]}</button>'
        for index, tile in enumerate(latest["tiles"])
    )
    pass_buttons = "\n".join(
        f'<button class="pass-choice" type="button" data-select-date="{day["date"].isoformat()}" '
        f'aria-pressed="{"true" if day["date"] == latest["date"] else "false"}">'
        f'<span class="pass-date">{day_label(day["date"])}<span class="selected-mark" aria-hidden="true">Selected</span></span>'
        '<span class="pass-bar" aria-hidden="true"><span data-pass-fill></span></span>'
        f'<span class="pass-share" data-pass-share>{percent_label(day["tiles"][0]["visible"], day["tiles"][0]["sampled"])} visible</span>'
        '</button>'
        for day in reversed(acquisitions)
    )
    return f"""
<section class="explorer" data-visibility-explorer hidden aria-label="Explore satellite passes">
  <div class="explorer-heading">
    <div><p class="eyebrow">A view through time</p><h2>What could the satellite see?</h2></div>
    <p>Choose a pass. Compare usable surface coverage with the places that remained unassessed.</p>
  </div>
  <div class="explorer-instrument">
  <section class="pass-comparison" aria-labelledby="comparison-title">
    <div class="grid-controls"><p class="eyebrow">01 · Choose a view</p><span class="control-title" id="grid-control-label">Image grid</span>
      <div class="grid-choices" role="group" aria-labelledby="grid-control-label">{grid_buttons}</div>
      <p class="control-help">The grids overlap. Keep one selected to compare the same sample across dates.</p>
    </div>
    <div class="best-pass"><p class="control-title">Start with a clearer view</p><p data-best-summary></p><button class="best-choice" type="button" data-select-best>Show clearest sampled pass</button></div>
    <div class="comparison-heading"><h3 id="comparison-title">Observation timeline</h3><p>Each bar shows the usable share.</p></div>
    <div class="comparison-scale" aria-hidden="true"><span>0% visible</span><span>100%</span></div>
    <div class="pass-choices" role="group" aria-label="Choose a satellite pass">{pass_buttons}</div>
    <a class="scene-jump" href="#scene-title">See the selected view ↓</a>
    <p class="comparison-note">Every bar uses a 0–100% scale. Empty areas of the bar mean unassessed ground.</p>
  </section>
  <section class="scene-panel" aria-labelledby="scene-title">
    <header class="scene-header"><strong id="scene-title">02 · Inspect the source view</strong><span>OPTICAL · SENTINEL-2</span></header>
    <div class="scene-view">
      <div data-scene-available hidden>
        <div class="scene-image-frame"><img data-scene-image width="335" height="333" alt=""></div>
        <div class="image-meta"><span data-scene-date></span><span>10 m · True colour</span></div>
      </div>
      <div class="scene-empty" data-scene-empty>
        <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M6 15V6h9m18 0h9v9M6 33v9h9m18 0h9v-9M9 34l9-10 7 7 7-13 7 16"/><circle cx="16" cy="15" r="3"/></svg>
        <h3>Image context unavailable</h3><p data-scene-missing>No published image crop matches this selected grid and date. The coverage counts remain available.</p>
      </div>
    </div>
    <div class="scene-note"><strong data-scene-heading>Read the source and its limits</strong><p data-scene-caption>The coverage summary is separate from the image context.</p><a href="/atlas/geta" data-return-atlas>Locate this observation in the atlas →</a><br><a href="/guide#satellite-imagery">Understand the imagery and sources →</a></div>
    <p class="scene-data-note">Historical image context. To assess change, compare repeat observations and record a human review.</p>
  </section>
  <div class="observation-panel">
    <div class="observation-main">
      <p class="eyebrow">03 · Read the evidence</p><p class="eyebrow">Selected grid · <span data-selected-grid></span></p>
      <h2>Usable surface view</h2>
      <div class="coverage-ring">
        <svg viewBox="0 0 200 200" role="img" aria-labelledby="coverage-ring-title">
          <title id="coverage-ring-title" data-coverage-title>Usable and unassessed surface coverage</title>
          <circle class="ring-base" cx="100" cy="100" r="78" pathLength="100" />
          <circle class="ring-visible" cx="100" cy="100" r="78" pathLength="100" stroke-dasharray="0 100" data-coverage-arc />
        </svg>
        <div class="ring-centre"><p class="metric" data-visible-percent></p><span>visible</span></div>
      </div>
      <p class="metric-caption" data-visible-caption></p>
      <div class="coverage-graphic">
        <div class="coverage-track" aria-hidden="true"><span data-coverage-fill></span></div>
        <div class="coverage-key"><span class="key-item"><span class="key-swatch" aria-hidden="true"></span>Visible</span><span class="key-item"><span class="key-swatch unassessed" aria-hidden="true"></span>Unassessed</span></div>
        <p class="coverage-caption">Share of sampled centres. This is an aggregate chart, not a map of individual locations.</p>
      </div>
    </div>
    <div class="observation-context">
      <p class="eyebrow">Satellite observation date</p>
      <p class="observation-date"><time data-selected-date></time></p>
      <dl class="cell-breakdown">
        <div><dt>Visible centres</dt><dd data-visible-count></dd></div>
        <div><dt>Unassessed centres</dt><dd data-unassessed-count></dd></div>
        <div><dt>Sampled centres</dt><dd data-sampled-count></dd></div>
      </dl>
      <p class="vegetation-note"><strong data-vegetation-count></strong> visible centres classified as vegetation.</p>
      <div class="interpretation-box"><h3>What this means</h3><p class="interpretation" data-interpretation></p></div>
      <p class="change-limit">A usable view does not establish vegetation loss. Understanding change takes another observation, a qualified method and human review.</p>
    </div>
  </div>
  </div>
  <div class="continue-workflow"><div><p class="eyebrow">From a signal to a decision</p><h3>Now try the human part.</h3><p>Practise reviewing a fictional signal, choosing a response and recording what to check next. Your selected real observation is not imported into the practice case.</p></div><a class="continue-link" href="/tour">Try the case walkthrough</a></div>
  <p class="sr-only" role="status" aria-live="polite" data-selection-announcement></p>
</section>"""


def render(snapshot: dict | None, *, now: datetime, public: bool = False, failed_at: datetime | None = None) -> str:
    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    masthead = (
        '<nav class="public-nav" aria-label="Page navigation">'
        '<a href="/welcome">Home</a><a href="/atlas/geta">Atlas</a><a href="/visibility" aria-current="page">Observations</a>'
        '<a href="/tour">Product tour</a><a href="/research">Research</a><a href="/guide">Guide</a></nav>'
        if public else '<p class="flag">Private research preview</p>'
    )
    robots = "" if public else '<meta name="robots" content="noindex">'
    brand = (
        '<a class="brand" href="/welcome">ForestProof</a>'
        if public else '<div class="brand">ForestProof</div>'
    )
    chrome = {
        "brand": brand,
        "masthead": masthead,
        "robots": robots,
        "atlas_styles": (
            '<link rel="stylesheet" href="/assets/atlas.css">'
            if public else f'<style>{ATLAS_STYLES.read_text(encoding="utf-8")}</style>'
        ),
        "explorer_script": '<script src="/assets/visibility.js" defer></script>' if public else "",
        "time_machine": TIME_MACHINE if public else "",
        "time_machine_link": '<p><a href="#compare-observations">Compare two historical views ↓</a></p>' if public else "",
        "footer_links": (
            '<span class="footer-links"><a href="/guide#coverage">Understand the coverage</a>'
            '<a href="/research">Research and methods</a><a href="/tour">Product tour</a></span>'
            if public else '<a href="https://sentiwiki.copernicus.eu/web/s2-processing#S2Processing-ClassificationMaskGeneration">Copernicus classification method</a>'
        ),
    }
    if snapshot is None:
        return template.substitute(
            **chrome,
            content="""<section class="unavailable">
<h2>Visibility report unavailable</h2>
<p>Check back after ForestProof has verified a Sentinel-2 report for this area.</p>
</section>""",
            attribution="Copernicus Sentinel-2 Level-2A",
        )

    checked = snapshot["checked"]
    acquisitions = snapshot["acquisitions"]
    overdue = now - checked >= CHECK_MAX_AGE
    if overdue:
        failure = " Latest check failed." if failed_at else ""
        status = (
            '<p class="status overdue"><strong>Source check overdue.</strong> '
            f'Showing the most recent verified report from {time_label(checked)}.{failure}</p>'
        )
    elif failed_at:
        status = (
            '<p class="status overdue"><strong>Latest source check failed.</strong> '
            f'Showing the report verified {time_label(checked)}.</p>'
        )
    else:
        status = f'<p class="status"><strong>Report verified</strong> {time_label(checked)}.</p>'

    archive = "\n".join(scene(day, latest=index == 0) for index, day in enumerate(acquisitions))
    history = f"""
<details class="archive" data-observation-archive open>
<summary>All sampled passes</summary>
<p class="archive-note">Read the same grid across dates. Each row retains its own sampled-cell denominator.</p>
{archive}
</details>"""
    method = """
<details class="method">
<summary>Sampling method and limits</summary>
<p>Each row counts native 20 m pixel centres inside the research rectangle. A centre counts as visible when the provider classifies the surface as vegetation, nonvegetated, or water. Cloud, shadow, unclassified, and no-data centres remain in the denominator.</p>
<p>The two grids overlap and each uses its own denominator. The page covers the listed passes only. Visibility does not measure disturbance or confirm field conditions.</p>
<p>Inspect the optional <a href="https://sentiwiki.copernicus.eu/web/s2-processing#S2Processing-ClassificationMaskGeneration">upstream Copernicus classification documentation</a>.</p>
</details>"""
    years = sorted({day["date"].year for day in acquisitions})
    attribution = " · ".join(f"Contains modified Copernicus Sentinel data [{year}]" for year in years)
    return template.substitute(
        **chrome,
        content=status + (explorer(acquisitions) if public else "") + READING_GUIDE + history + method,
        attribution=attribution,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    now = datetime.now(UTC)
    try:
        if args.output.suffix.lower() != ".html" or (args.report and args.report.resolve() == args.output.resolve()):
            raise ValueError("Choose a distinct HTML output")
        snapshot = project(read_report(args.report), now=now) if args.report else None
        write_page(args.output, render(snapshot, now=now))
    except (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError):
        parser.exit(1, "Could not generate the visibility page. Check the report and output path.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
