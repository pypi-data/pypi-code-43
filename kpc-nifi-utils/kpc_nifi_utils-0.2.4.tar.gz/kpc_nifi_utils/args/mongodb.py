from kpc_nifi_utils.common.args_parser import Args
from kpc_nifi_utils.shared import constants


class MongoArgs(Args):
    def __init__(self, *args):
        super().__init__(*args)

    def get_username(self):
        return self.get(constants.MONGO_USERNAME)

    def get_password(self):
        return self.get(constants.MONGO_PASSWORD)

    def get_host(self):
        return self.get(constants.MONGO_HOST)

    def get_port(self):
        return int(self.get(constants.MONGO_PORT)) if self.get(constants.MONGO_PORT) else None

    def get_dbname(self):
        return self.get(constants.MONGO_DBNAME)

    def get_replicaset(self):
        return self.get(constants.MONGO_REPLICA_SET)
