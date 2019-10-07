

from typing import Union

from ..Console import Console
from .ViewPortCell import ViewPortCell
from .ViewPortRenderer import ViewPortRenderer
from .ViewPortRGB import ViewPortRGB
from .Rectangle import Rectangle






class ViewPortBuffer2(object):

	LINE_STYLE_SIMPLE = [ "-", "|", "/", "\\", "\\", "/" ]

	def __init__(self, viewPort, ofsX:int, ofsY:int, width:int, height:int):
		self.__viewPort = viewPort
		self.__width = width
		self.__height = height
		self.__ofsX = ofsX
		self.__ofsY = ofsY
		self.rows = []
		for y in range(0, height):
			row = [ None ] * self.__width
			self.rows.append(row)
			for x in range(0, width):
				row[x] = ViewPortCell()
		self.__brightness = ViewPortRenderer.MAX_BRIGHTNESS
		self._bModified = False
		self.bErrorIfOutOfBounds = False
	#

	def _setBrightness(self, brightness:int):
		for row in self.rows:
			for cell in row:
				cell._brightness = brightness
		self.__brightness = brightness
	#

	@property
	def viewPort(self):
		return self.__viewPort
	#

	@property
	def height(self) -> int:
		return self.__height
	#

	@property
	def width(self) -> int:
		return self.__width
	#

	@property
	def ofsX(self) -> int:
		return self.__ofsX
	#

	@property
	def ofsY(self) -> int:
		return self.__ofsY
	#

	@property
	def bounds(self) -> Rectangle:
		return Rectangle(self.__ofsX, self.__ofsY, self.__width, self.__height)
	#

	@property
	def sizeRect(self) -> Rectangle:
		return Rectangle(0, 0, self.__width, self.__height)
	#

	def drawText(self, *args, text:str = None, colBG:ViewPortRGB = None, colFG:ViewPortRGB = None):
		if len(args) == 1:
			assert isinstance(args[0], (tuple, list))
			x = args[0][0]
			y = args[0][1]
		elif len(args) == 2:
			x = args[0]
			y = args[1]
		else:
			raise Exception("args ???")

		assert isinstance(text, str)

		assert isinstance(x, int)
		assert isinstance(y, int)

		if self.bErrorIfOutOfBounds:
			row = self.rows[y]
			for i, c in enumerate(text[0:self.__width]):
				cell = row[x + i]
				if c is not None:
					cell.c = c
				if colBG is not None:
					cell.colBG = int(colBG)
				if colFG is not None:
					cell.colFG = int(colFG)

		else:
			if 0 <= y < self.__height:
				row = self.rows[y]
				for i, c in enumerate(text[0:self.__width]):
					#self.rows[y][x + i].set(c, colBG, colFG)

					ix = x + i
					if 0 <= ix < self.__width:
						cell = row[ix]
						if c is not None:
							cell.c = c
						if colBG is not None:
							cell.colBG = int(colBG)
						if colFG is not None:
							cell.colFG = int(colFG)
	#

	def set(self, x:int, y:int, c:str = None, colBG:ViewPortRGB = None, colFG:ViewPortRGB = None):
		#if len(args) == 1:
		#	assert isinstance(args[0], (tuple, list))
		#	x = args[0][0]
		#	y = args[0][1]
		#elif len(args) == 2:
		#	x = args[0]
		#	y = args[1]
		#else:
		#	raise Exception("args ???")

		#assert isinstance(c, str)

		#assert isinstance(x, int)
		#assert isinstance(y, int)

		# self.rows[y][x].set(c, colBG, colFG)

		if self.bErrorIfOutOfBounds:
			cell = self.rows[y][x]
			if c is not None:
				cell.c = c
			if colBG is not None:
				cell.colBG = int(colBG)
			if colFG is not None:
				cell.colFG = int(colFG)

		else:
			if (0 <= y < self.__height) and (0 <= x < self.__width):
				cell = self.rows[y][x]
				if c is not None:
					cell.c = c
				if colBG is not None:
					cell.colBG = int(colBG)
				if colFG is not None:
					cell.colFG = int(colFG)
	#

	def drawRect(self, *args, colBG:ViewPortRGB = None, colFG:ViewPortRGB = None, lineStyle = None):
		if len(args) == 1:
			r = args[0]
			if isinstance(r, Rectangle):
				x1 = r.x1
				y1 = r.y1
				w = r.width
				h = r.height
			elif isinstance(r, (tuple, list)):
				assert len(r) == 4
				x1 = r[0]
				y1 = r[1]
				w = r[2]
				h = r[3]
			else:
				raise Exception("args ???")
		elif len(args) == 4:
			x1 = args[0]
			y1 = args[1]
			w = args[2]
			h = args[3]
		else:
			raise Exception("args ???")

		assert isinstance(x1, int)
		assert isinstance(y1, int)
		assert isinstance(w, int)
		assert isinstance(h, int)

		if lineStyle is None:
			lineStyle = ViewPortBuffer2.LINE_STYLE_SIMPLE
		else:
			assert isinstance(lineStyle, (tuple, list))
			assert len(lineStyle) == 6
		if colFG:
			assert isinstance(colFG, (int, ViewPortRGB))
		if colBG:
			assert isinstance(colBG, (int, ViewPortRGB))

		hh, vv, tl, tr, bl, br = lineStyle
		x2 = x1 + w - 1
		y2 = y1 + h - 1

		if self.bErrorIfOutOfBounds:
			self.rows[y1][x1].set(tl, colBG, colFG)
			self.rows[y1][x2].set(tr, colBG, colFG)
			self.rows[y2][x1].set(bl, colBG, colFG)
			self.rows[y2][x2].set(br, colBG, colFG)
			for x in range(x1 + 1, x2):
				self.rows[y1][x].set(hh, colBG, colFG)
				self.rows[y2][x].set(hh, colBG, colFG)
			for y in range(y1 + 1, y2):
				self.rows[y][x1].set(vv, colBG, colFG)
				self.rows[y][x2].set(vv, colBG, colFG)

		else:
			if 0 <= y1 < self.__height:
				if 0 <= x1 < self.__width:
					self.rows[y1][x1].set(tl, colBG, colFG)
				if 0 <= x2 < self.__width:
					self.rows[y1][x2].set(tr, colBG, colFG)
			if 0 <= y2 < self.__height:
				if 0 <= x1 < self.__width:
					self.rows[y2][x1].set(bl, colBG, colFG)
				if 0 <= x2 < self.__width:
					self.rows[y2][x2].set(br, colBG, colFG)
			for x in range(x1 + 1, x2):
				if 0 <= x < self.__width:
					if 0 <= y1 < self.__height:
						self.rows[y1][x].set(hh, colBG, colFG)
					if 0 <= y2 < self.__height:
						self.rows[y2][x].set(hh, colBG, colFG)
			for y in range(y1 + 1, y2):
				if 0 <= y < self.__height:
					if 0 <= x1 < self.__width:
						self.rows[y][x1].set(vv, colBG, colFG)
					if 0 <= x2 < self.__width:
						self.rows[y][x2].set(vv, colBG, colFG)
	#

	def fill(self, c:str = None, colBG:ViewPortRGB = None, colFG:ViewPortRGB = None):
		if c is not None:
			assert isinstance(c, str)
			assert len(c) == 1
		if colFG:
			assert isinstance(colFG, (int, ViewPortRGB))
		if colBG:
			assert isinstance(colBG, (int, ViewPortRGB))

		for y in range(0, self.__height):
			for x in range(0, self.__width):
				cell = self.rows[y][x]
				if c is not None:
					cell.c = c
				if colBG:
					cell.colBG = int(colBG)
				if colFG:
					cell.colFG = int(colFG)

		self._bModified = True
	#

	def fillRect(self, x:int, y:int, w:int, h:int, c:str = None, colBG:ViewPortRGB = None, colFG:ViewPortRGB = None):
		assert isinstance(x, int)
		assert isinstance(y, int)
		assert isinstance(w, int)
		assert isinstance(h, int)

		if c is not None:
			assert isinstance(c, str)
			assert len(c) == 1
		if colFG:
			assert isinstance(colFG, (int, ViewPortRGB))
		if colBG:
			assert isinstance(colBG, (int, ViewPortRGB))

		if self.bErrorIfOutOfBounds:
			for iy in range(y, y+h):
				for ix in range(0, x+w):
					cell = self.rows[iy][ix]
					if c is not None:
						cell.c = c
					if colBG:
						cell.colBG = int(colBG)
					if colFG:
						cell.colFG = int(colFG)

		else:
			for iy in range(y, y+h):
				if 0 <= iy < self.__height:
					row = self.rows[iy]
					for ix in range(0, x+w):
						if 0 <= ix < self.__width:
							cell = row[ix]
							if c is not None:
								cell.c = c
							if colBG:
								cell.colBG = int(colBG)
							if colFG:
								cell.colFG = int(colFG)

		self._bModified = True
	#

#














