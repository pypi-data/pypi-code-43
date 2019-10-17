import summer

from . import conf

session_provider = summer.DefaultSessionProvider(conf.sqlalchemy_uri, conf.sqlalchemy_autocommit)
