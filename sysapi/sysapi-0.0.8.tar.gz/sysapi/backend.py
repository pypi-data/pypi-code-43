from typing import List, Optional, Dict, Tuple
from sysapi.user import get_user, get_users, create_user, UserOut, UserIn, UserInDB
from sysapi.snapshot import SnapshotModel, get_snapshots, get_snapshot
import json
import logging
from libzfs_core import lzc_exists, lzc_create, lzc_snapshot
import pickledbod as pickledb
from os.path import exists, isfile, isdir
import pathlib
import os, pwd, grp
import datetime
# from pyzfs import 
import subprocess

LISTSNAPS_CMD = "/sbin/zfs list -H -t snapshot -o name ".split()
RECSNAP_CMD = "/sbin/zfs snap -o inspeere.com:autogen=yes -r ".split()
RESET_CMD = "./cleanup.sh"

SnapRes = Tuple[int, List[str]]
CmdRes = Tuple[int, str]

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
        
class PdbStore():
    db = None

    @classmethod
    def get_db(cls) -> pickledb.PickleDB:
        return cls.db

    @classmethod
    def create_db(cls, file: pathlib.Path) -> None:
        cls.db = pickledb.load(file, True)

def list_snaps(fsname: str) -> SnapRes:
    cp = subprocess.run(LISTSNAPS_CMD + list([fsname]), capture_output=True)
    if cp.returncode == 0: return (0, cp.stdout.split())
    else: 
        logging.debug("Snap error {}: {}".format(cp.returncode,cp.stderr))
        return (cp.returncode, [cp.stderr])

def recursive_snaps(fsname: str, snapname: str) -> CmdRes:
    cp = subprocess.run(RECSNAP_CMD + list([fsname+snapname]), capture_output=True)
    if cp.returncode == 0: return (0, "")
    else: return (cp.returncode, cp.stderr)


def do_reset():
    cp = subprocess.run(RESET_CMD)


def do_get_db(config_file) -> pickledb.PickleDB:
    config = do_get_config(config_file)['config']
    dbconfig = config['db']
    dbfile = pathlib.Path(dbconfig['path']) / dbconfig['file']
    PdbStore.create_db(dbfile)
    return PdbStore.get_db()

def do_get_installed(config_file: str)-> bool:
    db = do_get_db(config_file)
    installed = db.get('installed')
    return installed

def do_get_config(config_file: str):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


MISSING_ERR_MSG = \
    "Remember to create ZFS filesystems prior to calling " + \
    "backend init: ZFS filesystems need to be mounted in" + \
    " backend CT by adding an mp[n] setting in the CT " + \
    "configuration (/etc/pve/lxc/CYID.conf)"

CONFLICT_DIR_MSG = \
    "Please remove manually or run repair service to try " + \
    "to automatically remove conflicting object."

CONFLICT_SNAP_MSG = \
    "Please remove manually or run repair service to try " + \
    "to automatically remove conflicting snapshot."

def do_setup(config_file: str) -> bool:
    config = do_get_config(config_file)['config']
    logging.debug("config ={}".format(config))
    pool = config['pool']
    filesystems = config['filesystems']
    pool_obj = FileSystem(**pool)
    rootfs = None
    for fs in filesystems:
        fs_obj = FileSystem(**fs)
        if fs['rootfs']: rootfs = fs_obj
    for fs in FileSystem.filesystems.values():
        if not lzc_exists(bytes(fs.name,'utf-8')):
            logging.debug("Filesystem {} missing!".format(fs.name))
            return (False, "Filesystem {} missing.".format(fs.name)+ MISSING_ERR_MSG)

       
        
            
        
        if fs.rootfs:
            snaps = list_snaps(fs.name)
            # snaps[0] contains return code of unix command: 0 is ok.
            if snaps[0] == 0 and len(snaps[1]) > 0:
                return (False, "Filesystem {} contains snapshots.".format(fs.name)+ CONFLICT_SNAP_MSG)
            elif snaps[0] != 0:
                return (False, "Error listing filesystem {} snapshots.".format(fs.name)+ str(snaps[1][0]))
            res = recursive_snaps(fs.name, '@initial')
            if res[0] != 0:
                return (False, "Error creating recursiv snapshot in {}.".format(fs.name)+ str(res[1]))
            #lzc_snapshot([bytes(fs.name,'utf-8')+b'@initial'])
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
        newname = str(dbfile) + "bk-"+ datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        logging.debug("DB file already exists: {}! Renaming to {}."
                        .format(dbfile,newname))
        os.rename(dbfile,newname)
    PdbStore.create_db(dbfile)
    db = PdbStore.get_db()
    db.set('installed',True)
    db.set('rootfs',rootfs.name)
    db.dcreate('users')
    return (True, "")

def do_repair(config_file: str) -> bool:
    return (True, "")

def do_get_users(db: PdbStore) -> List[str]:
    logging.debug(db.dgetall('users'))
    return list(db.dgetall('users').keys())


def do_get_snapshots(db) -> List[str]:
    rootfs = db.get('rootfs')
    snaps = list_snaps(rootfs)
    if snaps[0] != 0: return (False, "Error listing filesystem {} snapshots.".format(rootfs)+ str(snaps[1][0]))
    return (True, snaps[1])



def do_get_user(db: PdbStore, login: str) -> Optional[UserInDB]:
    return db.dget('users',login)


def do_create_user(db: PdbStore, user_in: UserIn) -> Optional[UserInDB]:
    #return UserInDB(**user_in.dict(), hashed_password='lskjhdlhw')
    user = create_user(user_in)
    db.dadd('users', (user.username,user.__dict__))
    return user

def do_get_snapshot(db: PdbStore, snapshot: str) -> SnapshotModel:
    return get_snapshot(snapshot)