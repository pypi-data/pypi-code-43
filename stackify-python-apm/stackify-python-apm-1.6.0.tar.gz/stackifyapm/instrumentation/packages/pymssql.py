from stackifyapm.instrumentation.packages.dbapi2 import (
    ConnectionProxy,
    CursorProxy,
    DbApi2Instrumentation,
)


class PyMSSQLCursorProxy(CursorProxy):
    provider_name = "pymssql"


class PyMSSQLConnectionProxy(ConnectionProxy):
    cursor_proxy = PyMSSQLCursorProxy


class PyMSSQLInstrumentation(DbApi2Instrumentation):
    name = "pymssql"

    instrument_list = [("pymssql", "connect")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        return PyMSSQLConnectionProxy(wrapped(*args, **kwargs))
