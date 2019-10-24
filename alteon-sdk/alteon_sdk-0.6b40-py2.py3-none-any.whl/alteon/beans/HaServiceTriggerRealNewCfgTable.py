
from radware.sdk.beans_common import *


class EnumHaServiceTriggerRealNewCfgTrigRealTrkState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumHaServiceTriggerRealNewCfgTrigAllRemRealState(BaseBeanEnum):
    aadd = 1
    arem = 2


class EnumHaServiceTriggerRealNewCfgTrigRealTrkAutoOptState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class HaServiceTriggerRealNewCfgTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Index = kwargs.get('Index', None)
        self.NewCfgTrigRealTrkState = EnumHaServiceTriggerRealNewCfgTrigRealTrkState.enum(kwargs.get('NewCfgTrigRealTrkState', None))
        self.NewCfgTrigAllRemRealState = EnumHaServiceTriggerRealNewCfgTrigAllRemRealState.enum(kwargs.get('NewCfgTrigAllRemRealState', None))
        self.NewCfgTrigAddReals = kwargs.get('NewCfgTrigAddReals', None)
        self.NewCfgTrigRemReals = kwargs.get('NewCfgTrigRemReals', None)
        self.NewCfgTrigRealTrkAutoOptState = EnumHaServiceTriggerRealNewCfgTrigRealTrkAutoOptState.enum(kwargs.get('NewCfgTrigRealTrkAutoOptState', None))

    def get_indexes(self):
        return self.Index,
    
    @classmethod
    def get_index_names(cls):
        return 'Index',

