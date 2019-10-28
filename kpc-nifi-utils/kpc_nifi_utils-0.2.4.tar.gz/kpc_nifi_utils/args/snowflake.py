from kpc_nifi_utils.common.args_parser import Args
from kpc_nifi_utils.shared import constants


class SnowflakeArgs(Args):
    def __init__(self, *args):
        super().__init__(*args)

    def get_env(self):
        return self.get(constants.SNOWFLAKE_ENV)

    def get_username(self):
        return self.get(constants.SNOWFLAKE_USERNAME)

    def get_password(self):
        return self.get(constants.SNOWFLAKE_PASSWORD)

    def get_account(self):
        return self.get(constants.SNOWFLAKE_ACCOUNT)

    def get_warehouse(self):
        return self.get(constants.SNOWFLAKE_WAREHOUSE)

    def get_role(self):
        return self.get(constants.SNOWFLAKE_ROLE)
