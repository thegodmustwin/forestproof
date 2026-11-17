"""Render the visibility page from a reviewed Sentinel-2 report."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path
from string import Template

from tools.sentinel_visibility.project_visibility import project
from tools.source_status.build_source_status import day_label, read_report, time_label, write_page


TEMPLATE = Path(__file__).with_name("visibility.html")
CHECK_MAX_AGE = timedelta(hours=36)
READING_GUIDE = """
<section class="reading-guide" aria-labelledby="reading-guide-title">
<h2 id="reading-guide-title">How to read this report</h2>
<div>
<p><strong>Start with the percentages.</strong> Each shows the share of a grid inside the research area that the satellite could assess on that pass. Near zero means most of that grid was unassessed. The vegetation count comes from the visible cells in that row.</p>
<p><strong>Compare the same grid code across dates.</strong> The two grids overlap, so read their counts separately. Pass dates tell you when the satellite took the images. The report verification time tells you when ForestProof last verified the source.</p>
</div>
</section>
"""


def grid_row(tile: dict) -> str:
    visible, sampled = tile["visible"], tile["sampled"]
    percent = 100 * visible / sampled
    if visible == 0:
        display = "0%"
    elif percent < 0.1:
        display = "&lt;0.1%"
    else:
        display = f"{percent:.1f}%"
    return f"""
<li class="grid-row">
  <span class="grid-name">{tile["grid"]}</span>
  <div class="track" aria-hidden="true"><span style="width:{percent:.6f}%"></span></div>
  <span class="reading"><strong>{display}</strong><span>{visible:,} of {sampled:,} visible</span></span>
  <span class="vegetation">{tile["vegetation"]:,} classified as vegetation</span>
</li>"""


def scene(day: dict, *, latest: bool = False) -> str:
    date = day["date"]
    pass_time = f'<time datetime="{date.isoformat()}">{day_label(date)}</time>'
    heading = f"<h2>{pass_time}</h2>" if latest else f"<h3>{pass_time}</h3>"
    caption = '<p class="eyebrow">Latest pass in this report</p>' if latest else ""
    rows = "\n".join(grid_row(tile) for tile in day["tiles"])
    return f"""
<article class="pass{' latest' if latest else ''}">
  <header>{caption}{heading}</header>
  <ul class="grids" aria-label="Visibility by tile">{rows}</ul>
</article>"""


def render(snapshot: dict | None, *, now: datetime, public: bool = False, failed_at: datetime | None = None) -> str:
    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    masthead = "" if public else '<p class="flag">Private research preview</p>'
    robots = "" if public else '<meta name="robots" content="noindex">'
    brand = (
        '<a class="brand" href="/welcome">ForestProof</a>'
        if public
        else '<div class="brand">ForestProof</div>'
    )
    chrome = {"brand": brand, "masthead": masthead, "robots": robots}
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
    latest, *earlier = snapshot["acquisitions"]
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
    history = ""
    if earlier:
        days = "\n".join(scene(pass_day) for pass_day in earlier)
        history = f'<section class="history" aria-labelledby="history"><h2 id="history">Earlier sampled passes</h2>{days}</section>'

    method = """
<details>
<summary>Sampling method and limits</summary>
<p>Each row counts native 20 m pixel centres inside the research rectangle. A centre counts as visible when the provider classifies the surface as vegetation, nonvegetated, or water. Cloud, shadow, unclassified, and no-data centres remain in the denominator.</p>
<p>The two grids overlap and each uses its own denominator. The page covers the listed passes only. Visibility does not measure disturbance or confirm field conditions.</p>
</details>"""
    years = sorted({day["date"].year for day in snapshot["acquisitions"]})
    attribution = " · ".join(f"Contains modified Copernicus Sentinel data [{year}]" for year in years)
    return template.substitute(
        **chrome,
        content=READING_GUIDE + status + scene(latest, latest=True) + history + method,
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
