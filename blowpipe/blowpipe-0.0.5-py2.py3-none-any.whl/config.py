import os
import json
from blowpipe import utils


class BlowpipeConfig(object):
    def __init__(self, filename=None):
        if filename is not None:
            basename = filename.split("/")[-1]
            self.filename = filename
            self.root_dir = self.filename[0:len(filename)-len(basename)-1]
            self.data = self.load(filename)
        else:
            self.data = utils.IniFile()

    def load(self, filename):
        filename = self.get_filename()
        return utils.IniFile(filename)

    def save(self):
        """
        persists any settings to the preferences file
        :return:
        """
        root_dir = self.get_root_dir()
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir)
        filename = self.get_filename()
        f = open(filename, 'w')
        f.write(json.dumps(self.data, indent=4))
        f.close()

    def is_web_server_enabled(self):
        return self.data.get("http", "enabled", "False") == "True"

    def is_grpc_server_enabled(self):
        return self.data.get("grpc", "enabled", "False") == "True"

    def get_grpc_port(self):
        return int(self.data.get("grpc", "port", 50051))

    def set_grpc_port(self, port):
        self.data.set("grpc", "port", port)

    def get_grpc_client_ip(self):
        return self.data.get("grpc", "client_ip", "localhost")

    def set_grpc_client_ip(self, ip):
        self.data.set("grpc", "client_ip", ip)

    def get_grpc_server_ip(self):
        return self.data.get("grpc", "ip", "127.0.0.1")

    def set_grpc_server_ip(self, ip):
        self.data.set("grpc", "ip", "::")

    def get_http_port(self):
        return int(self.data.get("http", "port", 12345))

    def set_http_port(self, port):
        self.data.set("http", "port", port)

    def get_http_ip(self):
        return self.data.get("http", "ip", "0.0.0.0")

    def set_http_ip(self, ip):
        self.data.set("http", "ip", ip)

    def get_filename(self):
        return self.filename

    def get_root_dir(self):
        return self.root_dir

    def get_log_dir(self):
        root_dir = self.get_root_dir()
        return root_dir + "/logs"

    def get_syslog_filename(self):
        return self.get_log_dir() + "/syslog.log"
