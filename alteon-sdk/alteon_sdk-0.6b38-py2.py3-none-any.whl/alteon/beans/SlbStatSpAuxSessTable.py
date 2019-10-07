
from radware.sdk.beans_common import *


class SlbStatSpAuxSessTable(DeviceBean):
    def __init__(self, **kwargs):
        self.SpIndex = kwargs.get('SpIndex', None)
        self.Index = kwargs.get('Index', None)
        self.CurConn = kwargs.get('CurConn', None)
        self.MaxConn = kwargs.get('MaxConn', None)
        self.AllocFails = kwargs.get('AllocFails', None)

    def get_indexes(self):
        return self.SpIndex, self.Index,
    
    @classmethod
    def get_index_names(cls):
        return 'SpIndex', 'Index',

