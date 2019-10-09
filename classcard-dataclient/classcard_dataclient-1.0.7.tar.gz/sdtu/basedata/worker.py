# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/18 11:01
"""
import time
from datetime import datetime

from basedata.constants import SCHOOL_NAME
from basedata.convertor import (subject_convert, section_convert, student_convert, teacher_convert)
from basedata.oracleclient import (query_subject_data, query_section_data, query_card_data,
                                   query_student_class_table_data, query_student_data, query_teacher_data)
from classcard_dataclient import DataClient
from .loggerutils import logging

logger = logging.getLogger(__name__)

client = DataClient()
client.set_config_module("config")


def transact_subject_data():
    # 学校数据
    code, school = client.get_school_by_name(SCHOOL_NAME)
    if code:
        logger.error("Error: get school info, Detail: {}".format(school))
    school_id = school.get("uuid")

    # 获取课程科目数据
    subject_data = query_subject_data()

    # 保存课程科目数据
    for d in subject_data:
        subjects = subject_convert(data=d, school=school_id)
        code, data = client.create_subject(subjects)
        if not code:
            logger.error("Code: {}, Data: {}".format(code, data))
        else:
            logger.info("Code: {}, Data: {}".format(code, data))


def transact_section_data():
    # 学校数据
    code, school = client.get_school_by_name(SCHOOL_NAME)
    if code:
        logger.error("Error: get school info, Detail: {}".format(school))
    school_id = school.get("uuid")

    # 获取班级数据
    section_data = query_section_data()

    # 保存班级数据
    for d in section_data:
        section = section_convert(data=d, school=school_id)
        code, data = client.create_section(sections=section)
        if not code:
            logger.error("Code: {}, Data: {}".format(code, data))
        else:
            logger.info("Code: {}, Data: {}".format(code, data))


def transact_student_data():
    # 1. 获取一卡通数据
    cards = query_card_data()
    card_dict = {c['XGH']: c for c in cards if c.get("XGH")}
    # 2. 学校数据
    code, school = client.get_school_by_name(SCHOOL_NAME)
    if code:
        logger.error("Error: get school info, Detail: {}".format(school))
    school_id = school.get("uuid")
    # 3. 获取班级数据
    student_class_tables = query_student_class_table_data()
    student_section_dict = {d["SKBJ"]: d["XH"] for d in student_class_tables if d.get("SKBJ") and d.get("XH")}
    section_dict = {}
    if student_section_dict:
        code, sections = client.get_section_list(school_id=school_id)
        if code or not isinstance(sections, list):
            logger.error("Error: get section info, Detail: {}".format(sections))
            sections = []
        tmp_section_id_dict = {}
        if sections:
            tmp_section_id_dict = {d["number"]: d['uuid'] for d in sections if d.get("number")}
        for k, v in student_section_dict.items():
            section_id = tmp_section_id_dict.get(k)
            if section_id:
                section_dict[v] = school_id

    # 4. 获取学生数据
    student_data = query_student_data()
    for d in student_data:
        section_id = section_dict.get(d["XH"])
        ecard = card_dict.get(d["XH"])
        student = student_convert(data=d, ecard=ecard, school=school_id, section=section_id)
        code, data = client.create_student(students=student)
        if not code:
            logger.error("Code: {}, Data: {}".format(code, data))
        else:
            logger.info("Code: {}, Data: {}".format(code, data))


def transact_teacher_data():
    # 1. 获取一卡通数据
    cards = query_card_data()
    card_dict = {c['XGH']: c for c in cards if c.get("XGH")}
    # 2. 学校数据
    code, school = client.get_school_by_name(SCHOOL_NAME)
    if code:
        logger.error("Error: get school info, Detail: {}".format(school))
    school_id = school.get("uuid")
    # 3. 获取教职工数据
    teacher_data = query_teacher_data()
    for d in teacher_data:
        ecard = card_dict.get(d["ZGH"])
        teacher = teacher_convert(data=d, ecard=ecard, school=school_id)
        code, data = client.create_teacher(teacher)
        if not code:
            logger.error("Code: {}, Data: {}".format(code, data))
        else:
            logger.info("Code: {}, Data: {}".format(code, data))


def start_data_sync():
    start_time = time.time()
    logger.info("start data sync at {}".format(datetime.now()))
    transact_subject_data()
    transact_section_data()
    transact_student_data()
    transact_teacher_data()
    logger.info("end data sync at {}".format(datetime.now()))
    logger.info("data sync used: {}s".format(round(time.time() - start_time, 4)))


if __name__ == '__main__':
    pass
    # start_data_sync()
