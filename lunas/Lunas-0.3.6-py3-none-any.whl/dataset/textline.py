import itertools
from pathlib import Path

from .core import Dataset


class TextLine(Dataset):

    def __init__(self, filename: str, name: str = None):
        super().__init__(name)
        filename = Path(filename)
        assert filename.exists()
        self.filename: Path = filename
        self.size = -1

    @staticmethod
    def count_line(filename):
        f = open(filename, 'rb')
        buf_gen = itertools.takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in itertools.repeat(None)))
        n = 0
        end_is_newline = True
        for buf in buf_gen:
            m = buf.count(b'\n')
            n += m
            if m > 0:
                end_is_newline = buf.rindex(b'\n') == len(buf) - 1
        n += int(not end_is_newline)

    def __len__(self):
        if self.size < 0:
            size = 0
            for _ in self.generator():
                size += 1
            self.size = size
        return self.size

    def generator(self):
        with self.filename.open() as r:
            for l in r:
                yield l
