



class _FlexNone(object):

	def __init__(self):
		pass
	#

	def __eq__(self, v):
		return v is None
	#

	def __ne__(self, v):
		return v is not None
	#

	def __getitem__(self, key):
		return self
	#

	def __getattr__(self, key):
		return self
	#

	def __bool__(self):
		return False
	#

	def __str__(self):
		return "None"
	#

	def __repr__(self):
		return "None"
	#

#

NONE = _FlexNone()



class FlexObject(object):

	def __init__(self, data:dict):
		assert isinstance(data, dict)

		for key, value in list(data.items()):
			if isinstance(value, dict):
				self.__dict__[key] = FlexObject(value)
			elif isinstance(value, (list, tuple)):
				_ = []
				for item in value:
					if isinstance(item, dict):
						_.append(FlexObject(item))
					else:
						_.append(item)
				self.__dict__[key] = _
			else:
				self.__dict__[key] = value
	#

	def _getByPath(self, path):
		if len(path) == 0:
			return None

		nextKey = path[0]
		if nextKey in self.__dict__.keys():
			v = self.__dict__[nextKey]
		else:
			return NONE

		if len(path) == 1:
			return v
		else:
			if isinstance(v, FlexObject):
				return v._getByPath(path[1:])
			else:
				# path came to an end with a value
				return NONE
	#

	def _keys(self):
		return self.__dict__.keys()
	#

	def _isEmpty(self):
		return not bool(self.__dict__)
	#

	def _hasData(self):
		return bool(self.__dict__)
	#

	def _get(self, key):
		return self.__dict__.get(key)
	#

	def _values(self):
		return self.__dict__.values()
	#

	def _items(self):
		return self.__dict__.items()
	#

	def _remove(self, key:str):
		assert isinstance(key, str)

		if key in self.__dict__.keys():
			del self.__dict__[key]
			return True
		else:
			return False
	#

	def _clone(self):
		return FlexObject(self._toDict())
	#

	def __valueToJSON(self, value):
		if isinstance(value, FlexObject):
			return value._toDict()
		elif isinstance(value, (tuple, list)):
			return [
				self.__valueToJSON(x) for x in value
			]
		elif value is NONE:
			return None
		else:
			return value
	#
	
	def _toDict(self) -> dict:
		ret = {}
		for key, value in self.__dict__.items():
			ret[key] = self.__valueToJSON(value)
		return ret
	#

	def __isObj(self, data, filter:dict) -> bool:
		assert isinstance(data, FlexObject)
		assert isinstance(filter, dict)

		for k, v in filter.items():
			if k in data.__dict__:
				# 1st attempt
				v2 = data[k]
				if v != v2:
					return False
			else:
				if k.startswith("_"):
					# 2nd attempt
					k = k[1:]
					if k in data.__dict__:
						v2 = data[k]
						if v != v2:
							return False
					else:
						return False
				else:
					return False
		return True
	#

	def _find(self, key:str, **kwargs):
		assert isinstance(key, str)

		if key in self.__dict__:
			data = self.__dict__[key]
			if isinstance(data, (list, tuple)):
				for e in data:
					if self.__isObj(e, kwargs):
						return e
			elif isinstance(data, FlexObject):
				if self.__isObj(data, kwargs):
					return data
		return NONE
	#

	def _findR(self, **kwargs):
		for key, data in self.__dict__.items():
			if isinstance(data, (list, tuple)):
				for e in data:
					if isinstance(e, FlexObject):
						if self.__isObj(e, kwargs):
							return e
				for e in data:
					if isinstance(e, FlexObject):
						r = e._findR(**kwargs)
						if r is not NONE:
							return r
			elif isinstance(data, FlexObject):
				if self.__isObj(data, kwargs):
					return data
				r = data._findR(**kwargs)
				if r is not NONE:
					return r
		return NONE
	#

	def _findAllR(self, **kwargs):
		for key, data in self.__dict__.items():
			if isinstance(data, (list, tuple)):
				for e in data:
					if isinstance(e, FlexObject):
						if self.__isObj(e, kwargs):
							yield e
				for e in data:
					if isinstance(e, FlexObject):
						yield from e._findAllR(**kwargs)
			elif isinstance(data, FlexObject):
				if self.__isObj(data, kwargs):
					yield data
				yield from data._findAllR(**kwargs)
	#

	def __str__(self):
		strings = []
		for k in sorted(self.__dict__.keys()):
			v = self.__dict__[k]
			if isinstance(v, (str, float, int, bool)):
				strings.append(k + "=" + repr(v))
			elif isinstance(v, (tuple, list)):
				strings.append(k + "=" + self.__toStrShort(v))
			elif isinstance(v, FlexObject):
				strings.append(k + "=...")
			else:
				strings.append(k + "=?")
		s = "F{ " + ", ".join(strings) + " }"
		return s
	#

	def __repr__(self):
		return self.__str__()
	#

	def __toStrShort(self, values):
		ret = []
		for i, v in enumerate(values):
			if i == 3:
				ret.append("...")
				break
			else:
				if isinstance(v, FlexObject):
					ret.append("F")
				else:
					ret.append(str(v))
		return "[ " + ", ".join(ret) + " ]"
	#

	def __getitem__(self, key):
		return self.__getattr__(key)
	#

	def __setitem__(self, key, value):
		return self.__setattr__(key, value)
	#

	"""
	def __setattr__(self, key, value):
		print("XX", value)
		""
		v = self.__dict__.get(key)
		if v is None:
			return NONE
		else:
			return v
		""
	#
	"""

	def __getattr__(self, key):
		if key in self.__dict__:
			return self.__dict__[key]
		else:
			return NONE
	#

	def __setattr__(self, key, value):
		if (value is None) or isinstance(value, _FlexNone):
			if key in self.__dict__:
				del self.__dict__[key]
		else:
			if isinstance(value, dict):
				self.__dict__[key] = FlexObject(value)
			elif isinstance(value, (list, tuple)):
				_ = []
				for item in value:
					if isinstance(item, dict):
						_.append(FlexObject(item))
					else:
						_.append(item)
				self.__dict__[key] = _
			else:
				self.__dict__[key] = value
	#

#












