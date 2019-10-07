"""This module contains the api requests and response"""

import os
import json
import urllib.request
import datahub.telematics as telematics
import datahub.formatter as formatter

class Client:

    def __init__(self, domain, api_key=None):
        self._domain = domain
        self._api_key = api_key
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor)
    
    def format_url(self, api_path):
        return 'http://{}{}'.format(self._domain, api_path)

    def get_headers(self):
    
        if not self._api_key:
            return {'Provide API KEY'}

        return {
                'Content-Type' : 'application/json',
                'h-token' : self._api_key
            }
    
    def get_api(self, obj, api_path, query=None):
    
        url = self.format_url(api_path)
        if query:
            url = '{}?{}'.format(url, query)

        headers = self.get_headers()
        req = urllib.request.Request(url, headers=headers)
        resp = self._opener.open(req)
        return obj(formatter._json_response(resp))
    
    def api_post(self, res_obj, api_path, req_obj):
    
        url = self.format_url(api_path)

        json_data = req_obj.save_to_json()
        binary_data = json_data.encode()

        headers = self._get_request_headers()
        req = urllib.request.Request(url, binary_data, headers)
        resp = self._opener.open(req)
        return res_obj(formatter.json_response(resp))
    
    def get_repos(self):
        """The method is gets the list of repos"""

        api_path = '/hapi/datarepos'
        return self.get_api(telematics.Repos, api_path)
    
    def get_branches(self):
        """The method gets the list of branches by it's repo_id"""

        api_path = '/hapi/datarepos'
        return self.get_api(telematics.Branches, api_path)
    
    def get_tables(self, repo_id):
        """The method gets the list of tables by it's repo_id"""

        api_path = '/hapi/datarepo/{}'
        return self.get_api(telematics.Tables, api_path.format(repo_id))
    
    def get_dataset(self, repo_id, branch_id, table_id):
        """The method gets the dataset"""

        api_path = '/hapi/dataset/{}/{}/{}'
        return self.get_api(telematics.Dataset, api_path.format(repo_id, branch_id, table_id))
    
    def post_commit(self, repo_id, branch_id, table_id, obj):
        """The method posts the commit"""

        api_path = '/txn/{}/{}'
        return self.api_post(telematics.PostCommitResponse, obj, api_path.format(repo_id, branch_id))