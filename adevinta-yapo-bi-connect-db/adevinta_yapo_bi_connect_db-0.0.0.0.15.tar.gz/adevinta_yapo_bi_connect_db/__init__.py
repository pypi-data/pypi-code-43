import sys
import psycopg2
from sqlalchemy import create_engine
import os
import pandas as pd
import logging

class connect_db(object):
    def __init__(self, dbname, user, host, password, port ):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.engine = ""
        self.conn_psycopg2 = ""
        self.logger_db = logging.getLogger('connect_db')
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d - %(funcName)20s()] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.DEBUG)

    def get_dbname( self ):
        self.logger_db.info('Get database name.')
        return self.dbname

    def get_user( self ):
        self.logger_db.info('Get username.')
        return self.user

    def get_password( self ):
        self.logger_db.info('Get password.')
        return self.password

    def get_host( self ):
        self.logger_db.info('Get host.')
        return self.host

    def get_port( self ):
        self.logger_db.info('Get port.')
        return self.port

    def set_dbname(self, dbname ):
        self.logger_db.info('Set database name.')
        self.dbname = dbname

    def set_user(self, user ):
        self.logger_db.info('Set username.')
        self.user = user

    def set_password(self, password ):
        self.logger_db.info('Set password.')
        self.password = password

    def set_host(self, host ):
        self.logger_db.info('Set host.')
        self.host = host

    def set_port(self, port ):
        self.logger_db.info('Set port.')
        self.port = port

    def get_connection(self, type ):
        try:
            if type == 'engine':
                self.logger_db.info('Connect database postgresql method engine.')
                self.engine = create_engine('postgresql://'+self.user+':'+self.password+'@'+self.host+':'+self.port+'/'+self.dbname,echo=False)
            elif type == 'conn_psycopg2':
                self.logger_db.info('Connect database postgresql method psycopg2.')
                self.conn_psycopg2 = psycopg2.connect("dbname='"+self.dbname+"' user='"+self.user+"' host='"+self.host+"' password='"+self.password+"'")
        except Exception as e:
            self.logger_db.error('%s' % e)
            exit(e)

    def delete_table( self, query ):
        try:
            self.logger_db.info('Open cursor.')
            cur = self.conn_psycopg2.cursor()
            self.logger_db.info('Execute delete.')
            cur.execute(query)
            self.conn_psycopg2.commit()
            self.logger_db.info('Commit delete.')
            cur.close()
            self.logger_db.info('Close cursor.')
        except Exception as e:
            self.logger_db.error('%s' % e)
            cur.close()
            self.conn_psycopg2.rollback()
            self.conn_psycopg2.close()
            exit(e)

    def select_table( self, query ):
        try:
            self.logger_db.info('Select query.')
            query_output = pd.read_sql_query(query,con=self.engine)
            return query_output
        except Exception as e:
            self.logger_db.error('%s' % e)
            self.engine.connect().close()
            exit(e)

    def insert_table( self, query, schema_write, table_write, if_exists, index, chunksize ):
        try:
            self.logger_db.info('Insert data.')
            query.to_sql(name=table_write, con=self.engine, schema=schema_write, if_exists=if_exists, index=index, chunksize=chunksize)
        except Exception as e:
            self.logger_db.error('%s' % e)
            self.engine.connect().close()
            exit(e)

    def close_connection( self, type ):
        try:
            if type == 'engine':
                self.logger_db.info('Close connection engine.')
                self.engine.connect().close()
            elif type == 'conn_psycopg2':
                self.logger_db.info('Close connection psycopg2.')
                self.conn_psycopg2.close()
        except Exception as e:
            self.logger_db.error('%s' % e)
            exit(e)
