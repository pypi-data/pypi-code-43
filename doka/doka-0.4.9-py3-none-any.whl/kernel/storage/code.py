from pathlib import PosixPath
import shutil


class CodeStorage:
    def __init__(self, directory: PosixPath):
        self._directory = directory

    def remove(self):
        if self._directory.exists():
            shutil.rmtree(self._directory)
