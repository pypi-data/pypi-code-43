'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_column import BaseColumn
import adql


class AdqlColumn(BaseColumn):
    """
    classdocs
    """


    def __init__(self, adql_table, json_object=None, url=None):
        """
        Constructor
        """
        super().__init__(adql_table, json_object, url) 
             
        
    def type(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("adql").get("type","")
        return None
    
    
    def arraysize(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("adql").get("arraysize","")
        return None
     
     
    def ucd(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("adql").get("ucd","")
        return None
           
    
    def utype(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("adql").get("utype","")
        return None
    