# -*- coding: utf-8 -*-
# @Time     : 2019/10/7 12:37
# @Author   : Run 
# @File     : __init__.py.py
# @Software : PyCharm

import os, shutil


def makedirs(file_path: str) -> None:
    if os.path.exists(file_path):
        print("{} already exists".format(file_path))
    else:
        os.makedirs(file_path)
        print("{} established".format(file_path))


def delete_path(file_path: str) -> None:
    """
    Force delete file or dir(contains all subdirs and files).
    Ignore file's attributes like 'read-only'.
    """
    if os.path.exists(file_path):
        if os.path.isfile(file_path):  # file
            os.chmod(file_path, stat.S_IWRITE)
            os.remove(file_path)
        else:  # dir
            for path, sub_folders, sub_files in os.walk(file_path):
                for file in sub_files:
                    os.chmod(os.path.join(path, file), stat.S_IWRITE)
                    os.remove(os.path.join(path, file))
            shutil.rmtree(file_path)
        print("{} deleted".format(file_path))
    else:
        print("{} doesn't exist".format(file_path))