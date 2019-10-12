import os
from tensorflow import gfile
# from pyspark import SparkFiles
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
        func_arg_vars = list(wfile.Copy.__code__.co_varnames[:func.__code__.co_argcount])
        path_like_list = path_vars if len(path_vars) else func_arg_vars
        def wrapper(*args, **kwargs):
            args = list(args)
            func_var_dict = {var: kwargs.pop(var) if var in kwargs else args.pop(0) for var in func_arg_vars if var in kwargs or len(args)>0}
            func_var_dict = {var_name: pathStr(var_val).path if var_name in path_like_list else var_val
                             for var_name, var_val in func_var_dict.items()}
            ftype = [pathStr(func_var_dict[path_var]).attr for path_var in path_like_list]
            if all([ftype[0] == ftype_ for ftype_ in ftype]):
                File = wfile.filesys.get(ftype[0], gfile)
                if hasattr(File, func.__name__):
                    filefunc = getattr(File, func.__name__)
                elif hasattr(gfile, func.__name__):
                    filefunc = getattr(gfile, func.__name__)
                else:
                    filefunc = func
                return filefunc(**func_var_dict)
            else:
                return func(**func_var_dict)
        return wrapper
    return file_func


class wfile(object):
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
    def _overwrite(objpath, is_dir):
        ftype = wfile.filesys.get(pathStr(objpath).attr, gfile)
        exist = ftype.Exists(objpath)
        if exist:
            if is_dir:
                ftype.DeleteRecursively(objpath)
            else:
                ftype.Remove(objpath)

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
    def _CopyDirFuncDiffSys(*ftypelist):
        if 's3' in ftypelist and 'hdfs' in ftypelist:
            copy_func = s3File.CopyDirHdfs
        elif 's3' in ftypelist and 'local' in ftypelist:
            copy_func = s3File.CopyDirLocal
        else:
            copy_func = wfile._CopyDirectory
        return copy_func

    @staticmethod
    def _CopyFuncDiffSys(*ftypelist):
        if 's3' in ftypelist and 'hdfs' in ftypelist:
            copy_func = s3File.CopyHdfs
        elif 's3' in ftypelist and 'local' in ftypelist:
            copy_func = s3File.CopyLocal
        elif 'hdfs' in ftypelist and 'local' in ftypelist:
            copy_func = hdfsFile.CopyLocal
        else:
            assert False, "Can't copy between {}".format(' and '.join(ftypelist))
        return copy_func

    @staticmethod
    def _CopyDirectory(srcPath, dstPath):
        for root, dirs, files in wfile.Walk(srcPath):
            new_root = dstPath + root[len(srcPath):]
            for d in dirs:
                wfile.MakeDirs(os.path.join(new_root, d))
            for f in files:
                wfile.Copy(os.path.join(root, f), os.path.join(new_root, f))

    @staticmethod
    @typeDiagnosis('srcPath', 'dstPath')
    def CopyDirectory(srcPath, dstPath, overwrite=False):
        def addtail(path):
            if path[-1] != '/':
                path += '/'
            return path
        file1, file2 = wfile.filesys.get(pathStr(srcPath).attr, gfile), wfile.filesys.get(pathStr(dstPath).attr, gfile)
        path1, path2 = addtail(srcPath), addtail(dstPath)
        if overwrite:
            wfile._overwrite(path2, is_dir=True)
        copy_func = wfile._CopyDirFuncDiffSys(file1, file2)
        copy_func(path1, path2)

    @staticmethod
    @typeDiagnosis('srcPath', 'dstPath')
    def Copy(srcPath, dstPath, overwrite=False):
        # src and dst path in different file system
        file1, file2 = wfile.filesys.get(pathStr(srcPath).attr, gfile), wfile.filesys.get(pathStr(dstPath).attr, gfile)
        path1, path2 = srcPath, dstPath
        if overwrite:
            wfile._overwrite(path2, is_dir=False)
        try:
            gfile.Copy(path1, path2)
        except:
            copy_func = wfile._CopyFuncDiffSys(file1, file2)
            copy_func(srcPath, dstPath)

if __name__ == '__main__':
    a = pathStr('/Users/snoworday/Downloads/part-00100-eb6b4732-3b25-4cd2-978b-7f4f1f5f18a5-c000.txt')
    f = wfile.Open(a, 'r')
    c = 1