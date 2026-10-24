from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import Geometry


def test_geometry_accepts_wgs84_point_and_closed_polygon():
    assert Geometry(type="Point", coordinates=[36.7654, -0.3876]).coordinates == [36.7654, -0.3876]
    polygon = [[36.7, -0.4], [36.8, -0.4], [36.8, -0.3], [36.7, -0.4]]
    assert Geometry(type="Polygon", coordinates=[polygon]).type == "Polygon"


@pytest.mark.parametrize("geometry_type,coordinates", [
    ("Point", [181, 0]),
    ("Point", [36]),
    ("Polygon", [[[36.7, -0.4], [36.8, -0.4], [36.8, -0.3]]]),
])
def test_geometry_rejects_invalid_wgs84_shapes(geometry_type, coordinates):
    with pytest.raises(ValidationError):
        Geometry(type=geometry_type, coordinates=coordinates)
