import os

from . import data


class Counter:

    def __init__(self, **options):
        self.path = options.get('path', '.')
        self.count = options.get('count', False)
        self.size = options.get('size', False)
    
    def call(self):
        old = os.getcwd()
        os.chdir(self.path)
        if self.count:
            o = self.get_count(self.path)
        elif self.size:
            o = self.get_sizes(self.path)
        else:
            o = self.get_count(self.path)
        os.chdir(old)
        return o

    def get_count(self, path):
        return len(os.listdir(path))

    def get_sizes(self, path):
        return str(data.Data(sum([self.get_size_of(a) for a in os.listdir(path)])))
    
    def get_size_of(self, path):
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                o = 0
                for a in os.listdir(path):
                    o += self.get_size_of(path + '/' + a)
                return o
        except Exception:
            pass
        return 0
