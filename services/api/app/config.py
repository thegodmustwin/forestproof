from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    mode: str
    database_path: Path
    evidence_directory: Path
    web_origin: str
    internal_api_token: str | None = field(default=None, repr=False)
    copernicus_catalog_enabled: bool = False


def get_settings() -> Settings:
    """Read runtime configuration; internal service tokens must not be logged."""
    parents = Path(__file__).resolve().parents
    # Container paths can be shallower than the repository checkout.
    root = parents[3] if len(parents) > 3 else parents[1]
    return Settings(
        mode=os.getenv("FORESTPROOF_MODE", "demo").lower(),
        database_path=Path(os.getenv("FORESTPROOF_SQLITE_PATH", root / "data" / "local" / "forestproof.db")),
        evidence_directory=Path(os.getenv("EVIDENCE_STORAGE_PATH", root / "data" / "local" / "evidence")),
        web_origin=os.getenv("WEB_ORIGIN", "http://localhost:3000"),
        internal_api_token=os.getenv("FORESTPROOF_INTERNAL_API_TOKEN"),
        copernicus_catalog_enabled=os.getenv("FORESTPROOF_COPERNICUS_CATALOG_ENABLED", "false").lower() == "true",
    )
