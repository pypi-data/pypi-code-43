



from .Console import *
from .ConsoleBuffer import *
from .Rect import *






class CharacterBuffer(object):

	class _Cell(object):

		def __init__(self, bgColor:str):
			self.col = bgColor
			self.c = " "
		#

		def clear(self, bgColor:str):
			self.col = bgColor
			self.c = " "
		#

	#

	def __init__(self, width:int, height:int, bgColor:str = Console.RESET):
		self.__bgColor = bgColor
		self.__width = width
		self.__height = height
		self.__widthM1 = self.__width - 1
		self.__heightM1 = self.__height - 1
		self.__numberOfCells = self.__width * self.__height

		self.__lineNumbers = tuple(range(0, self.__height))
		self.__columnNumbers = tuple(range(0, self.__width))

		self._currentBuffer = [ [CharacterBuffer._Cell(bgColor) for x in self.__columnNumbers] for y in self.__lineNumbers]
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
	#

	def set(self, x:int, y:int, color:str, character:str):
		assert len(character) == 1

		cell = self._currentBuffer[y][x]
		if color != None:
			cell.c = character
		if color != None:
			cell.col = color
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
	#

	def printText(self, x:int, y:int, color:str, text:str):
		assert len(text) > 0

		i = 0
		for c in text:
			cell = self._currentBuffer[y][x + i]
			cell.c = c
			if color != None:
				cell.col = color
			i += 1
	#

	def copyToCharacterBuffer1(self, srcX:int, srcY:int, width:int, height:int, destX:int, destY:int, otherBuffer):
		assert isinstance(otherBuffer, CharacterBuffer)

		rSrc = Rect(srcX, srcY, width, height)
		assert self.bounds.isOtherRectInRect(rSrc)
		rDest = Rect(destX, destY, width, height)
		assert otherBuffer.bounds.isOtherRectInRect(rDest)

		deltaX = destX - srcX
		deltaY = destY - srcY

		# ----------------

		for srcIY in range(srcY, srcY + height):
			srcRow = self._currentBuffer[srcIY]
			destRow = otherBuffer._currentBuffer[srcIY + deltaY]
			for srcIX in range(srcX, srcX + width):
				srcCell = srcRow[srcIX]
				destCell = destRow[srcIX + deltaX]
				destCell.c = srcCell.c
				destCell.col = srcCell.col
	#

	def copyToCharacterBuffer0(self, destX:int, destY:int, otherBuffer):
		assert isinstance(otherBuffer, CharacterBuffer)

		width = self.__width
		height = self.__height

		rDest = Rect(destX, destY, width, height)
		assert otherBuffer.bounds.isOtherRectInRect(rDest)

		deltaX = destX
		deltaY = destY
		srcX = 0
		srcY = 0

		# ----------------

		for srcIY in range(srcY, srcY + height):
			srcRow = self._currentBuffer[srcIY]
			destRow = otherBuffer._currentBuffer[srcIY + deltaY]
			for srcIX in range(srcX, srcX + width):
				srcCell = srcRow[srcIX]
				destCell = destRow[srcIX + deltaX]
				destCell.c = srcCell.c
				destCell.col = srcCell.col
	#

	def copyToConsoleBuffer1(self, srcX:int, srcY:int, width:int, height:int, destX:int, destY:int, otherBuffer:ConsoleBuffer):
		rSrc = Rect(srcX, srcY, width, height)
		assert self.bounds.isOtherRectInRect(rSrc)
		rDest = Rect(destX, destY, width, height)
		assert otherBuffer.bounds.isOtherRectInRect(rDest)

		deltaX = destX - srcX
		deltaY = destY - srcY

		# ----------------

		for srcIY in range(srcY, srcY + height):
			srcRow = self._currentBuffer[srcIY]
			destRow = otherBuffer._currentBuffer[srcIY + deltaY]
			for srcIX in range(srcX, srcX + width):
				srcCell = srcRow[srcIX]
				destCell = destRow[srcIX + deltaX]
				destCell.c = srcCell.c
				destCell.col = srcCell.col
				destCell.bChanged = True
	#

	def copyToConsoleBuffer0(self, destX:int, destY:int, otherBuffer:ConsoleBuffer):
		width = self.__width
		height = self.__height

		rDest = Rect(destX, destY, width, height)
		assert otherBuffer.bounds.isOtherRectInRect(rDest)

		deltaX = destX
		deltaY = destY
		srcX = 0
		srcY = 0

		# ----------------

		for srcIY in range(srcY, srcY + height):
			srcRow = self._currentBuffer[srcIY]
			destRow = otherBuffer._currentBuffer[srcIY + deltaY]
			for srcIX in range(srcX, srcX + width):
				srcCell = srcRow[srcIX]
				destCell = destRow[srcIX + deltaX]
				destCell.c = srcCell.c
				destCell.col = srcCell.col
				destCell.bChanged = True
	#

#



