from yoncrawler.db.base_db import BaseDB, NotSupportedError, checkDir
from yoncrawler.util.logger import getMyLogger
from tinydb import TinyDB, where
import os

mylogger = getMyLogger()

class TinyDBSaver(BaseDB):
    def __init__(self, db_name, table_name,  dir_path=os.getcwd()):
        super().__init__()
        self.dir = checkDir(dir_path)
        self.db_name = db_name
        self.table_name = table_name
        try:
            self.connect()
        except Exception as e:
            mylogger.warning(e)
            return None

    def connect(self):
        path = os.path.join(self.dir, self.db_name) + ".json"

        self.database = TinyDB(path).table(self.table_name)

    def create(self, data):
        if isinstance(data, list):
            for x in data:
                self.database.insert(x)
        elif isinstance(data, dict):
            self.database.insert(data)
        else:
            mylogger.warning(f"Data type is Not correct : {str(type(data))}")


    def read(self, field, value):
        result = self.database.search(where(field)==value)
        if len(result) == 0:
            return None
        return result

    def update(self):
        raise NotSupportedError("JsonSaver", "update")

    def delete(self):
        raise NotSupportedError("JsonSaver", "delete")
