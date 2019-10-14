import os
from pathlib import Path
import logging
import re
import jaydebeapi
import jpype
import pandas as pd

from pydtc.utils import exec_time

## dict of database software name to jdbc driver class name
driver_class = {
               'db2': 'com.ibm.db2.jcc.DB2Driver',
               'teradata': 'com.teradata.jdbc.TeraDriver',
               'mssql': 'com.microsoft.sqlserver.jdbc.SQLServerDriver',
               'oracle': 'oracle.jdbc.driver.OracleDriver',
               'mysql': 'com.mysql.cj.jdbc.Driver'
               }

class DBCon():
    '''
    Class wrapping the connection to database via jdbc with batch/fast
    load capability.

    The jdbc driver jar file(s) to be supplied by the user which can be easily
    accquired and to be placed into folder jdbc_driver under the user's home
    directory.
    '''

    def __init__(self, db, host, user, password, database=None, driver=None, runtime_path=None):
        '''
        Instance of DBCon class.

        param:
            db: str; db2|teradata|mssql|mysql etc.
            host: str; url of db server.
            user: str
            password: str
            database: str; if not set, use xxx; before any operation; default None
            driver: str; the driver class name; default None
            runtime_path: str; location of the jvm lib, optional       
        '''

        self.logger = logging.getLogger(__name__)

        if runtime_path:
            jvm = runtime_path
        else:
            jvm = jpype.getDefaultJVMPath()

        self._db = db
        self._host = host
        self._user = user
        self._pass = password
        self._default = database

        self._conn = None
        self._cur = None

        try:
            self._driver = driver_class[db]
        except KeyError:
            if driver:
                self._driver = driver
            else:
                raise Exception('unknown driver class name. specify like: ' +
                                'driver = com.mysql.jdbc.Driver')

        lib_path = os.path.join(str(Path.home()), 'jdbc_driver')
        if not os.path.exists(lib_path):
            os.makedirs(lib_path)

        classes = [c for c in os.listdir(lib_path) if c.endswith('.jar')]

        if len(classes) == 0:
            raise Exception('no jar file(s) provided.')

        if os.name == 'nt':
            _path = ';'.join([os.path.join(lib_path, c) for c in classes])
        else:
            _path = ':'.join([os.path.join(lib_path, c) for c in classes])

        args = '-Djava.class.path={}'.format(_path)
        if jpype.isJVMStarted():
            pass
        else:
            jpype.startJVM(jvm, args)

    def connect(self):
        if self._default:
            connectionstring = 'jdbc:{}://{}/{}'.format(self._db, self._host, self._default)
        else:
            connectionstring = 'jdbc:{}://{}'.format(self._db, self._host)

        try:
            self._conn = jaydebeapi.connect(self._driver, connectionstring,
                                            [self._user, self._pass],
                                            None,)

            self._conn.jconn.setAutoCommit(False)
            self._cur = self._conn.cursor()

            self.logger.warning('Connected: %s', self._db)

        except jpype.JavaException as err:
            self.logger.error(err)
            raise

    @exec_time()
    def create_temp(self, sqlstr):
        '''
        param:
            sqlstr: str; sql statement, e.g. create temporary table temp (id int)
        '''

        try:
            stmt = self._conn.jconn.createStatement()
            stmt.executeUpdate(sqlstr)
            self._conn.commit()

            stmt.close()
        except Exception:
            self.logger.exception('Temporary table creation failed.')
            raise

    @exec_time()
    def load_temp(self, sqlstr, indata, chunksize=10000):
        '''
        param:
            sqlstr: str; sql statement
            indata: DataFrame; data to be inserted into temp table
            chunksize: int; default to 10000
        '''

        if isinstance(indata, pd.DataFrame):
            try:
                pstmt = self._conn.jconn.prepareStatement(sqlstr)

                _schema = [str(indata[c].dtype) for c in indata.columns]
                for i in range(0, len(indata), chunksize):
                    _data = indata.iloc[i: i+chunksize]
                    for j in zip(*_data.T.values.tolist()):
                        for k in range(len(j)):
                            if _schema[k].find('int') == 0:
                                pstmt.setInt(k+1, j[k])
                            elif _schema[k].find('obj') == 0:
                                pstmt.setString(k+1, j[k])

                        pstmt.addBatch()

                    pstmt.executeBatch()

                self._conn.commit()
                pstmt.close()
            except Exception:
                self.logger.exception('Temporary table insertion failed:')
                raise
        else:
            raise Exception('Input takes dataframe only')

    @exec_time()
    def read_sql(self, sqlstr):
        '''
        param:
            sqlstr: str; sql statement
        '''

        self._cur.execute(sqlstr)

        rows = []
        columns = [column[0] for column in self._cur.description]

        self.logger.debug('Columns: %s', columns)

        _has_rows = False
        for row in self._cur.fetchall():
            _has_rows = True
            r = dict(zip(columns, row))
            rows.append(r)

        if _has_rows:
            return pd.DataFrame(rows)
        else:
            return pd.DataFrame(columns=columns)

    def close(self):
        try:
            self._cur.close()
            self._conn.close()
        except Exception as e:
            self.logger.warning(e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
