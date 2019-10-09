from abc import ABC, abstractmethod
from yoncrawler.util.logger import getMyLogger
import os

class BaseDB(ABC):

    def __init__(self):
        self.logger = getMyLogger()
        self.database = None
        self._table_name = None
        self._db_name = None

    @property
    def db_name(self):
        return self._db_name
    @property
    def table_name(self):
        return self._table_name

    @db_name.setter
    def db_name(self, db_name):
        self._db_name = db_name.replace(" ", "_")

    @table_name.setter
    def table_name(self, table_name):
        self._table_name = table_name.replace(" ", "_")

    @abstractmethod
    def connect(self):
        raise NotImplementedError
    
    @abstractmethod
    def create(self, data):
        raise NotImplementedError

    @abstractmethod
    def read(self, field, value):
        raise NotImplementedError

    @abstractmethod
    def update(self):
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError


class NotSupportedError(Exception):
    def __init__(self, who, what):
        msg = f"{who} is not support method {what}."
        super().__init__(msg)


def checkDir(dir_path):
    if os.path.isdir(dir_path):
        path = dir_path
    else:
        mylogger = getMyLogger()
        mylogger.warning(f"{dir_path} Not exist, so automatically create it")
        os.makedirs(dir_path)
        path = dir_path
    if (path[-1] == '/') or (path[-1] == '\\'):
        path = path[:-1]

    return path