import copy
import datetime
import json
import os
import random

import requests

from dbstream.tunnel import create_ssh_tunnel


class DBStream:

    def __init__(self, instance_name, client_id):
        self.instance_name = instance_name
        self.instance_type_prefix = ""
        self.ssh_init_port = ""
        self.client_id = client_id
        self.ssh_tunnel = None
        self.dbstream_instance_id = 'df-' + datetime.datetime.now().strftime('%s') + '-' + str(
            random.randint(1000, 9999))

    def prefix(self):
        return self.instance_type_prefix + "_" + self.instance_name

    def remote_host(self):
        return os.environ[self.prefix() + "_HOST"]

    def remote_port(self):
        return os.environ[self.prefix() + "_PORT"]

    def credentials(self):
        if self.ssh_tunnel:
            host = self.ssh_tunnel.local_bind_host
            port = self.ssh_tunnel.local_bind_port
        else:
            host = self.remote_host()
            port = self.remote_port()
        return {
            'database': os.environ[self.prefix() + "_DATABASE"],
            'user': os.environ[self.prefix() + "_USERNAME"],
            'host': host,
            'port': port,
            'password': os.environ[self.prefix() + "_PASSWORD"],
        }

    def create_tunnel(self):
        self.ssh_tunnel = create_ssh_tunnel(
            instance=self.instance_name,
            port=self.ssh_init_port,
            remote_host=self.remote_host(),
            remote_port=self.remote_port()
        )
        return self.ssh_tunnel

    def execute_query(self, query):
        pass

    def _send_data_custom(self, data, replace=True):
        pass

    def _send(self, data, replace, batch_size=1000):
        pass

    def send_data(self, data, replace=True):
        data_copy = copy.deepcopy(data)
        if self._send_data_custom(data, replace=replace) != 0:
            url = os.environ.get("MONITORING_URL")
            if url:
                table_schema_name = data_copy["table_name"].split(".")
                body = {
                    "dbstream_instance_id": self.dbstream_instance_id,
                    "instance_name": self.instance_name,
                    "client_id": self.client_id,
                    "instance_type_prefix": self.instance_type_prefix,
                    "schema_name": table_schema_name[0],
                    "table_name": table_schema_name[1],
                    "nb_rows": len(data_copy["rows"]),
                    "nb_columns": len(data_copy["columns_name"]),
                    "timestamp": str(datetime.datetime.now()),
                    "ssh_tunnel": True if self.ssh_tunnel else False,
                    "local_absolute_path": os.getcwd()
                }
                r = requests.post(url=url, data=json.dumps(body))
                print(r.status_code)