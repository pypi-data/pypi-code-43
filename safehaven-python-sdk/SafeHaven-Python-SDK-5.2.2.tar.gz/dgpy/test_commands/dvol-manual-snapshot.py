#!/usr/bin/python
#
# Perform a simple (non-VSS enabled) checkpoint on a legacy Protection Group.
#
# Note that this call is meant for _legacy_ Protection Groups only.
# For non-legacy PGs, use 'pg-manual-checkpoint.py'.
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Perform a manual checkpoint on legacy @DVOL")

parser.add_argument('DVOL',                                 type=str, help = 'Name of the Protection Group')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()

try:
    client = CmsClient()
    res    = client.dvol_manual_snapshot(args.DVOL)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Manual snapshot job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to checkpoint {0}: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
