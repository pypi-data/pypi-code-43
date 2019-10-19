'''
Created on Nov 4, 2017

@author: stelios
'''
import models
from models.table import Table

class Schema(object):
    """Column class, equivalent to a Firethorn ADQL Column
    """


    def __init__(self, adql_schema=None):
        self.__adql_schema = adql_schema
        
        
    def _get_adql_schema(self):
        return self.__adql_schema  
    
    
    def name(self):
        return self.__adql_schema.name()
        
        
    def get_table_names (self):
        adql_tables=self.__adql_schema.select_tables()
        table_name_list = [table.name() for table in adql_tables]
        return table_name_list
    
    
    def get_tables(self):
        adql_tables=self.__adql_schema.select_tables()
        table_list = [Table(table) for table in adql_tables]
        return table_list
    
    
    def get_table_by_name(self, name):
        return models.table.Table(self.__adql_schema.select_table_by_name(name))
                                
                                
    def __str__(self):
        """Get class as string
        """
        return self.__adql_schema
