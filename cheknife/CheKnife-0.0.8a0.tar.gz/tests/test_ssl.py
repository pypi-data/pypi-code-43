from CheKnife import ssl
from ssl import PROTOCOL_TLSv1_2
from unittest import TestCase
from requests import Session
# nosetests --with-coverage --cover-inclusive --cover-package=CheKnife --cover-html tests/test_ssl.py


class SslTestCase(TestCase):
    def test_TLSVersionAdapter(self):
        for version in ['1', '1.1', '1.2', '2-3', 'client', 'server', 'made up']:
            self.assertIsInstance(ssl.tls_version_sessionmaker(version), Session)

        self.assertEqual(ssl.TLSVersionAdapter(ssl_version='wrong').ssl_version, PROTOCOL_TLSv1_2)