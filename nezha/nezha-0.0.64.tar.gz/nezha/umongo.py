import re
from typing import Mapping, Iterable, Dict

from nezha import utime
from pymongo import MongoClient

yesterday = lambda: re.compile(f'{utime.yesterday(precision="day")}.*')
today = lambda: re.compile(f'{utime.today(precision="day")}.*')


def insert_one(data: Mapping,
               collection: str, db: str, host: str, port: int, username: str, password: str,
               authSource: str) -> None:
    with MongoClient(host=host,
                     port=port,
                     username=username,
                     password=password,
                     authSource=authSource,
                     maxPoolSize=1) as MgClient:
        MgClient[db][collection].insert_one(data)


def find(condition: Mapping,
         collection: str, db: str, host: str, port: int, username: str, password: str,
         authSource: str) -> Iterable:
    with MongoClient(host=host,
                     port=port,
                     username=username,
                     password=password,
                     authSource=authSource,
                     maxPoolSize=1) as MgClient:
        return MgClient[db][collection].find(condition)


def find_one(condition: Mapping,
             collection: str, db: str, host: str, port: int, username: str, password: str,
             authSource: str) -> Dict:
    with MongoClient(host=host,
                     port=port,
                     username=username,
                     password=password,
                     authSource=authSource,
                     maxPoolSize=1) as MgClient:
        return MgClient[db][collection].find_one(condition)
