import os


CHUNKSIZE = 8 << 20  # 8 MB


class OSDestination:
    """Generator yielding `store()/delete()`-able files in a local directory"""
    def __init__(self, dirpath):
        os.makedirs(dirpath, exist_ok=True)
        self.dirpath = dirpath

    def __iter__(self):
        for dirpath, _, filenames in os.walk(self.dirpath):
            for filepath in (f'{dirpath}/{filename}' for filename in filenames):
                relpath = os.path.relpath(filepath, self.dirpath)
                yield self.file(relpath, stat=os.stat(filepath))

    def file(self, relpath, stat=None):
        return OSFile(self, relpath, stat=stat)

    def cleanup(self):
        """Remove any empty directories within the local directory"""
        for dirpath, dirnames, filenames in os.walk(self.dirpath):
            if not dirnames and not filenames:
                os.rmdir(dirpath)


class OSFile:
    """Store read()-ables / delete files locally"""

    __slots__ = ('name', 'size', 'modified', 'filepath')

    def __init__(self, osfs, relpath, stat=None):
        self.filepath = f'{osfs.dirpath}/{relpath}'
        self.name = relpath
        if stat is not None:
            self.size = stat.st_size
            self.modified = stat.st_mtime

    def store(self, src):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'wb') as dst:
            data = src.read(CHUNKSIZE)
            while data:
                dst.write(data)
                data = src.read(CHUNKSIZE)

    def delete(self):
        os.remove(self.filepath)
