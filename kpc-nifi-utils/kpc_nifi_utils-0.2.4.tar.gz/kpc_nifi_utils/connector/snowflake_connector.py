import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.connector.cursor import SnowflakeCursor

import kpc_nifi_utils.shared.constants as constants
from kpc_nifi_utils.args.snowflake import SnowflakeArgs


class SnowflakeConnector:
    def __init__(self, connector_args: SnowflakeArgs = None, map_setting: dict = None):
        self._args = connector_args
        self._map_setting = map_setting

        self._username = None
        self._password = None
        self._account = None
        self._env = None
        self._warehouse = None
        self._role = None

        if self._args is not None:
            self._username = self._args.get_username()
            self._password = self._args.get_password()
            self._account = self._args.get_account()
            self._env = self._args.get_env()
            self._warehouse = self._args.get_warehouse()
            self._role = self._args.get_role()

        if self._map_setting is not None:
            self._username = self._username if self._username else self._map_setting.get(constants.SNOWFLAKE_USERNAME)
            self._password = self._password if self._password else self._map_setting.get(constants.SNOWFLAKE_PASSWORD)
            self._account = self._account if self._account else self._map_setting.get(constants.SNOWFLAKE_ACCOUNT)
            self._env = self._env if self._env else self._map_setting.get(constants.SNOWFLAKE_ENV)
            self._warehouse = self._warehouse if self._warehouse else self._map_setting.get(
                constants.SNOWFLAKE_WAREHOUSE)
            self._role = self._role if self._role else self._map_setting.get(constants.SNOWFLAKE_ROLE)

    def connect(self, user=None, password=None, account=None, paramstyle=None):

        if user is None and password is None and account is None and self._args is None and self._map_setting is None:
            raise ValueError("Can not get db because there is no setting initialize or pass")

        user = user if user else self._username
        password = password if password else self._password
        account = account if account else self._account

        if paramstyle:
            snowflake.connector.paramstyle = paramstyle

        return snowflake.connector.connect(user=user,
                                           password=password,
                                           account=account)

    def with_context(self, cursor: SnowflakeCursor, warehouse: str = None, role: str = None):
        exe_warehouse = warehouse if warehouse else self._warehouse
        exe_role = role if role else self._role

        if exe_warehouse:
            cursor.execute('use warehouse {}'.format(exe_warehouse))

        if exe_role:
            cursor.execute('use role {}'.format(exe_role))

        return cursor

    def get_raw_dbname(self):
        env = self._env.upper()
        return 'PROD_RAW' if env == 'PROD' or env == 'PRODUCTION' else 'DEV_RAW'

    def compose_table_path(self, schema: str, table: str):
        return '"{}"."{}"."{}"'.format(self.get_raw_dbname(), schema, table)

    @staticmethod
    def as_dict_cursor(conn: snowflake.connector.SnowflakeConnection):
        return conn.cursor(DictCursor)
