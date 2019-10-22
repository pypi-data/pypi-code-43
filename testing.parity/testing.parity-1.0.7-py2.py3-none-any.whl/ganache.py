import os
import signal
import urllib.request
import json

from ethereum.utils import privtoaddr, decode_hex

from testing.common.database import (
    Database, DatabaseFactory, get_path_of
)

__all__ = ['GanacheServer', 'GanacheServerFactory']

DEFAULT_STARTGAS = 21000
DEFAULT_GASPRICE = 20000000000

class GanacheServer(Database):

    DEFAULT_SETTINGS = dict(auto_start=2,
                            base_dir=None,
                            ganache_server=None,
                            faucet_private_key=None,
                            port=None,
                            network_id=66,
                            min_gas_price=None,
                            copy_data_from=None)

    subdirectories = ['data', 'tmp']

    def initialize(self):
        self.ganache_server = self.settings.get('ganache_server')
        if self.ganache_server is None:
            self.ganache_server = get_path_of('ganache-cli')

        self.faucet_private_key = self.settings.get('faucet_private_key')
        if self.faucet_private_key is None:
            self.faucet_private_key = os.urandom(32)
        elif isinstance(self.faucet_private_key, str):
            self.faucet_private_key = decode_hex(self.faucet_private_key)

        self.author = self.settings.get('author')

        network_id = self.settings.get('network_id')
        if not isinstance(network_id, int):
            try:
                network_id = int(network_id, 16)
            except ValueError:
                raise Exception("Network ID must be an integer or hex string")
        self.network_id = network_id

    def dsn(self, **kwargs):
        return {'url': self.url(),
                'network_id': self.network_id}

    def url(self):
        return "http://localhost:{}".format(self.settings['port'])

    def get_faucet_private_key(self):
        return self.faucet_private_key

    def get_data_directory(self):
        return os.path.join(self.base_dir, 'data')

    def prestart(self):
        super(GanacheServer, self).prestart()

    def get_server_commandline(self):
        pkhex = self.faucet_private_key.hex()

        cmd = [self.ganache_server,
               "-p", str(self.settings['port']),
               "-i", str(self.network_id),
               f"--account=\"0x{pkhex},1606938044258990275541962092341162602522202993782792835301376\""]

        print(cmd)
        return cmd

    def is_server_available(self):
        try:
            urllib.request.urlopen(
                urllib.request.Request(
                    self.dsn()['url'],
                    headers={'Content-Type': "application/json"},
                    data=json.dumps({
                        "jsonrpc": "2.0",
                        "id": "1234",
                        "method": "eth_getBalance",
                        "params": ["0x{}".format(self.author), "latest"]
                    }).encode('utf-8')
                ))
            return True
        except Exception as e:
            if not hasattr(e, 'reason') or not isinstance(e.reason, ConnectionRefusedError):
                print(e)
            return False

    def pause(self):
        """stops service, without calling the cleanup"""
        self.terminate(signal.SIGTERM)

class GanacheServerFactory(DatabaseFactory):
    target_class = GanacheServer
