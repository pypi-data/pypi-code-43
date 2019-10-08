# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/4 15:18
"""
from .client.action import DataClient

client = DataClient()

school_id = 'aa0b1e0fdf1f4479bb3476a79f388f60'
sn = '210202A2HGZ18CB00197'


def get_device_info_test():
    code, data = client.get_class_device_info(school_id=school_id, sn=sn)
    print("Code: {}, Data: {}".format(code, data))


def get_school_info_test():
    code, data = client.get_school_info(school_id=school_id)
    print("Code: {}, Data: {}".format(code, data))


def create_section_test():
    data = {
        "name": "mayw测试一班",
        "num": 11901,
        "export": 2019,
        "education": "NA",
        "entrance": 2019,
        "category": 0,
        "teacher_num": "mayw01",
        "school": "0721554b97e84dff8ce378851b6158a0",
        "slogan": "勇往直前",
        "grade": "高一",
        "declaration": "",
        "description": ""
    }
    code, data = client.create_section(data=data)
    print("Code: {}, Data: {}".format(code, data))


def create_classroom_test():
    data = {
        "name": "mayw测试教室1",
        "mode": "1",
        "section_name": "mayw测试一班",
        "num": "M0001",
        "seats": 45,
        "category": "1",
        "device_sn": "210202A2HGZ18CB00036",
        "building": "求知楼",
        "school": "0721554b97e84dff8ce378851b6158a0",
        "extra_info": {},
        "floor": "1"
    }
    code, data = client.create_classroom(data=data)
    print("Code: {}, Data: {}".format(code, data))


if __name__ == '__main__':
    pass
    # get_device_info_test()
    # get_school_info_test()
    # create_section_test()
    create_classroom_test()