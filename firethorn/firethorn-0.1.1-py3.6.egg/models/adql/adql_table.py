'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_table import BaseTable
import adql
import logging
from astropy.table import Table as astropy_Table
import config as config


class AdqlTable(BaseTable):
    """
    classdocs
    """


    def __init__(self, adql_schema, json_object=None, url=None):
        """
        Constructor
        """
        super().__init__(adql_schema, json_object, url) 

        
    def select_columns(self):
        column_list = []
        json_list = self.get_json(self.url + "/columns/select")

        for column in json_list:
            column_list.append(adql.AdqlColumn(json_object=column, adql_table=self))
            
        return column_list
    
    
    def select_column_by_ident(self, ident):
        return adql.AdqlColumn(adql_table=self, url=ident)
 
    
    def select_column_by_name(self, column_name):
        """Get table by name
        
        Parameters
        ----------
        table_name: string, required
            The name of the Table being searched
         
        Returns
        -------
        table_list: list
            List of table names
        """
        response_json = {}
        try :
            response_json = self.get_json(  self.url + "/columns/select", { "adql.column.name": column_name })
        except Exception as e:
            logging.exception(e)   
            
        return adql.AdqlColumn(json_object = response_json, adql_table=self)    
                   
    
    def create_adql_column(self, column_name):
        return
    
    
    def count(self):
        """Get Row count
        
        Returns
        -------
        rowcount: integer
            Count of rows  
        """  
        rowcount=-1
        
        try:
            if (self.json_object!=None):  
                rowcount = self.json_object.get("metadata",[]).get("adql",[]).get("count",None)
        except Exception as e:
            logging.exception(e) 
               
        return rowcount
    
    
    def as_astropy (self, limit=True):
        """Get Astropy table
                             
        Returns
        -------
        astropy_table: Astropy.Table
            Table as Astropy table 
        """
        if (limit):
            if (self.count()>config.maxrows):
                raise Exception ("Max row limit exceeded")
            else :
                return astropy_Table.read(self.url + "/votable", format="votable",use_names_over_ids=True)
        else:
            return astropy_Table.read(self.url + "/votable", format="votable", use_names_over_ids=True)        
 