from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    mode: str
    database_path: Path
    evidence_directory: Path
    web_origin: str


def get_settings() -> Settings:
    """Read only non-secret configuration used by the local development slice."""
    parents = Path(__file__).resolve().parents
    # Container paths can be shallower than the repository checkout.
    root = parents[3] if len(parents) > 3 else parents[1]
    return Settings(
        mode=os.getenv("FORESTPROOF_MODE", "demo").lower(),
        database_path=Path(os.getenv("FORESTPROOF_SQLITE_PATH", root / "data" / "local" / "forestproof.db")),
        evidence_directory=Path(os.getenv("EVIDENCE_STORAGE_PATH", root / "data" / "local" / "evidence")),
        web_origin=os.getenv("WEB_ORIGIN", "http://localhost:3000"),
    )
