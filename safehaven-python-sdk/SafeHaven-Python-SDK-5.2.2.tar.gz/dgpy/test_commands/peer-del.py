#!/usr/bin/python
#
# Delete a peer node from the peer list of a given SRN.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Remove the peering relationship between @SRN and @PEER")

parser.add_argument('SRN',  type=str,                         help = 'IP address of the SafeHaven Replication Node (SRN)')
parser.add_argument('PEER', type=str,                         help = 'IP address of the peer of @SRN')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.peer_del(args.SRN, args.PEER)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Peer de-registration Job ID: {}".format(res.job_id)
except NotFoundError as e:
    die("No such node: '{0}'".format(args.DVOL))
except (LegacyMessageError, GrpcError) as e:
    die("Failed to remove {1} from {0} peer list: {2}".format(args.SRN, args.PEER, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
