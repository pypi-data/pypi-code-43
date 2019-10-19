'''
Created on Nov 4, 2017

@author: stelios
'''

try:
    import simplejson as json
except ImportError:
    import json
import warnings
from models.column import Column
from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

class Table(object):
    """Table class, equivalent to a Firethorn ADQL Table
    """


    def __init__(self, adql_table=None):
        self.__adql_table = adql_table
        
        
    def name(self):
        return self.__adql_table.name()   

        
    def get_column_names (self):
        adql_columns=self.__adql_table.select_columns()
        column_name_list = [col.name() for col in adql_columns]
        return column_name_list
    
    
    def get_columns (self):
        adql_columns=self.__adql_table.select_columns()
        column_list = [Column(col) for col in adql_columns]
        return column_list
    
            
    def get_column_by_name(self, name):
        return Column(self.__adql_table.select_column_by_name(name))
    
    
    def as_astropy (self, limit=True):
        """Get Astropy table
                             
        Returns
        -------
        astropy_table: Astropy.Table
            Table as Astropy table 
        """
        if (self.__adql_table!=None):
            return self.__adql_table.as_astropy()  
        else:
            return None     
    
    
    def rowcount (self):
        """Get Row count
        
        Returns
        -------
        rowcount: integer
            Count of rows  
        """  
        
        if (self.__adql_table!=None):
            return self.__adql_table.count()  
        else:
            return None        
          
    
                        
    def __str__(self):
        """Get class as string
        """
        return self.__adql_table
