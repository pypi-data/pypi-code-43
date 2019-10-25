#!/usr/bin/python
#
# Print the list of peering nodes of a given SRN.
#
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import LegacyMessageError

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s <SRN-IP>" % sys.argv[0]
else:
    try:
        peer_ips = CmsClient().peer_list(sys.argv[1])
    except LegacyMessageError as e:
        print "Failed to list {0} peer nodes: {1}".format(sys.argv[1], e)
    else:
        print "{0} peers: {1}".format(sys.argv[1], " and ".join(peer_ips))
