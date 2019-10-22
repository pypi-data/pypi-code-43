# -*- coding: utf-8 -*-
from flask import make_response, request, jsonify
from common.constants import ERROR_MSG_MAP

# def set_allow_origin(data):
#     """
#     生成response，并设置响应头，使其允许跨域
#     :param data:html，json等response.body
#     :return:修改好的resopnse对象
#     """
#     response = make_response(data)
#     response.headers.update({'Access-Control-Allow-Origin': request.path})
#     return response


def sx_json(data='', code=200, msg=None):
    """
    生成昇星科技专属的json，可以直接将此作为return的对象
    :param data: 真实需要返回的数据
    :param code: 错误代码，默认是200
    :param msg: 可为None
    :return: jiso格式的字符串，通过jsonfy处理字典
    """
    return jsonify({
        "data": data,
        "code": code,
        "msg": ERROR_MSG_MAP.get(code, 'something wrong') if msg is None else msg
    })