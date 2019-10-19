'''
Created on Jul 22, 2013

@author: stelios
'''

try:
    
    import json
    import logging
    from datetime import datetime
    import config as config
    import urllib.request
    from jdbc.jdbc_resource import JdbcResource
    from models.jdbc.jdbc_schema import JdbcSchema
    import models as models
    from core.setup_engine import SetupEngine
    from core.account import Account
    
except Exception as e:
    logging.exception(e)


class FirethornEngine(object):
    """ Provides the low level methods to setup Firethorn services, including JDBC connections and importing IVOA or local resources
    """


    def __init__(self, endpoint = "" , account = None, driver="net.sourceforge.jtds.jdbc.Driver",**kwargs):
        self.driver = driver
        self.endpoint = endpoint
        if (account==None):
            self.account = self.create_temporary_account()
        else:
            self.account = account
        return
    
    def login(self, username=None, password=None, community=None):
        """
        Login a User
        Creates a User object attached to the Firethorn Engine
        
        Parameters
        ----------
        username: string, optional
            Username
            
        password: string, optional
            Password
            
        community: string, optional
            Community
        """    
          
        
        new_auth = Account(endpoint=self.endpoint)
        new_auth.login(username, password, community)
        if (new_auth.logged_in):
            self.account = new_auth
        return new_auth.logged_in
    

    def identity(self):
        if (self.account!=None):
            return self.account.username
        
        return None


    def system_info_check(self):
        """
        Check system info
        """
        try :
            req = urllib.request.Request(self.endpoint + config.system_info, headers=self.account.get_identity_as_headers())
            with urllib.request.urlopen(req) as response:
                return (json.loads(response.read().decode('utf-8')))
        except Exception as e:
            logging.exception(e)
            
        return {} 
                     

    def create_temporary_account(self):
        """
        Create a temporary user
        
        """            
        username = None
        community = None
        
        try :
            
            req = urllib.request.Request(  self.endpoint + config.system_info, headers={"Accept" : "application/json"})
            with urllib.request.urlopen(req) as response:
                info = response.info()
                for header in info:
                    if (header.lower()=="firethorn.auth.username"):
                        username =  info[header]
                    if (header.lower()=="firethorn.auth.community"):
                        community =  info[header]
                        
        except Exception as e:
            logging.exception(e)
            
        self.account = Account(username = username, community = community, endpoint=self.endpoint)
        
        return self.account
        
         
    def create_jdbc_resource(self, resource_name , database, catalog, connection_type, host, username, password):

        """ Create a Jdbc Resource
        """
        
        jdbcspace=None
        try:
            
            data = urllib.parse.urlencode({config.resource_create_name_params['http://data.metagrid.co.uk/wfau/firethorn/types/entity/jdbc-resource-1.0.json'] : resource_name,
                                    "jdbc.resource.connection.database" : database,
                                    "jdbc.resource.connection.catalog" :catalog, 
                                    "jdbc.resource.connection.type" : connection_type, 
                                    "jdbc.resource.connection.host" : host, 
                                    "jdbc.resource.connection.user" : username, 
                                    "jdbc.resource.connection.pass" : password
                                    }).encode("utf-8")
    

            req = urllib.request.Request( self.endpoint + config.jdbc_creator, headers=self.account.get_identity_as_headers())
            response = urllib.request.urlopen(req,data)
            jdbcspace = json.loads(response.read().decode("utf-8"))
            response.close()
            
        except Exception as e:
            logging.exception(e)
            
        return JdbcResource(json_object=jdbcspace, account=self.account)    
    
    
    
    def select_jdbc_resource_by_name(self, name):
        """JDBC Resource select by catalog and schema name
        
        Parameters
        ----------
        name: string, required
            The JDBC Resource name

        Returns
        -------
        JdbcResource: JdbcResource
            The JdbcResource found
        """
        
        return     
            

    def select_jdbc_schema_by_name(self, jdbcurl, catalog, schema):
        """JDBC Schema select by catalog and schema name
        
        Parameters
        ----------
        catalog: string, required
            The JDBC Catalog name
            
        schema: string, required 
            The JDBC Schema name 
         
        Returns
        -------
        JdbcSchema: JdbcSchema
            The JdbcSchema found
        """
        
        response_json = {}
        
        try :
            data = urllib.parse.urlencode({config.jdbc_schema_catalog : catalog, config.jdbc_schema_schema : schema }).encode("utf-8")
            req = urllib.request.Request( jdbcurl + "/schemas/select", headers=self.account.get_identity_as_headers())

            with urllib.request.urlopen(req, data) as response:
                response_json =  json.loads(response.read().decode('utf-8'))
            schema = JdbcSchema(json_object = response_json, jdbc_resource=models.adql.AdqlResource(url=response_json.get("parent"), account=self.account))
        except Exception as e:
            logging.exception(e)      
            
        return schema
    
    
    def select_jdbc_resource_by_ident(self, ident):
        return JdbcResource(url=ident, account=self.account)

    
    def create_adql_resource(self, adqlspacename=None):
        """Create an ADQL Resource
        
        Parameters
        ----------
        adqlspacename: string, required
            ADQL Space name 
            
        
        Returns    
        -------
        adqlresource: AdqlResource
            The new AdqlResource 
        
        """
        
        adqlresource = ""
        
        try:
            ### Create workspace
            if adqlspacename==None:
                t = datetime.now()
                adqlspacename = 'workspace-' + t.strftime("%y%m%d_%H%M%S") 
            data = urllib.parse.urlencode({config.resource_create_name_params['http://data.metagrid.co.uk/wfau/firethorn/types/entity/adql-resource-1.0.json'] : adqlspacename}).encode("utf-8")
            req = urllib.request.Request( self.endpoint + config.workspace_creator, headers=self.account.get_identity_as_headers())
            with urllib.request.urlopen(req, data) as response:
                adqlresource =  json.loads(response.read().decode('utf-8'))
            response.close()
        except Exception as e:
            logging.exception(e)
            
        return models.adql.AdqlResource(json_object = adqlresource, account=self.account)
                         
                         
    def select_adql_resources(self):
        """
        Select all ADQL Resources
        """
        adqlresources = {}
        
        try:
 
            req = urllib.request.Request( self.endpoint + config.get_adql_resources_url, headers=self.account.get_identity_as_headers())
            with urllib.request.urlopen(req) as response:
                adqlresources =  json.loads(response.read().decode('utf-8'))
            response.close()
        except Exception as e:
            logging.exception(e)
            
        resource_object_list = []
        for resource in adqlresources:
            resource_object_list.append(models.adql.AdqlResource(json_object=resource, account=self.account))

        return resource_object_list
    
    
    def select_adql_resource_by_name(self, resource_name):
        """
        Select an ADQL resource by name
        """
        return
    
    
    def select_adql_resource_by_ident(self, ident):
        """
        Select an ADQL resource by ident
        """
        return models.adql.AdqlResource(account=self.account, url=ident)


    def select_ivoa_resources(self):
        """
        Select all ADQL Resources
        """
        ivoaresources = {}
        
        try:
 
            req = urllib.request.Request( self.endpoint + config.get_ivoa_resources_url, headers=self.account.get_identity_as_headers())
            with urllib.request.urlopen(req) as response:
                ivoaresources =  json.loads(response.read().decode('utf-8'))
            response.close()
        except Exception as e:
            logging.exception(e)

        resource_object_list = []
        for resource in ivoaresources:
            resource_object_list.append(models.ivoa.IvoaResource(json_object=resource, account=self.account))

        return resource_object_list
               
    
    
    def select_ivoa_resource_by_name(self, name):
        return 
    
    
    def select_ivoa_resource_by_ident(self, ident):
        """
        Select an IVOA resource by ident
        """
        return models.ivoa.IvoaResource(account=self.account, url=ident)
    

    def create_ivoa_resource(self, ivoa_space_name, url):
        """Create an IVOA resource
        
        Parameters
        ----------
        ivoa_space_name: string, required
            Name of IVOA resource

        url: string, required
            URL of IVOA resource to import
            
        Returns
        -------
        IvoaResource: IvoaResource
            The IVOA resource 
            
        """
        
        ivoa_resource = None
        try:
            data = urllib.parse.urlencode({"ivoa.resource.name" : ivoa_space_name , "ivoa.resource.endpoint" : url}).encode("utf-8")
            req = urllib.request.Request( self.endpoint + config.ivoa_resource_create, headers=self.account.get_identity_as_headers()) 
            with urllib.request.urlopen(req, data) as response:
                ivoa_resource =  json.loads(response.read().decode('utf-8'))
            response.close()
        except Exception as e:
            logging.exception(e)

        return models.ivoa.IvoaResource(account=self.account, json_object=ivoa_resource)

    
    def _get_attribute(self, ident, attr):
        """Get an attribute of a JSON HTTP resource
        
        Parameters
        ----------
        ident: string, required
            The URL being queried

        attr: string, required
            The attribute of the JSON response being asked for  
                   
        Returns
        -------
        attr_val: string
            Value of the attribute requested
        """
        
        attr_val = []
        try :
            req_exc = urllib.request.Request( ident, headers=self.account.get_identity_as_headers()).encode("utf-8")
            with urllib.request.urlopen(req_exc) as response:
                response_exc_json =  response.read().decode('utf-8')       
            attr_val = json.loads(response_exc_json)[attr]
        except Exception as e:
            logging.exception(e)
        return attr_val
    

    def import_schema_list(self, schema_names, adql_resource, jdbc_resource):
  
        for schema in schema_names:
            jdbc_schema = atlas_jdbc.select_schema_by_name(
                mapping,
                "dbo"
                )
            if (None != jdbc_schema):
                metadoc="https://raw.githubusercontent.com/wfau/metadata/master/metadocs/" + mapping + "_TablesSchema.xml"
                adql_schema = atlas_adql.import_jdbc_schema(
                    jdbc_schema,
                    mapping,
                    metadoc=metadoc
                    )
        
        
    def load_resources(self, config_file):
        """
        Load a set of Resources (and TAP) from a local or remote JSON configuration file
        """
        sEng = SetupEngine(json_file=config_file, firethorn_base=self.endpoint, firethorn_engine = self)
        sEng.setup_resources()


    def get_json(self, ident):
        """Select a JSON HTTP resource
        
        Parameters
        ----------
        ident: string, required
            The URL being queried

        """
        
        json_result = {}
        
        try :
            req_exc = urllib.request.Request(ident, headers=self.account.get_identity_as_headers())
            with urllib.request.urlopen(req_exc) as response:
                json_result =  json.loads(response.read().decode('utf-8'))
     
        except Exception as e:
            logging.exception(e)
            
        return json_result
    


