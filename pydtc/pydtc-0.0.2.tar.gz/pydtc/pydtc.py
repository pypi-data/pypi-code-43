import warnings
from pydtc.connection import DBCon
from pydtc.parallelize import ParallelDataFrame

def connect(db, host, user, password, database=None, driver=None):
    con = DBCon(db, host, user, password, database=database, driver=driver)
    con.connect()
    warnings.warn('use close() method at the end.')

    return con


def read_sql(con, sql):

    return con.read_sql(sql)


def create_temp(con, sql):

    con.create_temp(sql)


def load_temp(con, sql, df, chunksize=10000):

    con.load_temp(sql, df, chunksize=chunksize)


# speed up pandas cpu operation with multiprocessing especially for large set.
def p_apply(func, df, chunksize=10000, cores=None):
    try:
        pdf = ParallelDataFrame(df, num_ps=cores)

        return pdf.apply(func, chunksize=chunksize)

    finally:
        pdf.close()


def p_groupby_apply(func, df, groupkey, cores=None):
    try:
        pdf = ParallelDataFrame(df, num_ps=cores)

        return pdf.group_apply(func, groupkey)

    finally:
        pdf.close()