# -*- coding: utf-8 -*-

import typing
from importlib import import_module
from picage import Package


def walk_lbd_handler(module_name, valid_func_name_list):
    """
    :type module_name: str
    :param module_name:

    :type valid_func_name_list: typing.List[str]
    :param valid_func_name_list: list of valid function name works as
        lambda handler

    **中文文档**

    遍历一个模块, 以及它所有的子包和子模块, 以及里面用于 lambda_handler 的函数.
    """
    pkg = Package(module_name)
    for (
            current_module,
            parent_module,
            sub_packages,
            sub_modules,
    ) in pkg.walk(pkg_only=False):
        py_current_module = import_module(current_module.fullname)
        if parent_module is None:
            py_parent_module = None
        else:
            py_parent_module = import_module(parent_module.fullname)

        yield py_current_module, py_parent_module, None

        for func_name in valid_func_name_list:
            if func_name in py_current_module.__dict__:
                py_handler_func = getattr(py_current_module, func_name)
                yield py_current_module, py_parent_module, py_handler_func
