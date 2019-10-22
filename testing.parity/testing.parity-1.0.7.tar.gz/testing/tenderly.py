import os
import signal
import urllib.request
import json

from testing.common.database import (
    Database, DatabaseFactory, get_path_of, get_unused_port
)

__all__ = ['TenderlyServer', 'TenderlyServerFactory']

class TenderlyServer(Database):

    DEFAULT_SETTINGS = dict(
        auto_start=2,
        base_dir=None,
        copy_data_from=None,
        tenderly_cmd=None,
        target_host='127.0.0.1',
        target_port=None,
        proxy_host='127.0.0.1',
        port=None
    )

    def initialize(self):
        self.tenderly_cmd = self.settings.get('tenderly_cmd')
        if self.tenderly_cmd is None:
            self.tenderly_cmd = get_path_of('tenderly')

    def url(self):
        return "http://localhost:{}".format(self.settings['port'])

    def get_faucet_private_key(self):
        return self.faucet_private_key

    def get_data_directory(self):
        return os.path.join(self.base_dir, 'data')

    def prestart(self):
        super(TenderlyServer, self).prestart()

        if self.settings['target_port'] is None:
            raise Exception("target_port must be set")

    def get_server_commandline(self):
        cmd = [self.tenderly_cmd, "proxy",
               "--force",
               "--proxy-host", self.settings['proxy_host'],
               "--proxy-port", str(self.settings['port']),
               "--target-host", self.settings['target_host'],
               "--target-port", str(self.settings['target_port'])]

        return cmd

    def is_server_available(self):
        try:
            urllib.request.urlopen(
                urllib.request.Request(
                    self.url(),
                    headers={'Content-Type': "application/json"},
                    data=json.dumps({
                        "jsonrpc": "2.0",
                        "id": "1234",
                        "method": "eth_getBalance",
                        "params": ["0x0000000000000000000000000000000000000000", "latest"]
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

class TenderlyServerFactory(DatabaseFactory):
    target_class = TenderlyServer

def wrap_parity_with_tenderly(parity_server, tenderly_cmd=None):
    return TenderlyServer(
        target_port=parity_server.settings['jsonrpc_port'],
        tenderly_cmd=tenderly_cmd
    )
