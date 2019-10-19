'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_schema import BaseSchema
import jdbc
import logging


class JdbcSchema(BaseSchema):
    """
    classdocs
    """


    def __init__(self, jdbc_resource, json_object=None, url=None):
        """
        Constructor
        """
        super().__init__(jdbc_resource, json_object, url) 
        self.jdbc_resource = jdbc_resource
    
    
    def resource(self):
        return self.jdbc_resource
        
        
    def catalog_name(self):
        if (self.json_object!=None):
            return self.json_object.get("fullname","")
        else:
            return None
    
    
    def select_tables(self):
        table_list = []
        json_list = self.get_json(self.json_object.get("tables",""))

        for column in json_list:
            table_list.append(jdbc.JdbcTable(json_object=column, jdbc_schema=self))
            
        return table_list
    
        
    def select_table_by_ident(self, ident):
        return jdbc.JdbcTable(jdbc_schema=self, url=ident)
    
    
    def select_table_by_name(self, table_name):
        """Get table by name
        
        Parameters
        ----------
        table_name: string, required
            The name of the Table being searched
         
        Returns
        -------
        JdbcTable: JdbcTable
            The JdbcTable found
        """
        response_json = {}
        try :
            response_json = self.get_json(self.url + "/tables/select", { "jdbc.table.name": table_name })                
        except Exception as e:
            logging.exception(e)   
            
        return jdbc.JdbcTable(json_object = response_json, jdbc_schema=self)    
    
                           
    def create_table(self, table_name):
        return
    
