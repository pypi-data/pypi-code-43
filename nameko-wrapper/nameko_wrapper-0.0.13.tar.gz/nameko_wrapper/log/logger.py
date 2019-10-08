"""Logger"""
from nameko.standalone.rpc import ClusterRpcProxy

from ..rpc import caller
from ..config import Config, amqp_config


class Logger(object):

    def __init__(self, service_name, load_config=True):
        """初始化日志记录器

        :param service_name: 需要记录的服务名称
        """
        self.logger_service_name = 'log'
        self.logger_service_record_func = 'record'
        self.service_name = service_name
        self.all_modes = ['service', 'api', 'action']
        self.load_default_config()

        if load_config:
            self.load_config()

    def load_default_config(self):
        """默认配置"""
        self._all_config = {}
        self._logger_setting = self._all_config.get('LOGGER', {})
        self._timeout = self._logger_setting.get('TIMEOUT', 3)
        self._is_async = self._logger_setting.get('ASYNC', False)

        # service config
        self._service_config = {
            'enable': True
        }
        # api config
        self._api_config = {
            'enable': True
        }
        # action config
        self._action_config = {
            'enable': True
        }

    def load_config(self):
        # 读取配置
        self._all_config = Config().to_dict()
        self._logger_setting = self._all_config.get('LOGGER', {})
        self._timeout = self._logger_setting.get('TIMEOUT', 3)
        self._is_async = self._logger_setting.get('ASYNC', False)

        self._service_config.update(self._logger_setting.get('SERVICE', {}))
        self._api_config.update(self._logger_setting.get('API', {}))
        self._action_config.update(self._logger_setting.get('ACTION', {}))

    def _send(self, mode, **kwargs):
        """发送记录日志"""
        if mode not in self.all_modes:
            raise ValueError(f"mode does not in all support modes[{self.all_modes}]")

        payload = kwargs
        payload['service'] = self.logger_service_name
        return caller(
            self.logger_service_name,
            self.logger_service_record_func,
            is_async=self._is_async,
            timeout=self._timeout
        )(mode, payload)

    def _service_log(self, level, msg, **kwargs):
        """Service Log"""
        return self._send('service', level=level, message=msg, **kwargs)

    def debug(self, msg, **kwargs):
        """记录程序信息"""
        return self._service_log(level='debug', msg=msg, **kwargs)

    def info(self, msg, **kwargs):
        """记录程序信息"""
        return self._service_log(level='info', msg=msg, **kwargs)

    def warning(self, msg, **kwargs):
        """记录程序信息"""
        return self._service_log(level='warning', msg=msg, **kwargs)

    def error(self, msg, **kwargs):
        """记录程序信息"""
        return self._service_log(level='error', msg=msg, **kwargs)

    def critical(self, msg, **kwargs):
        """记录程序信息"""
        return self._service_log(level='critical', msg=msg, **kwargs)

    def api_watch(self, *args, **kwargs):
        """监视接口装饰器"""
        return self._send('api', *args, **kwargs)

    def action(self, *args, **kwargs):
        """记录用户行为"""
        return self._send('action', *args, **kwargs)

    def route_watch(self, request):
        """路由监控"""
        def wrapper(func):
            print('route watch:', request, dir(request), func)
            # 获取请求参数

            def call(*args, **kwargs):
                return func(*args, **kwargs)

            return call

        return wrapper
