# coding=utf-8
import os
import re
import sys
import zipfile
import shutil
import time
import subprocess
import tempfile
import getopt
import sys
import platform
import datetime


def get_timestr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def print_tag(tag, indent=0):
    print("\033[1;34m" + indent * 4 * " " + "[" + tag + "]\033[0m")


def print_log(log, indent=0):
    print("\033[1;32m" + indent * 4 * " " + "=>" + log + "\033[0m")


def print_err(log, indent=0):
    print("\033[1;31m" + indent * 4 * " " + "=>" + log + "\033[0m")


def print_warn(log, indent=0):
    print("\033[1;33m" + indent * 4 * " " + "=>" + log + "\033[0m")


def print_lines(lines, tag='', indent=0, num=0):
    maxnum = len(lines)
    if num > 0:
        minnum = maxnum - num
    else:
        minnum = 0
    if minnum < 0:
        minnum = 0
    for i in range(minnum, maxnum):
        print_log(tag + '=>' + lines[i], indent)


def copy_file(src_file, dest_file):
    if not os.path.exists(src_file):
        return
    if not check_file(src_file):
        return
    dest_dir = os.path.dirname(dest_file)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    open(dest_file, "wb").write(open(src_file, "rb").read())


def check_dir(path, *args):
    if not os.path.exists(path):
        return False
    default_filters = ['.DS_Store']
    now_filters = default_filters + list(args)
    for k in now_filters:
        if path.endswith(k) > 0:
            return False
    sub_files = os.listdir(path)
    if len(sub_files) == 0:
        return False
    if len(sub_files) == 1 and not check_file(sub_files[0], *args):
        return False
    return True


def check_file(path, *args):
    default_filters = ['.DS_Store', '.meta']
    now_filters = default_filters + list(args)
    for k in now_filters:
        if path.endswith(k):
            return False
    return True


def copy_dir(src_dir, dest_dir, *args):
    if not os.path.exists(src_dir):
        return
    if not check_dir(src_dir):
        return
    files = os.listdir(src_dir)
    for _file in files:
        src_file = os.path.join(src_dir, _file)
        dest_file = os.path.join(dest_dir, _file)
        if os.path.isdir(src_file):
            if check_dir(src_file):
                copy_dir(src_file, dest_file, *args)
        if os.path.isfile(src_file):
            copy_file(src_file, dest_file, *args)


def filter_dir(src_dir, *args):
    if not os.path.exists(src_dir):
        return
    if not check_dir(src_dir):
        return
    files = os.listdir(src_dir)
    for _file in files:
        src_file = os.path.join(src_dir, _file)
        if os.path.isdir(src_file):
            if check_dir(src_file):
                clean_dir(src_file, *args)
        if os.path.isfile(src_file):
            if not check_file(src_file):
                os.remove(src_file)
    clean_dir(src_dir, *args)


def clean_dir(src_dir, *args):
    if not os.path.exists(src_dir):
        return
    if not check_dir(src_dir):
        return
    files = os.listdir(src_dir)
    for _file in files:
        src_file = os.path.join(src_dir, _file)
        if os.path.isdir(src_file):
            if not check_dir(src_file, *args):
                shutil.rmtree(src_file)
            else:
                sub_files = os.listdir(src_file)
                if len(sub_files) == 0:
                    shutil.rmtree(src_file)
                else:
                    clean_dir(src_file, *args)


def join_path(*args):
    path = os.path.join(*args)
    path = path.replace("\\", "/")
    return path


def zip_dir(zipname, src_dir, *args):
    src_dir = join_path(src_dir)
    z = zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED, allowZip64=True)
    for root, dirs, files in os.walk(src_dir):
        for f in files:
            path = join_path(root, f)
            if check_file(path, *args):
                zpath = path.replace(src_dir, "")[1:]
                z.write(path, zpath)
    z.close()


def unzip_to_dir(zip_path, dest_dir, *args):
    z = zipfile.ZipFile(zip_path, 'r')
    for filename in z.namelist():
        if check_file(filename, *args):
            z.extract(filename, dest_dir)
    z.close()
