import base64
import tempfile
import os
import uuid
from os import path
from src.driver.by import By


class FileToStringUtils:

    BY_IMAGE = "By.Image: "

    def prepare_locator(self, by):
        prepared_by = None
        if not by is None and str(by).startswith(self.BY_IMAGE):
            locator_file = str(by).split(self.BY_IMAGE)[1]
            if path.exists(locator_file):
                encoded_file_locator = self.convert_file_to_base64_string(locator_file)
                prepared_by = By().image(encoded_file_locator)
                return prepared_by

        return by
        
    def convert_to_file(self, source, extension):
        temp_dir = tempfile.gettempdir()
        rokuality_temp_dir = str(temp_dir) + os.path.sep + "com.rokuality"
        if not os.path.exists(rokuality_temp_dir):
            os.makedirs(rokuality_temp_dir)

        decoded_str = base64.b64decode(source)
        artifact_file = str(rokuality_temp_dir) + os.path.sep + str(uuid.uuid1()) + extension
        with open(artifact_file, 'wb') as f:
            f.write(decoded_str)
        return artifact_file

    def convert_file_to_base64_string(self, file):
        if path.exists(file):
            with open(file, "rb") as file_to_convert:
                encoded_data = base64.b64encode(file_to_convert.read())
            if encoded_data is not None:
                return encoded_data.decode("utf-8")

        return None
