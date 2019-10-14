# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/18 9:36
"""
from basedata.constants import (get_student_field, get_section_field, get_card_field, get_student_class_table_field,
                                get_teacher_class_table_field, get_subject_field, get_teacher_field)
from basedata.oracleutils import query_data


def query_student_data(params=None):
    table_name, table_fields = get_student_field()
    data = query_data(table_name=table_name, fields=table_fields, params=params)
    return data


def query_section_data(params=None):
    table_name, table_fields = get_section_field()
    data = query_data(table_name=table_name, fields=table_fields, params=params)
    return data


def query_card_data(params=None):
    table_name, table_fields = get_card_field()
    data = query_data(table_name=table_name, fields=table_fields, params=params)
    return data


def query_student_class_table_data(params=None):
    table_name, table_fields = get_student_class_table_field()
    data = query_data(table_name=table_name, fields=table_fields, params=params)
    return data


def query_teacher_class_table_data(params=None):
    table_name, table_fields = get_teacher_class_table_field()
    data = query_data(table_name=table_name, fields=table_fields, params=params)
    return data


def query_subject_data(params=None):
    table_name, table_fields = get_subject_field()
    data = query_data(table_name=table_name, fields=table_fields, params=params)
    return data


def query_teacher_data(params=None):
    table_name, table_fields = get_teacher_field()
    data = query_data(table_name=table_name, fields=table_fields, params=params)
    return data
