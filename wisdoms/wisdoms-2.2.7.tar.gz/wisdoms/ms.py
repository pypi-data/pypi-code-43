# Used for micro-service which developed by nameko
# install nameko before use
"""
    Example::

        from wisdoms.auth import permit

        host = {'AMQP_URI': "amqp://guest:guest@localhost"}

        auth = permit(host)

        class A:
            @auth
            def func():
                pass
"""
from nameko.rpc import rpc

from nameko.standalone.rpc import ServiceRpcProxy

from nameko.exceptions import RpcTimeout, MethodNotFound

from functools import wraps
from operator import methodcaller

from wisdoms.utils import xpt_func
from wisdoms.exec import UserException
from wisdoms.commons import revert, codes

default_host = {'AMQP_URI': 'pyamqp://guest:guest@localhost'}
default_base_service = 'baseUserApp'


def rpc_with_timeout(host, service, func, data=None, timeout=8):
    try:
        with ServiceRpcProxy(service, host, timeout=timeout) as proxy:
            if data is not None:
                res = methodcaller(func, data)(proxy)
            else:
                res = methodcaller(func)(proxy)
            return res
    except RpcTimeout as e:
        print(service, ' ~~连接超时 %s sec......，检查是否启动......' % e)
        return revert(codes.TIMEOUT, desc=service + ' 连接超时')
    except MethodNotFound as e:
        print('function of this server not found,未找到方法 %s ' % e)
        return revert(codes.GET_WAY_ERROR, desc='未找到方法' + e)


def rpc_wrapper(service_, func_, *args, host_=default_host, timeout_=8, **kwargs):
    """
    rpc包装方法

    :param service_:
    :param func_:
    :param host_:
    :param timeout_:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        with ServiceRpcProxy(service_, host_, timeout=timeout_) as proxy:
            res = methodcaller(func_, *args, **kwargs)(proxy)
            return res
    except RpcTimeout as e:
        print(service_, ' ~~连接超时 %s sec......，检查是否启动......' % e)
        return revert(codes.TIMEOUT, desc=service_ + ' 连接超时')
    except MethodNotFound as e:
        print('function of this server not found,未找到方法 %s ' % e)
        return revert(codes.GET_WAY_ERROR, desc='未找到方法' + e)


def ms_base(ms_host=None, base_service=None, func=None, **extra):
    """
    返回父类，闭包，传参数ms host
    :param ms_host:
    :param base_service
    :param func
    :param extra: 额外信息
    :extra: roles 角色权限
    :extra: name 微服务名称
    :extra: types 微服务类型 essential 类型的应用 角色必须带creator
    :extra: entrance 微服务pc入口
    :extra: entrance4app 小程序入口
    :extra: entrance4back 后台入口
    :extra: identity 唯一标识 暂时只用于平台base service 其他微服务不添加
    :return: class of base
    """

    ms_host = ms_host if ms_host else default_host
    base_service = base_service if base_service else default_base_service
    func = func if func else 'app2db'

    class MsBase:
        name = 'ms-base'

        @rpc
        # @exception()
        def export_info2db(self):
            """
            export information of this service to database

            :return:
            """
            clazz = type(self)
            service = clazz.name
            functions = dir(clazz)

            origin = extra
            origin['service'] = service
            origin['functions'] = functions

            rpc_with_timeout(ms_host, base_service, func, origin)

    return MsBase


def permit(host=None, **extra):
    """
    调用微服务功能之前，进入基础微服务进行权限验证

    :param: host: micro service host
    :extra: service 基础应用微服务名称
    :extra: func 用户验证方法名称
    :extra: full_info 是否携带用户和组织全部信息 默认false
    :return decorator
    """
    host = host if host else default_host
    base_service = extra.get('service', default_base_service)
    verify_func = extra.get('func', 'verify')

    full_info = extra.get('full_info', False)

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            service = args[0].name
            func = f.__name__
            token = args[1].get('token')

            res = rpc_with_timeout(host, base_service, verify_func, {'service': service, 'func': func, 'token': token})

            try:
                # judge except
                if res.get('code'):
                    if res.get('code') < 0:
                        return res
            except:
                pass

            if res:

                org = None

                try:
                    # 添加组织信息 add info of org
                    org = res.get('org').get(str(res.get('current_org')))
                except:
                    pass

                try:
                    # delete user passoword
                    del res['password_hash']
                    del res['partner']
                except:
                    pass

                cut_user = dict()
                cut_org = dict()

                cut_user['id'] = res['id']
                cut_user['account'] = res['account']
                cut_user['username'] = res['username']
                cut_user['current_org'] = res.get('current_org')
                cut_user['phone'] = res.get('phone')
                cut_user['email'] = res.get('email')

                try:
                    if org:
                        cut_org['id'] = org['id']
                        cut_org['name'] = org['name']
                        cut_org['desc'] = org['desc']
                        cut_org['owner'] = org['owner']
                        cut_org['region'] = org['region']
                        cut_org['es_extend'] = org['es_extend']
                except:
                    pass

                if full_info:
                    args[1]['full_user'] = res
                    args[1]['full_org'] = org

                args[1]['uid'] = res.get('id')
                args[1]['user'] = cut_user
                args[1]['org'] = cut_org

                return f(*args, **kwargs)

            raise UserException('verified failed-用户权限验证失败')

        return inner

    return wrapper


def add_uid(host=None, **extra):
    """
    用户token 返回用户id
    :param host:
    :extra: service 基础应用微服务名称
    :extra: func 获取用户uid方法名称
    :return: decorator
    """
    host = host if host else default_host
    base_service = extra.get('service', default_base_service)
    get_uid_func = extra.get('func', 'get_uid')

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            token = args[1].get('token')

            res = rpc_with_timeout(host, base_service, get_uid_func, {'token': token})

            try:
                if res.get('code'):
                    if res.get('code') < 0:
                        return res
            except:
                pass

            if res:
                args[1]['uid'] = res
                return f(*args, **kwargs)

            raise UserException('verified failed-用户token验证失败')

        return inner

    return wrapper


def add_user(host=None, **extra):
    """
    用户token 返回用户信息
    :param host:
    :extra: service 基础应用微服务名称
    :extra: func 获取用户信息方法名称
    :extra: full_info 是否携带用户和组织全部信息 默认false
    :return: decorator
    """

    host = host if host else default_host
    base_service = extra.get('service', default_base_service)
    get_user_func = extra.get('func', 'get_user')
    full_info = extra.get('full_info', False)

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            token = args[1].get('token')

            res = rpc_with_timeout(host, base_service, get_user_func, {'token': token})

            try:
                if res.get('code'):
                    if res.get('code') < 0:
                        return res
            except:
                pass

            if res:

                org = None
                try:
                    # 添加组织信息 add info of org
                    org = res.get('org').get(str(res.get('current_org')))
                except:
                    pass

                try:
                    # delete user passoword
                    del res['password_hash']
                    del res['partner']
                except:
                    pass

                cut_user = dict()
                cut_org = dict()

                cut_user['id'] = res['id']
                cut_user['account'] = res['account']
                cut_user['username'] = res['username']
                cut_user['current_org'] = res.get('current_org')
                cut_user['phone'] = res.get('phone')
                cut_user['email'] = res.get('email')

                try:
                    if org:
                        cut_org['id'] = org['id']
                        cut_org['name'] = org['name']
                        cut_org['desc'] = org['desc']
                        cut_org['owner'] = org['owner']
                        cut_org['region'] = org['region']
                        cut_org['es_extend'] = org['es_extend']
                except:
                    pass

                if full_info:
                    args[1]['full_user'] = res
                    args[1]['full_org'] = org

                args[1]['uid'] = res.get('id')
                args[1]['user'] = cut_user
                args[1]['org'] = cut_org

                return f(*args, **kwargs)

            raise UserException('verified failed-用户token验证失败')

        return inner

    return wrapper


def privilege(host=None, **extra):
    """

    :param host:
    :param extra:
    :extra: service 基础应用微服务名称
    :extra: func 验证超级用户
    :extra: level 权限级别：default = 10
    :return:
    """
    host = host if host else default_host
    base_service = extra.get('service', default_base_service)
    get_user_func = extra.get('func', 'get_user')
    level = extra.get('level', 10)

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            token = args[1].get('token')

            res = rpc_with_timeout(host, base_service, get_user_func, {'token': token})

            try:
                if res.get('code'):
                    if res.get('code') < 0:
                        return res
            except:
                pass

            if res:
                try:
                    del res['password_hash']
                    del res['partner']
                except:
                    pass

                #  验证用户特权级别
                p = res.get('privilege', None)
                if p:
                    if p.get('level', 0) >= level:
                        args[1]['user'] = res
                        return f(*args, **kwargs)

            raise UserException('verified failed-用户特殊权限验证失败，用户特殊权限，或权限级别不够。权限级别:' + str(level))

        return inner

    return wrapper


def agent(host=None, **extra):
    """
    用户token 返回用户信息
    :param host:
    :extra: service 基础应用微服务名称
    :extra: func 获取用户信息方法名称
    :return: decorator
    """

    host = host if host else default_host
    base_service = extra.get('service', default_base_service)
    get_user_func = extra.get('func', 'get_agent')

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            token = args[1].get('token')

            res = rpc_with_timeout(host, base_service, get_user_func, {'token': token})

            try:
                if res.get('code'):
                    if res.get('code') < 0:
                        return res
            except:
                pass

            if res:

                org = None
                try:
                    # 添加组织信息 add info of org
                    org = res.get('org').get(str(res.get('current_org')))
                except:
                    pass

                try:
                    # delete user passoword
                    del res['password_hash']
                    del res['partner']
                except:
                    pass

                cut_user = dict()
                cut_org = dict()

                cut_user['id'] = res['id']
                cut_user['account'] = res['account']
                cut_user['username'] = res['username']
                cut_user['current_org'] = res.get('current_org')
                cut_user['phone'] = res.get('phone')
                cut_user['email'] = res.get('email')

                try:
                    if org:
                        cut_org['id'] = org['id']
                        cut_org['name'] = org['name']
                        cut_org['desc'] = org['desc']
                        cut_org['owner'] = org['owner']
                        cut_org['region'] = org['region']
                        cut_org['es_extend'] = org['es_extend']
                except:
                    pass

                tmp_permit = dict()

                tmp_permit['privilege'] = res.get('privilege')
                tmp_permit['org'] = res.get('agent_org')
                tmp_permit['region'] = res.get('agent_region')
                tmp_permit['agent'] = res.get('agent_sub')

                args[1]['uid'] = res.get('id')
                args[1]['user'] = cut_user
                args[1]['org'] = cut_org
                args[1]['permit'] = tmp_permit

                return f(*args, **kwargs)

            raise UserException('verified failed-用户token验证失败')

        return inner

    return wrapper


def config_server(host=default_host, service='configServerFunc', func='import_config', timeout=10):
    """
    从配置微服务获取配置
    :param host:
    :param service:
    :param func:
    :param timeout:
    :return:
    """
    try:
        with ServiceRpcProxy(service, host, timeout=timeout) as proxy:
            res = methodcaller(func)(proxy)
            print(res)
            return res
    except RpcTimeout as e:
        return {'code': -30, 'desc': '配置中心微服务连接超时，或未启动, 时长:%s' % e, 'data': None}


class MsFuncFactory:
    """
    微服务方法工厂class
    统一管理rabbit mq host
    """

    def __init__(self, host):
        self.host = host

    def rpc_wrapper(self, service, func, *args, **kwargs):
        """
        rpc包装器
        :param service:
        :param func:
        :param args:
        :param kwargs:
        :return: result of process of rpc
        """
        return rpc_wrapper(service, func, *args, self.host, **kwargs)

    def ms_base(self):
        """
        应用微服务基础类，父类
        :return: class
        """
        return ms_base(self.host)

    def permit(self, **extra):
        """
        权限验证
        :param extra:
        :return: decorator
        """
        return permit(self.host, **extra)

    def add_user(self, **extra):
        """
        user
        :param extra:
        :return: decorator
        """
        return add_user(self.host, **extra)

    def add_uid(self, **extra):
        """
        user id
        :param extra:
        :return: decorator
        """
        return add_uid(self.host, **extra)

    def privilege(self, **extra):
        """
        平台管理员权限验证装饰器
        :param extra:
        :return: decorator
        """
        return privilege(self.host, **extra)

    def config_server(self):
        """
        从配置中心获取配置
        :return: result type of dict
        """
        return config_server(self.host)
