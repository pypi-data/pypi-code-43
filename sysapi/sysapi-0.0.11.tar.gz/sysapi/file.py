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



