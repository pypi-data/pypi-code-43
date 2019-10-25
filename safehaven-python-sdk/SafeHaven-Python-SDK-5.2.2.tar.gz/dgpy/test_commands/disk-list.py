#!/usr/bin/python
#
# Print the available raw/standalone disks and LVM Volume Group pools on SRN nodes.
#
# Usage: $0 [SRN-IP]
#
import sys
from dgpy.cms_client import CmsClient

# The disk-list call requires an SRN IP. Default to all SRNs if no IP given.
client = CmsClient()
for srn_ip in sys.argv[1:] if len(sys.argv) > 1 else client.srns:
    print "\nDisks on {}:\n".format(srn_ip)
    result = client.disk_list(srn_ip)

    cols = ("Device", "Size", "In Use By (target or pool)")
    print "{0:^10} | {1:>5} | {2}".format(*cols)
    print "{0:^10} | {1:>5} | {2}".format(*('-' * len(c) for c in cols))
    for d in sorted(result.disks.keys()):
        inUse = ""
        if result.disks[d].is_claimed:
            if result.disks[d].owner and result.disks[d].owner != result.disks[d].vg_name:
                inUse = result.disks[d].owner
            elif result.disks[d].vg_name not in result.pools:
                inUse = "ERROR: unknown pool %r" % result.disks[d].vg_name
            else:
                inUse = "{0} (available: {1:.1f}G)".format(result.disks[d].vg_name,
                                                           result.pools[result.disks[d].vg_name]/(1024.**3))
        print "{0:<10} | {1:4d}G | {2}".format(d, result.disks[d].size>>30, inUse)
