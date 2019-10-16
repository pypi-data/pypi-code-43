import json
import os
from os import path
from src.utils.file_to_string_utils import FileToStringUtils

class BaseDriver:

    session = None
    server_url = None

    def set_session(self, session):
        self.session = session

    def get_session(self):
        return self.session

    def set_server_url(self, server_url):
        self.server_url = server_url

    def get_server_url(self):
        return self.server_url

    def prepare_cap_json(self, capabilities):
        prepared_json = {}
        parsed_json = json.loads(capabilities)
        for key,value in parsed_json.items():
                if os.path.exists(value):
                    encoded_data = FileToStringUtils().convert_file_to_base64_string(value)
                    prepared_json[key] = str(encoded_data)
                else:
                    prepared_json[key] = value
            
        return prepared_json
