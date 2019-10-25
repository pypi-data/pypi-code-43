#!/usr/bin/python
#
# List the properties of known Protection Groups (aka DVOLs).
#
import sys
from datetime                 import timedelta

from dgpy.cms_client          import CmsClient
from dgpy.aggregates.dvol     import dvol_pb2, dvol_enums_pb2
from dgpy.safehaven.api.types import types_enums_pb2

client = CmsClient()
for pg in (sys.argv[1:] if len(sys.argv) > 1 else client.dvols):
    print "\n{} Properties:".format(pg)
    props = client.dvol_list_properties(pg, remote=False) # DvolLegProperties
    for e in (
        ('Name',                          props.name),
        ('Status',                        dvol_enums_pb2.DvolStatus.Name(props.status)),
        ('Role',                          dvol_enums_pb2.DvolSiteRole.Name(props.role)),
        ('Snapshot Period',               "{}h".format(props.snapshot_period.ToTimedelta())
                                               if props.snapshot_period.ToSeconds() else "disabled"),
        ('Snapshot Logical Volume Size',  "{0:d}M".format(props.snapshot_size_bytes>>20)),
        ('IP Address of Site',             props.leg_ip),
        ('Backing device path',            props.leg_disk),
        ('Snapshot device path',           props.leg_snapshots_disk),
        ('SBD device path',                props.leg_sbd_device),
        ('Dirty Data',                     "{0:.1f}K".format(props.dirty_data_bytes/1024.)),
        ('WAN Throttle',                   "{}kbps".format(props.wan_throttle_kb) if props.wan_throttle_kb else "unlimited"),
        ('Quota Status',                   props.quota_status), # stringified enum literal
        ('Snapshot Type',                  types_enums_pb2.SbdType.Name(props.snapshot_type)),
        ('Active Connection to Peer Site', ('NO', 'YES')[props.active_connection]),
        ('Device Size in Bytes',           str(props.dvol_size_bytes)),
        ('Site Type',                      types_enums_pb2.SiteType.Name(props.pg_site_type)),
        ('Site Uses Stub VMs',             ('NO', 'YES')[props.has_stubs]),
        ('Primary Site IP',                props.primary_ip),
        ('ISCSI Sessions',                 props.sessions), # ';'-separated string whose parser sits in the GUI.
        ('Scheduled checkpoint daily',     "{:%T} UTC".format(props.scheduled_snapshot.firstInstant.ToDatetime())
                                               if props.scheduled_snapshot.firstInstant.ToSeconds() else "<none>"),
        ('Scheduled checkpoint interval',  "{}h".format(props.scheduled_snapshot.period.ToTimedelta())
                                               if props.scheduled_snapshot.period.ToSeconds() else "<none>"),
        ('AMIs to keep - total',           str(props.retention_policy.total_snapshots)
                                               if props.retention_policy.total_snapshots else "unlimited"),
        ('AMIs to keep - scheduled',       str(props.retention_policy.scheduled_snapshots)
                                               if props.retention_policy.scheduled_snapshots else "unlimited"),
    ):
        print "{0:<32}: {1}".format(*e)
