
from radware.sdk.beans_common import *


class EnumSlbPortInfoClientState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoSerState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoFltState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoRTSState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoHotStandbyState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoInterSWState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoProxyState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoIdSlbState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbPortInfoSymantecState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class SlbPortInfoTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Index = kwargs.get('Index', None)
        self.ClientState = EnumSlbPortInfoClientState.enum(kwargs.get('ClientState', None))
        self.SerState = EnumSlbPortInfoSerState.enum(kwargs.get('SerState', None))
        self.FltState = EnumSlbPortInfoFltState.enum(kwargs.get('FltState', None))
        self.RTSState = EnumSlbPortInfoRTSState.enum(kwargs.get('RTSState', None))
        self.HotStandbyState = EnumSlbPortInfoHotStandbyState.enum(kwargs.get('HotStandbyState', None))
        self.InterSWState = EnumSlbPortInfoInterSWState.enum(kwargs.get('InterSWState', None))
        self.ProxyState = EnumSlbPortInfoProxyState.enum(kwargs.get('ProxyState', None))
        self.IdSlbState = EnumSlbPortInfoIdSlbState.enum(kwargs.get('IdSlbState', None))
        self.SymantecState = EnumSlbPortInfoSymantecState.enum(kwargs.get('SymantecState', None))
        self.FitersAdded = kwargs.get('FitersAdded', None)

    def get_indexes(self):
        return self.Index,
    
    @classmethod
    def get_index_names(cls):
        return 'Index',

