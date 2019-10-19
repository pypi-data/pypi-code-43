'''
Created on Jul 22, 2013

@author: stelios
'''

try:
    
    import urllib.request
    import firethorn
    import json    
    import logging
    import os
    import urllib.request
except Exception as e:
    logging.exception(e)


class SetupEngine(object):
    """ Provides the low level methods to setup Firethorn services, including JDBC connections and importing IVOA or local resources
    """


    def __init__(self, json_file="", firethorn_base="", tap_included=True, firethorn_engine=None):
        self.json_file = json_file
        self.tap_included = tap_included
        self.jdbc_resources = {}
        self.firethorn_engine = firethorn_engine
        self.endpoint = firethorn_engine.endpoint
    
    
    def load_jdbc_resources(self, jdbc_resources_json):
        """
        Load JDBC resources into map from json_file
        """
        for jdbc_resource in jdbc_resources_json:
            _id = jdbc_resource.get("id","")
            name = jdbc_resource.get("name","")
            if  jdbc_resource["datauser" ]=="{datauser}":
                datauser = os.getenv('datauser', "")
            else:
                datauser = jdbc_resource["datauser"]
                
            if  jdbc_resource["datapass" ]=="{datapass}":
                datapass = os.getenv('datapass', "")
            else:
                datapass = jdbc_resource["datapass"]
                
            if  jdbc_resource["datahost" ]=="{datahost}":
                datahost = os.getenv('datahost', "")
            else:
                datahost = jdbc_resource["datahost"]       
                                     
            jdbc_resource["jdbc_object"] = self.firethorn_engine.create_jdbc_resource(name, jdbc_resource["datadata"], jdbc_resource["datacatalog"], jdbc_resource["datatype"], datahost, datauser, datapass)
            self.jdbc_resources[_id] = jdbc_resource
  
        
    def create_adql_resource(self, resource):
        """
        Create an ADQL Resource for the resource params passed from the json_file
        """                     
        name = resource.get("name","")
        _id = resource.get("id","")
        adql_schemas = resource.get("Schemas","")
        
        tap_name= name + " ADQL resource"
        new_adql_resource = self.firethorn_engine.create_adql_resource(tap_name)
        
        for schema in adql_schemas:
            schema_name = schema.get("adqlschema")
            print ("Importing " + schema_name)
            jdbc_resource_dict = self.jdbc_resources.get(schema.get("jdbcid"))
            jdbc_resource_object = jdbc_resource_dict.get("jdbc_object")
            jdbc_schema = jdbc_resource_object.select_schema_by_name(
                schema.get("jdbccatalog"),
                schema.get("jdbcschema")
            )
            
            if (jdbc_schema!=None):
                metadoc = schema.get("metadata").get("metadoc")
                metadoc_catalog_name = schema.get("metadata").get("catalog")
                adql_schema = new_adql_resource.import_jdbc_schema(
                    jdbc_schema,
                    metadoc_catalog_name,
                    metadoc=metadoc
                    )
                
        return new_adql_resource


    def create_tap_service(self, new_adql_resource):
        """
        Create a TAP service for a given resource
        """
        
        req = urllib.request.Request( self.endpoint + "/tap/"+ new_adql_resource.ident() + "/generateTapSchema", headers=new_adql_resource.account.get_identity_as_headers())
        response = urllib.request.urlopen(req)
        response.close()
        return self.endpoint + "/tap/"+ new_adql_resource.ident() + "/"

    
    def setup_resources(self):
        """
        For every AdqlResource in the json_file, setup the Resources (and TAP service if tap_included=true)
        """
        
        
        if (self.json_file.lower().startswith("http")):
            with urllib.request.urlopen(self.json_file) as url:
                json_obect = json.loads(url.read().decode())
        else :
            data = open(self.json_file)
            json_obect = json.load(data)
    
        name = json_obect.get("name")
        adql_resources_json = json_obect.get("AdqlResources")
        jdbc_resources_json = json_obect.get("JdbcResources")

        self.load_jdbc_resources(jdbc_resources_json)
        for resource in adql_resources_json:
            new_adql_resource = self.create_adql_resource(resource)
            if (self.tap_included):
                tap = self.create_tap_service(new_adql_resource)        
                print ("TAP Service available at: " + tap)
            print ("")
            

if __name__ == "__main__":
    ft = firethorn.Firethorn(endpoint=firethorn.config.endpoint)
    ft.login(firethorn.config.adminuser, firethorn.config.adminpass, firethorn.config.admingroup)
    ft.firethorn_engine.load_resources("../data/vsa-tap.json")
    #sEng = SetupEngine(json_file="https://raw.githubusercontent.com/stvoutsin/firethorn.py/dev/firethorn/data/osa-tap.json", firethorn_base="http://localhost:8081/firethorn")
    #sEng.setup_resources()
