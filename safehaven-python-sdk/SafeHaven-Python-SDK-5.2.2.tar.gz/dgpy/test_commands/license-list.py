#!/usr/bin/python
#
# Print details of the currently installed CMS software license.
#
import time
from dgpy.cms_client                           import CmsClient
from dgpy.messaging.shcomm.peer.peer_enums_pb2 import NodeStatus

cols = ("Type", "Licensed", "Available")

print "License Information"
print "| {0:<11} | {1:>21} | {2:<9} |".format(*cols)
print "| {0:<11} | {1:>21} | {2:<9} |".format(*('-' * len(c) for c in cols))

for idx, row in enumerate(zip(("Standby CMS", "Nodes", "DVOLs", "Expiry Date"),  CmsClient().license_list())):
    licensed, avail = row[1].split(",")
    if idx == 3: # The expiry date is hex-encoded
        licensed = time.strftime("%b %_e %Y, %I:%M:%S", time.localtime(int(licensed, base=16)))
    print "| {0:<11} | {1:>21} | {2:<9} |".format(row[0], licensed, avail)
