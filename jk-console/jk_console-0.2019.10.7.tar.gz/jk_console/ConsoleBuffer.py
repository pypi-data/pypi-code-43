



from .Console import *
from .ConsoleBuffer_Mixins import *
from ._Rect import _Rect







class _ConsoleBufferCell(object):

	def __init__(self, color:str):
		self._lastCol = color
		self._lastC = " "
		self.col = color
		self.c = " "
		self.bChanged = False
	#

	def clear(self, color:str = Console.RESET):
		self.col = color
		self.c = " "
		self.bChanged = True
	#

	def set(self, color:str, character:str):
		if character != None:
			assert len(character) == 1
			self.c = character
			self.bChanged = True
		if color != None:
			self.col = color
			self.bChanged = True
	#

	def copyTo(self, other):
		other.col = self.col
		other.c = self.c
		other.bChanged = True
	#

#



#
# This class implements a buffer for the text console. It consists of individual cells, one for every character.
#
# Every cell contain the following attributes:
# * `str col` : The color of the cell. (Foreground and background.)
# * `str c` : The (single) character of this cell.
# * `bool bChanged` : A boolean flag set to `true` on change. (Typically only changed cells will be rendered.)
# * `void clear(str bgColor)` : A convenience method to reset this cell.
#
class ConsoleBuffer(ConsoleBuffer_Mixins):

	def __init__(self, width:int = None, height:int = None, bgColor:str = Console.RESET):
		self._bgColor = bgColor
		self._width = Console.width() - 1 if width is None else width
		self._height = Console.height() - 1 if height is None else height
		self._widthM1 = self._width - 1
		self._heightM1 = self._height - 1
		self._numberOfCells = self._width * self._height

		self._lineNumbers = tuple(range(0, self._height))
		self._columnNumbers = tuple(range(0, self._width))

		self._data = [ [_ConsoleBufferCell(bgColor) for x in self._columnNumbers] for y in self._lineNumbers]

		assert len(self._lineNumbers) == self._height
		assert len(self._columnNumbers) == self._width
		assert len(self._data) == self._height
		for i in range(0, self._height):
			assert len(self._data[i]) == self._width

		self._bFullPaint = True

		self._Mixins_init()
	#

	def __str__(self):
		return "<ConsoleBuffer size=%dx%d at %x>" % (self._width, self._height, id(self))
	#

	def __repr__(self):
		return "<ConsoleBuffer size=%dx%d at %x>" % (self._width, self._height, id(self))
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
		assert isinstance(other, ConsoleBuffer)

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
				currentCellDest.col = currentCellSrc.col
				currentCellDest.bChanged = True
	#

	def bufferToConsole(self, ofsX:int = 0, ofsY:int = 0, bForceFullRepaint:bool = False):
		if self._bFullPaint or bForceFullRepaint:
			characters = []
			for y in self._lineNumbers:
				characters.clear()
				lastCol = None

				currentRow = self._data[y]
				for x in self._columnNumbers:
					currentCell = currentRow[x]
					#assert currentCell.col != None
					#assert currentCell.c != None
					currentCell._lastCol = currentCell.col
					currentCell._lastC = currentCell.c
					if lastCol != currentCell.col:
						lastCol = currentCell.col
						characters.append(lastCol)
					characters.append(currentCell.c)
					currentCell.bChanged = False
				characters.append(Console.RESET)
				Console.printAt(ofsX, ofsY + y, "".join(characters), False)
			self._bFullPaint = False

		else:
			startX = -1
			characters = []
			bLastWasChanged = False
			lastCol = None

			for y in self._lineNumbers:
				currentRow = self._data[y]
				for x in self._columnNumbers:
					currentCell = currentRow[x]
					#assert currentCell.col != None
					#assert currentCell.c != None
					if currentCell.bChanged:
						# we might have a change here
						if (currentCell.c != currentCell._lastC) or (currentCell.col != currentCell._lastCol):
							# yes, we really have a change here
							currentCell._lastCol = currentCell.col
							currentCell._lastC = currentCell.c
							if bLastWasChanged:
								if lastCol != currentCell.col:
									lastCol = currentCell.col
									characters.append(lastCol)
								characters.append(currentCell.c)
							else:
								if startX >= 0:
									characters.append(Console.RESET)
									Console.printAt(ofsX + startX, ofsY + y, "".join(characters), False)
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
					Console.printAt(ofsX + startX, ofsY + y, "".join(characters), False)
					characters.clear()
					startX = -1
					bLastWasChanged = False
					lastCol = None

		print(Console.RESET_TOPLEFT, end="", flush=True)
	#

#



