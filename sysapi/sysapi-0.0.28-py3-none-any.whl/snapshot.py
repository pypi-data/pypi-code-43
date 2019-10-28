from typing import List, Optional, Tuple, Union, Dict, Any
from pydantic import BaseModel, FilePath
from datetime import datetime, timedelta, timezone
from sysapi.env import read_params
import subprocess, logging
import pathlib

SnapshotsRes = Tuple[int, List[str]]
CmdRes = Tuple[int, str]
SnapRes = 'Tuple[bool, Union[str,SnapshotModel]]'

LISTSNAPS_CMD = "/sbin/zfs list -H -t snapshot -r -o name -s creation".split()
RECSNAP_CMD = "/sbin/zfs snap -o inspeere.com:source=api -r ".split()
SINGLESNAP_CMD = "/sbin/zfs snap -o inspeere.com:source=api ".split()
LIST_SNAP_CMD = "/sbin/zfs list -H -p -t snap -r -o name,creation -s creation".split()



def list_snaps(fsname: str) -> SnapshotsRes:
    logging.debug("Listing snapshots for fs='{}".format(fsname))
    try:
        cp = subprocess.run(LISTSNAPS_CMD + list([fsname]), capture_output=True)
    except Exception as inst:
        logging.debug("list_snaps command failed with exception {}".format(inst))
    if cp.returncode == 0:
        logging.debug("list_snaps command: ok.")
        return (0, cp.stdout.split())
    else: 
        logging.debug("Snap error {}: {}".format(cp.returncode,cp.stderr))
        return (cp.returncode, [cp.stderr])

def recursive_snaps(fsname: str, snapname: str) -> CmdRes:
    cp = subprocess.run(RECSNAP_CMD + list([fsname+snapname]), capture_output=True)
    logging.debug("recursive_snaps(fsname={}, snapname={} -> out={}, err={})".format(fsname,snapname,cp.stdout, cp.stderr))
    if cp.returncode == 0: return (0, "")
    else: return (cp.returncode, cp.stderr)

def single_snap(fsname: str, snapname: str) -> CmdRes:
    cp = subprocess.run(SINGLESNAP_CMD + list([fsname+snapname]), capture_output=True)
    logging.debug("single_snap(fsname={}, snapname={} -> out={}, err={})".format(fsname,snapname,cp.stdout, cp.stderr))
    if cp.returncode == 0: return (0, "")
    else: return (cp.returncode, cp.stderr)

def list_snap(fsname: str = None) -> SnapRes:
    cmd = LIST_SNAP_CMD
    if not fsname is None:
        cmd = cmd + list([fsname])
    cp = subprocess.run(cmd, capture_output=True)
    logging.debug("list_snap returned {}".format(cp.stdout))
    if cp.returncode == 0: 
        logging.debug("Stdout len = {}".format(len(cp.stdout)))
        if len(cp.stdout) ==0:
            return (False, "Snapshot not found.")
        return (True, cp.stdout.split())
    else:
        logging.debug("list snap command failed:"+str(cp.stderr))  
        return (False, "Snapshot not found.")



class SnapshotModel(BaseModel):
    suffix: str
    filesystem: str
    # path: FilePath = None
    # TODO: For early dev, deactivate path testing
    date: datetime

    @classmethod
    def lookup_snapshot(cls, snapsuffix: str, rel_path_in_snap: str , config: Dict[str,Any]):
        for fs in config['filesystems']:
            if fs['fstype'] == 'uroot': continue
            fullpath = pathlib.Path(fs['mountpoint']) / '.zfs' / 'snapshot' / rel_path_in_snap
            logging.debug("Lookup: testing fullpath={} (mp={})".format(fullpath, fs['mountpoint']))
            try:
                if fullpath.exists():
                    try:
                        return cls.get_snapshot(fs['name']+ snapsuffix)
                    except Exception as inst:
                        print("exception: {}".format(inst))
            except: pass
   
        return (False, "Unable to find snapshot named {} for file {}".format(snapsuffix,rel_path_in_snap))


    @classmethod
    def get_snapshot(cls, name: str):
        #params = read_params()
        #rootfs = params['rootfs']
   
        (res, detail) = list_snap(name)
        if res:
            logging.debug("get_snapshot: list snap returned {}".format(detail))   
            parts = detail[0].partition(b'@')
            logging.debug("parts = {}".format(parts))
            return (True, cls(    
                suffix=parts[1]+parts[2],
                filesystem=parts[0],
                date=datetime.fromtimestamp(int(detail[1]), timezone.utc)))
        else: return (False, detail)
