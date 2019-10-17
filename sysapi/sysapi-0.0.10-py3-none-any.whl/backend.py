from typing import List, Optional, Dict, Tuple, Any, Union
from sysapi.user import get_user, get_users, create_user, UserOut, UserIn, UserInDB
from sysapi.snapshot import SnapshotModel, get_snapshot
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
RESET_CMD = "./bin/cleanup.sh"
LIST_SNAP_CMD = "/sbin/zfs list -H -p -t snap -o name,creation".split()

SnapshotsRes = Tuple[int, List[str]]
CmdRes = Tuple[int, str]
SnapRes = Tuple[int, Union[str,SnapshotModel]]

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

def list_snaps(fsname: str) -> SnapshotsRes:
    logging.debug("Listing snapshots for fs='{}".format(fsname))
    cp = subprocess.run(LISTSNAPS_CMD + list([fsname]), capture_output=True)
    if cp.returncode == 0: return (0, cp.stdout.split())
    else: 
        logging.debug("Snap error {}: {}".format(cp.returncode,cp.stderr))
        return (cp.returncode, [cp.stderr])

def recursive_snaps(fsname: str, snapname: str) -> CmdRes:
    cp = subprocess.run(RECSNAP_CMD + list([fsname+snapname]), capture_output=True)
    if cp.returncode == 0: return (0, "")
    else: return (cp.returncode, cp.stderr)

def list_snap(fsname: str) -> SnapRes:
    cp = subprocess.run(LIST_SNAP_CMD + list([fsname]), capture_output=True)
    logging.debug("list_snap returned {}".format(cp.stdout))
    if cp.returncode == 0: return (0, cp.stdout.split())
    else: return (cp.returncode, cp.stderr)

def do_reset(resetkey: str):
    params = read_params()
    if params['resetkey']  == resetkey:
        cp = subprocess.run((RESET_CMD+" "+params['pool']+" "+params['rootfs']).split())
        return True
    else: return False


def open_db() -> pickledb.PickleDB:
    params = read_params()
    if not isdir(params['dbpath']):
        os.system("/bin/mkdir -p "+params['dbpath'])
    dbfile = pathlib.Path(params['dbpath']) / "safer.pdb"
    PdbStore.create_db(dbfile)
    return PdbStore.get_db()

def do_get_installed()-> bool:
    db = open_db()
    installed = db.get('installed')
    return installed

def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def read_params():
    if os.path.isfile("/etc/safer/params.json"):
        return read_config("/etc/safer/params.json")
    return read_config("./params.json")

def do_get_config() -> Any:
    params = read_params()
    logging.debug("Config vars={}".format(params))
    path = "./config.json"
    if os.path.isfile('/etc/safer/config.json'):
        path = '/etc/safer/config.json'
    with open(path, 'r') as f:
        raw_config = f.read()
        for k,v in params.items():
            raw_config = raw_config.replace('{'+k+'}',v)
        return json.loads(raw_config)
        

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
    config = do_get_config()['config']
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
                return (False, "Error creating recursive snapshot in {}.".format(fs.name)+ str(res[1]))
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
    db = open_db()
    db.set('installed',True)
    db.set('rootfs',rootfs.name)
    db.dcreate('users')
    return (True, "")

def do_repair(config_file: str) -> bool:
    return (True, "")

def do_get_users(db: PdbStore) -> List[str]:
    logging.debug(db.dgetall('users'))
    return list(db.dgetall('users').keys())


def do_get_snapshots() -> Tuple[bool,str]:
    params = read_params()
    rootfs = params['rootfs']
    snap_res : List[str] = list_snaps(rootfs)
    logging.debug("snape_res: {}".format(snap_res))
    if snap_res[0] != 0: return (False, "Error listing filesystem {} snapshots.".format(rootfs)+ str(snap_res[1][0]))
    snaps = [s[s.index(b"@"):] for s in snap_res[1]] #[str(s)[str(s).index("@"):] for s in snap_res[1]]
    return (True, snaps)



def do_get_user(db: PdbStore, login: str) -> Optional[UserInDB]:
    return db.dget('users',login)


def do_create_user(db: PdbStore, user_in: UserIn) -> Optional[UserInDB]:
    #return UserInDB(**user_in.dict(), hashed_password='lskjhdlhw')
    user = create_user(user_in)
    db.dadd('users', (user.username,user.__dict__))
    return user

def do_get_snapshot(snapshot: str) -> Tuple[bool, Union[SnapshotModel,str]]:
    params = read_params()
    rootfs = params['rootfs']
    (res, detail) = list_snap(rootfs+snapshot)
    if res == 0:
        snap = get_snapshot(snapshot, detail)
        return (True, snap)
    else: return (False, detail)
    