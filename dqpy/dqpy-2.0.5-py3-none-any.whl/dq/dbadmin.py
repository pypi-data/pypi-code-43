import sys

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from dq.config import Config

ACTION_CREATE = 'create'
ACTION_DROP = 'drop'


def create(url_key):
    try:
        engine = create_engine(Config.get(url_key))
        if not database_exists(engine.url):
            create_database(engine.url)
    except Exception as e:
        print('Unable to create database: %s' % e)


def drop(url_key):
    try:
        engine = create_engine(Config.get(url_key))
        drop_database(engine.url)
    except Exception as e:
        print('Unable to drop database: %s' % e)


def main():
    action = sys.argv[1]
    url_key = sys.argv[2] if len(sys.argv) > 2 else 'sql.url'
    if action == ACTION_CREATE:
        create(url_key)
    elif action == ACTION_DROP:
        drop(url_key)
