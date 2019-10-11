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
    This base class handles low-level RESTful API communications. Any class that
    needs to perform RESTful API communications should extend this class.
    """

    if sys.platform == 'win32':
        token_path = os.path.abspath(os.path.join(os.sep, 'Users',
            os.getlogin(), 'AppData', 'Local', 'Craedl', 'craedl'))
    elif sys.platform == 'darwin':
        token_path = os.path.abspath(os.path.join(os.sep, 'Users',
            os.getlogin(), 'Library', 'Preferences', 'Craedl', 'craedl'))
    else:
        token_path = os.path.expanduser('~/.config/Craedl/craedl')
    base_url = 'https://api.craedl.org/'

    def __init__(self):
        if not os.path.isfile(os.path.expanduser(self.token_path)):
            raise errors.Missing_Token_Error
    
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
        Handle a GET request.

        :param path: the RESTful API method path
        :type path: string
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.get(
            self.base_url + path,
            headers={'Authorization': 'Bearer %s' % token},
        )
        return self.process_response(response)

    def POST(self, path, data):
        """
        Handle a POST request.

        :param path: the RESTful API method path
        :type path: string
        :param data: the data to POST to the RESTful API method as described at
            https://api.craedl.org
        :type data: dict
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.post(
            self.base_url + path,
            json=data,
            headers={'Authorization': 'Bearer %s' % token},
        )
        return self.process_response(response)

    def PUT_DATA(self, path, data):
        """
        Handle a data PUT request.

        :param path: the RESTful API method path
        :type path: string
        :param data: the data to POST to the RESTful API method as described at
            https://api.craedl.org
        :type data: dict
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.put(
            self.base_url + path,
            data=data,
            headers={
                'Authorization': 'Bearer %s' % token,
                'Content-Disposition': 'attachment; filename="craedl-upload"',
            },
        )
        return self.process_response(response)

    def GET_DATA(self, path):
        """
        Handle a data GET request.

        :param path: the RESTful API method path
        :type path: string
        :returns: the data stream being downloaded
        """
        token = open(os.path.expanduser(self.token_path)).readline().strip()
        response = requests.get(
            self.base_url + path,
            headers={'Authorization': 'Bearer %s' % token},
            stream=True,
        )
        return response

    def process_response(self, response):
        """
        Process the response from a RESTful API request.

        :param response: the RESTful API response
        :type response: a response object
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        if response.status_code == 200:
            out = json.loads(response.content.decode('utf-8'))
            if out:
                return out
        elif response.status_code == 400:
            raise errors.Parse_Error(details=response.content.decode('ascii'))
        elif response.status_code == 401:
            raise errors.Invalid_Token_Error
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
    A Craedl directory object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('directory/' + str(id) + '/')['directory']
        for k, v in data.items():
            setattr(self, k, v)

    def __eq__(self, other):
        if not isinstance(other, Directory):
            return NotImplemented
        equal = True
        for i1, i2 in list(zip(vars(self).items(), vars(other).items())):
            if i1[0] != i2[0] or i1[1] != i2[1]:
                equal = False
        return equal

    def create_directory(self, name):
        """
        Create a new directory contained within this directory.
        
        **Note:** This method returns the updated instance of this directory
        (because it has a new child). The recommended usage is:

        .. code-block:: python

            home = home.create_directory('new-directory-name')

        Use :meth:`Directory.get` to get the new directory.

        :param name: the name of the new directory
        :type name: string
        :returns: the updated instance of this directory
        """
        data = {
            'name': name,
            'parent': self.id,
        }
        response_data = self.POST('directory/', data)
        return Directory(self.id)

    def create_file(self, file_path):
        """
        Create a new file contained within this directory.

        **Note:** This method returns the updated instance of this directory
        (because it has a new child). The recommended usage is:

        .. code-block:: python

            home = home.create_file('/path/on/local/computer/to/read/data')

        Use :meth:`Directory.get` to get the new file.

        :param file_path: the path to the file to be uploaded on your computer
        :type file_path: string
        :returns: the updated instance of this directory
        """
        file_path = os.path.expanduser(file_path)
        data = {
            'name': file_path.split('/')[-1],
            'parent': self.id,
            'size': os.path.getsize(file_path)
        }
        response_data = self.POST('file/', data)
        response_data2 = self.PUT_DATA(
            'data/' + str(response_data['id']) + '/',
            open(file_path, 'rb')
        )
        return Directory(self.id)

    def get(self, path):
        """
        Get a particular directory or file. This can be an absolute or
        relative path.

        :param path: the directory or file path
        :type path: string
        :returns: the requested directory or file
        """
        if not path or path == '.':
            return self
        if path[0] == '/':
            try:
                return Directory(self.parent).get(path)
            except errors.Not_Found_Error:
                while path.startswith('/') or path.startswith('./'):
                    if path.startswith('/'):
                        path = path[1:]  # 1 = len('/')
                    else:
                        path = path[2:]  # 2 = len('./')
                if not path or path == '.':
                    return self
                p = path.split('/')[0]
                if p != self.name:
                    raise FileNotFoundError(p + ': No such file or directory')
                path = path[len(p):]
                if not path:
                    return self
        while path.startswith('/') or path.startswith('./'):
            if path.startswith('/'):
                path = path[1:]  # 1 = len('/')
            else:
                path = path[2:]  # 2 = len('./')
        if not path or path == '.':
            return self
        p = path.split('/')[0]
        if p == '..':
            path = path[2:]  # 2 = len('..')
            while path.startswith('/'):
                path = path[1:]  # 1 = len('/')
            try:
                return Directory(self.parent).get(path)
            except errors.Not_Found_Error:
                raise FileNotFoundError(p + ': No such file or directory')
        for c in self.children:
            if p == c['name']:
                path = path[len(p):]
                while path.startswith('/'):
                    path = path[1:]  # 1 = len('/')
                if path:
                    return Directory(c['id']).get(path)
                else:
                    try:
                        return Directory(c['id'])
                    except errors.Not_Found_Error:
                        return File(c['id'])
        raise FileNotFoundError(p + ': No such file or directory')

    def list(self):
        """
        List the contents of this directory.

        :returns: a tuple containing a list of directories and a list of files
        """
        dirs = list()
        files = list()
        for c in self.children:
            if 'd' == c['type']:
                dirs.append(Directory(c['id']))
            else:
                files.append(File(c['id']))
        return (dirs, files)

class File(Auth):
    """
    A Craedl file object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('file/' + str(id) + '/')
        for k, v in data.items():
            setattr(self, k, v)

    def download(self, save_path):
        """
        Download the data associated with this file.

        :param save_path: the path to the directory on your computer that will
            contain this file's data
        :type save_path: string
        :returns: this file
        """
        save_path = os.path.expanduser(save_path)
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
    """
    A Craedl profile object.
    """

    def __init__(self, data=None, id=None):
        super().__init__()
        if not data and not id:
            data = self.GET('profile/whoami/')
        elif not data:
            data = self.GET('profile/' + str(id) + '/')
        for k, v in data.items():
            setattr(self, k, v)

    def create_project(self, name):
        """
        Create a new project belonging to this profile.

        Use :meth:`Profile.get_project` to get the new project.

        :param name: the name of the new project
        :type name: string
        :returns: this profile
        """
        data = {
            'name': name,
            'research_group': '',
        }
        response_data = self.POST('project/', data)
        return self

    def get_project(self, name):
        """
        Get a particular project that belongs to this profile.

        :param name: the name of the project
        :type name: string
        :returns: a project
        """
        projects = self.get_projects()
        for project in projects:
            if project.name == name:
                return project
        raise errors.Not_Found_Error

    def get_projects(self):
        """
        Get a list of projects that belong to this profile.

        :returns: a list of projects
        """
        data = self.GET('profile/' + str(self.id) + '/projects/')
        projects = list()
        for project in data:
            projects.append(Project(project['id']))
        return projects

    def get_publications(self):
        """
        Get a list of publications that belongs to this profile.

        :returns: a list of publications
        """
        data = self.GET('profile/' + str(self.id) + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications

    def get_research_group(self, slug):
        """
        Get a particular research group.

        :param slug: the unique slug in this research group's URL
        :type slug: string
        :returns: a research group
        """
        return Research_Group(slug)

    def get_research_groups(self):
        """
        Get a list of research groups that this profile belongs to.

        :returns: a list of research groups
        """
        data = self.GET('research_group/')
        research_groups = list()
        for research_group in data:
            research_groups.append(Research_Group(research_group['slug']))
        return research_groups

class Project(Auth):
    """
    A Craedl project object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('project/' + str(id) + '/')
        for k, v in data.items():
            if not (type(v) is dict or type(v) is list):
                if not v == None:
                    setattr(self, k, v)

    def get_data(self):
        """
        Get the data attached to this project. It always begins at the home
        directory.

        :returns: this project's home directory
        """
        d = Directory(self.root)
        return d

    def get_publications(self):
        """
        Get a list of publications attached to this project.

        :returns: a list of this project's publications
        """
        data = self.GET('project/' + str(self.id) + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications

class Publication(Auth):
    """
    A Craedl publication object.
    """

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

class Research_Group(Auth):
    """
    A Craedl research group object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('research_group/' + str(id) + '/')
        for k, v in data.items():
            if not (type(v) is dict or type(v) is list):
                if not v == None:
                    setattr(self, k, v)

    def create_project(self, name):
        """
        Create a new project belonging to this research group.

        Use :meth:`Research_Group.get_project` to get the new project.

        :param name: the name of the new project
        :type name: string
        :returns: this research group
        """
        data = {
            'name': name,
            'research_group': self.pk,
        }
        response_data = self.POST('project/', data)
        return self

    def get_project(self, name):
        """
        Get a particular project that belongs to this research group.

        :param name: the name of the project
        :type name: string
        :returns: a project
        """
        projects = self.get_projects()
        for project in projects:
            if project.name == name:
                return project
        raise errors.Not_Found_Error

    def get_projects(self):
        """
        Get a list of projects that belong to this research group.

        :returns: a list of projects
        """
        data = self.GET('research_group/' + self.slug + '/projects/')
        projects = list()
        for project in data:
            projects.append(Project(project['id']))
        return projects

    def get_publications(self):
        """
        Get a list of publications that belong to this research group.

        :returns: a list of publications
        """
        data = self.GET('research_group/' + self.slug + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications
