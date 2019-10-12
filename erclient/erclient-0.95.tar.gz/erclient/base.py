import csv
import json
import os
import random
from genericpath import exists

import requests
import xmltodict
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .config import api_base_url, api_base_url_rest, client_id, client_secret, token_url, note_schema, rest_username, \
    rest_password, rest_entity_id


class RemoteSchema():
    def __init__(self, schema):
        self.schema = schema

    def get_id(self):
        return self.schema['ID']

    def get_field(self, field):
        return self.schema[field]

    def set_field(self, field, value):
        self.schema = set_attr(schema=self.schema, key=field, value=value)
        return self.schema


class ErConnector():
    def __init__(self,
                 api_version='20',
                 client_id=client_id,
                 client_secret=client_secret,
                 api_base_url=api_base_url,
                 token_url=token_url,
                 rest_username=rest_username,
                 rest_password=rest_password,
                 rest_entity_id=rest_entity_id):
        self.api_version = api_version
        if api_version == 'rest':
            self.client_id = rest_username
            self.client_secret = rest_password
            self.api_base_url = api_base_url_rest
            self.rest_entity_id = rest_entity_id
            self.token_url = None
        else:
            self.client_id = client_id
            self.client_secret = client_secret
            self.api_base_url = api_base_url
            self.token_url = token_url
            self.cookies = None
            self.rest_entity_id = None
        self.token = self.fetch_token()

    def parse_response(self, input):
        # Parse responses as json to normalize between the 2 API versions
        if self.api_version == 'rest':
            try:
                return xmltodict.parse(input.text)['MessageResponse']
            except:
                try:
                    return xmltodict.parse(input.text)['ErrorResponse']
                except:
                    try:
                        return xmltodict.parse(input.text)['AboutItemResponse']
                    except:
                        try:
                            return xmltodict.parse(input.text)['ListResponse']
                        except:
                            return (input.text)
        else:
            try:
                return input.json()
            except:
                return input

    def fetch_token(self):

        # fetch either REST Token or OAuth2 token. Returns a string value

        if self.api_version == 'rest':
            error = False
            errorstr = 'Error: Remote REST Connection information is incomplete. '
            if self.api_base_url is None:
                error = True
                errorstr += ' ***API Base URL is missing.'
            if self.client_id is None:
                error = True
                errorstr += ' ***REST Username is missing.'
            if self.client_secret is None:
                error = True
                errorstr += ' ***REST Password is missing.'
            if self.rest_entity_id is None:
                error = True
                errorstr += ' ***REST EntityID is missing.'

            if error:
                raise Exception(errorstr)

        elif self.client_id is None or self.client_secret is None or self.api_base_url is None or self.token_url is None:
            error = False
            errorstr = 'Error: Remote OAuth2 Connection information is incomplete. '
            if self.client_id is None:
                error = True
                errorstr += ' ***client_id is missing.'
            if self.client_secret is None:
                error = True
                errorstr += ' ***client_secret is missing.'
            if self.api_base_url is None:
                error = True
                errorstr += ' ***API Base URL is missing.'
            if self.token_url is None:
                error = True
                errorstr += ' ***token_url is missing.'

            if error:
                raise Exception(errorstr)

        if self.api_version == 'rest':
            self.requestsession = requests.Session()
            requesturl = self.api_base_url + 'Authenticate/'
            params = {'UserName': self.client_id, 'Password': self.client_secret, 'EntityID': self.rest_entity_id}
            request_response = self.requestsession.post(requesturl, params)
            self.api_user_guid_rest = ((self.parse_response(request_response))['Data']['Message']).split('|')[1]
            self.cookies = request_response.cookies
            self.token = self.cookies['__erecruit__auth']
        else:
            self.requestsession = None
            client = BackendApplicationClient(client_id=self.client_id)
            oauth = OAuth2Session(client=client)
            bearer_token = oauth.fetch_token(token_url=self.token_url, client_id=self.client_id,
                                             client_secret=client_secret)['access_token']
            self.token = bearer_token
            self.api_user_guid_rest = None
        return self.token

    def send_request(self,
                     path,
                     verb='GET',
                     payload=None,
                     file=None,
                     pathonly=False,
                     rawresponse=False
                     ):

        # Send request and get response to either 2.0 or Rest API and normalize response into Json for easier handling

        bearer_token = self.token

        auth_headers = {}
        if self.api_version != 'rest':
            auth_headers['Authorization'] = 'Bearer %s' % bearer_token

        path = self.api_base_url + path

        if pathonly:
            return path
        else:
            # Handle file uploads as either a path or byte stream

            if isinstance(file, str) and os.path.exists(file):
                myfile = open(file, 'rb')
                myfile.seek(0)  # make sure we read from the start of the file
                file = {'file': myfile}
            elif hasattr(file, 'name'):
                file.seek(0)
                file = {'file': file}
            else:
                file = {}

            # Instead of allowing this method to pass an arbitrary verb to requests, lets keep control over it and use
            # requests's shortcuts, eg requests.post, requests.put etc.

            response = None

            if verb == 'GET':

                response = requests.get(path, headers=auth_headers, cookies=self.cookies)

            elif verb == 'POST':

                response = requests.post(path, data=payload, headers=auth_headers, files=file, cookies=self.cookies)

            elif verb == 'PUT':

                response = requests.put(path, data=payload, headers=auth_headers, files=file, cookies=self.cookies)

            elif verb == 'DELETE':

                response = requests.delete(path, data=payload, headers=auth_headers, files=file, cookies=self.cookies)

            if rawresponse:
                return response
            else:
                return self.parse_response(response)

class DataHelper(object):

    def get_id(self):
        return self.get_field('ID')

    def get_field(self, field):
        return self.data[field]

    def about_type(self):
        return self.get_field('AboutType')


# Schema parsing methods

def load_schema_from_file(file, schema_dir):
    with open(schema_dir + file, newline='') as jsonfile:
        data = json.load(jsonfile)
        return data


def load_schema(file, schema_dir):
    with open(schema_dir + file, newline='') as jsonfile:
        data = json.load(jsonfile)
        return data


def set_attr(schema, key, value):
    # ToDo: Use base schema to compare incoming values #
    if key in schema:
        schema[key] = value
        return schema
    else:
        raise Exception('Error: "' + key + '" is not a valid part of the schema')


def custom_field_schema():
    return {
        "Value": "string",
        "ID": 0,
        "Name": "string"
    }


def get_custom_field_id(schema, name):
    try:
        return [i for i in schema if i['Name'] == name][0]['ID']
    except:
        return None


def get_custom_field_type(schema, name):
    try:
        return [i for i in schema if i['Name'] == name][0]['FieldType']
    except:
        return None


def get_custom_field_values(schema, name):
    try:
        return [i for i in schema if i['Name'] == name][0]['PossibleValues']
    except:
        return None


def set_custom_attr(schema, key, value, randomize=False, random_upper=3):
    record = custom_field_schema()
    type = get_custom_field_type(schema, key)
    values = get_custom_field_values(schema, key)
    id = get_custom_field_id(schema, key)
    record['ID'] = id
    record['Name'] = key
    if type == 'List':
        if value not in values:
            raise Exception('Error: "{value}" is not a valid value. Possible values are: {values}'.format(value=value,
                                                                                                          values=', '.join(
                                                                                                              values)))
        else:
            if randomize:
                random_val = (random.randint(0, (len(values) - 1)))
                record['Value'] = values[random_val]
            else:
                record['Value'] = value
    elif type == 'Boolean':
        pass
    elif type == 'Integer':
        try:
            record['Value'] = int(value)
        except:
            raise Exception('Error: "' + key + '" must be an integer')
    elif type == 'Number':
        try:
            record['Value'] = int(value)
        except:
            raise Exception('Error: "' + key + '" must be an number')

    else:
        try:
            record['Value'] = str(value)
        except:
            raise Exception('Error: "' + key + '" must be a string')
    return record

# Function for loading data

def import_id_list(path):
    out = []

    def process_file(path):
        out = []
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if (row[0].isdigit()):
                    out.append(int(row[0]))
        return out

    if exists(path) is False:
        print(("{file} is missing or is not a valid CSV file".format(file=path)))
    else:
        if (os.path.isdir(path)):
            print("Processing Folder {folder}".format(folder=path))
            for f in (os.listdir(path)):
                out += process_file(path + f)
        elif (os.path.isfile(path)):
            print("Processing File {file}".format(file=path))
            out = process_file(path)
    return sorted(list(set(out)))


