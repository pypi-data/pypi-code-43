'''
Created on Feb 8, 2018

@author: stelios
'''

try:
    from base.base_resource import BaseResource
    import ivoa
    import urllib
    import json
    import config as config
    import logging
    import io
    import uuid
    import requests
except Exception as e:
    logging.exception(e)


class IvoaResource(BaseResource):
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
            schema_list.append(ivoa.IvoaSchema(json_object=schema, ivoa_resource=self))
        
        return schema_list
    
    
    def select_schema_by_ident(self, ident):
        return ivoa.IvoaSchema(url=ident,  ivoa_resource=self)
    
    
    def select_schema_by_name(self,schema_name):
        response_json = {}
        try :
            response_json = self.get_json(self.url + "/schemas/select", {config.ivoa_schema_select_by_name_param : schema_name })
        except Exception as e:
            logging.exception(e)      
            
        return ivoa.IvoaSchema(json_object = response_json, ivoa_resource=self)  
    

    def import_ivoa_metadoc(self, metadoc):
        """Import IVOA metadoc
        
        Parameters
        ----------
        metadoc: string, required
            Metadoc location

            
        Returns
        -------
        self: IvoaResource
            Copy of this IVOA resource
        
        """
      
        try:
            if (metadoc.lower().startswith("http://") or metadoc.lower().startswith("https://")):
                rsrc = requests.get(metadoc)
                files = {'vosi.tableset':  rsrc.content  }
            else :
                files = {'vosi.tableset':  open(metadoc,'rb') }
               
            
            urldst = self.url + "/vosi/import"
            requests.post(urldst, files=files, headers=self.account.get_identity_as_headers())
                       
        except Exception as e:
            logging.exception(e)
     
        return self
    