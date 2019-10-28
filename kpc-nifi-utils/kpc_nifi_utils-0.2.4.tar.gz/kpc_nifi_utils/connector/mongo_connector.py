import json
import urllib.parse as urlparse

from pymongo import MongoClient
from pymongo.cursor import Cursor

import kpc_nifi_utils.shared.constants as constants
from kpc_nifi_utils.args.mongodb import MongoArgs
from kpc_nifi_utils.common.json_encoder import EnhancedJSONEncoder


class MongoConnector:
    def __init__(self, connector_args: MongoArgs = None, map_setting: dict = None):
        self._args = connector_args
        self._map_setting = map_setting

        self._username = None
        self._password = None
        self._host = None
        self._port = None
        self._db_name = None
        self._replica_set = None

        if self._args is not None:
            self._username = self._args.get_username()
            self._password = self._args.get_password()
            self._host = self._args.get_host()
            self._port = self._args.get_port()
            self._db_name = self._args.get_dbname()
            self._replica_set = self._args.get_replicaset()

        if self._map_setting is not None:
            self._username = self._username if self._username else self._map_setting.get(constants.MONGO_USERNAME)
            self._password = self._password if self._password else self._map_setting.get(constants.MONGO_PASSWORD)
            self._host = self._host if self._host else self._map_setting.get(constants.MONGO_HOST)
            self._port = self._port if self._port else self._map_setting.get(constants.MONGO_PORT)
            self._db_name = self._db_name if self._db_name else self._map_setting.get(constants.MONGO_DBNAME)
            self._replica_set = self._replica_set if self._replica_set else self._map_setting.get(
                constants.MONGO_REPLICA_SET)

    def get_db(self,
               host=None,
               port=None,
               document_class=dict,
               tz_aware=None,
               connect=None,
               dbname=None,
               **kwargs):

        if host is None and self._args is None and self._map_setting is None:
            raise ValueError("Can not get db because there is no setting initialize or pass")

        dbname = dbname if dbname else self._db_name

        if host is None:
            connection_string = 'mongodb://'
            if self._username and self._password:
                connection_string += '{}:{}@'.format(urlparse.quote_plus(self._username),
                                                     urlparse.quote_plus(self._password))

            connection_string += '{}'.format(self._host)

            if self._port:
                connection_string += ':{}'.format(self._port)

            host = '{}'.format(connection_string)

            if self._replica_set:
                host += '/?replicaSet={}'.format(self._replica_set)

        client = MongoClient(host,
                             port,
                             document_class,
                             tz_aware,
                             connect,
                             **kwargs)

        return client.get_database(dbname)

    @staticmethod
    def parse_as_json(data):
        data_parse = data
        if isinstance(data, dict):
            data_parse = [data]
        elif isinstance(data, Cursor):
            data_parse = list(data)

        return json.dumps(data_parse, cls=EnhancedJSONEncoder)
