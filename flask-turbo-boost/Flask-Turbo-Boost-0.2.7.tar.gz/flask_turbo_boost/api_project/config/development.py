# coding: utf-8
from .default import Config


class DevelopmentConfig(Config):
    # App config
    DEBUG = True

    # SQLAlchemy config
    # SQLALCHEMY_DATABASE_URI = "postgresql://root:@localhost/frontend"
    SQLALCHEMY_DATABASE_URI = "sqlite:///%s/db/dev.sqlite3" % Config.PROJECT_PATH
