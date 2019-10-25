#!/usr/bin/python
#
# Add or modify a vmWare / vCenter site.
#
# Usage: $0 <site-name> <ip> <user> <pass>, with
#           - @site-name: name of the site
#           - @ip:        IP address of the vCenter server
#           - @user:      administrative user @ip
#           - @pass:      password for @user
#
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

if len(sys.argv) != 5:
    print >>sys.stderr, "Usage: %s <site-name> <ip> <user> <pass>" % sys.argv[0]
else:
    try:
        res = CmsClient().site_update_vcs(*sys.argv[1:])
    except GrpcError as e:
        print "Failed to add VCS site {0}: {1}".format(sys.argv[1], e)
    else:
        print "Adding VCS site {0} Job ID: {1}".format(sys.argv[1], res.job_id)
