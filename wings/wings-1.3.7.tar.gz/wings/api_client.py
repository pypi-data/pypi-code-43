import atexit
import importlib
import logging

import requests


class ApiClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.session = requests.Session()
        self.libns = self.get_export_url() + "components/library.owl#"
        self.dcdom = self.get_export_url() + "data/ontology.owl#"
        self.dclib = self.get_export_url() + "data/library.owl#"
        self.xsdns = "http://www.w3.org/2001/XMLSchema#"
        self.topcls = "http://www.wings-workflows.org/ontology/component.owl#Component"

        if self.login(kwargs["password"]) is False:
            raise ValueError("Login failed")

        atexit.register(self.logout)

    def get_server(self):
        return self.server

    def get_username(self):
        return self.username

    def login(self, password):
        self.session.get(self.server + "/sparql")
        data = {"j_username": self.username, "j_password": password}
        response = self.session.post(self.server + "/j_security_check", data)
        if response.status_code == 403 or response.status_code == 200:
            return True
        return False

    def logout(self):
        self.session.get(self.server + "/jsp/login/logout.jsp")
        self.session.close()

    def session(self):
        return self.session

    def _initialize(self, name):
        try:
            module_ = importlib.import_module(".%s" % name, __package__)
            try:
                class_ = getattr(module_, name.title())
                return class_(api_client=self)
            except AttributeError:
                logging.error("Class does not exist")
        except ImportError:
            logging.error("Module does not exist %s", name)

    def close(self):
        """
        Shutdown sessions across all instantiated services
        """
        self.logout()

    def __getattr__(self, attr):
        try:
            setattr(self, attr, self.kwargs[attr])
            return getattr(self, attr)
        except KeyError:
            setattr(self, attr, self._initialize(attr))
            return getattr(self, attr)

    def get_request_url(self):
        return self.server + "/users/" + self.username + "/" + self.domain + "/"

    def get_export_url(self):
        return (
            self.export_url + "/export/users/" + self.username + "/" + self.domain + "/"
        )

    @staticmethod
    def check_request(resp):
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise requests.exceptions.HTTPError
        except requests.exceptions.RequestException:
            raise requests.exceptions.RequestException
        return resp
