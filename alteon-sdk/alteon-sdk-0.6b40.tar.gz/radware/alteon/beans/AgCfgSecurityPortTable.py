
from radware.sdk.beans_common import *


class EnumAgSecurityPortCurCfgSecurityDosState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumAgSecurityPortNewCfgSecurityDosState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumAgSecurityPortCurCfgSecurityIpAclState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumAgSecurityPortNewCfgSecurityIpAclState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumAgSecurityPortCurCfgSecurityUbState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumAgSecurityPortNewCfgSecurityUbState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumAgSecurityPortCurCfgSecurityBogonState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class EnumAgSecurityPortNewCfgSecurityAddAttack(BaseBeanEnum):
    iplen = 1
    ipversion = 2
    broadcast = 3
    loopback = 4
    land = 5
    ipreserved = 6
    ipttl = 7
    ipprot = 8
    ipoptlen = 9
    fragmoredont = 10
    fragdata = 11
    fragboundary = 12
    fraglast = 13
    fragdontoff = 14
    fragopt = 15
    fragoff = 16
    fragoversize = 17
    tcplen = 18
    tcpportzero = 19
    blat = 20
    tcpreserved = 21
    nullscan = 22
    fullxmasscan = 23
    finscan = 24
    vecnascan = 25
    xmassscan = 26
    synfinscan = 27
    flagabnormal = 28
    syndata = 29
    synfrag = 30
    ftpport = 31
    dnsport = 32
    seqzero = 33
    ackzero = 34
    tcpoptlen = 35
    udplen = 36
    udpportzero = 37
    fraggle = 38
    pepsi = 39
    rc8 = 40
    snmpnull = 41
    icmplen = 42
    smurf = 43
    icmpdata = 44
    icmpoff = 45
    icmptype = 46
    igmplen = 47
    igmpfrag = 48
    igmptype = 49
    arplen = 50
    arpnbcast = 51
    arpnucast = 52
    arpspoof = 53
    garp = 54
    ip6len = 55
    ip6version = 56


class EnumAgSecurityPortNewCfgSecurityRemAttack(BaseBeanEnum):
    iplen = 1
    ipversion = 2
    broadcast = 3
    loopback = 4
    land = 5
    ipreserved = 6
    ipttl = 7
    ipprot = 8
    ipoptlen = 9
    fragmoredont = 10
    fragdata = 11
    fragboundary = 12
    fraglast = 13
    fragdontoff = 14
    fragopt = 15
    fragoff = 16
    fragoversize = 17
    tcplen = 18
    tcpportzero = 19
    blat = 20
    tcpreserved = 21
    nullscan = 22
    fullxmasscan = 23
    finscan = 24
    vecnascan = 25
    xmassscan = 26
    synfinscan = 27
    flagabnormal = 28
    syndata = 29
    synfrag = 30
    ftpport = 31
    dnsport = 32
    seqzero = 33
    ackzero = 34
    tcpoptlen = 35
    udplen = 36
    udpportzero = 37
    fraggle = 38
    pepsi = 39
    rc8 = 40
    snmpnull = 41
    icmplen = 42
    smurf = 43
    icmpdata = 44
    icmpoff = 45
    icmptype = 46
    igmplen = 47
    igmpfrag = 48
    igmptype = 49
    arplen = 50
    arpnbcast = 51
    arpnucast = 52
    arpspoof = 53
    garp = 54
    ip6len = 55
    ip6version = 56


class EnumAgSecurityPortNewCfgSecurityDoSAttacks(BaseBeanEnum):
    ok = 1
    addall = 2
    remall = 3


class EnumAgSecurityPortNewCfgSecurityBogonState(BaseBeanEnum):
    enabled = 1
    disabled = 2


class AgCfgSecurityPortTable(DeviceBean):
    def __init__(self, **kwargs):
        self.Indx = kwargs.get('Indx', None)
        self.CurCfgSecurityDosState = EnumAgSecurityPortCurCfgSecurityDosState.enum(kwargs.get('CurCfgSecurityDosState', None))
        self.NewCfgSecurityDosState = EnumAgSecurityPortNewCfgSecurityDosState.enum(kwargs.get('NewCfgSecurityDosState', None))
        self.CurCfgSecurityIpAclState = EnumAgSecurityPortCurCfgSecurityIpAclState.enum(kwargs.get('CurCfgSecurityIpAclState', None))
        self.NewCfgSecurityIpAclState = EnumAgSecurityPortNewCfgSecurityIpAclState.enum(kwargs.get('NewCfgSecurityIpAclState', None))
        self.CurCfgSecurityUbState = EnumAgSecurityPortCurCfgSecurityUbState.enum(kwargs.get('CurCfgSecurityUbState', None))
        self.NewCfgSecurityUbState = EnumAgSecurityPortNewCfgSecurityUbState.enum(kwargs.get('NewCfgSecurityUbState', None))
        self.CurCfgSecurityBogonState = EnumAgSecurityPortCurCfgSecurityBogonState.enum(kwargs.get('CurCfgSecurityBogonState', None))
        self.CurCfgSecurityAttacksBmap = kwargs.get('CurCfgSecurityAttacksBmap', None)
        self.NewCfgSecurityAttacksBmap = kwargs.get('NewCfgSecurityAttacksBmap', None)
        self.NewCfgSecurityAddAttack = EnumAgSecurityPortNewCfgSecurityAddAttack.enum(kwargs.get('NewCfgSecurityAddAttack', None))
        self.NewCfgSecurityRemAttack = EnumAgSecurityPortNewCfgSecurityRemAttack.enum(kwargs.get('NewCfgSecurityRemAttack', None))
        self.NewCfgSecurityDoSAttacks = EnumAgSecurityPortNewCfgSecurityDoSAttacks.enum(kwargs.get('NewCfgSecurityDoSAttacks', None))
        self.NewCfgSecurityBogonState = EnumAgSecurityPortNewCfgSecurityBogonState.enum(kwargs.get('NewCfgSecurityBogonState', None))

    def get_indexes(self):
        return self.Indx,
    
    @classmethod
    def get_index_names(cls):
        return 'Indx',

