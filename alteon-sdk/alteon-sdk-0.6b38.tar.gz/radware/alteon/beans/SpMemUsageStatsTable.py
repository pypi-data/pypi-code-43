
from radware.sdk.beans_common import *


class SpMemUsageStatsTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Index = kwargs.get('Index', None)
        self.CurrentMemory = kwargs.get('CurrentMemory', None)
        self.HiWaterMark = kwargs.get('HiWaterMark', None)
        self.MaxMemory = kwargs.get('MaxMemory', None)

    def get_indexes(self):
        return self.Index,
    
    @classmethod
    def get_index_names(cls):
        return 'Index',

