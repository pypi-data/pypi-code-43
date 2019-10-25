#!/usr/bin/python
#
# 3-in-1 checkpoint configuration for non-legacy PGs:
#   1) Periodic checkpoint interval in seconds (0 to disable);
#   2) Scheduled checkpoint in HH:MM UTC, plus optional VSS targets;
#   3) Snapshot retention policy total/scheduled (0 means unlimited).
#
# Example:
#   ./pg-checkpoint-config.py u16 0 17:15 ""  0 0
#
import sys
from datetime                      import datetime

from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.duration_pb2  import Duration

from dgpy.cms_client               import CmsClient
from dgpy.aggregates.dvol          import dvol_pb2, dvol_enums_pb2
from dgpy.errors                   import GrpcError

if len(sys.argv) != 7:
    print >>sys.stderr, "Usage: %s <PG-Name> <snapshot-period-in-seconds>     \\" % sys.argv[0]
    print >>sys.stderr, "          <scheduled snapshot HH:MM> <scheduled-VSS> \\"
    print >>sys.stderr, "          <retention total> <retention scheduled>"
else:
    try:
        scheduledInstant = Timestamp()
        scheduledInstant.FromDatetime(datetime.strptime(sys.argv[3], '%H:%M'))
        res = CmsClient().pg_checkpoint_config(
            dvolName  = sys.argv[1],
            period    = Duration(seconds=int(sys.argv[2])),
            scheduled = dvol_pb2.ScheduledSnapshot(
                    firstInstant = scheduledInstant,
                    period       = Duration(seconds=3600*24), # Hardcoded (FIXME: constant) to one day
                    vssTargets   = sys.argv[4].split(","),
            ),
            rp = dvol_pb2.SnapshotRetentionPolicy(
                    total_snapshots     = int(sys.argv[5]),
                    scheduled_snapshots = int(sys.argv[6]),
            ),
        )
    except GrpcError as e:
        print "Failed to configure {0} checkpoints: {1}".format(sys.argv[1], e)
    else:
        print "Configuring snapshots Job ID: {}".format(res.job_id)
