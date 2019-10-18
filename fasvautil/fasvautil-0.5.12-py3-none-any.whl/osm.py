import numpy as np
import utm

from fasvautil.location import UTMLocation, GPSLocation, to_latlon


def extend_from_utm(easting, northing, utm_zone, padding=25):
    """
    Get the plotting extend from the utm coordinates

    Args:
        easting (list[float]):        UTM easting coordinates
        northing (list[float]):       UTM northing coordinates
        utm_zone ((int, str)):  The UTM zone
        padding (int):          Padding around the UTM location

    Returns:

    """
    east = [int(np.min(easting)) - padding, int(np.max(easting)) + padding]
    north = [int(np.min(northing)) - padding, int(np.max(northing)) + padding]

    width = east[1] - east[0]
    height = north[1] - north[0]

    diff = height - width

    if diff > 0:
        east[0] -= abs(diff / 2)
        east[1] += abs(diff / 2)
    else:
        north[0] -= abs(diff / 2)
        north[1] += abs(diff / 2)

    lat_min, lon_min = utm.to_latlon(east[0], north[0], *utm_zone)

    lat_max, lon_max = utm.to_latlon(east[1], north[1], *utm_zone)

    return [lat_min, lat_max], [lon_min, lon_max]


def project_utm_positions(utm_positions, utm_zone):
    """
    Project the UTM positions onto a tilemap.

    Args:
        utm_positions (np.ndarray): A N*2 array of float values each of which represent a UTM location
        utm_zone (tuple[int, str]):     The UTM zone number and letter

    Returns:

    """
    if isinstance(utm_zone[0], str):
        # wrong order
        utm_zone = (utm_zone[1], utm_zone[0])

    lat, lon = to_latlon(easting=utm_positions[:, 0], northing=utm_positions[:, 1], zone_number=utm_zone[0],
                         zone_letter=utm_zone[1])

    return project(latitude=lat, longitude=lon)


def project_location(location, offset=None):
    """
    Project the given location into "Web Mercator" for OSM visualization

    Args:
        location (UTMLocation|GPSLocation|list[UTMLocation|GPSLocation]):     the location to project.
        offset (np.ndarray):                                                  Offset to the position in meter.

    Returns:
         tuple[float, float]: Coordinates `(x,y)` in the "Web Mercator" projection, normalised to be in the range [0,1].
    """

    if offset is not None:
        # add the offset to the position
        if isinstance(location, GPSLocation):
            location = location.as_utm()

        # we assume that the offset is in meter
        location.position += offset

        # convert the result to GPS
        location = location.as_gps()

    if isinstance(location, UTMLocation):
        location = location.as_gps()

    return project(location.longitude, location.latitude)


def project(longitude, latitude):
    """
    Project the longitude / latitude coords to "Web Mercator" within [0, 1] using numpy.

    Args:
        longitude (np.array): In degrees, between -180 and 180
        latitude (np.array): In degrees, between -85 and 85

    Returns:
        tuple[float, float]: Coordinates `(x,y)` in the "Web Mercator" projection, normalised to be in the range [0,1].
    """
    xtile = (longitude + 180.0) / 360.0
    lat_rad = np.radians(latitude)
    ytile = (1.0 - np.log(np.tan(lat_rad) + (1 / np.cos(lat_rad))) / np.pi) / 2.0
    return xtile, ytile