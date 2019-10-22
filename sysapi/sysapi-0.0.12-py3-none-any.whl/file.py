from enum import Enum
from typing import Optional, List, Union
from pydantic import BaseModel
from sysapi.snapshot import SnapshotModel, get_snapshot

class FileType(str, Enum):
    FILE        = "file"
    DIRECTORY   = "directory"
    SYMLINK     = "symlink"
    SOCKET      = "socket"
    SPECIAL     = "special"
    ## Following types should not be found in user dirs.
    ## but if they do, they appear as special.
    FIFO        = "fifo"
    BLOCK       = "block"
    CHAR        = "char"


class FileModel(BaseModel):
    name: str
    # path: DirectoryPath
    # TODO: For early dev, deactivate path testing
    path: str
    size: int
    perm: str
    ftype:  FileType
    snap: SnapshotModel
    owner: str

class SymlinkModel(FileModel):
    target: str = None # Allow for Dangling symlink

class DirectoryModel(FileModel):
    #parent: FileModel = None
    files: List[FileModel] = []



