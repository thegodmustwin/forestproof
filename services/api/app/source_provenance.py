"""Versioned source-neutral provenance contract for observation responses.

This contract does not implement LIVE ingestion or authentication. The currently
exposed projection accepts only known synthetic demo fixtures. Future LIVE
adapters must separately enforce authorization, source terms and storage.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .demo_data import DEMO_ORGANIZATION_ID


class SourceProvenance(BaseModel):
    """Describe origin and timing without interpreting the source's signal."""

    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["1"] = "1"
    data_mode: Literal["DEMO", "LIVE"]
    source_id: str = Field(min_length=1, max_length=128)
    product: str = Field(min_length=1, max_length=128)
    source_release: str | None = Field(default=None, min_length=1, max_length=128)
    processing_version: str = Field(min_length=1, max_length=128)
    record_key: str = Field(min_length=1, max_length=256)
    record_key_kind: Literal["SYNTHETIC_FIXTURE", "PROVIDER_NATIVE", "DERIVED_CELL"]
    observed_at: datetime | None = None
    observed_on: date | None = None
    published_at: datetime | None = None
    received_at: datetime
    quality_flags: list[str] = Field(max_length=50)
    completeness: Literal["UNKNOWN"] = "UNKNOWN"
    attribution: str | None = Field(default=None, max_length=500)

    @field_validator("source_id", "product", "processing_version", "record_key", "source_release")
    @classmethod
    def text_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Provenance identifiers cannot be blank")
        return value

    @field_validator("observed_at", "published_at", "received_at")
    @classmethod
    def time_must_have_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Provenance timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def ensure_distinct_source_semantics(self) -> "SourceProvenance":
        if (self.observed_at is None) == (self.observed_on is None):
            raise ValueError("Use exactly one observation timestamp or calendar date")
        if self.data_mode == "DEMO":
            if self.record_key_kind != "SYNTHETIC_FIXTURE" or "DEMO_DATA" not in self.quality_flags:
                raise ValueError("Demo provenance requires a synthetic fixture identity and label")
        else:
            if (self.record_key_kind == "SYNTHETIC_FIXTURE"
                    or self.source_id == "demo-synthetic-v1"
                    or any(flag.strip().upper() == "DEMO_DATA" for flag in self.quality_flags)):
                raise ValueError("Live provenance cannot contain a demo identity or label")
            if self.source_release is None or self.source_release.strip().lower() == "latest":
                raise ValueError("Live provenance requires a concrete source release")
        return self


def demo_source_provenance(observation: dict) -> dict:
    """Project existing fixture data; never relabel an arbitrary record as demo."""
    flags = observation.get("quality_flags")
    if (
        observation.get("organization_id") != DEMO_ORGANIZATION_ID
        or observation.get("source_id") != "demo-synthetic-v1"
        or not isinstance(observation.get("source_record_id"), str)
        or not observation["source_record_id"].startswith("DEMO-")
        or not isinstance(flags, list)
        or "DEMO_DATA" not in flags
        or "NOT_A_LIVE_DETECTION" not in flags
    ):
        raise ValueError("Only explicitly identified synthetic demo fixtures are supported")

    record = SourceProvenance(
        data_mode="DEMO",
        source_id=observation["source_id"],
        product=observation["source_product"],
        # The fixture's processing version is not a verified upstream release.
        source_release=None,
        processing_version=observation["processing_version"],
        record_key=observation["source_record_id"],
        record_key_kind="SYNTHETIC_FIXTURE",
        observed_at=observation["observed_at"],
        published_at=observation.get("published_at"),
        received_at=observation["ingested_at"],
        quality_flags=flags,
        attribution=None,
    )
    return record.model_dump(mode="json")
