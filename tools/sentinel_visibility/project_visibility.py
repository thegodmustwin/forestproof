"""Project a fixed Sentinel-2 research report onto fields safe for a read-only page."""

from datetime import date, datetime, timedelta


BOUNDS = [36.60, -0.49, 36.63, -0.46]
GRID_COUNTS = {"36MZE": 27_722, "37MBV": 27_724}


def project(report: dict, *, now: datetime) -> dict:
    if (not isinstance(report, dict)
            or report.get("schema") != "forestproof.sentinel2_visibility.v1"
            or report.get("area") != "Provisional Geta research rectangle"
            or report.get("bounds_wgs84") != BOUNDS
            or report.get("native_resolution_metres") != 20):
        raise ValueError("Expected a Sentinel-2 report for the fixed research rectangle")
    checked_at = report.get("checked_at")
    if not isinstance(checked_at, str):
        raise ValueError("Expected a report check timestamp")
    checked = datetime.fromisoformat(checked_at)
    if checked.utcoffset() != timedelta(0) or checked > now:
        raise ValueError("Expected a check timestamp in UTC at or before now")

    scenes = report.get("acquisitions")
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= 3:
        raise ValueError("Expected one to three acquisitions")
    acquisitions = {}
    for scene in scenes:
        if not isinstance(scene, dict) or not isinstance(scene.get("date"), str):
            raise ValueError("Expected a dated acquisition")
        day = date.fromisoformat(scene["date"])
        if day.isoformat() != scene["date"] or day > checked.date() or day in acquisitions:
            raise ValueError("Invalid or duplicate acquisition date")

        tiles = scene.get("tiles")
        if not isinstance(tiles, list) or len(tiles) != len(GRID_COUNTS):
            raise ValueError("Expected the two native grids")
        by_grid = {}
        for tile in tiles:
            if not isinstance(tile, dict) or not isinstance(tile.get("tile"), str):
                raise ValueError("Expected a native grid identifier")
            grid = tile["tile"]
            if grid not in GRID_COUNTS or grid in by_grid:
                raise ValueError("Invalid or duplicate native grid identifier")
            sampled = tile.get("sampled_centres")
            visible = tile.get("surface_classified_visible")
            vegetation = tile.get("vegetation_classified_visible")
            counts = tile.get("scl_counts_0_to_11")
            if (not isinstance(counts, list) or len(counts) != 12
                    or any(type(count) is not int or count < 0 for count in counts)
                    or any(type(count) is not int for count in (sampled, visible, vegetation))
                    or sampled != GRID_COUNTS[grid] or sampled != sum(counts)
                    or visible != sum(counts[4:7]) or vegetation != counts[4]):
                raise ValueError("Native grid counts did not reconcile")
            by_grid[grid] = {"grid": f"T{grid}", "sampled": sampled, "visible": visible, "vegetation": vegetation}
        acquisitions[day] = {"date": day, "tiles": [by_grid[grid] for grid in GRID_COUNTS]}

    return {"checked": checked, "acquisitions": [acquisitions[day] for day in sorted(acquisitions, reverse=True)]}
