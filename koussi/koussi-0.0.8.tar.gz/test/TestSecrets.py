import pprint
import unittest

from koussi.secrets import Secrets


class TestSecrets(unittest.TestCase):

    def test_import(self):
        params = {'keybase': {'user': 'pavelch', 'project': 'facebook'},
                  'envs': {'CYCOBOT_MESSAGE_API_KEY': 'ghghjg', 'FOO': 'bar', 'DD_API_KEY': 'key'}}
        my_secrets = Secrets(**params)()
        pprint.pprint(my_secrets)
        assert len(my_secrets) == 6

    def test_project(self):
        params = {'keybase': {'user': 'pavelch', 'project': 'passwords'}}
        my_secrets = Secrets(**params)()
        assert my_secrets['one'] == 'pass'


if __name__ == '__main__':
    unittest.main()
