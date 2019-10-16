"""
.. module:: dh_mssql
   :platform: Unix, Windows
   :synopsis: A module which contains the boiler plate methods to be used
   when the database is MSSQL.

.. moduleauthor:: Dharmateja Yarlagadda <dharmateja.yarlagadda@eneco.com>

"""

import logging
import pyodbc
from retrying import retry
from deprecated import deprecated
from datetime import date, timedelta
logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


def retry_if_error(exception):
    """Return True if we should retry (Currently all exeptions, but can be modified here for specific exceptions),
     False otherwise"""
    return isinstance(exception, Exception)


class SQLClient(object):
    """
    A SQL client for making basic select and updates according to the Datahub Platform.
    """

    def __init__(self,
                 db_host='localhost',
                 db_user_name='developer',
                 db_password='test',
                 db_schema='default',
                 db_driver='SQL Server',
                 data_source='test'):
        """
        Initialize a new instance.
        If specified, 'db_host' is the name of the remote host to which to
        connect.
        If specified, 'db_user_name' specifies the user_name with which to connect.
        If specified, 'db_password' specifies the password with which to connect.
        If specified, 'db_schema' specifies the schema to connect.
        If specified, 'db_driver' specifies the driver to use to connect.
        If specified, 'data_source' specifies the data_source for which the processes are being run.
        If these parameters are not specified defaults will be used.

        :param db_host: The database hostname/Ip Address.
        :type db_host: String
        :param db_user_name: The database username
        :type db_user_name: String
        :param db_password: The database password
        :type db_password: String
        :param db_schema: The database schema
        :type db_schema: String
        :param db_driver: The driver to be used for the connection.
        :type db_driver: String
        :param data_source: The data_source for which the processes are being run.
        :type data_source: String
        """

        self.host = db_host
        self.user_name = db_user_name
        self.password = db_password
        self.schema = db_schema
        self.driver = db_driver
        self.data_source = data_source

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def get_processed_files_list(self, days_back,
                                 processed_files_list):
        """
        Provide list of processed files for a particular date based on the days_back variable.

        :param days_back: Number  of days to go back, by default 0
        :param processed_files_list: empty  processed files list.
        :return: processed files list: It contains updated processed files list.
        """
        logging.info('DH_Utils: Fetching the list of processed files for a particular date from database')
        with pyodbc.connect(
                'DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
                    self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
            file_date = (date.today() - timedelta(days_back)).strftime("%Y-%m-%d")
            query = "select file_name from applications_inventory " \
                    "where data_source='{}' and file_date>='{}'".format(self.data_source, file_date)
            cursor.execute(query)
            for row in cursor.fetchall():
                processed_files_list.append(row[0])
        logging.info('DH_Utils: Finished fetching the list of processed files for a particular date from database')
        return processed_files_list

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def update_processed_files_list(self, file_name, file_date, processed_time):
        """
        Update the file_name in MSSQL database in processed file list.

        :param file_name: Name of the processed file.
        :type file_name: String
        :param file_date: Processed file date.
        :type file_date: String
        :param processed_time: Processed time of the file.
        :type processed_time: String
        :return: No return
        """
        logging.info('DH_Utils: Updating current processed time,file name and file_date into database')
        with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                            'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
                self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
            query = "insert into applications_inventory(data_source,file_name,file_date,processed_time) " \
                    "VALUES ('{}','{}','{}','{}')".format(self.data_source, file_name, file_date, processed_time)
            cursor.execute(query)
            cursor.execute('commit')
        logging.info('DH_Utils: Finished updating current processed time,file name and file_date into database')

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def get_last_processed_date(self, last_processed_date, file_name=None):
        """
        Get the last processed date for the given datasource/filename.

        :param last_processed_date: empty list.
        :type last_processed_date: List of datetime.
        :param file_name: The name of the file.( Default None)
        :type file_name: String
        :return: last_processed_time: The last processed_time for the data_source.
        """
        logging.info('DH_Utils: Fetching last processed date from database')
        with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                            'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
                self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
            if file_name:
                query = "select file_date from applications_inventory where data_source='{}' and file_name = '{}'" \
                    .format(self.data_source, file_name)
            else:
                query = "select file_date from applications_inventory where data_source='{}'".format(self.data_source)
            cursor.execute(query)
            for row in cursor.fetchall():
                last_processed_date.append(row[0])
        logging.info('DH_Utils: Finished fetching last processed date from database')
        return last_processed_date

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def get_last_processed_time(self,
                                last_processed_time, file_name=None):
        """
        Get the last processed time for the given datasource/filename.

        :param last_processed_time: empty list.
        :type last_processed_time: List of datetime.
        :param file_name: The name of the file.( Default None)
        :type file_name: String
        :return: last_processed_time: The last processed_time for the data_source.
        """
        logging.info('DH_Utils: Fetching last processed time from database')
        with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                            'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
                self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
            if file_name:
                query = "select processed_time from applications_inventory where " \
                        "data_source='{}' and file_name = '{}'".format(self.data_source, file_name)
            else:
                query = "select processed_time from applications_inventory where data_source='{}'".format(
                    self.data_source)
            cursor.execute(query)
            for row in cursor.fetchall():
                last_processed_time.append(row[0])
        logging.info('DH_Utils: Finished fetching last processed time from database')
        return last_processed_time

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def get_last_updated_time(self, table, reference_time, datetime_col='datetime',
                              processed_time_col='processed_time'):
        """
        Get the last processed time for the given datasource/filename.

        :param datetime_col:
        :param processed_time_col:
        :param reference_time: The date to compare.(Should help to make query faster as well.)
        :type reference_time: Date/String.
        :param table: The table from which we need to get the processed time.
        :return: last_updated_time: The last updated_time for the given table and data type.
        """
        logging.info('DH_Utils: Fetching last updated time from database')
        with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                            'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
                self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
            query = "select max({}) from {} where {} > '{}'".format(processed_time_col, table, datetime_col
                                                                    , reference_time)
            cursor.execute(query)
            for row in cursor.fetchone():
                logging.info('DH_Utils: Finished fetching last processed time from database')
                return row

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def update_processed_time(self, status, errors, file_name=None, processed_time=None, file_date=None):
        """
        Update the processed_time in database for the given data_source.

        :param status: The status of the process (0 or 1)
        :type status: Integer
        :param errors: The no of errors if any.
        :type errors: Integer
        :param file_name: The name of the file.( Default None)
        :type file_name: String
        :param processed_time: Processed time of the file.
        :type: processed_time: String
        :param file_date: Processed file date.
        :type file_date: String
        :return: No return
        """
        logging.info('DH_Utils: Updating current processed time, status, errors and file_date into database.')
        with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                            'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
                self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
            if status == 0:
                query = "update applications_inventory set errors='{}', status='{}'" \
                        "where data_source='{}'".format(str(errors), str(status), self.data_source)
            else:
                if file_name:
                    query = "update applications_inventory set file_date='{}', processed_time='{}'," \
                            "errors='{}', status='{}' where data_source='{}' and file_name='{}'" \
                        .format(file_date, processed_time, errors, status, self.data_source, file_name)
                else:
                    query = "update applications_inventory set file_date='{}', processed_time='{}'," \
                            "errors='{}', status='{}' where data_source='{}'" \
                        .format(file_date, processed_time, errors, status, self.data_source)
            cursor.execute(query)
            cursor.execute('commit')
        logging.info('DH_Utils: Finished updating current processed time, status, errors and file_date into database.')

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def update_processed_time_validations(self, data_type, processed_time=None):
        """
        Update the processed_time in database for the given data_source.

        :param data_type: The type of data being inserted DA/ID
        :type: processed_time: String
        :param processed_time: Processed time of the file.
        :type: processed_time: String
        :return: No return
        """
        logging.info('DH_Utils: Updating latest updated time into database.')
        with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                            'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
                                    .format(self.driver, self.host, self.schema, self.user_name, self.password)) \
                .cursor() as cursor:
            query = "update ebal_validations_inventory set last_processed_time='{}'" \
                    "where data_source='{}' and type='{}'".format(processed_time, self.data_source, data_type)
        cursor.execute(query)
        cursor.execute('commit')
        logging.info('DH_Utils: Finished updating latest updated time into database.')

    @retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
    def get_err_count(self):
        """
        Get the error count for the current process.
        :return: count: Int
        """
        count = 0
        logging.info('DH_Utils: Getting error count if any for the current process.')
        try:
            with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                                'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
                    self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
                query = "select errors from applications_inventory " \
                        "where data_source='{}'".format(self.data_source)
                cursor.execute(query)
                for row in cursor.fetchall():
                    count = row[0]
        except Exception as dbexception:
            logging.info('DH_Utils: Database exception while getting error count.')
        logging.info('DH_Utils: Finished getting error count for the current process.')
        return count

    @retry(stop_max_attempt_number=100, wait_fixed=20, retry_on_exception=retry_if_error)
    @deprecated(version='1.1', reason="Do not update processed time and error count separately."
                                      "Use the update processed time method instead for updating both.")
    def update_err_count(self, count, status):
        """
        Set the error count for the current process.

        :param count: The error count.
        :type count: Int
        :param status: The process status to be updated
        :type status: Int
        :return: No return
        """
        logging.info('DH_Utils: Updating error count, status for the current process into database')
        with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(
                self.driver, self.host, self.schema, self.user_name, self.password)).cursor() as cursor:
            query = "update applications_inventory set errors='{}', status='{}'" \
                    "where data_source='{}'".format(str(count), str(status), self.data_source)
            cursor.execute(query)
            cursor.execute('commit')
        logging.info('DH_Utils: Finished updating error count, status for the current process into database')

    def __repr__(self):
        return "<{module}.{name} at {id_} (hosts={hosts})>".format(
            module=self.__class__.__module__,
            name=self.__class__.__name__,
            id_=hex(id(self)),
            hosts=self.host,
        )


@deprecated(version='1.1', reason="Methods have been re-written inside a class to remove duplication.")
@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
def get_processed_files_list(db_host, db_user_name, db_password, db_schema, db_driver, days_back,
                             processed_files_list, data_source):
    """
    Provide list of processed files for a particular date based on the days_back variable.

    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_driver: The driver to be used for the connection.
    :type db_driver: String
    :param days_back: Number  of days to go back, by default 0
    :param processed_files_list: empty  processed files list.
    :param data_source:  Name of the source
    :return: processed files list: It contains updated processed files list.
    """
    logging.info('DH_Utils: Fetching the list of processed files for a particular date from database')
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
            db_driver, db_host, db_schema, db_user_name, db_password)).cursor() as cursor:
        file_date = (date.today() - timedelta(days_back)).strftime("%Y-%m-%d")
        query = "select file_name from applications_inventory " \
                "where data_source='{}' and file_date>='{}'".format(data_source, file_date)
        cursor.execute(query)
        for row in cursor.fetchall():
            processed_files_list.append(row[0])
    logging.info('DH_Utils: Finished fetching the list of processed files for a particular date from database')
    return processed_files_list


@deprecated(version='1.1', reason="Methods have been re-written inside a class to remove duplication.")
@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
def update_processed_files_list(db_host, db_user_name, db_password, db_schema, db_driver, file_name, file_date,
                                processed_time, data_source):
    """
    Update the file_name in MSSQL database in processed file list.

    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_driver: The driver to be used for the connection.
    :type db_driver: String
    :param file_name: Name of the processed file.
    :type file_name: String
    :param file_date: Processed file date.
    :type file_date: String
    :param processed_time: Processed time of the file.
    :type processed_time: String
    :param data_source: Name of the source.
    :type data_source: String
    :return: No return
    """
    logging.info('DH_Utils: Updating current processed time,file name and file_date into database')
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
            db_driver, db_host, db_schema, db_user_name, db_password)).cursor() as cursor:
        query = "insert into applications_inventory(data_source,file_name,file_date,processed_time) " \
                "VALUES ('{}','{}','{}','{}')".format(data_source, file_name, file_date, processed_time)
        cursor.execute(query)
        cursor.execute('commit')
    logging.info('DH_Utils: Finished updating current processed time,file name and file_date into database')


@deprecated(version='1.1', reason="Methods have been re-written inside a class to remove duplication.")
@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
def get_last_processed_date(db_host, db_user_name, db_password, db_schema,
                            db_driver, last_processed_date, data_source, file_name=None):
    """
    Get the last processed date for the given datasource/filename.

    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_driver: The driver to be used for the connection.
    :type db_driver: String
    :param last_processed_date: empty list.
    :type last_processed_date: List of datetime.
    :param data_source: Name of the source
    :param file_name: The name of the file.( Default None)
    :type file_name: String
    :return: last_processed_time: The last processed_time for the data_source.
    """
    logging.info('DH_Utils: Fetching last processed date from database')
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
            db_driver, db_host, db_schema, db_user_name, db_password)).cursor() as cursor:
        if file_name:
            query = "select file_date from applications_inventory where data_source='{}' and file_name = '{}'" \
                .format(data_source, file_name)
        else:
            query = "select file_date from applications_inventory where data_source='{}'".format(data_source)
        cursor.execute(query)
        for row in cursor.fetchall():
            last_processed_date.append(row[0])
    logging.info('DH_Utils: Finished fetching last processed date from database')
    return last_processed_date


@deprecated(version='1.1', reason="Methods have been re-written inside a class to remove duplication.")
@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
def get_last_processed_time(db_host, db_user_name, db_password, db_schema, db_driver,
                            last_processed_time, data_source, file_name=None):
    """
    Get the last processed time for the given datasource/filename.

    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param db_driver: The driver to be used for the connection.
    :type db_driver: String
    :param last_processed_time: empty list.
    :type last_processed_time: List of datetime.
    :param data_source: Name of the source
    :param file_name: The name of the file.( Default None)
    :type file_name: String
    :return: last_processed_time: The last processed_time for the data_source.
    """
    logging.info('DH_Utils: Fetching last processed time from database')
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
            db_driver, db_host, db_schema, db_user_name, db_password)).cursor() as cursor:
        if file_name:
            query = "select processed_time from applications_inventory where data_source='{}' and file_name = '{}'" \
                .format(data_source, file_name)
        else:
            query = "select processed_time from applications_inventory where data_source='{}'".format(data_source)
        cursor.execute(query)
        for row in cursor.fetchall():
            last_processed_time.append(row[0])
    logging.info('DH_Utils: Finished fetching last processed time from database')
    return last_processed_time


@deprecated(version='1.1', reason="Methods have been re-written inside a class to remove duplication.")
@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
def update_processed_time(db_host, db_user_name, db_password, db_schema, db_driver, file_date, processed_time,
                          data_source, file_name=None):
    """
    Update the processed_time in database for the given data_source.

    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param file_date: Processed file date.
    :type file_date: String
    :param processed_time: Processed time of the file.
    :type: processed_time: String
    :param data_source: Name of the data source.
    :type: data_source: String
    :param db_driver: The driver to be used for the connection.
    :type db_driver: String
    :param file_name: The name of the file.( Default None)
    :type file_name: String
    :return: No return
    """
    logging.info('DH_Utils: Updating current processed time and file_date into database')
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
            db_driver, db_host, db_schema, db_user_name, db_password)).cursor() as cursor:
        if file_name:
            query = "update applications_inventory set file_date='{}', processed_time='{}'" \
                    "where data_source='{}' and file_name='{}'".format(file_date, processed_time, data_source,
                                                                       file_name)
        else:
            query = "update applications_inventory set file_date='{}', processed_time='{}'" \
                    "where data_source='{}'".format(file_date, processed_time, data_source)
        cursor.execute(query)
        cursor.execute('commit')
    logging.info('DH_Utils: Finished updating current processed time and file_date into database')


@deprecated(version='1.1', reason="Methods have been re-written inside a class to remove duplication.")
@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
def get_err_count(db_host, db_user_name, db_password, db_schema, db_driver, data_source):
    """
    Get the error count for the current process.

    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param data_source: The data_source for the current process.
    :type data_source: String
    :param db_driver: The driver to be used for the connection.
    :type db_driver: String
    :return: count: Int
    """
    count = 0
    logging.info('DH_Utils: Getting error count if any for the current process.')
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
            db_driver, db_host, db_schema, db_user_name, db_password)).cursor() as cursor:
        query = "select errors from applications_inventory " \
                "where data_source='{}'".format(data_source)
        cursor.execute(query)
        for row in cursor.fetchall():
            count = row[0]
    logging.info('DH_Utils: Finished getting error count for the current process.')
    return count


@deprecated(version='1.1', reason="Methods have been re-written inside a class to remove duplication."
                                  "Use the update processed time method instead for updating error count.")
@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=retry_if_error)
def update_err_count(db_host, db_user_name, db_password, db_schema, db_driver, count, status, data_source):
    """
    Set the error count for the current process.

    :param db_host: The database hostname/Ip Address.
    :type db_host: String
    :param db_user_name: The database username
    :type db_user_name: String
    :param db_password: The database password
    :type db_password: String
    :param db_schema: The database schema
    :type db_schema: String
    :param count: The error count.
    :type count: Int
    :param status: The process status to be updated
    :type status: Int
    :param data_source: The data_source for the current process.
    :type data_source: String
    :param db_driver: The driver to be used for the connection.
    :type db_driver: String
    :return: No returna
    """
    logging.info('DH_Utils: Updating error count, status for the current process into database')
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={};'
                        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'.format(
            db_driver, db_host, db_schema, db_user_name, db_password)).cursor() as cursor:
        query = "update applications_inventory set errors='{}', status='{}'" \
                "where data_source='{}'".format(str(count), str(status), data_source)
        cursor.execute(query)
        cursor.execute('commit')
    logging.info('DH_Utils: Finished updating error count, status for the current process into database')
