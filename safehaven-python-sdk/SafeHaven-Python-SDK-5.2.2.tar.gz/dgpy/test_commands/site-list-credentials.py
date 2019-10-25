#!/usr/bin/python
#
# Print the Site Credentials of all known CMS sites.
#
# Usage: $0 [<site-name>]
# If no @site-name is present, lists credentials of all sites.
import sys
from dgpy.cms_client import CmsClient

cms = CmsClient()
for site in sys.argv[1:] if len(sys.argv) == 2 else cms.sites:
    res = cms.site_list_credentials(site)

    print "{0} site credentails:".format(res.name)

    whichOne = res.WhichOneof('CredentialsAggregate')
    if whichOne is None:      # No API credentials: MANUAL site
        print "\tMANUAL site - no credentials"
    if whichOne == 'clc':     # site.ClcCreds
        print "\tCLC User: {0.username}, Password: {0.password}, Account: {0.organization}, Location: {0.location}".format(res.clc)
    elif whichOne == 'vcs':   # site.VcsCreds
        print "\tvCenter {0.name} IP: {0.ip}, Username: {0.username}, Password: {0.password}".format(res.vcs)
    elif whichOne == 'aws':   # site.AwsCreds
        print "\tAWS Access Key: {0.access_key_id}, Key Secret: {0.secret_key}, Region: {0.region}".format(res.aws)
    elif whichOne == 'azure': # site.AzureCreds
        print "\tAzure Id: {0.client_id}, Secret: {0.client_secret}".format(res.azure)
        print "\tAzure Subscription: {0.subscription_id}, Tenant: {0.tenant_id}, Region: {0.region}".format(res.azure)
    else:
        print "Unknown site type %s: %r" % (whichOne, res)
