
from __future__ import annotations

import peewee

from healer.persist.arkon import ServerModel


class Message(ServerModel):
    id = peewee.AutoField()
    entry_list = peewee.IntegerField()
