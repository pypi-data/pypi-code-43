import io
import sys


class Tee(io.StringIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, *args, **kwargs):
        super().read(self, *args, **kwargs)

    def write(self, *args, **kwargs):
        print(*args, **kwargs, file=sys.__stdout__, end="")
        super().write(*args, **kwargs)
