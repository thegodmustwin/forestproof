from __future__ import annotations

from datetime import datetime
from math import isfinite
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator


CaseStatus = Literal[
    "NEW", "UNDER_REVIEW", "FIELD_VERIFICATION", "ACTION_RECORDED", "FOLLOW_UP", "CLOSED", "REOPENED"
]


class Geometry(BaseModel):
    type: Literal["Point", "Polygon", "MultiPolygon"]
    coordinates: Any

    @field_validator("coordinates")
    @classmethod
    def coordinate_shape_is_plausible(cls, value: Any, info: ValidationInfo) -> Any:
        geometry_type = info.data.get("type")
        if value in (None, [], {}):
            raise ValueError("A non-empty GeoJSON coordinate value is required")

        def valid_point(point: Any) -> bool:
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                return False
            longitude, latitude = point[0], point[1]
            if isinstance(longitude, bool) or isinstance(latitude, bool):
                return False
            if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
                return False
            return isfinite(longitude) and isfinite(latitude) and -180 <= longitude <= 180 and -90 <= latitude <= 90

        def valid_ring(ring: Any) -> bool:
            return (
                isinstance(ring, list)
                and len(ring) >= 4
                and all(valid_point(point) for point in ring)
                and ring[0][:2] == ring[-1][:2]
            )

        if geometry_type == "Point" and not valid_point(value):
            raise ValueError("Point coordinates must be a finite [longitude, latitude] pair within WGS84 bounds")
        if geometry_type == "Polygon" and not (
            isinstance(value, list) and value and all(valid_ring(ring) for ring in value)
        ):
            raise ValueError("Polygon coordinates must contain closed WGS84 linear rings")
        if geometry_type == "MultiPolygon" and not (
            isinstance(value, list)
            and value
            and all(isinstance(polygon, list) and polygon and all(valid_ring(ring) for ring in polygon) for polygon in value)
        ):
            raise ValueError("MultiPolygon coordinates must contain closed WGS84 polygon rings")
        return value


class CaseCreate(BaseModel):
    observation_id: str
    title: str = Field(min_length=4, max_length=160)
    owner_organization: str = Field(min_length=2, max_length=120)
    reviewer: str | None = Field(default=None, max_length=120)


class StatusTransition(BaseModel):
    to_status: CaseStatus
    actor: str = Field(min_length=2, max_length=120)
    note: str = Field(min_length=2, max_length=2000)


class AssignmentCreate(BaseModel):
    assignee: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=80)
    actor: str = Field(min_length=2, max_length=120)


class ActionCreate(BaseModel):
    action_type: str = Field(min_length=2, max_length=100)
    summary: str = Field(min_length=2, max_length=2000)
    actor: str = Field(min_length=2, max_length=120)
    occurred_at: datetime | None = None


class FollowUpCreate(BaseModel):
    assessment: Literal["VERIFIED_INCIDENT", "FALSE_POSITIVE", "INSUFFICIENT_EVIDENCE", "UNRESOLVED"]
    summary: str = Field(min_length=2, max_length=2000)
    actor: str = Field(min_length=2, max_length=120)
    observed_at: datetime | None = None


class EvidenceCreate(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    media_type: str = Field(default="application/octet-stream", max_length=120)
    content_base64: str = Field(min_length=1)
    source_description: str = Field(min_length=2, max_length=1000)
    actor: str = Field(min_length=2, max_length=120)
    observed_at: datetime | None = None
