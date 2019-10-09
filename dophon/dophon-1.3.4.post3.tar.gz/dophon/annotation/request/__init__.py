# coding: utf-8
import functools
import re
from flask import request, abort
from dophon import properties
from dophon_logger import *

from dophon.errors.ParamErrors import ReqParamError
from .param_adapter.handler import BaseHandler, CustomizeHandleProcessNotFoundError
from .param_adapter import *
import inspect
import json

logger = get_logger(eval(properties.log_types))

# Content-TYPE 2 adapter
PARAM_DICT = {
    None: is_none,
    'application/x-www-form-urlencoded': is_form,
    'multipart/form-data': is_form,
    'application/json': is_json,
    'text/xml': is_xml,
    'application/xml': is_xml,
    'text/plain': is_args
}

'''
参数体可以为多个,形参名称必须与请求参数名一一对应(只少不多)
装饰器中关键字参数列表可以指定参数名
'''

logger.inject_logger(globals())


# 处理请求参数装饰器(分离参数)


def auto_param(mix: bool = False, mix_param: str = 'p', content_handler: BaseHandler = None):
    def method(f):
        @functools.wraps(f)
        def args(*args, **kwargs):
            try:
                content_type = request.headers.get('Content-Type')
                if content_type:
                    if not content_handler:
                        handle_result = PARAM_DICT[content_type](request)
                        req_kwargs = eval(json.dumps(handle_result, ensure_ascii=False)) \
                            if isinstance(handle_result, dict) \
                            else handle_result
                    else:
                        try:
                            # 尝试自定义处理器处理请求
                            req_kwargs = content_handler.handle(content_type)(request)
                        except CustomizeHandleProcessNotFoundError as e:
                            # 尝试使用框架自定义处理器处理
                            handle_result = PARAM_DICT[content_type](request)
                            req_kwargs = eval(json.dumps(handle_result, ensure_ascii=False)) \
                                if isinstance(handle_result, dict) \
                                else handle_result
                else:
                    req_kwargs = request.args.to_dict()

                # 整合请求路径参数
                path_req_args = request.args.to_dict()
                for path_req_k in path_req_args:
                    if path_req_k not in req_kwargs:
                        req_kwargs[path_req_k] = path_req_args[path_req_k]

                assert isinstance(req_kwargs, dict), f'参数类型异常{type(req_kwargs)}'

                if mix:
                    kwarg_keys = inspect.signature(f).parameters.keys()
                    if mix_param in kwarg_keys:
                        mixed_kwargs = {
                            mix_param: req_kwargs
                        }
                        for k in kwarg_keys:
                            if k not in mixed_kwargs:
                                mixed_kwargs[k] = None
                        return f(**mixed_kwargs)
                    else:
                        raise ReqParamError(f'方法{f}缺少混合参数{mix_param}')
                else:
                    for k in inspect.signature(f).parameters.keys():
                        if k in req_kwargs:
                            kwargs[k] = req_kwargs[k]
                        else:
                            kwargs[k] = None
                    return f(**kwargs)
            except TypeError as t_e:
                logger.error('参数不匹配!!,msg:' + repr(t_e))
                raise t_e
                return abort(500)

        return args

    return method


'''
注意!!!
该注解只需方法体内存在一个形参!!!
同样,需要指定参数名的形式参数列表条目也只能存在一个,多个会默认取第一个
不匹配会打印异常
参数以json形式赋值
'''


# 处理请求参数装饰器(统一参数,参数体内参数指向json串)
def full_param(kwarg_list=[]):
    def method(f):
        @functools.wraps(f)
        def args(*args, **kwargs):
            try:
                if 'POST' == str(request.method):
                    r_arg = ()
                    r_kwarg = {}
                    if not kwarg_list:
                        r_arg = (request.json if request.is_json else request.form.to_dict(),)
                    else:
                        r_kwarg[kwarg_list[0]] = request.json if request.is_json else request.form.to_dict()
                    return f(*r_arg, **r_kwarg)
                elif 'GET' == str(request.method):
                    r_arg = ()
                    r_kwarg = {}
                    if not kwarg_list:
                        r_arg = (request.args.to_dict(),)
                    else:
                        r_kwarg[kwarg_list[0]] = request.args.to_dict()
                    return f(*r_arg, **r_kwarg)
                else:
                    logger.error('json统一参数不支持该请求方法!!')
                    return abort(400)
            except TypeError as t_e:
                logger.error('参数不匹配!!,msg:' + repr(t_e))
                return abort(500)

        return args

    return method


def file_param(alias_name: str = 'files', extra_param: str = 'args'):
    """
    文件参数装在装饰器

    ps 文件上传暂时只支持路由方法内单个参数接收(会有校验策略)

    参数demo(小程序):
        ImmutableMultiDict([('img_upload_test', <FileStorage: 'filename' ('image/jpeg')>)])
    :return:
    """

    def method(f):
        @functools.wraps(f)
        def args(*args, **kwargs):
            # 检测参数
            a_nums = len(args) + len(kwargs)
            if a_nums > 0:
                logger.error('路由绑定参数数量异常')
                raise Exception('路由绑定参数数量异常')
            try:
                extra_param_value = (request.form if request.form else request.json).to_dict()
            except:
                extra_param_value = {}
            k_args = {
                alias_name: request.files.to_dict(),
                extra_param: extra_param_value
            }
            return f(**k_args)

        return args

    return method


# 路径绑定装饰器
# 默认服务器从boot获取
def request_mapping(path='', methods=[], app=None):
    def method(f):
        try:
            # 自动获取蓝图实例并进行http协议绑定
            current_package = __import__(str(getattr(f, "__module__")), fromlist=True)
            try:
                package_app = getattr(current_package, '__app') \
                    if hasattr(current_package, '__app') \
                    else current_package.app \
                    if hasattr(current_package, 'app') \
                    else app \
                    if hasattr(app, 'routes') \
                    else __import__('dophon').blue_print(f"_annotation_auto_reg.{getattr(current_package, '__name__')}",
                                                         getattr(current_package, '__name__'))
            except Exception as e:
                logger.warn(f'{e}')
                package_app = __import__('dophon.boot', fromlist=True).app
            # 回设内部蓝图参数
            # print(package_app)
            setattr(current_package, '__app', package_app)
            result = package_app.route(path, methods=methods)(f)
        except Exception as e:
            logger.error(f'{getattr(f, "__module__")}参数配置缺失,请检查({path},{methods},{package_app})')

        def m_args(*args, **kwargs):
            if properties.debug_trace:
                logger.info(f'router endpoint:{getattr(f, "__module__")}.{f},router path:{path}')
            return result(*args, **kwargs)

        return m_args

    return method


# 请求方法缩写
def method_route(req_method: str, path: str = '', ):
    def method(f):
        result = request_mapping(path, [req_method])(f)

        def _args(*args, **kwargs):
            return result(*args, **kwargs)

        return _args

    return method


# get方法缩写
def get_route(path=''):
    def method(f):
        result = method_route('get', path)(f)

        def _args(*args, **kwargs):
            return result(*args, **kwargs)

        return _args

    return method


# post方法缩写
def post_route(path=''):
    def method(f):
        result = method_route('post', path)(f)

        def _args(*args, **kwargs):
            return result(*args, **kwargs)

        return _args

    return method


func_to_path = lambda f: f"""{"/" if re.match("^[a-zA-Z0-9]+", getattr(f, "__name__")) else ""}{re.sub("[^a-zA-Z0-9]",
                                                                                                       "/",
                                                                                                       getattr(f,
                                                                                                               "__name__"))}"""


# get方法缩写
def get(f, *args, **kwargs):
    path = func_to_path(f)
    result = get_route(re.sub('\s+', '', path))(f)

    @functools.wraps(f)
    def method():
        def _args():
            return result(*args, **kwargs)

        return _args

    return method


# post方法缩写
def post(f, *args, **kwargs):
    path = func_to_path(f)

    result = post_route(re.sub('\s+', '', path))(f)

    @functools.wraps(f)
    def method():
        def _args():
            return result(*args, **kwargs)

        return _args

    return method
