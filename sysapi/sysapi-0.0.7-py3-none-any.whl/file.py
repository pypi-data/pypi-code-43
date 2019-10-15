from enum import Enum
from typing import Optional, List, Union
from pydantic import BaseModel
from sysapi.snapshot import SnapshotModel, get_snapshot

class FileType(str, Enum):
    FILE        = "file"
    DIRECTORY   = "directory"
    SYMLINK     = "symlink"
    SOCKET      = "socket"
    FIFO        = "fifo"
    BLOCK       = "block"
    CHAR        = "char"


class FileModel(BaseModel):
    name: str
    # path: DirectoryPath
    # TODO: For early dev, deactivate path testing
    user: str
    path: str
    size: int
    perm: int
    ftype:  FileType
    snap: SnapshotModel
    owner: str

class SymlinkModel(FileModel):
    target: str = None # Allow for Dangling symlink

class DirectoryModel(FileModel):
    parent: str = None
    files: List[FileModel] = []


fake_file = FileModel(
    name="toto",
    user='victor',
    path='/',
    size=123456,
    perm=0o644,
    ftype=FileType.FILE,
    snap=get_snapshot("@first"),
    owner='victor')

fake_file2 = FileModel(
    name="tutu",
    user='victor',
    path='/',
    size=999888,
    perm=0o600,
    ftype=FileType.FILE,
    snap=get_snapshot("@second"),
    owner='victor')

fake_dir = DirectoryModel(
    parent="/",
    files=[fake_file, fake_file2],
    name="titi",
    user='victor',
    path='/',
    size=1024,
    perm=0o644,
    ftype=FileType.DIRECTORY,
    snap=get_snapshot("@current"),
    owner='victor')


