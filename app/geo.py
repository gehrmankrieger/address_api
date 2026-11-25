""" Distance Calculations/Math ONLY. """

from math import asin, cos, degrees, radians, sin, sqrt
from typing import NamedTuple


# Mean Earth radius
EARTH_RADIUS_KM = 6371.0088


class BoundBox(NamedTuple):
    """ Box around the search area, skip if outside said box. """
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """ Circle distance in kilometers between 2 points. """
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)
    a = sin(d_phi/2)**2 + cos(phi1) * cos(phi2) * sin(d_lambda/2)**2

    return 2 * EARTH_RADIUS_KM * asin(sqrt(min(1.0, a)))

def bounding_box(lat: float, lon: float, distance_km: float) -> BoundBox:
    """ Latitude/Longitude rectangle outside search circle as cheap SQL pre-filter. """

    # Distance as angle
    angle = distance_km / EARTH_RADIUS_KM

    lat_rad = radians(lat)
    min_lat = degrees(lat_rad - angle)
    max_lat = degrees(lat_rad + angle)

    # Box reaching Pole
    if min_lat <= -90 or max_lat >= 90:
        return BoundBox(max(min_lat, -90.0), min(max_lat, 90.0), -180.0, 180.0)

    lon_delta = degrees(asin(sin(angle) / cos(lat_rad)))
    min_lon, max_lon = lon - lon_delta, lon + lon_delta

    # Box over 180 degree Meridian
    if min_lon < -180 or max_lon > 180:
        return BoundBox(min_lat, max_lat, -180.0, 180.0)

    return BoundBox(min_lat, max_lat, min_lon, max_lon)