
from radware.sdk.beans_common import *


class EnumSlbOperGroupRealState(BaseBeanEnum):
    enable = 1
    disable = 2
    shutdown_connection = 3
    shutdown_persistent_sessions = 4


class EnumSlbOperGroupRealStatus(BaseBeanEnum):
    enable = 1
    disable = 2
    shutdown_connection = 3
    shutdown_persistent_sessions = 4


class EnumSlbOperGroupRealRuntimeStatus(BaseBeanEnum):
    running = 1
    failed = 2
    disabled = 3
    overloaded = 4


class SlbOperEnhGroupRealServerTable(DeviceBean):
    def __init__(self, **kwargs):
        self.RealServGroupIndex = kwargs.get('RealServGroupIndex', None)
        self.ServIndex = kwargs.get('ServIndex', None)
        self.State = EnumSlbOperGroupRealState.enum(kwargs.get('State', None))
        self.Status = EnumSlbOperGroupRealStatus.enum(kwargs.get('Status', None))
        self.IP = kwargs.get('IP', None)
        self.Descr = kwargs.get('Descr', None)
        self.RuntimeStatus = EnumSlbOperGroupRealRuntimeStatus.enum(kwargs.get('RuntimeStatus', None))

    def get_indexes(self):
        return self.RealServGroupIndex, self.ServIndex,
    
    @classmethod
    def get_index_names(cls):
        return 'RealServGroupIndex', 'ServIndex',

