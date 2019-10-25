#!/usr/bin/python
#
# List the disks ("PLUNs") of all VMs (targets) protected by a Protection Group.
#
# Usage: $0 [PG-Name]
# If no PG-Name is present, list the PLUNs of all targets of all known PGs.
import re
import sys
import time
from dgpy.cms_client import CmsClient

cols = ("VM Name", "Lun#", "Name", "Size")

client = CmsClient()
for pg in (sys.argv[1],) if len (sys.argv) > 1 else client.dvols:
    pluns = client.dvol_list_pluns(pg)
    if pluns:
        print "\n{} Disks:".format(pg)
        print "| {0:^20} | {1:^5} | {2:^8} | {3:>6} |".format(*cols)
        print "| {0:^20} | {1:^5} | {2:^8} | {3:>6} |".format(*('-' * len(c) for c in cols))
        for plun in pluns:
            fields = plun.split('\t')
            #
            # Order of fields in dvol_sbd_list_plun_to_msg:
            #
            # plun_name, size, lun_id, scsisn, iqn, vm_name
            # 0          1     2       3       4    5
            #
            vm, lun, name, size = fields[5], fields[2], fields[0], fields[1]
            # Legacy Protection Groups report their size in LVM units (e.g. "22G")
            # Newer-style Protection Groups report their size in bytes as a string (e.g. "10240")
            if re.match(r'^\d+$', size):
                size = "{0:d}G".format(int(size)>>30)
            print "| {0:^20} | {1:^5} | {2:^8} | {3:>6} |".format(vm, lun, name, size)
    else:
        print "\n{0} Disks: {1!r}".format(pg, pluns)
