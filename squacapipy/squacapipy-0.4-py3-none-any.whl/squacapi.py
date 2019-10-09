import requests
import os
import json
from squacapipy.errors import APITokenMissingError, APIBaseUrlError
from datetime import datetime


API_TOKEN = os.getenv('SQUAC_API_TOKEN')
API_BASE_URL = os.getenv('SQUAC_API_BASE')


if API_TOKEN is None:
    raise APITokenMissingError(
        "All methods require an API key"
    )

if API_BASE_URL is None:
    raise APIBaseUrlError(
        "All methods require a base API url"
    )

HEADERS = {'Content-Type': 'application/json',
           'Authorization': API_TOKEN}


def serialize_object(obj):
    '''for objects that don't natively serialize such as datetime'''
    if isinstance(obj, datetime):
        return obj.__str__()


class Response():
    '''simple custom response object

        takes requests obj text and turns into
        python dict
    '''
    def __init__(self, status_code, body, response_header):
        self.status_code = status_code
        self.body = body
        self.response_header = response_header


class SquacapiBase():
    def __init__(self, app, resource):
        self. app = app
        self.resource = resource

    def uri(self):
        return API_BASE_URL + "/" + self.app + "/" + self.resource + "/"

    def make_response(self, response):
        '''raise for errors, returns Response obj'''
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return Response(e.response.status_code,
                            json.loads(e.response.text), e.response.headers)

        return Response(response.status_code,
                        json.loads(response.text), response.headers)

    def get(self, **kwargs):
        '''get resources'''
        uri = self.uri()
        response = requests.get(uri, headers=HEADERS, params=kwargs)
        return self.make_response(response)

    def post(self, payload):
        '''create resources'''
        uri = self.uri()
        response = requests.post(
            uri,
            headers=HEADERS,
            data=json.dumps(payload, default=serialize_object))
        return self.make_response(response)

    def put(self, id, payload):
        '''update resource

           Must have trailing slash after id!!
        '''
        uri = self.uri() + id + "/"
        response = requests.put(uri, headers=HEADERS,
                                data=json.dumps(payload))

        return self.make_response(response)


'''Nslc classes

    * NslcBase inherits from SquacapiBase,
    * Network, Channel, and Group inherit from NslcBase
'''


class NslcBase(SquacapiBase):
    def __init__(self, resource):
        app = "nslc"
        super().__init__(app, resource)


class Network(NslcBase):
    def __init__(self):
        resource = "networks"
        super().__init__(resource)


class Channel(NslcBase):
    def __init__(self):
        resource = "channels"
        super().__init__(resource)


class Group(NslcBase):
    def __init__(self):
        resource = "groups"
        super().__init__(resource)


'''Measurement classes

    * MeasurentBase inherits from SquacapiBase,
    * Measurement, and Metric inherit from MeasurentBase
'''


class MeasurementBase(SquacapiBase):
    def __init__(self, resource):
        app = "measurement"
        super().__init__(app, resource)


class Metric(MeasurementBase):
    def __init__(self):
        resource = "metrics"
        super().__init__(resource)


class Measurement(MeasurementBase):
    def __init__(self):
        resource = "measurements"
        super().__init__(resource)


class DashboardBase(SquacapiBase):
    def __init__(self, resource):
        app = "dashboard"
        super().__init__(app, resource)


class Dashboard(DashboardBase):
    def __init__(self):
        resource = "dashboards"
        super().__init__(resource)


class Widget(DashboardBase):
    def __init__(self):
        resource = "widgets"
        super().__init__(resource)


class WidgetType(DashboardBase):
    def __init__(self):
        resource = "widgettypes"
        super().__init__(resource)
