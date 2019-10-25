#!/usr/bin/python
#
# List the targets (VMs) protected by a given Protection Group.
#
# Usage: $0 [PG-Name]
# If no PG-Name is present, list the targets of all known PGs.
import sys
import time
from dgpy.cms_client import CmsClient

cols = ("VM Name", "OS", "Mirror", "IQN")

client = CmsClient()
for pg in (sys.argv[1],) if len (sys.argv) > 1 else client.dvols:
    targets = client.dvol_list_targets(pg, remote=False)
    if targets:
        print "\n{} Targets:".format(pg)
        print " {0:^20} | {1:^10} | {2:^10} | {3}".format(*cols)
        print " {0:^20} | {1:^10} | {2:^10} | {3}".format(*('-' * len(c) for c in cols))
        for target in targets:
            print " {0.vm_name:^20} | {0.os_category:^10} | {0.mirror_type:^10} | {0.iqn}".format(target)
    else:
        print "\n{0} Targets: {1!r}".format(pg, targets)
