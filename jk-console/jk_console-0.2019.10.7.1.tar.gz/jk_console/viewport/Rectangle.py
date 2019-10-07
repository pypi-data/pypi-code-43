



from typing import Union



class Rectangle(object):

	def __init__(self, *args):
		if len(args) == 0:
			self.__x1 = 0
			self.__y1 = 0
			self.__x2 = 0
			self.__y2 = 0
		elif len(args) == 1:
			arg = args[0]
			if isinstance(arg, (tuple, list)):
				assert len(arg) == 4
				assert isinstance(arg[0], int)
				assert isinstance(arg[1], int)
				assert isinstance(arg[2], int)
				assert isinstance(arg[3], int)
				self.__x1 = arg[0]
				self.__y1 = arg[1]
				self.__x2 = self.__x1 + arg[2]
				self.__y2 = self.__y1 + arg[3]
			elif isinstance(arg, Rectangle):
				self.__x1 = arg.x1
				self.__y1 = arg.y1
				self.__x2 = arg.x2
				self.__y2 = arg.y2
			else:
				raise Exception("arg 0 is " + str(type(arg)) + " ???")
		elif len(args) == 4:
			assert isinstance(args[0], int)
			assert isinstance(args[1], int)
			assert isinstance(args[2], int)
			assert isinstance(args[3], int)
			self.__x1 = args[0]
			self.__y1 = args[1]
			self.__x2 = self.__x1 + args[2]
			self.__y2 = self.__y1 + args[3]
		else:
			raise Exception("args ???")

		self.__w = self.__x2 - self.__x1
		self.__h = self.__y2 - self.__y1
	#

	@property
	def width(self) -> int:
		return self.__w
	#

	@width.setter
	def width(self, value:int):
		assert isinstance(value, int)

		self.__w = value
		self.__x2 = self.__x1 + self.__w
	#

	@property
	def height(self) -> int:
		return self.__h
	#

	@height.setter
	def height(self, value:int):
		assert isinstance(value, int)

		self.__h = value
		self.__y2 = self.__y1 + self.__h
	#

	@property
	def x(self) -> int:
		return self.__x1
	#

	@x.setter
	def x(self, value:int):
		assert isinstance(value, int)

		self.__x1 = value
		self.__w = self.__x2 - self.__x1
	#

	@property
	def y(self) -> int:
		return self.__y1
	#

	@y.setter
	def y(self, value:int):
		assert isinstance(value, int)

		self.__y1 = value
		self.__h = self.__y2 - self.__y1
	#

	@property
	def x1(self) -> int:
		return self.__x1
	#

	@x1.setter
	def x1(self, value:int):
		assert isinstance(value, int)

		self.__x1 = value
		self.__w = self.__x2 - self.__x1
	#

	@property
	def y1(self) -> int:
		return self.__y1
	#

	@y1.setter
	def y1(self, value:int):
		assert isinstance(value, int)

		self.__y1 = value
		self.__h = self.__y2 - self.__y1
	#

	@property
	def x2(self) -> int:
		return self.__x2
	#

	@x2.setter
	def x2(self, value:int):
		assert isinstance(value, int)

		self.__x2 = value
		self.__w = self.__x2 - self.__x1
	#

	@property
	def y2(self) -> int:
		return self.__y2
	#

	@y2.setter
	def y2(self, value:int):
		assert isinstance(value, int)

		self.__y2 = value
		self.__h = self.__y2 - self.__y1
	#

	@property
	def topLeft(self) -> tuple:
		return (self.__x1, self.__y1)
	#

	@topLeft.setter
	def topLeft(self, value:Union[tuple, list]):
		assert isinstance(value, (tuple, list))
		assert len(value) == 2

		self.__x1 = value[0]
		self.__y1 = value[1]
		self.__w = self.__x2 - self.__x1
		self.__h = self.__y2 - self.__y1
	#

	@property
	def topRight(self) -> tuple:
		return (self.__x2 - 1, self.__y1)
	#

	@topRight.setter
	def topRight(self, value:Union[tuple, list]):
		assert isinstance(value, (tuple, list))
		assert len(value) == 2

		self.__x2 = value[0] + 1
		self.__y1 = value[1]
		self.__w = self.__x2 - self.__x1
		self.__h = self.__y2 - self.__y1
	#

	@property
	def bottomRight(self) -> tuple:
		return (self.__x2 - 1, self.__y2 - 1)
	#

	@bottomRight.setter
	def bottomRight(self, value:Union[tuple, list]):
		assert isinstance(value, (tuple, list))
		assert len(value) == 2

		self.__x2 = value[0] + 1
		self.__y2 = value[1] + 1
		self.__w = self.__x2 - self.__x1
		self.__h = self.__y2 - self.__y1
	#

	@property
	def bottomLeft(self) -> tuple:
		return (self.__x1, self.__y2 - 1)
	#

	@bottomLeft.setter
	def bottomLeft(self, value:Union[tuple, list]):
		assert isinstance(value, (tuple, list))
		assert len(value) == 2

		self.__x1 = value[0]
		self.__y2 = value[1] + 1
		self.__w = self.__x2 - self.__x1
		self.__h = self.__y2 - self.__y1
	#

	def isValid(self) -> bool:
		return (self.__w > 0) and (self.__h > 0)
	#

	def area(self) -> int:
		return self.__w * self.__h
	#

	#def clone(self) -> Rectangle:
	def clone(self):
		return Rectangle(self)
	#

	def enlarge(self, *args):
		if len(args) == 1:
			v = args[0]
			if isinstance(v, Rectangle):
				self.__x1 -= v.x1
				self.__y1 -= v.y1
				self.__x2 += v.x2
				self.__y2 += v.y2
			else:
				self.__x1 -= v
				self.__y1 -= v
				self.__x2 += v
				self.__y2 += v
		elif len(args) == 2:
			vh = args[0]
			vv = args[1]
			self.__x1 -= vh
			self.__y1 -= vv
			self.__x2 += vh
			self.__y2 += vv
		elif len(args) == 4:
			self.__x1 -= args[0]
			self.__y1 -= args[1]
			self.__x2 += args[2]
			self.__y2 += args[3]
		else:
			raise Exception("args ???")

		self.__w = self.__x2 - self.__x1
		self.__h = self.__y2 - self.__y1

		return self
	#

	def shrink(self, *args):
		if len(args) == 1:
			v = args[0]
			if isinstance(v, Rectangle):
				self.__x1 += v.x1
				self.__y1 += v.y1
				self.__x2 -= v.x2
				self.__y2 -= v.y2
			else:
				self.__x1 += v
				self.__y1 += v
				self.__x2 -= v
				self.__y2 -= v
		elif len(args) == 2:
			vh = args[0]
			vv = args[1]
			self.__x1 += vh
			self.__y1 += vv
			self.__x2 -= vh
			self.__y2 -= vv
		elif len(args) == 4:
			self.__x1 += args[0]
			self.__y1 += args[1]
			self.__x2 -= args[2]
			self.__y2 -= args[3]
		else:
			raise Exception("args ???")

		self.__w = self.__x2 - self.__x1
		self.__h = self.__y2 - self.__y1

		return self
	#

	#def intersect(self, other:Rectangle) -> Rectangle:
	def intersect(self, other):
		assert isinstance(other, Rectangle)

		if (other.__x1 > self.__x2) \
			or (other.__y1 > self.__y2) \
			or (other.__x2 < self.__x1) \
			or (other.__y2 < self.__y1):
			# no intersection
			return None

		x1 = max(self.__x1, other.__x1)
		y1 = max(self.__y1, other.__y1)
		x2 = min(self.__x2, other.__x2)
		y2 = min(self.__y2, other.__y2)

		return Rectangle(x1, y2, x2 - x1, y2 - y1)
	#

	#def unite(self, other:Rectangle) -> Rectangle:
	def unite(self, other):
		assert isinstance(other, Rectangle)

		x1 = min(self.__x1, other.__x1)
		y1 = min(self.__y1, other.__y1)
		x2 = max(self.__x2, other.__x2)
		y2 = max(self.__y2, other.__y2)

		return Rectangle(x1, y1, x2 - x1, y2 - y1)
	#

	@staticmethod
	#def intersectMany(other) -> Rectangle:
	def intersectMany(other):
		assert isinstance(other, (tuple, list))

		if len(other) == 0:
			raise Exception("args ???")

		if len(other) == 1:
			assert isinstance(other, Rectangle)
			return other

		rect = other[0]
		assert isinstance(rect, Rectangle)
		x1 = rect.__x1
		y1 = rect.__y1
		x2 = rect.__x2
		y2 = rect.__y2

		for r in other[1:]:
			assert isinstance(r, Rectangle)

			if (r.__x1 > x2) \
				or (r.__y1 > y2) \
				or (r.__x2 < x1) \
				or (r.__y2 < y1):
				# no intersection
				return None

			x1 = max(x1, r.__x1)
			y1 = max(y1, r.__y1)
			x2 = min(x2, r.__x2)
			y2 = min(y2, r.__y2)

		return Rectangle(x1, y1, x2 - x1, y2 - y1)
	#

	@staticmethod
	#def uniteMany(other) -> Rectangle:
	def uniteMany(other):
		assert isinstance(other, (tuple, list))

		x1 = min([ r.__x1 for r in other ])
		y1 = min([ r.__y1 for r in other ])
		x2 = max([ r.__x2 for r in other ])
		y2 = max([ r.__y2 for r in other ])

		return Rectangle(x1, y2, x2 - x2, y2 - y1)
	#

	def shift(self, x:int, y:int):
		assert isinstance(x, int)
		assert isinstance(y, int)

		self.__x1 += x
		self.__x2 += x
		self.__y1 += y
		self.__y2 += y
	#

#




