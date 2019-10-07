


from .ViewPortRGB import ViewPortRGB
from .ViewPortRenderer import ViewPortRenderer





class ViewPortCell(object):

	def __init__(self, c:str = None, colBG:ViewPortRGB = None, colFG:ViewPortRGB = None):
		self.c = c
		self.colBG = None if colBG is None else int(colBG)
		self.colFG = None if colFG is None else int(colFG)
		self._brightness = ViewPortRenderer.MAX_BRIGHTNESS
	#

	def set(self, c:str, colBG:ViewPortRGB, colFG:ViewPortRGB):
		if c is not None:
			self.c = c
		if colBG is not None:
			self.colBG = int(colBG)
		if colFG is not None:
			self.colFG = int(colFG)
	#

#




