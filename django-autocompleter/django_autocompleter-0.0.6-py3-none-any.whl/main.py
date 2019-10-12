import re
import json
import sys
import collections 
import sys, inspect
from abc import ABCMeta
try:
    from django.conf import settings
    from django.db import connection
except ImportError:
    raise ImportError("To run autocompeter version 0.0.1 you need Django")

try:
    from celery import shared_task
    from celery.result import AsyncResult
    static_or_class = staticmethod

except ImportError:
    
    def stub(f):
        def decorated_function(self, *args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    
    static_or_class = classmethod
    shared_task = stub
    AsyncResult = stub


class SearcherSerializer(object):
    
    __slots__ = ('list', 'res')
    
    __metaclass__ = ABCMeta
    
    def __init__(self, data=[], *args, **kwargs):
        self.fields = self.init_field()
        self.list = data
        self.res = {}
        self.__data()


    def init_field(self):
        try:
            return self.Meta.fields
        except AttributeError:
            return None        

    def __data(self):
        
        i = 0
        
        for i2 in self.list:
            data = {}
            
            for i1 in self.fields:
                
                data[i1] = i2.get(i1)
                self.res[i] = data
                
            del data
            
            i+=1

    
    @property
    def data(self, *args, **kwargs):
        return self.res


class Searcher(object):
    
    SQL = """SELECT * 
                FROM {}
                WHERE lower({}) ILIKE lower('%{}%') limit {};"""
    
    def __init__(self, *args, **kwargs):
        self.connection = connection 
        self.cursor = self.processor
        self.model_serializer = SearcherSerializer
        self.data = []
        self.limit = None
        self.table = None
        self.column = None
        self.value = None
        self.args = args
        self.kwargs = kwargs
    
    def dictfetchall(self, cursor):
        
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    def processor(self):
        
        cursor = self.connection.cursor()
        cursor.execute(self.SQL)
        self.data = self.dictfetchall(cursor)
        return cursor
    
    def init_params(self, *args, **kwargs):
        try:
            self.limit = settings.AUTOCOMPLETER['LIMIT']
            self.table = re.sub('[!@#$)(;:]', '', kwargs['table'])
            self.column = re.sub('[!@#$)(;:]', '', kwargs['column'])
            self.value = re.sub('[!@#$)(;:]', '', kwargs['value'])
            
            for name, obj in inspect.getmembers(sys.modules[
                    settings.AUTOCOMPLETER['SERILEZER_CLASSES']]):
                try:
                    if inspect.isclass(obj):
                        if issubclass(obj, self.model_serializer) and obj.Meta.model._meta.db_table == self.table:
                            self.model_serializer = obj 
                
                except AttributeError:
                    pass
        
        except KeyError:
            pass
    
    @static_or_class
    @shared_task
    def auctocompleter_run(cls, table, column, value):
        
        if not cls:
            cls = Searcher()
        
        cls.init_params(table=table, column=column, value=value)

        cls.SQL = cls.SQL.format(
                cls.table, cls.column, cls.value, cls.limit
            )
        cls.cursor().close()
        cls.connection.commit()
        return cls.model_serializer(cls.data).data


class Autocompleter(Searcher):
    
    def get(self, model, column, value):
        
        model = model()
        
        try:
            if settings.AUTOCOMPLETER['CELERY']:
                return  AsyncResult(str(
                            self.auctocompleter_run.delay(cls=False, table=model._meta.db_table, column=column, value=value)
                            )
                        ).get()
            
            return  self.auctocompleter_run(cls=self, table=model._meta.db_table, column=column, value=value)
        
        except KeyError:
            
            return  self.auctocompleter_run(cls=self, table=model._meta.db_table, column=column, value=value)

        except AttributeError:
            
            raise AttributeError('needs AUTOCOMPLETER parameters in project settings')
