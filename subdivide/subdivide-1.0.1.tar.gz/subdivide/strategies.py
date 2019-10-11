import numpy as N
from shapely.geometry import shape, LineString
from .util import pairs

def preserve_endpoints(geom, interval):
	"""
	Preserves endpoint(s) but not intermediate vertices. This will result in a 
	line with a changed length.
	"""
	n = int(round(geom.length/interval))
	rng = N.linspace(0,geom.length,n)
	for i in rng:
		yield geom.interpolate(i)	

def preserve_shape(geom, interval):
	yield geom.interpolate(0)
	for seg in pairs(geom.coords):
		n = int(round(seg.length/interval))
		rng = N.linspace(0,seg.length,n)[1::] #cut off first point
		for i in rng:
			yield seg.interpolate(i)

def exact_interval(geom, interval):
	"""
	Pins to exact interval and shortens geometry by some amount less
	than the specified interval. If feature is a ring, the last point
	will be preserved (this will create one segment that is not of the
	specified length)
	"""
	rng = list(N.arange(0,geom.length, interval))
	if geom.is_ring:
		rng.append(geom.length)
	for i in rng:
		yield geom.interpolate(i)

