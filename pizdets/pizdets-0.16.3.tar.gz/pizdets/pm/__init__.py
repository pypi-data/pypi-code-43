import zmq
from google.protobuf.reflection import ParseMessage

from . import protobuf_to_dict
from . import device_messages_pb2 as dev_msg, network_messages_pb2 as net_msg



context = zmq.Context()
class PMError(Exception):
    def __init__(self, error_type, error_message):
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self):
        return self.error_message + " ErrorType = " + str(self.error_type)


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


class PMDevice(object):
    def __init__(self, hub, device_serial, influxdb=None):
        self.hub = hub
        self.device_serial = device_serial
        self.last_header = None
        self.influxdb = influxdb

    def request(self, req):
        # reqType = 0
        respType = None
        # baseName = None
        if type(req) == int:
            reqType = req
            baseName = dev_msg.RequestType.Name(req)
        elif req.DESCRIPTOR.name.endswith("Request"):
            baseName = req.DESCRIPTOR.name[0:-7]
            reqType = dev_msg.RequestType.Value(baseName)
            if self.influxdb is not None:
                # Sending request to InfluxDB
                record = {
                    "measurement": req.DESCRIPTOR.name,
                    "tags": {
                        "device": self.device_serial
                    },
                    "fields": protobuf_to_dict(req)
                }
                self.influxdb.write_points([record])
        else:
            raise Exception("Not a valid request.")

        if baseName + "Response" in dev_msg.DESCRIPTOR.message_types_by_name:
            respType = dev_msg.DESCRIPTOR.message_types_by_name[baseName + "Response"]

        packet = bytearray((reqType,))

        if type(req) != int:
            packet += req.SerializeToString()

        self.hub.socket.send_multipart([self.device_serial, packet])

        resp = self.hub.socket.recv_multipart()

        self.last_header = net_msg.ReplyInfo.FromString(resp[0])

        if self.last_header.error:
            raise PMError(self.last_header.errorType, self.last_header.errorMessage)

        r = True

        if respType:
            # Sending response to InfluxDB
            r = ParseMessage(respType, resp[1])
            if self.influxdb is not None:
                record = {
                    "measurement": r.DESCRIPTOR.name,
                    "tags": merge_two_dicts({
                        "device": self.device_serial
                    }, protobuf_to_dict(req)),
                    "fields": protobuf_to_dict(r)
                }
                self.influxdb.write_points([record])

        return r


class PMHub(object):
    def __init__(self, address):
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(address)
        self.influxdb = None

    def log_to_influxdb(self, influxdb):
        self.influxdb = influxdb

    def get_devices(self):
        self.socket.send(b'')
        deviceSerials = self.socket.recv_multipart()
        return [PMDevice(self, serial, influxdb=self.influxdb) for serial in deviceSerials if serial]

    def __getitem__(self, serial):
        return PMDevice(self, serial, influxdb=self.influxdb)

    @staticmethod
    def local():
        return PMHub("tcp://host:5555")