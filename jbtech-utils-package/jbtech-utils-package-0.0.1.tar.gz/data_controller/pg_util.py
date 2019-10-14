""" Util to connect to a postgres DB """
from data_controller.pg_config import PGConfig
from py_utils.logger import logger
import psycopg2
import psycopg2.extras
import time
import re


class PGUtil:

    def __init__(self, user, database, sleep_period=5, max_retries=1):
        self.max_tries = max_retries
        self.sleep_period = sleep_period
        self.config = PGConfig()
        self.db_dict = self.config.get_db_dict(user, database)
        self.result_set = None
        self.cur = None

    def execute_query(self, statement, parameters=None):
        """
        General-purpose wrapper for psycopg2.

        Usage:
        1) database_dict should be a database connection dictionary as specified in environment
           variable. (e.g. postgresql_odc)
            a) Username
            b) password
            c) dbname
            d) port
            e) host

        2) statement should be a SQL statement formatted according to psycopg2 execute() standards.
        3) parameters should be dictionary/list for psycopg2 execute() substitution.

        Returns:
        1) rowcount (# rows affected by statement)
        2) result_set (If executing a select statement, this will return results.)
        """
        self._connect(self.db_dict)
        self.result_set = None

        try:
            logger.info("DB Statement: %s --- Parameters: %s" % (statement, parameters))
            self.cur = self.db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            if isinstance(parameters, list):
                self.cur.execute(statement, (parameters,))
            else:
                self.cur.execute(statement, parameters)

            if self.cur.rowcount > 0 \
                    and not re.findall("alter ", statement.lower()) \
                    and not re.findall("create ", statement.lower()) \
                    and not re.findall("delete ", statement.lower()) \
                    and not re.findall("insert ", statement.lower()) \
                    and not re.findall("update ", statement.lower()):
                self.result_set = self.cur.fetchall()

            self.db_conn.commit()
            logger.debug("Statement executed/committed successfully.")

        except psycopg2.Error as error:
            logger.err("Exception occurred on statement execution: %s" % str(error))
            self.db_conn.rollback()

        finally:
            self.cur.close()
            self.db_conn.close()

        logger.info("RowCount: %s" % self.cur.rowcount)
        logger.info("ResultSet: %s" % self.result_set)

        return self.cur.rowcount, self.result_set

    def _connect(self, database_dict):
        """
        Creates a psycopg2 connection object using environment dictionary.
        """
        tries = 0
        success = False

        host = database_dict['host']
        port = database_dict['port']
        dbname = database_dict['dbname']
        user = database_dict['username']
        password = database_dict['password']

        logger.info("Host: %s" % host)
        logger.info("Post: %s" % port)
        logger.info("Database Name: %s" % dbname)
        logger.info("User: %s" % user)
        logger.info("Password: %s" % password)

        while tries <= int(self.max_tries):
            try:
                self.db_conn = psycopg2.connect(host=host,
                                                port=port,
                                                dbname=dbname,
                                                user=user,
                                                password=password)
                success = True

            except psycopg2.Error as error:
                logger.err("Try %s: Psycopg2 connection failed with exception: %s"
                             % (tries, error))
                time.sleep(float(self.sleep_period))

            tries += 1

        if success is False:
            raise Exception("Database connection was not successful")