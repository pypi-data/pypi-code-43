"""
yml文件注册功能
"""
import os

import yaml

REGISTRY_PROPERTIES = dict()

def load_registry_properties(file,yaml_name:str):
    yaml = read_yaml_file(file, yaml_name)
    if yaml is None:
        return
    global REGISTRY_PROPERTIES
    REGISTRY_PROPERTIES = yaml["sobeyficus"]["registry"]

def read_yaml_file(file, yaml_name: str):
    """
    读取文件路径中的yaml文件
    :param yaml_name:
    :return:
    """
    # 获取当前文件路径
    filePath = os.path.dirname(file)

    # 这里采用一层一层的递归上去找是否有yaml_name的文件
    # 获取配置文件的路径
    yamlPath = _find_path(filePath, yaml_name)
    if yamlPath is None:
        # 如果文件不存在,忽略
        return None

    # 加上 ,encoding='utf-8'，处理配置文件中含中文出现乱码的情况。
    with open(yamlPath, 'r', encoding='utf-8') as f:
        cont = f.read()

    # 返回yaml文件对象
    return yaml.load(cont, Loader=yaml.FullLoader)


def _find_path(file_path, yaml_name):
    """
    递归查找文件
    :param file_path:
    :param yaml_name:
    :return:
    """
    # 这里window中取出来的路径也可能是 / 分割的，这里简单重写下
    r_path = os.path.join(file_path, yaml_name)
    if os.path.exists(r_path):
        return r_path
    else:
        folder_path = os.path.split(file_path)[0]
        if folder_path == file_path:
            return None
        else:
            return _find_path(folder_path, yaml_name)


def _get_separator():
    """
    判断是windows还是其他的,系统不一样 separtor不一样
    :return:
    """
    import platform
    if 'Windows' in platform.system():
        separator = '\\'
    else:
        separator = '/'
    return separator
