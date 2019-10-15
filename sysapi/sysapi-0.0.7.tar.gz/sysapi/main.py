from typing import Union, List
from fastapi import FastAPI, Path, HTTPException
from sysapi.backend import * #do_get_user, do_get_users, do_get_snapshots, do_get_snapshot, do_create_user, do_setup, do_repair
from sysapi.user import UserIn, UserOut
from sysapi.snapshot import SnapshotModel
from sysapi.file import FileModel, DirectoryModel
from pydantic import BaseModel
from pydantic.types import DirectoryPath, FilePath, errors, path_validator, path_exists_validator
from pathlib import Path as PathlibPath
import sys, os



app = FastAPI()

CONFIG_FILE="./config.json"
BACKVERSION="0.0.7rc"

config_file = CONFIG_FILE
#if len(sys.argv) > 1:
#    config_file = sys.argv[1]



## Relaxed path validation for devel
class UnboundFilePath(PathlibPath):
    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':
        yield path_validator
        #yield path_exists_validator
        yield cls.validate

    @classmethod
    def validate(cls, value: Path) -> Path:
        #if not value.is_file():
        #    raise errors.PathNotAFileError(path=value)

        return value


APIVERSION="v1"

@app.get("/")
def read_root():
    return {"service": "sysapi", "api-version": APIVERSION, "backend": BACKVERSION}

@app.get("/v1/users")
def get_users():
    return {"users": do_get_users()}

@app.get("/v1/config")
def get_config():
    return do_get_config(config_file)
    

@app.post("/v1/config/setup")
def setup_config() -> bool:
    (res, detail) = do_setup(config_file)
    if not res: raise HTTPException(status_code=409, detail=detail)
    return res


@app.get("/v1/user/{username}", response_model=UserOut)
def get_user(username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")) :
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    return user

@app.post("/v1/users/new", response_model=UserOut)
async def create_user(*, user_in: UserIn):
    new_user = do_create_user(user_in)
    return user_in
    #if new_user is not None: return new_user
    ## raise HTTPException(status_code=404, detail="User creation failed.")

@app.get("/v1/snapshots")
def get_snapshots():
    return {"snapshots": do_get_snapshots()}


@app.get("/v1/snapshot/{snapshot}", response_model=SnapshotModel)
def get_snapshot(snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$")) :
    if snapshot in do_get_snapshots():
        return do_get_snapshot(snapshot)
    else:
        raise HTTPException(status_code=404, detail="Snapshot unknown")

@app.get("/v1/fat/{snapshot}/{username}/{path:path}", response_model=FileModel)
def get_file_at_path(
    path: str = Path(None, regex='^.*[^/]$'),
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> FileModel:
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    snap = do_get_snapshot(snapshot)
    if snap is None: HTTPException(status_code=404, detail="Snapshot unknown")
    from sysapi.file import fake_file
    return fake_file

@app.get("/v1/dat/{snapshot}/{username}/{path:path}/", response_model=DirectoryModel)
def get_dir_at_path(
    path: str = Path(None, regex='^.*[^/]$'),
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> DirectoryModel:
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    snap = do_get_snapshot(snapshot)
    if snap is None: HTTPException(status_code=404, detail="Snapshot unknown")
    from sysapi.file import fake_dir
    return fake_dir

@app.get("/v1/fbefore/{snapshot}/{username}/{path:path}", response_model=FileModel)
def get_file_before_path(
    path: str = Path(None, regex='^.*[^/]$'),
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> FileModel:
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    snap = do_get_snapshot(snapshot)
    if snap is None: HTTPException(status_code=404, detail="Snapshot unknown")
    from sysapi.file import fake_file
    return fake_file

@app.get("/v1/dbefore/{snapshot}/{username}/{path:path}/", response_model=DirectoryModel)
def get_dir_before_path(
    path: str = Path(None, regex='^.*[^/]$'),
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> DirectoryModel:
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    snap = do_get_snapshot(snapshot)
    if snap is None: HTTPException(status_code=404, detail="Snapshot unknown")
    from sysapi.file import fake_dir
    return fake_dir

@app.get("/v1/historic/{username}/{path:path}", response_model=List[SnapshotModel])
def get_historic_path(
    path: str = Path(None),
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> List[SnapshotModel]:
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    return get_snapshots()


@app.get("/v1/past/{snapshot}/{username}/{path:path}", response_model=DirectoryModel)
def get_file_past_path(
    path: str = Path(None, regex='^.*[^/]$'),
    snapshot: str = Path(...,min_length=1, regex="^@[a-zA-Z0-9-_']+$"), 
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> FileModel:
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    snap = do_get_snapshot(snapshot)
    if snap is None: HTTPException(status_code=404, detail="Snapshot unknown")
    from sysapi.file import fake_dir
    return fake_dir

@app.post("/v1/copyto/{username}/{path:path}/", response_model=DirectoryModel)
def post_copy_to(
    files: List[FileModel],
    path: str = Path(None, regex='^.*[^/]$'),
    username: str = Path(...,min_length=1, regex="^[a-zA-Z'][a-zA-Z0-9-_']*$")
    ) -> DirectoryModel:
    user = do_get_user(username)
    if user is None: raise HTTPException(status_code=404, detail="User unknown")
    from sysapi.file import fake_dir
    return fake_dir