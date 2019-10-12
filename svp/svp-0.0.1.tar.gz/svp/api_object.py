import requests
import json
import os


class APIAssert(object):
    def assertResponse(self, actual_response, expected_status, optional_request=None):
        """Custom assertion wrapper that provides response information on failure.

        Arguments:
        actual_response: APIResponse containing actual response from server.

        expected_response: int of expected response status code

        Raises:
        AssertionError if error is found.
        """
        try:
            assert actual_response['status_code'] == expected_status
        except AssertionError as err:
            if optional_request:
                print("---Request payload---\n{}".format(optional_request))
            print("---Response---\n{}".format(actual_response))
            raise err


class APIResponse(dict):

    def __init__(self, response):
        """Initalizer for APIResponse.

        Parse a request response into a dict format.
        Also handle custom response behaviours via the
        custom_response() method.
        """
        self._response = response
        self['status_code'] = response.status_code
        self._custom_response(response)

    def __getitem__(self, key):
        """Override __getitme__.
        
        This replaces the KeyError behaviour with a ('unknown key', None)
        pattern which is better suited to many test automation contexts.
        """
        try:
            return super().__getitem__(key)
        except KeyError:
            super().__setitem__(key, None)

        return super().__getitem__(key)

    def _custom_response(self, response):
        """Handle custom response behaviours.""" 
        try:
            super().__init__(response.json())
        except json.decoder.JSONDecodeError as err:
            super().__init__({})


class API(object):
    """ApiObject - base object similar to page object."""

    def __init__(self, base_url=None):
        self.session = requests.Session()
        self.headers = {}
        self.base_url = base_url

    def _set_headers(self, headers):
        all_headers = {}
        all_headers.update(self.headers)
        if headers:
            all_headers.update(headers)
        
        return all_headers

    def post(self, api_call, data, headers=None):
        """Basic POST request."""
        all_headers = self._set_headers(headers)
        
        response = self.session.post(
            "{}{}".format(self.base_url, api_call),
            data=json.dumps(data),
            headers=all_headers
        )
        return APIResponse(response)

    def get(self, api_call, data={}, headers=None):
        """Basic GET request."""
        all_headers = self._set_headers(headers)
        
        response = self.session.get(
            "{}{}".format(self.base_url, api_call),
            data=json.dumps(data),
            headers=all_headers
        )
        return APIResponse(response)

    def delete(self, api_call, data={}, headers=None):
        """Basic DELETE request."""
        all_headers = self._set_headers(headers)

        response = self.session.delete(
            "{}{}".format(self.base_url, api_call),
            data=json.dumps(data),
            headers=all_headers
        )
        return APIResponse(response)

    def put(self, api_call, data, headers=None):
        """Basic PUT request."""
        all_headers = self._set_headers(headers)

        response = self.session.put(
            "{}{}".format(self.base_url, api_call),
            data=json.dumps(data),
            headers=all_headers
        )
        return APIResponse(response)

    def patch(self, api_call, data, headers=None):
        """Basic PATCH request."""
        all_headers = self._set_headers(headers)

        response = self.session.patch(
            "{}{}".format(self.base_url, api_call),
            data=json.dumps(data),
            headers=all_headers
        )
        return APIResponse(response)

    def close(self):
        self.session.close()
