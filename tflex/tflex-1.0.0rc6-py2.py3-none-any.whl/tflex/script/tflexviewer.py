# -*- coding: utf-8 -*-
"""Import a protobuf graph (.pb) into Tensorboard and get its address to open in Chrome

Example usage:
python import_pb.py -g ./freeze/frozen_graph.pb  -l ./tb_logs(optional) -f(optional)
argument --log_dir(-l) is optional, if no specific address is required, log dir will be on the same level as graph address
argument --depth(-d) is optional, it works only when -g is a dir, dir has depth of 1, when type3, search will go inside
till depth is 3, depth added 1 when go each level inside.


note:if use .tflex entension file, please use company-customized tensorflow package
"""

"""Oneline docstring"""

import os
import socket
import random
import argparse
import tensorflow as tf
import shutil

from tflex.utils import import_graph


def get_parser():
    parser = argparse.ArgumentParser(
        description='Visualization of deep learning models(.pb and .tflex file are supported).')
    parser.add_argument(
        '--graph', '-g',
        type=str,
        default='',
        required=True,
        help="Import protobuf graphDef file (.pb or .tflex file) or model dir(with pb or tflex files inside) to the tensorboard.")
    parser.add_argument(
        '--logdir', '-l',
        type=str,
        default=None,
        help="Log directory specified by user to save tensorboard logs.")
    parser.add_argument(
        '--depth', '-d',
        type=int,
        default=3,
        help="Recursion depth for model dir.")
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=6006,
        help="Port to serve TensorBoard on, default port is 6006."
    )

    return parser


def main():
    parser = get_parser()
    flags = parser.parse_args()
    ip = get_host_addr()
    if os.path.isdir(flags.graph):
        log_dir_path = is_default_log_path(flags.graph, flags.logdir, 0)
        clear_dir(log_dir_path)
        file_abs_path = os.path.abspath(flags.graph)
        do_dir_things(file_abs_path, flags.depth, log_dir_path)
    else:
        log_dir_path = is_default_log_path(flags.graph, flags.logdir, 1)
        create_file(flags.graph, log_dir_path)
    view_file_by_tensorboard(log_dir_path, ip, flags.port)


def clear_dir(dir_path):
    shutil.rmtree(dir_path)


def do_dir_things(file_path, depth, logDir):
    """ if given file path is Dir that containing many model dirs,
    search pb and tflex file inside the Dir,
    """
    if depth >= 0:
        new_depth = depth - 1
        if os.path.isfile(file_path):
            if file_path.endswith('.pb') or file_path.endswith('.tflex'):
                temp = file_path.replace('\\', '/')  # if in windows platform
                file_name = temp.split('/')[-1]
                os.makedirs(os.path.join(logDir, file_name))
                create_file(file_path, os.path.join(logDir, file_name))
            else:
                return
        else:
            for file in os.listdir(file_path):
                new_file_path = os.path.join(file_path, file)
                do_dir_things(new_file_path, new_depth, logDir)


def get_host_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:  # If there is no internet connected
        ip = 'localhost'
    return ip


def create_file(file_path, log_path):
    """Creating tensorboard log file."""
    if os.listdir(log_path):
        filesToRemove = [os.path.join(log_path, f) for f in os.listdir(log_path)]
        for f in filesToRemove:
            os.remove(f)
    graph, _, _ = import_graph(file_path)
    tf.summary.FileWriter(log_path, graph)


def is_default_log_path(file_path, log_path, flag):
    """if specific log path is entered, create log dir on there,
    else 1: if file_path is a pb or tflex file, create log dir on the same level of the graph file
         2： if file_path is a dir containing many model dirs, create log dir inside file_path"""
    if flag == 1:
        if log_path is None:
            parentPath = os.path.dirname(os.path.abspath(file_path))  # parent path of graph file
            log_dir_path = parentPath + "/logDir"
        else:
            log_dir_path = os.path.abspath(log_path)
    else:
        if log_path is None:
            dirPath = os.path.abspath(file_path)  # parent path of graph file
            log_dir_path = dirPath + "/logDir"
        else:
            log_dir_path = os.path.abspath(log_path)
    if not os.path.exists(log_dir_path):
        os.mkdir(log_dir_path)
    return log_dir_path


def view_file_by_tensorboard(log_path, ip_address, port):
    os.system(
        'tensorboard --logdir=' + log_path + " --host=" + ip_address + " --port=" + str(port))


if __name__ == '__main__':
    main()
