#!/usr/bin/python
#
# Print the (hopefully) unique cluster ID assigned to this cluster.
# The cluster ID should be different from 0000 and is the same on
# every node (CMS, SRN) of the cluster.
#
from dgpy.cms_client import CmsClient

print "Cluster ID:", CmsClient().cluster_id()
