#!/usr/bin/python
#
# Set the login password for a given user.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Set the login password of @USER to @PASS")

parser.add_argument('USER', type=str, help = 'Name of the user to modify')
parser.add_argument('PASS', type=str, help = 'New Login password for @USER')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.user_set_password(args.USER, args.PASS)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Set {0} password Job ID: {1}".format(args.USER, res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to set password for {0}: {1}".format(args.USER, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
