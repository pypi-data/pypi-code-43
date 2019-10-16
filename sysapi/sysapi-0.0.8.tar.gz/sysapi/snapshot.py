from typing import List, Optional
from pydantic import BaseModel, FilePath
from datetime import datetime, timedelta

class SnapshotModel(BaseModel):
    name: str
    # path: FilePath = None
    # TODO: For early dev, deactivate path testing
    path: str
    date: datetime


## TODO: Move this to unit tests...
test_snapshots = [ ]

deltas = [timedelta(days=365), timedelta(days=4), timedelta(hours=6), timedelta(minutes=45), timedelta(minutes=0)]
date_ref = datetime.now()

for i, s in enumerate(['@initial', '@first', '@second', '@third','@current']):
    test_snapshots.append(SnapshotModel(name=s, path='zpool/shared/filesystem'+s, date=date_ref-deltas[i] ))



def get_snapshots() -> List[str]:
    return [s.name for s in test_snapshots]

def get_snapshot(snapshot: str)-> Optional[SnapshotModel]:
    return next((s for s in test_snapshots if s.name == snapshot), None)