import json

import pg8000
from pg8000 import Cursor

import kpc_nifi_utils.shared.constants as constants
from kpc_nifi_utils.args.postgresql import PostgreSqlArgs
from kpc_nifi_utils.common.json_encoder import EnhancedJSONEncoder


class PostgreSqlConnector:
    def __init__(self, connector_args: PostgreSqlArgs = None, map_setting: dict = None):
        self._args = connector_args
        self._map_setting = map_setting

        self._username = None
        self._password = None
        self._host = None
        self._port = None
        self._db_name = None

        if self._args is not None:
            self._username = self._args.get_username()
            self._password = self._args.get_password()
            self._host = self._args.get_host()
            self._port = self._args.get_port()
            self._db_name = self._args.get_dbname()

        if self._map_setting is not None:
            self._username = self._username if self._username else self._map_setting.get(constants.POSTGRESQL_USERNAME)
            self._password = self._password if self._password else self._map_setting.get(constants.POSTGRESQL_PASSWORD)
            self._host = self._host if self._host else self._map_setting.get(constants.POSTGRESQL_HOST)
            self._port = self._port if self._port else self._map_setting.get(constants.POSTGRESQL_PORT)
            self._db_name = self._db_name if self._db_name else self._map_setting.get(constants.POSTGRESQL_DBNAME)

    def connect(self, user=None, host=None, unix_sock=None, port=None, database=None,
                password=None, ssl=None, timeout=None, application_name=None,
                max_prepared_statements=1000, tcp_keepalive=True):

        if user is None and host is None and port is None and self._args is None and self._map_setting is None:
            raise ValueError("Can not get db because there is no setting initialize or pass")

        user = user if user else self._username
        password = password if password else self._password
        host = host if host else self._host
        port = port if port else self._port
        database = database if database else self._db_name

        return pg8000.connect(user=user, host=host, unix_sock=unix_sock, port=port, database=database,
                              password=password, ssl=ssl, timeout=timeout, application_name=application_name,
                              max_prepared_statements=max_prepared_statements, tcp_keepalive=tcp_keepalive)

    @staticmethod
    def fetchall_asdict(cursor: Cursor):
        cols = [a[0].decode("utf-8") for a in cursor.description]
        result = []
        for row in cursor.fetchall():
            result.append({a: b for a, b in zip(cols, row)})

        return result

    @staticmethod
    def fetchone_asdict(cursor: Cursor):
        cols = [a[0].decode("utf-8") for a in cursor.description]
        result = []
        res = cursor.fetchone()
        result.append({a: b for a, b in zip(cols, list(res))})

        return result[0]

    @staticmethod
    def fetchmany_asdict(cursor: Cursor, num: int):
        cols = [a[0].decode("utf-8") for a in cursor.description]
        result = []
        for row in cursor.fetchmany(num):
            result.append({a: b for a, b in zip(cols, row)})

        return result

    @staticmethod
    def parse_as_json(data):
        data_parse = data
        if isinstance(data, dict):
            data_parse = [data]

        return json.dumps(data_parse, cls=EnhancedJSONEncoder)
