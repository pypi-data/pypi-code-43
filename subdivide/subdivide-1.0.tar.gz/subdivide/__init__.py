"""
Fiona- and geojson-compatible module for interpolating coordinates along lines
"""
from shapely.geometry import shape, mapping, MultiLineString
import logging as log
from .strategies import preserve_shape
from .cut import cut

def __subdivide(geometry, interval=1, strategy=preserve_shape):
    coords = [(p.x, p.y) for p in strategy(geometry,interval)]
    try:
        geometry.coords = coords
    except ValueError:
        log.info("Could not subdivide: coordinates likely too closely spaced")

    return geometry

def subdivide(geometry, **kwargs):
    """
    Subdivides line at a given interval
    """
    geometry = shape(geometry)
    if hasattr(geometry,'geoms'):
        return MultiLineString([__subdivide(g, **kwargs) for g in geometry.geoms])
    return __subdivide(geometry, **kwargs)

def subdivide_all(records, interval=1, strategy=preserve_shape):
    """
    Subdivides line at a given interval
    """
    for rec in records:
        try:
            assert rec['geometry']['type'] == "LineString"
            geom = shape(rec["geometry"])
            coords = [(p.x, p.y) for p in strategy(geom,interval)]
            rec["geometry"]["coordinates"] = coords

        except Exception as e:
            # Writing untransformed features to a different shapefile
            # is another option.
            log.exception("Error transforming record")
        yield rec
