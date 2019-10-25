from . import utils
from .f import F
from . import d
from .dbtypes import DB_PGSQL, DB_SQLITE3

OPS = {
	"gt": ">",
	"gte": ">=",
	"lt": "<",
	"lte": "<=",
	"neq": "<>",
	"eq": "=",
	"exact": "=",
	"regex": "~",
	"in": "IN",	
	"notin": "NOT IN",
	"isnull": "IS",
	"exists": "EXISTS",
	"nexists": "NOT EXISTS",
	"between": "BETWEEN",
	"contains": "LIKE",
	"startswith": "LIKE",
	"endswith": "LIKE",
	"ncontains": "NOT LIKE",
	"nstartswith": "NOT LIKE",
	"nendswith": "NOT LIKE",
	"all": "=",
}

class _Q:
	def __init__ (self, *args, **kargs):
		self._clause = None
		self._value = None
		self._void = False
		
		if kargs:
			assert len (kargs) == 1
			self.k, self.v = kargs.popitem ()
		elif len (args) == 0:
			self.k, self.v = "", None
		elif len (args) == 2:
			self.k, self.v = args	
		else:	
			self._clause = args [0]
		self._exclude = False
	
	def add_percent (self, val, pos = 0):
		if isinstance (val, F):
			val.add_percent (pos)
			return val
		val = val.replace ("%", "\\%")
		if pos == 0:
			return "%" + val + "%"
		elif pos == 1:	
			return "%" + val
		return val + "%"
			
	def render (self, engine = DB_PGSQL):
		if self._clause is not None:
			if self._exclude and self._clause:		
				self._clause = "NOT (" + self._clause + ")"				
				self._exclude = False				
			return self._clause
		
		elif self.v is None:
			self._clause = ""
			self._void = True
			return self._clause
			
		else:
			k, v = self.k, self.v
			ll = k.split ("__")
			if len (ll) == 1:
				fd, op = k, "eq"
			else:
				if ll [-1] in (OPS):
					fd, op = ".".join (ll [:-1]), ll [-1]
				else:
					fd, op = ".".join (ll), "eq"
					
			try:
				_op = OPS [op]
			except KeyError:
				raise TypeError ('Unknown Operator: {}'.format (op))
				
			_val = v
			_escape = True
			if op.endswith ("all"):
				fd, _val = "1", int (_val)
			elif op == "in":
				if isinstance (_val, (list, tuple)):
					_val = "({})".format (",".join ([d.toval (each, engine) for each in _val]))
				else:
					_val = "({})".format (str (_val))					
				_escape = False
			elif op.endswith ("contains"):				
				_val = self.add_percent (_val, 0)
			elif op.endswith ("endswith"):
				_val = self.add_percent (_val, 1)
			elif op.endswith ("startswith"):
				_val = self.add_percent (_val, 2)
			elif op == "between":
				_val = "{} AND {}".format (d.toval (_val [0], engine), d.toval (_val [1], engine))
				_escape = False				
			elif op == "isnull":
				if not _val: # False
					_op = "IS NOT"
				_val = None
			
			self._value = _escape and d.toval (_val, engine) or _val
			self._clause = "{} {} {}".format (fd, _op, self._value)		
			
		if self._exclude and self._clause:			
			self._clause =  "NOT (" + self._clause + ")"		
			self._exclude = False
		return self._clause	
	
	def _joinwith (self, op, b):
		if self and b:
			return Q ("({} {} {})".format (self, op, b))
		return self or b
	
	def __len__ (self):
		return (self._clause or self.v is not None) and 1 or 0
		
	def __str__ (self):
		return self.render ()
	
	def __repr__ (self):
		return "<sqlphile.q.Q_ object: {}>".format (self.render ())

	def __or__ (self, b):
		return self._joinwith ("OR", b)
		
	def __and__ (self, b):
		return self._joinwith ("AND", b)
	
	def __invert__ (self):
		self._exclude = True
		return self

def Q (*args, **kargs):
	clauses = []
	if kargs:
		assert len (kargs)
		for k, v in kargs.items ():
			clauses.append (_Q (**{k : v}))		
		
		if len (clauses) == 1:			
			return clauses [0]
		else:
			stack = []
			for clause in clauses:
				res = clause.render ()
				if res:
					stack.append (res)
			if stack:
				return _Q ("(" + " AND ".join (stack) + ")")
			else:
				return _Q ("")
	return _Q (*args)
	
class V (_Q):
	def __init__ (self, *args, **kargs):
		self._clause = None		
		self._value = None		
		if kargs:
			assert len (kargs) == 1
			self.k, self.v = kargs.popitem ()
		elif len (args) == 2:
			self.k, self.v = args
		elif not args or args [0] is None:
			self.k, self.v = "", None
		else:
			self.k, self.v = "__eq", args [0]
		self._exclude = False
	
	def render (self, engine = DB_PGSQL):
		if self.v is None:
			return "NULL"
		_Q.render (self, engine)
		return self._value
		
	def __str__ (self):
		return self.render ()		
		

def batch (**filters):
	Qs = []
	for k, v in filters.items ():		
		if v is None:
			continue
		Qs.append (Q (k, v))	
	return Qs
	