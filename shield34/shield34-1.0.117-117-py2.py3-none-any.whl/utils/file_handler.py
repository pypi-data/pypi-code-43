import fnmatch
import os

import requests


def upload_file(url, file):

    http_response = requests.put(url, data=file)
    if http_response.status_code == 200:
        return True
    else:
        return False

class FileHandler:

    @staticmethod
    def find_files(directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    return filename

        return ""
