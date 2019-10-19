import udsoncan
from udsoncan.connections import IsoTPConnection, PythonIsoTpConnection
from udsoncan.client import Client
from udsoncan.exceptions import *
from udsoncan.services import *
import udsoncan.configs
import can


def algo(seed, param):
    return b"\xed\xcb\xa9\x87"


class my_codec(udsoncan.DidCodec):
    def encode(self, s):
        return bytes(s.encode('ascii'))


config = dict(udsoncan.configs.default_client_config)
config['data_identifiers'] = {0xF190: my_codec, 1: 'H', 2: 'H', 3: 'i'}
config['security_algo'] = algo

conn = IsoTPConnection('vcan0', rxid=0x123, txid=0x456)
#bus = can.interface.Bus('vcan0', bustype='socketcan')
#conn = PythonIsoTpConnection(bus, txid=0x456, rxid=0x123, params={'stmin' : 1, })
with Client(conn,  request_timeout=2, config=config) as client:
    try:
        # integer with value of 3
        client.change_session(
            DiagnosticSessionControl.Session.extendedDiagnosticSession)
        # Fictive security level. Integer coming from fictive lib, let's say its value is 5
        client.unlock_security_access(3)
        # Standard ID for VIN is 0xF190. Codec is set in the client configuration
        response = client.read_data_by_identifier([1, 2, 3])
        print(response)
        client.ecu_reset(ECUReset.ResetType.hardReset)  # HardReset = 0x01
    except NegativeResponseException as e:
        print('Server refused our request for service %s with code "%s" (0x%02x)' % (
            e.response.service.get_name(), e.response.code_name, e.response.code))
    except InvalidResponseException as e:
        print('Server sent an invalid payload : %s' %
              e.response.original_payload)
