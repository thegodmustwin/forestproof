from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class ProviderHealth:
    provider: str
    status: str
    checked_at: datetime
    detail: str


class ForestAlertProvider(Protocol):
    """Contract for source adapters; never discard the source's original record ID."""

    def discover(self, area: dict[str, Any], time_range: tuple[datetime, datetime]) -> list[dict[str, Any]]: ...

    def fetch(self, cursor: str) -> dict[str, Any]: ...

    def normalize(self, record: dict[str, Any]) -> dict[str, Any]: ...

    def provenance(self, record: dict[str, Any]) -> dict[str, Any]: ...
