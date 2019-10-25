#!/usr/bin/python
#
# Delete a site by name.
#
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s <site-name>" % sys.argv[0]
else:
    try:
        res = CmsClient().site_del(sys.argv[1])
    except GrpcError as e:
        print "Failed to delete site {0}: {1}".format(sys.argv[1], e)
    else:
        print "Site {0} delete Job ID: {1}".format(sys.argv[1], res.job_id)
