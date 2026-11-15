"""Inspect co-registered archived GLAD-L status, alert-date and clear-date grids."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from pathlib import Path

import numpy as np
import rasterio

from inspect_glad_observation_dates import EXPECTED_EXTENT, ObservationDateTile, select_window, summarize_dates


BOUNDS = (36.60, -0.49, 36.63, -0.46)
BANDS = {"status": "uint8", "detection": "uint16", "observation": "uint16"}


def read_band(release, band, generation):
    remote = ObservationDateTile(generation, archive_day=release, band=band)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(remote.filename, opener=remote.open) as source:
            transform = source.transform
            if (source.driver != "GTiff" or source.crs is None or source.crs.to_epsg() != 4326
                    or source.count != 1 or source.dtypes != (BANDS[band],) or source.shape != (40000, 40000)
                    or source.bounds != EXPECTED_EXTENT or transform.b != 0 or transform.d != 0
                    or transform.a <= 0 or transform.e >= 0):
                raise ValueError(f"Unexpected native grid for {band}")
            window = select_window(source, BOUNDS)
            values = source.read(1, window=window, masked=True)
            if remote.read_error is not None:
                raise remote.read_error
    return transform, window, values, {
        "url": remote.url, "generation": generation, "etag": remote.etag,
        "last_modified": remote.last_modified, "bytes_read": remote.transfer_bytes,
        "window_sha256": sha256(values.data.astype("<u2").tobytes() + np.ma.getmaskarray(values).tobytes()).hexdigest(),
    }


def summarize_alerts(status, detection, *, release):
    max_day = (release - date(release.year, 1, 1)).days + 1
    if status.shape != detection.shape or not np.isin(status.compressed(), [0, 2, 3]).all():
        raise ValueError("Inconsistent native status or date values")
    probable = np.ma.filled(status == 2, False)
    confirmed = np.ma.filled(status == 3, False)
    flagged = probable | confirmed
    valid_alert_day = np.ma.filled((detection >= 1) & (detection <= max_day), False)
    if np.any(flagged & ~valid_alert_day):
        raise ValueError("A flagged cell lacks a plausible first detection day")
    alerted = detection.data[flagged]
    latest = date(release.year, 1, 1) + timedelta(days=int(alerted.max()) - 1) if alerted.size else None
    return {
        "sampled_centres": int(status.size),
        "probable_centres": int(probable.sum()),
        "confirmed_centres": int(confirmed.sum()),
        "masked_status_centres": int(np.ma.count_masked(status)),
        "masked_detection_centres": int(np.ma.count_masked(detection)),
        "latest_first_detection": latest.isoformat() if latest else None,
    }


def candidate_receipt(report, transform, window, status, detection, observation):
    confirmed = np.ma.filled(status == 3, False)
    if not confirmed.any():
        raise ValueError("The archive contains no source-confirmed candidate")
    latest = detection.data[confirmed].max()
    row, column = (int(value) for value in np.argwhere(confirmed & (detection.data == latest))[0])
    native_row, native_col = row + int(window.row_off), column + int(window.col_off)
    lon = transform.c + transform.a * (native_col + 0.5)
    lat = transform.f + transform.e * (native_row + 0.5)
    release = date.fromisoformat(report["release_folder_day"])
    year_start = date(release.year, 1, 1)
    observed = int(np.ma.filled(observation, 0)[row, column])
    return {
        "state": "PRIVATE_HISTORICAL_REVIEW_CANDIDATE",
        "source": report["source"],
        "scope": report["scope"],
        "archive_release_day": report["release_folder_day"],
        "checked_at": report["checked_at"],
        "assets": report["assets"],
        "native_grid": {"crs": "EPSG:4326", "row": native_row, "column": native_col},
        "centre_wgs84": [lon, lat],
        "provider_status_code": 3,
        "first_detection_day": (year_start + timedelta(days=int(latest) - 1)).isoformat(),
        "latest_clear_observation_day": (year_start + timedelta(days=observed - 1)).isoformat() if observed else None,
        "limits": (
            "Provider confirmation concerns the remote-sensing signal. "
            "Operational area approval, direct-source publication rights and owner review are pending."
        ),
    }


def inspect(release, generations, *, private_receipt=None):
    inputs = {band: read_band(release, band, generations[band]) for band in BANDS}
    if len({entry[0] for entry in inputs.values()}) != 1:
        raise ValueError("The three native transforms differ")
    status, detection, observation = (inputs[band][2] for band in BANDS)
    if not status.shape == detection.shape == observation.shape:
        raise ValueError("Unexpected native window sizes")
    report = {
        "source": "UMD GLAD-L C2 archive",
        "scope": "Provisional Geta research rectangle",
        "release_folder_day": release.isoformat(),
        "checked_at": datetime.now(UTC).isoformat(),
        "assets": {band: entry[3] for band, entry in inputs.items()},
        "alert_window": summarize_alerts(status, detection, release=release),
        "clear_observation_window": summarize_dates(observation, as_of=release),
        "native_alert_eligibility": "unknown",
    }
    if private_receipt is not None:
        transform, window, *_ = inputs["status"]
        receipt = candidate_receipt(report, transform, window, status, detection, observation)
        with private_receipt.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=date.fromisoformat)
    for band in BANDS:
        parser.add_argument(f"--{band}-generation", required=True)
    parser.add_argument("--private-receipt", type=Path, help="New JSON file in a trusted private directory.")
    args = parser.parse_args()
    try:
        report = inspect(args.release, {band: getattr(args, f"{band}_generation") for band in BANDS},
                         private_receipt=args.private_receipt)
    except (OSError, ValueError, rasterio.errors.RasterioError) as error:
        parser.exit(1, f"GLAD-L archive inspection failed: {error}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
