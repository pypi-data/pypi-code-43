# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/18 11:01
"""
import time
from datetime import datetime

from basedata.convertor import (subject_convert, section_convert, student_convert, teacher_convert)
from basedata.oracleclient import (query_subject_data, query_section_data, query_card_data,
                                   query_student_data, query_teacher_data)
from classcard_dataclient import DataClient
from config import SCHOOL_NAME
from utils.loggerutils import logging

logger = logging.getLogger(__name__)

client = DataClient()
client.set_config_module("config")


def get_school_id():
    code, school = client.get_school_by_name(SCHOOL_NAME)
    if code or not isinstance(school, dict):
        logger.error("Error: get school info, Detail: {}".format(school))
        school = {}
    return code, school.get("uuid")


def transact_subject_data():
    logger.info("start subject data sync at {}".format(datetime.now()))
    # 学校数据
    code, school_id = get_school_id()
    if code or not school_id:
        logger.error("Error: get school id fail, now break transact next data.")
        return

    # 课程科目数据
    # subject_data = query_subject_data(params={"NJ": ('>', 2015)})
    subject_data = query_subject_data()
    tmp_data = {}
    for d in subject_data:
        kcdm = d['KCDM']
        if not tmp_data.get(kcdm):
            tmp_data[kcdm] = d
    subject_data = tmp_data.values()
    # 课程科目数据
    for d in subject_data:
        subjects = subject_convert(data=d, school=school_id)
        code, data = client.create_subject(subjects)
        if code:
            logger.error("Code: {}, Msg: {}".format(code, data))
    logger.info("end subject data sync at {}".format(datetime.now()))


def transact_section_data():
    logger.info("start section data sync at {}".format(datetime.now()))
    # 学校数据
    code, school_id = get_school_id()
    if code or not school_id:
        logger.error("Error: get school id fail, now break transact next data.")
        return

    # 获取班级数据
    section_data = query_section_data(params={"NJ": ('>', 2010)})
    # 保存班级数据
    for d in section_data:
        section = section_convert(data=d, school=school_id)
        code, data = client.create_section(sections=section)
        if code:
            logger.error("Code: {}, Msg: {}".format(code, data))
    logger.info("end section data sync at {}".format(datetime.now()))


def transact_student_data():
    logger.info("start student data sync at {}".format(datetime.now()))
    # 1. 一卡通数据
    cards = query_card_data()
    card_dict = {c['XGH']: c for c in cards if c.get("XGH")}
    # 2. 学校数据
    code, school_id = get_school_id()
    if code or not school_id:
        logger.error("Error: get school id fail, now break transact next data.")
        return
    # 3. 班级数据
    code, sections = client.get_section_list(school_id=school_id)
    if code or not isinstance(sections, list):
        logger.error("Error: get section info, Detail: {}".format(sections))
        sections = []
    section_dict = {d["name"]: d['uuid'] for d in sections if d.get("name")}
    # 4. 学生数据
    student_data = query_student_data()
    for d in student_data:
        section_id = section_dict.get(d["BH"])
        ecard = card_dict.get(d["XH"])
        student = student_convert(data=d, ecard=ecard, school=school_id, section=section_id)
        code, data = client.create_student(students=student)
        if code:
            logger.error("Code: {}, Msg: {}".format(code, data))
    logger.info("end student data sync at {}".format(datetime.now()))


def transact_teacher_data():
    logger.info("start teacher data sync at {}".format(datetime.now()))
    # 1. 一卡通数据
    cards = query_card_data()
    card_dict = {c['XGH']: c for c in cards if c.get("XGH")}
    # 2. 学校数据
    code, school_id = get_school_id()
    if code or not school_id:
        logger.error("Error: get school id fail, now break transact next data.")
        return
    # 3. 教职工数据
    teacher_data = query_teacher_data()
    for d in teacher_data:
        ecard = card_dict.get(d["ZGH"])
        teacher = teacher_convert(data=d, ecard=ecard, school=school_id)
        code, data = client.create_teacher(teacher)
        if code:
            logger.error("Code: {}, Msg: {}".format(code, data))
    logger.info("end teacher data sync at {}".format(datetime.now()))


def start_data_sync():
    start_time = time.time()
    logger.info("start data sync at {}".format(datetime.now()))
    transact_section_data()
    transact_student_data()
    transact_teacher_data()
    # transact_subject_data()
    logger.info("end data sync at {}".format(datetime.now()))
    logger.info("data sync used: {}s".format(round(time.time() - start_time, 4)))


if __name__ == '__main__':
    pass
    # start_data_sync()
