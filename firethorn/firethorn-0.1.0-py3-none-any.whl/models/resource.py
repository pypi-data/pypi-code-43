import logging
from models.query import Query
import urllib
import json
from models.adql import adql_resource
from models.schema import Schema

class Resource(object):
    """
    Resource client class
         
    Attributes
    ----------
      
    adql_resource: AdqlResource, optional
        The AdqlResource behind the Resource object
    
    url: String, optional
        A String representing the URL of the resource
        

    """

    def __init__(self, adql_resource=None, url=None):
        self.url = url             
        self.__adql_resource = adql_resource
        return        

    
    def add_schema(self, schema=None, schema_name=None):
        """
        Add a Schema into the resource
        """
        
        if schema==None:
            schema = self.__adql_resource.select_schema_by_name(schema_name)
        else :
            schema = schema._get_adql_schema()
            
        self.__adql_resource.import_adql_schema(schema, schema_name)

    
    def get_schema_by_name(self, schema_name=None):
        """
        Get a copy of the schema by name
        """
        adql_schema = self.__adql_resource.select_schema_by_name(schema_name)
        return Schema(adql_schema=adql_schema)

    
    def query(self, query="", mode="SYNC"):
        """        
        Run a query on the imported resources
        
        Parameters
        ----------
        query : str, required
            The query string
            
        Returns
        -------
        query : `Query`
            The created Query
        """
        adql_query = self.__adql_resource.create_query(query)
        return Query(adql_query=adql_query, mode=mode)


    def get_schemas(self):
        """Get list of schemas in a resource
        """

        schemas = []
        
        try:
            adql_schemas = self.__adql_resource.select_schemas()              
            for adql_schema in adql_schemas:
                schemas.append(Schema(adql_schema=adql_schema))

        except Exception as e:
            logging.exception(e)

        return schemas   
    
    
    def get_schema_names(self):
        """Get list of schemas in a resource
        """

        schemas = []
        
        try:
            adql_schemas = self.__adql_resource.select_schemas()              
            schemas = [adql_schema.name() for adql_schema in adql_schemas]

        except Exception as e:
            logging.exception(e)

        return schemas   
    

    

