



from .Console import *
from .ConsoleBufferRGB_Mixins import *
from ._Rect import _Rect







class _ConsoleBufferRGBCell(object):

	def __init__(self, colorBG:int, colorFG:int):
		self._lastColBG = colorBG
		self._lastColFG = colorFG
		self._lastC = " "
		self.colBG = colorBG
		self.colFG = colorFG
		self.c = " "
		self.bChanged = False
	#

	def copyTo(self, other):
		other.colBG = self.colBG
		other.colFG = self.colFG
		other.c = self.c
		other.bChanged = True
	#

#



#
# This class implements a buffer for the text console. It consists of individual cells, one for every character.
#
# Every cell contain the following attributes:
# * `str c` : The (single) character of this cell.
# * `bool bChanged` : A boolean flag set to `true` on change. (Typically only changed cells will be rendered.)
# * `int bgColor` : The background color of the cell.
#
class ConsoleBufferRGB(ConsoleBufferRGB_Mixins):

	def __init__(self, width:int = None, height:int = None, bgColor:int = None, bWithCaching:bool = True):
		self._bgColor = bgColor
		self._width = Console.width() - 1 if width is None else width
		self._height = Console.height() - 1 if height is None else height
		self._widthM1 = self._width - 1
		self._heightM1 = self._height - 1
		self._numberOfCells = self._width * self._height

		self._lineNumbers = tuple(range(0, self._height))
		self._columnNumbers = tuple(range(0, self._width))

		self._data = [ [_ConsoleBufferRGBCell(bgColor, None) for x in self._columnNumbers] for y in self._lineNumbers]

		assert len(self._lineNumbers) == self._height
		assert len(self._columnNumbers) == self._width
		assert len(self._data) == self._height
		for i in range(0, self._height):
			assert len(self._data[i]) == self._width

		self._bFullPaint = True

		# caching

		self._bWithCaching = bWithCaching
		if bWithCaching:
			self.__colMapBG = {}
			self.__colMapFG = {}
			self.__compileColor = self.__compileColorWithCaching
		else:
			self.__colMapBG = None
			self.__colMapFG = None
			self.__compileColor = self.__compileColorWithoutCaching

		#self._Mixins_init()
	#

	def clearInternalCache(self):
		if self._bWithCaching:
			self.__colMapBG.clear()
			self.__colMapFG.clear()
	#

	def __str__(self):
		return "<ConsoleBufferRGB size=%dx%d at %x>" % (self._width, self._height, id(self))
	#

	def __repr__(self):
		return "<ConsoleBufferRGB size=%dx%d at %x>" % (self._width, self._height, id(self))
	#

	#
	# Returns a tuple with two values: The width and height.
	#
	@property
	def size(self):
		return self._width, self._height
	#

	@property
	def width(self):
		return self._width
	#

	@property
	def height(self):
		return self._height
	#

	#
	# Force full repaint for next rendering.
	#
	def fullRepaint(self):
		self._bFullPaint = True
	#

	def bufferToBuffer(self, ofsX:int, ofsY:int, other, bForceFullRepaint:bool = False):
		assert isinstance(other, ConsoleBufferRGB)

		sourceRect = _Rect(0, 0, self._width, self._height)
		destRect = _Rect(0, 0, other._width, other._height)
		destRect0 = sourceRect.clone().move(ofsX, ofsY).intersect(destRect)
		sourceRect0 = destRect0.clone().move(-ofsX, -ofsY)

		for y in range(0, destRect0.height):
			currentRowSrc = self._data[sourceRect0.y + y]
			currentRowDest = other._data[destRect0.y + y]
			for x in range(0, destRect0.width):
				currentCellSrc = currentRowSrc[sourceRect0.x + x]
				currentCellDest = currentRowDest[destRect0.x + x]
				currentCellDest.c = currentCellSrc.c
				currentCellDest.colBG = currentCellSrc.colBG
				currentCellDest.colFG = currentCellSrc.colFG
				currentCellDest.bChanged = True
	#

	#
	# Convert the rgb color valus to a string
	#
	def __compileColorWithCaching(self, bgRGB:int, fgRGB:int):
		s = ""
		if bgRGB != None:
			colStr = self.__colMapBG.get(bgRGB)
			if colStr is None:
				colStr = "\033[48;2;" + str((bgRGB >> 16) & 0xff) + ";" + str((bgRGB >> 8) & 0xff) + ";" + str(bgRGB & 0xff) + "m"
				self.__colMapBG[bgRGB] = colStr
			s += colStr
		if fgRGB != None:
			colStr = self.__colMapFG.get(fgRGB)
			if colStr is None:
				colStr = "\033[38;2;" + str((fgRGB >> 16) & 0xff) + ";" + str((fgRGB >> 8) & 0xff) + ";" + str(fgRGB & 0xff) + "m"
				self.__colMapFG[fgRGB] = colStr
			s += colStr
		return s
	#

	#
	# Convert the rgb color valus to a string
	#
	def __compileColorWithoutCaching(self, bgRGB:int, fgRGB:int):
		s = ""
		if bgRGB != None:
			s += "\033[48;2;" + str((bgRGB >> 16) & 0xff) + ";" + str((bgRGB >> 8) & 0xff) + ";" + str(bgRGB & 0xff) + "m"
		if fgRGB != None:
			s += "\033[38;2;" + str((fgRGB >> 16) & 0xff) + ";" + str((fgRGB >> 8) & 0xff) + ";" + str(fgRGB & 0xff) + "m"
		return s
	#

	def bufferToConsole(self, ofsX:int = 0, ofsY:int = 0, bForceFullRepaint:bool = False):
		if self._bFullPaint or bForceFullRepaint:
			characters = []
			for y in self._lineNumbers:
				characters.clear()
				lastColBG = None
				lastColFG = None

				currentRow = self._data[y]
				for x in self._columnNumbers:
					currentCell = currentRow[x]
					#assert currentCell.col != None
					#assert currentCell.c != None
					currentCell._lastColBG = currentCell.colBG
					currentCell._lastColFG = currentCell.colFG
					currentCell._lastC = currentCell.c
					if (lastColBG != currentCell.colBG) or (lastColFG != currentCell.colFG):
						lastColBG = currentCell.colBG
						lastColFG = currentCell.colFG
						characters.append(self.__compileColor(lastColBG, lastColFG))
					characters.append(currentCell.c)
					currentCell.bChanged = False
				characters.append(Console.RESET)
				Console.printAt(ofsX, ofsY + y, "".join(characters), False)
			self._bFullPaint = False

		else:
			startX = -1
			characters = []
			bLastWasChanged = False
			lastColBG = None
			lastColFG = None

			for y in self._lineNumbers:
				currentRow = self._data[y]
				for x in self._columnNumbers:
					currentCell = currentRow[x]
					#assert currentCell.col != None
					#assert currentCell.c != None
					if currentCell.bChanged:
						# we might have a change here
						if (currentCell.c != currentCell._lastC) \
							or (currentCell.colBG != currentCell._lastColBG) \
							or (currentCell.colFG != currentCell._lastColFG):

							# yes, we really have a change here
							currentCell._lastColBG = currentCell.colBG
							currentCell._lastColFG = currentCell.colFG
							currentCell._lastC = currentCell.c
							if bLastWasChanged:
								if (lastColBG != currentCell.colBG) or (lastColFG != currentCell.colFG):
									lastColBG = currentCell.colBG
									lastColFG = currentCell.colFG
									characters.append(self.__compileColor(lastColBG, lastColFG))
								characters.append(currentCell.c)
							else:
								if startX >= 0:
									characters.append(Console.RESET)
									Console.printAt(ofsX + startX, ofsY + y, "".join(characters), False)
									characters.clear()
								startX = x
								lastColBG = currentCell.colBG
								lastColFG = currentCell.colFG
								characters.append(self.__compileColor(currentCell.colBG, currentCell.colFG))
								characters.append(currentCell.c)
								bLastWasChanged = True
						else:
							bLastWasChanged = False
						currentCell.bChanged = False
					else:
						bLastWasChanged = False

				if startX >= 0:
					characters.append(Console.RESET)
					Console.printAt(ofsX + startX, ofsY + y, "".join(characters), False)
					characters.clear()
					startX = -1
					bLastWasChanged = False
					lastColBG = None
					lastColFG = None

		print(Console.RESET_TOPLEFT, end="", flush=True)
	#

#



