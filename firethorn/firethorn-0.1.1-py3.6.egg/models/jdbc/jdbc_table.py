'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_table import BaseTable
import jdbc
import logging


class JdbcTable(BaseTable):
    """
    classdocs
    """


    def __init__(self, jdbc_schema, json_object=None, url=None):
        """
        Constructor
        """
        self.jdbc_schema = jdbc_schema
        super().__init__(jdbc_schema, json_object, url) 
        
        
    def resource(self):
        if (self.jdbc_schema!=None):
            return self.jdbc_schema.resource()
        else:
            return None 
    
    
    def schema(self):
        return self.jdbc_schema
        
        
    def select_columns(self):
        column_list = []
        json_list = self.get_json(self.json_object.get("columns",""))

        for column in json_list:
            column_list.append(jdbc.JdbcColumn(json_object=column, jdbc_table=self))
            
        return column_list
    
    
    def select_column_by_ident(self, ident):
        return jdbc.JdbcColumn(jdbc_table=self, url=ident)
 
    
    def select_column_by_name(self, column_name):
        """Get column by name
        
        Parameters
        ----------
        column_name: string, required
            The name of the Table being searched
         
        Returns
        -------
        column_list: list
            List of table names
        """
        response_json = {}
        try :
            response_json = self.get_json(  self.url + "/columns/select", { "jdbc.table.column.select.name": column_name })
        except Exception as e:
            logging.exception(e)   
            
        return jdbc.JdbcColumn(json_object = response_json, jdbc_table=self)    
                         
                         
    def create_column(self, column_name):
        return
    
    