'''
Created on Feb 8, 2018

@author: stelios
'''

import urllib
import config as config
import logging

class Account(object):
    '''
    classdocs
    '''

    
    def __init__(self, username=None, password=None, community=None, endpoint=config.endpoint):
        self.username = username
        self.password = password
        self.community = community     
        self.logged_in = False
        self.endpoint = endpoint
        if (self.username!=None):
            self.login(username, password, community)
        
        
    @property
    def username(self):
        return self.__username
        
        
    @username.setter
    def username(self, username):
        self.__username = username


    @property
    def password(self):
        return self.__password
        
        
    @password.setter
    def password(self, password):
        self.__password = password
        
        
    @property
    def community(self):
        return self.__community
        
        
    @community.setter
    def community(self, community):
        self.__community = community

    @property
    def logged_in(self):
        return self.__logged_in
        
        
    @logged_in.setter
    def logged_in(self, logged_in):
        self.__logged_in = logged_in
   

    def login(self, username=None, password=None, community=None):
        try :
            
            req = urllib.request.Request(self.endpoint + config.system_info, headers=self.get_identity_as_headers())
            with urllib.request.urlopen(req) as response:
                response.read().decode('utf-8')     
                if (response.getcode()==200):
                    self.logged_in = True
                    self.username=username
                    self.password=password
                    self.community=community
        except Exception as e:
            logging.exception(e)
            pass
        
        return
            
        
    def get_identity_as_headers(self):
        """
        Get a Dictionary of values representing a Identity, to be used for Firethorn Requests
        """
        if (self.username!=None):
            if (self.password!=None and self.username!=None and self.community!=None):
                return {"Accept" : "application/json", "firethorn.auth.community" : self.community, "firethorn.auth.username" : self.username, "firethorn.auth.password" : self.password}
            elif (self.community==None):
                return {"Accept" : "application/json", "firethorn.auth.username" : self.username, "firethorn.auth.password" : self.password}
            elif (self.password==None):
                return {"Accept" : "application/json", "firethorn.auth.community" : self.community, "firethorn.auth.username" : self.username}
            else:
                return {"Accept" : "application/json", "firethorn.auth.username" : self.username}
        else :
            return {"Accept" : "application/json"}
        
        
    def __str__(self):
        """ Print User as string
        """
        return 'Username: %s ' %(self.username) 

        