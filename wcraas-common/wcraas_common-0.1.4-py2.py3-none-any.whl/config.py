from collections import namedtuple
from environs import Env


class AMQPConfig(namedtuple("AMQPConfig", ("host", "port", "user", "password"))):
    __slots__ = ()

    @classmethod
    def fromenv(cls):
        """
        Create a `wcraas_common.AMQPConfig` from Environment Variables.

        >>> conf = AMQPConfig.fromenv()
        >>> type(conf)
        <class 'wcraas_common.config.AMQPConfig'>
        >>> conf._fields
        ('host', 'port', 'user', 'password')
        >>> conf.host
        'localhost'
        >>> conf.port
        5672
        >>> conf.user
        'guest'
        >>> conf.password
        'guest'
        """
        env = Env()
        env.read_env()

        with env.prefixed("COTTONTAIL_"):
            return cls(
                host=env.str("HOST", "localhost"),
                port=env.int("PORT", 5672),
                user=env.str("USER", "guest"),
                password=env.str("PASS", "guest"),
            )
