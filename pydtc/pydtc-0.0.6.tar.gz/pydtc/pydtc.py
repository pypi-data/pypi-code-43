import asyncio
from pydtc.connection import DBClient, APIClient
from pydtc.parallelize import ParallelDataFrame

def connect(db, host, user, password, database=None, driver=None, runtime_path=None):
    con = DBClient(db, host, user, password, database=database, driver=driver, runtime_path=None)
    con.connect()

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
    except:
        raise
    finally:
        pdf.close()


def p_groupby_apply(func, df, groupkey, cores=None):
    try:
        pdf = ParallelDataFrame(df, num_ps=cores)

        return pdf.group_apply(func, groupkey)
    except:
        raise
    finally:
        pdf.close()


def api_get(urls, auth=None, loop=None):
    if loop:
        _loop = loop
    else:
        try:
            _loop = asyncio.get_running_loop()
        except RuntimeError:
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    try:
        api = APIClient(auth=auth, loop=_loop)

        if isinstance(urls, list):
            results = _loop.run_until_complete(api.fetch_all(urls))
        else:
            results = _loop.run_until_complete(api.fetch(urls))

        return results
    except:
        raise
    finally:
        asyncio.run(api.close())


def api_update(url, data=None, method='put', auth=None, loop=None):
    if loop:
        _loop = loop
    else:
        try:
            _loop = asyncio.get_running_loop()
        except RuntimeError:
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    try:
        api = APIClient(auth=auth, loop=_loop)

        results = _loop.run_until_complete(api.update(url, data=data, method=method))

        return results
    except:
        raise
    finally:
        asyncio.run(api.close())