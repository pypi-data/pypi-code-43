'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_object import BaseObject

class BaseTable(BaseObject):
    """
    classdocs
    """


    def __init__(self, parent, json_object=None, url=None):
        """
        Constructor
        """
        self.parent = parent
        super().__init__(account=self.parent.account, json_object=json_object, url=url) 
        
        
    def resource(self):
        return self.parent.resource()
    
    
    def schema(self):
        return self.parent
    
    
    def select_columns(self):
        return self.get_json(self.json_object.get("columns",""))
    
