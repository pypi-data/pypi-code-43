#!/usr/bin/python
#
# Delete a non-legacy Protection Group  by name.
#
# Will throw an error if attempting to delete a legacy PG.
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Delete the non-legacy Protection Group @PG")

parser.add_argument('PG', type=str,                           help = 'Name of the Protection Group')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.pg_delete(args.PG)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "PG deletion Job ID: {}".format(res.job_id)
except NotFoundError as e:
    die("No such PG: '{0}'".format(args.PG))
except GrpcError as e:
    die("Failed to delete {0}: {1}".format(args.PG, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
