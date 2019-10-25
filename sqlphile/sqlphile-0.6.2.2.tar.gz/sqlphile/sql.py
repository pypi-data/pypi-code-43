from . import utils
from .q import Q, V, batch, _Q
from .d import toval, D
from copy import deepcopy
from .dbtypes import DB_PGSQL, DB_SQLITE3
from .skitai_compat import EMPTY

class SQL:
    def __init__ (self, template, engine = DB_PGSQL, conn = None, check_filter = False):    
        self._template = template        
        self._engine = engine
        self._conn = conn
        self._check_filter = check_filter
        self._filters = []
        self._limit = 0
        self._offset = 0
        self._order_by = None
        self._group_by = None
        self._having = None
        self._returning = None
        self._insert_into = None
        self._cte = []
        self._feed = {}
        self._data = {}
        self._unionables = []
        self._transact = False
        self._explicit_empty = False        
    
    def branch (self, conn = None):
        new = self.__class__ (self._template, self._engine, conn or self._conn)
        new._filters = deepcopy (self._filters)
        new._limit = deepcopy (self._limit)
        new._offset = deepcopy (self._offset)
        new._order_by = deepcopy (self._order_by)
        new._group_by = deepcopy (self._group_by)
        new._having = deepcopy (self._having)
        new._returning = deepcopy (self._returning)
        new._insert_into = deepcopy (self._insert_into)
        new._cte = deepcopy (self._cte)
        new._feed = deepcopy (self._feed)
        new._data = deepcopy (self._data)
        new._explicit_empty = self._explicit_empty
        new._check_filter = self._check_filter
        return new 
            
    @property
    def query (self):
        return self.as_sql ()
    
    def addD (self, prefix, D_):
        assert prefix != "this", "Cannot use data prefix `this`"
        D_.encode (self._engine)
        self._data [prefix] = D_
        
    def render (self):
        return self.as_sql ()
        
    def __str__ (self):
        return self.as_sql ()
                        
    def __getitem__(self, key):
        key.start and self.offset (key.start)
        if key.stop:
            self.limit (key.stop - (key.start or 0))
        return self

    def execute (self):
        if self._explicit_empty:
            return self
        if self._check_filter:
            assert self._filters, "No filter for modification, if you want to modify anyway use .all ()"
        return self._conn.execute (self.query) or self        
    
    def all (self):
        self._filters.append ("1 = 1")
        return self
                        
    def exclude (self, *Qs, **filters):
        g = []
        for q in Qs + tuple (batch (**filters)):
            if not q:
                continue
            if not isinstance (q, str):
                q.render (self._engine)
            g.append (str (q))

        cluses = " AND ".join (g)    
        if cluses:
            self._filters.append ("NOT (" + cluses + ")")        
        return self
    
    def into (self, table_spec):
        self._insert_into = "INSERT INTO " + table_spec
        return self

    def returning (self, *args):
        self._returning = "RETURNING " + ", ".join (args)
        return self
    
    def filter (self, *Qs, **filters):
        for q in Qs + tuple (batch (**filters)):
            if not q:
                continue
            if not isinstance (q, str):                    
                q.render (self._engine)            
            self._filters.append (str (q))        
        return self
    
    def having (self, cond):
        self._having = "HAVING " + cond
        return self
        
    def order_by (self, *by):
        self._order_by = utils.make_orders (by)
        return self
    
    def group_by (self, *by):
        self._group_by = utils.make_orders (by, "GROUP")
        return self
        
    def limit (self, val):
        if val == 0:
            self._explicit_empty = True
        self._limit = "LIMIT {}".format (val)
        return self
    
    def offset (self, val):
        self._offset = "OFFSET {}".format (val)
        return self

    def with_ (self, alias, sql):
        self._cte.append ("{} AS ({})".format (alias, str (sql)))
        return self

    def data (self, __donotusethisvariable__ = None, **karg):        
        if __donotusethisvariable__:
            d = __donotusethisvariable__
            d.update (karg)
        else:
            d = karg
            
        for k, v in d.items ():
            if isinstance (v, D):
                self.addD (k, v)            
            else:    
                self._data [k] = toval (v, self._engine)
        return self
        
    def feed (self, **karg):
        for k, v in karg.items ():
            if isinstance (v, D):
                self.addD (k, v)
            else:            
                # Q need str()
                if isinstance (v, _Q) and not v:
                    # for ignoring
                    v = "1 = 1"                    
                elif isinstance (v, (V, _Q)):
                    v.render (self._engine)                    
                self._feed [k] = str (v)
        return self
    
    def as_sql (self):
        raise NotImplementedError
    
    def tran (self):
        self._transact = True

    def intersect (self, sql):
        self._unionables.append ((sql, "INTERSECT"))
        return self

    def except_ (self, sql):
        self._unionables.append ((sql, "EXCEPT"))
        return self

    def union (self, sql):        
        self._unionables.append ((sql, "UNION"))
        return self

    def union_all (self, sql):
        self._unionables.append ((sql, 'UNION ALL'))
        return self

    def maybe_union (self, current):
        n_q = len (self._unionables)
        qs = []
        qs.append (current)        
        for idx, (sql, type) in enumerate (self._unionables):
            qs.append (type)
            qs.append (str (sql))
        r = "\n".join (qs)
        if self._transact:
            return "BEGIN TRANSACTION;\n" + r + ";\nCOMMIT;"
        return r    

    # only work if self._explicit_empty ---------------------------
    def fetchall (self, *args, **kargs):
        return []

    def fetchmany (self, *args, **kargs):
        return []

    def fetchone (self, *args, **kargs):
        return

    def dispatch (self, *args, **kargs):
        return EMPTY

    def one (self, *args, **kargs):
        return EMPTY.one (*args, **kargs)
        
    def fetch (self, *args, **kargs):
        return EMPTY.fetch (*args, **kargs)


class TemplateParams:
    def __init__ (self, this, data):
        self.filter = " AND ".join ([f for f in this._filters if f])
        self.limit = this._limit
        self.offset = this._offset
        self.group_by = this._group_by
        self.order_by = this._order_by
        self.having = this._having
        self.returning = this._returning
        self.insert_into = this._insert_into
        self.cte = this._cte

        self.columns = data.columns
        self.values = data.values
        self.pairs = data.pairs

class SQLTemplateRenderer (SQL):
    def __call__ (self, **karg):
        return self.feed (**karg)
    
    def as_sql (self):
        data = utils.D (**self._data)
        this = TemplateParams (self, data)
        self._feed.update (self._data)
        self._feed ["this"] = this
        if self._template.find ("{_") != -1:
            compatables = {
                "_filters": this.filter,
                "_limit": this.limit,
                "_offset": this.offset,
                "_order_by": this.order_by,
                "_group_by": this.group_by,
                "_having": this.having,
                "_returning": this.returning,
                "_columns": data.columns, 
                "_values": data.values, 
                "_pairs": data.pairs
            }
            self._feed.update (compatables)
        r = self._template.format (**self._feed)
        return self.maybe_union (r)    

class SQLComposer (SQL):    
    def __init__ (self, template, engine = DB_PGSQL, conn = None, check_filter = False):
        SQL.__init__ (self, template, engine, conn, check_filter)
        self._joins = []
    
    def branch (self, conn = None):
        new = SQL.branch (self, conn)
        new._joins = deepcopy (self._joins)
        return new
                
    def get (self, *columns):
        self._feed ["select"] = ", ".join (columns)
        return self
    
    def _join (self, jtype, obj, alias, on, *Qs, **filters):
        if alias:
            if alias.find (".") != -1:
                Qs = (alias,) + Qs
                alias = ''
            else:
                alias = ' AS {}'.format (alias)

        _filters = []
        for q in (on,) + Qs + tuple (batch (**filters)):
            if not q:
                continue            
            if not isinstance (q, str):
                q.render (self._engine)
            _filters.append (str (q))
        _filters = " AND ".join ([f for f in _filters if f])
        if not isinstance (obj, str):
            # SQL
            obj = "({})".format (obj)
        self._joins.append (
            "{} {}{} ON {}".format (jtype, obj, alias, _filters)
        )
        return self
    
    def from_ (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("FROM", obj, alias, on, *Qs, **filters)
    
    def join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("INNER JOIN", obj, alias, on, *Qs, **filters)
    
    def left_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("LEFT OUTER JOIN", obj, alias, on, *Qs, **filters)
    
    def right_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("RIGHT OUTER JOIN", obj, alias, on, *Qs, **filters)
    
    def full_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("FULL OUTER JOIN", obj, alias, on, *Qs, **filters)

    def cross_join (self, obj, alias = '', on = None, *Qs, **filters):
        return self._join ("CROSS JOIN", obj, alias, *Qs, on, **filters)    
        
    def as_sql (self):
        data = utils.D (**self._data)
        self._feed ["this"] = data
        if self._template.find ("{_") != -1:
            compatables = {
                "_columns": data.columns, 
                "_values": data.values, 
                "_pairs": data.pairs
            }
            self._feed.update (compatables)
        sql = [
            self._template.format (**self._feed)
        ]
        for join in self._joins:
            sql.append (join)
        _filters = [f for f in self._filters if f]
        _filters and sql.append ("WHERE " + " AND ".join (_filters))
        if self._group_by:
            sql.append (self._group_by)
            self._having and sql.append (self._having)
        self._order_by and sql.append (self._order_by)
        self._limit and sql.append (self._limit)
        self._offset and sql.append (self._offset)
        self._returning and sql.append (self._returning)
        if self._insert_into:
            sql.insert (0, self._insert_into)
        if self._cte:
            sql.insert (0, "WITH " + ", ".join (self._cte))
        r = "\n".join (sql)
        return self.maybe_union (r)
