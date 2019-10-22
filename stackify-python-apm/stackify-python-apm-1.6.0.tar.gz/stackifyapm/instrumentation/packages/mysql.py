from stackifyapm.instrumentation.packages.dbapi2 import (
    ConnectionProxy,
    CursorProxy,
    DbApi2Instrumentation,
)


class MySQLCursorProxy(CursorProxy):
    provider_name = "mysql"


class MySQLConnectionProxy(ConnectionProxy):
    cursor_proxy = MySQLCursorProxy


class MySQLInstrumentation(DbApi2Instrumentation):
    name = "mysql"

    instrument_list = [("MySQLdb", "connect"), ('flaskext.mysql', 'MySQL.connect')]

    def call(self, module, method, wrapped, instance, args, kwargs):
        return MySQLConnectionProxy(wrapped(*args, **kwargs))
