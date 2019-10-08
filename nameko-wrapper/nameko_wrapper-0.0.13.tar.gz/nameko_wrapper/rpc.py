from nameko.rpc import rpc as nameko_rpc
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.exceptions import RpcTimeout

from nameko_wrapper.config import amqp_config
from nameko_wrapper.exceptions import ServiceErrorException, TimeoutException

from marshmallow.exceptions import ValidationError

from .response import RpcResponse
from .exceptions import ServiceException


def rpc(func):
    """
    Nameko Rpc Dispatch Result Wrapper

    作用： 添加自定义响应`RpcResponse`内容返回和自定义异常处理`ServiceException`

        为了有效的处理服务异常，服务所有异常应继承自ServiceException
    """

    @nameko_rpc
    def wrapper(*args, **kwargs):
        try:
            call_result = func(*args, **kwargs)
        except ServiceException as e:
            exception_info = e.msg if hasattr(e, 'msg') else None
            return RpcResponse(msg=exception_info, code=e.code).result
        except ValidationError as schema_error:
            # 捕捉表单验证异常
            return RpcResponse(data=schema_error.normalized_messages(), code=400).result
        # except Exception as E:
        #     print(E)
        #     print('Uncaught RPC response exception: {}.'.format(E))
        #     return RpcResponse(data={'info': 'Service error'}, code=500).result
        else:
            if hasattr(call_result, 'result'):
                return call_result.result
            else:
                raise UserWarning('RPC 调用结果须使用`RpcResponse`返回')

    return wrapper


def caller(service, method, *, is_async=False, timeout=12, **kwargs):
    """
    Nameko Service Call

    :param str service: service name
    :param str method: service method name
    :param args: method args
    :param bool is_async: is async call
    :param int timeout: timeout seconds
    :param kwargs: method kwargs
    :return: rpc call result
    """

    def wrapper(*args, **kwargs):
        with ClusterRpcProxy(amqp_config, timeout=timeout) as cluster_rpc:
            try:
                srv = getattr(cluster_rpc, service, None)
                call = getattr(srv, method, None)
                if srv and call:
                    if is_async:
                        result = call.call_async(*args, **kwargs)
                    else:
                        result = call(*args, **kwargs)
                else:
                    raise ServiceErrorException('service `{}` does not have `{}` method'.format(service, method))
            except RpcTimeout:
                # 当调用超时时，返回None
                raise TimeoutException
            except Exception as e:
                print('Call Exception:', e)
                raise e
            return result

    return wrapper
