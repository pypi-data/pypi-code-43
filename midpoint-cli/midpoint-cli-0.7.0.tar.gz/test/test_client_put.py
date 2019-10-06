import unittest

from midpoint_cli.mpclient import MidpointClient, RestApiClient, MidpointUnsupportedOperation


class ResultMockup:
    status_code = 200


class SessionMockup:
    def __init__(self):
        self.put_invocations = 0

    def put(self, *args, **kwargs):
        self.put_invocations += 1
        return ResultMockup()


class RestApiClientMockup(RestApiClient):
    def __init__(self):
        self.url = 'http://mockup/midpoint/'
        self.username = 'username'
        self.password = 'password'
        self.requests_session = SessionMockup()


class ClientApiTest(unittest.TestCase):
    def test_put_single(self):
        mockup = RestApiClientMockup()
        client = MidpointClient(api_client=mockup)
        res = client.put_xml(xml_file='sandbox-environment/resource-repository1.xml')
        self.assertEqual(res, ('resource', 'e510e0d9-3fc0-417c-a5cd-88d452b229e8'))
        self.assertEqual(1, mockup.requests_session.put_invocations)

    def test_put_multiple(self):
        mockup = RestApiClientMockup()
        client = MidpointClient(api_client=mockup)
        with self.assertRaises(MidpointUnsupportedOperation) as context:
            client.put_xml(xml_file='sample-objects-01.xml')


if __name__ == '__main__':
    unittest.main()
