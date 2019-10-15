import unittest
import requests

from http.client import HTTPConnection

from toxiproxy import Toxiproxy
from chaostp.proxy.actions import delete_all_proxies, delete_proxy, \
    create_proxy, enable_proxy, disable_proxy, add_toxic, reset_server, \
    reset_all, populate, delete_toxic
from chaostp.proxy.probes import get_num_toxics

import logging
HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

t = Toxiproxy()


@unittest.skipIf(
    t.running() is False,
    "Test skipped: toxiproxy server not running")
class TestActions(unittest.TestCase):

    def test_reset_server(self):
        self.assertEqual(reset_server(), True)

    def test_reset_all(self):
        self.assertEqual(reset_all(), True)

    def test_delete_proxy(self):
        self.test_create_proxy()
        ret = delete_proxy(proxy_name="test_proxy")
        self.assertEqual(ret, True)
        proxy = requests.get('http://127.0.0.1:8474/proxies/test_proxy').json()
        self.assertEqual(proxy['error'], 'proxy not found')

    def test_create_proxy(self):
        delete_all_proxies()
        proxy = create_proxy(
            proxy_name="test_proxy",
            upstream="127.0.0.1:8080",
            listen="127.0.0.1:9000",
            enabled=False
        )
        proxy = requests.get('http://127.0.0.1:8474/proxies/test_proxy').json()
        self.assertEqual(proxy['name'], 'test_proxy')

    def test_enable_proxy(self):
        self.test_create_proxy()
        enable_proxy(proxy_name="test_proxy")
        proxy = requests.get('http://127.0.0.1:8474/proxies/test_proxy').json()
        self.assertEqual(proxy['enabled'], True)

    def test_disable_proxy(self):
        #         import pdb; pdb.set_trace()
        self.test_enable_proxy()
        disable_proxy(proxy_name="test_proxy")
        proxy = requests.get('http://127.0.0.1:8474/proxies/test_proxy').json()
        self.assertEqual(proxy['enabled'], False)

    def test_delete_toxic(self):
        delete_all_proxies()
        create_proxy(
            proxy_name="test_proxy",
            upstream="127.0.0.1:8888",
            listen="127.0.0.1:9999",
            enabled=False
        )
        add_toxic(
            proxy_name="test_proxy",
            type="latency",
            stream="downstream",
            attributes={"latency": 1000}
        )

        # the next should add a toxic to the same (only) proxy...
        add_toxic(
            type="latency",
            stream="upstream",
            attributes={"latency": 1000}
        )
        delete_toxic(
            proxy_name="test_proxy",
            type="latency",
            stream="downstream"
        )
        self.assertEqual(get_num_toxics("test_proxy"), 1)

    def test_add_toxic(self):
        #         import pdb;pdb.set_trace()
        self.test_create_proxy()
        add_toxic(
            proxy_name="test_proxy",
            type="latency",
            stream="upstream",
            attributes={"latency": 1000}
        )
        proxy = requests.get('http://127.0.0.1:8474/proxies/test_proxy').json()
        self.assertEqual(len(proxy['toxics']), 1)
        toxic = proxy['toxics'][0]
        self.assertEqual(toxic['name'], "latency_upstream")

    def test_create_bandwith_degradation_toxic(self):
        self.test_create_proxy()
        add_toxic(
            proxy_name="test_proxy",
            toxic_name="bandwith_degradation_toxic",
            type="bandwidth",
            stream="upstream",
            toxicity=0.5,
            attributes={"rate": 400}
        )
        proxy = requests.get('http://127.0.0.1:8474/proxies/test_proxy').json()
        self.assertEqual(len(proxy['toxics']), 1)
        toxic = proxy['toxics'][0]
        self.assertEqual(toxic['name'], "bandwith_degradation_toxic")
        self.assertEqual(toxic['toxicity'], 0.5)

    def test_create_toxic_proxy_not_existent(self):
        self.test_create_proxy()
        ret = add_toxic(
            proxy_name="foo_bar",
            toxic_name="bandwith_degradation_toxic",
            type="bandwidth",
            stream="upstream",
            toxicity=0.5,
            attributes={"rate": 400}
        )
        self.assertEqual(ret, -1)

    def test_populate(self):

        proxies = [
            {
                "name": "test_toxiproxy_populate1",
                "upstream": "127.0.0.1:3306",
                "listen": "127.0.0.1:3307"
            },
            {
                "name": "test_toxiproxy_populate2",
                "upstream": "127.0.0.1:3308",
                "listen": "127.0.0.1:3309",
            },
        ]

        num = populate(proxies)
        self.assertEqual(num, 2)


if __name__ == "__main__":
    unittest.main()
