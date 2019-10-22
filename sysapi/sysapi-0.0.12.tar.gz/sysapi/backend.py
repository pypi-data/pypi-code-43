from typing import List, Optional, Dict, Tuple, Any, Union
from sysapi.user import get_user, get_users, create_user, UserOut, UserIn, UserInDB
from sysapi.snapshot import SnapshotModel, get_snapshot
from sysapi.file import FileModel, FileType, DirectoryModel
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
from stat import *

LISTSNAPS_CMD = "/sbin/zfs list -H -t snapshot -o name -s creation".split()
RECSNAP_CMD = "/sbin/zfs snap -o inspeere.com:source=api -r ".split()
RESET_CMD = "./bin/cleanup.sh"
LIST_SNAP_CMD = "/sbin/zfs list -H -p -t snap -o name,creation -s creation".split()

SnapshotsRes = Tuple[int, List[str]]
CmdRes = Tuple[int, str]
SnapRes = Tuple[bool, Union[str,SnapshotModel]]

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
    logging.debug("recursive_snaps(fsname={}, snapname={} -> out={}, err={})".format(fsname,snapname,cp.stdout, cp.stderr))
    if cp.returncode == 0: return (0, "")
    else: return (cp.returncode, cp.stderr)

def list_snap(fsname: str) -> SnapRes:
    cp = subprocess.run(LIST_SNAP_CMD + list([fsname]), capture_output=True)
    logging.debug("list_snap returned {}".format(cp.stdout))
    if cp.returncode == 0: 
        logging.debug("Stdout len = {}".format(len(cp.stdout)))
        if len(cp.stdout) ==0:
            return (False, "Snapshot not found.")
        return (True, cp.stdout.split())
    else:
        logging.debug("list snap command failed:"+str(cp.stderr))  
        return (False, "Snapshot not found.")

def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def read_params():
    if os.path.isfile("/etc/safer/params.json"):
        return read_config("/etc/safer/params.json")
    return read_config("./params.json")


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
    params = read_params()
    logging.debug("config ={}".format(config))
    pool = config['pool']
    filesystems = config['filesystems']
    #pool_obj = FileSystem(**pool)
    for fs in filesystems:
        fs_obj = FileSystem(**fs)
 
    for fs in FileSystem.filesystems.values():
        if not lzc_exists(bytes(fs.name,'utf-8')):
            logging.debug("Filesystem {} missing!".format(fs.name))
            return (False, "Filesystem {} missing.".format(fs.name)+ MISSING_ERR_MSG)
        logging.debug("fs = {}".format(fs.__dict__))
        if fs.fstype == "uroot":
            snaps = list_snaps(fs.name)
            # snaps[0] contains return code of unix command: 0 is ok.
            if snaps[0] == 0 and len(snaps[1]) > 0:
                return (False, "Filesystem {} contains snapshots.".format(fs.name)+ CONFLICT_SNAP_MSG)
            elif snaps[0] != 0:
                return (False, "Error listing filesystem {} snapshots.".format(fs.name)+ str(snaps[1][0]))
            res = recursive_snaps(fs.name, '@initial')
            if res[0] != 0:
                return (False, "Error creating recursive snapshot in {}.".format(fs.name)+ str(res[1]))
        
        homes = params['homes']
        owner = params['uowner']
        owner_uid = pwd.getpwnam(owner).pw_uid
        if fs.fstype == "udirs":
            home = pathlib.Path(fs.mountpoint) / homes
            if not home.exists():
                os.mkdir(home, 0o755)
                os.chown(home, owner_uid,0)
    db = open_db()
    db.set('installed',True)
    db.dcreate('users')
    return (True, "")

def do_repair(config_file: str) -> bool:
    return (True, "")


def do_get_snapshots() -> Tuple[bool,str]:
    params = read_params()
    rootfs = params['rootfs']
    snap_res = list_snaps(rootfs)
    logging.debug("snap_res: {}".format(snap_res))
    if snap_res[0] != 0: return (False, "Error listing filesystem {} snapshots.".format(rootfs)+ str(snap_res[1][0]))
    snaps = [s[s.index(b"@"):] for s in snap_res[1]] #[str(s)[str(s).index("@"):] for s in snap_res[1]]
    return (True, snaps)


def do_get_users() -> List[str]:
    db = open_db()
    logging.debug(db.dgetall('users'))
    return list(db.dgetall('users').keys())



def do_get_user(login: str) -> Optional[UserInDB]:
    db = open_db()
    try:
        return db.dget('users',login)
    except:
        return None


def do_create_user(user_in: UserIn) -> Tuple[bool, Optional[UserInDB]]:
    #return UserInDB(**user_in.dict(), hashed_password='lskjhdlhw')
    logging.debug("do_create_user: {}".format(user_in))
    params = read_params()
    db = open_db()
    users = db.get('users')
    if user_in.username in users:
        return (False, "User {} already exists".format(user_in.username))
    user = UserInDB(**user_in.dict(), hashed_password=user_in.password)

    homes = params['homes']
    owner = params['uowner']
    owner_uid = pwd.getpwnam(owner).pw_uid
    config = do_get_config()['config']
    logging.debug("config : {}".format(config))
    filesystems = config['filesystems']
    logging.debug("Filesystems = {}".format(filesystems))
    for fs in filesystems:
        fs_obj = FileSystem(**fs)
        if fs_obj.fstype == "udirs":
            userdir = pathlib.Path(fs_obj.mountpoint) / homes / user_in.username
            if not userdir.exists():
                logging.debug("Creating userdir: {}".format(userdir))
                os.mkdir(userdir, 0o755)
                os.chown(userdir, owner_uid,0)
            else: 
                return (False, 
                    "Homedir for user {} already exists! "+
                    "Retry creating user after moving or deleting the directory.".format(user.username))
            for udir in fs_obj.dirs:
                dirpath = userdir / udir
                os.mkdir(dirpath, 0o755)
                os.chown(dirpath, owner_uid,0)
    db.dadd('users', (user.username,user.__dict__))
    return (True,user)

def do_get_snapshot(snapshot: str) -> Tuple[bool, Union[SnapshotModel,str]]:
    params = read_params()
    rootfs = params['rootfs']
    (res, detail) = list_snap(rootfs+snapshot)
    if res:
        logging.debug("list snap returned {}".format(detail))
        return (True, get_snapshot(snapshot, detail))
    else: return (False, detail)
    

def do_create_snapshot(snapshot: str) -> bool:
    params = read_params()
    rootfs = params['rootfs']
    res = recursive_snaps(rootfs, snapshot)
    if res[0] != 0:
        logging.info("Create snapshot failed: {}".format(res[1]))
        return False
    return True

def build_reverse_dir_map() -> Dict[str,FileModel]:
    config = do_get_config()['config']
    filesystems = config['filesystems']
    rmap = dict()
    for fs in filesystems:
        fs_obj = FileSystem(**fs)
        if fs_obj.fstype != "udirs": continue
        for udir in fs_obj.dirs:
            rmap[udir] = fs_obj.mountpoint
    return rmap   

def build_file_response(
    path_in_snap: pathlib.Path(), fpath: str, snapshot: str, 
    username: str, iparams: Dict[str,Any]
    ) -> Tuple[bool, Union[FileModel,str]]:

    params = read_params() if iparams == None else iparams
    logging.debug("looking for file in '{}'...".format(path_in_snap))
    try:
        stat = os.stat(path_in_snap)
    except:
        return (False, "File not found.")
    uid = stat[ST_UID]
    login = pwd.getpwuid(uid).pw_name
    if login == params['uowner']: s_user = username
    else: s_user = login
    mode = stat[ST_MODE]
    ftype = FileType.SPECIAL
    if S_ISDIR(mode):
        ftype = FileType.DIRECTORY
    if S_ISREG(mode):
        ftype = FileType.FILE
    if S_ISLNK(mode):
        ftype = FileType.SYMLINK
    (res, snap_obj )= do_get_snapshot(snapshot)
    if not res : return (res, snap_obj)

    return (True, FileModel(
        name = os.path.basename(fpath), 
        owner = s_user, 
        path = os.path.dirname(fpath) +'/', 
        size = stat[ST_SIZE],
        perm = filemode(mode),
        ftype = ftype,
        snap = snap_obj ))

def build_dir_response(
    path_in_snap: pathlib.Path(), fpath: str, snapshot: str, 
    username: str, iparams: Dict[str,Any]
    ) -> Tuple[bool, Union[DirectoryModel,str]]:

    params = read_params() if iparams == None else iparams
    if not path_in_snap.is_dir():
        return (False, "Not a directory.")

    (res, snap_obj )= do_get_snapshot(snapshot)
    if not res : return (res, snap_obj)

    content : List[FileModel] = list()
    for direlem in path_in_snap.iterdir():
        logging.debug("direlem: {}".format(direlem))
    
        try:
            stat = os.stat(direlem)
        except:
            return (False, "File not found.")
        uid = stat[ST_UID]
        login = pwd.getpwuid(uid).pw_name
        if login == params['uowner']: s_user = username
        else: s_user = login
        mode = stat[ST_MODE]
        ftype = FileType.SPECIAL
        if S_ISDIR(mode):
            ftype = FileType.DIRECTORY
        if S_ISREG(mode):
            ftype = FileType.FILE
        if S_ISLNK(mode):
            ftype = FileType.SYMLINK
        
        content.append(FileModel(
            name = os.path.basename(direlem), 
            owner = s_user, 
            path = fpath +'/', 
            size = stat[ST_SIZE],
            perm = filemode(mode),
            ftype = ftype,
            snap = snap_obj )
        )

    """ parent = path_in_snap.parent
    try:
        stat = os.stat(parent)
    except:
        return (False, "Parent dir not found.")
    uid = stat[ST_UID]
    login = pwd.getpwuid(uid).pw_name
    if login == params['uowner']: s_user = username
    else: s_user = login
    mode = stat[ST_MODE]
    ftype = FileType.SPECIAL
    if S_ISDIR(mode):
        ftype = FileType.DIRECTORY
    if S_ISREG(mode):
        ftype = FileType.FILE
    if S_ISLNK(mode):
        ftype = FileType.SYMLINK """
    
    (res,detail) = do_get_file_at_path(fpath, snapshot, username, False)
    if not res: return (res,detail)

    return (True, DirectoryModel(
        **detail.__dict__,
        files = content
        ))


def fake_root_as_file(snap:str) -> FileModel:
    params = read_params()

    rootfs = pathlib.Path('/'+params['rootfs'])
    rootstat = rootfs.stat()
    return FileModel(
        name = "",
        path = "/",
        size = rootstat.st_size,
        perm = filemode(rootstat.st_mode),
        ftype = FileType.DIRECTORY,
        snap = SnapshotModel(
            name = snap,
            date = rootstat.st_ctime
        ),
        owner = pwd.getpwuid(rootstat.st_uid).pw_name
    )

def fake_root_as_dir(snap:str) -> DirectoryModel:
    params = read_params()
    config = do_get_config()['config']

    root_file_model = fake_root_as_file(snap)
    content: List[FileModel] = []
    for fs in config['filesystems']:
        dir_sep_pos = fs['name'].rfind('/')
        (res, file_model) = do_get_file_at_path(fs['name'][dir_sep_pos+1:], snap, params['admin'])
        if not res: logging.error("fake_root_as_dir error: {} ".format(file_model))
        content.append(file_model)
    
    return DirectoryModel(
        **root_file_model.__dict__,
        files = content
    )

def do_get_file_at_path(fpath: str, snapshot:str, username: str,
    dir_result: bool = False) -> Tuple[bool, Union[FileModel,DirectoryModel,str]]:
    params = read_params()
    s_rootfs = '/' + params['rootfs']
    homedir = params['homedir']
    path_in_snap = None
    if username == params['admin']:
        logging.debug("fpath={}".format(fpath))
        ## Root sees files from rootfs, ie. /rpool/shared, but snapshots are at fs level
        if fpath == "":
            if dir_result: return (True, fake_root_as_dir(snapshot))
            return (True,fake_root_as_file(snapshot))
        dir_sep_pos = fpath.find('/')
        if dir_sep_pos == -1: 
            fpath_right = ""
            fpath_left = fpath
        else: 
            fpath_right =  fpath[dir_sep_pos+1:]
            fpath_left = fpath[:dir_sep_pos+1]

        path_in_snap = pathlib.Path(s_rootfs) / fpath_left / '.zfs' / 'snapshot' / snapshot[1:] 
        if fpath_right != "":
            path_in_snap = path_in_snap / fpath_right
        logging.debug("path_in_snap ={}".format(str(path_in_snap)))
        ## The owner of a file owned by www-data in /rpool/shared/hf-1/home/<user> is <user>  
        owner = "root"  ## FIX ME
    else:
        dir_sep_pos = fpath.find('/')
        if dir_sep_pos != -1:
            ## given path is compound, we extract the 1st level directory part
            dirname = fpath[:dir_sep_pos]
            ## Resolve in which fs the file is located
            ## If rmap does not find it, then it belongs to user's homedir fs (eg. hf-1)
            rmap = build_reverse_dir_map()
            fspath = rmap.get(dirname, s_rootfs + '/' + homedir)
        else:
            ## If given path is not compound, then it is a file located in user's homedir
            fspath = s_rootfs + '/' + homedir
    
        s_homedir = params['homes'] + '/' + username

        ## Navigate in requested snapshot
        path_in_snap = pathlib.Path(fspath) / '.zfs' / 'snapshot' / snapshot[1:]
        path_in_snap = path_in_snap / s_homedir / fpath
    if dir_result:
        return build_dir_response(path_in_snap, fpath, snapshot, username, params)
    else:
        return build_file_response(path_in_snap, fpath, snapshot, username, params)
        


