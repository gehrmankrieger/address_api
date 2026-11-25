"""Unit tests for the distance helpers."""

import pytest

from app.geo import bounding_box, haversine_km


def test_haversine_same_point_is_zero() -> None:
    assert haversine_km(14.5995, 120.9842, 14.5995, 120.9842) == 0


def test_haversine_paris_to_london() -> None:
    # Known great-circle distance is about 343.5 km.
    assert haversine_km(48.8566, 2.3522, 51.5074, -0.1278) == pytest.approx(343.5, abs=1.0)


def test_bounding_box_contains_center() -> None:
    lat, lon = 14.5995, 120.9842
    box = bounding_box(lat, lon, 50)
    assert box.min_lat < lat < box.max_lat
    assert box.min_lon < lon < box.max_lon
    # The north edge is ~50 km from the centre.
    assert haversine_km(lat, lon, box.max_lat, lon) == pytest.approx(50, rel=1e-3)


def test_bounding_box_near_pole_uses_full_longitude() -> None:
    box = bounding_box(89.9, 0, 100)
    assert box.max_lat == 90.0
    assert (box.min_lon, box.max_lon) == (-180.0, 180.0)


def test_bounding_box_across_antimeridian_uses_full_longitude() -> None:
    box = bounding_box(0, 179.9, 100)
    assert (box.min_lon, box.max_lon) == (-180.0, 180.0)