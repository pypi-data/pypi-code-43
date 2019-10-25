#
# Abstractions and routines dealing with Distributed Volumes (Dvols).
#
import re
import os
import time
import types
import string
import logging
import collections

import dgpy.utils
from UserList    import UserList
from conf_file   import ConfigDict, SyntropyValue
from collections import namedtuple, Iterable

#
# Configuration file syntax-validation functions.
#
def _string(v):
    return v and v.strip('"')

def _bool(v):
    return _string(v) in ('true', 'false')

def _number(v):
    return re.match('\s*\d+\s*$', _string(v))

def _ipaddress(v):
    return dgpy.utils.is_valid_ip(_string(v))

def _sbd(v):
    return re.match('/dev/sbd([0-9]|1[0-5])$', _string(v))

def _path(v):
    return os.path.isabs(_string(v))

def _lvmsize(v):
    return re.match(r'^(\d+(?:\.\d+)?)(K|KB|M|MB|G|GB|T|TB|B)?$', _string(v), re.IGNORECASE)

def _snapid(v):
    s = _string(v)
    return s and len(s) == 8 and all(c in string.hexdigits for c in s)

def _csv(v):
    s = _string(v)
    return s and all(map(_string, s.split(',')))


class Dvol(ConfigDict):
    """Class representing a data volume on a running cluster, built from *.dvol file.

    The class contains all configuration file keys as @__dict. It is possible to access the
    configuration file keys as self.<name> where <name> is one of the known keys.

    The following attributes are mapped to the SRN to which this Dvol is attached (via %SRN):
    @service_ip:     service IP
    @tcp_port:       TCP port
    @storage_ip:     (public) storage IP
    @sbd_device:     name of the local sbd device
    @disk:           device path of the storage disk
    @snapshots_disk: device path of the snapshot device
    @site_type:      the local site type
    @stubs:          whether stubs are configured on this site or not
    @vnames:         local list of VM names

    The same list of attributes is available under the subobject @local.
    @remote:         nested %SRN listing the remote SRN configuration
    """
    #--------------------------------------------------------------------------------------------------------------
    # CLASS CONSTANTS
    #--------------------------------------------------------------------------------------------------------------
    # SRN Dvol states
    STATUS = ( "UNKNOWN", "UNSYNCED", "CREATING", "STARTING", "RUNNING", "TEST_FAILOVER", "FAILOVER", "MIGRATING", "MIGRATED", "FAILING_BACK_STOPPING_OLD_MASTER", "CREATE_FAILED", "TEST_FAILOVER_FAILED", "FAILOVER_FAILED", "RESIZING", "DELETING", "STOPPING", "STOPPED", "ERROR" )

    # Site type (CLC, ...)
    PG_SITE_TYPE = ( "MANUAL", "VMWARE", "CLC", "AWS", "AZURE" )

    # Supported Dvol types (COW/COW, ROW/COW)
    TYPE = ( "COW", "ROW", "INVALID" )

    # Guest type (DATA, MACHINE)
    GUEST_TYPE = ( "DATA", "MACHINE" )

    # Dvol leg role
    LEG_ROLE = ( "MASTER_LEG", "REMOTE_LEG" )

    ATTR_MAP = collections.OrderedDict([
        ('dvol_name',                           _string),
        ('type',                                lambda v: v in Dvol.TYPE),
        ('role',                                lambda v: v in Dvol.LEG_ROLE),
        ('state.status',                        lambda v: v in Dvol.STATUS),
        ('state.periodic_resync_enabled',       _bool),
        ('state.periodic_snapshot_enabled',     _bool),
        ('snapshot_period',                     _number),
        ('legless',                             _bool),

        ('ms_ip',                               _ipaddress), # MS service IP
        ('ms_storage_ip',                       _ipaddress),
        ('sbd_ms_disk',                         _string),
        ('ms_sbd_device',                       _sbd),       # /dev/sbdXX on the MS
        ('sbd_ms_snapshots_disk',               _path),

        ('rs_ip',                               _ipaddress),
        ('rs_storage_ip',                       _ipaddress),
        ('sbd_rs_disk',                         _string),
        ('rs_sbd_device',                       _sbd),
        ('sbd_rs_snapshots_disk',               _path),

        ('sbd_sync_threshold',                  _number),
        ('sbd_cache_size',                      _number),
        ('sbd_port_number',                     _number),
        ('dvol_lv_size',                        _lvmsize),

        ('sbd_device_bitmap',                   _path),
        ('sbd_most_recent_snapshot_id',         _snapid),

        ('primary_ip',                          _ipaddress), # service IP of the primary site

        ('primary_site_type',                   lambda v: _string(v) in Dvol.PG_SITE_TYPE),
        ('primary_stubs',                       _bool),
        ('primary_vnames',                      _csv),

        ('secondary_site_type',                 lambda v: _string(v) in Dvol.PG_SITE_TYPE),
        ('secondary_stubs',                     _bool),
        ('secondary_vnames',                    _csv),

        ('plun_volume_group',                   _string),  # XXX PLUN syntax validator
        ('plun_count',                          _number),

        #
        # From here to end -- optional attributes only
        #
        ('dvol.configversion',                  lambda v: _string(v) == '1'),
        ('active_snapshot_id',                  _snapid),

        ('sbd_test_failover_image_device',      _path),
        ('sbd_test_failover_image_snapshot_id', _snapid),
        ('sbd_test_failover_image_bitmap',      _path),
        ('sbd_test_failover_image_snap_size',   _lvmsize),

        ('sbd_scheduled_checkpoint_targets_list', _string),
        ('sbd_scheduled_checkpoint_stop_sync',    _string),
        ('sbd_scheduled_checkpoint_interval',     _string),
        ('sbd_first_scheduled_checkpoint_daily',  _string),
        ('sbd_snapshots_size',                    _lvmsize),
        ('sbd_snapshot_page_size',                _number),
        ('sbd_snapshot_file',                     _path),
        ('retention_scheduled',                   _string),
        ('retention_total',                       _string),
        ('protection_type',                       _string),
    ])

    # List of fields that are only present during test-failover (dvol_sbd.h:struct dvol_sbd_test_failover_prop)
    TESTFO_ATTR = set([
        'sbd_test_failover_image_device',         # LVM snapshot device
        'sbd_test_failover_image_snapshot_id',    # snapshot ID for LVM TFO image
        'sbd_test_failover_image_bitmap',         # bitmap file used for TFO
        'sbd_test_failover_image_snap_size'       # size of the snapshot
    ])

    # List of optional attributes (may, but need not, be present)
    OPTIONAL_ATTR = TESTFO_ATTR.union(set([
        'dvol.configversion',     # always "1"
        'ms_sbd_device',          # newer format: only fields relevant for the particular site
        'rs_sbd_device',          # newer format
        'sbd_ms_snapshots_disk',  # newer format
        'sbd_rs_snapshots_disk',  # newer format
        'sbd_ms_disk',            # newer format
        'sbd_rs_disk',            # absent in failover, see https://trello.com/c/qB1EIxnD/505-cluster-diagnosis-script-false-reporting-for-failed-over-pg
        'active_snapshot_id',     # if present, indicates that Dvol is running on a snapshot disk (else real disk)
        'primary_vnames',         # sometimes not present
        'secondary_vnames',       # sometimes not present
        'sbd_snapshots_size',     # no longer needed for AWS PGs in SH5
        'sbd_snapshot_file',      # NULL on SH5 AWS remote site (no snapshots used)
        'sbd_snapshot_page_size', # deprecated since bba162da9a0316dfc41ecf5e1bfea67883744e6c
        'sbd_scheduled_checkpoint_targets_list',
        'sbd_scheduled_checkpoint_stop_sync',
        'sbd_scheduled_checkpoint_interval',
        'sbd_first_scheduled_checkpoint_daily',
        'retention_total',
        'retention_scheduled',
        'protection_type'
    ]))

    #--------------------------------------------------------------------------------------------------------------
    # INNER CLASSES
    #--------------------------------------------------------------------------------------------------------------
    # Inner class that maps the ms/rs_xxx and primary/secondary_xxx attributes to this and the remote instance.
    SRN = namedtuple('SRN', ['service_ip', 'tcp_port',
                             'storage_ip', 'sbd_device', 'disk', 'snapshots_disk',
                             'site_type', 'stubs', 'vnames'])

    class Target(ConfigDict):
        """Representation of a Dvol Target. Attribute names are the TARGET_xxx constants in reader_writer.h
        See also dvol_sbd_writer.c:write_target_data()
        @dvol_name:                   Dvol which hosts this target
        @vm_name:                     name of the target VM
        @iqn:                         target IQN
        @os_category:                 part of os_type, one of %OS_CATEGORY
        @os_version:                  part of os_type (not checked)
        @primary_spoofed_signature:   spoofed signature of the primary leg
        @secondary_spoofed_signature: spoofed signature of the secondary leg
        @mirror_type:                 one of %MIRROR_TYPE
        """
        # as in defines.h
        IQN_PREFIX = 'iqn.2016-09.io.ctl'

        ATTR_MAP = collections.OrderedDict([
            ('dvol_name',                   _string),
            ('vm_name',                     _string),
            ('iqn',                         lambda v: _string(v).startswith(Dvol.Target.IQN_PREFIX)),
            ('os_category',                 lambda v: _string(v) in Dvol.Target.OS_CATEGORY),
            ('os_version',                  _string),
            ('primary_spoofed_signature',   _string),
            ('secondary_spoofed_signature', _string),
            ('mirror_type',                 lambda v: _string(v) in Dvol.Target.MIRROR_TYPE)
        ])

        # Synchronization type
        MIRROR_TYPE = ( "LRA", "LVM_RAID1", "RSYNC" )

        # Operating system type
        OS_CATEGORY = ( "OTHER", "LINUX", "WINDOWS" )

        @staticmethod
        def generate_external_iqn(dvol_name, vm_name):
            """Generate IQN from @dvol_name and @vm_name.
            Like lib_utils.c:tg_generate_external_iqn
            """
            return "%s:%s-%s-external" % (Dvol.Target.IQN_PREFIX, dvol_name, vm_name)

        def __init__(self, config_dict):
            """Arguments in @config_dict correspond to keys in *.target file.
            Not all elements in @ATTR_MAP need to be present.
            @pluns: list of PLUNs
            """
            ConfigDict.__init__(self, config_dict)
            self.pluns = set()

        def __eq__(self, other):
            return ConfigDict.__eq__(self, other) and self.pluns == other.pluns

        def add_plun(self, config_dict):
            """Add target PLUN generated from @config_dict."""
            plun = Dvol.Target.PLUN(config_dict)
            if plun.dvol_name != self.dvol_name:
                raise ValueError("Invalid dvol_name = %r - should be %r" % (plun.dvol_name, self.dvol_name))
            elif plun.vm_name != self.vm_name:
                raise ValueError("Invalid vm_name = %r - should be %r" % (plun.vm_name, self.vm_name))
            elif plun.tgt_name != self.iqn:
                raise ValueError("Invalid tgt_name = %r - should be %r" % (plun.tgt_name, self.iqn))
            elif plun in self.pluns:
                raise KeyError("Duplicate %s PLUN %s" % (self.name, plun))
            self.pluns.add(plun)


        class PLUN(ConfigDict):
            """Representation of a Target PLUN after it has been created."""
            # from lib_utils.c
            SCSI_SERIAL_NUMBER_PREFIX = 'SDGDvolD'

            ATTR_MAP = collections.OrderedDict([
                ('plun_name',      _string),
                ('plun_lunid',     _number),
                ('size',           _lvmsize),
                ('dvol_name',      _string),
                ('vm_name',        _string),
                ('tgt_name',       lambda v: _string(v).startswith(Dvol.Target.IQN_PREFIX)),
                ('scsisn',         lambda v: _string(v).startswith(Dvol.Target.PLUN.SCSI_SERIAL_NUMBER_PREFIX)),
                ('backing_device', _string) # DM devices only
            ])

            # Allow SCSISNs to differ only in their disk_id.
            # (Since the disk_ids in MS/RS pairs are not identical in Syntropy, but consecutive).
            def __hash__(self):
                return hash(repr([(k, v[:-2] if k == 'scsisn' else v) for k,v in self.iteritems()]))


    #--------------------------------------------------------------------------------------------------------------
    # CLASS METHODS
    #--------------------------------------------------------------------------------------------------------------
    def __init__(self, config_dict):
        """Arguments in @config_dict correspond exactly to keys in *.dvol file
        @local:   Cluster.Dvol fields representing the Dvol state on this node
        @remote:  Cluster.Dvol fields representing the Dvol state on the remote node
        @targets: list of targets
        """
        ConfigDict.__init__(self, config_dict)
        self.local   = None
        self.remote  = None
        self.targets = set()

        # Sanity checks
        if config_dict['primary_ip'] not in (config_dict['ms_ip'], config_dict['rs_ip']):
            raise ValueError("Invalid primary IP %s - does not belong to MS/RS site." % config_dict['primary_ip'])

        tfo_keys = set(config_dict.keys()) & Dvol.TESTFO_ATTR
        if tfo_keys and tfo_keys != Dvol.TESTFO_ATTR:
            raise KeyError("Missing test-failover key(s): %s", ', '.join(Dvol.TESTFO_ATTR - tfo_keys))

        # Check whether the master site is the primary site
        ms_is_prim = config_dict['primary_ip'] == config_dict['ms_ip']

        conf_keys  = ['%s_ip', '%s_port', '%s_storage_ip',
                      '%s_sbd_device', 'sbd_%s_disk', 'sbd_%s_snapshots_disk']
        site_keys  = ['%s_site_type', '%s_stubs', '%s_vnames']

        master = Dvol.SRN(*map(config_dict.get,
                               map(lambda s: s.replace('%s', 'ms'), conf_keys) + \
                               map(lambda s: s.replace('%s', 'primary' if ms_is_prim else 'secondary'), site_keys)))
        remote = Dvol.SRN(*map(config_dict.get,
                               map(lambda s: s.replace('%s', 'rs'), conf_keys) + \
                               map(lambda s: s.replace('%s', 'secondary' if ms_is_prim else 'primary'), site_keys)))

        if ms_is_prim and not remote.disk:
            raise Exception("Remote site %s does not have a disk" % remote.service_ip)
        self.local, self.remote = (master, remote) if config_dict['role'] == Dvol.LEG_ROLE[0] else (remote, master)

    def add_target(self, tgt):
        """Add a Dvol.Target to the list of targets of this Dvol."""
        assert isinstance(tgt, Dvol.Target)
        if tgt.dvol_name != self.name:
            raise ValueError("Invalid dvol_name = %r - should be %r" % (tgt.dvol_name, self.name))
        elif tgt in self.targets:
            raise KeyError("Duplicate %s target %s" % (self.name, tgt))
        self.targets.add(tgt)

    def diff(self, other):
        """Return the set of keys of entries in which @self and @other differ"""
        # FIXME: this is not going to work on test-failover fields,
        #        leaving it in for now until there is a test-failover case
        #        to 'test the test-failover'.
        #
        # Notes:
        # - role always differs
        # - periodic_resync_enabled may differ (it seems the value is ignored on the RS,
        #   the default configuration sets it to 'true' on the MS and 'false' on the RS
        # - the following may also differ (ROW/COW context in particular):
        #   * sbd_snapshots_size     (e.g. MS='5.0G', RS='2.0G')
        #   * sbd_snapshot_page_size (e.g. MS='512', RS='1048576')
        exclude = set([ 'role', 'state.periodic_resync_enabled',
                        'sbd_snapshots_size', 'sbd_snapshot_page_size',
                        'primary_stubs', 'secondary_stubs'
                    ])
        return set(k for k in self.keys() if self.get(k) != other.get(k)) - exclude

    # Computed attributes
    @property
    def name(self):
        return self['dvol_name']

    @property
    def state(self):
        return self['state.status']

    @property
    def is_master(self):
        return self['role'] == Dvol.LEG_ROLE[0] # FIXME: assumes that first element means 'master'

    @property
    def legless(self):
        return self['legless'] == 'true'

    @property
    def is_primary(self):
        return self['primary_ip'] == self.service_ip

    @property
    def snapshot_enabled(self):
        return self['state.periodic_snapshot_enabled'] == 'true'

    @property
    def guest_type(self):
        """Returns the %GUEST_TYPE. A NULL ('<none>') dvol_sbd_plun_vgroup indicates a DATA Dvol"""
        return Dvol.GUEST_TYPE[self.get('plun_volume_group', '<none>') != '<none>']

    @property
    def is_data_dvol(self): # FIXME: assumes that 'DATA' is always first element
        return self.guest_type == Dvol.GUEST_TYPE[0]

    # Built-in operators
    def __eq__(self, other):
        """Pairwise comparison of master/remote pairs, i.e. self != self by definition."""
        if other.__class__ != self.__class__ or self.diff(other):
            return False
        return self.local == other.remote and self.remote == other.local and self.targets == other.targets

    def __str__(self):
        return "%s(name=%r, type=%s, role=%r, state=%r, targets=[%s], local=%s, remote=%s)" % (self.__class__.__name__,
                self.name, self['type'],
                self['role'], self.state, '+'.join(map(str, self.targets)), self.local, self.remote)


class DvolSummaryInfo(object):
    """Encapsulate Dvol information as returned by dvol-list
    @name:            Dvol name
    @master_ip:       IP address of master leg
    @remote_ip:       IP address of remote leg
    @status:          see dvol_status.yaml
    @protection_type: see protection_type.yaml
    @os_category:     see os_category.yaml
    @has_image:       whether Dvol has a test failover image (value of bool 'dp_test_failover' in C code)
    @prim_sbd:        sbd type of the primary site
    @scnd_sbd:        sbd type of the secondary site
    @prim_disk:       disk type of the primary site
    @scnd_disk:       disk type of the secondary site
    @guest_type:      type of the protection group (%GUEST_TYPE)
    NOTE: this depends on info_manager.c:add_dprop_to_msg() -- KEEP IN SYNC
    """
    # List of possible Dvol states (unified on CMS and SRN)
    DP_STATUS  = ( "UNKNOWN", "UNSYNCED", "CREATING", "STARTING", "RUNNING", "TEST_FAILOVER", "FAILOVER", "MIGRATING", "MIGRATED", "FAILING_BACK_STOPPING_OLD_MASTER", "CREATE_FAILED", "TEST_FAILOVER_FAILED", "FAILOVER_FAILED", "RESIZING", "DELETING", "STOPPING", "STOPPED", "ERROR" )

    # dvol-list-properties Sbd Snapthot Type (see sbd3/usr/sbdm.c)
    SBD_TYPE   = ( "COW", "ROW", "INVALID" )

    # Leg Disk Type
    DISK_TYPE  = ( "RAWDISK", "LOGICAL_VOLUME", "INVALID_DISK" )

    # Protection Type (Cloud Type + Protection behaviour)
    PROTECTION_TYPE = ( "LEGACYPG", "AWSPG", "AZUREPG" )

    # [['Name', 'Master', 'Remote', 'Status', 'Type', 'OS', 'Sbd Type', 'Disk Type', 'Guest'], ...]
    def __init__(self, dp_name, dp_ip0, dp_ip1, dp_status, dp_type_and_image, dp_os, sbd_type, disk_type, guest):
        """Argument list is hard-coded to follow (tab-separated) output of dvol-list.
        KEEP IN SYNC WITH GO CODE (cmd/gosh/console/console.go)
        """
        assert dp_os in Dvol.Target.OS_CATEGORY

        self.name            = dp_name
        self.master_ip       = dp_ip0
        self.remote_ip       = dp_ip1
        self.status          = dp_status
        self.protection_type = dp_type_and_image.split(' ')[0]
        self.os_category     = dp_os
        self.has_image       = 'TFO image' in dp_type_and_image

        self.prim_sbd,  self.scnd_sbd  = sbd_type.split('/')
        self.prim_disk, self.scnd_disk = disk_type.split('/')
        self.guest_type      = guest

        assert self.protection_type in DvolSummaryInfo.PROTECTION_TYPE
        assert self.prim_sbd        in Dvol.TYPE
        assert self.scnd_sbd        in Dvol.TYPE
        assert self.prim_disk       in DvolSummaryInfo.DISK_TYPE
        assert self.scnd_disk       in DvolSummaryInfo.DISK_TYPE
        assert self.guest_type      in Dvol.GUEST_TYPE

    @property
    def unhealthy_status(self):
        """Assess whether Dvol's status is healthy"""
        # FIXME: easygen
        return self.status in ( 'UNKNOWN', 'CREATE_FAILED', 'STOPPING', 'STOPPED',
                                'FAILOVER_FAILED', 'TEST_FAILOVER_FAILED', 'UNSYNCED', 'ERROR')
    def __repr__(self):
        return "%s(%r, %r, %r, status=%r, ip=%r/%r, sbd_type=%r/%r, disk_type=%r/%r, guest=%r)" % (
               self.__class__.__name__, self.name, self.protection_type, self.os_category, self.status,
               self.master_ip, self.remote_ip,
               self.prim_sbd, self.scnd_sbd, self.prim_disk, self.scnd_disk, self.guest_type)


# DvolSnapshotInfo: data format returned by 'dvol-list-snapshots'
# Two snapshots are identical if they agree in all parameters.
# @snapshot_id: hex timestamp, e.g. '53C03A38'
# @schedule:    'MANUAL' or 'PERIODIC'
# @size:        snapshot size in bytes
class DvolSnapshotInfo(namedtuple('DvolSnapshotInfo', ['snapshot_id', 'schedule', 'consistency', 'size'])):
    def when(self):
        """Decode epoch seconds information contained in @snapshot_id"""
        return time.strftime("%a, %b %-e at %-I:%M:%S %p", time.localtime(int('0x' + self.snapshot_id, 0)))

# DvolProperties: wraps the output of dvol-list-properties
# NOTE: the format below depends on the console format only, NOT the internal parameter ordering.
class DvolProperties(namedtuple('DvolProperties', [
    'name',              # /dev basename, e.g. 'gg'
    'status',            # e.g. RUNNING (dvol_enum.c)
    'role',              # master | remote (dvol_enum.c)

    'snapshot_period',   # snapshot period in seconds, '0': disabled
    'snapshots_lv_size', # snap size (see size_string_to_bytes())

    'ip',                # Site IP (a.b.c.d)
    'disk',              # backing device path, e.g. /dev/a/gg
    'snapdev',           # snapshot device path, e.g. /dev/a/gg-snaps
    'sbd_device',        # sbd path, e.g. /dev/sbd0
    'dirty_data',        # dirty data in bytes
    'wan_sync_throttle', # WAN-Sync throttle in KB/s ('0' means disabled)
    'quota_status',      # one of IN_LIMIT | ROW_HARDQUOTA | ROW_SOFTQUOTA | UNKNOWN

    'snapshot_type',     # sbd type: NOT_AVAILABLE | COW | ROW
    'active_connection', # '1': active, '0': no connection to peer site
    'device_size',       # same as sbd_details_device_size_in_bytes

    'pg_type',           # prim PG site type (see site_type_to_str()), e.g. VMWARE_VAPP
    'pg_stubs',          # whether prim PG site uses VM stubs (true) or out-of-band (false)

    'master_site_ip',    # primary_ip (see dvol_sbd.h)
    'iscsi_sessions',    # string with iSCSI session information

    'scheduled_checkpoints_daily_time', # first time in the day a schedule checkpoint is taken
    'scheduled_checkpoints_interval',   # interval between periodic checkpoints

    'amis_to_keep_total',               # number of AWS AMIs to keep per target for all checkpoints
    'amis_to_keep_scheduled'            # number of AWS AMIs to keep per target for scheduled checkpoints
    ])):
    """Info for a Dvol taken from output of dvol-list-properties
    """
    def __repr__(self):
        """Enforce the same output as generated by the console.
        Used for compliance testing.
        """
        return re.sub('^\s*', '', '''
          Name                              : %s
          Status                            : %s
          Role                              : %s
          Snapshot Period                   : %s
          Snapshot Logical Volume Size      : %s
          IP Address of Site                : %s
          Backing device path               : %s
          Snapshot device path              : %s
          SBD device path                   : %s
          Dirty Data                        : %s
          WAN Throttle                      : %s
          Quota Status                      : %s
          Snapshot Type                     : %s
          Active Connection to Peer Site    : %s
          Device Size in Bytes              : %s
          Site Type                         : %s
          Site Uses Stub VMs                : %s
          Primary Site IP                   : %s
          ISCSI Sessions                    : %s
          Scheduled checkpoint daily time   : %s
          Scheduled checkpoint interval     : %s
          AMIs to keep - total              : %s
          AMIs to keep - scheduled          : %s''' % (
            self.name, self.status, self.role,
            self.snapshot_period, self.snapshots_lv_size,
            self.ip, self.disk, self.snapdev, self.sbd_device,
            self.dirty_data, self.wan_sync_throttle, self.quota_status,
            self.snapshot_type, self.active_connection, self.device_size,
            self.pg_type,
            self.pg_stubs, self.master_site_ip, self.iscsi_sessions,
            self.scheduled_checkpoints_daily_time, self.scheduled_checkpoints_interval,
            self.amis_to_keep_total, self.amis_to_keep_scheduled
        ), flags=re.MULTILINE)

    @property
    def unsynched(self):
        """Return the Dirty Data (sbd number_of_dirty_pages * sector_size) as a number."""
        return int(self.dirty_data)

    @property
    def rdp_port_open(self):
        """Return True if the RDP port listed in the 'ISCSI Sessions' part appears to be open."""
        # Matches the syntax of the pgiscsiinfo (targetInfo) scripts: ";rdp port: 3389/tcp open ms-wbt-server;time updated:"
        return bool(re.search(r';rdp port:[^;]+\s+open[^;]*;', self.iscsi_sessions))

    def SnapshotsConfigured(self):
        return self.snapshots_lv_size != '0'

    def HasPeriodicSnapshots(self):
        return self.SnapshotsConfigured() and self.snapshot_period != '0'

    def IsActive(self):
        return self.status == 'RUNNING' and self.active_connection == '1'


class ArgumentError(SyntaxError): pass

class DvolCreate(namedtuple('DvolCreate', [
        'name',             # Human-readable name for the Dvol (dvol_name)
        'type',             # COW | ROW
        'lv_size',          # Size with suffix 'K|M|G' (defaults to megabytes), e.g. '10.0G'
        'sync_threshold',   # Sync threshold size in KB (default 1MB)

        'ms_snap_size',     # Reserved space for snapshots on primary site (same format as 'size')
        'rs_snap_size',     # Reserved space for snapshots on remote site
        'snapshot_period',  # Period (in seconds) between snapshots

        'ms_ip',            # Service IP of the Master Site
        'ms_storage_ip',    # Storage IP of the Master Site
        'ms_data_pool',     # VG Name of the Data Storage Pool on the MS (as reported by 'vgs')
        'ms_snap_pool',     # VG Name of the Checkpoint Storage Pool on the MS

        'rs_ip',            # Service IP of the Remote Site
        'rs_storage_ip',    # Storage IP of the Remote Site
        'rs_data_pool',     # VG Name of the Data Storage Pool on the RS
        'rs_snap_pool',     # VG Name of the Checkpoint Storage Pool on the RS

        'pg_prim_type',     # Primary SiteType (e.g. CLC)
        'pg_sec_type',      # Secondary SiteType (e.g. AWS)
        'pg_prim_stubs',    # Whether primary PG site uses VM stubs (true) or out-of-band mirroring (false)
        'pg_sec_stubs',     # Whether secondary PG site uses VM stubs (analogous to pg_prim_stubs)
        'pg_prim_name',     # Deprecated: primary site name
        'pg_sec_name',      # Deprecated: secondary site name
        'plun_params',      # ':'-separated list of PLUN properties, or '<none>' (plun_props)

         #
         # Stub Provisioning
         #
        'make_stubs',       # Whether or not to provision CLC stubs (true or false)
        'group_uuid',       # CLC parent group (folder) uuid for the stubs
        'location',         # CLC data centre location alias for stub location (eg CA2)
        'group_name',       # CLC folder name into which the stubs are grouped
        'name_seeds',       # CLC 6-char stub seed name alias list (comma-separated)
        'stub_templates',   # CLC list of template names to create the stubs (comma-separated)
        'num_cpu',          # CLC number of CPUs per each stub VM
        'memory_gb',        # CLC memory in GB allocated to each stub VM
        'network_name',     # CLC network name to connect the stubs to (hex ID)
        'stub_password',    # CLC administrative password to use for the stubs
        'descriptions',     # CLC stub descriptions for each VM (comma-separated)
        'target_names',     # CLC iSCSI target names for each stub (comma-separated)
        'makestub_url',     # CLC ansible URL to download makestub script from
        'stub_os_type',     # CLC operating system type common to all stubs (WINDOWS or LINUX)
        'prim_rec_plan',    # CLC recovery plan information (primary site)
        'prim_vapp_name',   # CLC recovery plan VAPP name (primary site)
        'sec_rec_plan',     # CLC recovery plan information (secondary site)
        'sec_vapp_name',    # CLC recovery plan VAPP name (secondary site)
    ])):

    def __new__(cls, *args, **kwargs):
        """Construct immutable named tuple object with argument validation at construction time."""

        # 1. Argument length validation: one of @args, @kwargs must be able to initialize object.
        expected_len = len(cls._fields)
        args_len     = len(args if args else kwargs)
        if args_len == 1 and not kwargs and isinstance(args[0], cls):
            validated_args = args[0]._asdict()
        elif args_len != expected_len:
            raise Exception("%s: expected %d arguments, got %d" % (cls.__name__, expected_len, args_len))
        elif args:
            validated_args = dict(zip(cls._fields, args))
            if kwargs:
                validated_args.update(kwargs)
        else:
            validated_args = kwargs

        # 2. Argument type validation
        if validated_args['type'].upper() not in Dvol.TYPE:
             raise ArgumentError("Invalid Dvol type %r" % validated_args['type'])

        for pg in ('pg_prim_type', 'pg_sec_type'):
            if validated_args[pg] not in Dvol.PG_SITE_TYPE:
                raise ArgumentError("Invalid %s site type %r" % (pg, validated_args[pg]))

        for b in ('pg_prim_stubs', 'pg_sec_stubs', 'make_stubs'):
            if not _bool(validated_args[b]):
                raise ArgumentError("Invalid %s boolean value %r" % (b, validated_args[b]))

        for i in ('ms_ip', 'rs_ip', 'ms_storage_ip', 'rs_storage_ip'):
            if not _ipaddress(validated_args[i]):
                raise ArgumentError("Invalid %s IP Address %r" % (i, validated_args[i]))

        if validated_args['pg_prim_type'] == 'MANUAL' and validated_args['pg_sec_type'] != 'MANUAL':
            raise ArgumentError("Either both or none of pg_prim_type / pg_sec_type may be set to MANUAL")
        elif validated_args['pg_prim_type'] != 'MANUAL' and validated_args['pg_sec_type'] == 'MANUAL':
            raise ArgumentError("Either both or none of pg_prim_type / pg_sec_type may be set to MANUAL")
        elif validated_args['pg_prim_type'] == 'MANUAL' and validated_args['plun_params'] != '<none>':
            raise ArgumentError("plun_params must be <none> when using MANUAL (Data Dvol) type")

        elif validated_args['pg_prim_type'] == 'MANUAL' and validated_args['pg_prim_name'] != '<none>':
            raise ArgumentError("pg_prim_name must be <none> when using MANUAL (Data Dvol) type")
        elif validated_args['pg_prim_type'] == 'MANUAL' and validated_args['pg_sec_name'] != '<none>':
            raise ArgumentError("pg_sec_name must be <none> when using MANUAL (Data Dvol) type")

        elif validated_args['pg_prim_type'] == 'MANUAL' and validated_args['prim_rec_plan'] != '':
            raise ArgumentError("prim_rec_plan must be empty when using MANUAL (Data Dvol) type")
        elif validated_args['pg_prim_type'] == 'MANUAL' and validated_args['sec_rec_plan'] != '':
            raise ArgumentError("sec_rec_plan must be empty when using MANUAL (Data Dvol) type")

        return super(DvolCreate, cls).__new__(cls, **validated_args)


    @classmethod
    def from_ConfHash(cls, config):
        """Produce a DvolCreate instance from configuration dictionary @config."""
        # Prepopulate the stub-provisioning part with empty defaults
        # FIXME: this is a work-around and should be removed soon.
        def_val = lambda key: 'false' if key == 'make_stubs' else ''
        kwargs  = { k:(SyntropyValue(config[k]) if k in config else def_val(k)) for k in cls._fields }
        return cls(**kwargs)

    def __repr__(self):
        return re.sub('^\s*', '', '''
          Dvol Name                    : %s
          Type                         : %s
          Size                         : %s
          Sync Threshold               : %s
          MS Snapshot Size             : %s
          RS Snapshot Size             : %s
          Snapshot Period              : %s
          Master Service IP            : %s
          Master Storage IP            : %s
          MS Data Storage Pool         : %s
          MS Snapshot Storage Pool     : %s
          Remote Service IP            : %s
          Remote Storage IP            : %s
          RS Data Storage Pool         : %s
          RS Snapshot Storage Pool     : %s
          Primary Site PG Type         : %s
          Secondary Site PG Type       : %s
          Primary Site uses VM stubs   : %s
          Secondary Site uses VM stubs : %s
          Primary Site Name            : %s
          Secondary Site Name          : %s
          PLUN Properties              : %s
          Provision CLC stubs:         : %s
          ''' % (
            self.name, self.type.upper(), self.lv_size, self.sync_threshold,
            self.ms_snap_size, self.rs_snap_size, self.snapshot_period,
            self.ms_ip, self.ms_storage_ip, self.ms_data_pool, self.ms_snap_pool,
            self.rs_ip, self.rs_storage_ip, self.rs_data_pool, self.rs_snap_pool,

            self.pg_prim_type, self.pg_sec_type,
            self.pg_prim_stubs, self.pg_sec_stubs,
            self.pg_prim_name, self.pg_sec_name,
            self.plun_params, self.make_stubs
          ), flags=re.MULTILINE)

    @property
    def is_cow_cow(self):
        """Checks for the first value of sbd_type"""
        return self.type.upper() == Dvol.TYPE[0]

    @property
    def is_data_dvol(self):
        """Return True if configured as a Data Dvol"""
        return self.pg_prim_type == 'MANUAL' # FIXME: site_type ( "MANUAL", "VMWARE", "CLC", "AWS", "AZURE" )

    @property
    def vg_name(self):
        """Return the VG name that Syntropy would assign to this Dvol."""
        # see VGROUP_SUFFIX in dvol_sbd_add_to_dvols()
        return "" if self.is_data_dvol else self.name + "-vg"


class VM(object):
    """A VM is a Syntropy target, along with an ordered list of hard disk (aka Syntropy PLUN)."""
    #
    # Inner Classes
    #

    # Target - representation of a target within the @plun_params
    # NOTE: not using Dvol.Target here, since (a) keys must be in order and (b) field checks can not
    # be enforced (iqn and dvol_name are both set to <none>)
    Target = namedtuple('Target', [
        'iqn',                         #define PARAM_CREATE_TARGET_IQN                            0
        'dvol_name',                   #define PARAM_CREATE_TARGET_DVOL_NAME                      1
        'vm_name',                     #define PARAM_CREATE_TARGET_VM_NAME                        2
        'os_category',                 #define PARAM_CREATE_TARGET_OS_CATEGORY                    3
        'os_version',                  #define PARAM_CREATE_TARGET_OS_VERSION                     4
        'primary_spoofed_signature',   #define PARAM_CREATE_TARGET_PRIMARY_SPOOFED_SIGNATURE      5
        'secondary_spoofed_signature', #define PARAM_CREATE_TARGET_SECONDARY_SPOOFED_SIGNATURE    6
        'mirror_type'                  #define PARAM_CREATE_TARGET_MIRROR_TYPE                    7
    ])

    # PLUN inner class (see PARAM_CREATE_PLUN_NUM_REQ_PARAMS_SHORT)
    # NOTE: the 'dvol_name' is ignored when sending PLUN parameters. This is because of using
    #       'k < PARAM_CREATE_PLUN_NUM_REQ_PARAMS_SHORT-1' (= 3) in dvol_sbd_reader.c:parse_target_params()
    class PLUN(namedtuple('PLUN', [
            'plun_name',  #define PARAM_CREATE_PLUN_NAME        0 --> 0
        #    'dvol_name', #define PARAM_CREATE_PLUN_DVOL_NAME   1 --> IGNORED
            'size',       #define PARAM_CREATE_PLUN_SIZE        2 --> now 1
            'vm_name'     #define PARAM_CREATE_PLUN_VM_NAME     3 --> now 2
        ])):
        def __repr__(self):
            """Use Syntropy serialization format."""
            return ",".join(self)

    @classmethod
    def from_plun_prop(cls, plun_prop):
        """Generate a VM description from a Syntropy plun_prop."""
        # A plun_prop is a '|'-separated string. The first 8 of its fields form a Target;
        # the remaining fields contain PLUN data, each of which is ','-separated.
        targetFields = plun_prop.split('|')
        if len(targetFields) < len(VM.Target._fields):
            raise ArgumentError("Invalid plun_prop %r" % plun_prop)

        return cls(VM.Target(*targetFields[:len(VM.Target._fields)]),
                   [VM.PLUN(*r.split(',')) for r in targetFields[len(VM.Target._fields):]])

    def __init__(self, target, pluns):
        """Class wraps target plus list of disks (PLUNs)."""
        self.target, self.pluns = target, pluns

    def __str__(self):
        """Pretty-printed representation."""
        return "%s: %s, disks: %s" % (self.target.vm_name, self.target.os_version,
                                            ", ".join(p.size for p in self.pluns))

    def __repr__(self):
        """Employ the same serialization format as used by Syntropy."""
        return '|'.join(self.target + tuple(map(repr, self.pluns)))


class RecoveryPlan(namedtuple('RecoveryPlan', [
        'res_name',        # Main resource name (= target_name on the master site, differs from it on the remote site)

        'up_index',        # Position of this RecoveryPlan within the power-on RecoverySequence
        'up_action',       # Power-on action (always "POWER_ON")
        'up_delay',        # Power-on delay in seconds

        'down_index',      # Position of this RecoveryPlan within the power-down RecoverySequence
        'down_action',     # Power-down action ("POWER_OFF" or "SHUTDOWN")
        'down_delay',      # Power-down delay in seconds

        'res_desc',        # Textual description of @res_name (used by GUI only)
        'res_ip',          # IP of the VM/target

        'group_id',        # UNUSED (nowhere referenced by the code)
        'group_name',      # UNUSED (nowhere referenced by the code)

        'target_name',     # Identifies VM target (equals @res_name on the master site)
    ])):

    def __new__(cls, res_name,
                up_index, up_action, up_delay,
                down_index, down_action, down_delay,
                res_desc, res_ip, group_id, group_name, target_name):
        """Wrapper to perform type conversion and argument validation."""
        if not dgpy.utils.is_valid_ip(res_ip):
            raise ArgumentError("%r is not a valid IP" % res_ip)
        return super(RecoveryPlan, cls).__new__(cls, res_name,
                                                int(up_index), up_action, long(up_delay),
                                                int(down_index), down_action, long(down_delay),
                                                res_desc, res_ip, group_id, group_name, target_name)
    def __lt__(self, other):
        return self.up_index < other.up_index

    def __str__(self):
        return "%s (%s), up #%d/%d, down #%d/%d" % (self.res_name, self.res_ip,
                                                    self.up_index, self.up_delay, self.down_index, self.down_delay)
    def __repr__(self):
        """Use Syntropy serialization format."""
        return ",".join(map(str, self))


class RecoverySequence(UserList):
    """The ordered sequence of recovery plan operations."""
    @classmethod
    def from_hash_list(cls, *hl):
        """Use a list of hashes to generate the RecoverySequence.
        The following dict keys are used (mandatory unless otherwise noted):
        @target_name:  target name
        @res_ip:       the IP address of @target
        @res_name:     optional resource name (defaults to @target)
        """
        if len(hl) == 1 and isinstance(hl[0], types.GeneratorType):
            hl = [e for e in hl[0]]         # Expand generator: we need to know its len()
        return cls(RecoveryPlan(
                res_name    = h.get('res_name', h['target']),
                up_index    = h.get('up_index', i),
                up_action   = 'POWER_ON',   # This is currently the only possible method.
                up_delay    = h.get('up_delay', 120),
                down_index  = h.get('down_index', len(hl)-1 - i),
                down_action = h.get('down_action', 'SHUTDOWN'),
                down_delay  = h.get('down_delay', 0),
                res_desc    = h.get('res_desc', ''),
                res_ip      = h['ip'],
                group_id    = '<none>',     # not used by Syntropy code
                group_name  = '<none>',     # not used by Syntropy code
                target_name = h['target']) for i,h in enumerate(hl))

    @classmethod
    def from_string(cls, s):
        """Parse @s as containing a RecoverySequence."""
        if s.strip() == "":
            return UserList([])
        return cls(RecoveryPlan(*r.split(',')) for r in s.split('|'))

    def __init__(self, *args):
        def flatten(acc, l):
            """Helper function to deal with mixed arguments."""
            acc.extend(l) if isinstance(l, Iterable) else acc.append(l)
            return acc
        # validate arguments
        seq = sorted(reduce(flatten, args, []))
        for i, e in enumerate(seq):
            if not isinstance(e, RecoveryPlan):
                raise ArgumentError("%s (%s) is not of type 'RecoveryPlan'" % (e, type(e)))
            elif e.up_index != i:
                raise ArgumentError("Recovery step #%d (%s) has unexpected up_index=%d" % (i, e, e.up_index))
            elif e.down_index != len(seq)-1 - i:
                raise ArgumentError("Recovery step #%d (%s) has unexpected down_index=%d" % (i, e, e.down_index))
        return super(RecoverySequence, self).__init__(seq)

    def __repr__(self):
        """Use Syntropy serialization."""
        return '|'.join(map(repr, self))


class DvolAddVM(namedtuple('DvolAddVM', [
        'dvol_name',        # Name of Dvol to add the VM(s) to
        'new_pg_size',      # New _total_ size of the PG (_after_ adding the VMs, > current_sbd_size)
        'snapshot_ms_size', # New snapshot device size on the master site (use 0 to keep old size)
        'snapshot_rs_size', # New snapshot device size on the remote site (use 0 to keep old size)
        'pg_prim_type',     # Type of primary PG site, e.g. VMWARE_VAPP
        'pg_sec_type',      # Type of secondary PG site (format like pg_prim_type)
        'plun_props',       # ':'-separated list of PLUN properties or '<none>'
         #
         # Stub Provisioning - the following 18 fields are identical with DvolCreate:
         #
        'make_stubs',       # Whether or not to provision CLC stubs (true or false)
        'group_uuid',       # CLC parent group (folder) UUID for the stubs
        'location',         # CLC data centre location alias for stub location
        'group_name',       # CLC folder name into which the stubs are grouped
        'name_seeds',       # CLC 6-char stub seed name alias list (comma-separated)
        'stub_templates',   # CLC list of template names (comma-separated)
        'num_cpu',          # CLC number of CPUs per each stub VM
        'memory_gb',        # CLC memory in GB allocated to each stub VM
        'network_name',     # CLC network name to connect the stubs to (hex ID)
        'stub_password',    # CLC administrative password to use for the stubs
        'descriptions',     # CLC stub descriptions for each VM (comma-separated)
        'target_names',     # CLC VM names to protect
        'makestub_url',     # CLC Ansible URL to download makestub script from
        'stub_os_type',     # CLC operating system type common to all stubs (WINDOWS or LINUX)
        'prim_rec_plan',    # CLC recovery plan information (primary site)
        'prim_vapp_name',   # CLC recovery plan VAPP name (primary site)
        'sec_rec_plan',     # CLC recovery plan information (secondary site)
        'sec_vapp_name',    # CLC recovery plan VAPP name (secondary site)
    ])):

    def __new__(cls, *args, **kwargs):
        """Construct immutable named tuple - compare with DvolCreate."""

        # 1. Argument length validation: one of @args, @kwargs must be able to initialize object.
        expected_len = len(cls._fields)
        args_len     = len(args if args else kwargs)
        if args_len == 1 and not kwargs and isinstance(args[0], cls):
            validated_args = args[0]._asdict()
        elif args_len != expected_len:
            raise Exception("%s: expected %d arguments, got %d" % (cls.__name__, expected_len, args_len))
        elif args:
            validated_args = dict(zip(cls._fields, args))
            if kwargs:
                validated_args.update(kwargs)
        else:
            validated_args = kwargs

        # 2. Argument type validation
        if not _lvmsize(validated_args['new_pg_size']):
            raise ArgumentError("Invalid new_pg_size %r" % validated_args['new_pg_size'])

        for pg in ('pg_prim_type', 'pg_sec_type'):
            if validated_args[pg] not in Dvol.PG_SITE_TYPE:
                raise ArgumentError("Invalid %s site type %r" % (pg, validated_args[pg]))

        return super(DvolAddVM, cls).__new__(cls, **validated_args)

    @classmethod
    def from_ConfHash(cls, config):
        """Produce a DvolAddVM instance from configuration dictionary @config."""
        # FIXME: define YAML serialization
        # - takes a nested dictionary
        # - VMs are represented as sequence of dictionary
        # - VMs must have right syntax (throw exception)
        return cls(**{ k:config[k] for k in cls._fields })

    def __repr__(self):
        return " ".join('"%s"' % i for i in self)

if __name__ == '__main__':
    pass
