from os import path, remove
from shutil import copy as shutil_copy


class File:
    def __init__(self, file_path=None):
        self.path = file_path

    def exists(self, file_path=None):
        if not file_path:
            file_path = self.path

        return path.isfile(file_path)

    def delete(self, file_path=None):
        if not file_path:
            file_path = self.path

        if self.exists(file_path=file_path):
            remove(file_path)
        return self.exists(file_path=file_path)

    def write(
        self, data, overwrite=False, encoding="utf-8", newline="\n", file_path=None
    ):
        if not file_path:
            file_path = self.path

        if data and isinstance(data, str):
            if overwrite or not self.exists(file_path=file_path):
                with open(
                    file_path, "w", encoding=encoding, newline=newline
                ) as file_stream:
                    file_stream.write(data)
            else:
                with open(
                    file_path, "a", encoding=encoding, newline=newline
                ) as file_stream:
                    file_stream.write(data)

    def read(self, file_path=None, encoding="utf-8", newline="\n"):
        if not file_path:
            file_path = self.path

        data = None

        if self.exists(file_path):
            with open(
                self.path, "r", encoding=encoding, newline=newline
            ) as file_stream:
                data = file_stream.read()

        return data

    def copy(self, destination):
        if self.exists(self.path):
            shutil_copy(self.path, destination)
