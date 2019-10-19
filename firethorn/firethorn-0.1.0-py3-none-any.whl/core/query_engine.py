'''
Created on Jun 4, 2014

@author: stelios
'''

import urllib.request
import time
import signal
from models.adql_query.adql_query import AdqlQuery
try:
    import simplejson as json
except ImportError:
    import json
from utils.string_functions import string_functions
string_functions = string_functions()
import config as config
import logging


class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()




class QueryEngine(object):
    """Query engine, used to drive queries through the core Firethorn service 
    """



    def __init__(self, account=None):
        self.id = None
        self.account = account
        
        
    def get_status(self, url):
        """Wrapper function to send a GET request to get the status of a resource and return the JSON
        
        Parameters
        ----------
        url: string, required
            URL to query
                   
        Returns    
        -------
        query_json: string
            The JSON response as a string
        
        """
 
        request = urllib.request.Request(url,headers=self.account.get_identity_as_headers())
        with urllib.request.urlopen(request) as response:
            query_json = response.read().decode('utf-8')
        return query_json            
            
            
    def _getRows(self, query_results):
        """Get rows from a query result

        
        Parameters
        ----------
        query_results: string, required
            Query results
                   
        Returns    
        -------
        row_length: integer
            The number of rows
        
        """
        rows = json.loads(query_results)
        row_length = -1
        if len(rows)<=1:
            return row_length
        else :
            row_length = len(rows[1])
 
        return row_length
        
    
    def create_query(self, adql_query_input, adql_query_status_next, adql_resource, account, adql_query_wait_time=600000, jdbc_schema_ident=None, params=None):
        """
        Create query
        """
        
        json_result = {}
        
        try :
            from datetime import datetime
            urlenc = {}

            if (params != None):
                urlenc = params
            
            if (adql_query_input!=None):
                urlenc.update({config.query_param : adql_query_input})     
            if (adql_query_status_next!=None):
                urlenc.update({config.query_status_update : adql_query_status_next})
            if (adql_query_wait_time!=None):
                urlenc.update({config.query_wait_time_param : adql_query_wait_time})
            if (jdbc_schema_ident!=None):
                urlenc.update({config.jdbc_schema_ident : jdbc_schema_ident})   
            
            data = urllib.parse.urlencode(urlenc).encode('utf-8')
            request = urllib.request.Request(adql_resource.url + config.query_create_uri, headers=account.get_identity_as_headers())
            with urllib.request.urlopen(request, data) as response:
                json_result = json.loads(response.read().decode('UTF-8'))
                
        except Exception as e:
            if (type(e).__name__=="Timeout"):
                raise
            else:
                logging.exception(e)

        return AdqlQuery(json_object=json_result, adql_resource=adql_resource)


    def update_query(self,  adql_query, adql_query_input=None, adql_query_status_next=None, adql_query_wait_time=None, adql_query_delay=100):
        """
        Create query
        """
        
        json_result = {}
        
        try :
            
            urlenc = {}
            
            if (adql_query_input!=None):
                urlenc.update({config.query_param : adql_query_input})           
            if (adql_query_status_next!=None):
                urlenc.update({config.query_status_update : adql_query_status_next})
            if (adql_query_wait_time!=None):
                urlenc.update({config.query_wait_time_param : adql_query_wait_time})
            if (adql_query_delay!=None):
                urlenc.update({config.adql_query_delay : adql_query_delay})   
                                                
            data = urllib.parse.urlencode(urlenc).encode('utf-8')
            request = urllib.request.Request(adql_query.url, headers=adql_query.account.get_identity_as_headers())

            with urllib.request.urlopen(request, data) as response:
                json.loads(response.read().decode('UTF-8'))
                
        except Exception as e:
            if (type(e).__name__=="Timeout"):
                raise
            else:
                logging.exception(e)

        return adql_query


    
          
            
