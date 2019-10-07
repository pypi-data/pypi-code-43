
from radware.sdk.beans_common import *


class EnumSlbRealServerSecondPartProxy(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbRealServerSecondPartLdapwr(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbRealServerSecondPartFastHealthCheck(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbRealServerSecondPartSubdmac(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbRealServerSecondPartOverflow(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbRealServerSecondPartBkpPreempt(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumSlbRealServerSecondPartMode(BaseBeanEnum):
    physical = 1
    logical = 2


class EnumSlbRealServerSecondPartUpdateAllRealServers(BaseBeanEnum):
    none = 0
    mode = 1
    maxcon = 2
    weight = 3
    all = 4


class EnumSlbRealServerSecondPartProxyIpMode(BaseBeanEnum):
    enable = 0
    address = 2
    nwclss = 3
    disable = 4


class EnumSlbRealServerSecondPartProxyIpPersistency(BaseBeanEnum):
    disable = 0
    client = 1
    host = 2


class EnumSlbRealServerSecondPartProxyIpNWclassPersistency(BaseBeanEnum):
    disable = 0
    client = 1


class SlbNewCfgEnhRealServerSecondPartTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Index = kwargs.get('Index', None)
        self.UrlBmap = kwargs.get('UrlBmap', None)
        self.Proxy = EnumSlbRealServerSecondPartProxy.enum(kwargs.get('Proxy', None))
        self.Ldapwr = EnumSlbRealServerSecondPartLdapwr.enum(kwargs.get('Ldapwr', None))
        self.Idsvlan = kwargs.get('Idsvlan', None)
        self.Avail = kwargs.get('Avail', None)
        self.FastHealthCheck = EnumSlbRealServerSecondPartFastHealthCheck.enum(kwargs.get('FastHealthCheck', None))
        self.Subdmac = EnumSlbRealServerSecondPartSubdmac.enum(kwargs.get('Subdmac', None))
        self.Overflow = EnumSlbRealServerSecondPartOverflow.enum(kwargs.get('Overflow', None))
        self.BkpPreempt = EnumSlbRealServerSecondPartBkpPreempt.enum(kwargs.get('BkpPreempt', None))
        self.Mode = EnumSlbRealServerSecondPartMode.enum(kwargs.get('Mode', None))
        self.UpdateAllRealServers = EnumSlbRealServerSecondPartUpdateAllRealServers.enum(kwargs.get('UpdateAllRealServers', None))
        self.ProxyIpMode = EnumSlbRealServerSecondPartProxyIpMode.enum(kwargs.get('ProxyIpMode', None))
        self.ProxyIpAddr = kwargs.get('ProxyIpAddr', None)
        self.ProxyIpMask = kwargs.get('ProxyIpMask', None)
        self.ProxyIpv6Addr = kwargs.get('ProxyIpv6Addr', None)
        self.ProxyIpv6Prefix = kwargs.get('ProxyIpv6Prefix', None)
        self.ProxyIpPersistency = EnumSlbRealServerSecondPartProxyIpPersistency.enum(kwargs.get('ProxyIpPersistency', None))
        self.ProxyIpNWclass = kwargs.get('ProxyIpNWclass', None)
        self.ProxyIpNWclassPersistency = EnumSlbRealServerSecondPartProxyIpNWclassPersistency.enum(kwargs.get('ProxyIpNWclassPersistency', None))

    def get_indexes(self):
        return self.Index,
    
    @classmethod
    def get_index_names(cls):
        return 'Index',

