#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: QQHong

"""
一些较为零散的常用函数组成的工具模块
"""

import os
import bson
import urllib
import socket
import hashlib
import subprocess
from wsgiref.simple_server import make_server

import pymongo


def get_http_request_headers(headers=None):
    """
    获取HTTP的请求头
    :param headers: 指定的headers字段
    :return:
    """
    default_headers = {
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Referer": "https://www.baidu.com/",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }
    if headers is None:
        return default_headers
    return default_headers.update(headers)


def get_paths(path, recursive=False):
    """
    获取文件夹下的所有文件的路径
    :param path: 文件夹的路径
    :param recursive: 是否递归该文件夹
    :return: 所有文件路径组成的列表
    """
    paths = []
    if os.path.isdir(path):
        for root, dirs, filenames in os.walk(path):
            if recursive or (not recursive and root == path):
                paths.extend(map(lambda filename: os.path.join(root, filename), filenames))
    else:
        paths.append(path)
    return paths


def get_hash(path, hash_algorithms=None):
    """
    计算文件的hash值
    :param path: 文件路径
    :param hash_algorithms: 需要的哈希算法所组成的列表，例如：["md5"]
    :return: hash 字段及值组成的字典
    """
    if hash_algorithms is None:
        hash_algorithms = ["md5", "sha1", "sha256"]
    hash_values = {}
    content = open(path, "rb").read()
    for hash_algorithm in hash_algorithms:
        hash_values[hash_algorithm] = getattr(hashlib, hash_algorithm)(content).hexdigest()
    return hash_values


def file_split(path, size=1024*1024*1024):
    """
    对文件(通常为大文件)进行分割
    :param path: 文件路径
    :param size: 分割后每一份文件的大小，单位为byte
    :return:
    """
    with open(path, "rb") as src:
        index = 0
        content = src.read(size)
        while content != b"":
            open(path + "." + str(index), "wb").write(content)
            index += 1
            content = src.read(size)


def file_merge(path):
    """
    对文件进行合并
    :param path: 文件路径
    :return:
    """
    with open(path, "wb") as f:
        index = 0
        src = path + "." + str(index)
        while os.path.exists(src):
            content = open(path + "." + str(index), "rb").read()
            f.write(content)
            index += 1
            src = path + "." + str(index)


def duplicate_removal(old_list, sort=False):
    """
    对列表去重
    :param old_list: 原有列表
    :param sort: 是否保持原有排序
    :return: 去重后的新列表
    """
    new_list = list(set(old_list))
    if sort:
        new_list.sort(key=old_list.index)
    return new_list


def duplicate_removal_file(old_file_path, new_file_path, sort=False):
    """
    对文件内容按行进行去重
    :param old_file_path: 需去重的文件路径
    :param new_file_path: 去重后文件的保存路径
    :param sort: 是否需要保持原有排序，默认不保存
    :return:
    """
    lines = [line for line in open(old_file_path, encoding="utf-8").readlines()]
    lines = duplicate_removal(lines, sort)
    open(new_file_path, "w", encoding="utf-8").write("".join(lines))


def http_sever_by_wsgi(port=80, root_dir="."):
    """
    WSGI构建的简要的文件下载服务器(不考虑性能|安全等问题，仅供自身使用，切勿对外提供服务)
    :param port: 端口
    :param root_dir: 根目录
    :return:
    """
    # 列目录时展示的文件夹、文件的图标及默认返回的响应体(定义编码方式)
    folder_img = "data:image/gif;base64,R0lGODlhEAAQALMAAJF7Cf8A//zOLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAEALAAAAAAQABAAAAQqMMhJqwQ42wmE/8AWdB+YaWSZqmdWsm9syjJGx/YN6zPv5T4gr0UkikQRADs="
    file_img = "data:image/gif;base64,R0lGODlhEAAQALMAAAAAAIAAAACAAICAAAAAgIAAgACAgMDAwICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAA0ALAAAAAAQABAAAAQwsDVEq5V4vs03zVrHIQ+SkaJXYWg6sm5nSm08h3EJ5zrN9zjbLneruYo/JK9oaa4iADs="
    default_body = '<meta charset="UTF-8">'
    # 每次请求所调用的函数

    def application(environ, start_response):
        # Wsgi会对值进行latin1解码，导致中文异常，故此先用latin1编码再用utf-8进行解密
        requests_path = environ['PATH_INFO'].encode("latin1").decode("utf-8")
        local_path = os.path.join(root_dir + requests_path)
        print("Host:{}".format(environ["HTTP_HOST"]))
        if os.path.exists(local_path):
            # 文件直接提供下载
            if os.path.isfile(local_path):
                body = open(local_path, "rb").read()
                start_response('200 OK', [('Content-Type', 'application/octet-stream'), ('Content-Length', str(len(body)))])
            # 文件夹则列出目录
            elif os.path.isdir(local_path):
                start_response('200 OK', [('Content-Type', 'text/html')])
                body = default_body + '<style>a {text-decoration: none}</style>'
                dirs, files, show = '', '', '<img src="{}"> <a href="{}">{}<a><br/>'
                for each in os.listdir(local_path):
                    one = os.path.join(local_path, each)
                    if os.path.isdir(one):
                        dirs += show.format(folder_img, os.path.join(requests_path, each), each)
                    else:
                        files += show.format(file_img, os.path.join(requests_path, each), each)
                body += dirs + files
            else:
                start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
                body = default_body + "未知错误"
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            body = default_body + "页面不存在"
        if type(body) != bytes:
            body = body.encode("utf-8")
        return [body]
    # 启动WSGI文件服务器
    httpd = make_server('0.0.0.0', port, application)
    httpd.serve_forever()


def request_by_socket(url):
    """
    socket构造的HTTP 协议的GET请求，可在某些特殊场景下使用
    :param url: 需请求的URL
    :return: 响应头, 响应体
    """
    url = urllib.parse.urlparse(url)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 80 if url.port is None else url.port
    send_content = "GET " + url.path + "HTTP/1.1\r\nConnection: close\r\n\r\n"
    send_content = send_content.encode()
    client.connect((url.hostname, port))
    client.send(send_content)
    recv_data = b""
    while True:
        content = client.recv(1024)
        if not content:
            break
        recv_data += content
    response_header, response_body = recv_data.split('\r\n\r\n', 1)
    return response_header, response_body


def export_mongodb_data_to_json_file(host, port, database_name, collection_name, filter_condition={}, save_mode="all", save_dir="./"):
    """
    导出mongodb的数据到json文件中
    :param host: 网络地址
    :param port: 端口
    :param database_name: 数据库名
    :param collection_name: 集合名
    :param filter_condition: 数据过滤条件
    :param save_mode: 数据保存方式，all/one，all将所有数据保存至一个json文件，one将每一份数据单独保存至一个json文件
    :param save_dir: json文件保存的路径，文件名函数自生成
    :return:
    """
    client = pymongo.MongoClient(host, port)
    collection = client[database_name][collection_name].with_options(codec_options = bson.CodecOptions(unicode_decode_error_handler="ignore"))
    documents = collection.find(filter_condition)
    if save_mode == "all":
        data = [document for document in documents]
        save_path = os.path.join(save_dir, collection_name + ".json")
        open(save_path, "w", encoding="utf-8").write(bson.json_util.dumps(data, indent=4, ensure_ascii=False))
    elif save_mode == "one":
        for document in documents:
            save_path = os.path.join(save_dir, str(document["_id"]) + ".json")
            try:
                open(save_path, "w", encoding="utf-8").write(bson.json_util.dumps(document, indent=4, ensure_ascii=False))
            except Exception as e:
                print(document["_id"])


def multiple_decompress(path):
    """
    对文件夹（含子文件夹）下的所有压缩文件或某个单独的压缩文件进行递归形式的解压缩，实现对多重压缩包的解压
    :param path: 文件夹或文件路径
    :return:
    """
    if os.path.isdir(path):
        compressed_files = get_paths(path, recursive=True)
    else:
        compressed_files = [path]
    for compressed_file in compressed_files:
        target_dir = os.path.splitext(compressed_file)[0]
        command = "7z x -r -aos {} -o{}".format(compressed_file, target_dir)
        pi = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        for i in iter(pi.stdout.readline, b""):
            print(i.decode("GBK"), end="")
        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            multiple_decompress(target_dir)
