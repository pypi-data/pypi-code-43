'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_resource import BaseResource
import urllib
import config as config
import json
import logging
import jdbc


class JdbcResource(BaseResource):
    """
    classdocs
    """


    def __init__(self, account, json_object=None, url=None):
        """
        Constructor    
        """
        super().__init__(account, json_object, url) 
        

    def select_schemas(self):
        schema_list = []
        json_list = self.get_json(self.url + "/schemas/select")
        
        for schema in json_list:
            schema_list.append(jdbc.JdbcSchema(json_object=schema, jdbc_resource=self))
        
        return schema_list
    
    
    def select_schema_by_ident(self, ident):
        return jdbc.JdbcSchema(url=ident, jdbc_resource=self)
    
    
    def select_schema_by_name(self, catalog_name, schema_name):
        response_json = {}
        try :
            response_json = self.get_json(self.url + "/schemas/select", {config.jdbc_schema_catalog : catalog_name, config.jdbc_schema_schema : schema_name })                
        except Exception as e:
            logging.exception(e)      
            
        return jdbc.JdbcSchema(json_object = response_json, jdbc_resource=self)
    
    
    def create_schema(self, catalog_name, schema_name):
        return
    
    