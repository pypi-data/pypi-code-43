'''
Created on Feb 8, 2018

@author: stelios
'''

import urllib
import json
import logging
import os
import json

class BaseObject(object):
    """
    classdocs
    """


    def __init__(self, account, json_object=None, url=None ):
        """
        Constructor
        """
        self.json_object = json_object
        self.url = url
        self.account = account
        if (self.json_object==None and self.url!=None):
            self.json_object = self.get_json(self.url) 
             
        
        
    @property
    def url(self):
        return self.__url
        
        
    @url.setter
    def url(self, url):
        self.__url= url 
        if (self.json_object!=None and url==None):
            self.__url = self.json_object.get("self",None)           


    def name(self):
        if (self.json_object==None):
            if (self.url!=None):
                self.json_object = self.get_json(self.url)
                return self.json_object.get("name","")
        else:
            return self.json_object.get("name","")
        
        
    def ident(self):
        if (self.json_object==None):
            if (self.url!=None):
                self.json_object = self.get_json(self.url)
                return os.path.basename(self.json_object.get("self",""))
        else:
            return os.path.basename(self.json_object.get("self",""))
        
        
    def owner(self):
        if (self.json_object==None):
            if (self.url!=None):
                self.json_object = self.get_json(self.url)
                return self.json_object.get("owner","")
        else:
            return self.json_object.get("owner","")


    def get_json(self, ident, postparams=None):
        """Select a JSON HTTP resource
        
        Parameters
        ----------
        ident: string, required
            The URL being queried

        """
        
        data=None
        json_result = {}
        req = None
        
        if postparams!=None:
            data = urllib.parse.urlencode(postparams).encode("utf-8")
        
        try :
            req = urllib.request.Request( ident, headers=self.account.get_identity_as_headers())
            
            with urllib.request.urlopen( req, data) as response:
                json_result =  json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logging.exception(e)
            
        return json_result
    

    def refresh(self):
        self.json_object = self.get_json(self.url)
      

    def __str__(self):
        """ 
        Print Class as string
        """
         
        return str(json.dumps( self.json_object ,indent=2))
