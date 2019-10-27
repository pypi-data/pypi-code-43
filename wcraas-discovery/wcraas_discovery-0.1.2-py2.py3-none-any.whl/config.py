import logging

from collections import namedtuple
from environs import Env

from wcraas_common import AMQPConfig


class Config(namedtuple("Config", ("amqp", "loglevel"))):
    __slots__ = ()

    @classmethod
    def fromenv(cls):
        """
        Create a `wcraas_discovery.Config` from Environment Variables.

        >>> conf = Config.fromenv()
        >>> type(conf)
        <class 'config.Config'>
        >>> conf._fields
        ('amqp', 'loglevel')
        >>> conf.amqp
        AMQPConfig(host='localhost', port=5672, user='guest', password='guest')
        >>> conf.loglevel
        20
        """
        env = Env()
        env.read_env()

        return cls(
            amqp=AMQPConfig.fromenv(),
            loglevel=getattr(logging, env.str("LOGLEVEL", "INFO")),
        )
