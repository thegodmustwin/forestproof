"""Score a predeclared radar rule on the independent 2019 Mount Kenya fire."""

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from hashlib import file_digest, sha256
import json
from pathlib import Path

import numpy as np

from radar import BOUNDS, GRID, ROOT, SHAPE, asset_url, capture_metadata, read_band


REFERENCES = (
    ("2019-01-28", "02DA52"),
    ("2019-02-09", "02E09C"),
    ("2019-02-21", "02E6CE"),
)
TARGET = ("2019-03-17", "02F38A")
THRESHOLDS = (2, 3, 4)
BURN_INTERIOR_CELLS = 3
CONTROL_BUFFER_CELLS = 14
STABLE_NBR_MAX_CHANGE = 0.07
SEED = 345


def neighbours(mask, radius):
    padded = np.pad(mask, radius, constant_values=False)
    summed = np.pad(padded, ((1, 0), (1, 0))).cumsum(0, dtype=np.int32).cumsum(1, dtype=np.int32)
    width = 2 * radius + 1
    return summed[width:, width:] - summed[:-width, width:] - summed[width:, :-width] + summed[:-width, :-width]


def radar_capture(identity, with_angle=False):
    metadata = capture_metadata(*identity)
    bands = ("VV", "VH", "MASK", "ANGLE") if with_angle else ("VV", "VH", "MASK")
    with ThreadPoolExecutor(max_workers=3) as pool:
        arrays = list(pool.map(lambda band: read_band(*identity, band), bands))
    vv, vh, mask = arrays[:3]
    valid = (mask == 1) & np.isfinite(vv) & np.isfinite(vh) & (vv > 0) & (vh > 0)
    return (
        np.where(valid, vv, np.nan),
        np.where(valid, vh, np.nan),
        arrays[3] if with_angle else None,
        metadata["properties"]["datetime"],
    )


def baseline(captures):
    vv = np.stack([capture[0] for capture in captures])
    vh = np.stack([capture[1] for capture in captures])
    valid = np.isfinite(vv).all(axis=0)
    return np.median(vv, axis=0), np.median(vh, axis=0), valid


def matched_indices(affected, control, vv, vh, angle, nbr):
    # Groups use only pre-event observations and acquisition geometry.
    def by_stratum(mask):
        indices = np.flatnonzero(mask)
        covariates = zip(
            np.floor(10 * np.log10(vv.flat[indices]) / 3).astype(np.int16),
            np.floor(10 * np.log10(vh.flat[indices]) / 3).astype(np.int16),
            angle.flat[indices] // 5,
            np.floor(nbr.flat[indices] / 0.15).astype(np.int16),
            strict=True,
        )
        groups = defaultdict(list)
        for index, covariate in zip(indices, covariates, strict=True):
            groups[covariate].append(index)
        return groups

    burn_groups = by_stratum(affected)
    control_groups = by_stratum(control)
    rng = np.random.default_rng(SEED)
    matches = [[], []]
    for group in sorted(burn_groups.keys() & control_groups.keys()):
        count = min(len(burn_groups[group]), len(control_groups[group]))
        matches[0].extend(rng.choice(burn_groups[group], count, replace=False))
        matches[1].extend(rng.choice(control_groups[group], count, replace=False))
    if not matches[0]:
        raise ValueError("No overlapping pre-event covariate strata")
    return tuple(np.asarray(match, dtype=np.intp) for match in matches)


def summaries(vv_change, vh_change, selection):
    vv = vv_change.ravel()[selection]
    vh = vh_change.ravel()[selection]
    eligible = np.isfinite(vv) & np.isfinite(vh)
    vv, vh = vv[eligible], vh[eligible]
    return {
        "selected_cells": int(len(eligible)),
        "assessed_cells": int(len(vv)),
        "unavailable_cells": int(len(eligible) - len(vv)),
        "median_vv_change_db": round(float(np.median(vv)), 5) if len(vv) else None,
        "median_vh_change_db": round(float(np.median(vh)), 5) if len(vh) else None,
        "flags": {
            str(threshold): int(((np.abs(vv) >= threshold) & (np.abs(vh) >= threshold)).sum())
            for threshold in THRESHOLDS
        },
    }


def optical_input():
    from optical import read_optical

    cache = ROOT / "optical_20190218_20190310.npz"
    if cache.exists():
        with np.load(cache, allow_pickle=False) as values:
            if tuple(values["shape"]) != SHAPE or not np.array_equal(values["transform"], tuple(GRID)):
                raise ValueError("Cached optical comparison grid mismatch")
            result = tuple(values[name] for name in ("prefire_nbr", "delta_nbr", "vegetation_mask"))
        if any(array.shape != SHAPE for array in result) or result[-1].dtype != np.bool_:
            raise ValueError("Cached optical comparison array mismatch")
        return result

    result = read_optical(SHAPE, GRID)
    np.savez_compressed(
        cache, prefire_nbr=result[0], delta_nbr=result[1], vegetation_mask=result[2],
        shape=SHAPE, transform=tuple(GRID),
    )
    return result


def input_fingerprints():
    paths = (ROOT / "optical_20190218_20190310.npz", *sorted(ROOT.glob("radar_*.npy")))
    return {path.name: digest(path) for path in paths}


def digest(path):
    with path.open("rb") as handle:
        return file_digest(handle, "sha256").hexdigest()


def offline_score():
    # Import at run time so the mathematical helpers can be tested in isolation.
    from reference import EXPECTED_SHA256, build_reference

    burn, analysed = build_reference(SHAPE, GRID)
    prefire_nbr, delta_nbr, optical_vegetation = optical_input()
    interior = neighbours(burn & analysed, BURN_INTERIOR_CELLS) == (2 * BURN_INTERIOR_CELLS + 1) ** 2
    stable = (
        analysed & optical_vegetation & np.isfinite(prefire_nbr)
        & (np.abs(delta_nbr) <= STABLE_NBR_MAX_CHANGE)
        & (neighbours(burn, CONTROL_BUFFER_CELLS) == 0)
    )

    # Select matched pairs before loading the target radar change.
    captures = [radar_capture(identity, with_angle=identity == REFERENCES[-1]) for identity in REFERENCES]
    vv_baseline, vh_baseline, valid = baseline(captures)
    angle = captures[-1][2]
    matching_data = valid & np.isfinite(prefire_nbr) & (angle <= 90)
    positives, negatives = matched_indices(
        interior & matching_data, stable & matching_data,
        vv_baseline, vh_baseline, angle, prefire_nbr,
    )
    vv_target, vh_target, _, acquisition = radar_capture(TARGET)
    vv_change = 10 * np.log10(vv_target / vv_baseline)
    vh_change = 10 * np.log10(vh_target / vh_baseline)
    paired_valid = np.isfinite(vv_change.ravel()[positives]) & np.isfinite(vh_change.ravel()[positives])
    paired_valid &= np.isfinite(vv_change.ravel()[negatives]) & np.isfinite(vh_change.ravel()[negatives])
    report = {
        "study_bounds_wgs84": BOUNDS,
        "grid_shape": SHAPE,
        "reference_product": "EMSR345 AOI01 Delineation Monitoring 1 v1",
        "reference_archive_sha256": EXPECTED_SHA256,
        "reference_acquisitions": [capture[3] for capture in captures],
        "radar_acquisition_metadata": [asset_url(*identity, "metadata.json") for identity in (*REFERENCES, TARGET)],
        "cached_input_sha256": input_fingerprints(),
        "target_acquisition": acquisition,
        "prefire_matching": {
            "rng_seed": SEED,
            "bins_vv_vh_db": 3,
            "bins_angle_deg": 5,
            "bins_optical_nbr": 0.15,
            "pairs_before_target_mask": int(len(positives)),
            "pair_unavailable": int((~paired_valid).sum()),
        },
        "mapped_burn_entire_window_cells": int(burn.sum()),
        "mapped_burn_analysed_cells": int((burn & analysed).sum()),
        "analysed_cells": int(analysed.sum()),
        "strict_burn_interior_cells": int(interior.sum()),
        "strict_burn_interior_with_prefire_optical_cells": int((interior & np.isfinite(prefire_nbr)).sum()),
        "matched_pool_burn": int((interior & matching_data).sum()),
        "matched_pool_control": int((stable & matching_data).sum()),
        "all_mapped_burn": summaries(vv_change, vh_change, np.flatnonzero(burn & analysed)),
        "strict_burn_interior": summaries(vv_change, vh_change, np.flatnonzero(interior)),
        "optically_stable_control_candidates": summaries(vv_change, vh_change, np.flatnonzero(stable)),
        "matched_burn": summaries(vv_change, vh_change, positives[paired_valid]),
        "matched_control": summaries(vv_change, vh_change, negatives[paired_valid]),
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "mount-kenya-report.json")
    args = parser.parse_args()
    report = offline_score()
    data = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    args.report.write_bytes(data)
    print(data.decode("utf-8"), end="")
    print(f"Report SHA-256 {sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
