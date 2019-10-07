



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




class ConsoleBufferWO(object):

	class _Cell(object):

		def __init__(self, bgColor:str):
			self.col = bgColor
			self.c = " "
			self.bChanged = False
		#

		def clear(self, bgColor:str):
			self.col = bgColor
			self.c = " "
			self.bChanged = True
		#

	#

	def __init__(self, ofsX:int = 0, ofsY:int = 0, width:int = None, height:int = None, bgColor:str = Console.RESET, bAlwaysFullRepaint = False):
		self.__bgColor = bgColor
		self.__width = Console.width() - 1 if width is None else width
		self.__height = Console.height() - 1 if height is None else height
		self.__widthM1 = self.__width - 1
		self.__heightM1 = self.__height - 1
		self.__numberOfCells = self.__width * self.__height
		self.__ofsX = ofsX
		self.__ofsY = ofsY

		self.defaultFramedBoxSettings = FramedBoxSettings()

		self.__lineNumbers = tuple(range(0, self.__height))
		self.__columnNumbers = tuple(range(0, self.__width))

		self.__lastBuffer = [ [ConsoleBufferWO._Cell(bgColor) for x in self.__columnNumbers] for y in self.__lineNumbers]
		self._currentBuffer = [ [ConsoleBufferWO._Cell(bgColor) for x in self.__columnNumbers] for y in self.__lineNumbers]

		assert len(self.__lineNumbers) == self.__height
		assert len(self.__columnNumbers) == self.__width
		assert len(self.__lastBuffer) == self.__height
		assert len(self._currentBuffer) == self.__height
		for i in range(0, self.__height):
			assert len(self.__lastBuffer[i]) == self.__width
			assert len(self._currentBuffer[i]) == self.__width

		self.__bFullPaint = True
		self.__bAlwaysFullRepaint = bAlwaysFullRepaint
	#

	@property
	def bounds(self):
		return Rect(0, 0, self.__width, self.__height)
	#

	@property
	def size(self):
		return self.__width, self.__height
	#

	@property
	def width(self):
		return self.__width
	#

	@property
	def height(self):
		return self.__height
	#

	def clear(self):
		bgColor = self.__bgColor
		for y in self.__lineNumbers:
			for x in self.__columnNumbers:
				self._currentBuffer[y][x].clear(bgColor)
		self.__bFullPaint = True
	#

	def set(self, x:int, y:int, color:str, character:str):
		assert len(character) == 1

		cell = self._currentBuffer[y][x]
		if character != None:
			cell.c = character
			cell.bChanged = True
		if color != None:
			cell.col = color
			cell.bChanged = True
	#

	def hline(self, x1:int, y:int, x2:int, color:str, character:str):
		assert len(character) == 1

		row = self._currentBuffer[y]
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
			cell = self._currentBuffer[iy][x]
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

	def fill(self, x:int, y:int, w:int, h:int, color:str, character:str):
		assert len(character) == 1

		for iy in range(y, y + h):
			row = self._currentBuffer[iy]
			for ix in range(x, x + w):
				cell = row[ix]
				cell.c = character
				if color != None:
					cell.col = color
				cell.bChanged = True
	#

	def printText(self, x:int, y:int, color:str, text:str):
		assert len(text) > 0

		i = 0
		for c in text:
			cell = self._currentBuffer[y][x + i]
			cell.c = c
			if color != None:
				cell.col = color
			cell.bChanged = True
			i += 1
	#

	def bufferToConsole(self):
		if self.__bFullPaint or self.__bAlwaysFullRepaint:
			characters = []
			for y in self.__lineNumbers:
				characters.clear()
				lastCol = None

				lastRow = self.__lastBuffer[y]
				currentRow = self._currentBuffer[y]
				for x in self.__columnNumbers:
					lastCell = lastRow[x]
					currentCell = currentRow[x]
					#assert currentCell.col != None
					#assert currentCell.c != None
					lastCell.col = currentCell.col
					lastCell.c = currentCell.c
					if lastCol != currentCell.col:
						lastCol = currentCell.col
						characters.append(lastCol)
					characters.append(currentCell.c)
					currentCell.bChanged = False
				characters.append(Console.RESET)
				Console.printAt(self.__ofsX, self.__ofsY + y, "".join(characters), False)
			self.__bFullPaint = False

		else:
			startX = -1
			characters = []
			bLastWasChanged = False
			lastCol = None

			for y in self.__lineNumbers:
				lastRow = self.__lastBuffer[y]
				currentRow = self._currentBuffer[y]
				for x in self.__columnNumbers:
					lastCell = lastRow[x]
					currentCell = currentRow[x]
					#assert currentCell.col != None
					#assert currentCell.c != None
					if currentCell.bChanged:
						# we might have a change here
						if (currentCell.c != lastCell.c) or (currentCell.col != lastCell.col):
							# yes, we really have a change here
							lastCell.col = currentCell.col
							lastCell.c = currentCell.c
							if bLastWasChanged:
								if lastCol != currentCell.col:
									lastCol = currentCell.col
									characters.append(lastCol)
								characters.append(currentCell.c)
							else:
								if startX >= 0:
									characters.append(Console.RESET)
									Console.printAt(self.__ofsX + startX, self.__ofsY + y, "".join(characters), False)
									characters.clear()
								startX = x
								lastCol = currentCell.col
								characters.append(currentCell.col)
								characters.append(currentCell.c)
								bLastWasChanged = True
						else:
							bLastWasChanged = False
						currentCell.bChanged = False
					else:
						bLastWasChanged = False

				if startX >= 0:
					characters.append(Console.RESET)
					Console.printAt(self.__ofsX + startX, self.__ofsY + y, "".join(characters), False)
					characters.clear()
					startX = -1
					bLastWasChanged = False
					lastCol = None

		print(Console.RESET_TOPLEFT, end="", flush=True)
	#

#



