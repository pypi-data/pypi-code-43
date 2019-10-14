# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/17 20:15
"""

TABLES = {
    "V_BZKS": {
        "remark": "学生信息表",
        "table_fields": ["XH", "XM", "MZDM", "XBDM", "SFZJH", "YXDM", "ZYMC", "XSLB", "ZJLB"],
    },
    "V_YP_BZKS": {
        "remark": "学生信息表",
        "table_fields": ["XH", "XM", "MZDM", "XBDM", "SFZJH", "YXDM", "ZYMC", "XSLB", "ZJLB", "BH"],
    },
    "V_YD_BJ": {
        "remark": "班级信息",
        "table_fields": ["BH", "NJ", "YXDM", "ZYDM", "BJMC"],
    },
    "V_YKT_NEW_KPJBXX": {
        "remark": "一卡通",
        "table_fields": ["XGH", "XM", "CARDID", "CARDNUM", "KZT", "XBDM", "DWDM", "DWMC", "USERLB"],
    },
    "V_BZKS_XSKB": {
        "remark": "学生课表",
        "table_fields": ["XN", "XM", "XQ", "XH", "KCDM", "KCMC", "SKBJ", "ZC", "XQJ", "DSZ", "JC", "SKDD",
                         "RKJSGH", "RKJSXM"],
    },
    "V_BZKS_JSKB": {
        "remark": "教师课表",
        "table_fields": ["XN", "XQ", "KCDM", "SKBJH", "SKBJ", "RKJSGH", "ZC", "XQJ", "DSZ", "JC", "SKDD",
                         "SKBJRS", "XF", "SKDDXQ", "XKKH"],
    },
    "V_BZKS_KCKXX": {
        "remark": "课程库信息",
        "table_fields": ["KCDM", "KCZWMC", "XF", "KCLB", "KHFS", "KKBMDM", "XLCC", "KCMCPY", "KKBMMC"],
    },
    "V_JZG": {
        "remark": "教职工表",
        "table_fields": ["ID", "ZGH", "XM", "XBDM", "MZDM", "CSRQ", "DWDM", "JG", "SFZJH"],
    }
}


def get_student_field():
    table_name = 'V_YP_BZKS'
    return table_name, TABLES[table_name]['table_fields']


def get_section_field():
    table_name = 'V_YD_BJ'
    return table_name, TABLES[table_name]['table_fields']


def get_card_field():
    table_name = 'V_YKT_NEW_KPJBXX'
    return table_name, TABLES[table_name]['table_fields']


def get_student_class_table_field():
    table_name = 'V_BZKS_XSKB'
    return table_name, TABLES[table_name]['table_fields']


def get_teacher_class_table_field():
    table_name = 'V_BZKS_JSKB'
    return table_name, TABLES[table_name]['table_fields']


def get_subject_field():
    table_name = 'V_BZKS_KCKXX'
    return table_name, TABLES[table_name]['table_fields']


def get_teacher_field():
    table_name = 'V_JZG'
    return table_name, TABLES[table_name]['table_fields']
