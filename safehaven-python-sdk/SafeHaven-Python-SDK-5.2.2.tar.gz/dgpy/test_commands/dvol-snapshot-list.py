#!/usr/bin/python
#
# List the snapshots (checkpoints) of a given Protection Group (DVOL).
#
# Usage: $0 <PG-Name> <Master/Remote (m|r)>, with
#         - @PG-Name:       name of the protection group
#         - @Master/Remote: whether to list master ('m') or remote ('r') snaphots
import sys
import time
from dgpy.utils      import lvm_size, to_lvm_size
from dgpy.cms_client import CmsClient

cols = ("Date", "Snapshot ID", "Schedule", "Consistency", "Size")

if len(sys.argv) < 2:
    print >>sys.stderr, "Usage: %s <PG-Name>  <Master/Remote (m|r)>" % sys.argv[0]
else:
    client = CmsClient()
    remote = len(sys.argv) > 2 and sys.argv[2] in ('r', 'remote')
    snapshots = client.dvol_list_snapshots(sys.argv[1], remote=remote)
    if snapshots:
        print "{0} {1} Snapshots:".format(sys.argv[1], ('Master', 'Remote')[remote])
        print "| {0:^21} | {1:^14} | {2:^10} | {3:^13} | {4:^6} |".format(*cols)
        print "| {0:^21} | {1:^14} | {2:^10} | {3:^13} | {4:^6} |".format(*('-' * len(c) for c in cols))
        # The snapshots are already sorted in ascending order of ID.
        for s in snapshots:
            print "| {1:^21} | {0[id]:^14} | {0[schedule]:^10} | {0[consistency]:^13} | {2:>6} |".format(s,
                time.strftime("%a, %b %_e  %I:%M:%S", time.localtime(int('0x' + s['id'], 0))),
                to_lvm_size(lvm_size(s['size'])))
    else:
        print "{0} {1} Snapshots: []".format(sys.argv[1], ('Master', 'Remote')[remote])
