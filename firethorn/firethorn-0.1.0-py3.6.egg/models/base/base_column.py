'''
Created on Feb 8, 2018

@author: stelios
'''
from base.base_object import BaseObject

class BaseColumn(BaseObject):
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
        if (self.json_object!=None):
            return self.table().resource()
        else:
            return None 
        

    def schema(self):
        if (self.json_object!=None):
            return self.table().schema()
        else:
            return None 
        
    
    def table(self):
        return self.parent 


    def type(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("jdbc","")!=""):
                return self.json_object.get("meta").get("jdbc").get("type","")
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
        return ""
           
    
    def utype(self):
        if (self.json_object.get("meta","")!=""):
            if (self.json_object.get("meta").get("adql","")!=""):
                return self.json_object.get("meta").get("adql").get("utype","")
        return None
    

    