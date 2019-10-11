from shapely.geometry import LineString

def pairs(list):
	for i in range(1, len(list)):
		yield LineString((list[i-1], list[i]))