import os
import boto3
from tensorflow import gfile
from collections import defaultdict
# from pyspark import SparkFiles
import pyhdfs
from functools import reduce
try:
    from dl_rank.file.file_api import s3FileObj, pathStr
except:
    from .file_api import s3FileObj, pathStr
import boto3
from shutil import copytree
class hdfsFile(object):
    ip = ''
    client = None
    @staticmethod
    def DeleteRecursively(path):
        hdfsFile.client.delete(path)

    @staticmethod
    def Remove(path):
        hdfsFile.client.delete(path)

    @staticmethod
    def ListDirectory(dirname):
        return hdfsFile.client.listdir(dirname)

    # 上传文件
    def upload(self, fileName, tmpFile):
        fs = self.client
        fs.copy_from_local(fileName, tmpFile)

    @staticmethod
    def Copy(srcPath, dstPath):
        if not srcPath.startswith('hdfs://'):
            dstPath = dstPath.strip('/')
            _ = os.system('hadoop fs -copyFromLocal {src} {dst}'.format(src=srcPath, dst=dstPath))
            # hdfsFile.client.copy_from_local(srcPath, dstPath)
        elif not dstPath.startswith('hdfs://'):
            srcPath = srcPath.strip('/')
            _ = os.system('hadoop fs -copyToLocal {src} {dst}'.format(src=srcPath, dst=dstPath))
            # hdfsFile.client.copy_to_local(srcPath, dstPath)
        else:
            srcPath = srcPath.strip('/')
            dstPath = dstPath.strip('/')
            _ = os.system('hadoop fs -cp {src} {dst}'.format(src=srcPath, dst=dstPath))
            # tmpPath = '/tmp/dl_rank/hdfs'
            # gfile.MakeDirs(tmpPath)
            # hdfsFile.client.copy_to_local(srcPath, tmpPath)
            # hdfsFile.client.copy_from_local(tmpPath, dstPath)
            # gfile.DeleteRecursively(tmpPath)

    @staticmethod
    def MakeDirs(filePath):
        if not hdfsFile.client.exists(filePath):
            # os.system('hadoop client -mkdir '+filePath)
            hdfsFile.client.mkdirs(filePath)
            return 'mkdir'
        return 'exits'

    @staticmethod
    def Rename(srcPath, dstPath):
        if not hdfsFile.client.exists(srcPath):
            return False
        hdfsFile.client.rename(srcPath, dstPath)
        return True

    @staticmethod
    def Walk(top):
        return hdfsFile.client.walk(top)

    @staticmethod
    def Open(filename):
        return hdfsFile.client.open(filename)

    @staticmethod
    def Exists(filename):
        return hdfsFile.client.exists(filename)

    @staticmethod
    def IsDirectory(filename):
        filestatus = hdfsFile.client.get_file_status(filename)
        assert False

class s3File(object):
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    @staticmethod
    def split_s3_path(filename):
        filename = filename.strip('s3://')
        bucket, key = filename.split('/', 1)
        return bucket, key

    @staticmethod
    def _list_obj_under_path(filename):
        filename = filename.strip('/')
        bucket, keyname = s3File.split_s3_path(filename)
        bucket = s3File.s3.Bucket(bucket)
        objs = bucket.objects.filter(Prefix=keyname)
        return objs

    @staticmethod
    def Exists(filename):
        objs = list(s3File._list_obj_under_path(filename))
        if len(objs) > 0:   # and objs[0].key.strip('/') == keyname:
            return True
        else:
            return False

    @staticmethod
    def IsDirectory(filename):
        objs = list(s3File._list_obj_under_path(filename))
        if len(objs) == 0:
            return False
        elif len(objs) > 1 or objs[0].key[-1] == '/':
            return True
        else:
            return False

    @staticmethod
    def ListDirectory(dirname):
        _, dirs, files = s3File.Walk(dirname, True)
        dirs = [d.strip('/') for d in dirs]
        return dirs + files

    @staticmethod
    def Open(filename):
        bucket, keyname = s3File.split_s3_path(filename)
        obj = s3File.s3.Object(bucket, keyname)
        return s3FileObj(obj.get()['Body'])#.read().decode('utf-8')

    @staticmethod
    def MakeDirs(dirname):
        bucket, keyname = s3File.split_s3_path(dirname)
        if keyname[-1] != '/':
            keyname = keyname + '/'
            s3File.client.put_object(Bucket=bucket, Key=keyname)

    @staticmethod
    def DeleteRecursively(dirname):
        obj = s3File._list_obj_under_path(dirname)
        obj.delete()

    @staticmethod
    def Walk(dirname, one_step=False):
        bucket, keyroot = s3File.split_s3_path(dirname)
        all_obj = [obj.key for obj in list(s3File._list_obj_under_path(dirname))]

        def _walk(root):
            obj_under_dir = [obj.strip(root) for obj in filter(lambda name: name.startswith(root), all_obj)]
            pre_key_under_dir = set([obj.split('/')[0]+'/' if '/' in obj else obj for obj in obj_under_dir])
            dirs, files = reduce(lambda x, y: (x[0]+[os.path.join(root, y)], x[1]) if '/' in y else (x[0], x[1]+[os.path.join(root, y)]),
                                 pre_key_under_dir,
                                 initial=([], []))
            return root, dirs, files

        def _recursive_walk(root):
            root, dirs, files = _walk(root)
            yield 's3://'+os.path.join(bucket, root), \
                  [d.strip('/') for d in dirs], \
                  files
            for d in dirs:
                yield from _recursive_walk(os.path.join(root, d))

        if dirname[-1] != '/':
            dirname += '/'
        if one_step:
            return _walk(keyroot)
        else:
            return _recursive_walk(keyroot)

    @staticmethod
    def Rename(oldname, newname):
        s3File.Copy(oldname, newname)
        oldbucket, oldkey = s3File.split_s3_path(oldname)
        s3File.s3.Object(oldbucket, oldkey).delete()

    @staticmethod
    def Remove(filename):
        bucket, key = s3File.split_s3_path(filename)
        s3File.s3.Object(bucket, key).delete()

    @staticmethod
    def Copy(srcPath, dstPath):
        # if srcPath.startswith('s3://') and dstPath.startswith('s3://'):
        #     newbucket, newkey = s3File.split_s3_path(dstPath)
        #     # if newkey[-1] == '/':
        #     #     name = srcPath.rsplit('/', 1)[1]
        #     #     newkey += name
        #     oldname = srcPath.strip('s3://')
        #     s3File.s3.Object(newbucket, newkey).copy_from(CopySource=oldname)
        # else:
        recursive = '--recursive' if srcPath[-1] == '/' else ''
        _ = os.system('aws s3 cp {srcPath} {dstPath} {recursive}'.format(srcPath=srcPath, dstPath=dstPath, recursive=recursive))


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
        hdfsFile.client = pyhdfs.HdfsClient(ip_port)

    @staticmethod
    def typeDiagnosis(func):
        def wrapper(*args):
            ftype = [pathStr(p).attr for p in args]
            path = [pathStr(p).path for p in args]
            File = wFile.filesys.get(ftype[0], default=gfile)
            File.__getattribute__(File, func.__name__)(*path)
            func()
        return wrapper

    @staticmethod
    @typeDiagnosis
    def Exists(filename):
        pass

    @staticmethod
    @typeDiagnosis
    def Open():
        pass

    @staticmethod
    @typeDiagnosis
    def DeleteRecursively():
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
        file1, file2 = wFile.filesys.get(pathStr(srcPath).attr, default=gfile), wFile.filesys.get(pathStr(dstPath).attr, default=gfile)
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