from os import getenv
import urllib

try:
    import pyodbc
except ImportError:
    pyodbc = None
from sqlalchemy import create_engine
from .connection import Connection


class MSSQL(Connection):
    """Child class that inherits from Connection with specific configuration
        for connecting to MS SQL."""

    def __init__(self, schema=None, server=None, db=None, user=None, pwd=None):
        """Initializes an MS SQL database connection

        .. note::
            When object is instantiated without params, SQLSorcery will
            attempt to pull the values from the environment. See the
            README for examples of setting these correctly in a .env
            file.
        :param schema: Database object schema prefix
        :type schema: string
        :param server: IP or URL of database server
        :type server: string
        :param db: Name of database
        :type db: string
        :param user: Username for connecting to the database
        :type user: string
        :param pwd: Password for connecting to the database.
            **Security Warning**: always pass this in with environment
            variables when used in production.
        :type pwd: string
        """
        self.server = server or getenv("MS_SERVER") or getenv("DB_SERVER")
        self.db = db or getenv("MS_DB") or getenv("DB")
        self.user = user or getenv("MS_USER") or getenv("DB_USER")
        self.pwd = pwd or getenv("MS_PWD") or getenv("DB_PWD")
        self.schema = schema or getenv("MS_SCHEMA") or getenv("DB_SCHEMA") or "dbo"
        driver = f"{{{pyodbc.drivers()[0]}}}"
        params = urllib.parse.quote_plus(
            f"DRIVER={driver};SERVER={self.server};DATABASE={self.db};UID={self.user};PWD={self.pwd}"
        )
        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}", isolation_level="AUTOCOMMIT"
        )
