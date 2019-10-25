#!/usr/bin/python
#
# Add or modify a CenturyLink Cloud site.
#
# Usage: $0 <site-name> <account> <user> <pass> <location>, with
#           - @site-name: name of the site
#           - @account:   which CLC (sub-)account of @user to use
#           - @user:      CLC portal login name
#           - @pass:      password for @user
#           - @location:  data centre location to use (e.g. CA2, VA1, ...)
#
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

if len(sys.argv) != 6:
    print >>sys.stderr, "Usage: %s <site-name> <account> <user> <pass> <location>" % sys.argv[0]
else:
    try:
        res = CmsClient().site_update_clc(*sys.argv[1:])
    except GrpcError as e:
        print "Failed to add CLC site {0}: {1}".format(sys.argv[1], e)
    else:
        print "Adding CLC site {0} Job ID: {1}".format(sys.argv[1], res.job_id)
