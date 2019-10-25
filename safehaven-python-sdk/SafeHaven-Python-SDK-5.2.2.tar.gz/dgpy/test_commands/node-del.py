#!/usr/bin/python
#
# Delete a Safehaven Replication Node by its node name.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Unregister the SafeHaven Replication @NODE")

parser.add_argument('NODE', type=str,                         help = 'Name of Node to unregister')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.node_del(args.NODE)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Node deletion Job ID: {}".format(res.job_id)
except NotFoundError as e:
    die("No such node: '{0}'".format(args.DVOL))
except (LegacyMessageError, GrpcError) as e:
    die("Failed to delete {0}: {1}".format(args.NODE, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
