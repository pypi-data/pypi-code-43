from kpc_nifi_utils.common.args_parser import Args
from kpc_nifi_utils.shared import constants


class PostgreSqlArgs(Args):
    def __init__(self, *args):
        super().__init__(*args)

    def get_username(self):
        return self.get(constants.POSTGRESQL_USERNAME)

    def get_password(self):
        return self.get(constants.POSTGRESQL_PASSWORD)

    def get_host(self):
        return self.get(constants.POSTGRESQL_HOST)

    def get_port(self):
        return int(self.get(constants.POSTGRESQL_PORT)) if self.get(constants.POSTGRESQL_PORT) else None

    def get_dbname(self):
        return self.get(constants.POSTGRESQL_DBNAME)
