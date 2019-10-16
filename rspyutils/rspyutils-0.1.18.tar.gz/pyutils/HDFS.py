# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import pyhdfs
import re, os
from pyutils import dates


# 关于python操作hdfs的API可以查看官网:
# https://hdfscli.readthedocs.io/en/latest/api.html
class HDFSCli(object):
    def __init__(self, host, user="root"):
        self.fs = pyhdfs.HdfsClient(hosts=host,
                                    user_name=user)

    # 创建目录
    def mkdirs(self, hdfs_path):
        self.fs.mkdirs(hdfs_path)

    # 删除hdfs文件
    def delete_hdfs_file(self, hdfs_path):
        self.fs.delete(hdfs_path)

    # 判断文档存在
    def is_exist_file(self, hdfs_path) -> bool:
        return self.fs.exists(hdfs_path)

    # 移动或者修改文件
    def move_or_rename(self, hdfs_src_path, hdfs_dst_path) -> bool:
        return self.fs.rename(hdfs_src_path, hdfs_dst_path)

    # 从hdfs获取文件到本地
    def get_from_hdfs(self, local_path, hdfs_path):
        self.fs.copy_to_local(hdfs_path, local_path)

    # 上传文件到hdfs
    def put_to_hdfs(self, local_path, hdfs_path):
        self.fs.copy_from_local(local_path, hdfs_path)

    # 追加数据到hdfs文件
    def append_to_hdfs(self, hdfs_path, data):
        self.fs.append(hdfs_path, data, overwrite=False, append=True)

    # 覆盖数据写到hdfs文件
    def write_to_hdfs(self, local_file, hdfs_path):
        if self.is_exist_file(hdfs_path):
            self.delete_hdfs_file(hdfs_path)
            self.put_to_hdfs(local_file, hdfs_path)
        else:
            self.put_to_hdfs(local_file, hdfs_path)

    # 返回目录下的文件
    def list(self, hdfs_path):
        return self.fs.listdir(hdfs_path)

    def rm_file_by_date(self, hdfs_path, date_len=30):
        thr_date = dates.get_before_date(date_len).strftime("%Y-%m-%d")
        for x in self.list(hdfs_path):
            file_date = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", x)
            if file_date and dates.get_date_compare(thr_date, file_date[0]):
                self.delete_hdfs_file(os.path.join(hdfs_path, x))

    def rm_file_all(self, hdfs_path):
        for x in self.list(hdfs_path):
            self.delete_hdfs_file(os.path.join(hdfs_path, x))


if __name__ == '__main__':
    fs = HDFSCli(host="iZbp13z41dx386bju3wb1zZ:50070",
                 user="root")
    fs.rm_file_all("/recommend/samh/data/rank/ctr/")
    # fs.delete_hdfs_file("/recommend/samh/rank/")
    # print(fs.list('/recommend/samh/rank/data/'))
