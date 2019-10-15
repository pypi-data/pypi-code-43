from typing import List, Optional, Dict
from sysapi.user import get_user, get_users, create_user, UserOut, UserIn, UserInDB
from sysapi.snapshot import SnapshotModel, get_snapshots, get_snapshot
import json
import logging
from libzfs_core import lzc_exists, lzc_create
import pickledbod as pickledb
from os.path import exists, isfile, isdir
import pathlib
import os, pwd, grp
import datetime
# from pyzfs import 


class PdbStore():
    db = None

    @classmethod
    def get_db(cls) -> pickledb.PickleDB:
        return cls.db

    @classmethod
    def create_db(cls, file: pathlib.Path) -> None:
        cls.db = pickledb.load(file, True)


def do_get_config(config_file: str):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

class FileSystem():
    filesystems : 'Dict[str,FileSystem]' = dict()

    def __init__(self,**kwargs) -> None:
        self.__dict__ = {**self.__dict__, **kwargs}
        FileSystem.filesystems[self.name] = self

    def __repr__(self):
        return "FileSystem(name={}, pool={}, parent={}, backup={}, owner={})"\
            .format(self.name, self.pool, self.parent, self.backup, self.owner)

    def __str__(self)-> str:
        return self.name
        

MISSING_ERR_MSG = \
    "Remember to create ZFS filesystems prior to calling " + \
    "backend init: ZFS filesystems need to be mounted in" + \
    " backend CT by adding an mp[n] setting in the CT " + \
    "configuration (/etc/pve/lxc/CYID.conf)"

CONFLICT_DIR_MSG = \
    "Please remove manually or run repair service to try " + \
    "to automatically remove conflicting object."

def do_setup(config_file: str) -> bool:
    config = do_get_config(config_file)['config']
    logging.debug("config ={}".format(config))
    pool = config['pool']
    filesystems = config['filesystems']
    pool_obj = FileSystem(**pool)
    for fs in filesystems:
        fs_obj = FileSystem(**fs)
    for fs in FileSystem.filesystems.values():
        if not lzc_exists(bytes(fs.name,'utf-8')):
            logging.debug("Filesystem {} missing!".format(fs.name))
            return (False, "Filesystem {} missing.".format(fs.name)+ MISSING_ERR_MSG)
        for dir in fs.dirs:
            dirpath = pathlib.Path(fs.mountpoint) / dir 
            if exists(dirpath):
                if not isdir(dirpath):
                    return (False, 
                        "Filesystem {} contains conflicting object {}."
                            .format(fs.name,dir) + CONFLICT_DIR_MSG)
                else:
                    logging.debug("Filesystem {} already contains a directory named {}!"
                        .format(fs.name,dir))
                    ## Fix owner and perms
                    owner_uid = pwd.getpwnam(fs.owner).pw_uid
                    os.chown(dirpath, owner_uid, 0)
                    os.chmod(dirpath, 0o755)
            else:
                os.mkdir(dirpath,0o755)
                owner_uid = pwd.getpwnam(fs.owner).pw_uid
                os.chown(dirpath, owner_uid, 0)
    dbconfig = config['db']
    dbfile = pathlib.Path(dbconfig['path']) / dbconfig['file']
    logging.debug("Creating DB: {}".format(dbfile))
    if exists(dbfile):
        logging.debug("DB file already exists: {}! Renaming to {}."
                        .format(fs.name,dir))

        newname = dbfile + "bk-"+ datetime.now().strftime("%Y%m%d-%H%M%S")
        os.rename(dbfile,newname)
    PdbStore.create_db(dbfile)
    db = PdbStore.get_db()
    return (True, "")

def do_repair(config_file: str) -> bool:
    return (True, "")

def do_get_users() -> List[str]:
    return get_users()

def do_get_snapshots() -> List[str]:
    return get_snapshots()
    

def do_get_user(login: str) -> Optional[UserInDB]:
    return get_user(login)


def do_create_user(user_in: UserIn) -> Optional[UserInDB]:
    #return UserInDB(**user_in.dict(), hashed_password='lskjhdlhw')
    return create_user(user_in)

def do_get_snapshot(snapshot: str) -> SnapshotModel:
    return get_snapshot(snapshot)