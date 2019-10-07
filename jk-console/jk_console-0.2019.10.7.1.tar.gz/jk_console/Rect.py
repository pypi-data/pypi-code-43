



class Rect(object):

	def __init__(self, x:int, y:int, w:int, h:int):
		assert w >= 0
		assert h >= 0
		self._x1 = x
		self._y1 = y
		self._w = w
		self._h = h
		self._x2 = x + w
		self._y2 = y + h
	#

	@property
	def x(self):
		return self._x1
	#

	@property
	def y(self):
		return self._y1
	#

	@property
	def w(self):
		return self._w
	#

	@property
	def width(self):
		return self._w
	#

	@property
	def h(self):
		return self._h
	#

	@property
	def height(self):
		return self._h
	#

	@property
	def x1(self):
		return self._x1
	#

	@property
	def y1(self):
		return self._y1
	#

	@property
	def x2(self):
		return self._x2
	#

	@property
	def y2(self):
		return self._y2
	#

	def __str__(self):
		return "Rect(" + str(self._x1) + ", " + str(self._y1) + ", " + str(self._x2) + ", " + str(self._y2) + ")"

	def move(self, x:int, y:int):
		return Rect(self._x1 + x, self._y1 + x, self._w, self._h)
	#

	def setPosition(self, x:int, y:int):
		return Rect(x, x, self._w, self._h)
	#

	def setSize(self, w:int, h:int):
		return Rect(self._x1, self._y1, w, h)
	#

	def isPointInRect(self, x:int, y:int):
		return (x >= self._x1) and (y >= self._y1) and (x <= self._x2) and (y <= self._y2)
	#

	def isOtherRectInRect(self, other):
		assert isinstance(other, Rect)
		return (other._x1 >= self._x1) and (other._y1 >= self._y1) and (other._x2 <= self._x2) and (other._y2 <= self._y2)
	#

	def shrink(self, left:int = 0, bottom:int = 0, right:int = 0, top:int = 0, all:int = 0):
		if all != 0:
			x1 = self._x1 + all
			x2 = self._x2 - all
			y1 = self._y1 + all
			y2 = self._y2 - all
		else:
			x1 = self._x1 + left
			x2 = self._x2 - right
			y1 = self._y1 + top
			y2 = self._y2 - bottom
		return Rect(x1, y1, x2 - x1, y2 - y1)
	#

	def grow(self, left:int = 0, bottom:int = 0, right:int = 0, top:int = 0, all:int = 0):
		if all != 0:
			x1 = self._x1 - all
			x2 = self._x2 + all
			y1 = self._y1 - all
			y2 = self._y2 + all
		else:
			x1 = self._x1 - left
			x2 = self._x2 + right
			y1 = self._y1 - top
			y2 = self._y2 + bottom
		return Rect(x1, y1, x2 - x1, y2 - y1)
	#

	def union(self, other):
		assert isinstance(other, Rect)
		x1 = min(self._x1, other._x1, self._x2, other._x2)
		y1 = min(self._y1, other._y1, self._y2, other._y2)
		x2 = max(self._x1, other._x1, self._x2, other._x2)
		y2 = max(self._y1, other._y1, self._y2, other._y2)
		w = x2 - x1
		h = y2 - y1
		if (w < 0) or (h < 0):
			return None
		else:
			return Rect(x1, y1, w, h)
	#

	def intersect(self, other):
		assert isinstance(other, Rect)
		if (other._x2 < self._x1) or (other._y2 < self._y1) \
			or (self._x2 < other._x1) or (self._y2 < other._y1):
			return None
		x1 = other._x1 if self._x1 < other._x1 else self._x1
		y1 = other._y1 if self._y1 < other._y1 else self._y1
		x2 = other._x2 if self._x2 > other._x2 else self._x2
		y2 = other._y2 if self._y2 > other._y2 else self._y2
		w = x2 - x1
		h = y2 - y1
		return Rect(x1, y1, w, h)
	#

#








