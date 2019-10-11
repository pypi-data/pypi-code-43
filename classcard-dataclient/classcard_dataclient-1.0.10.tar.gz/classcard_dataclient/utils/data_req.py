# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/4 17:18
"""
from __future__ import absolute_import, unicode_literals

from .core import config
from .loggerutils import logging
from .requestutils import (do_get_request, do_post_request)

logger = logging.getLogger(__name__)


def edtech_server_url():
    """class_card server url"""

    server_url = config.get("EDTECH_SERVER_URL")
    return server_url


def edtech_server_token():
    """class_card server token"""
    token = config.get("EDTECH_SERVER_TOKEN")
    return token


def class_card_server_url():
    """class_card server url"""
    server_url = config.get("CLASS_CARD_SERVER_URL")
    return server_url


def class_card_server_token():
    """class_card server token"""
    token = config.get("CLASS_CARD_SERVER_TOKEN")
    return token


def create_section_req(data, school_id):
    """create section of edtech user server"""
    url = "{}/api/v1/schools/{}/sections/".format(edtech_server_url(), school_id)
    resp = do_post_request(url=url, json=data, token=edtech_server_token())
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def create_teacher_req(data, school_id):
    """create teacher of edtech user server"""
    url = "{}/api/v1/schools/{}/teachers/".format(edtech_server_url(), school_id)
    resp = do_post_request(url=url, json=data, token=edtech_server_token())
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def create_student_req(data, school_id):
    """create student of edtech user server"""
    url = "{}/api/v1/schools/{}/students/".format(edtech_server_url(), school_id)
    resp = do_post_request(url=url, json=data, token=edtech_server_token())
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def get_school_by_id(school_id):
    """get school info by school_id"""
    url = "{}/api/v1/schools/{}/".format(edtech_server_url(), school_id)
    resp = do_get_request(url=url, token=edtech_server_token())
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def get_school_by_name(name):
    """get school info by school name"""
    url = "{}/api/v1/schools_mini/".format(edtech_server_url())
    resp = do_get_request(url=url, token=edtech_server_token(), params={"name": name})
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    if isinstance(data, list) and len(data) > 1:
        logger.warning("Warning: Too many school named {}, but get first school. Detail: {}".format(name, data))
    return code, data[0] if isinstance(data, list) else {}


def get_section_by_school(school_id):
    """get school info by school name"""
    url = "{}/api/v1/schools/{}/sections/simple/".format(edtech_server_url(), school_id)
    resp = do_get_request(url=url, token=edtech_server_token())
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))

    return code, data


def get_device_info(school_id, sn):
    """get class device info by school_id and sn"""
    url = "{}/api/volcano/class_device/{}/".format(class_card_server_url(), sn)
    resp = do_get_request(url=url, token=class_card_server_token(), school_in_header=school_id)
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


# def create_section_req(data, school_id):
#     """create section of class card server"""
#     url = "{}/api/class/".format(class_card_server_url())
#     resp = do_post_request(url=url, json=data, token=class_card_server_token(), school_in_header=school_id)
#     code = resp.code
#     data = resp.data.get('data', {}) if not code else resp.msg
#     if code:
#         logger.error("Error: Request: {}, Detail: {}".format(url, data))
#     return code, data


def create_classroom_req(data, school_id):
    """create classroom of class card server"""
    url = "{}/api/classroom/".format(class_card_server_url())
    resp = do_post_request(url=url, json=data, token=class_card_server_token(), school_in_header=school_id)
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data


def create_subject_req(data, school_id):
    """create subject of class card server"""
    url = "{}/api/subject/".format(class_card_server_url())
    resp = do_post_request(url=url, json=data, token=class_card_server_token(), school_in_header=school_id)
    code = resp.code
    data = resp.data.get('data', {}) if not code else resp.msg
    if code:
        logger.error("Error: Request: {}, Detail: {}".format(url, data))
    return code, data
