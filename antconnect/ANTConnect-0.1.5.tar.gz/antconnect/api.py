import time
import codecs
import json
import base64
import requests
from .logger import Logger


class API:
    _host = ""
    _access_token = ""
    _api_version = "1.0"
    _authenticated = False
    _logger = None

    def __init__(self, host: str):
        self._host = host
        self._logger = Logger()

    def turn_on_logging(self) -> None:
        self._logger.on()

    def turn_off_logging(self) -> None:
        self._logger.off()

    # def oauth_client(self, username: str, password: str) -> bool:
    #     self._authenticated = False
    #     response = self._make_request('/oauth/token', 'POST', {
    #         "grant_type": "password",
    #         "username": username,
    #         "password": password,
    #     })
    #     parsed_response = response.json()
    #     if 'access_token' not in parsed_response:
    #         return False
    #     self._access_token = parsed_response['access_token']
    #     self._authenticated = True
    #     return True

    def login(self, client_id: str, client_secret: str, username: str, password: str) -> bool:
        self._authenticated = False
        response = self._make_request('/oauth/token', 'POST', {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret
        })
        parsed_response = response.json()
        if 'access_token' not in parsed_response:
            raise SystemError("Please check credentials")
        self._access_token = parsed_response['access_token']
        self._authenticated = True
        return True

    # def oauth_token(self, client_id: str, client_secret: str) -> bool:
    #     self._authenticated = False
    #     response = self._make_request('/oauth/token', 'POST', {
    #         "grant_type": "client_credentials",
    #         "client_id": client_id,
    #         "client_secret": client_secret
    #     })
    #     parsed_response = response.json()
    #     if 'access_token' not in parsed_response:
    #         return False
    #     self._access_token = parsed_response['access_token']
    #     self._authenticated = True
    #     return True

    def _make_api_request(self, path: str, method: str,
                          parameters: dict = None) -> dict:
        parameters = {} if parameters is None else parameters
        if not self._authenticated:
            raise SystemError("You are not authenticated, please use login first.")

        data = parameters if method in ['GET', 'DELETE'] else json.dumps(
            parameters)
        url = 'api/{}/{}'.format(self._api_version, path)
        self._logger.log("")
        self._logger.log("request - [{}] {}".format(method, url), False)
        response = self._make_request(
            url,
            method,
            data,
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer {}".format(
                    self._access_token)
            })
        self._logger.log("response - [{}] {}\r\n".format(
            response.status_code, response.text), False)

        if response.text == '':
            return ''

        parsed_response = response.json()
        if 'message' in parsed_response:
            if parsed_response['message'] == 'Unauthenticated.':
                raise PermissionError('Unauthenticated')
            if parsed_response['message'] == "Too Many Attempts.":
                raise ProcessLookupError("Too many requests attempted")
        return parsed_response

    def _make_request(self, path: str, method: str, parameters: dict = None,
                      headers: dict = None) -> requests.Response:
        parameters = {} if parameters is None else parameters
        headers = {} if headers is None else headers
        url = '{}{}'.format(self._host, path)
        if method == 'GET':
            return requests.get(
                url, params=parameters, headers=headers)
        if method == 'PUT':
            return requests.put(
                url, data=parameters, headers=headers)
        if method == 'DELETE':
            return requests.delete(
                url, params=parameters, headers=headers)
        if method == 'POST':
            return requests.post(
                url, data=parameters, headers=headers)

        raise NotImplementedError("http method not implemented")

    def projects_read(self) -> [dict]:
        path = 'projects'
        return self._make_api_request(path, 'GET')

    def project_create(self, name: str) -> dict:
        path = 'project'
        return self._make_api_request(path, 'POST', {
            "name": name
        })

    def project_read(self, project_id: str) -> dict:
        path = 'project/{}'.format(project_id)
        return self._make_api_request(path, 'GET')

    def project_update(self, project_id: str, name: str) -> dict:
        path = 'project/{}'.format(project_id)
        return self._make_api_request(path, 'PUT', {
            "name": name
        })

    def project_delete(self, project_id: str) -> dict:
        path = 'project/{}'.format(project_id)
        return self._make_api_request(path, 'DELETE')

    def tables_read(self, project_id: str) -> [dict]:
        path = 'tables'
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id
        })

    def table_create(self, project_id: str, name: str) -> dict:
        path = 'table'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "name": name
        })

    def table_read(self, project_id: str, table_id: str) -> dict:
        path = 'table/{}'.format(table_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id
        })

    def table_update(self, project_id: str, table_id: str, name: str) -> dict:
        path = 'table/{}'.format(table_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "name": name
        })

    def table_delete(self, project_id: str, table_id: str) -> dict:
        path = 'table/{}'.format(table_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id
        })

    def columns_read(self, project_id: str, table_id: str) -> [dict]:
        path = 'columns'
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def column_create(self, project_id: str, table_id: str, name: str,
                      fieldtype: str, default_value: str = "",
                      options: list = None) -> dict:
        options = [] if options is None else options
        path = 'column'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name,
            "type": fieldtype,
            "options": options,
            "default": default_value,
            "required": True
        })

    def column_read(self, project_id: str, table_id: str, column_id):
        path = 'column/{}'.format(column_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def column_update(self, project_id: str, table_id: str, column_id: str,
                      name: str) -> dict:
        path = 'column/{}'.format(column_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name
        })

    def column_delete(self,
                      project_id: str, table_id: str, column_id: str) -> dict:
        path = 'column/{}'.format(column_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def records_create_csv(self, project_id: str, table_id: str,
                       records_csv: str) -> [dict]:
        path = 'records/import'
        with codecs.open(records_csv, mode="r", encoding='utf-8') as csv_file:
            encoded_csv = base64.b64encode(str.encode(csv_file.read()))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def records_create(self, project_id: str, table_id: str,
                       records: dict) -> [dict]:
        path = 'records/import'
        encoded_csv = base64.b64encode(self.create_virtual_csv(records).encode("utf-8"))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def records_read(self, project_id: str, table_id: str) -> dict:
        path = 'records'
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def records_delete(self, project_id: str, table_id: str,
                       records_ids: [str]) -> dict:
        path = 'records'
        parameters = {
            "project[id]": project_id,
            "table[id]": table_id
        }
        for i, record_id in enumerate(records_ids):
            parameters["records[{}]".format(i)] = record_id
        return self._make_api_request(path, 'DELETE', parameters)

    def records_verify_csv(self, project_id: str, table_id: str, records_csv: str) -> dict:
        path = 'records/verify'
        with codecs.open(records_csv, mode="r", encoding='utf-8') as csv_file:
            encoded_csv = base64.b64encode(str.encode(csv_file.read()))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def records_verify(self, project_id: str, table_id: str, records: list) -> dict:
        path = 'records/verify'
        encoded_csv = base64.b64encode(self.create_virtual_csv(records).encode("utf-8"))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def record_create(self, project_id: str, table_id: str,
                      record_values: dict) -> dict:
        path = 'record'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "record": record_values
        })

    def record_read(self, project_id: str, table_id: str,
                    record_id: str) -> dict:
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def record_update(self, project_id: str, table_id: str, record_id: str,
                      updated_record_values: dict) -> dict:
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "record": updated_record_values
        })

    def record_delete(self, project_id: str, table_id: str,
                      record_id: str) -> dict:
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def record_history(self, project_id: str, table_id: str,
                       record_id: str) -> dict:
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def revisions_read(self, project_id: str, table_id: str) -> dict:
        path = 'revisions'
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def revision_create(self, project_id: str, table_id: str,
                        name: str) -> dict:
        path = 'revision'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name,
            "timestamp": time.time()
        })

    def revision_read(self, project_id: str, table_id: str,
                      revision_id: str) -> dict:
        path = 'revision/{}'.format(revision_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def revision_update(self, project_id: str, table_id: str,
                        revision_id: str, name: str) -> dict:
        path = 'revision/{}'.format(revision_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name,
            "timestamp": time.time()
        })

    def revision_delete(self: str, project_id: str, table_id: str,
                        revision_id: str) -> dict:
        path = 'revision/{}'.format(revision_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    # def search(self, project_id: str, table_id: str, search_phrase: str,
    #            search_fields: [str]) -> dict:
    #     path = 'search'
    #     parameters = {
    #         "project[id]": project_id,
    #         "table[id]": table_id,
    #         "searchphrase": search_phrase
    #     }
    #     for i, search_field in enumerate(search_fields):
    #         parameters["searchfields[{}]".format(i)] = search_field
    #     return self._make_api_request(path, 'GET', parameters)

    def create_virtual_csv(self, records: list):
        encoded_csv = ",".join(records[0].keys())+"\n"
        for record in records:
            recs = []
            for key in record.keys():
                recs.append(record[key])
            encoded_csv += ",".join(recs)+"\n"
        return encoded_csv  