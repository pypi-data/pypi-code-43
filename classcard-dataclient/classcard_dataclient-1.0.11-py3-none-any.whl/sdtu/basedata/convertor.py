# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/18 10:15
"""
from classcard_dataclient.models import Student, Class, Subject, Teacher
from utils.loggerutils import logging

logger = logging.getLogger(__name__)


def val_of(d, k):
    try:
        val = d[k]
    except:
        val = None
    return val


def section_convert(data, school):
    if not isinstance(data, dict):
        return None
    section = Class(**{
        "name": val_of(data, "BJMC"),
        "number": val_of(data, "BH"),
        "education": val_of(data, "YXDM"),
        "category": 0,
        "teacher": None,
        "school": school,
        "grade": val_of(data, "NJ"),
        "motto": "",
        "description": ""
    })
    return section


def subject_convert(data, school):
    if not isinstance(data, dict):
        return None
    subjects = Subject(**{
        "name": val_of(data, "KCZWMC"),
        "number": val_of(data, "KCDM"),
        "school": school,
    })
    return subjects


def student_convert(data, ecard, school, section=None):
    if not isinstance(data, dict):
        return None
    gender = val_of(data, "XBDM")
    gender = "M" if gender in ['男', '1', 1] else ("F" if gender in ['女', '2', 2] else "U")
    student = Student(**{
        "name": val_of(data, "XM"),
        "number": val_of(data, "XH"),
        "password": val_of(data, "XH"),
        "gender": gender,
        "birthday": None,
        "email": None,
        "phone": None,
        "avatar": None,
        "ecard": val_of(ecard, "CARDID") if ecard else None,
        "specific": None,
        "description": None,
        "classof": None,
        "graduateat": None,
        "section": section,
        "school": school,
    })
    return student


def teacher_convert(data, ecard, school):
    if not isinstance(data, dict):
        return None
    gender = val_of(data, "XBDM")
    gender = "M" if gender in ['男', '1', 1] else ("F" if gender in ['女', '2', 2] else "U")
    teacher = Teacher(**{
        "name": val_of(data, "XM"),
        "number": val_of(data, "ZGH"),
        "password": val_of(data, "ZGH"),
        "gender": gender,
        "birthday": val_of(data, "CSRQ"),
        "email": None,
        "phone": None,
        "avatar": None,
        "ecard": val_of(ecard, "CARDID") if ecard else None,
        "specific": None,
        "description": None,
        "school": school,
    })
    return teacher
