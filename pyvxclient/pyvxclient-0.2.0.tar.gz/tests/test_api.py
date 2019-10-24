from unittest import TestCase
from pyvxclient.client import Client
from pyvxclient.errors import NotAuthorized, EndpointURLNotFound, WrongCredentials
import requests_mock
from tests.data import api
from tests.data.spec import spec


# TODO: improve tests


class TestApi(TestCase):

    def setUp(self) -> None:
        requests_mocker = requests_mock.Mocker()
        base_url = 'https://vxapitest-test-test.vx.se/public/not_exist_for_test'
        requests_mocker.get(base_url + '/api/v1/spec', json=spec,
                            status_code=200, headers={'Content-Type': 'application/json'})
        self.api_key = "202803e1003a4b1932701da04ea3d698a73346c47a68f0882c84fc893f843c60"
        requests_mocker.get(base_url + '/api/v1/api/api_key', json={
            "api_key": self.api_key,
            "expires": "2019-05-14T21:25:19.956397+00:00"
        }, status_code=200, headers={'Content-Type': 'application/json'})

        self.base_url = base_url
        self.requests_mocker = requests_mocker
        self.requests_mocker.start()

        # re-raise exception just for documentation
        try:
            # deve finire con /
            client = Client(url=self.base_url + '/', cache_path='/tmp/pyvxclient.swagger.json')
            '''
            err: cannot load vxapi client
            err: expected str, bytes or os.PathLike object, not NoneType
            '''
            token = client.get_token('massimo', 'password')
            # non richiamare la set_api_key
            client.api_key = token['api_key']
            client.setup()
        except NotAuthorized as e:
            print("err: user not authorized, please login again")
            raise e
        except EndpointURLNotFound as e:
            print("err: %s" % e)
            raise e
        except WrongCredentials as e:
            print("err: %s" % e)
            raise e
        except ConnectionError as e:
            print("err: endpoint could not be contacted: %s" % e)
            raise e
        except Exception as e:
            print("err: cannot load vxapi client")
            print("err: %s" % e)
            raise e

        self.client = client

    def tearDown(self) -> None:
        self.requests_mocker.stop()

    def test_get_single(self) -> None:
        self.requests_mocker.get(self.base_url +
                                 '/api/v1/api?api_key={}'.format(self.api_key),
                                 json=api.api,
                                 status_code=200, headers={'Content-Type': 'application/json'})

        ret = self.client.Api.get()
        self.assertTrue(ret.json)
