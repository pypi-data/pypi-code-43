import pymysql


class MyDBException(Exception):
    pass


class MultiColumnsError(MyDBException):
    pass


class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('"Dict" object has no attribute "{}"'.format(key))

    def __setattr__(self, key, value):
        self[key] = value


class _Engine(object):
    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


class MysqlWrapper(object):
    def __init__(self, user, passwd, db, host, port, **kwargs):
        params = dict(user=user, passwd=passwd, db=db, host=host, port=port)
        defaults = dict(use_unicode=True, charset='utf8')
        for k, v in defaults.items():
            params[k] = kwargs.pop(k, v)
        params.update(kwargs)
        self.params = params
        self.engine = _Engine(lambda: pymysql.connect(**params))
        self.conn = None

    def __enter__(self):
        return self

    def get_conn(self):
        self._get_conn()

    def is_connected(self):
        return self.__is_connected()

    def __is_connected(self):
        if not self.conn:
            return False
        else:
            try:
                result = self.conn.ping()
                if self.conn.__module__.startswith('MySQLdb'):
                    if result is None:
                        return True
                    else:
                        return False
                elif self.conn.__module__.startswith('cymysql'):
                    if result is True:
                        return True
                    else:
                        return False
                else:
                    return result
            except Exception as err:
                return False

    def __exit__(self, *args):
        if self.conn:
            if self.__is_connected():
                self.conn.close()

    def _get_conn(self):
        if self.__is_connected():
            pass
        else:
            self.conn = self.engine.connect()

    def select_one(self, sql, *args):
        return self._select(sql, True, *args)

    def select(self, sql, *args):
        return self._select(sql, False, *args)

    def select_int(self, sql, *args):
        d = self._select(sql, True, *args)
        if len(d) != 1:
            raise MultiColumnsError('Except only one column')
        return d.values()[0]

    def insert(self, table, **kw):
        cols, args = zip(*kw.items())
        sql = 'insert into {table} ({fields}) values ({values})'.format(
            table=table,
            fields=' ,'.join(['`%s`' % col for col in cols]),
            values=' ,'.join(['?' for _ in cols])
        )
        return self._update(sql, *args)

    def update(self, sql, *args):
        return self._update(sql, *args)

    def _select(self, sql, only_first, *args):
        self._get_conn()
        cursor = None
        sql = sql.replace('?', '%s')
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, args)
            if cursor.description:
                names = [x[0] for x in cursor.description]
            if only_first:
                values = cursor.fetchone()
                if not values:
                    return None
                return Dict(names, values)
            return [Dict(names, x) for x in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()

    def _update(self, sql, *args):
        self._get_conn()
        cursor = None
        sql = sql.replace('?', '%s')
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, args)
            r = cursor.lastrowid
            try:
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise Exception(e)
            return r
        finally:
            if cursor:
                cursor.close()
