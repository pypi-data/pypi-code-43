import logging

from collections import namedtuple
from environs import Env

from wcraas_common import AMQPConfig


class MongoConfig(namedtuple("MongoConfig", ("host", "port", "db", "user", "password"))):
    __slots__ = ()

    @classmethod
    def fromenv(cls):
        """
        Create a `wcraas_storage.MongoConfig` from Environment Variables.

        >>> conf = MongoConfig.fromenv()
        >>> type(conf)
        <class 'config.MongoConfig'>
        >>> conf._fields
        ('host', 'port', 'db', 'user', 'password')
        >>> conf.host
        'localhost'
        >>> conf.port
        27017
        """
        env = Env()
        env.read_env()

        with env.prefixed('MONGO_'):
            return cls(
                host=env.str("HOST", "localhost"),
                port=env.int("PORT", 27017),
                db=env.str("DB", "wcraas"),
                user=env.str("USER", None),
                password=env.str("PASS", None),
            )


class Config(namedtuple("Config", ("amqp", "mongo", "mapping", "loglevel"))):
    __slots__ = ()

    @classmethod
    def fromenv(cls):
        """
        Create a `wcraas_storage.Config` from Environment Variables.

        >>> conf = Config.fromenv()
        >>> type(conf)
        <class 'config.Config'>
        >>> conf._fields
        ('amqp', 'mongo', 'mapping', 'loglevel')
        >>> conf.amqp
        AMQPConfig(host='localhost', port=5672, user='guest', password='guest')
        >>> conf.mongo
        mongo = MongoConfig(host='localhost', port=27017, db='wcraas', user=None, password=None)
        >>> conf.mapping
        {}
        >>> conf.loglevel
        20
        """
        env = Env()
        env.read_env()

        return cls(
            amqp=AMQPConfig.fromenv(),
            mongo=MongoConfig.fromenv(),
            mapping=env.json("QUEUE_COLLECTION_MAP", "{}") or dict(),
            loglevel=getattr(logging, env.str("LOGLEVEL", "INFO")),
        )

