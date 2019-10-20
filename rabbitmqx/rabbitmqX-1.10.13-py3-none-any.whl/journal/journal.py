import time
from enum import Enum

class Journal (object):
    def __init__(self, id, type, data, action):
        self.type = type
        self.id = id
        self.datatime = time.time()
        self.action = action
        self.data = data

class Action(str,Enum):
    CREATE = 'create'
    DELETE = 'delete'
    UPDATE = 'update'