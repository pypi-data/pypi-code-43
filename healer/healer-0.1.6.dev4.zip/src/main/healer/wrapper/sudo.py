"""
Wrapper for sudo
https://linux.die.net/man/8/sudo
"""

from __future__ import annotations

import os
from typing import List

from healer.wrapper.base import Base


class Sudo(Base):

    def __init__(self):
        super().__init__('wrapper/sudo')

    def script(self, script:str):
        self.execute_unit_sert(script.split())

    def folder_check(self, folder:str):
        return self.has_success(['test', '-d', folder])

    def folder_assert(self, folder:str):
        assert self.folder_check(folder), f"Missing folder '{folder}'"

    def folder_ensure(self, folder:str):
        self.execute_unit_sert(['mkdir', '--parents', folder])

    def parent_ensure(self, path:str):
        folder = os.path.dirname(path)
        self.folder_ensure(folder)

    def file_check(self, file:str):
        return self.has_success(['test', '-f', file])

    def file_assert(self, file:str):
        assert self.file_check(file), f"Missing file '{file}'"

    def file_load(self, file):
        return self.execute_unit_sert(['cat', file]).stdout

    def file_save(self, file:str, text:str):
        self.parent_ensure(file)
        self.execute_unit_sert(['dd', f"of={file}"] , stdin=text)

    def files_copy(self, source, target):
        self.parent_ensure(target)
        self.execute_unit_sert(['cp', '--force', source, target])

    # FIXME atomic
    def files_move(self, source:str, target:str):
        self.files_delete(target)
        self.parent_ensure(target)
        self.execute_unit_sert(['mv', '--force', source, target])

    def files_delete(self, path:str):
        self.execute_unit_sert(['rm', '--force', '--recursive', path])

    def files_sync_attr(self, source:str, target:str):
        preserve = "mode,timestamps"
        self.execute_unit_sert(['cp', '--force', f'--preserve={preserve}', '--attributes-only', source, target])

    def files_sync_path(self, source:str, target:str):
        if self.folder_check(source):
            source = os.path.join(source, '')  # ensure traling slash
            self.folder_ensure(target)
        else:
            self.parent_ensure(target)
        self.execute_unit_sert(['rsync', '-rlptD', '--force', source, target ])

    def xattr_name(self, name:str):
        return f"user.healer.{name}"

    def xattr_get(self, file:str, name:str):
        name = self.xattr_name(name)
        result = self.execute_unit(['getfattr', '-n', name, '--only-values', file])
        if result.rc == 0:
            return result.stdout
        else:
            return None

    def xattr_set(self, file:str, name:str, value:str):
        name = self.xattr_name(name)
        self.execute_unit_sert(['setfattr', '-n', name, '-v', value, file])


SUDO = Sudo()
