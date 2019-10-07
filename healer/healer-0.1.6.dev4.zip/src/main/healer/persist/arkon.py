"""
"""

from __future__ import annotations

import logging
import os
import uuid
from configparser import ConfigParser
from typing import List
from typing import Type

import peewee
from playhouse.sqlite_ext import SqliteExtDatabase

from healer.config import CONFIG
from healer.persist.support.schemaless import NoSqlDatabase
from healer.support.files import FilesSupport

logger = logging.getLogger(__name__)


class PersistSupport:
    """
    """

    @staticmethod
    def activate_database(
            database:peewee.Database,
            model_class_list:List[Type[peewee.Model]],
        ) -> None:
        database.bind(model_class_list)
        database.create_tables(model_class_list)

    @staticmethod
    def cluster_section() -> ConfigParser:
        "produce replicated data store"
        return CONFIG['persist/cluster']

    @staticmethod
    def cluster_database(entry_name:str='arkon_file') -> NoSqlDatabase:
        datafile = PersistSupport.cluster_section()[entry_name]
        logger.debug(f"datafile: {datafile}")
        FilesSupport.ensure_parent(datafile)
        database = NoSqlDatabase(datafile=datafile)
        return database

    @staticmethod
    def private_section() -> ConfigParser:
        return CONFIG['persist/private']

    @staticmethod
    def private_database(entry_name:str='arkon_file') -> SqliteExtDatabase:
        "produce local cache data store"
        datafile = PersistSupport.private_section()[entry_name]
        logger.debug(f"datafile: {datafile}")
        FilesSupport.ensure_parent(datafile)
        database = SqliteExtDatabase(database=datafile)
        return database


class ServerModel(peewee.Model):
    """
    """

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ServerSupport.model_class_list.append(cls)


class ServerSupport:
    """
    """

    section = "database"

    model_class_list:List[Type] = list()

    @staticmethod
    def produce_datafile() -> str:
        return PersistSupport.produce_datafile(ServerSupport.section)

    @staticmethod
    def ensure_database() -> NoSqlDatabase:
        database = PersistSupport.produce_database(ServerSupport.section)
        PersistSupport.activate_database(database, ServerSupport.model_class_list)
        return database

    @staticmethod
    def desure_database() -> None:
        datapath = PersistSupport.produce_datafile(ServerSupport.section)
        datapath_shm = datapath + '-shm'
        datapath_wal = datapath + '-wal'
        path_list = [datapath, datapath_shm, datapath_wal ]
        for path in path_list:
            if os.path.exists(path):
                os.remove(path)
