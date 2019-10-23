from typing import List, Optional, Tuple, Union
from pydantic import BaseModel, FilePath
from datetime import datetime, timedelta, timezone
from sysapi.env import read_params
import subprocess, logging

SnapshotsRes = Tuple[int, List[str]]
CmdRes = Tuple[int, str]
SnapRes = 'Tuple[bool, Union[str,SnapshotModel]]'

LISTSNAPS_CMD = "/sbin/zfs list -H -t snapshot -o name -s creation".split()
RECSNAP_CMD = "/sbin/zfs snap -o inspeere.com:source=api -r ".split()
LIST_SNAP_CMD = "/sbin/zfs list -H -p -t snap -o name,creation -s creation".split()


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



class SnapshotModel(BaseModel):
    name: str
    # path: FilePath = None
    # TODO: For early dev, deactivate path testing
    date: datetime

    @classmethod
    def get_snapshot(cls, name: str):
        params = read_params()
        rootfs = params['rootfs']
        (res, detail) = list_snap(rootfs+name)
        if res:
            logging.debug("list snap returned {}".format(detail))
            return (True, cls(    
                name=name,
                date=datetime.fromtimestamp(int(detail[1]), timezone.utc)))
        else: return (False, detail)
