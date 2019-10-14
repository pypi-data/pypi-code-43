# -*- coding: utf-8 -*-
from __future__ import (print_function, unicode_literals)
'''
Created on 22 aug 2018

@author: Jarrige_Pi

 18.08.22 (0.9.0) - creation
 18.11.07 (0.9.1) - added target and shapeType Write keyword
                    added close Write method (shapefile 2.0)

'''

import os.path as OP
from sys import version_info
import json
from numbers import Number
from collections import OrderedDict

PY3 = version_info.major == 3
if PY3:
    izip = zip
    import builtins
    unicode23 = builtins.str
    byte23 = builtins.bytes
    file_encoding = 'utf-8'
    copen = builtins.open
else:
    from itertools import izip
    import __builtin__
    unicode23 = __builtin__.unicode
    byte23 = __builtin__.str
    file_encoding = 'cp1252'
    from codecs import open as copen

from ganessa.util import ws, strf3

__version__ = '0.9.1'

POINT = 1
POLYLINE = 3
POLYGON = 5

# Class wrapper for write functions to geojson
class Writer(object):
    def __init__(self, shapeType=POLYLINE, target=None):
        self.gtype = shapeType
        self.nfields = []
        self.sfields = []
        self.gobjects = []
        self.records = []
        self.proj = 'wgs84'
        self.target = target

    def point(self, x, y):
        self.gobjects.append((POINT, (x, y)))

    def line(self, parts=None, shapeType=POLYLINE):
        self.gobjects.append((shapeType, [] if parts is None else parts))

    def poly(self, parts=None, shapeType=POLYGON):
        self.gobjects.append((shapeType, [] if parts is None else parts))

    def field(self, name, vtype='N', size=None):
        self.nfields.append(name)
        self.sfields.append(size if vtype.upper() == 'C' else 0)

    def record(self, *args):
        self.records.append(args)

    def projection(self, proj):
        self.proj = proj

    def save(self, target=None):
        fname = self.target if target is None else target
        fname = OP.splitext(fname)[0]
        if self.proj == 'wgs84':
            convert = lambda x: x
        else:
            import pyproj
            wgs84 = pyproj.Proj(ws("+init=EPSG:4326"))      # doit etre explicitement definie
            dicproj = dict(wgs84="+init=EPSG:4326",       # geoCRS 2D
                       lamb93="+init=EPSG:2154",       # RGF93 / Lambert93 (projCRS) 
                       rgf93="+init=EPSG:4171",       # RGF93 2D 
                       lambN="+init=EPSG:27561", 
                       lambC="+init=EPSG:27562",
                       lambS="+init=EPSG:27563",
                       ntf="+init=EPSG:4275", ntfparis= "+init=EPSG:4807",
                       lamb1="+init=EPSG:27571",
                       lamb2="+init=EPSG:27572",
                       lamb3="+init=EPSG:27573",
                       utm20n="+init=EPSG:4559",    # Martinique - Guadeloupe
                       utm40s="+init=EPSG:2975",    # Réunion
                       utm22n="+init=EPSG:2972",    # Guyanne
                       # 'macau': b'+ellps=intl +proj=tmerc +lat_0=22.212222 +lon_0=113.536389 +k=1.000000 +x_0=20000.0 +y_0=20000.0 +units=m'
                       macau='+ellps=intl +proj=tmerc +lat_0=22.212222 +lon_0=113.536389 +k=1.000000 +x_0=19685.0 +y_0=20115.0 +units=m'
                       )
            for lat in range(42, 51):
                dicproj['cc'+str(lat)] = "+init=EPSG:{:4d}".format(3900+lat)
                dicproj['rgf93-cc'+str(lat)] = "+init=EPSG:{:4d}".format(3900+lat)

            try:
                prj = dicproj[self.proj]
            except KeyError:
                prj = self.proj
                if prj.upper().startswith('EPSG:'):
                    prj = '+init=' + prj.upper()
            fmprj = pyproj.Proj(ws(prj))
            def convert(pt):
                return pyproj.transform(fmprj, wgs84, *pt)

        items = []
        for (gtype, gdata), data in izip(self.gobjects, self.records):
            if gtype == POINT:
                stype = 'Point'
                wdata = convert(gdata)
            else:
                if len(gdata) == 1:
                    stype = 'LineString'
                    wdata = [convert(x) for x in gdata[0]]
                else:
                    stype = 'MultiLineString'
                    wdata = [[convert(x) for x in part] for part in gdata]
            geom = dict(type=stype,
                        coordinates=wdata)
            pdata = [float(strf3(x)) if isinstance(x, Number) else x for x in data]
            props = dict(izip(self.nfields, pdata))
            items.append(dict(type='Feature',
                              geometry=geom,
                              properties=props))
        encode = {} if PY3 else dict(encoding='utf-8')
        with copen(fname + '.geojson', 'w' , encoding='utf-8') as f:
            item_to_dump = dict(type='FeatureCollection', features=items)
            json.dump(item_to_dump, f, indent=2, **encode)

    close = save

class _Shape(object):
    def __init__(self, typ):
        self.shapeType = typ
        self.points = []

class _ShapeRecord:
    """A shape object of any type."""
    def __init__(self, shape=None, record=None):
        self.shape = shape
        self.record = record

# Class wrapper for read functions from geojson
class Reader(object):
    def __init__(self, fname, encoding=None):
        # fields to keep order, set for efficiency
        self.fields = []
        self.fieldset = set()
        self.data = []
        self.name = OP.splitext(fname)[0]
        self.count = 0
        for ext in ('.json', '.geojson'):
            if  OP.exists(self.name  + ext):
                self.name += ext
                break
        else:
            return
        # Lecture du fichier
        with copen(self.name, 'r' , encoding='utf-8') as f:
            item_to_filter = json.load(f)
        if item_to_filter['type'] != 'FeatureCollection':
            return
        for item in item_to_filter['features']:
            if item['type'] != 'Feature':
                continue
            geom = item['geometry']
            props = item.get('properties', {})
            gtype = geom['type']
            gdata = geom['coordinates']
            if gtype == 'Point':
                self.data.append((POINT, tuple(gdata), props))
            elif gtype == 'LineString':
                self.data.append((POLYLINE,
                                  [[tuple(pt) for pt in gdata]], props))
            else:
                continue
            # update fields list
            for p in props.keys():
                if p not in self.fieldset:
                    self.fields.append(p)
                    self.fieldset.add(p)
        return

    def shape(self, pos= 0):
        return self.data[pos][0:2]

    def iterShapes(self):
        for obj in self.data:
            yield obj[0:2]

    def _allfields(self, rec):
        '''Explode object props according to the field order'''
        return [rec.get(field, '') for field in self.fields]

    def record(self, pos= 0):
        return self._allfields(self.data[pos][2])

    def iterRecords(self):
        for obj in self.data:
            yield self._allfields(obj[2])

    def shapeRecord(self, pos= 0):
        rec = self.data[pos]
        return _ShapeRecord(rec[0:2], rec[2])

    def iterShapeRecords(self):
        for obj in self.data:
            yield _ShapeRecord(obj[0:2], obj[2])

    def __len__(self):
        return len(self.data)

# for symmetry with shapefile
class ShapefileException(Exception):
    pass       
            
if __name__ == "__main__":
    sig = Reader('D:/Temp/tmp-N.geojson')
    print('Read count:', len(sig))
    print('Fields:', sig.fields)
    for item in sig.iterShapes():
        pass
    for item in sig.iterRecords():
        pass
    print('Termine')
