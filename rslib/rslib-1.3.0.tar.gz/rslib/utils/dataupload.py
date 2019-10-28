import collections
import traceback

from hdfs.ext.kerberos import KerberosClient
from rslib.utils.impala_utils import ImpalaUtils
import pandas as pd

BASEDIR = '/fuxi/up/'


def dataupload2hdfs(data, file, sep='\t'):
    client = KerberosClient("http://fuxi-luoge-01:50070;http://fuxi-luoge-11:50070")
    # print(client.list("/fuxi/up"))
    data = '\n'.join(sep.join(map(str, line)) for line in data)
    # data = '\n'.join(str(k) + sep + str(v) for k, v in data.items())
    tries = 5
    err = ''
    while tries > 0:
        try:
            client.write(BASEDIR + file, data=data, append=False, overwrite=True, encoding='utf8')
            print(('data upload 2 hdfs (%s times), ' + BASEDIR + file) % str(6 - tries))
            break
        except:
            err = traceback.format_exc()
            tries -= 1
    else:
        print('data upload 2 hdfs, failed')
        print(err)


def hdfs2hive(file, table, partition=None):
    # handler = ImpalaUtils(conn_type='impala')
    handler = ImpalaUtils(conn_type='hive')
    if partition:
        ADD_PAR = "alter table " + table + " add partition (ds='%s')" % partition
        handler.exec_sql_dml(sql=ADD_PAR)

    LOAD_HIVE = " LOAD DATA INPATH '" + BASEDIR + file + "'" + \
                " OVERWRITE INTO TABLE " + table
    if partition:
        LOAD_HIVE += " PARTITION (ds='%s') " % partition

    handler.exec_sql_dml(sql=LOAD_HIVE)
    print('hdfs 2 hive: ', LOAD_HIVE)
    handler.close_conn()

    handler = ImpalaUtils(conn_type='impala')
    META = 'INVALIDATE METADATA ' + table + ';'
    handler.exec_sql_dml(sql=META)
    handler.close_conn()


def create_table_from_pandas(df, table, sep=r'\t', partition=None):
    pandas2hive_type = collections.defaultdict(lambda: 'string')
    pandas2hive_type.update(
        {
            'int64': 'bigint',
            'float64': 'double',
            'object': 'string',
        }
    )
    # df = pd.DataFrame({'bb': [1, 2, 3], 'c': [2, 2, 3], 'aa': ['4', '5', '6']})
    # cols_type = [pandas2hive_type[col_type] if col_type in pandas2hive_type else 'string' for col_type in cols_type]
    CREATE_TABLE = r' CREATE EXTERNAL TABLE IF NOT EXISTS ' + table + '(' \
                   + ','.join(
        [str(col_name) + ' ' + pandas2hive_type[str(df[col_name].dtype)] for col_name in df.columns]) \
                   + ')'
    if partition:
        CREATE_TABLE += r' partitioned by (ds string)'

    if sep:
        CREATE_TABLE += r' ROW FORMAT DELIMITED FIELDS TERMINATED BY "' + sep + r'"'

    # CREATE_TABLE += r';'
    print(CREATE_TABLE)

    handler = ImpalaUtils(conn_type='hive')
    handler.exec_sql_dml(sql=CREATE_TABLE)
    print('create hive table: ', CREATE_TABLE)
    handler.close_conn()


def pandas2hive(df, table, partition=None):
    create_table_from_pandas(df, table, partition=partition)
    data = list(zip(*[df[col_name].tolist() for col_name in df.columns]))
    file = 'temp_file_' + table
    dataupload2hdfs(data, file)
    hdfs2hive(file, table, partition)


if __name__ == '__main__':
    # df = pd.DataFrame({'bb': [1, 2, 3], 'c': [2, 2, 3], 'aa': ['4', '5', '6']})
    # table = 'up_nsh_ads.diting_rslib_test'
    # pandas2hive(df, table)

    df = pd.DataFrame({'bb': [1, 2, 3], 'c': [2, 2, 3], 'aa': ['撒大声地', '5', '6']})
    table = 'up_nsh_tmp.diting_rslib_test_par21'
    partition = '2019-10-21'
    pandas2hive(df, table, partition)

    # data = 'aaaaaaa' * 10
    # print('dasdasd')
    # dataupload2hdfs(data, 'test_file')
