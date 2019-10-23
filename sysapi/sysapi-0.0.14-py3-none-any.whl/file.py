from enum import Enum
from typing import Optional, List, Union, Dict, Tuple, Any
from pydantic import BaseModel
from sysapi.snapshot import SnapshotModel
import pathlib
import logging
import os, pwd
from stat import filemode

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

    @classmethod
    def create_file(cls, 
            path_in_snap: pathlib.Path, 
            fpath: str, snapshot: str, 
            username: str, iparams: Dict[str,Any]) -> 'Tuple[bool, Union[FileModel,str]]':
        params = iparams
        logging.debug("looking for file in '{}', fpath='{}'...".format(path_in_snap, fpath))
        
        stat_res : os.stat_result = path_in_snap.stat()
        uid = stat_res.st_uid
        login = pwd.getpwuid(uid).pw_name
        if login == params['uowner']: s_user = username
        else: s_user = login
        mode = stat_res.st_mode
        ftype = FileType.SPECIAL
        if path_in_snap.is_dir():
            ftype = FileType.DIRECTORY
        if path_in_snap.is_file():
            ftype = FileType.FILE
        if path_in_snap.is_symlink():
            ftype = FileType.SYMLINK
        (res, snap_obj )= SnapshotModel.get_snapshot(snapshot)
        if not res : return (res, snap_obj)

        return (True, cls(
            name = os.path.basename(fpath), 
            owner = s_user, 
            path = os.path.dirname(fpath) +'/', 
            size = stat_res.st_size,
            perm = filemode(mode),
            ftype = ftype,
            snap = snap_obj ))

class SymlinkModel(FileModel):
    target: str = None # Allow for Dangling symlink

class DirectoryModel(FileModel):
    #parent: FileModel = None
    files: List[FileModel] = []



