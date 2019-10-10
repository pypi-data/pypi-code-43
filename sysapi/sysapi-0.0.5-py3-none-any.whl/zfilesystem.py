from typing import List
from pydantic import BaseModel, DirectoryPath

class FilesystemModel(BaseModel):
    name: str
    # mountpoint: DirectoryPath = None
    # TODO: For early dev, deactivate path testing
    mountpoint: str

class ZfsPath(BaseModel):
    """ Break path elements in a ZFS filesystem.

    A path in a ZFS filesystem is composed of the prefix corresponding
    to the mountpoint and the remaining part from the mountpoint.
    This class helps reverse looking up for a ZFS filesystem given any path.
    """
    basefsdir: FilesystemModel
    # pathinfs: DirectoryPath = None
    # TODO: For early dev, deactivate path testing
    pathinfs: str




static_fs_list = ['hf-1', 'lf-1', 'nobk-1', 'sync-1']

def discover_filesystems() -> List[FilesystemModel]:
    # FIXME: replaced with real discovery
    return [FilesystemModel(name='zpool/shared/'+ n, mountpoint='/zpool/shared/'+ n) for n in static_fs_list]

def lookup_zfs_path(path: str)-> Optional[ZfsPath]:
    filesystems = discover_filesystems()
    for fs in filesystems:
        if path.startswith(fs.mountpoint): 
            return ZfsPath(basefsdir=fs, pathinfs=path[len(fs.mountpoint):])
    return None 
