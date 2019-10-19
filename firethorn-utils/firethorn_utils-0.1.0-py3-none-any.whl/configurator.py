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
except Exception as e:
    logging.exception(e)


class Configurator(object):
    """ Provides the low level methods to setup Firethorn services, including JDBC connections and importing IVOA or local resources
    """


    def __init__(self, firethorn_object):
        self.firethorn_object = firethorn_object
        self.endpoint = firethorn_object.firethorn_engine.endpoint
        self.tap_included = True
        self.jdbc_resources = {}
        self.ivoa_resources = {}
        
    
    def load_jdbc_resources(self, jdbc_resources_json):
        """
        Load JDBC resources into map from json_file
        """
        for jdbc_resource in jdbc_resources_json:
            
            _id = jdbc_resource.get("id","")
            name = jdbc_resource.get("name","")
            datauserstring = jdbc_resource["datauser"].strip()
            datapasstring = jdbc_resource["datapass"].strip()
            datahoststring = jdbc_resource["datahost"].strip()
          
            if datauserstring.strip().startswith("{"):
                datauser = os.getenv(datauserstring[datauserstring.find("{")+1:datauserstring.find("}")], "")
            else:
                datauser = jdbc_resource["datauser"]
                
            if datapasstring.startswith("{"):
                datapass = os.getenv(datapasstring[datapasstring.find("{")+1:datapasstring.find("}")], "")
            else:
                datapass = jdbc_resource["datapass"]
                
            if datahoststring.startswith("{"):
                datahost = os.getenv(datahoststring[datahoststring.find("{")+1:datahoststring.find("}")], "")
            else:
                datahost = jdbc_resource["datahost"]       
                                     
            jdbc_resource["jdbc_object"] = self.firethorn_object.firethorn_engine.create_jdbc_resource(name, jdbc_resource["datadata"], jdbc_resource["datacatalog"], jdbc_resource["datatype"], datahost, datauser, datapass)
            self.jdbc_resources[_id] = jdbc_resource
  

    def load_ivoa_resources(self, ivoa_resources_json):
        """
        Load JDBC resources into map from json_file
        """
        for resource in ivoa_resources_json:
            new_ivoa_resource = {}
            _id = resource.get("id","")
            name = resource.get("name","")
            url = resource.get("url","")
            ivoa_resource = self.firethorn_object.firethorn_engine.create_ivoa_resource(url=url, ivoa_space_name=name)
            ivoa_resource.import_ivoa_metadoc(resource.get("metadoc"))
            new_ivoa_resource["jdbc_object"] = ivoa_resource
            self.ivoa_resources[_id] = new_ivoa_resource

        
    def create_adql_resource(self, resource):
        """
        Create an ADQL Resource for the resource params passed from the json_file
        """                     
        name = resource.get("name","")
        _id = resource.get("id","")
        adql_schemas = resource.get("Schemas","")
        
        tap_name = name + " ADQL resource"
        new_adql_resource = self.firethorn_object.firethorn_engine.create_adql_resource(tap_name)
        
        for schema in adql_schemas:
            
            if (schema.get('ivoaid',"")!=""):
                ivoa_resource_dict = self.ivoa_resources.get(schema.get("ivoaid"))
                ivoa_resource_object = ivoa_resource_dict.get("jdbc_object")
                ivoa_schema = ivoa_resource_object.select_schema_by_name(schema.get("ivoaschema"))
                print ("Importing IVOA Schema: " + schema.get("ivoaschema"))

                if (ivoa_schema!=None):
                    new_adql_resource.import_ivoa_schema(
                        ivoa_schema,
                        schema.get("adqlschema")
                        )
                    
            elif (schema.get('jdbcid',"")!=""):
                
                schema_name = schema.get("adqlschema")
                print ("Importing JDBC Schema: " + schema_name)
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
        try:
            response = urllib.request.urlopen(req)
            response.close()
        except Exception as e:
            logging.exception(e)
        return self.endpoint + "/tap/"+ new_adql_resource.ident() + "/"

    
    def load_resources(self, json_file):
        """
        For every AdqlResource in the json_file, setup the Resources (and TAP service if tap_included=true)
        """
        
        
        if (json_file.lower().startswith("http")):
            with urllib.request.urlopen(json_file) as url:
                json_obect = json.loads(url.read().decode())
        else :
            with open(json_file) as f:
                json_obect = json.load(f)

    
        name = json_obect.get("name")
        adql_resources_json = json_obect.get("AdqlResources", [])
        jdbc_resources_json = json_obect.get("JdbcResources", [])
        ivoa_resources_json = json_obect.get("IvoaResources", [])


        self.load_jdbc_resources(jdbc_resources_json)
        self.load_ivoa_resources(ivoa_resources_json)
        
        for resource in adql_resources_json:
            new_adql_resource = self.create_adql_resource(resource)
            if (self.tap_included):
                tap = self.create_tap_service(new_adql_resource)        
                print ("TAP Service available at: " + tap)
            print ("")
            
