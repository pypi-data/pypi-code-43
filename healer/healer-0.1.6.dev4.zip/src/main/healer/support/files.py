"""
File system operatins
"""

from __future__ import annotations

import errno
import fcntl
import os
import shutil
import tempfile
import threading


class FilesPathLock(object):

    file_desc:int = -1
    system_path:str = None
    thread_guard = threading.Event()  # TODO

    def __init__(self, system_path:str):
        assert os.path.exists(system_path), f"Missing path: {system_path}"
        self.system_path = system_path

    def __enter__(self):
        self.aquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def aquire(self) -> bool:
        if self.file_desc >= 0:
            return True
        try:
            self.file_desc = os.open(self.system_path, os.O_RDONLY)
            fcntl.flock(self.file_desc, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError as error:
            if error.errno == errno.EAGAIN:
                self.release()
                return False
            else:
                raise error

    def release(self) -> None:
        if self.file_desc >= 0:
            os.close(self.file_desc)
            self.file_desc = -1


class FilesSupport():
    """
    file system operations
    """

    @staticmethod
    def machine_id() -> str:
        "use system provided machine id"
        path = "/etc/machine-id"
        if os.path.isfile(path):
            with open(path, 'r') as file:
                return file.read().strip()

    @staticmethod
    def has_writable(dir_path:str) -> bool:
        "verify folder is writable"
        try:
            testfile = tempfile.TemporaryFile(dir=dir_path)
            testfile.close()
        except OSError as error:
            if error.errno == errno.EACCES:  # 13
                return False
            error.filename = dir_path
            raise
        return True

    @staticmethod
    def ensure_parent(path:str) -> None:
        "make parent directory"
        parent = os.path.dirname(path)
        FilesSupport.ensure_folder(parent)

    @staticmethod
    def ensure_folder(path:str) -> None:
        "make nested directory tree"
        if os.path.isdir(path):
            pass
        else:
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def desure_path(path:str) -> None:
        "remove a file or a tree"
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
