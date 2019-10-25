#!/usr/bin/python
#
# Perform a simple (non-VSS enabled) checkpoint on a non-legacy Protection Group.
#
# Note that this call is mean for _non-legacy_ Protection Groups only.
# For legacy PGs, use 'dvol-manual-checkpoint.py'.
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s <PG-Name>" % sys.argv[0]
else:
    try:
        res = CmsClient().pg_manual_checkpoint(sys.argv[1])
    except GrpcError as e:
        print "Failed to checkpoint {0}: {1}".format(sys.argv[1], e)
    else:
        print "Manual checkpoint Job ID: {}".format(res.job_id)
