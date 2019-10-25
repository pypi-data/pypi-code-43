#!/usr/bin/python
#
# Set the WAN replication speed of the specified DVOL to the given value.
#
# The WAN replication speed (aka "Wan Sync Throttle") is specified either as
# - the value 0 (disables the throttle),
# - the string 'unlimited' as an alias to 0 (likewise disables throttle),
# - a positive integer specifying the desired WAN replication speed in KB/sec.
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Set the WAN replication speed of the specified @DVOL to @WAN-THROTTLE")

parser.add_argument('DVOL',                                 type=str, help = 'Name of the Protection Group')
parser.add_argument('WAN_THROTTLE', metavar='WAN-THROTTLE', type=int, help = 'Desired WAN replication speed in KB/sec; use 0 for "unlimited"')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()

try:
    client = CmsClient()
    res    = client.dvol_set_wan_throttle(args.DVOL, args.WAN_THROTTLE)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Set WAN-throttle job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to set the WAN replication speed on {0}: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
except Exception as e:
    die("Oops: {}".format(e))
