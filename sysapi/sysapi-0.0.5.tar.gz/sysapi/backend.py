from typing import List, Optional
from sysapi.user import get_user, get_users, create_user, UserOut, UserIn, UserInDB
from sysapi.snapshot import SnapshotModel, get_snapshots, get_snapshot
# from pyzfs import 

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