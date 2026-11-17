"""Render ForestProof's public entry page from the reviewed visibility report."""

from pathlib import Path
from string import Template

from tools.sentinel_visibility.build_visibility_page import CHECK_MAX_AGE
from tools.source_status.build_source_status import day_label, time_label


TEMPLATE = Path(__file__).with_name("welcome.html")


def render_home(snapshot, *, now, failed_at=None):
    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    if snapshot is None:
        return template.substitute(
            snapshot=(
                '<p class="kicker">Geta visibility</p>'
                '<h2>Report unavailable</h2>'
                '<p class="context">Check back when the next verified report is available.</p>'
            ),
            attribution="",
        )

    latest = snapshot["acquisitions"][0]
    rows = []
    for tile in latest["tiles"]:
        percent = tile["visible"] / tile["sampled"] * 100
        if 0 < percent < 0.1:
            label = "&lt;0.1%"
        else:
            label = f"{percent:.1f}%" if percent else "0%"
        rows.append(
            f'<li><span class="grid-label">{tile["grid"]}</span>'
            f'<span class="track" aria-hidden="true"><span style="width:{percent:.6f}%"></span></span>'
            f'<strong>{label} <span hidden>visible</span></strong></li>'
        )
    checked = snapshot["checked"]
    if now - checked >= CHECK_MAX_AGE:
        status = "<strong>Source check overdue.</strong> Last verified "
    elif failed_at:
        status = "<strong>Latest source check failed.</strong> Last verified "
    else:
        status = "Source files checked "
    return template.substitute(
        snapshot=(
            '<p class="kicker">Latest sampled pass</p>'
            f'<h2>{day_label(latest["date"])}</h2>'
            '<p class="context">Share of sampled cells visible in each overlapping grid.</p>'
            f'<ul class="quick-read" aria-label="Visible share by grid">{"".join(rows)}</ul>'
            f'<p class="context">{status}{time_label(checked)}.</p>'
        ),
        attribution=f'· Contains modified Copernicus Sentinel data [{latest["date"].year}]',
    )
