

import re





class ViewPortRGB(object):

	def __init__(self, ri, gi, bi):
		self.ri = ri
		self.gi = gi
		self.bi = bi
	#

	def __int__(self):
		return self.ri * 256 + self.gi * 16 + self.bi
	#

	def __str__(self):
		return "#%02x%02x%02x" % (self.ri * 16, self.gi * 16, self.bi * 16)
	#

	_HEXVALS = "0123456789abcdef"
	_P1 = re.compile(r"^#([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])$")
	_P2 = re.compile(r"^#([0-9a-f])([0-9a-f])([0-9a-f])$")
	_P3 = re.compile(r"^rgb\(\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*\)$")

	#
	# Parse CSS codes as used by web technologies
	#
	@staticmethod
	def parseCSS(css:str):
		css = css.lower()
		m = ViewPortRGB._P1.match(css)
		if m:
			sr = m.group(1)
			sg = m.group(2)
			sb = m.group(3)
			r = (ViewPortRGB._HEXVALS.index(sr[0]) << 4) + ViewPortRGB._HEXVALS.index(sr[1])
			g = (ViewPortRGB._HEXVALS.index(sg[0]) << 4) + ViewPortRGB._HEXVALS.index(sg[1])
			b = (ViewPortRGB._HEXVALS.index(sb[0]) << 4) + ViewPortRGB._HEXVALS.index(sb[1])
			return ViewPortRGB(r >> 4, g >> 4, b >> 4)
		m = ViewPortRGB._P2.match(css)
		if m:
			sr = m.group(1)
			sg = m.group(2)
			sb = m.group(3)
			r = ViewPortRGB._HEXVALS.index(sr)
			g = ViewPortRGB._HEXVALS.index(sg)
			b = ViewPortRGB._HEXVALS.index(sb)
			return ViewPortRGB(r, g, b)
		m = ViewPortRGB._P3.match(css)
		if m:
			sr = m.group(1)
			sg = m.group(2)
			sb = m.group(3)
			r = int(sr)
			if r > 255:
				raise Exception("Invalid red component in: " + repr(css))
			g = int(sg)
			if g > 255:
				raise Exception("Invalid green component in: " + repr(css))
			b = int(sb)
			if b > 255:
				raise Exception("Invalid blue component in: " + repr(css))
			return ViewPortRGB(r >> 4, g >> 4, b >> 4)
		raise Exception("Not a CSS color string: " + repr(css))
	#

	@staticmethod
	def rgb256(r:int, g:int, b:int):
		if (r < 0) or (r > 255):
			raise Exception("Red value must be a valid integer value! (Value specified: " + str(r) + ")")
		if (g < 0) or (g > 255):
			raise Exception("Red value must be a valid integer value! (Value specified: " + str(g) + ")")
		if (b < 0) or (b > 255):
			raise Exception("Red value must be a valid integer value! (Value specified: " + str(b) + ")")
		return ViewPortRGB(r >> 4, g >> 4, b >> 4)
	#

	@staticmethod
	def rgb1(r:float, g:float, b:float):
		if not isinstance(g, (int, float)) or (r < 0) or (r > 1):
			raise Exception("Red value must be a valid float value in the range [0..1]! (Value specified: " + str(r) + ")")
		if not isinstance(g, (int, float)) or (g < 0) or (g > 1):
			raise Exception("Green value must be a valid float value in the range [0..1]! (Value specified: " + str(g) + ")")
		if not isinstance(g, (int, float)) or (b < 0) or (b > 1):
			raise Exception("Blue value must be a valid float value in the range [0..1]! (Value specified: " + str(b) + ")")
		return ViewPortRGB(int(r * 15.9999), int(g * 15.9999), int(b * 15.9999))
	#

#



