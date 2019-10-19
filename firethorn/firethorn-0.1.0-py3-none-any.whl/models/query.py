'''
Created on Nov 4, 2017

@author: stelios
'''
import logging
from table import Table
from adql import adql_schema
try:
    import simplejson as json
except ImportError:
    import json


class Query(object):
    """
    Query Class, stores information for a Firethorn query 
    
    Attributes
    ----------
    querystring: string, optional
        The Query as a sring

    adql_resource: string, optional
        The query Resource
    
    adql_query: string, optional
        The AdqlQuery object
        
    account: Account, optional
        Reference to the he Authentication Engine being used
                  
    """

    def __init__(self,  querystring=None,  adql_query=None, mode="SYNC"):
        self.adql_query = adql_query
        self.mode = mode
        self.querystring = querystring
        if (self.adql_query!=None):
            self.account = self.adql_query.account
        if (mode=="SYNC"):
            self.run()
        pass
       
            
    @property
    def querystring(self):
        return self.__querystring
        
        
    @querystring.setter
    def querystring(self, querystring):
        self.__querystring = querystring
        
    
    @property
    def mode(self):
        return self.__mode
        
        
    @mode.setter
    def mode(self, mode):
        self.__mode = mode    
               
                     
    def run (self):
        """
        Run a query
        
        """
        try: 
            if (self.mode.upper()=="SYNC"):
                self.adql_query.run_sync()
            else :      
                self.adql_query.update(adql_query_status_next="COMPLETED")
        except Exception as e:
            logging.exception(e)
            
        return 
    

    def update (self, query_input):
        """
        Run Query
        """
        try: 
            self.adql_query.update(adql_query_input=query_input)
            self.querystring = query_input
        except Exception as e:
            logging.exception(e)    
            
        return 
    
    
    def results (self):
        """
        Get Results
        
        """
        if (self.adql_query!=None):
            if (self.adql_query.table()!=None):
                return Table(adql_table=self.adql_query.table())
        
        return None


    def status (self):
        """
        Get Status 
        """
        if self.adql_query!=None:
            return self.adql_query.status()

                   
    def error (self):
        """
        Get Error message
        """
        if self.adql_query!=None:
            return self.adql_query.error()


    def isRunning(self):
        """
        Check if a Query is running
        """
        if self.adql_query!=None:
            return self.adql_query.isRunning()
    
    
    def __str__(self):
        """ Print class as string
        """
        return 'Query: %s\nQuery ID: %s\n ' %(self.querystring, self.adql_query.url) 
    



    
        