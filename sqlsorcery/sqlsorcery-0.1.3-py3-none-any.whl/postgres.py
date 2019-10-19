from os import getenv
from sqlalchemy import create_engine
from .connection import Connection


class PostgreSQL(Connection):
    """Child class that inherits from Connection with specific configuration
        for connecting to PostgreSQL."""

    def __init__(
        self, schema=None, server=None, port=None, db=None, user=None, pwd=None
    ):
        """Initializes a PostgreSQL database connection

         .. note::
            When object is instantiated without params, SQLSorcery will
            attempt to pull the values from the environment. See the
            README for examples of setting these correctly in a .env
            file.
        :param schema: Database object schema prefix
        :type schema: string
        :param server: IP or URL of database server
        :type server: string
        :param port: Port number
        :type port: string
        :param db: Name of database
        :type db: string
        :param user: Username for connecting to the database
        :type user: string
        :param pwd: Password for connecting to the database.
            **Security Warning**: always pass this in with environment
            variables when used in production.
        :type pwd: string
        """
        self.server = server or getenv("PG_SERVER") or getenv("DB_SERVER")
        self.port = port or getenv("PG_PORT") or getenv("DB_PORT")
        self.db = db or getenv("PG_DB") or getenv("DB")
        self.user = user or getenv("PG_USER") or getenv("DB_USER")
        self.pwd = pwd or getenv("PG_PWD") or getenv("DB_PWD")
        self.schema = schema or getenv("PG_SCHEMA") or getenv("DB_SCHEMA") or "public"
        sid = f"{self.server}:{self.port}/{self.db}"
        cstr = f"postgres://{self.user}:{self.pwd}@{sid}"
        self.engine = create_engine(cstr)
