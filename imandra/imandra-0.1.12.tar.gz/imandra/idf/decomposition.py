import os.path 
import requests
import json

from .exception import process_errors

class Decomposition(object):
    def __init__(self, job_hash, api_url, headers):
        self.job_hash = job_hash
        self.api_url  = api_url
        self.headers  = headers
        self.__regions_code = \
          { "flat" : None
          , "tree" : None
          }

    def status(self):
        url = os.path.join(self.api_url, "api/ipl-worker/status", self.job_hash)
        r = requests.get\
          ( url
          , headers = self.headers
          )
        return process_errors(r)

    def __get_regions_code(self, kind):
        url = os.path.join(self.api_url, "api/ipl-worker/data", self.job_hash, "regions_ast_Scenario_symbolic_{}.py".format(kind))
        r = requests.get\
          ( url
          , headers = self.headers
          )
        self.__regions_code[kind] = process_errors(r)
 
    def dump(self, fp, kind="tree"):
        if self.__regions_code[kind] is None:
            self.__get_regions_code(kind)
        fp.write(self.__regions_code[kind]) 

    def dumps(self, kind="tree"):
        if self.__regions_code[kind] is None:
            self.__get_regions_code(kind)
        return self.__regions_code[kind]




