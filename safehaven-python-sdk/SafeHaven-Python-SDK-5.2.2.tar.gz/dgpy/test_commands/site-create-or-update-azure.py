#!/usr/bin/python
#
# Add or modify an Azure site.
#
# Usage: $0 <site-name> <client_id> <secret> <sub_id> <tenant_id> <region>, with
#         - @site_name:  Name of the Azure site
#         - @client_id:  Client ID of the Azure App
#         - @secret:     Client Secret or password of the Azure App
#         - @sub_id:     Subscription ID of the Azure account
#         - @tenant_id:  Tenant ID of the Azure Active Directory
#         - @region:     Azure region to use for this site
#
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

if len(sys.argv) != 7:
    print >>sys.stderr, "Usage: %s <site-name> <client_id> <secret> <sub_id> <tenant_id> <region>" % sys.argv[0]
else:
    try:
        res = CmsClient().site_update_azure(*sys.argv[1:])
    except GrpcError as e:
        print "Failed to add Azure site {0}: {1}".format(sys.argv[1], e)
    else:
        print "Adding Azure site {0} Job ID: {1}".format(sys.argv[1], res.job_id)
