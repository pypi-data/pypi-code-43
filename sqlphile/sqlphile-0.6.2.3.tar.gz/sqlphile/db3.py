import sqlite3
import json
import zlib
import sqlphile
from . import sql
from .dbtypes import DB_SQLITE3
from .skitai_compat import dispatch
from rs4 import asyncore
from rs4.cbutil import tuple_cb

class AttrDict (dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        
class open:
    def __init__ (self, path, dir = None, auto_reload = False, auto_closing = True):        
        self.closed = False
        self.auto_closing = auto_closing
        self.conn = None
        self.conn = sqlite3.connect (path, check_same_thread = False)        
                
        self.expt = None
        self._init (dir, auto_reload, DB_SQLITE3)   
    
    def _init (self, dir, auto_reload, engine):    
        self.create_cursor ()        
        self.sqlphile = sqlphile.SQLPhile (dir, auto_reload, engine = engine, conn = self)
    
    def create_cursor (self):    
        self.cursor = self.c = self.conn.cursor ()        
    
    def set_autocommit (self, flag = None):
       # flags: None (autocommit), DEFERRED, IMMEDIATE or EXCLUSIVE
       self.conn.isolation_level = flag
        
    def __enter__ (self):        
        return self
    
    def __exit__ (self, type, value, tb):        
        self.auto_closing and self.close ()

    def __del__ (self):
        self.close ()

    def __getattr__ (self, name):        
        try: 
            return getattr (self.c, name)
        except AttributeError:
            return getattr (self.sqlphile, name)

    def close (self):
        if self.conn and not self.closed:
            self.c.close ()
            self.conn.close ()
            self.closed = True

    def commit (self):    
        return self.conn.commit ()
    
    def rollback (self):    
        return self.conn.rollback ()    

    def serialize (self, obj):
        return zlib.compress (json.dumps (obj).encode ("utf8"))    
    
    def deserialize (self, data):
        return json.loads (zlib.decompress (data).decode ('utf8'))
    
    def blob (self, obj):
        return sqlite3.Binary (obj)    
    
    def field_names (self):
        return [x [0] for x in self.description]
        
    def as_dict (self, row, field_names = None):        
        return AttrDict (dict ([(f, row [i]) for i, f in enumerate (field_names or self.field_names ())]))
    
    def execute (self, sql, *args, **kargs):
        if isinstance (sql, (list, tuple)):
            sql = ";\n".join (map (str, sql)) + ";"              
        try:
            self.cursor.execute (str (sql), *args, **kargs)
        except:
            self.expt = asyncore.compact_traceback () [2]
            raise
        return self
    
    def fetchone (self, as_dict = False):
        try: 
            rows = self.fetchall (as_dict)
        except IndexError:
            return None    
        
    def fetchall (self, as_dict = False):
        return self.fetchmany (0, as_dict)
    
    def fetchmany (self, limit, as_dict = False):
        rows = limit and self.cursor.fetchmany (limit) or self.cursor.fetchall ()
        if not as_dict:
            return rows        
        field_names = self.field_names ()
        return [self.as_dict (row, field_names) for row in rows]
    
    def dispatch (self, *args, **kargs):
        return dispatch (self.fetchall (True), self.expt)

    def one (self, *args, **kargs):
        from skitai import exceptions
        
        rows = self.fetchall (True)
        if not rows:
            raise exceptions.HTTPError ("410 Partial Not Found")
        if len (rows) > 1:
            raise exceptions.HTTPError ("409 Conflict")    
        return rows [0]
    
    def fetch (self, *args, **kargs):
        return self.fetchall (True)
    

class open2 (open):
    def __init__ (self, conn, dir = None, auto_reload = False, auto_closing = True):
        self.closed = False
        self.conn = conn       
        self.auto_closing = auto_closing 
        self._init (dir, auto_reload, DB_SQLITE3)


# for faking skitai.was.db objects ---------------------------------------------
# single connection multi cursors

class open3 (open2):
    def __init__ (self, conn, dir = None, auto_reload = False):
        self.closed = False
        self.conn = conn   
        self.auto_closing = False
        self._init (dir, auto_reload, DB_SQLITE3)
        
    def _init (self, dir, auto_reload, engine):
        self.sqlphile = sqlphile.SQLPhile (dir, auto_reload, engine = engine, conn = self)
        self.cursor = self.c = None        
        self.cursors = []

    def __del__ (self):
        for each in self.cursors:
            each.close ()
        self.conn.close ()        

    def execute (self, *args, **kargs):
        cursor = self.conn.cursor ()
        self.cursors.append (cursor)
        return Executed (self, cursor, *args, **kargs)


class Executed (open):
    def __init__ (self, conn, cursor, *args, **kargs):
        self.conn = conn
        self.cursor = self.c = cursor        
        self.expt = None        
        self.meta = {}
        try:
            self.execute (*args, **kargs)
        except:            
            self.expt = asyncore.compact_traceback () [2] 
        else:    
            self.conn.commit ()           
    
    def __del__ (self):
        self.conn = None

    def set_callback (self, callback, reqid = None, timeout = 10):
        if reqid is not None:
            self.meta ["__reqid"] = reqid                        
        tuple_cb (self, callback)

    def maybe_reraise (self):
        self.conn = None # break back ref. for ensure call __del__
        if self.expt:
            raise self.expt

    def dispatch (self, *args, **kargs):
        self.conn = None
        return open.dispatch (self, *args, **kargs)

    def commit (self, *args, **kargs):
        self.maybe_reraise ()
    
    def fetch (self, *args, **kargs):
        self.maybe_reraise ()        
        return open.fetch (self, *args, **kargs)
    
    def one (self, *args, **kargs):
        self.maybe_reraise ()
        return open.one (self, *args, **kargs)

    # lower version compatable --------------------
    def wait (self, timeout = 10, *args, **karg):
        pass
    getswait = getwait = dispatch    
    wait_or_throw = commit
