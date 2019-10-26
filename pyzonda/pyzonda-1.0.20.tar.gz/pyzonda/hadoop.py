#!/usr/bin/python3

from __future__ import print_function
import subprocess
import io
import re


class HDFS:
    def __init__(self):
        """
        Constructor
        """
    @staticmethod
    def get(remote_path, local_path):
        """
        Get file from HDFS to local directory
        :param remote_path: hadoop fs path
        :type remote_path: str
        :param local_path: local path of the file to be downloaded
        :type local_path: str
        :return: status of transaction
        """
        sts = 0
        return sts

    @staticmethod
    def put(local_path, remote_path, keep_local=True):
        """
        Get file from HDFS to local directory
        :param local_path: local path of the file
        :type local_path: str
        :param remote_path: hadoop fs path of the file to be uploaded
        :type remote_path: str
        :param keep_local: indicates if the local file should be removed after transaction
        :return: status of transaction
        """
        sts = 0
        return sts

    @staticmethod
    def ls(path):
        output = []
        cmd = 'hdfs dfs -ls -R {}'.format(path).split()

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):
            output.append(line.strip())

        p.wait()
        if p.returncode != 0:
            output = []
            pass

        if output:
            output = [{'permissions': y[0], 'size_in_bytes': y[4], 'user': y[2], 'group': y[3], 'last_modification_date': y[5], 'last_modification_hour': y[6], 'path': y[7]} for y in [re.split('\s+', x) for x in output] if y[0][0] != 'd']

        return output

    @staticmethod
    def exists(path):
        """
        Check if the path exists in HDFS
        :param path: hdfs path to check
        :type path: str
        :return: true if the file exists else false
        """
        return True if HDFS.ls(path) else False

    def rm(self):
        raise NotImplemented

    def mv(self):
        raise NotImplemented

    def count(self):
        raise NotImplemented

    def mkdir(self):
        raise NotImplemented

    def __repr__(self):
        """
        String representation
        :return: object string representation
        """
        return str(self)
