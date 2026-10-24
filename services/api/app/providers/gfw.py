from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GfwProviderStatus:
    provider: str = "Global Forest Watch Data API"
    operational_status: str = "AVAILABLE_WITH_CREDENTIALS"
    configured: bool = False
    tile_template: str = "https://tiles.globalforestwatch.org/umd_glad_sentinel2_alerts/latest/dynamic/{z}/{x}/{y}.png"
    notice: str = (
        "The public raster tile layer is documented as geographic context. Individual observations are disabled "
        "until an approved API credential, source terms, area of interest, and retention policy are configured."
    )


def status() -> GfwProviderStatus:
    # Never reveal a secret or treat its mere presence as source verification.
    return GfwProviderStatus(configured=bool(os.getenv("GFW_API_KEY")))
