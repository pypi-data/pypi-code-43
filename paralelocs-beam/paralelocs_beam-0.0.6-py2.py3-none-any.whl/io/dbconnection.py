from __future__ import absolute_import
import sqlalchemy
import os
import stat
import logging

from sqlalchemy import Column, Integer, String, MetaData, create_engine, text
from sqlalchemy.schema import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from google.cloud import storage
from google.oauth2 import service_account



__all__=['DBHandle', 'DBConfig']


class DBConfig():

    def __init__(self, 
                drivername = None, 
                username = None, 
                password = None, 
                database = None, 
                tablename = None,
                host = None,
                port = 5432,
                connect_args=None):

        self.database = database
        self.host = host
        self.port = port

        self.connection_config = URL(
                                    drivername= drivername,
                                    username= username,
                                    password= password,
                                    host= host,
                                    database= database,
                                    port=port
                                )
        self.connect_args = connect_args

class Connection():

    def __init__(self, db_config, connect_args):
        self.db_config = db_config
        self.connect_args=connect_args
        if connect_args is not None:
            self.get_credentials()

    def __enter__(self):
        logging.info('Opening database connection on host {}, port {} and database {}...'.format(self.db_config.host, self.db_config.port, self.db_config.database))
        if self.connect_args is None:
            self.engine = create_engine(self.db_config)

        else:
            self.engine = create_engine(self.db_config, connect_args= self.connect_args)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        return (self.engine, self.session)
        

    def __exit__(self, type, value, traceback):
        logging.info('Closing database connection...')
        self.session.close()
        self.session.bind.dispose()

    def get_credentials(self):
        logging.info('Getting credentials to SSL connection..')
        client = storage.Client()
        bucket = client.get_bucket('perfect-order-api.appspot.com')
        bucket.get_blob('cloud_sql_ssl/server-ca.pem').download_to_filename('server-ca.pem')
        bucket.get_blob('cloud_sql_ssl/client-key.pem').download_to_filename('client-key.pem')
        os.chmod("client-key.pem", stat.S_IRWXU)
        bucket.get_blob('cloud_sql_ssl/client-cert.pem').download_to_filename('client-cert.pem')



class DBHandle(object):

    def __init__(self, tablename, db_config, filters= None, batch_size=3):
        self.tablename = tablename
        self.db_config = db_config
        self.filters = filters
        self.batch_size = batch_size
        self.table_object = self._get_table_object()
        self.columns_name = self._get_columns_name()

    def connection(self):
        return Connection(self.db_config.connection_config, self.db_config.connect_args)

    def read(self):
        with self.connection() as conn:
            logging.info('Reading data {} from database {}..'.format(self.tablename, self.db_config.database))
            engine, session = conn
            for record in self._windowed_query(session.query(self.table_object), self.table_object.id, session):
                yield self._serialize(record)

    def _get_table_object(self):
        with self.connection() as conn:
            logging.info('Getting metadata from table {} from database {}...'.format(self.tablename, self.db_config.database))
            engine, session = conn
            return create_table_object(Table(self.tablename, MetaData(bind=engine), autoload = True))

    def _get_columns_name(self):
        return {k.name for (k) in self.table_object.__table__.columns}
    
    def _serialize(self, record):
        return {col: getattr(record, col) for col in self.columns_name}

    def _column_windows(self, column, session):
        """Return a series of WHERE clauses against 
        a given column that break it into windows.

        Result is an iterable of tuples, consisting of
        ((start, end), whereclause), where (start, end) are the ids.
        
        Requires a database that supports window functions, 
        i.e. Postgresql, SQL Server, Oracle.

        Enhance this yourself !  Add a "where" argument
        so that windows of just a subset of rows can
        be computed.

        """
        def int_for_range(start_id, end_id):
            if end_id:
                return and_(
                    column>=start_id,
                    column<end_id
                )
            else:
                return column>=start_id
        
            
        q = session.query(
                    column, 
                    func.row_number().\
                            over(order_by=column).\
                            label('rownum')
                    ).\
                    from_self(column)
        if self.batch_size > 1:
            q = q.filter(sqlalchemy.text("rownum %% %d=1" % self.batch_size))

        intervals = [id for id, in q]

        while intervals:
            start = intervals.pop(0)
            if intervals:
                end = intervals[0]
            else:
                end = None
            yield int_for_range(start, end)
    
    def _windowed_query(self, queryset, column, session):
        """"Break a Query into windows on a given column."""

        for whereclause in self._column_windows(column, session):
            if self.filters is None:
                for row in queryset.filter(whereclause).order_by(column):
                    yield row
            else:
                for row in queryset.filter(whereclause, text(self.filters)).order_by(column):
                    yield row

def create_table_object(table_object):

    class TableObject(declarative_base()):
        __table__ = table_object

    return TableObject