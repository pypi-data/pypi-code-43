#!/usr/bin/python
#
# Print list of all Safehaven Replication Nodes.
#
from dgpy.cms_client                           import CmsClient
from dgpy.messaging.shcomm.peer.peer_enums_pb2 import NodeStatus

cols = ("Node", "Service IP", "Site", "#PGs", "Status", "Storage IP", "Local Storage")

print "Registered SRNs:"
print "| {0:<20} | {1:<15} | {2:<6} | {3:^5} | {4:<8} | {5:^15} | {6:^15} |".format(*cols)
print "| {0:<20} | {1:<15} | {2:<6} | {3:^5} | {4:<8} | {5:^15} | {6:^15} |".format(*('-' * len(c) for c in cols))

for srn in CmsClient().node_list():
    storage_ip    = "= service_ip" if srn.storage_ip       == srn.service_ip else srn.storage_ip
    local_storage = "= service_ip" if srn.local_storage_ip == srn.service_ip else srn.local_storage_ip
    print "| {0.name:<20} | {0.service_ip:<15.15} | {0.site_name:<6.6} | {0.pg_count:^5} | {1:<8} | {2:^15} | {3:^15} |".format(srn,
                                                                             NodeStatus.Name(srn.status), storage_ip, local_storage)
