#!/usr/bin/python
#
# Add or modify an AWS site.
#
# Usage: $0 <site-name> <access_key> <secret_key> <region>, with
#         - @site_name:  name of the AWS site
#         - @access_key: API access key
#         - @secret_key: API secret key
#         - @region:     AWS region to use for this site
#
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

if len(sys.argv) != 5:
    print >>sys.stderr, "Usage: %s <site-name> <access_key> <secret_key> <region>" % sys.argv[0]
else:
    try:
        res = CmsClient().site_update_aws(*sys.argv[1:])
    except GrpcError as e:
        print "Failed to add AWS site {0}: {1}".format(sys.argv[1], e)
    else:
        print "Adding AWS site {0} Job ID: {1}".format(sys.argv[1], res.job_id)
