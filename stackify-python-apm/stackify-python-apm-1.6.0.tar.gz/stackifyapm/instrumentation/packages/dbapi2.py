from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import wrapt, get_method_name
from stackifyapm.utils.helper import is_async_span


class CursorProxy(wrapt.ObjectProxy):
    provider_name = None
    name = None

    def callproc(self, procname, params=None):
        return self._trace_sql(self.__wrapped__.callproc, procname, params)

    def execute(self, sql, params=None):
        return self._trace_sql(self.__wrapped__.execute, sql, params)

    def executemany(self, sql, param_list):
        return self._trace_sql(self.__wrapped__.executemany, sql, param_list)

    def _bake_sql(self, sql):
        return sql

    def _trace_sql(self, method, sql, params):
        sql_string = self._bake_sql(sql)
        kind = "db.{0}.sql".format(self.provider_name)
        extra_data = {
            "wrapped_method": get_method_name(method),
            "provider": self.name or self.provider_name,
            "type": "Database",
            "sub_type": "database_sql",
            "statement": sql_string,
        }
        with CaptureSpan(kind, extra_data, is_async=is_async_span()):
            if params is None:
                return method(sql)
            else:
                return method(sql, params)


class ConnectionProxy(wrapt.ObjectProxy):
    cursor_proxy = CursorProxy

    def cursor(self, *args, **kwargs):
        return self.cursor_proxy(self.__wrapped__.cursor(*args, **kwargs))


class DbApi2Instrumentation(AbstractInstrumentedModule):
    connect_method = None

    def call(self, module, method, wrapped, instance, args, kwargs):
        return ConnectionProxy(wrapped(*args, **kwargs))

    def call_if_sampling(self, module, method, wrapped, instance, args, kwargs):
        return self.call(module, method, wrapped, instance, args, kwargs)
