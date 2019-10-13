import numpy as np

from fasvautil.location import UTMLocation, GPSLocation


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