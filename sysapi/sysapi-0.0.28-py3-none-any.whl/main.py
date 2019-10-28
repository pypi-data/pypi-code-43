from typing import Union, List
from fastapi import FastAPI, Path, HTTPException
from sysapi.backend import * #do_get_user, do_get_users, do_get_snapshots, do_get_snapshot, do_create_user, do_setup, do_repair
from sysapi.user import UserIn, UserOut
from sysapi.snapshot import SnapshotModel
from sysapi.file import FileModel, DirectoryModel
from sysapi.preptest import do_prepare_test
from pydantic import BaseModel
from pydantic.types import DirectoryPath, FilePath, errors, path_validator, path_exists_validator
from pathlib import Path as PathlibPath
import sys, os



app = FastAPI()

CONFIG_FILE="/etc/safer/config.json"
BACKVERSION="0.0.28"

config_file = CONFIG_FILE
#if len(sys.argv) > 1:
#    config_file = sys.argv[1]


db = open_db()

APIVERSION="v1"

@app.get("/")
def read_root():
    return {"service": "sysapi", "api-version": APIVERSION, "backend": BACKVERSION}

@app.get("/v1/installed")
def get_installed():
    return do_get_installed()

@app.get("/v1/danger/reset")
def get_reset_warning_DANGEROUS(*,resetkey: str) -> bool:
    if do_reset(resetkey): return True
    else: raise HTTPException(status_code=404, detail="Permission denied")
    return False

@app.get("/v1/test/prepare")
def prepare_test(*,resetkey: str, testname: str = "test1") -> List[Union[int,str]]:
    return do_prepare_test(resetkey, testname)

@app.get("/v1/config")
def get_config():
    config = do_get_config()
    return config
    

@app.post("/v1/config/setup")
def setup_config() -> bool:
    (res, detail) = do_setup(config_file)
    if not res: raise HTTPException(status_code=409, detail=detail)
    return res

@app.get("/v1/users")
def get_users():
    return {"users": do_get_users()}

@app.get("/v1/user/{username}", response_model=UserOut)
def get_user(username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")) :
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    return user

@app.post("/v1/users/new", response_model=UserOut)
def create_user(*, user_in: UserIn):
    new_user = do_create_user(user_in)
    return user_in
    #if new_user is not None: return new_user
    ## raise HTTPException(status_code=404, detail="User creation failed.")

@app.get("/v1/snapshots")
def get_snapshots_merged():
    do_current_snapshot()
    (res, detail) = do_get_snapshots()
    if not res: raise HTTPException(status_code=409, detail=detail)
    return {"snapshots": detail}


@app.get("/v1/snapshots/{filesystem:path}")
def get_snapshots_singlefs(filesystem: str = Path(..., min_length=1, regex="^[^/@][^@]*$")):
    do_current_snapshot()
    (res, detail) = do_get_snapshots(filesystem)
    if not res: raise HTTPException(status_code=409, detail=detail)
    return {"snapshots": detail}



@app.get("/v1/snapshot/{snapshot:path}", response_model=SnapshotModel)
def get_snapshot(snapshot: str = Path(...,min_length=1, regex="^[^/@][^@]*@[^@]+$")) -> SnapshotModel:
    (res,snaps) = do_get_snapshots()
    if not res: raise HTTPException(status_code=409, detail=snaps)
    logging.debug("snaps = {}".format(snaps))
    if bytes(snapshot, 'utf-8') in snaps:
        (res, detail) = do_get_snapshot(snapshot)
        if res: return detail
        else: raise  HTTPException(status_code=404, detail=detail)
    else: raise HTTPException(status_code=404, detail="Snapshot unknown")

@app.post("/v1/snapshot/{snapshot}")
def create_snapshot(snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$")) -> Tuple[bool,str]:
    return do_create_snapshot(snapshot)

@app.post("/v1/snapshot/{snapshot}/{filesystem:path}")
def create_snapshot(
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"),
    filesystem: str = Path(..., min_length=1, regex="^[^/@][^@]*$")) -> Tuple[bool,str]:
    return do_create_snapshot(snapshot, filesystem)



@app.get("/v1/fat/{snapshot}/{username}/{path:path}", response_model=FileModel)
def get_file_at_path(
    path: Optional[str] = ".",
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> FileModel:
    params = read_params()
    if username != params['admin']:
        user = do_get_user(username)
        if user is None: raise HTTPException(status_code=404, detail="User unknown")
    do_current_snapshot()
    #(res, snap) = do_get_snapshot(snapshot)
    #if not res: raise HTTPException(status_code=404, detail="Snapshot unknown")
    (res, detail) = do_get_file_at_path(path, snapshot, username)
    logging.debug("do_get_file_at_path() returned {}:{}".format(res,detail))
    if res: return detail
    raise HTTPException(status_code=404, detail=detail)
    

@app.get("/v1/dat/{snapshot}/{username}/{path:path}", response_model=DirectoryModel)
def get_dir_at_path(
    path: Optional[str] = ".",
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> DirectoryModel:
    logging.debug("path={}".format(path))
    params = read_params()
    if username != params['admin']:
        user = do_get_user(username)
        if user is None: raise HTTPException(status_code=404, detail="User unknown")
    do_current_snapshot()
    #(res, snap) = do_get_snapshot(snapshot)
    #if not res: raise HTTPException(status_code=404, detail="Snapshot unknown")
    (res, detail) = do_get_file_at_path(path, snapshot, username, True)
    if res: return detail
    raise HTTPException(status_code=404, detail=detail)

@app.get("/v1/historic/{username}/{path:path}", response_model=List[SnapshotModel])
def get_historic_path(
    path: str = Path(None),
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> List[SnapshotModel]:
    params = read_params()
    if username != params['admin']:
        user = do_get_user(username)
        if user is None: raise HTTPException(status_code=404, detail="User unknown")
    do_current_snapshot()
    (res, detail) = do_get_historic(path, username)
    if not res: raise HTTPException(status_code=409, detail=detail)
    return detail


@app.get("/v1/past/{snapshot}/{username}/{path:path}", response_model=DirectoryModel)
def get_file_past_path(
    path: Optional[str] = ".",
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> DirectoryModel:
    params = read_params()
    if username != params['admin']:
        user = do_get_user(username)
        if user is None: raise HTTPException(status_code=404, detail="User unknown")
    #snap = do_get_snapshot(snapshot)
    #if snap is None: HTTPException(status_code=404, detail="Snapshot unknown")
    do_current_snapshot()
    (res, detail) = do_get_past(path, snapshot, username)
    if not res: raise HTTPException(status_code=409, detail=detail)
    logging.debug("Returning {} of type {}".format(detail, type(detail)))
    return detail

@app.post("/v1/copy/{snapshot}/{username}/{path:path}", response_model=bool)
def post_copy_to(
    path: Optional[str] = ".",
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$"),
    destructive: bool = False
    ) -> bool:
    params = read_params()
    if username != params['admin']:
        user = do_get_user(username)
        if user is None: raise HTTPException(status_code=404, detail="User unknown")
    do_current_snapshot()
    #snap = do_get_snapshot(snapshot)
    #if snap is None: HTTPException(status_code=404, detail="Snapshot unknown")
    (res, detail) = do_copy(path, snapshot, username, destructive)
    if not res: raise HTTPException(status_code=409, detail=detail)
    return True
    