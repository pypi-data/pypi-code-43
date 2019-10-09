# Copyright 2019 The Johns Hopkins University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import requests
import sys

from craedl import errors

class Auth():
    """
    A base authentication class.
    """

    base_url = 'https://api.craedl.org/'
    ### FOR DEVELOPMENT ###
    base_url = 'https://api.localhost.test:8000/'
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #######################

    token_path = '~/.config/craedl'

    def __init__(self):
        if not os.path.isfile(os.path.expanduser(self.token_path)):
            sys.exit('ERROR: You have not configured an authentication token.\nUse `craedl-token` to configure your authentication token.')
    
    def __repr__(self):
        string = '{'
        for k, v in vars(self).items():
            if type(v) is str:
                string += "'" + k + "': '" + v + "', "
            else:
                string += "'" + k + "': " + str(v) + ", "
        if len(string) > 1:
            string = string[:-2]
        string += '}'
        return string

    def GET(self, path):
        """
        GET
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.get(
            self.base_url + path,
            headers={'Authorization': 'Bearer %s' % token},
            verify=False # FOR DEVELOPMENT
        )
        return self.process_response(response)

    def POST(self, path, data):
        """
        POST
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.post(
            self.base_url + path,
            json=data,
            headers={'Authorization': 'Bearer %s' % token},
            verify=False # FOR DEVELOPMENT
        )
        return self.process_response(response)

    def PUT_DATA(self, path, data):
        """
        PUT_DATA
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.put(
            self.base_url + path,
            data=data,
            headers={
                'Authorization': 'Bearer %s' % token,
                'Content-Disposition': 'attachment; filename="craedl-upload"',
            },
            verify=False # FOR DEVELOPMENT
        )
        return self.process_response(response)

    def GET_DATA(self, path):
        """
        GET_DATA
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.get(
            self.base_url + path,
            headers={'Authorization': 'Bearer %s' % token},
            stream=True,
            verify=False # FOR DEVELOPMENT
        )
        return response

    def process_response(self, response):
        """
        process_response
        """
        if response.status_code == 200:
            out = json.loads(response.content.decode('utf-8'))
            if out:
                return out
        elif response.status_code == 400:
            raise errors.Parse_Error(details=response.content.decode('ascii'))
        elif response.status_code == 401:
            sys.exit('ERROR: (invalid token).')
            #raise errors.Invalid_Token_Error
        elif response.status_code == 403:
            raise errors.Unauthorized_Error
        elif response.status_code == 404:
            raise errors.Not_Found_Error
        elif response.status_code == 500:
            raise errors.Server_Error
        else:
            raise errors.Other_Error

class Directory(Auth):
    """
    A Craedl directory.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('directory/' + str(id) + '/')['directory']
        for k, v in data.items():
            setattr(self, k, v)

    def create_directory(self, name):
        """
        Create a new directory contained within this directory.
        """
        data = {
            'name': name,
            'parent': self.id,
        }
        response_data = self.POST('directory/', data)
        return Directory(response_data['id'])

    def create_file(self, open_path):
        data = {
            'name': open_path.split('/')[-1],
            'parent': self.id,
            'size': os.path.getsize(open_path)
        }
        response_data = self.POST('file/', data)
        F = File(response_data['id'])
        response_data2 = self.PUT_DATA(
            'data/' + str(F.id) + '/',
            open(open_path, 'rb')
        )
        return F

    def get(self, path):
        p = path.split('/')[0]
        for c in self.children:
            if p != c['name']:
                sys.exit('ERROR: ' + p + ': No such file or directory')
            else:
                next_path = path.replace(p, '')
                if len(next_path) > 0 and '/' == next_path[0]:
                    next_path = next_path[1:]
                if next_path:
                    return Directory(c['id']).get(next_path)
                else:
                    return Directory(c['id'])

    def list(self):
        dirs = list()
        files = list()
        for c in self.children:
            if 'd' == c['type']:
                dirs.append(Directory(c['id']))
            else:
                files.append(File(c['id']))
        return [dirs, files]

class File(Auth):

    def __init__(self, id):
        super().__init__()
        data = self.GET('file/' + str(id) + '/')
        for k, v in data.items():
            setattr(self, k, v)

    def download(self, save_path):
        data = self.GET_DATA('data/' + str(self.id) + '/')
        try:
            f = open(save_path, 'wb')
        except IsADirectoryError:
            f = open(save_path + '/' + self.name, 'wb')
        for chunk in data.iter_content():
            f.write(chunk)
        f.close()

        return self

class Profile(Auth):

    def __init__(self, data=None, id=None):
        super().__init__()
        if not data and not id:
            data = self.GET('profile/whoami/')
        elif not data:
            data = self.GET('profile/' + str(id) + '/')
        for k, v in data.items():
            setattr(self, k, v)

    def get_projects(self):
        data = self.GET('profile/' + str(self.id) + '/projects/')
        projects = list()
        for project in data:
            projects.append(Project(project['id']))
        return projects

    def get_publications(self):
        data = self.GET('profile/' + str(self.id) + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications

class Project(Auth):

    def __init__(self, id):
        super().__init__()
        data = self.GET('project/' + str(id) + '/')
        for k, v in data.items():
            if not (type(v) is dict or type(v) is list):
                if not v == None:
                    setattr(self, k, v)

    def create_publication(self, data):
        data['project'] = self.id
        response_data = self.POST('publication/', data)
        return Publication(response_data)

    def get_data(self):
        d = Directory(self.root)
        return d

    def get_publications(self):
        data = self.GET('project/' + str(self.id) + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications

class Publication(Auth):

    authors = list()

    def __init__(self, data=None, id=None):
        self.authors = list()
        super().__init__()
        if not data:
            data = self.GET('publication/' + str(id) + '/')
        for k, v in data.items():
            if k == 'authors':
                for author in v:
                    self.authors.append(Profile(author))
            else:
                if not v == None:
                    setattr(self, k, v)
