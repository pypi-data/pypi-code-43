from hdfs.ext.kerberos import KerberosClient
from rslib.utils.impala_utils import ImpalaUtils

BASEDIR = '/fuxi/up/'

def dataupload2hdfs(data, file, sep=','):
    client = KerberosClient("http://fuxi-luoge-01:50070;http://fuxi-luoge-11:50070")
    # print(client.list("/fuxi/up"))
    data = '\n'.join(sep.join(map(str, line)) for line in data)
    # data = '\n'.join(str(k) + sep + str(v) for k, v in data.items())
    tries = 3
    while tries > 0:
        try:
            client.write(BASEDIR + file, data=data, append=False, overwrite=True)
            print('data upload 2 hdfs, ' + BASEDIR + file)
            break
        except:
            tries -= 1
    else:
        print('data upload 2 hdfs, failed')


def hdfs2hive(file, table, ds):
    handler = ImpalaUtils(conn_type='impala')

    ADD_PAR = "alter table " + table + " add partition (ds='%s')" % ds
    handler.exec_sql_dml(sql=ADD_PAR)

    LOAD_HIVE = " LOAD DATA INPATH '" + BASEDIR + file + "'" + \
                " OVERWRITE INTO TABLE " + table + \
                " PARTITION (ds='%s') " % ds
    handler.exec_sql_dml(sql=LOAD_HIVE)
    print('hdfs 2 hive: ', LOAD_HIVE)
    handler.close_conn()
