#!/usr/bin/python
#
# Add a new user to the system.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Add a new @USER to the system")

parser.add_argument('USER', type=str, help = 'Name of the user to add to the system')
parser.add_argument('PASS', type=str, help = 'Login password to use for @USER')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.user_add(args.USER, args.PASS)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Add user Job ID: {}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to add user '{0}': {1}".format(args.PASS, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
