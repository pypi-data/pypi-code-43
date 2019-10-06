import unittest

from midpoint_cli.mpclient import RestApiClient, MidpointClient


class NamespaceMockup:
    url = 'http://mockup/midpoint/'
    username = 'mockup USERNAME'
    password = 'mockup PASSWORD'


class ClientApiTest(unittest.TestCase):
    def test_url_sanitization(self):
        client = RestApiClient('http://localhost:8080/dumbo', '', '')
        self.assertEqual(client.url, 'http://localhost:8080/midpoint/')

    def test_rest_types(self):
        client = RestApiClient('http://localhost:8080/dumbo', '', '')
        self.assertEqual(client.resolve_rest_type('task'), 'tasks')

        try:
            client.resolve_rest_type('bogus')
            self.fail()
        except AttributeError:
            pass

    def test_client_from_namespace(self):
        ns = NamespaceMockup()
        client = MidpointClient(ns)
        self.assertEqual(ns.url, client.api_client.url)
        self.assertEqual(ns.username, client.api_client.username)
        self.assertEqual(ns.password, client.api_client.password)

    def test_client_from_object(self):
        api_client = RestApiClient('cli-url', 'cli-usr', 'cli-pwd')
        client = MidpointClient(api_client=api_client)
        self.assertEqual(api_client, client.api_client)

    def test_client_from_priority(self):
        ns = NamespaceMockup()
        api_client = RestApiClient('cli-url', 'cli-usr', 'cli-pwd')
        client = MidpointClient(api_client=api_client, ns=ns)
        self.assertEqual(api_client, client.api_client)


if __name__ == '__main__':
    unittest.main()
