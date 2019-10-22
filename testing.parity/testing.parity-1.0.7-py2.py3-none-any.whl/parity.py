import binascii
import os
import signal
import subprocess
import urllib.request
import json
import re
import copy

from py_ecc.secp256k1 import privtopub
from ethereum.utils import encode_int32, privtoaddr, decode_hex

from testing.common.database import (
    Database, DatabaseFactory, get_path_of, get_unused_port
)

__all__ = ['ParityServer', 'ParityServerFactory']

DEFAULT_STARTGAS = 21000
DEFAULT_GASPRICE = 20000000000

# https://wiki.parity.io/Chain-specification
ethash_engine = {
    "Ethash": {
        "params": {
            "minimumDifficulty": "$difficulty",
            "difficultyBoundDivisor": "0x0800",
            "durationLimit": "0x0a",
            "homesteadTransition": "0x0"
        }
    }
}
ethash_genesis = {
    "seal": {
        "ethereum": {
            "nonce": "0x00006d6f7264656e",
            "mixHash": "0x00000000000000000000000000000000000000647572616c65787365646c6578"
        }
    },
    "author": "0x0000000000000000000000000000000000000000",
    "timestamp": "0x00",
    "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "extraData": "0x",
    "gasLimit": "0x2fefd8"
}
instant_engine = {
    "instantSeal": {
        "params": {}
    }
}
instant_genesis = {
    "seal": {
        "generic": "0x0"
    },
    "difficulty": "0x20000",
    "author": "0x0000000000000000000000000000000000000000",
    "timestamp": "0x00",
    "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "extraData": "0x",
    "gasLimit": "0x7A1200"
}
chain_json_params_2_5_7 = {
    "gasLimitBoundDivisor": "0x0400",
    "accountStartNonce": "0x0100000",
    "maximumExtraDataSize": "0x20",
    "minGasLimit": "0x1388",
    "eip150Transition": "0x0",
    "eip160Transition": "0x0",
    "eip161abcTransition": "0x0",
    "eip161dTransition": "0x0",
    "eip155Transition": "0x0",
    "eip140Transition": "0x0",
    "eip211Transition": "0x0",
    "eip214Transition": "0x0",
    "eip658Transition": "0x0",
    "eip145Transition": "0x0",
    "eip1014Transition": "0x0",
    "eip1052Transition": "0x0",
    "wasmActivationTransition": "0x0"
}
chain_json_params_2_5_8 = {
    "gasLimitBoundDivisor": "0x0400",
    "accountStartNonce": "0x0100000",
    "maximumExtraDataSize": "0x20",
    "minGasLimit": "0x1388",
    "eip150Transition": "0x0",
    "eip160Transition": "0x0",
    "eip161abcTransition": "0x0",
    "eip161dTransition": "0x0",
    "eip155Transition": "0x0",
    "eip98Transition": "0x7fffffffffffff",
    "maxCodeSize": 24576,
    "maxCodeSizeTransition": "0x0",
    "eip140Transition": "0x0",
    "eip211Transition": "0x0",
    "eip214Transition": "0x0",
    "eip658Transition": "0x0",
    "eip145Transition": "0x0",
    "eip1014Transition": "0x0",
    "eip1052Transition": "0x0",
    "wasmActivationTransition": "0x0"
}

chain_json_accounts_2_5_7 = {
    "0000000000000000000000000000000000000001": {"balance": "1", "builtin": {"name": "ecrecover", "pricing": {"linear": {"base": 3000, "word": 0}}}},
    "0000000000000000000000000000000000000002": {"balance": "1", "builtin": {"name": "sha256", "pricing": {"linear": {"base": 60, "word": 12}}}},
    "0000000000000000000000000000000000000003": {"balance": "1", "builtin": {"name": "ripemd160", "pricing": {"linear": {"base": 600, "word": 120}}}},
    "0000000000000000000000000000000000000004": {"balance": "1", "builtin": {"name": "identity", "pricing": {"linear": {"base": 15, "word": 3}}}},
    "0000000000000000000000000000000000000005": {"builtin": {"name": "modexp", "activate_at": "0x0", "pricing": {"modexp": {"divisor": 2}}}},
    "0000000000000000000000000000000000000006": {"builtin": {"name": "alt_bn128_add", "activate_at": "0x0", "pricing": {"linear": {"base": 500, "word": 0}}}},
    "0000000000000000000000000000000000000007": {"builtin": {"name": "alt_bn128_mul", "activate_at": "0x0", "pricing": {"linear": {"base": 40000, "word": 0}}}},
    "0000000000000000000000000000000000000008": {"builtin": {"name": "alt_bn128_pairing", "activate_at": "0x0", "pricing": {"alt_bn128_pairing": {"base": 100000, "pair": 80000}}}}
}

chain_json_accounts_2_5_8 = {
    "0000000000000000000000000000000000000001": {"balance": "1", "builtin": {"name": "ecrecover", "pricing": {"linear": {"base": 3000, "word": 0}}}},
    "0000000000000000000000000000000000000002": {"balance": "1", "builtin": {"name": "sha256", "pricing": {"linear": {"base": 60, "word": 12}}}},
    "0000000000000000000000000000000000000003": {"balance": "1", "builtin": {"name": "ripemd160", "pricing": {"linear": {"base": 600, "word": 120}}}},
    "0000000000000000000000000000000000000004": {"balance": "1", "builtin": {"name": "identity", "pricing": {"linear": {"base": 15, "word": 3}}}},
    "0000000000000000000000000000000000000005": {"balance": "1", "builtin": {"name": "modexp", "activate_at": 0, "pricing": {"modexp": {"divisor": 20}}}},
    "0000000000000000000000000000000000000006": {
        "balance": "1",
        "builtin": {
            "name": "alt_bn128_add",
            "activate_at": 0,
            "eip1108_transition": "0x7fffffffffffff",
            "pricing": {
                "alt_bn128_const_operations": {
                    "price": 500,
                    "eip1108_transition_price": 150
                }
            }
        }
    },
    "0000000000000000000000000000000000000007": {
        "balance": "1",
        "builtin": {
            "name": "alt_bn128_mul",
            "activate_at": 0,
            "eip1108_transition": "0x7fffffffffffff",
            "pricing": {
                "alt_bn128_const_operations": {
                    "price": 40000,
                    "eip1108_transition_price": 6000
                }
            }
        }
    },
    "0000000000000000000000000000000000000008": {
        "balance": "1",
        "builtin": {
            "name": "alt_bn128_pairing",
            "activate_at": 0,
            "eip1108_transition": "0x7fffffffffffff",
            "pricing": {
                "alt_bn128_pairing": {
                    "base": 100000,
                    "pair": 80000,
                    "eip1108_transition_base": 45000,
                    "eip1108_transition_pair": 34000
                }
            }
        }
    }
}

class ParityServer(Database):

    DEFAULT_SETTINGS = dict(auto_start=2,
                            base_dir=None,
                            parity_server=None,
                            instant_seal=True,
                            ethash=False,
                            author="0x0102030405060708090001020304050607080900",
                            faucet_private_key=None,
                            port=None,
                            jsonrpc_port=None,
                            enable_ws=False,
                            ws_port=None,
                            bootnodes=None,
                            node_key=None,
                            no_dapps=False,
                            dapps_port=None,
                            difficulty=None,
                            network_id=66,
                            min_gas_price=None,
                            copy_data_from=None)

    subdirectories = ['data', 'tmp']

    def initialize(self):
        self.parity_server = self.settings.get('parity_server')
        if self.parity_server is None:
            self.parity_server = get_path_of('parity')

        p = subprocess.Popen([self.parity_server, '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = p.communicate(timeout=15)

        for line in errs.split(b'\n') + outs.split(b'\n'):
            m = re.match(r"^\s+version\sParity(?:-Ethereum)?\/v([0-9.]+).*$", line.decode('utf-8'))
            if m:
                v = tuple(int(i) for i in m.group(1).split('.'))
                break
        else:
            raise Exception("Unable to figure out Parity version")

        self.version = v
        self.chainfile = os.path.join(self.base_dir, 'chain.json')
        self.faucet_private_key = self.settings.get('faucet_private_key')
        if self.faucet_private_key is None:
            self.faucet_private_key = os.urandom(32)
        elif isinstance(self.faucet_private_key, str):
            self.faucet_private_key = decode_hex(self.faucet_private_key)

        self.author = self.settings.get('author')

        difficulty = self.settings.get('difficulty')
        if difficulty is None:
            difficulty = "0x400"
        elif isinstance(difficulty, int):
            difficulty = hex(difficulty)
        elif isinstance(difficulty, str):
            if not difficulty.startswith("0x"):
                difficulty = "0x{}".format(difficulty)
        self.difficulty = difficulty

        network_id = self.settings.get('network_id')
        if not isinstance(network_id, int):
            try:
                network_id = int(network_id, 16)
            except ValueError:
                raise Exception("Network ID must be an integer or hex string")
        self.network_id = network_id

    def dsn(self, **kwargs):
        dsn = {'node': 'enode://{}@127.0.0.1:{}'.format(self.node_public_key, self.settings['port']),
               'url': self.url(),
               'network_id': self.network_id}
        ws_url = self.ws_url()
        if ws_url:
            dsn['ws_url'] = ws_url
        return dsn

    def url(self):
        return "http://localhost:{}".format(self.settings['jsonrpc_port'])

    def ws_url(self):
        if self.settings['ws_port']:
            return "ws://localhost:{}".format(self.settings['ws_port'])
        return None

    def get_faucet_private_key(self):
        return self.faucet_private_key

    def get_data_directory(self):
        return os.path.join(self.base_dir, 'data')

    def prestart(self):
        super(ParityServer, self).prestart()

        if self.settings['jsonrpc_port'] is None:
            self.settings['jsonrpc_port'] = get_unused_port()

        if self.settings['enable_ws'] and self.settings['ws_port'] is None:
            self.settings['ws_port'] = get_unused_port()

        if self.settings['node_key'] is None:
            self.settings['node_key'] = "{:0>64}".format(binascii.b2a_hex(os.urandom(32)).decode('ascii'))

        pub_x, pub_y = privtopub(binascii.a2b_hex(self.settings['node_key']))
        pub = encode_int32(pub_x) + encode_int32(pub_y)
        self.node_public_key = "{:0>128}".format(binascii.b2a_hex(pub).decode('ascii'))

        # write chain file
        chain = {
            "name": "testing.parity.dev"
        }
        if self.version >= (2, 5, 8):
            chain["params"] = copy.deepcopy(chain_json_params_2_5_8)
            chain["accounts"] = copy.deepcopy(chain_json_accounts_2_5_8)
        else:
            chain["params"] = copy.deepcopy(chain_json_params_2_5_7)
            chain["accounts"] = copy.deepcopy(chain_json_accounts_2_5_7)
        if self.settings.get('ethash'):
            chain["engine"] = copy.deepcopy(ethash_engine)
            chain["genesis"] = copy.deepcopy(ethash_genesis)
            chain["engine"]["Ethash"]["difficulty"] = self.difficulty
        elif self.settings.get('instant_seal'):
            chain["engine"] = copy.deepcopy(instant_engine)
            chain["genesis"] = copy.deepcopy(instant_genesis)
        else:
            raise Exception("No selected engine")
        if self.author.startswith("0x"):
            author = self.author[2:]
        else:
            author = self.author
        chain["genesis"]["author"] = "0x" + author
        chain["genesis"]["difficulty"] = self.difficulty
        chain["accounts"][privtoaddr(self.faucet_private_key).hex()] = {
            "balance": "1606938044258990275541962092341162602522202993782792835301376",
            "nonce": "1048576"
        }
        chain["params"]["networkID"] = hex(self.network_id)

        with open(self.chainfile, 'w') as f:
            json.dump(chain, f)

    def get_server_commandline(self):
        if self.author.startswith("0x"):
            author = self.author[2:]
        else:
            author = self.author

        cmd = [self.parity_server,
               "--port", str(self.settings['port']),
               "--no-color",
               "--chain", self.chainfile,
               "--author", author,
               "--tracing", 'on',
               "--node-key", self.settings['node_key']]

        # version specific arguments
        if self.version >= (2, 5, 8):
            cmd.extend(["--reseal-max-period", "0",
                        "--reseal-min-period", "0"])

        if self.version >= (2, 2, 0):
            cmd.extend(["--base-path", self.get_data_directory()])
        else:
            cmd.extend(["--datadir", self.get_data_directory(),
                        "--no-ui"])

        if self.version >= (1, 7, 0):
            cmd.extend(["--jsonrpc-port", str(self.settings['jsonrpc_port']),
                        "--jsonrpc-hosts", "all"])
            if self.settings.get('ws_port') is None:
                cmd.extend(["--no-ws"])
            else:
                cmd.extend([
                    "--ws-interface", "local",
                    "--ws-port", str(self.settings['ws_port']),
                    "--ws-origins", "all",
                    "--ws-hosts", "all"
                ])

        else:
            cmd.extend(["--rpcport", str(self.settings['jsonrpc_port'])])

        if self.settings['no_dapps']:
            cmd.extend(['--no-dapps'])
        elif self.version < (1, 7, 0):
            cmd.extend(['--dapps-port', str(self.settings['dapps_port'])])

        if self.settings['min_gas_price']:
            if self.version >= (2, 2, 0):
                cmd.extend(['--min-gas-price', str(self.settings['min_gas_price'])])
            else:
                cmd.extend(['--gasprice', str(self.settings['min_gas_price'])])

        if self.settings['bootnodes'] is not None:
            if isinstance(self.settings['bootnodes'], list):
                self.settings['bootnodes'] = ','.join(self.settings['bootnodes'])

            cmd.extend(['--bootnodes', self.settings['bootnodes']])

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

class ParityServerFactory(DatabaseFactory):
    target_class = ParityServer
