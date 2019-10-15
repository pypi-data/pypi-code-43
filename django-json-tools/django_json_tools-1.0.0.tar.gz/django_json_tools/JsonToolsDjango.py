import json

from django.db import models
from django.http import HttpResponse

"""
   适配 django 的 http 返回  json 数据
    
    get_json_models(ser, data, code, msg)
        栗子:
        class get_user_info(APIView):
            user = User.object.get(pk=1)
            return get_json_models(UserSerializer, user, 1, '查询用户信息成功')
    
        {'code':1, msg: '查询用户信息成功', data: {'id':1, 'username': 'ingrun'} }
         
"""


def get_json_success(msg=None):
    if msg is None:
        msg = '成功'
    dick = {'code': 1, 'msg': msg, 'data': ''}
    return json.dumps(dick, ensure_ascii=False)


def http_response_json_success(msg=None):
    return HttpResponse(get_json_success(msg))


def get_json_error(msg=None):
    if msg is None:
        msg = '错误'
    dick = {'code': 0, 'msg': msg, 'data': ''}
    return json.dumps(dick, ensure_ascii=False)


def http_response_json_error(msg=None):
    return HttpResponse(get_json_error(msg))


def get_json_models(ser,  data, code=None, msg=None):
    """
    将一条模型数据完整返回
    :param ser:   这是模型序列化器
    :param data:  模型数据  可一个 models 或者是一个 queryset
    :param code:
    :param msg:
    :return:
    """
    code = __get_code(data, code)
    msg = __get_msg(code, msg)
    ser2 = ser(data, many=(not isinstance(data, models.Model)))
    dick = {'code': code, 'msg': msg, 'data': ser2.data}
    return HttpResponse(json.dumps(dick, ensure_ascii=False))


def http_response_json_models(ser,  data, code=None, msg=None):
    return HttpResponse(get_json_models(ser, data, code, msg))


def __get_code(data, code=None):
    if code:
        return code
    else:
        if data:
            code = 1
        else:
            code = 0
        return code


def __get_msg(code=None, msg=None):
    if msg:
        return msg
    else:
        if code:
            msg = "操作成功！"
        else:
            msg = "操作失败！"
        return msg
