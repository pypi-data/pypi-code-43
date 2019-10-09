from yoncrawler.db.base_db import BaseDB, NotSupportedError, checkDir
from yoncrawler.util.logger import getMyLogger
from pymongo import MongoClient

mylogger = getMyLogger()

class MongoDBSaver(BaseDB):
    def __init__(self, db_name, table_name, client="mongodb://mongo:27017/"):
        super().__init__()
        self.db_name = db_name
        self.table_name = table_name
        self.client = client

        try:
            self.database = self.connect()
        except Exception as e:
            mylogger.warning(e)
            return None

    def connect(self):
        client = MongoClient(self.client)
        db = client[self.db_name]
        collection = db[self.table_name]
        return collection

    def create(self, data):
        if isinstance(data, list):
            result = self.database.insert_many(data)
        elif isinstance(data, dict):
            result = self.database.insert_one(data)
        else:
            mylogger.warning(f"Data type is Not correct : {str(type(data))}")

    def read(self, field, value):
        result = self.database.find_one({field : value})
        return result

    def update(self):
        raise NotSupportedError("MongoSaver", "update")

    def delete(self):
        raise NotSupportedError("MongoSaver", "delete")