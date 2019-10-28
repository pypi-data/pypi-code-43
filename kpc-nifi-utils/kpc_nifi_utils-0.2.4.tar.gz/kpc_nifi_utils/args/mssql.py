from kpc_nifi_utils.common.args_parser import Args
from kpc_nifi_utils.shared import constants


class MSSqlArgs(Args):
    def __init__(self, *args):
        super().__init__(*args)

    def get_username(self):
        return self.get(constants.MSSQL_USERNAME)

    def get_password(self):
        return self.get(constants.MSSQL_PASSWORD)

    def get_dsn(self):
        return self.get(constants.MSSQL_HOST)

    def get_port(self):
        return int(self.get(constants.MSSQL_PORT)) if self.get(constants.MSSQL_PORT) else None

    def get_dbname(self):
        return self.get(constants.MSSQL_DBNAME)
