"""Render an isolated, read-only ForestProof source-status preview from a GLAD-L report."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

SOURCE_URL = "https://storage.googleapis.com/earthenginepartners-hansen/GLADalert/C2/current/obsDate_030E_10S_040E_00N.tif"
BOUNDS = [36.60, -0.49, 36.63, -0.46]
WINDOWS = (7, 14, 30, 60)
MAX_REPORT_BYTES = 16_384
PAGE = Path(__file__).with_name("source_status.html")


def read_date(value: str) -> date:
    day = date.fromisoformat(value)
    if value != day.isoformat():
        raise ValueError("Expected an ISO calendar date")
    return day


def utc_time(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("Expected a timestamp with timezone")
    return value.astimezone(UTC)


def project(report: dict, *, now: datetime) -> dict:
    if not isinstance(report, dict) or report.get("source") != "UMD GLAD-L observation date":
        raise ValueError("Expected a GLAD-L observation-date report")
    if report.get("bounds_wgs84") != BOUNDS:
        raise ValueError("Unexpected research rectangle")
    generation = report["source_generation"]
    if not isinstance(generation, str) or not re.fullmatch(r"[0-9]{1,20}", generation):
        raise ValueError("Invalid source generation")
    if report.get("source_url") != f"{SOURCE_URL}?generation={generation}":
        raise ValueError("Unexpected observation-date source object")

    last_modified = report["source_last_modified"]
    if not isinstance(last_modified, str):
        raise ValueError("Expected a provider modification timestamp")
    modified = utc_time(parsedate_to_datetime(last_modified))
    checked = utc_time(datetime.fromisoformat(report["checked_at"]))
    as_of = read_date(report["as_of"])
    raw_latest = report["latest_cloud_free_observation_day"]
    latest = None if raw_latest is None else read_date(raw_latest)
    if not (modified <= checked <= now and modified.year == as_of.year
            and modified.date() <= as_of <= checked.date()):
        raise ValueError("Inconsistent source, check and reporting dates")
    if latest and not date(as_of.year, 1, 1) <= latest <= modified.date():
        raise ValueError("Observation date is outside the source window")

    total, masked, no_clear, observed = (report[key] for key in (
        "sampled_centres", "masked_centres", "no_clear_observation_this_year_centres",
        "observed_this_year_centres",
    ))
    if total != 14_400 or any(type(n) is not int or not 0 <= n <= total for n in (total, masked, no_clear, observed)):
        raise ValueError("Invalid sample counts")
    if masked + no_clear + observed != total or bool(latest) != bool(observed):
        raise ValueError("Inconsistent sample counts or latest date")
    counts = report["centres_observed_within_days"]
    if not isinstance(counts, dict) or set(counts) != {str(days) for days in WINDOWS}:
        raise ValueError("Unexpected observation windows")
    age = (as_of - latest).days if latest else None
    previous = 0
    rows = []
    for days in WINDOWS:
        count = counts[str(days)]
        if (type(count) is not int or not previous <= count <= observed
                or bool(count) != (age is not None and age <= days)):
            raise ValueError("Inconsistent observation-window count")
        rows.append((days, count, count / total * 100))
        previous = count
    return {
        "checked": checked, "modified": modified, "as_of": as_of, "latest": latest,
        "total": total, "masked": masked, "no_clear": no_clear, "rows": rows,
    }


def time_label(moment: datetime) -> str:
    return f'<time datetime="{moment.isoformat()}">{moment:%d %b %Y, %H:%M UTC}</time>'


def day_label(day: date) -> str:
    return f'<time datetime="{day.isoformat()}">{day:%d %b %Y}</time>'


def render(snapshot: dict | None) -> str:
    layout = PAGE.read_text(encoding="utf-8")
    if snapshot is None:
        content = """<section class="unavailable" aria-labelledby="empty-title">
<h2 id="empty-title">Source report unavailable</h2>
<p>ForestProof has no source report to display for this area. Local observation dates and coverage are unknown.</p>
</section>"""
        return layout.replace("<!-- STATUS CONTENT -->", content)
    latest = snapshot["latest"]
    as_of = snapshot["as_of"]
    title = day_label(latest) if latest else "Unknown"
    age = (as_of - latest).days if latest else None
    age_note = f"{age} calendar days before the reporting date." if age is not None else "The report contains no cloud-free date for this year."
    rows = "\n".join(
        f'<li><span>{days} days</span><span class="track" aria-hidden="true"><span style="width:{percentage:.1f}%"></span></span>'
        f'<strong>{percentage:.1f}%</strong><small>{count:,} locations</small></li>'
        for days, count, percentage in snapshot["rows"]
    )
    content = f"""<section class="reading" aria-labelledby="latest-label">
<div class="headline">
<h2 id="latest-label">Latest local cloud-free observation</h2>
<p class="date">{title}</p>
<p>{age_note}</p>
</div>
<dl class="clocks">
<div><dt>Provider file updated</dt><dd>{time_label(snapshot["modified"])}</dd></div>
<div><dt>ForestProof checked</dt><dd>{time_label(snapshot["checked"])}</dd></div>
<div><dt>Reporting date</dt><dd>{day_label(as_of)}</dd></div>
</dl>
</section>
<section class="coverage" id="observation-windows" aria-labelledby="coverage-heading">
<h2 id="coverage-heading">How recently was the area observed?</h2>
<p>Share of {snapshot["total"]:,} sample locations with a cloud-free observation by {day_label(as_of)}.</p>
<ul class="windows">{rows}</ul>
<details id="method"><summary>Sampling method and limits</summary>
<p>Each sample is the centre of a cell in the source raster. The windows include the reporting day. {snapshot["no_clear"]:,} locations had no cloud-free date this year and {snapshot["masked"]:,} were masked in the raster. Both count toward the total sample.</p>
<p>Observation dates describe what the source could see. Alert eligibility and ground conditions remain unknown. The research area has a provisional extent.</p>
</details>
</section>"""
    return layout.replace("<!-- STATUS CONTENT -->", content)


def read_report(path: Path) -> dict:
    with path.open("rb") as stream:
        payload = stream.read(MAX_REPORT_BYTES + 1)
    if len(payload) > MAX_REPORT_BYTES:
        raise ValueError("Report is too large")
    return json.loads(payload)


def write_page(path: Path, html: str) -> None:
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, mode="w", encoding="utf-8", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(html)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.suffix.lower() != ".html" or (args.report and args.report.resolve() == args.output.resolve()):
            raise ValueError("Choose a distinct HTML output")
        snapshot = project(read_report(args.report), now=datetime.now(UTC)) if args.report else None
        write_page(args.output, render(snapshot))
    except (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError):
        parser.exit(1, "Could not generate the source-status page. Check the report and output path.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
