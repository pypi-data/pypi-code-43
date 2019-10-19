'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_object import BaseObject

class BaseResource(BaseObject):
    """
    classdocs
    """


    def __init__(self, account, json_object=None, url=None):
        """
        Constructor    
        """
        super().__init__(account, json_object, url) 
        

    def select_schemas(self):
        return
    
    
    def select_schema_by_ident(self, ident):
        return
    
    
    def select_schema_by_name(self, catalog_name, schema_name):
        return

