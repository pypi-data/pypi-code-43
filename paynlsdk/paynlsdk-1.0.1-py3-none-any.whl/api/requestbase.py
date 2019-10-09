from urllib.parse import urlencode
from abc import ABC, abstractmethod

from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.exceptions import SchemaException
from paynlsdk.validators import ParamValidator


class RequestBase(ABC):
    def __init__(self):
        self._api_token = None
        self._service_id = None
        self._raw_response = None
        self._response = None

    @property
    def api_token(self):
        return self._api_token

    @api_token.setter
    def api_token(self, api_token: str):
        self._api_token = api_token

    @property
    def service_id(self):
        return self._service_id

    @service_id.setter
    def service_id(self, service_id: str):
        self._service_id = service_id

    @property
    def raw_response(self):
        return self._raw_response

    @property
    @abstractmethod
    def response(self) -> ResponseBase:
        pass

    @abstractmethod
    def requires_api_token(self):
        pass

    @abstractmethod
    def requires_service_id(self):
        pass

    @abstractmethod
    def get_version(self):
        pass

    @abstractmethod
    def get_controller(self):
        pass

    @abstractmethod
    def get_method(self):
        pass

    @abstractmethod
    def get_query_string(self):
        pass

    def get_url(self):
        return 'v{0}/{1}/{2}/json'.format(self.get_version(), self.get_controller(), self.get_method())

    def get_std_parameters(self):
        rs = {}
        if self.requires_api_token():
            ParamValidator.assert_not_empty(self.api_token, 'api_token')
            rs["token"] = self.api_token
        if self.requires_service_id():
            ParamValidator.assert_not_empty(self.service_id, 'service_id')
            rs["serviceId"] = self.service_id
        return rs

    def to_query_string(self):
        rs = self.get_parameters()
        if rs.__len__() == 0:
            return ""
        return urlencode(rs)

    @abstractmethod
    def get_parameters(self):
        pass

    def handle_schema_errors(self, error_dict):
        if error_dict:
            raise SchemaException(error_dict)

