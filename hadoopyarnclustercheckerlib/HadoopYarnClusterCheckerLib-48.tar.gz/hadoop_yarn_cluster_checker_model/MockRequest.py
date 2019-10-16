import os
from pathlib import Path

import requests

from UtilsTest import UtilsTest
from MockResponse import MockResponse


class MockRequest:
    __file_running_app = os.path.dirname(__file__) + "/res/running_app.json"
    __file_empty = os.path.dirname(__file__) + "/test/res/empty_cluster.json"
    def __init__(self, has_internet: bool, are_jobs_running: bool):
        self.hasInternet = has_internet
        self.are_jobs_running = are_jobs_running

    def __load_xml_files(self, isJobRunning: bool):
        cwd = Path(os.getcwd())
        print(cwd)
        file_path = ""
        if isJobRunning:
            file_path = UtilsTest.get_file_running_app(self)
        else:
            file_path = UtilsTest.get_file_empty_cluster(self)
        with open(file_path, "r") as xmlFile:
            xmlText = xmlFile.read()
            return MockResponse(xmlText)

    def __load_running_jobs_xml(self):
        cwd = Path(os.getcwd())
        file_path =  "/test/res/running_app.json"
        with open(self.__file_running_app, "r") as successResponseBodyFile:
            xml_text = successResponseBodyFile.read()
            return MockResponse(xml_text)

    def get(self, host):
        if self.hasInternet:
            return requests.get(host)
        return self.__load_xml_files(self.are_jobs_running)
