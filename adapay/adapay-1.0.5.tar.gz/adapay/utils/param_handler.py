"""
2019.8.1 create by jun.hu
参数处理
"""
import json


def pop_empty_value(params_dict):
    """
    去掉参数中value为空的字段
    :return: 去除空参数后的参数字典
    """
    temp_dict = dict()
    temp_dict.update(params_dict)
    for (key, value) in params_dict.items():
        if value is None or value == '' or value == {} or value == []:
            temp_dict.pop(key)
    return temp_dict


def get_plain_text(all_params):
    temp_list = list()
    for (k, v) in sorted(all_params.items()):
        if not isinstance(v, str):
            v = json.dumps(v, ensure_ascii=False)
        if not v:
            continue
        temp_list.append('{}={}'.format(str(k), str(v)))
    plain_text = '&'.join(temp_list)
    return plain_text


def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()
