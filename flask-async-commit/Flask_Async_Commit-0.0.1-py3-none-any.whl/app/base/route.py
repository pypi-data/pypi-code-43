# ! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~

    A brief description goes here.

    :copyright: (c) Jimmy@2018年03月16日.
"""

from flask import Blueprint, g, request
import random
from app.base.models import ZoneStructMap, DeviceZoneMap
from common.response_helper import sx_json
from common.constants import ZONE_STRUCT


base = Blueprint('base', __name__)


def callable_zone_id():
    line = list(range(8, 19))
    for i in range(100):
        yield line[i % len(line)]


@base.route('/')
def test():
    zone_id = callable_zone_id()
    for i in range(50):
        device_mac = random.randint(1000000, 9999999)
        m = DeviceZoneMap(device_mac=device_mac, zone_id=zone_id.next(),
                          position_y=50, position_x=50, radius=60)
        m.quick_save()
    return 'success'
    # return jsonify(DeviceZoneMap.hyper_device_of_upper_zone('1'))

@base.route('/device_info', methods=['GET'])
def GET_device_info():
    """

    :return:
    """
    zone_id_list = request.args.get('zone_id', None)
    alive_list = request.args.get('alive', None)
    device_list = DeviceZoneMap.hyper_device_of_zone(zone_id_list=zone_id_list, alive_list=alive_list)
    result = []
    flag = True     # true表明
    for i in device_list:
        for j in result:
            if i['zone_id'] == j['zone_id']:    # 如果已经有某个字典的zone_id键的值等于i的zone_id
                j['device_list'].append(i)      # 就append进入字典的device_list字段
                flag = False    # 执行了这一句，下面的if flag之后就不执行了
                break
        if flag:                                # 否则新建一个字典
            result.append(dict(zone_id=i['zone_id'], device_list=[i]))
    return sx_json(result)

@base.route('/zone_info', methods=['GET'])
def GET_zone_info():
    zone_id_list = request.args.get('zone_id', None)
    alive_list = request.args.get('deepth', None)
    device_list = DeviceZoneMap.hyper_device_of_zone(zone_id_list=zone_id_list, alive_list=alive_list)
    result = []
    flag = True     # true表明
    for i in device_list:
        for j in result:
            if i['zone_id'] == j['zone_id']:    # 如果已经有某个字典的zone_id键的值等于i的zone_id
                j['device_list'].append(i)
                flag = False    # 执行了这一句，下面的if flag之后就不执行了
                break
        if flag:
            result.append(dict(zone_id=i['zone_id'], device_list=[i]))
    return sx_json(result)
