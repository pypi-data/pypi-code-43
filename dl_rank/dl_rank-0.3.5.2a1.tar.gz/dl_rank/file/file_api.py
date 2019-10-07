import os
from tensorflow import gfile
# from pyspark import SparkFiles

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
            self.attr = 's3://'
        elif self.path.startswith('hdfs://'):
            self.attr = 'hdfs://'
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
            def wrapper():
                result = obj()
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

if __name__ == '__main__':
    p = pathStr('/Users/snoworday')
    os.PathLike
    os.stat(p)
    print(str(p))
    p[2]
    p.__str__()
    p.strip()
    t = p + 'd'
    b = 4




