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
  <div class="controls">
    <div><span class="control-title" id="grid-control-label">Keep one image grid selected</span>
      <div class="grid-choices" role="group" aria-labelledby="grid-control-label">{grid_buttons}</div>
      <p class="control-help">These grids overlap the same research area. Their counts are separate, so compare one grid across dates.</p>
    </div>
    <div class="best-pass"><p class="control-title">Find a more usable view</p><p data-best-summary></p><button class="best-choice" type="button" data-select-best>Show clearest sampled pass</button></div>
  </div>
  <div class="explorer-instrument">
  <section class="pass-comparison" aria-labelledby="comparison-title">
    <div class="comparison-heading"><h2 id="comparison-title">Compare sampled passes</h2><p>Usable share of each grid's sampled centres</p></div>
    <div class="comparison-scale" aria-hidden="true"><span>0% visible</span><span>100%</span></div>
    <div class="pass-choices" role="group" aria-label="Choose a satellite pass">{pass_buttons}</div>
    <p class="comparison-note">Every bar uses the full 0–100% scale. An almost empty bar means that most ground conditions could not be assessed.</p>
  </section>
  <div class="observation-panel">
    <div class="observation-main">
      <p class="eyebrow">Selected pass · <span data-selected-grid></span></p>
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
  <div class="continue-workflow"><div><p class="eyebrow">From a signal to a decision</p><h3>What happens after an observation?</h3><p>Try a clearly labelled fictional case and see how evidence, review and follow-up fit together.</p></div><a class="continue-link" href="/tour">Try the case walkthrough</a></div>
  <p class="sr-only" role="status" aria-live="polite" data-selection-announcement></p>
</section>"""


def render(snapshot: dict | None, *, now: datetime, public: bool = False, failed_at: datetime | None = None) -> str:
    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    masthead = (
        '<nav class="public-nav" aria-label="Page navigation">'
        '<a href="/welcome">Home</a><a href="/visibility" aria-current="page">Explore Geta</a>'
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
