import warnings

from nameko.dependency_providers import DependencyProvider
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.exceptions import RpcTimeout
from nameko.events import event_handler

from nameko_wrapper.config import amqp_config
from nameko.rpc import rpc as nameko_rpc


class CrontabDependency(DependencyProvider):
    """Crontab Dependency"""
    tasks = []

    def __init__(self, service_name, crontab_service_name='scheduler', timeout=7):
        """初始化Crontab依赖
        
        :param str service_name: 注入服务名称
        :param str crontab_service_name: 定时调度微服务名称
        :timeout int timeout: 定时任务调用超时时间（单位：秒）
        """
        self.dispatch_service_name = service_name
        self.crontab_service_name = crontab_service_name
        self.timeout = timeout
        self.is_register = False

    def bind(self, container, attr_name):
        """绑定属性"""
        setattr(container.service_cls, '__scheduler_started_handle', self.add_listen_schedule_service_start())
        return super().bind(container, attr_name)

    def setup(self):
        """向Crontab微服务进行任务注册"""
        self.register_tasks()

    def stop(self):
        """当正常停止服务时调用"""
        self.remove_tasks()

    def kill(self):
        """当强制结束时调用"""
        self.remove_tasks()

    def get_dependency(self, worker_ctx):
        """获取依赖"""
        return self
    
    def add_listen_schedule_service_start(self):
        """监听调度服务启动"""
        @event_handler(self.crontab_service_name, 'scheduler_started')
        def scheduler_started(instance, payload):
            self.register_tasks()
        return scheduler_started

    def _call_crontab_service(self, method_name, *args, **kwargs):
        with ClusterRpcProxy(amqp_config, timeout=self.timeout) as cluster_rpc:
            crontab_service = getattr(cluster_rpc, self.crontab_service_name)
            crontab_service_method = getattr(crontab_service, method_name)
            try:
                result = crontab_service_method(*args, **kwargs)
                print('To service <{0}> register task `{1}` result: {2}'.format(self.crontab_service_name, method_name, result))
                self.is_register = True
            except RpcTimeout:
                warnings.warn(
                    "`{}` service may not start, crontab relative function is unavailable".format(self.crontab_service_name)
                )

    def register_tasks(self):
        """注册任务"""
        self._call_crontab_service('register_tasks', self.dispatch_service_name, self.tasks)

    def remove_tasks(self):
        """移除任务"""
        self.tasks = []
        self._call_crontab_service('remove_tasks', self.dispatch_service_name)

    def add_task(self, task_name, method, unit, mode, value, params, options):
        """添加任务"""
        for index, item in enumerate(self.tasks):
            if task_name == item['name']:
                self.tasks.pop(index)

        self.tasks.append({
            'name': task_name, 'method': method, 'unit': unit, 'mode': mode, 'value': value, 'params': params, 'options': options
        })

    def event_handler(self, value, unit=None, mode=None, *, params=None, **options):
        """event handler 装饰器

        :param str value: 调度规则
        :param str unit: 调度单位，如`second, ...`
        :param str mode: 调度模式，支持`周期调度`和`定时调度`
        :param obj params: 任务执行参数，可以任意对象
        :param obj options: job 选项

        调用对象必须包含一个可调用参数
        """
        def wrapper(func):
            # 添加任务
            # 此处`event_type`为`服务名-函数名`避免与其它服务冲突
            self.add_task(func.__name__, 'event', unit, mode, str(value), params, options)
            return event_handler(self.crontab_service_name, self.dispatch_service_name + '&' + func.__name__)(func)
        return wrapper

    def rpc(self, value, unit=None, mode=None, *, params=None, **options):
        """RPC 装饰器
        
        :param str value: 调度规则
        :param str unit: 调度单位，如`second, ...`
        :param str mode: 调度模式，支持`周期调度`和`定时调度`
        :param obj params: 任务执行参数，可以任意对象

        调用对象必须包含一个可调用参数
        """
        def wrapper(func):
            # print('wrapper function:', func)
            self.add_task(func.__name__, 'rpc', unit, mode, value, params, options)

            @nameko_rpc
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner
        return wrapper
