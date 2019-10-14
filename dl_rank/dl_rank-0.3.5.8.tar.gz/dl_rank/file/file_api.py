import os
# from pyspark import SparkFiles
import boto3
from functools import reduce
import subprocess
import pyhdfs

class hdfsFile(object):
    ip = ''
    port = ''
    client = None

    @staticmethod
    def init_client(ip_port):
        assert 'HADOOP_HOME' in os.environ and 'HADOOP_HDFS_HOME' in os.environ
        classpath = subprocess.check_output('hadoop classpath --glob', shell=True).decode('utf-8').strip()
        if 'CLASSPATH' not in os.environ:
            os.environ['CLASSPATH'] = ''
        if classpath not in os.environ['CLASSPATH']:
            os.environ['CLASSPATH'] = ':'.join([os.environ['CLASSPATH'], classpath])
        hdfsFile.ip, hdfsFile.port = ip_port.split(':')
        hdfsFile.client = pyhdfs.HdfsClient(ip_port)

    @staticmethod
    def DeleteRecursively(path):
        hdfsFile.client.delete(path)

    @staticmethod
    def Remove(path):
        hdfsFile.client.delete(path)

    @staticmethod
    def ListDirectory(dirname):
        return hdfsFile.client.listdir(dirname)

    @staticmethod
    def CopyLocal(srcPath, dstPath):
        if dstPath.startswith('hdfs://'):
            hdfsFile.client.copy_from_local(srcPath, dstPath)
        elif srcPath.startswith('hdfs://'):
            hdfsFile.client.copy_to_local(srcPath, dstPath)

    @staticmethod
    def Copy(srcPath, dstPath, overwrite=False):
        if overwrite and hdfsFile.Exists(dstPath):
            hdfsFile.Remove(dstPath)
        else:
            os.system('hadoop fs -cp {src} {dst}'.format(src=srcPath, dst=dstPath))


    @staticmethod
    def MakeDirs(filePath):
        if not hdfsFile.client.exists(filePath):
            hdfsFile.client.mkdirs(filePath)

    @staticmethod
    def Rename(srcPath, dstPath):
        if not hdfsFile.client.exists(srcPath):
            return False
        os.system('hadoop fs -mv {src} {dst}'.format(src=srcPath, dst=dstPath))
        # hdfsFile.client.rename(srcPath, dstPath)
        return True

    @staticmethod
    def RenameDirectory(srcPath, dstPath):
        hdfsFile.Rename(srcPath, dstPath)

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
        try:
            filestatus = hdfsFile.client.get_file_status(filename)
            if filestatus.childrenNum:
                return True
            else:
                return False
        except:
            # not exists
            return False

class s3File(object):
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    @staticmethod
    def split_s3_path(filename):
        filename = filename[len('s3://'):]
        bucket, key = filename.split('/', 1)
        return bucket, key

    @staticmethod
    def _list_obj_under_path(filename):
        bucket, keyname = s3File.split_s3_path(filename)
        bucket = s3File.s3.Bucket(bucket)
        objs = bucket.objects.filter(Prefix=keyname)
        return objs

    @staticmethod
    def Exists(filename):
        filename = removetail(filename)
        _, keyname = s3File.split_s3_path(filename)
        objs = iter(s3File._list_obj_under_path(filename))
        try:
            obj = next(objs)
            obj_tail = obj.key[len(keyname):]
            if obj_tail == '' or obj_tail.startswith('/'):
                return True
            else:
                return False
        except StopIteration:
            return False

    @staticmethod
    def IsDirectory(filename):
        filename = addtail(filename)
        objs = iter(s3File._list_obj_under_path(filename))
        try:
            _ = next(objs)
            return True
        except StopIteration:
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
            obj_under_dir = [obj[len(root):] for obj in filter(lambda name: name.startswith(root), all_obj)]
            pre_key_under_dir = set([obj.split('/')[0]+'/' if '/' in obj else obj for obj in obj_under_dir])
            if '' in pre_key_under_dir:
                pre_key_under_dir.remove('')
            dirs, files = reduce(lambda x, y: (x[0]+[y], x[1]) if '/' in y else (x[0], x[1]+[y]),
                                 pre_key_under_dir,
                                 ([], []))
            return root, dirs, files

        def _recursive_walk(root):
            root, dirs, files = _walk(root)
            yield 's3://'+os.path.join(bucket, root), \
                  [d.strip('/') for d in dirs], \
                  files
            for d in dirs:
                yield from _recursive_walk(os.path.join(root, d))

        if keyroot[-1] != '/':
            keyroot += '/'
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
    def RenameDirectory(oldname, newname):
        oldname = addtail(oldname)
        newname = addtail(newname)
        bucket, _ = s3File.split_s3_path(oldname)
        all_obj = [obj.key for obj in list(s3File._list_obj_under_path(oldname))]
        for old_key in all_obj:
            old_key = os.path.join('s3://'+bucket, old_key)
            new_key = newname + old_key[len(oldname):]
            if old_key[-1] == '/':
                if not s3File.Exists(new_key):
                    s3File.MakeDirs(new_key)
            else:
                s3File.Copy(old_key, new_key)
        s3File.DeleteRecursively(oldname)


    @staticmethod
    def Remove(filename):
        bucket, key = s3File.split_s3_path(filename)
        s3File.s3.Object(bucket, key).delete()

    @staticmethod
    def CopyLocal(srcPath, dstPath, is_recursive=False):
        cmd = 'aws s3 cp {srcPath} {dstPath}'.format(srcPath=srcPath, dstPath=dstPath)
        if is_recursive:
            cmd += ' --recursive'
        os.system(cmd)

    @staticmethod
    def CopyDirLocal(srcPath, dstPath):
        s3File.CopyLocal(srcPath, dstPath, is_recursive=True)

    @staticmethod
    def _CopyHdfs(srcPath, dstPath, is_recursive=False):
        cmd = 's3-dist-cp --src={srcPath} --dest={dstPath}'.format(srcPath=srcPath, dstPath=dstPath)
        if is_recursive:
            pass
        os.system(cmd)

    @staticmethod
    def CopyDirHdfs(srcPath, dstPath):
        s3File._CopyHdfs(srcPath, dstPath, is_recursive=True)

    @staticmethod
    def Copy(srcPath, dstPath, overwrite=False):
        if overwrite and s3File.Exists(dstPath):
            s3File.Remove(dstPath)
        newbucket, newkey = s3File.split_s3_path(dstPath)
        oldname = srcPath.strip('s3://')
        s3File.s3.Object(newbucket, newkey).copy_from(CopySource=oldname)

class pathStr(os.PathLike):
    def __new__(cls, *args, **kwargs):
        instance = super(pathStr, cls).__new__(cls)
        instance.path = None
        return instance

    def __init__(self, path, prefix=None):
        if isinstance(path, pathStr):
            self.path = path.path
            self.attr = path.attr
        else:
            if prefix is not None:
                self.path = os.path.join(prefix, path)
            else:
                self.path = path
            self._setAttr()
            if self.attr == 'local' and prefix is None:
                self.path = os.path.abspath(path)

    def _setAttr(self):
        if self.path.startswith('s3://'):
            self.attr = 's3'
        elif self.path.startswith('hdfs://'):
            self.attr = 'hdfs'
            if self.path.startswith('hdfs:///'):
                self.path = 'hdfs://'+hdfsFile.ip + self.path[7:]
        else:
            self.attr = 'local'

    def __add__(self, other):
        # self + other
        if other[0] == '/':
            other = other[1:]
        path = os.path.join(self.path, other)
        return pathStr(path)

    def __radd__(self, other):
        # self + other
        path = os.path.join(other, self.path)
        return pathStr(path)

    def __iadd__(self, other):
        if other[0] == '/':
            other = other[1:]
        self.path = os.path.join(self.path, other)
        return self

    def __getitem__(self, item):
        return self.path[item]

    def __fspath__(self):
        return self.path

    def __str__(self):
        return self.path

    # def __repr__(self):
    #     return self.path

    def __getattr__(self, item):
        obj = getattr(self.path, item)
        if hasattr(obj, '__call__'):
            def wrapper(*args, **kwargs):
                result = obj(*args, **kwargs)
                if isinstance(result, str):
                    return pathStr(result)
                else:
                    return result
            return wrapper
        else:
            return obj

class s3FileObj(object):
    def __init__(self, fileobj):
        self.file = fileobj

    def read(self):
        return self.file.read().decode('utf-8')

    def readline(self):
        f = self.file.iter_lines()
        for line in f:
            yield line.decode('utf-8')

    def readlines(self):
        all_file = self.file.read().decode('utf-8')
        all_file_list = all_file.split('\n')
        return all_file_list

    def __enter__(self):
        pass

    def __exit__(self):
        self.file.close()


def addtail(path):
    if path[-1] != '/':
        path += '/'
    return path

def removetail(path):
    if path[-1] == '/':
        path = path[:-1]
    return path

if __name__ == '__main__':
    p = pathStr('/Users/snoworday')
    s3File.Walk(p)
    os.stat(p)
    print(str(p))
    p[2]
    p.__str__()
    p.strip()
    t = p + 'd'
    b = 4




