"""Measure local cloud-free observation recency from one published GLAD-L date tile."""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import time
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from pathlib import PurePath
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

import numpy as np
import rasterio
from rasterio.coords import BoundingBox
from rasterio.windows import Window, from_bounds


BASE_URL = "https://storage.googleapis.com/earthenginepartners-hansen/GLADalert/C2/current"
TILE = "obsDate_030E_10S_040E_00N.tif"
EXPECTED_EXTENT = BoundingBox(30, -10, 40, 0)
BLOCK_SIZE = 256 * 1024
TRANSFER_LIMIT = 8 * 1024 * 1024
RECENCY_DAYS = (7, 14, 30, 60)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ObservationDateTile:
    """Read a pinned object through budgeted byte ranges for offline inspection."""

    def __init__(self, generation: str, *, opener=None):
        if not re.fullmatch(r"[0-9]{1,20}", generation):
            raise ValueError("Expected an exact numeric provider object generation")
        self.url = f"{BASE_URL}/{TILE}?{urlencode({'generation': generation})}"
        self._generation = generation
        self._opener = opener or build_opener(NoRedirect())
        self._deadline = time.monotonic() + 90
        self._blocks: dict[int, bytes] = {}
        self.transfer_bytes = 0
        self.read_error: Exception | None = None
        with self._request() as response:
            if response.status != 200 or response.headers.get("x-goog-generation") != generation:
                raise ValueError("Could not verify the pinned tile generation")
            length = response.headers.get("Content-Length", "")
            if not re.fullmatch(r"[0-9]{1,10}", length) or int(length) <= 0:
                raise ValueError("Invalid tile content length")
            self.size = int(length)
            self.etag = response.headers.get("ETag")
            self.last_modified = response.headers.get("Last-Modified")
            if not self.etag or not self.last_modified:
                raise ValueError("The provider did not return tile identity and modification time")

    def _request(self, start: int | None = None, end: int | None = None):
        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Tile inspection took too long")
        headers = {"Accept-Encoding": "identity", "User-Agent": "ForestProof-GLAD-Coverage/1.0"}
        if start is not None:
            headers["Range"] = f"bytes={start}-{end}"
        return self._opener.open(
            Request(self.url, method="HEAD" if start is None else "GET", headers=headers),
            timeout=min(12.0, remaining),
        )

    def open(self, path, mode="rb"):
        if PurePath(path).name != TILE or mode not in {"r", "rb"}:
            raise FileNotFoundError(path)
        return TileHandle(self)

    def read_at(self, position, size):
        end = self.size if size < 0 else min(self.size, position + size)
        if end - position > TRANSFER_LIMIT:
            raise ValueError("Refusing an oversized raster read")
        chunks = []
        while position < end:
            block_start = position // BLOCK_SIZE * BLOCK_SIZE
            block = self._blocks.get(block_start)
            if block is None:
                block = self._fetch_block(block_start)
                self._blocks[block_start] = block
            offset = position - block_start
            part = block[offset:offset + end - position]
            chunks.append(part)
            position += len(part)
        return b"".join(chunks)

    def _fetch_block(self, start: int):
        end = min(start + BLOCK_SIZE, self.size) - 1
        size = end - start + 1
        if self.transfer_bytes + size > TRANSFER_LIMIT:
            raise ValueError("Tile inspection exceeded the transfer budget")
        with self._request(start, end) as response:
            if (
                response.status != 206
                or response.headers.get("Content-Range") != f"bytes {start}-{end}/{self.size}"
                or response.headers.get("x-goog-generation") != self._generation
                or response.headers.get("ETag") != self.etag
                or response.headers.get("Content-Encoding", "identity") != "identity"
            ):
                raise ValueError("Provider response did not match the pinned byte range")
            data = response.read(size + 1)
        if len(data) != size:
            raise ValueError("Incomplete pinned byte range")
        self.transfer_bytes += size
        return data


class TileHandle(io.RawIOBase):
    def __init__(self, tile):
        super().__init__()
        self._tile = tile
        self._position = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self._position

    def seek(self, offset, whence=io.SEEK_SET):
        self._checkClosed()
        base = {io.SEEK_SET: 0, io.SEEK_CUR: self._position, io.SEEK_END: self._tile.size}[whence]
        if base + offset < 0:
            raise ValueError("Cannot seek before the beginning of the tile")
        self._position = base + offset
        return self._position

    def read(self, size=-1):
        self._checkClosed()
        try:
            data = self._tile.read_at(self._position, size)
        except (OSError, ValueError) as exc:
            # GDAL invokes this through a callback that can swallow Python errors.
            self._tile.read_error = exc
            raise
        self._position += len(data)
        return data


def select_window(dataset, bounds: tuple[float, float, float, float]) -> Window:
    west, south, east, north = bounds
    if not (
        all(math.isfinite(value) for value in bounds)
        and dataset.bounds.left <= west < east <= dataset.bounds.right
        and dataset.bounds.bottom <= south < north <= dataset.bounds.top
        and east - west <= 0.05 and north - south <= 0.05
    ):
        raise ValueError("Use a rectangle up to 0.05 degrees per side inside the tile")
    raw = from_bounds(*bounds, dataset.transform)
    # Select native pixel centres inside the half-open native window.
    col_start = math.ceil(round(raw.col_off - 0.5, 8))
    row_start = math.ceil(round(raw.row_off - 0.5, 8))
    col_end = math.ceil(round(raw.col_off + raw.width - 0.5, 8))
    row_end = math.ceil(round(raw.row_off + raw.height - 0.5, 8))
    if col_end <= col_start or row_end <= row_start:
        raise ValueError("The rectangle contains no complete native sampling centres")
    return Window(col_start, row_start, col_end - col_start, row_end - row_start)


def summarize_dates(data: np.ma.MaskedArray, *, as_of: date) -> dict:
    """Keep documented zero-day values separate from GDAL-masked cells."""
    first_day = date(as_of.year, 1, 1)
    current_day = (as_of - first_day).days + 1
    values = data.compressed()
    if np.any(values > current_day):
        raise ValueError("The raster contains a date later than the requested reporting day")
    observed = values[values > 0]
    latest = (first_day + timedelta(days=int(observed.max()) - 1)).isoformat() if observed.size else None
    return {
        "sampled_centres": int(data.size),
        "masked_centres": int(np.ma.count_masked(data)),
        "no_clear_observation_this_year_centres": int(np.count_nonzero(values == 0)),
        "observed_this_year_centres": int(observed.size),
        "latest_cloud_free_observation_day": latest,
        "centres_observed_within_days": {
            str(days): int(np.count_nonzero(current_day - observed.astype(np.int32) <= days))
            for days in RECENCY_DAYS
        },
    }


def inspect(generation: str, bounds: tuple[float, float, float, float], as_of: date) -> dict:
    remote = ObservationDateTile(generation)
    published = parsedate_to_datetime(remote.last_modified).date()
    if published.year != as_of.year or published > as_of:
        raise ValueError("The reporting day must be on or after asset publication in the same year")
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(TILE, opener=remote.open) as dataset:
            if (
                dataset.driver != "GTiff"
                or dataset.crs is None
                or dataset.crs.to_epsg() != 4326
                or dataset.count != 1
                or dataset.dtypes != ("uint16",)
                or dataset.shape != (40000, 40000)
                or dataset.bounds != EXPECTED_EXTENT
                or dataset.transform.b != 0 or dataset.transform.d != 0
                or dataset.transform.a <= 0 or dataset.transform.e >= 0
            ):
                raise ValueError("Unexpected GLAD-L observation-date raster grid")
            cells = dataset.read(1, window=select_window(dataset, bounds), masked=True)
            if remote.read_error is not None:
                raise remote.read_error
            stats = summarize_dates(cells, as_of=as_of)
    return {
        "source": "UMD GLAD-L observation date",
        "scope": "Provisional research rectangle",
        "source_url": remote.url,
        "source_generation": generation,
        "source_etag": remote.etag,
        "source_last_modified": remote.last_modified,
        "range_bytes_read": remote.transfer_bytes,
        "window_values_sha256": sha256(cells.data.astype("<u2").tobytes() + np.ma.getmaskarray(cells).tobytes()).hexdigest(),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "as_of": as_of.isoformat(),
        "bounds_wgs84": list(bounds),
        **stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", required=True, help="Exact GCS object generation for the date layer.")
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    parser.add_argument("--bounds", required=True, type=float, nargs=4, metavar=("WEST", "SOUTH", "EAST", "NORTH"))
    args = parser.parse_args()
    try:
        result = inspect(args.generation, tuple(args.bounds), args.as_of)
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        parser.exit(1, f"Observation-date check failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())