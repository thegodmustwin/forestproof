"""Render the public geographic atlas from the same reviewed visibility projection."""

from pathlib import Path
from string import Template

from tools.sentinel_visibility.build_visibility_page import CHECK_MAX_AGE, scene
from tools.source_status.build_source_status import time_label


TEMPLATE = Path(__file__).with_name("atlas.html")


def render_atlas(snapshot, *, now, failed_at=None):
    if snapshot is None:
        status = '<p class="status overdue"><strong>Observation report unavailable.</strong> Geography remains contextual; open the report to check its status.</p>'
        archive = '<p>No verified observation report is available. <a href="/visibility">View report status</a>.</p>'
    else:
        checked = snapshot["checked"]
        if now - checked >= CHECK_MAX_AGE:
            prefix = '<strong>Source check overdue.</strong> Last verified '
        elif failed_at:
            prefix = '<strong>Latest source check failed.</strong> Last verified '
        else:
            prefix = '<strong>Report verified</strong> '
        status = f'<p class="status">{prefix}{time_label(checked)}. Observation dates are separate.</p>'
        archive = "\n".join(scene(day, latest=index == 0) for index, day in enumerate(snapshot["acquisitions"]))
    return Template(TEMPLATE.read_text(encoding="utf-8")).substitute(
        atlas_styles='<link rel="stylesheet" href="/assets/atlas.css"><link rel="stylesheet" href="/assets/maplibre-gl.css">',
        atlas_script='<script type="module" src="/assets/atlas.js"></script>',
        observation_archive=archive,
        status=status,
    )
