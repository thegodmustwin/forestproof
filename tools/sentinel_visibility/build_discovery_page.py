"""Render discovery from the already validated, public visibility projection.

Only explicitly selected public fields enter the page; no raw provider receipts,
private records or source-state files are indexed.
"""
from datetime import datetime
from html import escape
from pathlib import Path
from string import Template

from tools.sentinel_visibility.build_visibility_page import CHECK_MAX_AGE, percent_label
from tools.source_status.build_source_status import time_label

TEMPLATE = Path(__file__).with_name("discovery.html")


def _observation(day, tile):
    date = day["date"]
    grid = tile["grid"]
    visible, sampled = tile["visible"], tile["sampled"]
    image = grid == "T36MZE" and date.isoformat() in ("2026-11-08", "2026-11-13")
    share = percent_label(visible, sampled)
    quality = "clearer" if visible / sampled >= .1 else "limited"
    image_text = "Published image context available." if image else "Matching image context unavailable."
    url = f"/atlas/geta?grid={escape(grid, quote=True)}&amp;date={date.isoformat()}"
    return f'''<article class="result" data-search-record data-kind="observation" data-place="geta" data-source="sentinel-2" data-quality="{quality}" data-date="{date.isoformat()}" data-grid="{escape(grid, quote=True)}" data-search="geta kenya sentinel-2 sentinel optical coverage visibility observation {date.isoformat()} {date.strftime('%d %B %Y').lower()} {date.strftime('%d %b %Y').lower()} {escape(grid.lower(), quote=True)} {'image available' if image else 'missing imagery'}">
<p class="eyebrow">Optical coverage · Sentinel-2 · {escape(grid)}</p>
<h3><a href="{url}">Geta · <time datetime="{date.isoformat()}">{date.strftime('%d %b %Y')}</time> · {escape(grid)}</a></h3>
<p>{visible:,} of {sampled:,} sampled centres visible ({share}). {image_text}</p>
<p class="limit">Usable optical coverage, not a forest-loss alert. The research rectangle is provisional.</p>
<p class="why" data-why>Included in the published visibility report. <a href="/guide#coverage">How coverage is measured</a>{' · <a href="/assets/geta-context.json">Image provenance</a>' if image else ''}</p>
</article>'''


def render_discovery(snapshot: dict | None, *, now: datetime, failed_at: datetime | None = None) -> str:
    if snapshot is None:
        status = '<strong>Observation report unavailable.</strong> Published observations will appear after a report is verified.'
        observations = ''
    else:
        checked = snapshot["checked"]
        if now - checked >= CHECK_MAX_AGE:
            prefix = '<strong>Source check overdue.</strong> Last verified '
        elif failed_at:
            prefix = '<strong>Latest source check failed.</strong> Last verified '
        else:
            prefix = '<strong>Report verified</strong> '
        status = prefix + time_label(checked) + '. Observation dates are separate.'
        observations = '\n'.join(_observation(day, tile) for day in snapshot['acquisitions'] for tile in day['tiles'])
    dates = '' if snapshot is None else ''.join(
        f'<option value="{day["date"].isoformat()}">{day["date"].strftime("%d %b %Y")}</option>'
        for day in snapshot['acquisitions']
    )
    return Template(TEMPLATE.read_text(encoding='utf-8')).substitute(status=status, observations=observations, dates=dates)
