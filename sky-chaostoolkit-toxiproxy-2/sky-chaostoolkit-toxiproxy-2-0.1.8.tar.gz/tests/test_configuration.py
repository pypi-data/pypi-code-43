import unittest
from toxiproxy import Toxiproxy
from chaostp import get_servers

t = Toxiproxy()


class TestConfiguration(unittest.TestCase):

    def test_toxiproxy_servers(self):

        conf = {
            "toxiproxy": [
                {
                    "host": "server1_host"
                },
                {
                    "host": "server2_host",
                    "port": 9999
                }
            ]
        }
        servers = get_servers(conf)
        self.assertEqual(len(servers), 2)

        conf = {
            "toxiproxy_host": "foo",
            "toxiproxy_port": 1111
        }
        servers = get_servers(conf)
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]["host"], "foo")
