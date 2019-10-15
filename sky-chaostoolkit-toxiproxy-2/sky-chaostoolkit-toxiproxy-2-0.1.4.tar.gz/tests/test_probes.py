import unittest
import re
from toxiproxy import Toxiproxy
from chaostp.proxy.probes import server_running, get_proxies, get_proxy, \
        api_version, get_num_toxics
from chaostp.proxy.actions import delete_all_proxies, create_proxy, add_toxic

t = Toxiproxy()


def cmp_version(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]
    return normalize(version1) >= normalize(version2)


class TestProbes(unittest.TestCase):

    def test_server_running(self):
        self.assertEqual(t.running(), server_running())

    @unittest.skipIf(
        t.running() is False,
        "Test skipped: toxiproxy server not running")
    def test_get_toxics(self):
        delete_all_proxies()
        create_proxy(
            proxy_name="test_proxy",
            upstream="localhost:8888",
            listen="localhost:9999",
            enabled=False
        )
        add_toxic(
            proxy_name="test_proxy",
            type="latency",
            stream="downstream",
            attributes={"latency": 1000}
        )
        add_toxic(
            proxy_name="test_proxy",
            type="latency",
            stream="upstream",
            attributes={"latency": 1000}
        )
        self.assertEqual(get_num_toxics("test_proxy"), 2)

    @unittest.skipIf(
        t.running() is False,
        "Test skipped: toxiproxy server not running")
    def test_version(self):
        self.assertTrue(cmp_version(api_version(), '2.0'))

    @unittest.skipIf(
        t.running() is False,
        "Test skipped: toxiproxy server not running")
    def test_get_proxies(self):
        delete_all_proxies()
        create_proxy(
            proxy_name="test_proxy_1",
            upstream="localhost:8888",
            listen="localhost:9999",
            enabled=False
        )
        create_proxy(
            proxy_name="test_proxy_2",
            upstream="localhost:8888",
            listen="localhost:9999",
            enabled=False
        )
        proxies = get_proxies()
        self.assertEqual(len(proxies), 2)

    @unittest.skipIf(
        t.running() is False,
        "Test skipped: toxiproxy server not running")
    def test_get_proxy(self):
        delete_all_proxies()
        create_proxy(
            proxy_name="test_proxy",
            upstream="localhost:8080",
            listen="localhost:80",
            enabled=False
        )

        name = get_proxy("test_proxy")
        self.assertEqual(name, "test_proxy")


if __name__ == "__main__":
    unittest.main()
