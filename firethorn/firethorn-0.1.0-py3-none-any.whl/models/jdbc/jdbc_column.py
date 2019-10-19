'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_column import BaseColumn
import jdbc


class JdbcColumn(BaseColumn):
    """
    classdocs
    """


    def __init__(self, jdbc_table, json_object=None, url=None):
        """
        Constructor
        """
        super().__init__(jdbc_table, json_object, url) 
        
        
    def type(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("jdbc","")!=""):
                return self.json_object.get("meta").get("jdbc").get("type","")
        return None
    
    
    def size(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("jdbc").get("size","")
        return None
     
     
    def ucd(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("adql").get("ucd","test")
        return "test"
           
    
    def utype(self):    
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("adql").get("utype","")
        return None
    