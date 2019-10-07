#!/usr/bin/env python3





class _Rect(object):

	def __init__(self, x:int, y:int, w:int, h:int):
		self.x = x
		self.y = y
		self.width = w
		self.height = h
	#

	@property
	def x1(self):
		return self.x
	#

	@property
	def y1(self):
		return self.y
	#

	@property
	def x2(self):
		return self.x + self.width
	#

	@property
	def y2(self):
		return self.y + self.height
	#

	def __str__(self):
		return "Rect(" + str(self.x) + ", " + str(self.y) + ", " + str(self.x2) + ", " + str(self.y2) + ")"

	def move(self, x:int, y:int):
		self.x += x
		self.y += y
		return self
	#

	def setPosition(self, x:int, y:int):
		self.x = x
		self.y = y
		return self
	#

	def setSize(self, w:int, h:int):
		self.width = w
		self.height = h
		return self
	#

	def isPointInRect(self, x:int, y:int):
		return (x >= self.x) and (y >= self.y) and (x <= self.x + self.width) and (y <= self.y + self.height)
	#

	def isOtherRectInRect(self, other):
		assert isinstance(other, _Rect)
		return (other.x >= self.x) and (other.y >= self.y) and (other.x2 <= self.x2) and (other.y2 <= self.y2)
	#

	def shrink(self, left:int = 0, bottom:int = 0, right:int = 0, top:int = 0, all:int = 0):
		if all != 0:
			self.x += all
			self.width -= 2 * all
			self.y += all
			self.height -= 2 * all
		else:
			self.x += left
			self.width -= left + right
			self.y += top
			self.height -= top + bottom
		return self
	#

	def grow(self, left:int = 0, bottom:int = 0, right:int = 0, top:int = 0, all:int = 0):
		if all != 0:
			self.x -= all
			self.width += 2 * all
			self.y -= all
			self.height += 2 * all
		else:
			self.x -= left
			self.width += left + right
			self.y -= top
			self.height += top + bottom
		return self
	#

	def union(self, other):
		assert isinstance(other, _Rect)
		x1 = min(self.x, other.x, self.x2, other.x2)
		y1 = min(self.y, other.y, self.y2, other.y2)
		x2 = max(self.x, other.x, self.x2, other.x2)
		y2 = max(self.y, other.y, self.y2, other.y2)
		w = x2 - x1
		h = y2 - y1
		return _Rect(x1, y1, w, h)
	#

	def intersect(self, other):
		assert isinstance(other, _Rect)
		if (other.x2 < self.x) or (other.y2 < self.y) \
			or (self.x2 < other.x) or (self.y2 < other.y):
			return None
		x1 = other.x if self.x < other.x else self.x
		y1 = other.y if self.y < other.y else self.y
		x2 = other.x2 if self.x2 > other.x2 else self.x2
		y2 = other.y2 if self.y2 > other.y2 else self.y2
		w = x2 - x1
		h = y2 - y1
		return _Rect(x1, y1, w, h)
	#

	def clone(self):
		return _Rect(self.x, self.y, self.width, self.height)

#








