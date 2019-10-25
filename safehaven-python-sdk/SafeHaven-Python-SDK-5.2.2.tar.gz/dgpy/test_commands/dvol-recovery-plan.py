#!/usr/bin/python
#
# List the recovery plan of a given DVOL on a given SRN site.
#
# Usage:
#  $0 [--raw] <PG-Name> <SRN-IP>
#
# Use --raw to print the recovery plan in Syntropy string format
# (this is useful for replay via dvol-create-or-update-recovery-plan).
#
# Example:
#  ./dvol-list-recovery-plan.py u16 10.55.220.229
import sys
from dgpy.cms_client import CmsClient
from dgpy.errors     import LegacyMessageError

# See RECOVERY_PLAN_STR_xxx in recovery_plan.h
cols = ("Resource", "#Up", "Up Action", "Up Delay", "#Down", "Down Action", "Down Delay", "Description", "IP", "Target")

args = sys.argv[1:] if len(sys.argv) > 1 else []
raw  = '--raw' in args
if raw:
    args.remove('--raw')

if len(args) != 2:
    print >>sys.stderr, "Usage: %s [--raw] <PG-Name> <SRN-IP>" % sys.argv[0]
else:
    try:
        rp = CmsClient().dvol_list_recovery_plan(*args)
        if raw and rp:
            print rp
        elif rp:
            print "{} Recovery Plan:".format(args[0])
            print "| {0:^17} | {1:>5} | {2:^10} | {3:>10} | {4:>7} | {5:^11} | {6:^12} | {7:^20} | {8:^15} | {9:^17} |".format(*cols)
            print "| {0:^17} | {1:>5} | {2:^10} | {3:>10} | {4:>7} | {5:^11} | {6:^12} | {7:^20} | {8:^15} | {9:^17} |".format(*('-' * len(c) for c in cols))
            for p in rp:
                print "| {0.res_name:^17} | {0.up_index:>5} | {0.up_action:^10} | {0.up_delay:>10} | {0.down_index:>7} | {0.down_action:^11} | {0.down_delay:^12} | {0.res_desc:<20.20} | {0.res_ip:^15} | {0.target_name:^17} |".format(p)
        else:
            print "{0} Recovery Plan: {1!r}".format(args[0], rp)
    except LegacyMessageError as e:
        print "Failed to list {0} recovery plan: {1}".format(args[0], e)
