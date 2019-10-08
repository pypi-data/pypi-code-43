import os
import boto3
from tensorflow import gfile
from collections import defaultdict
# from pyspark import SparkFiles
import hdfs3
from functools import reduce
import smart_open
try:
    from dl_rank.file.file_api import s3FileObj, pathStr, s3File, hdfsFile
except:
    import file_api
    s3FileObj = file_api.s3FileObj
    pathStr = file_api.pathStr
    s3File = file_api.s3File
    hdfsFile = file_api.hdfsFile
import boto3
from shutil import copytree

def typeDiagnosis(func):
    def wrapper(*args, **kwargs):
        args = list(args)
        func_arg_num = func.__code__.co_argcount
        ftype = [pathStr(p).attr for p in args[:func_arg_num]]
        args[:func_arg_num] = [pathStr(p).path for p in args[:func_arg_num]]
        File = wFile.filesys.get(ftype[0], gfile)
        filefunc = getattr(File, func.__name__)
        return filefunc(*args, **kwargs)
    return wrapper

class wFile(object):
    path_store = dict()
    filesys = {'s3': s3File, 'hdfs':hdfsFile}
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def set_hdfs_client(ip_port):
        hdfsFile.ip = ip_port
        ip, port = ip_port.split(':')
        hdfsFile.client = hdfs3.HDFileSystem(host=ip, port=port)

    @staticmethod
    @typeDiagnosis
    def Exists(filename):
        pass

    @staticmethod
    def Open(*args, **kwargs):
        return smart_open.open(*args, **kwargs)

    @staticmethod
    @typeDiagnosis
    def DeleteRecursively(dirname):
        pass

    @staticmethod
    @typeDiagnosis
    def IsDirectory(dirname):
        pass

    @staticmethod
    @typeDiagnosis
    def Walk(top):
        pass

    @staticmethod
    @typeDiagnosis
    def MakeDirs(dirname):
        pass

    @staticmethod
    @typeDiagnosis
    def Remove(filename):
        pass

    @staticmethod
    @typeDiagnosis
    def ListDirectory(dirname):
        pass

    @staticmethod
    @typeDiagnosis
    def Rename(oldname, newname):
        pass

    @staticmethod
    def Copy(srcPath, dstPath):
        file1, file2 = wFile.filesys.get(pathStr(srcPath).attr, gfile), wFile.filesys.get(pathStr(dstPath).attr, gfile)
        path1, path2 = pathStr(srcPath).path, pathStr(dstPath).path
        if file1.IsDirectory(path1):
            if path1[-1] != '/':
                path1 += '/'
            if path2[-1] != '/':
                path2 += '/'
        else:
            if path1[-1] == '/':
                path1 = path1[:-1]
            elif path2[-1] == '/':
                path2 = path2[:-1]

        if s3File in [file1, file2]:
            s3File.Copy(path1, path2)
        elif hdfsFile in [file1, file2]:
            hdfsFile.Copy(path1, path2)
        else:
            if file1.IsDirectory(path1):
                copytree(path1, path2)
            else:
                gfile.Copy(path1, path2)

if __name__ == '__main__':
    a = pathStr('/Users/snoworday/Downloads/part-00100-eb6b4732-3b25-4cd2-978b-7f4f1f5f18a5-c000.txt')
    f = wFile.Open(a, 'r')
    c = 1