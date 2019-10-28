import json

import pytds

import kpc_nifi_utils.shared.constants as constants
from kpc_nifi_utils.args.mssql import MSSqlArgs
from kpc_nifi_utils.common.json_encoder import EnhancedJSONEncoder


class MSSqlConnector:
    def __init__(self, connector_args: MSSqlArgs = None, map_setting: dict = None):
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
            self._host = self._args.get_dsn()
            self._port = self._args.get_port()
            self._db_name = self._args.get_dbname()

        if self._map_setting is not None:
            self._username = self._username if self._username else self._map_setting.get(constants.MSSQL_USERNAME)
            self._password = self._password if self._password else self._map_setting.get(constants.MSSQL_PASSWORD)
            self._host = self._host if self._host else self._map_setting.get(constants.MSSQL_HOST)
            self._port = self._port if self._port else self._map_setting.get(constants.MSSQL_PORT)
            self._db_name = self._db_name if self._db_name else self._map_setting.get(constants.MSSQL_DBNAME)

    def connect(self,
                dsn=None, database=None, user=None, password=None, timeout=None, login_timeout=15, as_dict=None,
                appname=None, port=None, tds_version=1946157060, autocommit=False, blocksize=4096, use_mars=False,
                auth=None, readonly=False, load_balancer=None, use_tz=None, bytes_to_unicode=True, row_strategy=None,
                failover_partner=None, server=None, cafile=None, validate_host=True, enc_login_only=False):

        if self._args is None \
                and self._map_setting is None \
                and dsn is None \
                and database is None \
                and user is None \
                and password is None \
                and port is None:
            raise ValueError("Can not get db because there is no setting initialize or pass")

        dsn = dsn if dsn else self._host
        user = user if user else self._username
        password = password if password else self._password
        port = port if port else self._port
        database = database if database else self._db_name

        if as_dict is None:
            as_dict = True

        return pytds.connect(dsn=dsn, database=database, user=user, password=password, timeout=timeout,
                             login_timeout=login_timeout, as_dict=as_dict, appname=appname, port=port,
                             tds_version=tds_version, autocommit=autocommit, blocksize=blocksize, use_mars=use_mars,
                             auth=auth, readonly=readonly, load_balancer=load_balancer, use_tz=use_tz,
                             bytes_to_unicode=bytes_to_unicode, row_strategy=row_strategy,
                             failover_partner=failover_partner, server=server, cafile=cafile,
                             validate_host=validate_host, enc_login_only=enc_login_only)

    @staticmethod
    def parse_as_json(data):
        data_parse = data
        if isinstance(data, dict):
            data_parse = [data]

        return json.dumps(data_parse, cls=EnhancedJSONEncoder)
