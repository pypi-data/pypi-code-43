



from .Console import *
from .Rect import *






class FramedBoxSettings(object):

	def __init__(self):
		self.bgColor = Console.BackGround.STD_BLACK
		self.bgChar = " "
		self.frameColor = Console.BackGround.STD_BLACK + Console.ForeGround.STD_LIGHTGRAY
		self.frameCharLeft = "|"
		self.frameCharRight = "|"
		self.frameCharTop = "-"
		self.frameCharBottom = "-"
		self.frameCharTopLeft = "/"
		self.frameCharTopRight = "\\"
		self.frameCharBottomLeft = "\\"
		self.frameCharBottomRight = "/"
		self.textColor = Console.BackGround.STD_BLACK + Console.ForeGround.STD_LIGHTGRAY
	#

#




class ConsoleBuffer_Mixins:

	def _Mixins_init(self):
		self.defaultFramedBoxSettings = FramedBoxSettings()
	#

	#
	# Fill the entire buffer with the default background color.
	#
	def clear(self):
		bgColor = self._bgColor
		for y in self._lineNumbers:
			for x in self._columnNumbers:
				self._data[y][x].clear(bgColor)
		self._bFullPaint = True
	#

	#
	# Fill the entire buffer with the specified color and character.
	#
	def fill(self, color:str, character:str):
		if character != None:
			assert len(character) == 1

		for y in self._lineNumbers:
			for x in self._columnNumbers:
				cell = self._data[y][x]
				if character != None:
					cell.c = character
				if color != None:
					cell.col = color
		self._bFullPaint = True
	#

	#
	# Fill a single cell with color and character.
	#
	def set(self, x:int, y:int, color:str, character:str):
		cell = self._data[y][x]
		if character != None:
			assert len(character) == 1
			cell.c = character
			cell.bChanged = True
		if color != None:
			cell.col = color
			cell.bChanged = True
	#

	#
	# Fill a single cell with color and character.
	#
	def setSafe(self, x:int, y:int, color:str, character:str):
		if (x < 0) or (y < 0) or (x >= self._width) or (y >= self._height):
			return
		cell = self._data[y][x]
		if character != None:
			assert len(character) == 1
			cell.c = character
			cell.bChanged = True
		if color != None:
			cell.col = color
			cell.bChanged = True
	#

	def printText(self, x:int, y:int, color:str, text:str):
		assert len(text) > 0

		i = 0
		row = self._data[y]
		for c in text:
			if (x + i) >= len(row):
				break
			cell = row[x + i]
			cell.c = c
			if color != None:
				cell.col = color
			cell.bChanged = True
			i += 1
	#

	def hline(self, x1:int, y:int, x2:int, color:str, character:str):
		assert len(character) == 1

		row = self._data[y]
		for ix in range(x1, x2 + 1):
			cell = row[ix]
			cell.c = character
			if color != None:
				cell.col = color
			cell.bChanged = True
	#

	def vline(self, x:int, y1:int, y2:int, color:str, character:str):
		assert len(character) == 1

		for iy in range(y1, y2 + 1):
			cell = self._data[iy][x]
			cell.c = character
			if color != None:
				cell.col = color
			cell.bChanged = True
	#

	def printBoxedText(self, centerX:int, centerY:int, text:str, settings:FramedBoxSettings = None):
		if settings is None:
			settings = self.defaultFramedBoxSettings

		wtext = len(text)
		x1 = centerX - int(wtext/2) - 2
		x2 = x1 + 4 + wtext
		y1 = centerY - 2
		y2 = centerY + 2
		w = x2 - x1
		h = y2 - y1

		self.hline(x1, y1, x2, settings.frameColor, settings.frameCharTop)
		self.hline(x1, y2, x2, settings.frameColor, settings.frameCharBottom)
		self.vline(x1, y1, y2, settings.frameColor, settings.frameCharLeft)
		self.vline(x2, y1, y2, settings.frameColor, settings.frameCharRight)
		self.set(x1, y1, settings.frameColor, settings.frameCharTopLeft)
		self.set(x2, y1, settings.frameColor, settings.frameCharTopRight)
		self.set(x1, y2, settings.frameColor, settings.frameCharBottomLeft)
		self.set(x2, y2, settings.frameColor, settings.frameCharBottomRight)
		self.fill(x1 + 1, y1 + 1, w - 2, h - 2, settings.bgColor, settings.bgChar)
		self.printText(x1 + 2, y1 + 2, settings.textColor, text)
	#

	def drawFrame(self, rect:Rect = None, x1:int = None, y1:int = None, x2:int = None, y2:int = None, settings:FramedBoxSettings = None):
		if settings is None:
			settings = self.defaultFramedBoxSettings

		if rect:
			x1 = rect.x1
			y1 = rect.y1
			x2 = rect.x2
			y2 = rect.y2

		self.hline(x1, y1, x2, settings.frameColor, settings.frameCharTop)
		self.hline(x1, y2, x2, settings.frameColor, settings.frameCharBottom)
		self.vline(x1, y1, y2, settings.frameColor, settings.frameCharLeft)
		self.vline(x2, y1, y2, settings.frameColor, settings.frameCharRight)
		self.set(x1, y1, settings.frameColor, settings.frameCharTopLeft)
		self.set(x2, y1, settings.frameColor, settings.frameCharTopRight)
		self.set(x1, y2, settings.frameColor, settings.frameCharBottomLeft)
		self.set(x2, y2, settings.frameColor, settings.frameCharBottomRight)
	#

	def fillRectangle(self, x:int, y:int, w:int, h:int, color:str, character:str):
		assert len(character) == 1

		for iy in range(y, y + h):
			row = self._data[iy]
			for ix in range(x, x + w):
				cell = row[ix]
				cell.c = character
				if color != None:
					cell.col = color
				cell.bChanged = True
	#

#



