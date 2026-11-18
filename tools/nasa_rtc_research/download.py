"""One-batch, local-only ASF download with transient Earthdata credentials.

The manifest must come from a separately reviewed NASA catalog selection.
No source records or credentials are published by this tool.
"""

import argparse
import datetime as dt
import getpass
import hashlib
import http.cookiejar
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import warnings
from pathlib import Path

DATA_HOST = "cumulus.asf.earthdatacloud.nasa.gov"
AUTH_HOST = "urs.earthdata.nasa.gov"
REDIRECT_HOSTS = frozenset((DATA_HOST, AUTH_HOST, "auth.asf.alaska.edu", "d1bctmng8vmwga.cloudfront.net"))
MAX_FILE = 8 * 1024**3
MAX_BATCH = 100 * 1024**3
MAX_MANIFEST = 1024 * 1024
CHUNK = 1024 * 1024


class UnsafeInput(Exception):
    pass


def allowed_url(url, hosts):
    p = urllib.parse.urlsplit(url)
    try:
        port = p.port
    except ValueError:
        return False
    return (p.scheme == "https" and p.hostname in hosts and port in (None, 443)
            and p.username is None and p.password is None and not p.fragment)


def load_manifest(path):
    if path.stat().st_size > MAX_MANIFEST:
        raise UnsafeInput("Manifest is too large.")
    with path.open("r", encoding="utf-8") as stream:
        doc = json.load(stream)
    if not isinstance(doc, dict) or set(doc) != {"bounds_wgs84", "assets"}:
        raise UnsafeInput("Unexpected manifest fields.")
    bounds = doc["bounds_wgs84"]
    if (not isinstance(bounds, list) or len(bounds) != 4 or
            any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in bounds)):
        raise UnsafeInput("Invalid research bounds.")
    west, south, east, north = bounds
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise UnsafeInput("Invalid research bounds.")
    assets = doc["assets"]
    if not isinstance(assets, list) or len(assets) != 21:
        raise UnsafeInput("Expected exactly 21 assets.")
    required = {"day", "role", "band", "filename", "url", "concept_id", "size_bytes", "md5"}
    filenames, identities, combinations = set(), set(), set()
    total = 0
    for item in assets:
        if not isinstance(item, dict) or set(item) != required:
            raise UnsafeInput("Unexpected asset fields.")
        day, role, band = item["day"], item["role"], item["band"]
        try:
            if not isinstance(day, str) or dt.date.fromisoformat(day).isoformat() != day:
                raise ValueError()
        except ValueError:
            raise UnsafeInput("Invalid acquisition date.") from None
        if role not in ("reference", "target") or band not in ("VV", "VH", "mask"):
            raise UnsafeInput("Invalid asset role or band.")
        name, url, concept, size, md5 = (item[x] for x in ("filename", "url", "concept_id", "size_bytes", "md5"))
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.tif", name, re.I):
            raise UnsafeInput("Invalid asset filename.")
        if not isinstance(url, str) or not allowed_url(url, {DATA_HOST}):
            raise UnsafeInput("Unapproved asset URL.")
        parsed = urllib.parse.urlsplit(url)
        if parsed.query or not parsed.path.startswith("/OPERA/OPERA_L2_RTC-S1"):
            raise UnsafeInput("Unapproved asset path.")
        pieces = parsed.path.split("/")
        if any(part in (".", "..") or "%" in part for part in pieces) or pieces[-1] != name:
            raise UnsafeInput("Asset path and filename do not match.")
        if not isinstance(concept, str) or not re.fullmatch(r"G[0-9]+-[A-Za-z0-9_-]+", concept):
            raise UnsafeInput("Invalid catalog concept ID.")
        if isinstance(size, bool) or not isinstance(size, int) or not 1 <= size <= MAX_FILE:
            raise UnsafeInput("Invalid catalog file size.")
        if not isinstance(md5, str) or not re.fullmatch(r"[0-9a-fA-F]{32}", md5):
            raise UnsafeInput("Invalid catalog checksum.")
        combo = (day, band)
        if name.lower() in filenames or url in identities or combo in combinations:
            raise UnsafeInput("Duplicate asset or day/band.")
        filenames.add(name.lower())
        identities.add(url)
        combinations.add(combo)
        total += size
    if total > MAX_BATCH or len({x["day"] for x in assets}) != 7:
        raise UnsafeInput("Unexpected batch size or day count.")
    for day in {x["day"] for x in assets}:
        day_items = [x for x in assets if x["day"] == day]
        if {x["band"] for x in day_items} != {"VV", "VH", "mask"} or len({x["role"] for x in day_items}) != 1:
            raise UnsafeInput("Incomplete or inconsistent daily asset set.")
    return assets


def md5_new():
    return hashlib.md5(usedforsecurity=False)


def valid_file(path, asset):
    if path.is_symlink() or not path.is_file() or path.stat().st_size != asset["size_bytes"]:
        return False
    digest = md5_new()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest().lower() == asset["md5"].lower()


class RestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl, REDIRECT_HOSTS):
            raise UnsafeInput("Download redirected to an unapproved host.")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            for key in list(redirected.headers):
                if key.lower() in ("authorization", "proxy-authorization"):
                    del redirected.headers[key]
            for key in list(redirected.unredirected_hdrs):
                if key.lower() in ("authorization", "proxy-authorization"):
                    del redirected.unredirected_hdrs[key]
        return redirected


def create_opener(username, password):
    manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, "https://" + AUTH_HOST, username, password)
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}), RestrictedRedirect(),
        urllib.request.HTTPBasicAuthHandler(manager),
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    )


def download(opener, asset, directory):
    destination = directory / asset["filename"]
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".forestproof-download-", suffix=".part", dir=directory, delete=False) as out:
            tmp = Path(out.name)
            digest = md5_new()
            count = 0
            request = urllib.request.Request(asset["url"], headers={"User-Agent": "ForestProof research batch/1.0"})
            with opener.open(request, timeout=90) as response:
                if response.status != 200 or not allowed_url(response.geturl(), REDIRECT_HOSTS):
                    raise UnsafeInput("Provider did not return an approved data response.")
                for chunk in iter(lambda: response.read(CHUNK), b""):
                    count += len(chunk)
                    if count > asset["size_bytes"]:
                        raise UnsafeInput("Downloaded asset exceeds catalog size.")
                    digest.update(chunk)
                    out.write(chunk)
            if count != asset["size_bytes"] or digest.hexdigest().lower() != asset["md5"].lower():
                raise UnsafeInput("Downloaded asset did not match catalog size and checksum.")
            out.flush()
            os.fsync(out.fileno())
        # Hard-link within the same directory atomically fails if destination exists.
        os.link(tmp, destination)
    finally:
        if tmp is not None:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass


def main():
    parser = argparse.ArgumentParser(description="Download one reviewed ASF research batch locally.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        assets = load_manifest(args.manifest)
        if not args.output_dir.is_dir() or args.output_dir.is_symlink():
            raise UnsafeInput("Output directory must already exist and not be a symbolic link.")
        missing = []
        for asset in assets:
            path = args.output_dir / asset["filename"]
            if path.exists() or path.is_symlink():
                if not valid_file(path, asset):
                    raise UnsafeInput("An existing file does not match the catalog; no files overwritten.")
            else:
                missing.append(asset)
        print(f"Verified {len(assets) - len(missing)}/{len(assets)} existing assets; {len(missing)} needed.", flush=True)
        if args.check_only or not missing:
            return 0
        if not sys.stdin.isatty():
            raise UnsafeInput("Interactive terminal required for private sign-in.")
        username = input("Earthdata username: ").strip()
        if not username:
            raise UnsafeInput("Earthdata username is required.")
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("Earthdata password (not shown): ")
        if not password:
            raise UnsafeInput("Earthdata password is required.")
        opener = create_opener(username, password)
        del username, password
        for index, asset in enumerate(missing, 1):
            download(opener, asset, args.output_dir)
            print(f"Verified {index}/{len(missing)} newly downloaded assets.", flush=True)
        print("Batch complete: all downloaded assets matched catalog size and checksum.", flush=True)
        return 0
    except UnsafeInput as exc:
        print(f"SETUP OR DOWNLOAD DID NOT COMPLETE: {exc}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as exc:
        print(f"DOWNLOAD DID NOT COMPLETE: provider returned HTTP {exc.code}. Check account authorization and retry only after reviewing saved files.", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, getpass.GetPassWarning):
        print("SETUP OR DOWNLOAD DID NOT COMPLETE. No credentials were displayed; verify manifest, access and existing files before retrying.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("DOWNLOAD STOPPED. Completed verified files remain available for resuming.", file=sys.stderr)
        return 1
    except Exception:
        print("DOWNLOAD DID NOT COMPLETE. Check Earthdata access and network; retry only after reviewing saved files.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
