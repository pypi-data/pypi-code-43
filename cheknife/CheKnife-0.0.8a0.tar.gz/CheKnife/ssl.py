import requests
import ssl
from warnings import warn
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager


class TLSVersionAdapter(HTTPAdapter):
    poolmanager = None
    ssl_versions = {
        '1': ssl.PROTOCOL_TLSv1,
        '1.1': ssl.PROTOCOL_TLSv1_1,
        '1.2': ssl.PROTOCOL_TLSv1_2,
        '2-3': ssl.PROTOCOL_SSLv23,
        'client': ssl.PROTOCOL_TLS_CLIENT,
        'server': ssl.PROTOCOL_TLS_SERVER,
    }

    def __init__(self, ssl_version='1.2', **kwargs):
        self.ssl_version = self.get_ssl_version(str(ssl_version))

        super(TLSVersionAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block, ssl_version=self.ssl_version)

    def get_ssl_version(self, version):
        try:
            return self.ssl_versions[version]
        except KeyError:
            warn(f'SSL Version not found for: {version}\nUsing default TLSv1.2.\n'
                 f'Supported versions are {list(self.ssl_versions.keys())}')
            return ssl.PROTOCOL_TLSv1_2


def tls_version_sessionmaker(tls_version='1.2'):
    session = requests.Session()
    session.mount('https://', TLSVersionAdapter(tls_version))
    return session
