
from radware.sdk.beans_common import *


class EnumPortOperRmon(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumPortOperState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class AgPortOperTable(DeviceBean):
    def __init__(self, **kwargs):
        self.portOperIdx = kwargs.get('portOperIdx', None)
        self.portOperRmon = EnumPortOperRmon.enum(kwargs.get('portOperRmon', None))
        self.portOperState = EnumPortOperState.enum(kwargs.get('portOperState', None))

    def get_indexes(self):
        return self.portOperIdx,
    
    @classmethod
    def get_index_names(cls):
        return 'portOperIdx',

