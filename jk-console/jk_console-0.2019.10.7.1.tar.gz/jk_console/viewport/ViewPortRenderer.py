


from ..Console import Console




class _RendererImpl(object):

	MAX_BRIGHTNESS = 20

	def __init__(self):
		self.bgTables = []
		self.fgTables = []
		for i in range(0, 101, 5):
			f = i / 100
			self.bgTables.append(_RendererImpl.__createRGBTableBG(f))
			self.fgTables.append(_RendererImpl.__createRGBTableFG(f))
	#

	@staticmethod
	def __createRGBTableBG(brightness:float):
		assert 0 <= brightness <= 1

		f = brightness * 16
		ret = [ 0 ] * (16 * 16 * 16)
		for r in range(0, 16):
			for g in range(0, 16):
				for b in range(0, 16):
					index = r * 256 + g * 16 + b
					ret[index] = "\033[48;2;" + str(int(r * f)) + ";" + str(int(g * f)) + ";" + str(int(b * f)) + "m"
		return ret
	#

	@staticmethod
	def __createRGBTableFG(brightness:float):
		assert 0 <= brightness <= 1

		f = brightness * 16
		ret = [ 0 ] * (16 * 16 * 16)
		for r in range(0, 16):
			for g in range(0, 16):
				for b in range(0, 16):
					index = r * 256 + g * 16 + b
					ret[index] = "\033[38;2;" + str(int(r * f)) + ";" + str(int(g * f)) + ";" + str(int(b * f)) + "m"
		return ret
	#

	"""
	def toConsoleStr(self, c:str, bgIndex:int, fgIndex:int, brightness:int):
		ret = []
		if bgIndex is not None:
			ret.append(self.bgTables[brightness][bgIndex])
		if fgIndex is not None:
			ret.append(self.bgTables[brightness][bgIndex])
		if c is not None:
			ret.append(c)
		return self.bgTables[brightness][bgIndex] + self.fgTables[brightness][fgIndex] + c
	#
	"""

#

ViewPortRenderer = _RendererImpl()








