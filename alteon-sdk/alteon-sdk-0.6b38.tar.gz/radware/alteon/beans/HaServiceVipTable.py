
from radware.sdk.beans_common import *


class HaServiceVipTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Index = kwargs.get('Index', None)
        self.VipIndex = kwargs.get('VipIndex', None)

    def get_indexes(self):
        return self.Index, self.VipIndex,
    
    @classmethod
    def get_index_names(cls):
        return 'Index', 'VipIndex',

