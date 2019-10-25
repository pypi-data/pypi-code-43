#!/usr/bin/python
#
# Scaled-down version of pg-checkpoint-config to only set the periodic
# checkpoint interval (non-legacy PGs only).
#
# NOTE: As a side effect, any scheduled checkpoint will be cleared,
#       and the retention policy will be set to 0/0 (unlimited).
#       Use at your own discretion!
import sys
from dgpy.cms_client               import CmsClient
from google.protobuf.duration_pb2  import Duration
from dgpy.errors                   import GrpcError

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s <PG-Name> <snapshot-period-in-seconds>" % sys.argv[0]
else:
    try:
        res = CmsClient().pg_checkpoint_config(sys.argv[1], Duration(seconds=int(sys.argv[2])))
    except GrpcError as e:
        print "Failed to set {0} checkpoint period: {1}".format(sys.argv[1], e)
    else:
        print "Configuring checkpoint-period Job ID: {}".format(res.job_id)
