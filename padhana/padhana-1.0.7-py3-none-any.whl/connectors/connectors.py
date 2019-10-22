from os import listdir
from os.path import isfile, join
import fnmatch


class FolderConnector:

    def __init__(self, seq=None, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if not hasattr(self, 'path'):
            raise ValueError('You must provide a path')

        if not hasattr(self, 'filter'):
            self.filter = '*'

        self.files = self.__get_files__()
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):

        if self.index > len(self.files) - 1:
            raise StopIteration
        else:
            self.index += 1
            return join(self.path, self.files[self.index - 1])

    def __get_files__(self):
        return [f for f in listdir(self.path) if
                fnmatch.fnmatch(f, self.filter)]
