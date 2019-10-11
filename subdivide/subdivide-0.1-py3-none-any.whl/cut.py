import numpy as N
from shapely.geometry import shape, mapping, Point, LineString
import logging as log

def cut(records, interval=100, preserve_attributes=False):
	"""
	Cuts a line into equal-length components given a characteristic length scale.
	"""
	def segment(line, start, end):
		yield line.interpolate(start)
		for c in geom.coords:
			distance = line.project(Point(c))
			if start < distance < end:
				yield Point(c)
		yield line.interpolate(end)

	for rec in records:
		try:
			assert rec['geometry']['type'] == "LineString"
			geom = shape(rec["geometry"])
			n = int(round(geom.length/interval))
			rng = N.linspace(0,geom.length,n)
			pairs = zip(rng[:-1],rng[1:])
			for distances in pairs:
				coords = [(p.x, p.y) for p in segment(geom,*distances)]
				out = {
					"type": "Feature",
					"geometry": {
						"type": "LineString",
						"coordinates": coords
					},
					"properties": {}
				}
				if preserve_attributes:
					for i in ["properties", "id"]:
						if rec[i]:
							out[i] = rec[i]
				yield out

		except Exception as e:
			# Writing untransformed features to a different shapefile
			# is another option.
			log.exception("Error transforming record")
