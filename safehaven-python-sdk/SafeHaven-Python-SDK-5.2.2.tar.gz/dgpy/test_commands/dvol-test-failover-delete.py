#!/usr/bin/python
#
# Delete the test-failover image on the remote site of a PG.
#
# Usage: $0 <PG-Name> <PowerOff: y|n>, with
#         - @PG-Name:  name of the Dvol that has the test-failover image
#         - @PowerOff: whether to power off the remote site before deleting the image
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Delete the test-failover image on the remote site of @DVOL")

parser.add_argument('DVOL',            type=str,              help = 'Name of the Protection Group')
parser.add_argument('-o', '--power-off', action='store_true', help = 'Whether to power off the remote site before deleting the image')
parser.add_argument('-w', '--wait',      action='store_true', help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.dvol_test_failover_delete(args.DVOL, args.power_off)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Test-failover delete job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to delete {0} test-failover: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
