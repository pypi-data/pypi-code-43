#!/usr/bin/python
#
# Delete a legacy Protection Group by name.
#
# Will throw an error if attempting to delete a non-legacy PG.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Delete the legacy Protection Group @DVOL")

parser.add_argument('DVOL', type=str,                         help = 'Name of the Protection Group')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()

try:
    client = CmsClient()
    res    = client.dvol_delete(args.DVOL)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Delete {0} job #{1}".format(args.DVOL, res.job_id)
except NotFoundError as e:
    die("No such DVOL: '{0}'".format(args.DVOL))
except (LegacyMessageError, GrpcError) as e:
    die("Failed to delete {0}: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
