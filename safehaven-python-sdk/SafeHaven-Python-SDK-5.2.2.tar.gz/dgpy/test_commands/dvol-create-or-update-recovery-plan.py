#!/usr/bin/python
#
# Create or update a DVOL recovery plan.
#
# Usage:
#  $0 <PG-Name> <SRN-IP> <recovery-plan-as-string>
#
# This uses the recovery plan in raw string format - tricky to get right.
#
# Example:
#  ./dvol-create-or-update-recovery-plan.py u16 10.55.220.229 "CA2GRRTAWS-UB02,0,POWER_ON,30,0,SHUTDOWN,0,UBUNTU 16 Guest VM,10.55.220.131,<none>,<none>,CA2GRR"
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Update the Recovery @PLAN of @DVOL on @SRN-IP")

parser.add_argument('DVOL',                     type=str, help = 'Name of the Protection Group')
parser.add_argument('SRN_IP', metavar='SRN-IP', type=str, help = 'IP address of the SRN to update')
parser.add_argument('PLAN',                     type=str, help = 'New Recovery Plan in comma-separated string format')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.dvol_create_or_update_recovery_plan(dvolName=args.DVOL, srnIp=args.SRN_IP, rp=args.PLAN)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Update recovery-plan job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to update {0} recovery plan at {1}: {2}".format(args.DVOL, args.SRN_IP, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
