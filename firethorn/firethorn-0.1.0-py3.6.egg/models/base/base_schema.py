'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_object import BaseObject

class BaseSchema(BaseObject):
    """
    classdocs
    """


    def __init__(self, parent, json_object=None, url=None):
        """
        Constructor
        """
        self.parent = parent
        super().__init__(parent.account, json_object, url) 
        
        
    def resource(self):
        return self.parent
    
    
    def name(self):
        return self.schema_name()
    
    
    def schema_name(self):
        if (self.json_object!=None):
            return self.json_object.get("fullname","")
        else:
            return None
        
            
    def select_tables(self):
        return
    

    def select_table_by_ident(self, ident):
        return
    
    
    def select_table_by_name(self, table_name):
        return
    
