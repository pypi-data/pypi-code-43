import os
import boto3
from tensorflow import gfile
from collections import defaultdict
# from pyspark import SparkFiles
from functools import reduce
import smart_open
try:
    from dl_rank.file.file_api import s3FileObj, pathStr,hdfsFile,s3File
except:
    import file_api
    s3FileObj = file_api.s3FileObj
    pathStr = file_api.pathStr
    hdfsFile = file_api.hdfsFile
    s3File = file_api.s3File

def typeDiagnosis(*path_vars):
    def file_func(func):
        func_arg_vars = list(wFile.Copy.__code__.co_varnames[:func.__code__.co_argcount])
        path_like_list = path_vars if len(path_vars) else func_arg_vars
        def wrapper(*args, **kwargs):
            args = list(args)
            func_var_dict = {var: kwargs[var] if var in kwargs else args.pop(0) for var in func_arg_vars if var in kwargs or len(args)>0}
            ftype = [pathStr(func_var_dict[path_var]).attr for path_var in path_like_list]
            func_var_dict = {var_name: pathStr(var_val).path if var_name in func_var_dict else var_val
                             for var_name, var_val in func_var_dict.items()}
            if all([ftype[0] == ftype_ for ftype_ in ftype]):
                File = wFile.filesys.get(ftype[0], gfile)
                if hasattr(File, func.__name__):
                    filefunc = getattr(File, func.__name__)
                else:
                    filefunc = getattr(gfile, func.__name__)
                return filefunc(**func_var_dict)
            else:
                return func(**func_var_dict)
        return wrapper
    return file_func


class wFile(object):
    path_store = dict()
    filesys = {'s3': s3File, 'hdfs':hdfsFile, 'local': gfile}
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def init_hdfs(ip_port):
        hdfsFile.init_client(ip_port)

    @staticmethod
    @typeDiagnosis()
    def Exists(filename):
        pass

    @staticmethod
    def Open(*args, **kwargs):
        args = [arg.path if isinstance(arg, pathStr) else arg for arg in args]
        for key, value in kwargs.items():
            if isinstance(value, pathStr):
                kwargs[key] = value.path
        return smart_open.open(*args, **kwargs)

    @staticmethod
    @typeDiagnosis()
    def DeleteRecursively(dirname):
        pass

    @staticmethod
    @typeDiagnosis()
    def IsDirectory(dirname):
        pass

    @staticmethod
    @typeDiagnosis()
    def Walk(top):
        pass

    @staticmethod
    @typeDiagnosis()
    def MakeDirs(dirname):
        pass

    @staticmethod
    @typeDiagnosis()
    def Remove(filename):
        pass

    @staticmethod
    @typeDiagnosis()
    def ListDirectory(dirname):
        pass

    @staticmethod
    @typeDiagnosis()
    def Rename(oldname, newname):
        pass

    @staticmethod
    def CopyDirectory(srcPath, dstPath, overwrite=False):

        file1, file2 = wFile.filesys.get(pathStr(srcPath).attr, gfile), wFile.filesys.get(pathStr(dstPath).attr, gfile)
        path1, path2 = pathStr(srcPath).path, pathStr(dstPath).path
        exist = file2.Exists(path2)
        if exist and not overwrite:
            assert False, '{} has exist'.format(path2)
        if path1[-1] != '/':
            path1 += '/'
        if path2[-1] != '/':
            path2 += '/'
        if exist:
            file2.DeleteRecursively(path2)
        for root, dirs, files in wFile.Walk(srcPath):
            new_root = path2 + root[len(path1):]
            for d in dirs:
                wFile.MakeDirs(os.path.join(new_root, d))
            for f in files:
                wFile.Copy(os.path.join(root, f), os.path.join(new_root, f))

    @staticmethod
    @typeDiagnosis('srcPath', 'dstPath')
    def Copy(srcPath, dstPath, overwrite=False):
        file1, file2 = wFile.filesys.get(pathStr(srcPath).attr, gfile), wFile.filesys.get(pathStr(dstPath).attr, gfile)
        path1, path2 = pathStr(srcPath).path, pathStr(dstPath).path
        exist = file2.Exists(path2)
        if exist and not overwrite:
            assert False, '{} has exist'.format(path2)
        if exist:
            file2.Remove(path2)
        try:
            gfile.Copy(path1, path2)
        except:
            ftypelist = [file1, file2]
            if 's3' in ftypelist and 'hdfs' in ftypelist:
                copy_func = s3File.CopyHdfs
            elif 's3' in ftypelist and 'local' in ftypelist:
                copy_func = s3File.CopyLocal
            elif 'hdfs' in ftypelist and 'local' in ftypelist:
                copy_func = hdfsFile.CopyLocal
            else:
                assert False, "Can't copy between {} and {}".format(file1, file2)
            copy_func(srcPath, dstPath)

if __name__ == '__main__':
    a = pathStr('/Users/snoworday/Downloads/part-00100-eb6b4732-3b25-4cd2-978b-7f4f1f5f18a5-c000.txt')
    f = wFile.Open(a, 'r')
    c = 1